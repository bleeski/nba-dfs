#!/usr/bin/env python3
"""Consistency checks for the nba-dfs build documents.

Usage:
    python scripts/check_docs.py            # all checks, findings listed, exit 1 if any
    python scripts/check_docs.py --quick    # the same checks, terse output (used by the smoke suite)
    python scripts/check_docs.py --show-sections   # also print every reading-list section reference
                                                   # with the heading it resolves to, for a human or audit read

Checks (ADJUDICATION-R2 entries R2-1 and R2-21):
  1. Chunk IDs agree across the chunk files, the BUILD_PLAN chunk table, the BUILD_PLAN dependency graph,
     the build order line, and the PROGRESS status board.
  2. Dependencies agree across chunk headers, the chunk table and the graph; the graph has no cycles;
     no chunk depends on a chunk later in the build order.
  3. The Floor-only route resolves: every chunk on it depends only on chunks on it, and none of them
     is in the deferred set.
  4. Every file a chunk's reading list names exists (or is an artifact an earlier chunk builds), every
     numbered section it names exists as a heading in that file, and every quoted section name appears
     in that file.
  5. Every repo path written in backticks in the authored documents exists, or is a runtime or build
     artifact.
  6. No authored document contains an em dash (U+2014) or an en dash (U+2013). Third-party inputs kept
     byte for byte (docs/reference/, spikes/ downloads, the reviewers' own files) are not checked.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHUNK_DIR = ROOT / "docs" / "build" / "chunks"
BUILD_PLAN = ROOT / "docs" / "build" / "BUILD_PLAN.md"
PROGRESS = ROOT / "docs" / "build" / "PROGRESS.md"

ID = r"C\d\d[a-z]?"
ID_RE = re.compile(rf"\b({ID})\b")

# Paths that do not exist in the design repo but are produced by build chunks or at runtime.
FUTURE_PREFIXES = (
    "src/", "tests/", "fixtures/", "config/", "inbox/", "data/", "runs/", "out/",
    ".claude/agents/", ".claude/settings.json", "scripts/dfs.cmd", "scripts/preflight.py", "scripts/build_fixtures.py",
    "pyproject.toml",
)
FUTURE_FILES = {
    ".claude/commands/night.md", ".claude/commands/news.md", ".claude/commands/swap.md",
    ".claude/commands/status.md", ".claude/commands/results.md",
}

# Authored documents: checked for dashes and for dangling paths.
AUTHORED_GLOBS = [
    "CLAUDE.md", "README.md", ".claude/commands/*.md",
    "docs/BRIEF.md", "docs/ARCHITECTURE.md", "docs/SLATE-BRIEF-MOCK.md",
    "docs/adr/*.md", "docs/build/*.md", "docs/build/chunks/*.md",
    "docs/review/ADJUDICATION.md", "docs/review/ADJUDICATION-R2.md",
    "docs/review/critique-*.md",
    "docs/research/*.md", "docs/brief/*.md",
]
PATH_CHECK_GLOBS = [
    "CLAUDE.md", "README.md", ".claude/commands/*.md", "docs/BRIEF.md", "docs/ARCHITECTURE.md",
    "docs/adr/*.md", "docs/build/*.md", "docs/build/chunks/*.md", "docs/review/ADJUDICATION-R2.md",
]

findings: list[str] = []
section_rows: list[tuple[str, str, str, str]] = []


def fail(msg: str) -> None:
    findings.append(msg)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def ids_in(text: str) -> list[str]:
    return ID_RE.findall(text)


# ---------------------------------------------------------------- 1 and 2: IDs and dependencies

def chunk_files() -> dict[str, Path]:
    out = {}
    for p in sorted(CHUNK_DIR.glob("C*.md")):
        m = re.match(rf"({ID})-", p.name)
        if not m:
            fail(f"chunk file name not recognized: {p.name}")
            continue
        if m.group(1) in out:
            fail(f"two chunk files for {m.group(1)}")
        out[m.group(1)] = p
    return out


def header_deps(p: Path) -> set[str]:
    text = read(p)
    m = re.search(r"\*\*Depends on:\*\*(.*?)(?:\*\*Parallel with|\*\*Hard cut|$)", text, re.S)
    if not m:
        fail(f"{p.name}: no 'Depends on' in header")
        return set()
    seg = m.group(1).split("\n\n")[0]
    seg = re.sub(r"\([^)]*\)", "", seg)  # drop parenthetical notes such as "(runs after C04a ...)"
    return set(ids_in(seg))


def plan_table() -> dict[str, set[str]]:
    out = {}
    for line in read(BUILD_PLAN).splitlines():
        m = re.match(rf"\|\s*({ID})\s*\|([^|]*)\|([^|]*)\|([^|]*)\|", line)
        if m:
            deps = set() if m.group(4).strip() == "none" else set(ids_in(m.group(4)))
            out[m.group(1)] = deps
    return out


def plan_graph() -> dict[str, set[str]]:
    text = read(BUILD_PLAN)
    block = re.search(r"```mermaid(.*?)```", text, re.S)
    if not block:
        fail("BUILD_PLAN: no mermaid dependency graph")
        return {}
    deps: dict[str, set[str]] = {}
    for line in block.group(1).splitlines():
        m = re.match(r"\s*(\w+)(?:\[[^\]]*\])?\s*-->\s*(\w+)", line)
        if not m:
            continue
        a, b = m.group(1), m.group(2)
        for node in (a, b):
            if re.fullmatch(ID, node):
                deps.setdefault(node, set())
        if re.fullmatch(ID, a) and re.fullmatch(ID, b):
            deps[b].add(a)
    return deps


def plan_line(label: str) -> list[str]:
    m = re.search(rf"\*\*{re.escape(label)}\*\*[^:]*:\s*([^\n]*)", read(BUILD_PLAN))
    if not m:
        fail(f"BUILD_PLAN: no '{label}' line")
        return []
    first = m.group(1).split("**")[0]
    return ids_in(first)


def progress_ids() -> list[str]:
    out = []
    for line in read(PROGRESS).splitlines():
        m = re.match(rf"\|\s*({ID})\s", line)
        if m:
            out.append(m.group(1))
    return out


def check_structure() -> None:
    files = chunk_files()
    table = plan_table()
    graph = plan_graph()
    order = plan_line("Build order")
    floor = plan_line("Floor-only route:")
    deferred = plan_line("Deferred in the Floor-only branch:")
    prog = progress_ids()

    sets = {
        "chunk files": set(files), "BUILD_PLAN table": set(table), "BUILD_PLAN graph": set(graph),
        "build order": set(order), "PROGRESS board": set(prog),
    }
    ref = set(files)
    for name, s in sets.items():
        if s != ref:
            fail(f"chunk IDs differ: {name} has extra {sorted(s - ref)} and lacks {sorted(ref - s)} (compared with chunk files)")
    if len(order) != len(set(order)):
        fail("build order lists a chunk twice")
    if len(prog) != len(set(prog)):
        fail("PROGRESS lists a chunk twice")

    for cid, p in files.items():
        h = header_deps(p)
        if cid in table and h != table[cid]:
            fail(f"{cid}: header depends on {sorted(h)} but BUILD_PLAN table says {sorted(table[cid])}")
        if cid in graph and h != graph[cid]:
            fail(f"{cid}: header depends on {sorted(h)} but the graph says {sorted(graph[cid])}")
        for d in h:
            if d not in files:
                fail(f"{cid}: depends on unknown chunk {d}")
        title = read(p).splitlines()[0]
        if not title.startswith(f"# {cid}:"):
            fail(f"{p.name}: first line should start with '# {cid}:'")

    # cycles
    deps = {c: header_deps(p) for c, p in files.items()}
    state: dict[str, int] = {}

    def visit(n: str, stack: list[str]) -> None:
        if state.get(n) == 1:
            fail(f"dependency cycle: {' -> '.join(stack + [n])}")
            return
        if state.get(n) == 2:
            return
        state[n] = 1
        for d in sorted(deps.get(n, ())):
            visit(d, stack + [n])
        state[n] = 2

    for n in sorted(deps):
        visit(n, [])

    # order
    pos = {c: i for i, c in enumerate(order)}
    for c, ds in deps.items():
        for d in ds:
            if c in pos and d in pos and pos[d] >= pos[c]:
                fail(f"{c} depends on {d}, which comes later in the build order")

    # Floor-only route walk
    floor_set = set(floor)
    if floor_set & set(deferred):
        fail(f"Floor-only route and deferred set overlap: {sorted(floor_set & set(deferred))}")
    done: set[str] = set()
    for c in floor:
        missing = deps.get(c, set()) - done
        if missing:
            fail(f"Floor-only route: {c} needs {sorted(missing)}, which are not done earlier on the route")
        done.add(c)
    # every non-deferred chunk before opening night must not depend on a deferred chunk
    for c in floor:
        bad = deps.get(c, set()) & set(deferred)
        if bad:
            fail(f"Floor-only route: {c} depends on deferred {sorted(bad)}")

    # status vocabulary
    text = read(PROGRESS)
    for line in text.splitlines():
        m = re.match(rf"\|\s*({ID})[^|]*\|\s*([^|]*)\|", line)
        if m:
            status = m.group(2).strip()
            if not re.fullmatch(r"not started|done|deferred \(after opening night\)|in progress \(checkpoint \d+\)|blocked: .+", status):
                fail(f"PROGRESS: {m.group(1)} has unknown status '{status}'")

    # required sections in every chunk file
    required = ["## Goal", "## Reading list", "## Scope", "**Out of scope:**", "## Contracts",
                "## Definition of done", "## What I check", "## Size estimate and checkpoints",
                "## Usage budget", "## Risks", "**Changelog:**"]
    for cid, p in files.items():
        t = read(p)
        for r in required:
            if r not in t:
                fail(f"{cid}: missing section '{r}'")


# ---------------------------------------------------------------- 4: reading lists

PATH_TOKEN = re.compile(r"`([^`\s]+)`")


# Engine module paths written relative to src/nbadfs/ (for example select/solver.py).
MODULE_DIRS = ("ingest/", "facts/", "news/", "history/", "projections/", "scoring/", "sim/", "field/",
               "settle/", "select/", "validate/", "export/", "resolve/", "brief/", "learn/", "llm/", "schemas/")


def looks_like_path(tok: str) -> bool:
    if tok.startswith(("/", "http", "uv ", "~")):
        return False  # slash commands, URLs, commands, home-relative settings values
    if "/" in tok:
        return True
    # a bare file name counts only if it exists at the repo root (for example CLAUDE.md)
    return tok.endswith((".md", ".py", ".txt", ".toml", ".json", ".csv", ".parquet")) and (ROOT / tok).exists()


def is_future(path: str) -> bool:
    return path.startswith(FUTURE_PREFIXES) or path.startswith(MODULE_DIRS) or path in FUTURE_FILES


def resolve(tok: str) -> Path | None:
    tok = tok.strip().rstrip(",.;:")
    tok = tok.split("#")[0]
    if tok.endswith("/"):
        tok = tok[:-1]
    p = ROOT / tok
    return p


def norm(s: str) -> str:
    return re.sub(r"[\"'`*“”‘’]", "", s).lower()


def heading_for(text: str, num: str) -> str | None:
    pat = re.compile(rf"^#{{1,4}}\s+{re.escape(num)}(?:[.\s:]|$)(.*)$", re.M)
    m = pat.search(text)
    if m:
        return m.group(0).strip()
    return None


def strip_parentheticals(seg: str) -> str:
    """Drop backticked text and parenthetical notes so 'sections 2.1 (the x bullet), 2.2' reads as '2.1, 2.2'."""
    seg = re.sub(r"`[^`]*`", "", seg)
    prev = None
    while prev != seg:
        prev = seg
        seg = re.sub(r"\([^()]*\)", "", seg)
    return seg


def section_numbers(seg: str) -> list[str]:
    nums: list[str] = []
    seg = strip_parentheticals(seg)
    num = r"\d+(?:\.\d+)*[a-z]?"
    for m in re.finditer(rf"\bsections?\s+({num}(?:\s*(?:,|;|\band\b|\bto\b)\s*(?:\band\b\s*)?{num})*)", seg):
        body = m.group(1)
        parts = [x for x in re.split(r"\s*(?:,|;|\band\b)\s*", body) if x.strip()]
        for part in parts:
            if " to " in part:
                a, b = [x.strip() for x in part.split(" to ")]
                nums.extend([a, b])
            elif part.strip():
                nums.append(part.strip())
    return nums


def entry_numbers(seg: str) -> list[str]:
    out: list[str] = []
    for m in re.finditer(r"\bentr(?:y|ies)\s+((?:R2-)?\d+(?:\s*(?:,|and|to)\s*(?:R2-)?\d+)*)", seg):
        body = m.group(1)
        if " to " in body:
            a, b = [x.strip() for x in body.split(" to ")]
            pre = "R2-" if a.startswith("R2-") else ""
            for k in range(int(a.replace("R2-", "")), int(b.replace("R2-", "")) + 1):
                out.append(f"{pre}{k}")
        else:
            out.extend(x.strip() for x in re.split(r"\s*(?:,|and)\s*", body) if x.strip())
    return out


def check_reading_lists() -> None:
    for p in sorted(CHUNK_DIR.glob("C*.md")):
        cid = p.name.split("-")[0]
        text = read(p)
        m = re.search(r"## Reading list[^\n]*\n(.*?)(?=\n## )", text, re.S)
        if not m:
            continue
        for line in m.group(1).splitlines():
            if not line.strip():
                continue
            toks = [(mm.start(), mm.group(1)) for mm in PATH_TOKEN.finditer(line) if looks_like_path(mm.group(1))]
            if not toks:
                continue
            for i, (start, tok) in enumerate(toks):
                end = toks[i + 1][0] if i + 1 < len(toks) else len(line)
                seg = line[start + len(tok) + 2:end]
                path = resolve(tok)
                rel = tok.strip().rstrip(",.;:")
                if not path.exists():
                    if is_future(rel):
                        continue
                    fail(f"{cid} reading list: file not found: {rel}")
                    continue
                if path.is_dir():
                    continue
                target = read(path) if path.suffix in (".md", ".txt", ".py") else ""
                for num in section_numbers(seg):
                    h = heading_for(target, num)
                    section_rows.append((cid, rel, f"section {num}", h or "NOT FOUND"))
                    if not h:
                        fail(f"{cid} reading list: {rel} has no section {num}")
                if path.name.startswith("ADJUDICATION"):
                    for e in entry_numbers(seg):
                        h = heading_for(target, e)
                        section_rows.append((cid, rel, f"entry {e}", h or "NOT FOUND"))
                        if not h:
                            fail(f"{cid} reading list: {rel} has no entry {e}")
                for q in re.findall(r"\"([^\"]+)\"", seg):
                    if q.startswith(("uv ", "dfs ")) or "/" in q:
                        continue
                    found = norm(q) in norm(target)
                    section_rows.append((cid, rel, f'"{q}"', "found" if found else "NOT FOUND"))
                    if not found:
                        fail(f"{cid} reading list: '{q}' not found in {rel}")


# ---------------------------------------------------------------- 5: dangling paths anywhere

def authored(globs: list[str]) -> list[Path]:
    out: list[Path] = []
    for g in globs:
        out.extend(sorted(ROOT.glob(g)))
    return out


def check_paths() -> None:
    for p in authored(PATH_CHECK_GLOBS):
        for n, line in enumerate(read(p).splitlines(), 1):
            for tok in PATH_TOKEN.findall(line):
                if not looks_like_path(tok):
                    continue
                rel = tok.strip().rstrip(",.;:")
                if not rel.startswith(("docs/", "spikes/", "scripts/", ".claude/")):
                    continue
                if any(ch in rel for ch in "<>*{}") or " " in rel:
                    continue
                if is_future(rel):
                    continue
                if not (ROOT / rel).exists():
                    fail(f"{p.relative_to(ROOT)}:{n}: path not found: {rel}")


# ---------------------------------------------------------------- 6: dashes

def check_dashes() -> None:
    for p in authored(AUTHORED_GLOBS):
        for n, line in enumerate(read(p).splitlines(), 1):
            if "—" in line:
                fail(f"{p.relative_to(ROOT)}:{n}: em dash")
            if "–" in line:
                fail(f"{p.relative_to(ROOT)}:{n}: en dash")


def main(argv: list[str]) -> int:
    quick = "--quick" in argv
    check_structure()
    check_reading_lists()
    check_paths()
    check_dashes()
    if "--show-sections" in argv:
        print("chunk | file | reference | resolves to")
        for row in section_rows:
            print(" | ".join(row))
        print()
    if findings:
        print(f"check_docs: {len(findings)} finding(s)")
        for f in findings:
            print("  -", f)
        return 1
    if not quick:
        print(f"check_docs: all checks passed ({len(section_rows)} reading-list references resolved)")
    else:
        print("check_docs: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
