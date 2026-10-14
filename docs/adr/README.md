# Decision records

Each record is short: context, options considered, the decision, and what it means for results, cost, or the owner's nightly workload. Records are never deleted; a reversed decision is superseded by a new record and kept for history. Revision notes dated 2026-10-14 come from `docs/review/ADJUDICATION.md`.

**Changelog:** 2026-10-14 (round 2 final gate, ADJUDICATION-R2 entries R2-33 and R2-34): ADR-003, 004, 005, 010, 013, 017, 019 and 020 carry round 2 changelog lines or inline superseded markers; their rows below say which. **Changelog:** 2026-10-14 (round 2, ADJUDICATION-R2): ADR-029 to ADR-031 added; ADR-007, 018, 023, 024, 025, 026 superseded in part (each marks the superseded wording inline); ADR-008 Decision bullets corrected. 2026-10-14 (round 1): ADR-023 to ADR-028 added; ADR-001, 009, 011, 012, 022 superseded; ADR-002, 003, 004, 005, 007, 008, 010, 013, 014, 015, 016, 017, 019, 020 revised.

| ADR | Decision | Status |
|---|---|---|
| 001 | Both goals on one simulated night; the insurance budget | Superseded by 024 and 025 |
| 002 | One shared, stat-level simulation of the whole night, with a model-error layer | Accepted (revised 2026-10-14) |
| 003 | The LLM sets beliefs (facts act in the MVP; inferences shadow); code sets lineups | Accepted (revised 2026-10-14); fact supersession and researcher timing marked inline in round 2 (R2-10, R2-34) |
| 004 | Every DraftKings interaction is manual | Accepted (revised 2026-10-14); salary file every run, copy-not-move inbox and standings folder updated in round 2 (R2-14, R2-33, R2-34) |
| 005 | A source layer with a data-posture switch; permissive plus `nba_api` for box scores (D1 answered) | Accepted (D1 answered 2026-10-14); DraftKings `Status` verified present (R2-33) |
| 006 | GLPK for Classic candidates, enumeration for Showdown, OR-Tools as fallback | Accepted |
| 007 | Greedy selection per contest on Goal 1; feasibility-tested concentration cap | Accepted (revised 2026-10-14); guarantee statement superseded by 029 |
| 008 | The field is simulated from a public view that never falls back to our baseline | Accepted (Decision bullets corrected in round 2) |
| 009 | Duplication as prize share, switched on after calibration | Superseded by 024 |
| 010 | One validator; the exporter is the only path to an upload file; four states per slate | Accepted (revised 2026-10-14); slate fingerprint, repair wording and the changed-rows rule marked inline in round 2 (R2-8, R2-34) |
| 011 | Stored replacements and `dfs apply` | Superseded by 026 |
| 012 | QA proposals typed and judged by code, up to three iterations | Superseded by 028 |
| 013 | Claude Code mapping; the desktop launcher; the advisor rule | Accepted (revised 2026-10-14); researcher and watcher timing marked inline in round 2 (R2-1, R2-34) |
| 014 | Every run is replayable from a manifest, snapshots, seeds and decision records | Accepted (revised 2026-10-14) |
| 015 | Learn per layer on dense signals; adopt through shadow tests and sign-off; the ramp gate | Accepted (revised 2026-10-14) |
| 016 | Early-season priors from last season, shrinkage and widened uncertainty | Accepted (revised 2026-10-14) |
| 017 | Python 3.13, uv, numpy, one CLI; DuckDB after the MVP | Accepted (revised 2026-10-14); DuckDB marked after the MVP inline (R2-34) |
| 018 | Reuse: port the entry-history parser and name normalizer; learn from the rest | Accepted; suffix stripping in matching superseded by 031 |
| 019 | Delivery first; only DraftKings validity blocks a file; the fallback ladder | Accepted (revised 2026-10-14); old ladder and P(washout) marked superseded inline (R2-6, R2-34) |
| 020 | Versioned scoring adapter with nightly self-checks; eighth-point Captain totals | Accepted (revised 2026-10-14); triple-double +4.5 re-verified on last season (R2-33) |
| 021 | Deterministic by construction | Accepted |
| 022 | The night spike as reference implementation and test oracle | Superseded by 027 |
| 023 | Three release states (Floor, Baseline, Optimizer) and a feature flag per capability | Accepted; usage bullet and bare rehearsal date superseded by 030 |
| 024 | Goal 1 is top-1% prize equity in dollars; duplication and ties inside the objective | Accepted (owner decision); tie formula, additive approximation and diminishing-returns claim superseded by 029 |
| 025 | Goal 2 is the probability of a severe-drawdown night; the insurance control with an exact paired margin | Accepted (owner decision; control after the MVP); Settlement bullet superseded by 029 |
| 026 | Late news is a live re-solve on the joint state; open-slot late swap; the legal repair | Accepted; insufficient-time drop and saved-night writes superseded by 030 |
| 027 | The night spike is a mechanics benchmark only; calibration against last season | Accepted |
| 028 | QA is one pre-lock coherence pass | Accepted (from week 2) |
| 029 | Settlement v2: one tie split, joint ranks in every field, realized outcomes for Goal 2, an exact top tail, greedy as a labeled heuristic | Accepted (round 2) |
| 030 | Operations v2: a walkable Floor-only route, time to lock as a label, isolated drills, recoverable exports, versioned rehearsals | Accepted (round 2) |
| 031 | A player's identity has no team; a slate's identity is a fingerprint of its pool | Accepted (round 2) |
