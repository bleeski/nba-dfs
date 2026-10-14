# C04b: Injury report, `dfs status --apply`, payout pastes, entry history, contest-facts cache

**State:** Floor. **Size:** M (one session, about 1.5 to 2 hours, three checkpoints). **Depends on:** C04a. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the report's team names map through C02's team map; payout tests use the tables the owner pastes plus written examples of the other layouts; the entry-history test reads the export copied by `scripts/build_fixtures.py`; the owner's check can run as a drill on the saved Oct 15 night if this chunk slips to Saturday. 2026-10-14 (ADJUDICATION-R2): created from the second half of v1's C04 (R2-1). The injury report merges per team and keeps a NOT YET SUBMITTED team's earlier statuses (R2-12); report names follow the person-key rules (R2-9); `dfs status --apply` moves here from C10 because this chunk owns the injury adapter (advisor consultation 3).

## Goal, and why it sits here

Give the Floor its two sets of outside facts: the official injury report, merged across reports so a team that has not filed yet keeps its earlier statuses, with `dfs status --apply` turning a new official status into facts and a repair; and real payout facts (pasted tables, the entry-history export, a cache), so contests stop running on defaults. It can run on Friday Oct 16 or slip to Saturday without harm: no preseason injury reports exist (R4), so the parser's first live use is Monday Oct 19 evening, and payouts are first needed by C08.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` the "Person key" preamble (the `Last, First` rule); sections 2.3, 2.4, 2.6, 3.1 (the "Team codes" bullet), 3.2, 4.2 (the precedence rule), 4.4, 13 (`dfs status --apply`), 15 (`[facts]`).
2. `docs/ARCHITECTURE.md` section 3 component rows 4 and 5; section 10 "Sources table" (the official injury report row).
3. `docs/research/R4-data-sources.md` section 4.3 (the injury report: URL patterns, cadence, NOT YET SUBMITTED, parser evidence) and `spikes/data/s03g_injury_pdf_parse_v3.py` (the working parser to port).
4. `docs/research/R8-user-nba-history.md` (paid-share facts) and `spikes/history/nba_entry_history.py` (the parser to port, per ADR-018).
5. `docs/review/ADJUDICATION.md` entry 1 only (contest facts status).

## Scope

**Build:**

- `ingest/injury_report.py`: fetch the latest official injury report PDF trying both naming patterns (15-minute slots; hourly file by last-modified), snapshot it under `data/snapshots/`, parse rows (port the v3 spike parser) including NOT YET SUBMITTED, match names with the person-key rules (`Last, First` flipped first), map the report's full team names to DraftKings codes through C02's team map (`ingest/teams.py`), map statuses; maintain `InjuryState` by the merge rule (CONTRACTS 2.6): a team's newest submitted section replaces its earlier statuses, and a NOT YET SUBMITTED team keeps its last submitted statuses labeled `cached:<report_time>`; rate-limited; fails soft (the brief marks "not checked for injuries").
- `dfs status`: prints the injury-report diff since the last run, including teams still cached. `dfs status --apply`: writes acting `official_report` facts for each changed status (through `news/state.py` from C04a, so supersession and precedence apply) and runs the repair (the same path as `dfs out` with the re-solve off), through the run lock.
- The Floor and brief-lite read `InjuryState`: `p_active` from official statuses; the brief lists the report's time and any cached teams.
- `facts/payout_paste.py`: the paste parser (CONTRACTS 2.3) with tests on the tables the owner pastes (at least two) plus written examples of the GPP, double-up, satellite, Top-N and Showdown layouts in R6 and R8's formats.
- `facts/entry_history.py`: the ported 14-column parser with tests on the owner's real export (`fixtures/history/entry_history.csv`, copied by `scripts/build_fixtures.py`).
- `facts/cache.py`: `data/contest_facts_cache.json` keyed by (name pattern, fee, field-size bucket); a contest seen before is "template" without a new paste; a paste upgrades it to "verified". `facts/contests.py` (from C04a) now prefers paste, then cache, then defaults.

**Out of scope:** the news watcher (C17), standings (C13, C14), the researcher (C11b), `dfs start` (C11a).

## Contracts

- **Consumes:** `NewsState`, `FactRecord` supersession, `ContestFacts` defaults, the Floor and the repair path (C04a); `identity.match` and the team map `ingest/teams.py` (C02); `export`, `Ledger`, the run lock (C03).
- **Produces:** `InjuryState` and the injury-report adapter with its snapshot format; `dfs status --apply`; `PayoutCurve`; `ContestFacts` with `verified` and `template` status; the facts cache.

## Definition of done

- Injury-report tests: both March 2026 PDFs parse with 0 unrecognized statuses; both URL patterns are tried; a 404 fails soft with the brief label; the 11:00 AM report followed by the 5:30 PM report reproduces R4's Anthony Edwards change (Questionable to Available).
- Merge tests: a team that is NOT YET SUBMITTED in a newer report keeps its earlier Out and Questionable statuses, labeled cached; a team's new submitted section replaces its earlier statuses; a report never wipes a team it did not cover.
- `dfs status --apply` test: a new official Out writes an acting fact and produces a repaired file in under 10 seconds, leaving every other row unchanged; a user `dfs in` does not override an official Out unless the owner vetoes the official fact.
- Payout paste tests on the owner's pasted tables (at least two) and the written GPP, double-up, satellite, Top-N and Showdown examples; the cache test: a contest seen in the entry-history export is "template" on its next appearance; a later paste upgrades it to "verified".
- Entry-history parser test on the owner's real export, `fixtures/history/entry_history.csv` (432 NBA rows in R8).

## What I check

Paste one of your test contests' payout tables into `inbox/payouts/<contest_id>.txt`, then run:

```bash
uv run dfs night --floor
```

Expected: that contest's brief line shows facts status "verified"; the brief says "injury report checked at <time>" (or "not checked for injuries" if no report is posted yet, which is normal in preseason). Then run `uv run dfs status` and see the injury-report line with its time. If this chunk runs on Saturday (no games), run the same check as a drill on the saved Oct 15 night instead: `uv run dfs night --floor --night 2026-10-15 --as-of "2026-10-15T17:00-05:00"` (the first line says DRILL; the Oct 15 contest whose payout table you saved on Thursday shows "verified").

## Size estimate and checkpoints

About 1.5 to 2 hours. Checkpoint 1: the injury adapter with the merge rule and its tests (commit). Checkpoint 2: `dfs status --apply` through facts and the repair (commit). Checkpoint 3: the payout paste, entry history and cache (commit; if time runs short, this checkpoint moves to the start of C08, its first real consumer, and PROGRESS.md says so).

## Usage budget

About 25% of a five-hour window and 4% of a weekly window (estimates). If the session passes 40% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **The 2026-27 injury-report file naming is unknown until Oct 19.** The adapter tries both known patterns and a directory probe; a miss is a label, not a failure. Parser fixes are allowed Monday evening (no games that night), followed by a replay drill because the capability's source changed (ADR-030).
- **Names in the report do not match the pool.** Unmatched names are listed in the brief for a manual `dfs out`; an override line fixes repeats.
- **No preseason reports to test live.** The March fixtures carry NOT YET SUBMITTED rows, which is the case that matters on opening night.
