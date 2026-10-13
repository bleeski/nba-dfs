# Decision records

Each record is short: context, options considered, the decision, and what it means for results, cost, or the owner's nightly workload.

| ADR | Decision | Status |
|---|---|---|
| 001 | Both goals are computed on one simulated night that includes model error; the insurance budget trades them off | Accepted |
| 002 | One shared, stat-level simulation of the whole night, with a model-error layer | Accepted |
| 003 | The LLM sets beliefs (checked against sources, tagged public or private); code sets lineups | Accepted |
| 004 | Every DraftKings interaction is manual | Accepted |
| 005 | A source layer with a data-posture switch; permissive by default, with two stated terms bets | Proposed (owner decides, D1) |
| 006 | GLPK for Classic candidates, enumeration for Showdown, OR-Tools as fallback | Accepted |
| 007 | Greedy scenario coverage per contest; constrained insurance search across the night | Accepted |
| 008 | The field is simulated from a public view of the night | Accepted |
| 009 | Duplication counts at the expected prize share, switched on after calibration | Proposed (owner decides, D2) |
| 010 | One validator; the exporter is the only path to an upload file | Accepted |
| 011 | Ready-made if-out files, a narrow re-run, a per-entry ledger, in-place late swap | Accepted |
| 012 | QA proposals are typed, independent, judged by code; QA starts in week 2 | Accepted |
| 013 | Claude Code mapping; the desktop launcher runs every night step without Claude | Accepted |
| 014 | Every run is replayable from a manifest, snapshots, seeds and decision records | Accepted |
| 015 | Learn per layer on dense signals; adopt changes through shadow tests and sign-off | Accepted |
| 016 | Early-season priors from last season, shrinkage and widened uncertainty | Accepted |
| 017 | Python 3.13, uv, numpy, DuckDB, one CLI | Accepted |
| 018 | Reuse: port the entry-history parser and name normalizer; learn from the rest | Accepted |
| 019 | Delivery first; only DraftKings validity blocks a file | Accepted |
| 020 | Versioned scoring adapter with nightly self-checks | Accepted |
| 021 | Deterministic by construction | Accepted |
| 022 | The night benchmark spike is a reference and test oracle, not engine code | Accepted |
