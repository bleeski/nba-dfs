# C20: Incremental field-score cache (only if the re-solve misses budget on 12 games)

**State:** Optimizer (conditional). **Size:** M (one session, about 1 to 2 hours, three checkpoints). **Depends on:** C10. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

## Goal, and why it sits here

Run this chunk only if C10 recorded that the re-solve missed 180 seconds on the saved Oct 16 12-game slate (PROGRESS.md and `capabilities.toml` with `resolve.enabled = false` and the reason) after C10's first two mitigations were tried. Otherwise skip it and note why. The structural cost in the re-solve is re-scoring every field lineup in every scenario after one game changes. This chunk caches each field lineup's score as quantized per-game partial sums, so re-simulating two games touches two columns of partial sums rather than the whole field, and it replaces field resampling after a scratch with importance weights (re-weighting the existing sample so it represents the shifted ownership). The target is a total re-solve under 60 seconds, so the live path can ship with its flag on.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 7 (determinism and `simulate_game`), 8, 11.4, 15 (`[resolve]`, `[field]`).
2. `docs/ARCHITECTURE.md` section 3 "Late news and lock waves"; section 5 "Who the simulated opponents are", "Ownership"; section 6 "Late news and late swap: the joint re-solve (ADR-026)"; section 11 "Performance tests".
3. `docs/adr/ADR-026-late-news-as-live-resolve-and-open-slot-swap.md` (the budget and the fallback), `docs/adr/ADR-020-scoring-adapter.md` (the eighth-point rule, which fixes the quantum), `docs/adr/ADR-021-determinism.md`.
4. `docs/review/ADJUDICATION.md` entry 10 only.
5. `docs/build/chunks/C10-resolve-late-swap-news-commands.md` "Definition of done" and "Risks" (the recorded timing and the mitigations that must already have been tried), and the drill log in `docs/build/PROGRESS.md` for the measured times.

## Scope

**Build:**

- `field/cache.py`: `FieldScoreCache` keyed by slate and lineup hash, shared by every contest on the slate (contests differ only in their weights over the same lineups). For each game and each unique field lineup, store the lineup's points from players in that game per scenario as `int16` at a quantum of `cache.quantum_points` (setting, default 0.125: UTIL points are quarter-point multiples and Captain totals are eighth-point values per ADR-020, so the cache is exact). Stored as memory-mapped arrays under `runs/<run_id>/cache/` with the hashes of the scenario set, the public view and the pool that built them.
- `score_field_incremental(cache, changed_games, new_game_arrays, weights) -> FieldScores`: recompute partial sums only for `changed_games`, apply the per-game deltas to the lineup totals, and rebuild the quantile grid; untouched games are never re-read beyond their totals.
- `field/reweight.py`: `reweight_field(field_sample, old_view, new_view, settings) -> FieldSample`: after a public fact shifts the public view, multiply each lineup's weight by the ratio of its probability under the new view to the old (the product of its players' popularity ratios, with the entrant-type mixture from C08), renormalize, and compute the effective sample size (how many independent lineups the weighted sample is worth). Below `cache.min_ess_share` (setting, default 0.5) of the original, resample that slate's field fully instead and say so in the timings.
- `resolve` (C10) uses the cache when `cache.enabled` (default true once this chunk ships) and the stored hashes match; otherwise `dfs night` builds the cache once in the night build, before any news, and the re-solve falls back to full scoring with a logged reason.
- `dfs drill news --at 30|10|2` reports cache hits, games re-simulated, the effective sample size and the total re-solve time.

**Out of scope:** any change to the field mixture, the settlement or the swap; live-score conditioning (C22); candidate generation speed.

## Contracts

- **Consumes:** `FieldSample`, `FieldScores`, `score_field`, `PublicView`, `build_field` (C08); `ScenarioSet`, `simulate_game` (C07); `resolve` and the drill harness (C10); `Slate` (C02).
- **Produces:** `FieldScoreCache(slate_key, lineup_hashes, games, quantum, partial: {game_id: int16[S, M]}, totals: int32[S, M], built_from: {scenario_hash, public_view_hash, pool_hash})`, `score_field_incremental`, `reweight_field` with `FieldSample.ess`. Added to CONTRACTS.md section 8, with `[cache]` in section 15, in the same commit.

## Definition of done

- Exactness: on the saved Oct 16 slate, the cache totals equal full scoring to the quantum for every lineup and scenario; after re-simulating two games, the incremental `FieldScores` grid equals a full recompute exactly (the quantum makes it exact, so the tolerance is zero).
- Reweighting: after a scripted scratch, ownership from the reweighted sample matches a freshly built sample within the Monte Carlo tolerance C08 used; a scratch of a 60%-owned player drives the effective sample size below the setting and triggers the full resample.
- Stale cache: a changed public-view hash forces a rebuild with the logged reason; a matching hash uses the cache.
- Determinism: the incremental path and the full path give byte-identical upload files for the same news state.
- Memory: the cache for the 12-game slate at `resolve.S` stays under `cache.max_ram_gb` (setting, default 2) in RAM with the rest on disk; the figure is recorded.
- Timing: the C10 scenario (one star out in a game shared by the main Classic and a Showdown) finishes under 60 seconds total at `resolve.S` 10,000; recorded in PROGRESS.md; `resolve.enabled` flips to true with the date.

## What I check

On the saved Oct 16 files, after `dfs night`:

```bash
uv run dfs drill news --at 30
```

Expected: a line like "re-solve finished in 48 s (cache: 2 of 12 games re-simulated, field reweighted, effective sample 71%); with a 3-minute upload you would have about 26 minutes to spare". Then `--at 10` and `--at 2`, which should still print the window arithmetic from C10. The upload file should be identical to one produced with `cache.enabled = false`.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: the cache and incremental scoring with the exactness test (commit). Checkpoint 2: reweighting with the effective-sample-size rule (commit). Checkpoint 3: wiring into the re-solve, the drill timings, the flag flip (commit).

## Risks

- **The cache is too large for 12 games.** It is per slate and per unique lineup, not per contest; if still too large, collapse locked games' partials into the totals (they can no longer change) and lower `resolve.S` for the drill.
- **Importance weights degenerate on big scratches.** The effective-sample-size rule resamples; the timing then shows the slower path, and either the budget still holds or the drill says so.
- **The cache goes stale silently.** Every use checks the three hashes; a mismatch rebuilds and logs.
- **Sixty seconds still misses.** Report the time; the C10 fallback (repair) remains the path and the flag stays off.
