# C17: News watcher

**State:** Optimizer (milestone M4). **Size:** M (one session, about 1 to 2 hours, three checkpoints). **Depends on:** C10, C11a (the launcher), C11b (the posture allowlist in `llm/fetch.py`). **Parallel with:** none.

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): reporter posts are matched with C02's `identity.match_query` (whole-token matching), not a fuzzy matcher; the chunk enables and rehearses the existing `watcher` capability rather than adding one. 2026-10-14 (ADJUDICATION-R2): depends on C10, C11a (the launcher) and C11b (the posture allowlist in `llm/fetch.py`), and reads C04b for the injury adapter and the `dfs status --apply` path the watcher reuses (R2-1); the official path follows the news commands' rule, so the re-solve is attempted only when the earliest affected lock is at least `resolve.min_minutes_to_lock` away and the repair runs otherwise (R2-6); usage budget added. 2026-10-14: created.

## Goal, and why it sits here

Stop the owner from being the polling loop. The watcher is plain Python that never calls Claude: it fetches the official injury report every 15 minutes (both naming patterns), polls a list of NBA reporters' Bluesky posts every 60 seconds through the public API, and turns what it finds into two kinds of events. Official changes become facts and run the late-news path through the run lock, exactly as `dfs status --apply` does (the re-solve, or the repair when a lock is too close). Reporter posts become "possible" alerts that act on nothing until the owner confirms with `dfs out` or `dfs in`. The launcher starts it in its own window with keep-awake, and `dfs status` shows whether it is alive. It follows C10 because it drives C10's re-solve and nothing else.

## Reading list (nothing else)

1. `docs/build/CONTRACTS.md` sections 2.6, 4.1 to 4.4, 11.1 (`run_lock`), 11.4, 11.7 (Time to lock), 13.
2. `docs/ARCHITECTURE.md` section 3 "Late news and lock waves", "The deterministic and LLM boundary"; section 8 "The late-news path, end to end", "Process limits during a night"; section 10 "The posture as decided, and its terms bets".
3. `docs/adr/ADR-013-claude-code-runtime-and-budget.md` (the Desktop launcher bullet, the last Decision bullet, and its revision note), `docs/adr/ADR-026-late-news-as-live-resolve-and-open-slot-swap.md` (the re-solve trigger and the run lock), `docs/adr/ADR-005-data-posture-and-source-layer.md` (the allowlist rule).
4. `docs/review/ADJUDICATION.md` entries 10 and 19 only.
5. `docs/build/chunks/C04b-injury-report-and-payout-facts.md` "Scope" (the injury adapter and the `dfs status --apply` path the watcher reuses) and `docs/build/chunks/C10-resolve-late-swap-news-commands.md` "Scope" (the news-commands bullet: when the re-solve runs and when the repair runs).

## Scope

**Build:**

