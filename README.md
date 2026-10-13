# nba-dfs

A DraftKings NBA DFS engine (Classic and Showdown Captain Mode), designed to be built and run nightly by Claude Code on one Windows laptop.

**Status (2026-10-13):** design only, awaiting the owner's approval. No engine code exists yet.

## Where things are

| Path | What it is |
|---|---|
| `docs/ARCHITECTURE.md` | The design: goals as math, system overview, projections, field, portfolio, LLM layer, runbook, learning, data, testing, risks, build plan, decisions |
| `docs/adr/` | One decision record per significant choice (index in `docs/adr/README.md`) |
| `docs/research/` | Research memos (R1 to R9), prior-repo reviews (RR1 to RR4), the first-principles sketch (S1), repo-review changes (S2), red-team rounds (RT1, RT2) |
| `docs/brief/` | The owner's architecture brief |
| `docs/SLATE-BRIEF-MOCK.md` | A layout mock of the nightly two-minute brief |
| `spikes/` | Throwaway verification scripts and their outputs; nothing here is engine code |

## Privacy

Runtime folders (`inbox/`, `runs/`, `data/`, `out/`) are never committed: they hold DraftKings entries and standings that include other users' names.
