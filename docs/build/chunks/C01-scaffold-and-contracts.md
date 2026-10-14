# C01: Scaffold and contracts

**State:** M0. **Size:** L (one session, about 2 to 3 hours, three checkpoints; relabeled from M by advisor consultation 5). **Depends on:** nothing. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final gate, advisor consultation 5): relabeled L; `scripts/check_docs.py` leaves the reading list (C01 only runs it); checkpoints reordered so the fixture builder C02 needs comes before the tiny fixtures, which may move to the start of C08 if this session runs long; binomial hand values come from a standalone script; the settings test skips the `[field.<family>]` placeholder. 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): the tiny fixtures C01 writes are eleven settlement fixtures with hand values (fields as explicit point masses, compared to 1e-9) and one property fixture (`tiny_crn_swap`), and the infeasible-cap and same-team cases move to C09 and C10; the conservation test covers the settlement fixtures; `floor` starts enabled and `enable` and `disable` join the stubbed commands; `lineup_hash` is implemented here as a pure function with tests; `scripts/build_fixtures.py` builds a fixture folder for every archived night (with its post-lock file), copies the April 2026 NBA salary file and the entry-history export from their local paths, and leaves out the WNBA file. 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): `restrict` joins the stubbed commands; the conservation test runs over each tiny fixture that carries a payout table. 2026-10-14 (ADJUDICATION-R2 entry R2-33, the owner's real files of Oct 14): the repository is public, so real DraftKings files and third-party downloads become local-only fixtures built by `scripts/build_fixtures.py`, `realfiles` tests fail when a file is missing, and the standings salt is never committed. 2026-10-14 (ADJUDICATION-R2): the contracts it types are v2 (settlement, field, identity, drill mode, time to lock, capability fingerprints); the new tiny fixtures are hand-computed under the single tie split (R2-2 to R2-5); `scripts/check_docs.py` wired into the smoke suite (R2-21); usage budget added. 2026-10-14: created.

## Goal, and why it sits first

Turn every interface in `docs/build/CONTRACTS.md` into code and fixtures, so that each later chunk builds against typed models and stub signatures rather than prose, and can be tested on its own. Create the repo scaffold, the CLI skeleton with every command stubbed, the configuration files, the test harness, and the fixture directory. Nothing in this chunk computes anything real, except the hand-computed expected values written into the tiny fixtures and `lineup_hash` (a pure function, CONTRACTS section 10, that every later chunk shares).

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` in full (about 7,000 words; it is the specification for this chunk).
2. `docs/adr/ADR-017-tech-stack.md` (Python 3.13, uv, numpy, Typer, pydantic; DuckDB after the MVP).
3. `docs/adr/ADR-021-determinism.md`.
4. `docs/adr/ADR-023-release-states-and-feature-flags.md` and `docs/adr/ADR-030-operations-v2-floor-route-lock-labels-drills-exports.md`, the "Versioned rehearsals" bullet only (the capability flags file).
5. `docs/adr/ADR-029-settlement-v2-single-tie-split-joint-ranks-realized-outcomes.md` (the rules the tiny fixtures must encode).
6. `CLAUDE.md` (the protocol you are following). `scripts/check_docs.py` is already in the repo; you only run it from a test, so do not read it.

## Scope

**Build:**

- `pyproject.toml` managed by uv: package `nbadfs` under `src/`, console script `dfs = nbadfs.cli:app`, dependencies `typer`, `pydantic>=2`, `numpy`, `scipy`, `pandas`, `pyarrow`, `httpx`, `pdfplumber`, `swiglpk`, `ortools`, `nba_api`, `pytest`, `hypothesis`, `tomli`/`tomllib`. Pin versions. `uv sync` must succeed on this Windows laptop.
- `src/nbadfs/schemas/`: one module per CONTRACTS section (`dk_files.py`, `slate.py`, `contest_facts.py`, `news.py`, `injury.py`, `history.py`, `projections.py`, `scenarios.py`, `field.py`, `settlement.py`, `portfolio.py`, `ledger.py`, `manifest.py`, `brief.py`, `capabilities.py`) with pydantic models for every named model in CONTRACTS sections 1 to 12 (including `PayoutCurve`, `InjuryState`, `FieldScores`, `Settlement` with its four arrays, `UploadFile.tight_rows`, `RunManifest.drill_id`), field names exactly as written there, docstrings carrying each contract's rule. Numpy arrays are typed as `numpy.ndarray` with a validator on dtype and shape where CONTRACTS states them; a validator rejects float16 for any points or score array (CONTRACTS section 7).
- Stub signatures with docstrings (raising `NotImplementedError("chunk Cxx")`) for every function named in CONTRACTS: `identity.match`, `score_line`, `p_above`, `p_equal`, `settle`, `night_goal2`, `select_contest`, `validate`, `export`, `repair`, `resolve`, `swap`, and the rest. These pin the signatures later chunks fill.
- `lineup_hash` (CONTRACTS section 10) implemented, not stubbed: a pure function, `sha1` of the sorted `f"{person_key}|{role}"` strings (`CPT` for the Captain slot, `UTIL` for every other slot in both formats), with tests: Classic slot permutations of the same players hash equal; the same six Showdown players with a different Captain hash differently; a lineup given by names and the same lineup given by DraftKings IDs hash equal once the names are matched (the test builds both `person_key|role` inputs by hand, since `identity.match` arrives in C02). C08 and C09 consume it.
- `src/nbadfs/cli.py`: a Typer app with every command in CONTRACTS section 13 registered and stubbed to print "not built yet: chunk Cxx" and exit 0; the global options `--night`, `--as-of`, `--fixtures`, `--json`, `--yes` parsed into a `Clock` and a `Paths` object (CONTRACTS 1.1; C03 wires the lock rules and drill mode to them); the exit-code convention (0, 2, 3, 4, 5).
- `src/nbadfs/settings.py`: loads `config/settings.toml`, `config/posture.toml`, `config/capabilities.toml` into pydantic settings models with the defaults in CONTRACTS section 15; a test asserts every key in section 15 exists with that default and that `settle.exact_max_field` and `settle.rank_window_sd` do not; it skips the `[field.<family>]` placeholder, which has no defaults until C08 adds them.
- `config/settings.toml`, `config/posture.toml` (`posture = "permissive_plus_nba_api"`, allowed hosts list), `config/capabilities.toml` (the eight capabilities, `floor` with `enabled = true` and the other seven with `enabled = false`, each with `rehearsed_on = ""`, `rehearsed_commit = ""`, `rehearsed_paths = []`, `drill_artifact = ""`), `config/identity_overrides.toml` (empty table with a comment), `config/secrets.example.toml` (`odds_api_key = ""`); `config/secrets.toml` gitignored.
- `scripts/build_fixtures.py`: builds the **local-only** fixtures named in CONTRACTS section 14 on this laptop, idempotent, printing what it copied and the hashes: `fixtures/dk/<night>/` for every archived night in `data/archive/<night>/` (so 2026-10-14, 2026-10-15 and 2026-10-16 appear as the owner's files are archived), each with `post_lock_entries.csv` copied from the latest Classic entries download taken after that slate's first lock, when one exists; the public salary files from `spikes/dk/out/downloads/github/` except `rosteropt_nba_wnba_showdown.csv` (a WNBA file); the April 2026 NBA salary file, copied from `C:\Users\benja\Documents\dfs-os\reference-docs\sample-data\dk_nba_salaries_sample.csv` (a 2-game slate of 2026-04-15, 70 players, no `Status` column) to `fixtures/dk/public/dk_nba_2026-04-15.csv`; the owner's entry-history export, copied from `C:\Users\benja\Downloads\draftkings-contest-entry-history.csv` (432 NBA rows, R8) to `fixtures/history/entry_history.csv`; and the two injury PDFs and `player_box_2026.parquet` from `spikes/**/out/downloads/`. These folders are gitignored; nothing real or third-party is committed (the GitHub repository is public).
- A pytest marker `realfiles`: a test that needs a local-only fixture fails with a message naming the missing file and the command `uv run python scripts/build_fixtures.py`, unless the environment variable `NBADFS_ALLOW_MISSING_REALFILES=1` is set, in which case it skips.
- `config/standings_salt.txt`: created once locally with a random value if absent, gitignored, never committed (C13 hashes standings names with it).
- `fixtures/tiny/`: the twelve hand-written JSON files CONTRACTS section 14 assigns to C01, each written as its "How a tiny contest is written" paragraph says (explicit point masses per scenario; degenerate fields for counted ranks; full binomial sums otherwise): eleven settlement fixtures with the expected results **computed by hand under CONTRACTS section 9** and written into each file, and one property fixture (`tiny_crn_swap.json`, inputs only, no hand values). Counted-rank values are worked by hand in the README; binomial values come from `fixtures/tiny/compute_expected.py`, a short standalone script that does not import `nbadfs` and prints its arithmetic. `tiny_infeasible_cap_showdown.json` and `tiny_same_team_two_out.json` are written later by C09 and C10. `fixtures/synthetic/` gets only a README; C07 serializes the R9 synthetic night. `fixtures/identity/` and `fixtures/dk/layout/` get a README naming the files C02 adds.
- `tests/`: pytest configured with markers `smoke` and `slow`; `conftest.py` with fixture loaders; a smoke test per schema module that round-trips an example through JSON; a test that `uv run dfs --help` lists every command; a test that each of the eleven settlement fixtures has hand-computed values satisfying the conservation rule (payouts sum to the paid pool; top-1% allocations to the top-1% pool); the `lineup_hash` tests; `tests/test_docs.py` (marked `smoke`) that runs `scripts/check_docs.py --quick` and fails on any finding.
- `.gitignore` extended for `inbox/`, `data/`, `runs/`, `out/`, `config/secrets.toml`, `config/standings_salt.txt`, `.venv/`, and the local-only fixture folders `fixtures/dk/20*/`, `fixtures/dk/layout/`, `fixtures/dk/public/`, `fixtures/injury/`, `fixtures/history/`.
- `scripts/dfs.cmd`: a one-line Windows launcher that runs `uv run dfs %*` from the repo (C11a makes the full launcher).
- The `.claude/` folder is already present (`commands/run-chunk.md`); leave it.

**Out of scope:** any parser, any settlement arithmetic in code, any network call, DuckDB, hooks, skills.

## Contracts

- **Consumes:** none.
- **Produces:** every model in CONTRACTS sections 1 to 12 as code; the stub signatures; `lineup_hash` (implemented); the settings models (section 15); the CLI surface (section 13); the fixture set (section 14). If a contract cannot be expressed as written, that is a change request under `CLAUDE.md`; a one-sentence clarification that changes no field or rule is recorded in PROGRESS.md.

## Definition of done

- `uv sync` succeeds; `uv run dfs --help` lists `status, night, out, in, start, restrict, fact, news, swap, repair, uploaded, results, research, unlock, rehearsed, enable, disable, replay, history, digest, sim, field, drill, insure` and the global options.
- `uv run pytest -m smoke` passes in under 60 seconds and covers every schema module, the settings test, the tiny-fixture conservation test, the `lineup_hash` tests and `tests/test_docs.py`.
- The twelve files C01 writes in `fixtures/tiny/` exist (eleven settlement fixtures with hand values and one property fixture, `tiny_crn_swap.json`, with inputs only), with a README explaining each; `tiny_tie_100_60.json` says $80 each in total and $50 each in top-1% money.
- The float16 validator rejects a float16 points array (test).
- `uv run python scripts/build_fixtures.py` builds the local-only fixtures, including `fixtures/dk/2026-10-14/` from `data/archive/2026-10-14/`, `fixtures/dk/public/dk_nba_2026-04-15.csv` and `fixtures/history/entry_history.csv`, and leaves out the WNBA file; `git check-ignore` confirms every local-only folder is ignored and `git ls-files fixtures` lists only hand-written fixtures; a `realfiles` test with its file removed fails with the rebuild message, and skips when `NBADFS_ALLOW_MISSING_REALFILES=1`.

## What I check

Open a terminal in the repo and run:

```bash
uv run dfs --help
```

Expected: a list of commands including `night`, `status`, `out`, `in`, `start`, `swap`, `repair`, `uploaded`, `rehearsed`. Then:

```bash
uv run pytest -m smoke -q
```

Expected: all tests pass, in under 60 seconds.

## Size estimate and checkpoints

About 2 to 3 hours. Checkpoint 1: `pyproject.toml`, `uv sync`, the CLI skeleton, settings loading, smoke harness, `tests/test_docs.py`, the ignore rules (commit). Checkpoint 2: all schema modules and stub signatures with round-trip tests, `lineup_hash` with its tests, `scripts/build_fixtures.py` and the `realfiles` marker (commit; C02 needs the fixture builder on Thursday). Checkpoint 3: the eleven settlement fixtures with hand values, `compute_expected.py`, and the one property fixture (commit). Nothing before C08 consumes the tiny fixtures, so if the session runs long, checkpoint 3 moves to the start of C08 and PROGRESS.md says so; C01 is then done at checkpoint 2.

## Usage budget

About 35% of a five-hour window and 7% of a weekly window (estimates until M1 is measured). If the session passes 50% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **`swiglpk` or `ortools` has no wheel for Python 3.13 on Windows.** Pin to the newest version that installs; if `swiglpk` fails, note it and C04a uses OR-Tools CBC as primary (ADR-006 fallback).
- **A hand-computed tiny value is wrong.** Every tiny file shows its arithmetic line by line in the README; the conservation test catches most slips.
- **Windows path or encoding surprises in `uv`.** Pin the Python version in `pyproject.toml`; keep paths relative; note anything odd in PROGRESS.md for C02.