- `watch/watcher.py`: one loop with a fake-able clock. Every `watch.official_interval_s` (setting, default 900) call the C04b injury adapter trying both URL patterns; snapshot the file; diff against the last parsed report (with C04b's per-team merge); for each changed row write a `FactRecord` with `source.kind = "official_report"` and run the same path as `dfs status --apply` through the ledger's run lock (wait while another run holds it; never two at once): `resolve` when the `resolve` capability is on and the earliest affected lock is at least `resolve.min_minutes_to_lock` away, otherwise the repair, with any row locking within `export.tight_minutes` exported and labeled tight (CONTRACTS 11.4 and 11.7 "Time to lock"). Every `watch.reporter_interval_s` (setting, default 60) fetch each handle in `config/watch.toml` from Bluesky's public AppView (`app.bsky.feed.getAuthorFeed`, no login) through the posture allowlist; snapshot new posts; match names against tonight's pools with C02's `identity.match_query` (whole-token matching, accents folded, suffixes kept, never edit distance); classify the post as `out`, `in`, `questionable`, `starter` or `unknown`; detect negation ("not out", "will play", "no longer questionable") and set `negated`; write an `Alert` with `status = "possible"`. A possible alert never writes a fact. Every poll updates `runs/<night>/watcher_heartbeat.json`.
- `watch/negation.py` with `fixtures/watch/reporter_posts.json`: a labeled set of realistic posts, at least a third of them negations or non-news (praise, statistics, history), each with its expected classification.
- `dfs watch [--replay <file>]`: run the loop in the foreground, or replay a post fixture and print the alerts it would raise. `dfs out "<name>"` and `dfs in "<name>"` mark any matching possible alert `confirmed`; `dfs alert dismiss <id>` marks it `dismissed`.
- `dfs status` gains a watcher block: alive or stale (no heartbeat for `watch.stale_after_s`, setting, default 1800), the last official check and whether it changed anything, the last reporter poll, open possible alerts with their text and the confirming command, errors in the last hour. Network errors are logged and the loop continues.
- The launcher (C11a) gains a "Start watcher" entry that opens its own window with keep-awake; this chunk enables and rehearses the existing `watcher` capability (C01 creates all eight in `capabilities.toml`) and records it with `dfs rehearsed watcher`.

**Out of scope:** any LLM reading of posts; props or odds feeds; live scores (C22); the researcher's search budget (C11b, C21); auto-confirming alerts.

## Contracts

- **Consumes:** the injury adapter, its snapshot format and `dfs status --apply` (C04b); `identity.match` (C02); `NewsState`, `FactRecord` and the commands (C04a, C10); fact translation (C06); `resolve` (C10); `Ledger.run_lock` (C03); `Slate` pools (C02); the posture allowlist used by `dfs research fetch` (C11b); the launcher and capability flags (C11a).
- **Produces:** `Alert(alert_id, created_at, source: "bluesky"|"official", handle, post_url, text, matched: [{person_key, name, team}], kind_guess, negated, status: "possible"|"confirmed"|"dismissed", snapshot_id)`, `WatcherHealth(alive, last_official_at, last_reporter_at, open_alerts, errors_last_hour)`, `config/watch.toml`, `dfs watch`, `dfs alert dismiss`, the `dfs status` block. `Alert` and `WatcherHealth` go into CONTRACTS.md as section 4.6 in the same commit.

## Definition of done

- With a fake clock, the official check runs at 15-minute marks and the reporter poll every 60 seconds; both URL patterns are tried; a 404 is logged and the loop continues.
- An official diff (a March 2026 PDF swapped for an edited copy) writes facts and runs the re-solve (with the `resolve` capability on and the earliest affected lock at least `resolve.min_minutes_to_lock` away; with the lock 3 minutes away the repair runs instead and the row is exported labeled tight, being inside `export.tight_minutes`); with the run lock held by another process the watcher waits and runs once it is released; the ledger shows one run.
- Replay of `fixtures/watch/reporter_posts.json`: every post gets its expected classification; zero `out` alerts on negated posts; non-news posts raise nothing; `news_state.json` is unchanged after the replay (possible alerts never act).
- `dfs out` after a possible alert marks it confirmed and runs the re-solve once.
- `dfs status` shows "stale" when the heartbeat is older than the setting.
- Every fetched post and PDF is snapshotted under `data/snapshots/<date>/`.
- The launcher entry starts the watcher with keep-awake; rehearsed on a real evening and recorded in `capabilities.toml`.

## What I check

On any evening, start the watcher from the launcher, wait a few minutes, then:

```bash
uv run dfs status
```

Expected: a watcher block like "alive; official report checked 4 minutes ago, no changes; reporters polled 30 seconds ago; 1 possible alert: 'X (BOS) ruled out' from @reporter, confirm with `dfs out "X"`". Then:

```bash
uv run dfs watch --replay fixtures/watch/reporter_posts.json
```

Expected: a list of alerts with their guessed kind and a "negated" mark on the posts that say a player is not out; nothing under `runs/` changes.

## Size estimate and checkpoints

About 1 to 2 hours. Checkpoint 1: the loop, the official path through the run lock, the heartbeat (commit). Checkpoint 2: the Bluesky poll, name matching, negation, alerts, the replay fixture (commit). Checkpoint 3: the `dfs status` block, the launcher entry, the rehearsal (commit).

## Usage budget

About 25% of a five-hour window and 4% of a weekly window (estimates until measured). If the session passes 40% of a five-hour window, stop at the next checkpoint and hand off.

## Risks

- **Bluesky's public API changes or rate-limits.** Back off and keep polling the official report; reporters are a convenience and the official report is the acting source.
- **The reporter list is unknown.** The owner names the handles in `config/watch.toml`; an empty list disables the poll with a status line and nothing else breaks.
- **Possible alerts are noisy.** They never act; `dfs alert dismiss` and the negation set keep them readable.
- **The laptop sleeps or the window closes.** Keep-awake plus the heartbeat; `dfs status` says "stale" rather than pretending.
