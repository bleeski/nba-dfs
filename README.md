# nba-dfs

A DraftKings NBA DFS engine (Classic and Showdown Captain Mode), designed to be built in chunked Claude Code sessions and run nightly by Claude Code on one Windows laptop.

**Status (2026-10-14):** **design final** (architecture v5) after two rounds of independent review; build plan, contracts and chunk files ready; awaiting the owner's approval to start chunk C01. No engine code exists yet. From here the design changes only through the change-control rule in `CLAUDE.md`.

**Changelog:** 2026-10-14: privacy section corrected (the repository is public). 2026-10-14 (design final): round 2 adjudication, owner checklist, docs checker, and the chunk split added to the index. 2026-10-14: created.

## Where things are

| Path | What it is |
|---|---|
| `docs/BRIEF.md` | The living requirements document: goals (as decided 2026-10-14), constraints, problems, MVP, advisor rule |
| `docs/ARCHITECTURE.md` | The design (v5, final): goals as math, system overview, projections, field and settlement, portfolio, LLM layer, runbook, learning, data, testing, risks, decisions |
| `docs/adr/` | One decision record per significant choice, ADR-001 to ADR-031 (index in `docs/adr/README.md`); superseded records are kept and marked |
| `docs/review/ADJUDICATION.md` | Round 1: the register of both first critiques' items with verdicts, evidence, and the owner's escalation answers |
| `docs/review/ADJUDICATION-R2.md` | Round 2: the rulings on the two final reviews, with the verification log; the later word where the rounds differ |
| `docs/build/` | `BUILD_PLAN.md` (milestones, dependency graph, critical path, calendar), `CONTRACTS.md` (the interfaces C01 turns into code), `chunks/` (one file per build chunk, IDs C01 to C22 with C04a, C04b, C11a, C11b), `PROGRESS.md` (the tracker every build session reads first and updates last), `OWNER_CHECKLIST.md` (the owner's day-by-day work plan) |
| `docs/research/` | Research memos (R1 to R9), prior-repo reviews (RR1 to RR4), the first-principles sketch (S1), change records (S2, S3), red-team rounds (RT1, RT2), and `advisor-log.md` |
| `docs/reference/` | The DraftKings rules files, the projection DAG draft, and the competitive-edge report |
| `docs/brief/` | The owner's original architecture brief of 2026-10-13 (history) |
| `docs/SLATE-BRIEF-MOCK.md` | A layout mock of the nightly two-minute brief |
| `scripts/check_docs.py` | Consistency checks across the build documents (reading lists, chunk IDs, dependencies, the Floor-only route, no em dashes) |
| `spikes/` | Throwaway verification scripts and their outputs; nothing here is engine code |
| `CLAUDE.md` | The build-session protocol, change control, and the nightly rules |

## How a build session starts

Type `/run-chunk C01` (or the next chunk ID shown in `docs/build/PROGRESS.md`). The session reads the tracker and the chunk file, builds only that chunk, runs the tests, updates the tracker, commits, and stops.

## Privacy

This repository is **public** on GitHub (as of 2026-10-14). Runtime folders (`inbox/`, `runs/`, `data/`, `out/`) are never committed: they hold DraftKings entries and standings that include other users' names. Real DraftKings files and third-party downloads used as test fixtures are local only (gitignored) and rebuilt by `scripts/build_fixtures.py`; the standings-hashing salt is never committed.
