# C01: Scaffold and contracts

**State:** M0. **Size:** M (one session, about 1 to 2 hours). **Depends on:** nothing. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

## Goal, and why it sits first

Turn every interface in `docs/build/CONTRACTS.md` into code and fixtures, so that each later chunk builds against typed models and stub signatures rather than prose, and can be tested on its own. Create the repo scaffold, the CLI skeleton with every command stubbed, the configuration files, the test harness, and the fixture directory. Nothing in this chunk computes anything real.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` in full (about 3,500 words).
2. `docs/adr/ADR-017-tech-stack.md` (Python 3.13, uv, numpy, Typer, pydantic; DuckDB after the MVP).
3. `docs/adr/ADR-021-determinism.md`.
4. `docs/adr/ADR-023-release-states-and-feature-flags.md` (the capability flags file).
5. `CLAUDE.md` (the protocol you are following).

## Scope

**Build:**

- `pyproject.toml` managed by uv: package `nbadfs` under `src/`, console script `dfs = nbadfs.cli:app`, dependencies `typer`, `pydantic>=2`, `numpy`, `scipy`, `pandas`, `pyarrow`, `httpx`, `pdfplumber`, `swiglpk`, `ortools`, `nba_api`, `pytest`, `hypothesis`, `tomli`/`tomllib`. Pin versions. `uv sync` must succeed on this Windows laptop.
- `src/nbadfs/schemas/`: one module per CONTRACTS section (`dk_files.py`, `slate.py`, `contest_facts.py`, `news.py`, `history.py`, `projections.py`, `scenarios.py`, `field.py`, `settlement.py`, `portfolio.py`, `ledger.py`, `manifest.py`, `brief.py`) with pydantic models for every named model in CONTRACTS sections 2 to 12, field names exactly as written there, docstrings carrying each contract's rule. Numpy arrays are typed as `numpy.ndarray` with a validator on dtype and shape where CONTRACTS states them.
- `src/nbadfs/cli.py`: a Typer app with every command in CONTRACTS section 13 registered and stubbed to print "not built yet: chunk Cxx" and exit 0, the global options `--night`, `--as-of`, `--fixtures`, `--json`, `--yes` parsed into a `Clock` and a `Paths` object (CONTRACTS 1.1; C03 wires the lock rules to it), and the exit-code convention.
- `src/nbadfs/settings.py`: loads `config/settings.toml`, `config/posture.toml`, `config/capabilities.toml` into pydantic settings models with the defaults in CONTRACTS section 15; a test asserts every key in section 15 exists with that default.
- `config/settings.toml`, `config/posture.toml` (`posture = "permissive_plus_nba_api"`, allowed hosts list), `config/capabilities.toml` (every capability in PROGRESS.md with `enabled = false`, `rehearsed_on = ""`), `config/secrets.example.toml` (`odds_api_key = ""`); `config/secrets.toml` gitignored.
- `fixtures/` populated from the spike outputs named in CONTRACTS section 14 (public salary files, the two injury PDFs, `player_box_2026.parquet`) and `fixtures/tiny/` hand-written JSON contests with the expected settlement results computed by hand and written into the file. `fixtures/synthetic/` gets only a README; C07 serializes the R9 synthetic night (it is the first consumer, and reading the spike is a C07 cost, not a C01 cost).
- `tests/`: pytest configured with markers `smoke` and `slow`; `conftest.py` with fixture loaders; a smoke test per schema module that round-trips an example through JSON; a test that `uv run dfs --help` lists every command.
- `.gitignore` extended for `inbox/`, `data/`, `runs/`, `out/`, `config/secrets.toml`, `.venv/`.
- `scripts/dfs.cmd` and a desktop-shortcut note: a one-line Windows launcher that runs `uv run dfs %*` from the repo (the full launcher is C11).
- The `.claude/` folder is already present (`commands/run-chunk.md`); leave it.

**Out of scope:** any parser, any arithmetic, any network call, DuckDB, hooks, skills.

## Contracts

- **Consumes:** none.
- **Produces:** every model in CONTRACTS sections 2 to 12 as code; the settings models (section 15); the CLI surface (section 13); the fixture set (section 14). If a contract cannot be expressed as written, change CONTRACTS.md in the same commit and record it in PROGRESS.md under deviations.

## Definition of done

- `uv sync` succeeds; `uv run dfs --help` lists `status, night, out, in, start, fact, news, swap, repair, uploaded, results, research, unlock, replay, history, digest, sim, field, drill, rehearsed, insure` and the global options.
- `uv run pytest -m smoke` passes in under 60 seconds and covers every schema module.
- `fixtures/tiny/*.json` exist with hand-computed expected values and a README explaining each.
- The settings test passes for every default in CONTRACTS section 15.

## What I check

Open a terminal in the repo and run:

```bash
uv run dfs --help
```

Expected: a list of commands including `night`, `status`, `out`, `in`, `start`, `swap`, `repair`, `uploaded`. Then:

```bash
uv run pytest -m smoke -q
```

Expected: all tests pass, under 60 seconds.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: `pyproject.toml`, `uv sync`, the CLI skeleton, settings loading, smoke harness (commit). Checkpoint 2: all schema modules with round-trip tests (commit). Checkpoint 3: fixtures and the tiny contests (commit).

## Risks

- **`swiglpk` or `ortools` has no wheel for Python 3.13 on Windows.** Pin to the newest version that installs; if `swiglpk` fails, note it and C09 uses OR-Tools CBC as primary (ADR-006 fallback).
- **A contract is ambiguous.** Resolve it in CONTRACTS.md with one sentence, in the same commit, and list it in PROGRESS.md.
- **Windows path or encoding surprises in `uv`.** Pin the Python version in `pyproject.toml`; keep paths relative; note anything odd in PROGRESS.md for C02.
