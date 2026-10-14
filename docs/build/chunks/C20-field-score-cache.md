# C20: Incremental field-score cache (only if the re-solve misses budget on 12 games)

**State:** Optimizer (conditional). **Size:** M (one session, about 1 to 2 hours, three checkpoints). **Depends on:** C10. **Parallel with:** none (every chunk touches `cli.py`, `CONTRACTS.md` and settings; run one at a time).

**Changelog:** 2026-10-14 (ADJUDICATION-R2): the cache preserves the field interface of CONTRACTS section 8 (`p_above`, `p_equal`, the exact eighth-point top tail and its weights, the tail fit; never float16), and the exactness test covers the tail as well as the grid (R2-4); reweighting refreshes `sampled_share` so copies are counted once (R2-4); C10's fallback is the repair, and the re-solve is attempted only when the earliest affected lock is at least `resolve.min_minutes_to_lock` away, so the T-2 drill expects the repair (R2-6); usage budget added. 2026-10-14: created.

## Goal, and why it sits here

Run this chunk only if C10 recorded that the re-solve missed 180 seconds on the saved Oct 16 12-game slate (PROGRESS.md and `capabilities.toml` with `resolve.enabled = false` and the reason) after C10's first two mitigations were tried. Otherwise skip it and note why. The structural cost in the re-solve is re-scoring every field lineup in every scenario after one game changes. This chunk caches each field lineup's score as quantized per-game partial sums, so re-simulating two games touches two columns of partial sums rather than the whole field, and it replaces field resampling after a scratch with importance weights (re-weighting the existing sample so it represents the shifted ownership). The target is a total re-solve under 60 seconds, so the live path can ship with its flag on.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 7 (determinism, `simulate_game` and the precision rule), 8 (all, including the `FieldScores` rules), 11.4, 11.7 (Time to lock), 15 (`[resolve]`, `[field]`).
2. `docs/ARCHITECTURE.md` section 3 "Late news and lock waves"; section 5 "Who the simulated opponents are", "Ownership"; section 6 "Late news and late swap: the joint re-solve (ADR-026)"; section 11 "Performance tests".
3. `docs/adr/ADR-026-late-news-as-live-resolve-and-open-slot-swap.md` (the budget and the fallback), `docs/adr/ADR-020-scoring-adapter.md` (the eighth-point rule, which fixes the quantum), `docs/adr/ADR-021-determinism.md`.
4. `docs/review/ADJUDICATION.md` entry 10 only.
5. `docs/build/chunks/C10-resolve-late-swap-news-commands.md` "Definition of done" and "Risks" (the recorded timing and the mitigations that must already have been tried), and the drill log in `docs/build/PROGRESS.md` for the measured times.

## Scope

**Build:**

- `field/cache.py`: `FieldScoreCache` keyed by slate and lineup hash, shared by every contest on the slate (contests differ only in their weights over the same lineups). For each game and each unique field lineup, store the lineup's points from players in that game per scenario as `int16` at a quantum of `cache.quantum_points` (setting, default 0.125: UTIL points are quarter-point multiples and Captain totals are eighth-point values per ADR-020, so the cache is exact). Stored as memory-mapped arrays under `runs/<run_id>/cache/` with the hashes of the scenario set, the public view and the pool that built them.
- `score_field_incremental(cache, changed_games, new_game_arrays, weights) -> FieldScores`: recompute partial sums only for `changed_games`, apply the per-game deltas to the lineup totals, and rebuild the whole `FieldScores` from them: the bulk grid, the tail threshold, the exact top-of-field scores (integer eighths) with their weights, and the tail fit with its `tail_fit_status`; untouched games are never re-read beyond their totals. The cache preserves the field interface of CONTRACTS section 8: settlement still reads the field only through `p_above` and `p_equal` on exact eighth-point scores, and nothing in the cache or the rebuilt `FieldScores` is float16 or rounded to two decimals (ADJUDICATION-R2 R2-4).
- `field/reweight.py`: `reweight_field(field_sample, old_view, new_view, settings) -> FieldSample`: after a public fact shifts the public view, multiply each lineup's weight by the ratio of its probability under the new view to the old (the product of its players' popularity ratios, with the entrant-type mixture from C08), renormalize, refresh `sampled_share` per lineup hash from the new weights (so the copy-rate excess is still counted once, CONTRACTS section 9), and compute the effective sample size (how many independent lineups the weighted sample is worth). Below `cache.min_ess_share` (setting, default 0.5) of the original, resample that slate's field fully instead and say so in the timings.
- `resolve` (C10) uses the cache when `cache.enabled` (default true once this chunk ships) and the stored hashes match; otherwise `dfs night` builds the cache once in the night build, before any news, and the re-solve falls back to full scoring with a logged reason. C10's own fallback is unchanged: the re-solve is attempted only when the earliest affected lock is at least `resolve.min_minutes_to_lock` away, and on a timeout or inside that window the repair runs (CONTRACTS 11.4 and 11.7 "Time to lock").
- `dfs drill news --at 30|10|2` reports cache hits, games re-simulated, the effective sample size and the total re-solve time.

