# ADR-006: GLPK for Classic candidates, full enumeration for Showdown, OR-Tools as the fallback solver

**Status:** Accepted (design). **Date:** 2026-10-13.

## Context

Classic needs thousands of candidate lineups per slate, each the best legal lineup for some set of point values (one simulated scenario, or leverage-adjusted means). Showdown has a small enough lineup space to list. The brief asks for a free solver chosen on merits (the user mentioned PuLP). Results must be deterministic for replay and common random numbers (ADR-021).

## Evidence (VERIFIED, indicative timings: other agents were running on the laptop)

Benchmark `spikes/solvers/bench_solvers.py` on a synthetic 6-game, about 120-player Classic pool and a 22-player Showdown pool; summary in `spikes/solvers/out/20261013-1656_bench_summary.txt`.

| Task | GLPK (swiglpk 5.0.13) | OR-Tools CBC | OR-Tools CP-SAT | SCIP | HiGHS (tuned) | PuLP + CBC |
|---|---|---|---|---|---|---|
| One Classic lineup, random objective, median | **2.2 ms** | 23.5 ms | 39.4 ms | 29.5 ms | 53.9 ms | 75.6 ms (500-lineup run) |
| 5,000 Classic lineups, 1 process | **21.8 s** | 131.3 s | 267.0 s | 286.5 s | 403.3 s | not run |
| 5,000 Classic lineups, 4 processes | **7.6 s** | 37.7 s | 78.7 s | not run | 123.8 s | not run |
| 150 Classic lineups in sequence with overlap limits | 30.8 s | 74.4 s | 68.8 s | 228.9 s | 227.2 s | 108.2 s |

- Formulation: one yes/no variable per player plus position-feasibility rows ("Hall" form) was 5x to 25x faster than the "player in slot" form with identical optimal lineups (phase A rows: GLPK 0.8 s against 20.0 s for 20 lineups).
- Determinism: repeat runs gave identical lineup hashes (for example GLPK 5,000 lineups with 1 and 4 processes both hash `57f714200c68d5a7`).
- Showdown: all 440,121 legal lineups of a 22-player pool listed in 0.015 seconds, and the best matched the solver optimum exactly (`20261013-1700_enumerate_showdown.json`).

- Ties: every solver reached the identical optimal value on every solve, but solvers often returned different lineups among equally good ones (R2, VERIFIED). Single-threaded runs were repeatable for every solver; CP-SAT with 8 workers was not (3 of 4 checks differed).
- At 240 players, per-solve time rose 1.5x to 2.5x with the same ranking (R2 phase F).

## Options considered

PuLP with CBC (the user's suggestion; PuLP 2.4 pinned by pydfs-lineup-optimizer ships a 2015 CBC build plus 35 to 50 ms of file and process overhead per solve), HiGHS, OR-Tools CBC and CP-SAT, SCIP, and GLPK.

**Disagreement on record.** The R2 research memo recommends OR-Tools CBC as primary, HiGHS as fallback, and GLPK only as an optional fast path, because GLPK is GPL-3 and unchanged since 2020. This record chooses GLPK as primary anyway: the GPL does not bind a private tool that is never distributed; "unchanged since 2020" means stable for problems this small; and the roughly 10x speed difference buys headroom for 12-game slates, 240-player pools and late-news re-runs. The fallback design below covers the maintenance risk. If `swiglpk` ever lacks a wheel for the engine's Python version, OR-Tools CBC becomes primary with no other change.

## Decision

- **Classic candidates:** GLPK through `swiglpk`, with a persistent model whose objective is replaced for each scenario, the Hall formulation, no wall-clock time limit, one single-threaded solve per worker process, results merged in a fixed order.
- **Deterministic tie-break:** each objective adds a tiny, fixed perturbation keyed by the player's stable identifier (far smaller than any real point difference), so equally good lineups resolve the same way on every solver and every run.
- **Fallback solver:** OR-Tools CBC (Apache 2.0), behind the same small interface, used automatically if GLPK fails to load; also the reference implementation in tests (both must return the same optimum).
- **Showdown:** full enumeration, screened, no solver.
- **Not chosen:** PuLP (slow, old CBC), HiGHS (slowest per lineup here), sequential overlap-constrained generation (slow and unnecessary, because selection creates diversity).
- **License:** GLPK is GPL-3; fine for a private tool that is not distributed.

## Consequences

- **Results:** 20,000 Classic candidates take well under a minute on 4 processes, so candidate breadth is never the bottleneck.
- **Cost:** free; one more pip package.
- **Workload:** none.
- **Re-check:** timings were taken under load; the Phase 1 performance test re-measures on a real slate.
