# CLAUDE.md

NBA DFS engine for DraftKings (Classic and Showdown Captain Mode), built in chunked Claude Code sessions and run nightly on this Windows laptop. The owner is a product manager, not an engineer: write to him in plain language, lead with the answer, define jargon once, give every technical choice one sentence on what it means for results, cost or his nightly workload, and use no em dashes.

## What this repo is

- `docs/BRIEF.md`: the living requirements. The two goals as decided on 2026-10-14: Goal 1 is top-1% prize equity per contest (expected dollars from top-1% places after tie splits, as a share of the top-1% pool); Goal 2 is the probability of a severe-drawdown night (winnings under 25% of fees).
- `docs/ARCHITECTURE.md` (v4), `docs/adr/` (ADR-001 to ADR-028; superseded ones are kept), `docs/review/ADJUDICATION.md` (every design change traces to an entry there).
- `docs/build/BUILD_PLAN.md`, `docs/build/CONTRACTS.md`, `docs/build/chunks/Cxx-*.md`, `docs/build/PROGRESS.md`: the build.
- `src/nbadfs/`: the engine (once built). `tests/`, `fixtures/`. Runtime folders `inbox/`, `data/`, `runs/`, `out/` are never committed.

## Build-session protocol (`/run-chunk <id>`)

1. Read `docs/build/PROGRESS.md` first. If the chunk is `done`, stop and say so. If it is `in progress (checkpoint N)`, resume from the handoff notes.
2. Read the chunk file `docs/build/chunks/<id>-*.md` second, then only the files and sections its reading list names. Do not read the whole architecture.
3. Check that the chunk's dependencies are `done` in PROGRESS.md. If not, stop and tell the owner which chunk to run first.
4. Build only this chunk's scope. Anything else you find goes in PROGRESS.md under "Things found but out of scope".
5. Contracts first: confirm the consumed contracts exist in `src/nbadfs/schemas/`; produce this chunk's contracts as code and fixtures before behavior.
6. Work checkpoint by checkpoint. At each checkpoint the tests pass and the engine still runs. If the session is running long, stop at the last checkpoint, write handoff notes in PROGRESS.md, commit, and tell the owner to run `/run-chunk <id>` again in a new session.
7. Consult the advisor (`/advisor` if configured; otherwise an independent reviewer subagent with model `fable` that reads only the chunk file and the code in question) when stuck on one problem for more than about 20 minutes, and once before declaring the chunk done, with one named question. Log each consultation in `docs/research/advisor-log.md`. Never call the advisor during a nightly run.
8. Run the tests: `uv run pytest -m smoke` (under 60 seconds) and this chunk's tests; the full suite where it exists (under 5 minutes).
9. Do the chunk's "What I check" step yourself first, and tell the owner the plain-language check and its expected result.
10. Update PROGRESS.md: status, finished date, commit hash, usage (ask the owner to read `/usage` and type the five-hour and weekly shares), deviations, handoff notes.
11. Commit with the chunk ID first in the message (`C04: contest facts, injury report, Floor portfolio`). Do not push unless the owner asks.
12. Stop. Do not start the next chunk. End with: what was built, what the owner checks, and the one line to type next.

## Rules that never bend

- Never write into `out/uploads/` by any tool other than the exporter (`uv run dfs ...`). Never fetch or script anything on `draftkings.com`. Never read the private standings folder or raw standings files (they carry other users' names).
- Only DraftKings validity blocks a file. Every other check labels.
- Deterministic by construction: no wall-clock solver limits; every random draw keyed by stable identifiers; the same inputs give byte-identical files.
- No new research memos before Oct 20 except a spike a chunk needs. Research ends when it resolves the named decision.
- On a game night: no edits to `src/` from 60 minutes before the first lock to the last lock (`dfs unlock` lifts it and is recorded). No environment repair inside the entry window; a failing preflight sends the night to the no-LLM launcher path.
- LLM outputs are files validated by code before anything reads them. The LLM never writes lineups, exposures, or upload files.
- The data posture is permissive plus `nba_api` for box scores and game logs only (Decision D1). ESPN JSON, RotoWire, sportsbooks and DraftKings endpoints are off. Nothing ever defeats a technical block.

## Nightly runs (once the engine exists)

`/night`, `/news`, `/swap`, `/status`, `/results` are thin wrappers over `uv run dfs` commands. Fresh session for `/news` and `/swap`. No advisor calls, no design work, no `src/` edits during a night. Report in plain language: the four states per slate, what is off, the file to upload, and the one next action.

## Writing for the owner

Lead with the answer. Plain language; define jargon the first time. One sentence per technical choice on what it means for results, cost or workload. No em dashes. When you say something is verified, show what you ran and what came back.
