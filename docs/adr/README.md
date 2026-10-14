# Decision records

Each record is short: context, options considered, the decision, and what it means for results, cost, or the owner's nightly workload. Records are never deleted; a reversed decision is superseded by a new record and kept for history. Revision notes dated 2026-10-14 come from `docs/review/ADJUDICATION.md`.

**Changelog:** 2026-10-14: ADR-023 to ADR-028 added; ADR-001, 009, 011, 012, 022 superseded; ADR-002, 003, 004, 005, 007, 008, 010, 013, 014, 015, 016, 017, 019, 020 revised.

| ADR | Decision | Status |
|---|---|---|
| 001 | Both goals on one simulated night; the insurance budget | Superseded by 025 |
| 002 | One shared, stat-level simulation of the whole night, with a model-error layer | Accepted (revised 2026-10-14) |
| 003 | The LLM sets beliefs (facts act in the MVP; inferences shadow); code sets lineups | Accepted (revised 2026-10-14) |
| 004 | Every DraftKings interaction is manual | Accepted (revised 2026-10-14) |
| 005 | A source layer with a data-posture switch; permissive plus `nba_api` for box scores (D1 answered) | Accepted (D1 answered 2026-10-14) |
| 006 | GLPK for Classic candidates, enumeration for Showdown, OR-Tools as fallback | Accepted |
| 007 | Greedy selection per contest on Goal 1; feasibility-tested concentration cap | Accepted (revised 2026-10-14) |
| 008 | The field is simulated from a public view that never falls back to our baseline | Accepted (revised 2026-10-14) |
| 009 | Duplication as prize share, switched on after calibration | Superseded by 024 |
| 010 | One validator; the exporter is the only path to an upload file; four states per slate | Accepted (revised 2026-10-14) |
| 011 | Stored replacements and `dfs apply` | Superseded by 026 |
| 012 | QA proposals typed and judged by code, up to three iterations | Superseded by 028 |
| 013 | Claude Code mapping; the desktop launcher; the advisor rule | Accepted (revised 2026-10-14) |
| 014 | Every run is replayable from a manifest, snapshots, seeds and decision records | Accepted (revised 2026-10-14) |
| 015 | Learn per layer on dense signals; adopt through shadow tests and sign-off; the ramp gate | Accepted (revised 2026-10-14) |
| 016 | Early-season priors from last season, shrinkage and widened uncertainty | Accepted (revised 2026-10-14) |
| 017 | Python 3.13, uv, numpy, one CLI; DuckDB after the MVP | Accepted (revised 2026-10-14) |
| 018 | Reuse: port the entry-history parser and name normalizer; learn from the rest | Accepted |
| 019 | Delivery first; only DraftKings validity blocks a file; the fallback ladder | Accepted (revised 2026-10-14) |
| 020 | Versioned scoring adapter with nightly self-checks; eighth-point Captain totals | Accepted (revised 2026-10-14) |
| 021 | Deterministic by construction | Accepted |
| 022 | The night spike as reference implementation and test oracle | Superseded by 027 |
| 023 | Three release states (Floor, Baseline, Optimizer) and a feature flag per capability | Accepted |
| 024 | Goal 1 is top-1% prize equity in dollars; duplication and ties inside the objective | Accepted (owner decision) |
| 025 | Goal 2 is the probability of a severe-drawdown night; the insurance control with an exact paired margin | Accepted (owner decision; control after the MVP) |
| 026 | Late news is a live re-solve on the joint state; open-slot late swap; the legal repair | Accepted |
| 027 | The night spike is a mechanics benchmark only; calibration against last season | Accepted |
| 028 | QA is one pre-lock coherence pass | Accepted (from week 2) |
