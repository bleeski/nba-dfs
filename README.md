# nba-dfs

A DraftKings NBA DFS engine (Classic and Showdown Captain Mode), designed to be built in chunked Claude Code sessions and run nightly by Claude Code on one Windows laptop.

**Status (2026-10-14):** design v4 after adjudicating two independent critiques; build plan written; awaiting the owner's approval to start chunk C01. No engine code exists yet.

## Where things are

| Path | What it is |
|---|---|
| `docs/BRIEF.md` | The living requirements document: goals (as decided 2026-10-14), constraints, problems, MVP, advisor rule |
| `docs/ARCHITECTURE.md` | The design (v4): goals as math, system overview, projections, field and settlement, portfolio, LLM layer, runbook, learning, data, testing, risks, decisions |
| `docs/adr/` | One decision record per significant choice (index in `docs/adr/README.md`); superseded records are kept |
| `docs/review/ADJUDICATION.md` | The register of both critiques' items with verdicts, evidence, and the owner's escalation answers |
| `docs/build/` | `BUILD_PLAN.md` (milestones, dependency graph, critical path), `chunks/` (one file per build chunk), `PROGRESS.md` (the tracker every build session reads first and updates last) |
| `docs/research/` | Research memos (R1 to R9), prior-repo reviews (RR1 to RR4), the first-principles sketch (S1), change records (S2, S3), red-team rounds (RT1, RT2), and `advisor-log.md` |
| `docs/reference/` | The DraftKings rules files, the projection DAG draft, and the competitive-edge report |
| `docs/brief/` | The owner's original architecture brief of 2026-10-13 (history) |
| `docs/SLATE-BRIEF-MOCK.md` | A layout mock of the nightly two-minute brief |
| `spikes/` | Throwaway verification scripts and their outputs; nothing here is engine code |
| `CLAUDE.md` | The build-session protocol and the nightly rules |

## How a build session starts

Type `/run-chunk C01` (or the next chunk ID shown in `docs/build/PROGRESS.md`). The session reads the tracker and the chunk file, builds only that chunk, runs the tests, updates the tracker, commits, and stops.

## Privacy

Runtime folders (`inbox/`, `runs/`, `data/`, `out/`) are never committed: they hold DraftKings entries and standings that include other users' names.
