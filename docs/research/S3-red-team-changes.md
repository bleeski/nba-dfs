# S3. What the red-team rounds changed, and why

**Date:** 2026-10-13. **Inputs:** RT1 (29 findings on the first draft), the R9 laptop benchmark, RT2 (round-1 scorecard: 19 fixed, 10 partly fixed, 0 not fixed; 19 new findings). The full design is `docs/ARCHITECTURE.md` version 3. RT2's verdict: ready for the owner's approval once its must-fix items were made, with no third round needed; all must-fix items are addressed below.

## The biggest changes

| Area | First draft | Version 3 | Why (finding) |
|---|---|---|---|
| Goal 2 in the model | Outcome noise only | Three layers: outcome noise, symmetric model error, edge uncertainty (a night-wide weight on our view versus the public view, allowed below zero); edge uncertainty feeds reporting only in Phase 1 | At the planned volume the model said washout never happens (RT1 1); symmetric error barely changed that and an engine assuming it is right underestimated washout about 9x (R9); the pre-set bar for using edge uncertainty in selection was not met (RT2 5) |
| Insurance control | One weight swept across contests | Constrained swap search; `G1_c(new) >= (1 - epsilon) x G1*_c + 2 x SE_paired` on a validation set; frozen contests; roll-back on a reporting set; runs when at least 50 washout scenarios exist; default 2% | The sweep did not enforce per-contest guarantees (RT1 7); budgets leaked out of sample (R9); the first margin was written backwards and the 1% skip rule would have skipped the nights where it helped (RT2 4) |
| Scenario sets | One set | Four: screening, selection, validation, reporting | Selection on one set flatters its picks (RT1 18, R2); a search checked on one set exploits its noise (R9) |
| Duplication | Prize share from the best-scoring entry | Maximum over entries of probability times expected share; switched on per format after a calibration check | The first form broke the greedy guarantee (RT1 8); duplicate-aware selection changed most synthetic Showdown picks (R9); switch on evidence, not a file count (RT2 15) |
| Late news | Rebuild on news | Stored replacements for "sits" and "plays", `dfs apply` combining all confirmed changes in seconds, "valid until" stamps, official versus possible alerts, `dfs out` and `dfs in` from the launcher, ledger with pending state | A rebuild finished at tip (RT1 2); finished if-out files did not combine, went stale, and ignored "he plays" (RT2 1 to 3); free text cannot safely drive changes without confirmation (RT2 6) |
| Field model | Built from our baseline model | Built from a public view (consensus, salary value, public-tagged news) | Our baseline leaked our edge into the field and private-only news hid public news (RT1 4) |
| Operating without Claude | `--no-llm` typed into Claude | Desktop launcher for every night step | At the usage cap Claude stops accepting commands (RT1 6) |
| Upload integrity | Hooks on two tools | Hooks on Edit, Write, Bash and PowerShell; manifest hashes; `/status` flags unknown files | Hand-built files were a recurring prior-engine failure (RT1 10) |
| Phase 1 | Whole stack in five days | Tiers A (floor), B (model), C (night); minimal field and selection on Thursday; usage projected after Wednesday | Thursday's rehearsal needed Friday's code; no floor was defined (RT1 5, RT2 7) |
| Opening night | 11:30 am build | Monday-evening build; Tuesday `dfs night --no-llm --reuse-overrides` at 12:30 pm; parser fixes allowed Monday evening | Workday timing (RT1 24); a one-game re-run cannot refresh three games or fill new entries (RT2 8) |
| Volume | 50 to 200 entries from night one | Decision D9: start at 25 to 50, scale after the Nov 3 readout | No prior engine showed an edge (RT1 14) |
| User time | "About 25 to 35 minutes" | 30 to 45 minutes plus an on-call window, measured by projection from timed rehearsal actions | The estimate undercounted (RT1 20, RT2 11) |

## Smaller changes

- Overrides: quotes checked against saved pages; role changes as mixtures; a public or private tag; a teammate-minutes cap; a veto command (RT1 15, 16).
- QA moved to week 2, with logged queries, a held-out-half replication rule and a query cap (RT1 23, 26).
- Contest facts from the entry-history export moved into Phase 1 (RT1 11).
- The two terms bets in the permissive posture stated plainly; researcher allowlist by domain without ESPN or paywalled sites (RT1 12, RT2 14).
- DraftKings `Status` and `Starting` relabeled BET for NBA (RT1 21).
- Fallback removes ruled-out players (RT1 22).
- Standings moved out of the project, hashed, and blocked from Claude by every tool (RT1 28, RT2 16).
- The Odds API plan corrected to about 7 prop nights a month (RT2 17).
- Usage read from a status-line file, or asked for once a day (RT2 18).
- Run lock with a heartbeat; the launcher owns the watcher (RT2 13).
- Hunch test computed nightly on paired per-contest measures, with "undecided" as an allowed answer (RT1 3, RT2 12).
- Decision D10 added: fields of 100 to 199 count first place only.
- Citation slips fixed (RT2 19); ADR-001, 002, 004, 005, 007, 009, 011, 013 and 019 brought into line (RT2 9).

## What was not changed

- The two goals, the shared night simulation, the LLM-sets-beliefs boundary, manual DraftKings I/O, and the validator as the only path to an upload file. Both red-team rounds rated these sound.
- The solver choice (GLPK primary, OR-Tools CBC fallback), with R2's differing recommendation recorded in ADR-006.
