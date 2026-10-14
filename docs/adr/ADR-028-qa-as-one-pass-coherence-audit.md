# ADR-028: QA is one pre-lock coherence pass that files cited challenges; code owns splits and swaps

**Status:** Accepted (from week 2). **Supersedes:** ADR-012. **Source:** ADJUDICATION entry 18 (B-I-10). **Changelog:** 2026-10-14 created.

## Context

ADR-012 gave the QA adversary two tracks: construction changes (swap pairs, exposure caps) judged by simulation, and belief changes judged by a 20-game evidence bar computed by code, over up to three iterations. Critique B showed the deterministic local-improvement pass already tests leverage swaps in under a second, that a statistical split which passes a 20-game bar should be computed by code in the priors module before the build starts, and that the 20-game bar automatically rejects the things an LLM can actually catch an hour before lock (a stagger quote, a player who has not cleared physicals, a lineup pairing a guard with his own backup). The owner's MLB QA agent spent about 109,000 tokens and a median of 26 minutes for one change (RR1). The owner's "up to three iterations" was in the vision section the brief itself calls a starting hypothesis; the owner is asked to confirm.

## Decision

- **One pass, from week 2,** after the main build: at most 3 minutes, one iteration, a separate subagent with no web access that sees only a fact packet (the top 15 players by portfolio exposure, the top 5 Showdown Captains, the raw news digest with its fetched sources, contest facts status).
- **Two proposal types only:** a **missed-news challenge** (points to a fetched article or injury-report row that contradicts an active player's status or role, with the quote) and a **lineup-coherence flag** (names specific player pairs in one lineup whose on-court roles are mutually exclusive, with the reason). At most 8 proposals.
- **Code judges both:** a challenge must pass the same quote and publish-time checks as a researcher fact record, then materiality and regret (no contest may lose more than 2% of its Goal 1 under the old beliefs); a coherence flag is tested by re-selection with the pair excluded and accepted only if Goal 1 and Goal 2 do not worsen by more than noise.
- **Historical splits** (back-to-backs, rest days, home and away) are computed by the deterministic priors module when at least 20 games or 300 minutes exist and the effect survives shrinkage and a held-out half of seasons; they are not QA proposals.
- **Pairwise leverage swaps** stay in the deterministic local-improvement step.
- The pre-QA portfolio is kept and scored against real standings.

## Consequences

- **Results:** QA catches the misses an LLM can see and cannot fish for statistics.
- **Cost:** one short subagent run a night instead of up to three long ones.
- **Workload:** accepted changes appear in the brief with their citation; any can be vetoed.