**Out of scope:** any change to the field mixture, the settlement or the swap; live-score conditioning (C22); candidate generation speed.

## Contracts

- **Consumes:** `FieldSample`, `FieldScores`, `score_field`, `PublicView`, `build_field` (C08); `ScenarioSet`, `simulate_game` (C07); `resolve` and the drill harness (C10); `Slate` (C02).
- **Produces:** `FieldScoreCache(slate_key, lineup_hashes, games, quantum, partial: {game_id: int16[S, M]}, totals: int32[S, M], built_from: {scenario_hash, public_view_hash, pool_hash})`, `score_field_incremental`, `reweight_field` with `FieldSample.ess`. Added to CONTRACTS.md section 8, with `[cache]` in section 15, in the same commit.

## Definition of done

- Exactness: on the saved Oct 16 slate, the cache totals equal full scoring to the quantum for every lineup and scenario; after re-simulating two games, the incremental `FieldScores` (grid, tail threshold, `tail_scores`, `tail_weights`, `tail_fit`, `tail_fit_status`) equals a full recompute exactly, and `p_above` and `p_equal` agree exactly at every lattice score in the top 1% (the quantum makes it exact, so the tolerance is zero); a dtype test finds no float16 anywhere in the cache or the rebuilt `FieldScores`.
- Reweighting: after a scripted scratch, ownership from the reweighted sample matches a freshly built sample within the Monte Carlo tolerance C08 used; a scratch of a 60%-owned player drives the effective sample size below the setting and triggers the full resample; after reweighting, `sampled_share` matches the new weights and the settlement's copy excess (`copy_rate - sampled_share`, CONTRACTS section 9) is computed from the refreshed shares, so copies are counted once (a test).
- Stale cache: a changed public-view hash forces a rebuild with the logged reason; a matching hash uses the cache.
- Determinism: the incremental path and the full path give byte-identical upload files for the same news state.
- Memory: the cache for the 12-game slate at `resolve.S` stays under `cache.max_ram_gb` (setting, default 2) in RAM with the rest on disk; the figure is recorded.
- Timing: the C10 scenario (one star out in a game shared by the main Classic and a Showdown) finishes under 60 seconds total at `resolve.S` 10,000; recorded in PROGRESS.md; `resolve.enabled` flips to true with the date.

## What I check

On the saved Oct 16 files, after `dfs night`:

```bash
uv run dfs drill news --at 30
```

Expected: a line like "re-solve finished in 48 s (cache: 2 of 12 games re-simulated, field reweighted, effective sample 71%); with a 3-minute upload you would have about 26 minutes to spare". Then `--at 10`, which should print the same kind of line, and `--at 2`, which should print "re-solve skipped, repair ran" with the changed rows exported and labeled tight (C10's rule; the re-solve needs at least `resolve.min_minutes_to_lock` minutes). The upload file should be identical to one produced with `cache.enabled = false`.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: the cache and incremental scoring with the exactness test (commit). Checkpoint 2: reweighting with the effective-sample-size rule (commit). Checkpoint 3: wiring into the re-solve, the drill timings, the flag flip (commit).

## Usage budget

About 25% of a five-hour window and 4% of a weekly window (estimates until measured). If the session passes 40% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **The cache is too large for 12 games.** It is per slate and per unique lineup, not per contest; if still too large, collapse locked games' partials into the totals (they can no longer change) and lower `resolve.S` for the drill.
- **Importance weights degenerate on big scratches.** The effective-sample-size rule resamples; the timing then shows the slower path, and either the budget still holds or the drill says so.
- **The cache goes stale silently.** Every use checks the three hashes; a mismatch rebuilds and logs.
- **Sixty seconds still misses.** Report the time; the C10 fallback (repair) remains the path and the flag stays off.
