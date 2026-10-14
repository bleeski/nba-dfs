# CLAUDE.md

NBA DFS engine for DraftKings (Classic and Showdown Captain Mode), built in chunked Claude Code sessions and run nightly on this Windows laptop. The owner is a product manager, not an engineer: write to him in plain language, lead with the answer, define jargon once, give every technical choice one sentence on what it means for results, cost or his nightly workload, and use no em dashes.

**Changelog:** 2026-10-14 (owner's request, approved in chat): every build session updates the owner's build tracker page (step 12; started in step 3), renumbering the closing step to 13. 2026-10-14 (ADJUDICATION-R2 entry R2-33): the repository is public, so real DraftKings files, third-party downloads and the standings salt never enter git. 2026-10-14 (design final, ADJUDICATION-R2): change-control rule added; step 3 explains `deferred`; the chunk split (C04a, C04b, C11a, C11b) and the design-final file list. 2026-10-14: created.

## What this repo is

- `docs/BRIEF.md`: the living requirements. The two goals as decided on 2026-10-14: Goal 1 is top-1% prize equity per contest (expected dollars from top-1% places after tie splits, as a share of the top-1% pool); Goal 2 is the probability of a severe-drawdown night (winnings under 25% of fees).
- `docs/ARCHITECTURE.md` (v5, **design final**), `docs/adr/` (ADR-001 to ADR-031; superseded ones are kept and marked), `docs/review/ADJUDICATION.md` (round 1) and `docs/review/ADJUDICATION-R2.md` (round 2; the later word where they differ). Every design change traces to an entry in one of them.
- `docs/build/BUILD_PLAN.md`, `docs/build/CONTRACTS.md`, `docs/build/chunks/Cxx-*.md`, `docs/build/PROGRESS.md`, `docs/build/OWNER_CHECKLIST.md`: the build. `scripts/check_docs.py` checks that these files agree.
- `src/nbadfs/`: the engine (once built). `tests/`, `fixtures/`. Runtime folders `inbox/`, `data/`, `runs/`, `out/` are never committed.

## Build-session protocol (`/run-chunk <id>`)

1. Read `docs/build/PROGRESS.md` first. If the chunk is `done`, stop and say so. If it is `in progress (checkpoint N)`, resume from the handoff notes. If it is `deferred (after opening night)` and opening night has not passed, stop and say so.
2. Read the chunk file `docs/build/chunks/<id>-*.md` second (chunk IDs include suffixes such as `C04a`), then only the files and sections its reading list names. Do not read the whole architecture.
3. Check that the chunk's dependencies are `done` in PROGRESS.md. A dependency that is `not started`, `in progress`, `blocked` or `deferred` is not done: stop and tell the owner which chunk to run first. If every dependency is done, mark the chunk `in_progress` on the build tracker (step 12).
4. Build only this chunk's scope. Anything else you find goes in PROGRESS.md under "Things found but out of scope".
5. Contracts first: confirm the consumed contracts exist in `src/nbadfs/schemas/`; produce this chunk's contracts as code and fixtures before behavior.
6. Work checkpoint by checkpoint. At each checkpoint the tests pass and the engine still runs. If the session is running long or passes the chunk's usage budget, stop at the last checkpoint, write handoff notes in PROGRESS.md, commit, update the build tracker (step 12), and tell the owner to run `/run-chunk <id>` again in a new session.
7. Consult the advisor (`/advisor`, configured as Fable; if a session does not expose the advisor tool, an independent reviewer subagent with model `fable` that reads only the chunk file and the code in question) when stuck on one problem for more than about 20 minutes, and once before declaring the chunk done, with one named question. Log each consultation in `docs/research/advisor-log.md`. Never call the advisor during a nightly run.
8. Run the tests: `uv run pytest -m smoke` (under 60 seconds, including the docs checker) and this chunk's tests; the full suite where it exists (under 5 minutes).
9. Do the chunk's "What I check" step yourself first, and tell the owner the plain-language check and its expected result.
10. Update PROGRESS.md: status, finished date, commit hash, usage (ask the owner to read `/usage` and type the five-hour and weekly shares), deviations, handoff notes. After C04a, also record the M1 usage reading (C01 to C04a together) and say whether the Floor-only branch applies.
11. Commit with the chunk ID first in the message (`C04a: Floor core, scoring, simple points`). Do not push unless the owner asks.
12. Update the build tracker, the owner's progress page at https://claude.ai/artifact/894yJvrf5PpRwaKXyxA4Tm, with the `ArtifactData` tool (load it with ToolSearch if it is deferred). `get` collection `chunks`, doc_id the chunk ID (for example `C04a`), then `update` that document, passing the version you read as `if_version`. Set `status` to match PROGRESS.md (`done`; `in_progress` with the checkpoint in the note; `blocked` with the reason in the note; or `deferred`), `note` (one plain-language sentence for the owner: what was built, or where it stopped and why), `updatedAt` (ISO 8601 time) and `updatedBy` (`claude`), and when the chunk is done also `finished` (YYYY-MM-DD) and `commit` (the short hash from step 11). PROGRESS.md stays the source of truth: if the tool is unavailable or the write fails, say so in the closing message and carry on; never block a chunk on the tracker, and never touch it during a nightly run.
13. Stop. Do not start the next chunk. End with: what was built, what the owner checks, and the one line to type next.

## Change control (the design is final as of 2026-10-14)

- A build session that finds a design problem (a contract that cannot work as written, a rule that contradicts another, a test that cannot pass for a reason in the design, a dependency the plan missed) logs it as a **change request** in PROGRESS.md under "Change requests": the problem, why it matters for results, opening night, cost or workload, the proposed change, and whether it blocks the chunk.
- If it blocks the chunk, the session stops at the last passing checkpoint, writes handoff notes, commits, and asks the owner. If it does not block, the session finishes its scope as written and raises the request in its closing message.
- **Nothing in the design changes without the owner's approval:** not the brief, the architecture, a decision record, a contract, the build plan, or a chunk's scope. An approved change edits the affected files in the same commit, records the owner's answer in PROGRESS.md, and gets a changelog line in each file it touches.
- Not a change request: a one-sentence clarification of a contract that changes no field, signature or rule (record it in PROGRESS.md), a bug fix inside the chunk's own scope, or adding a contract or settings key that the chunk's own file says it adds.

## Rules that never bend

- The GitHub repository is public (as of 2026-10-14). Real DraftKings files (the owner's entries, salary files, post-lock downloads, standings), third-party downloads, runtime data and the standings salt never enter git; real-file fixtures are local only and rebuilt by `scripts/build_fixtures.py` (CONTRACTS section 14).
- Never write into `out/uploads/` by any tool other than the exporter (`uv run dfs ...`). Never fetch or script anything on `draftkings.com`. Never read the private standings folder or raw standings files (they carry other users' names).
- Only DraftKings validity blocks a file. Every other check labels.
- Deterministic by construction: no wall-clock solver limits; every random draw keyed by stable identifiers; the same inputs give byte-identical files.
- No new research memos before Oct 20 except a spike a chunk needs. Research ends when it resolves the named decision.
- On a game night: no edits to `src/` from 60 minutes before the first lock to the last lock (`dfs unlock` lifts it and is recorded). No environment repair inside the entry window; a failing preflight sends the night to the no-LLM launcher path.
- LLM outputs are files validated by code before anything reads them. The LLM never writes lineups, exposures, or upload files.
- The data posture is permissive plus `nba_api` for box scores and game logs only (Decision D1). ESPN JSON, RotoWire, sportsbooks and DraftKings endpoints are off. Nothing ever defeats a technical block.
- Drills on saved nights (`--as-of`) write only under `runs/drills/`; they never touch live records.

## Nightly runs (once the engine exists)

`/night`, `/news`, `/swap`, `/status`, `/results` are thin wrappers over `uv run dfs` commands (built in C11a; `/results` in C13). Fresh session for `/news` and `/swap`. No advisor calls, no design work, no `src/` edits during a night. Report in plain language: the four states per slate, what is off or stale, the file to upload (and any rows labeled "tight"), and the one next action.

## Writing for the owner

Lead with the answer. Plain language; define jargon the first time. One sentence per technical choice on what it means for results, cost or workload. No em dashes. When you say something is verified, show what you ran and what came back.
