# ADR-014: Every run is replayable from a manifest, snapshots, seeds, and LLM decision records

**Status:** Accepted (design). **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION entries 3 and 38): MVP run artifacts are JSON and Parquet files; DuckDB arrives with the learning chunk after the MVP; the replay command is after the MVP, but everything replay needs is recorded from day one; every raw download and pre-lock snapshot is archived from Oct 15 onward.

## Context

The brief requires any night to be replayable with an LLM in the loop: inputs, data snapshots, model versions, seeds, and LLM decisions as structured records. Claude Code has no seed or temperature control, and transcripts are kept only 30 days in an internal format (R7). For 395 of 480 entries in your MLB engine nobody could tell which file was uploaded (RR1).

## Options considered

1. **Re-run the LLM on replay.** Not reproducible.
2. **Keep transcripts as the record.** Internal format, 30-day retention, not structured.
3. **A run manifest plus raw snapshots plus structured decision records; replay reuses the records.**

## Decision

Option 3.

- **Run manifest** (`runs/<run_id>/manifest.json`): git commit, configuration hash, model versions, seeds, hashes of every inbox file, snapshot paths, decision-record IDs, output file hashes, timings, and LLM usage reported by each subagent.
- **Snapshots:** every source response saved byte for byte with fetch time and hash under `data/snapshots/<date>/`.
- **Decision records:** every LLM input packet and output file, validation result, and accept or reject reason.
- **Upload tracking:** each exported file's hash, the user's "uploaded N of N" read-back, and the post-upload completeness check, so it is always known which file each entry holds.
- **Replay:** `uv run dfs replay <run_id>` re-executes every deterministic step from snapshots and decision records without network or LLM calls and checks that output hashes match.
- **Storage:** DuckDB (a single-file analytics database) for tables, Parquet for large arrays, plain files for snapshots; none of it is committed to git (it contains entries and other users' names).

## Consequences

- **Results:** any surprising night can be re-examined exactly, and every layer can be re-scored later with new methods.
- **Cost:** a few hundred megabytes of disk per month (BET), on a laptop with about 670 GB free.
- **Workload:** none; a weekly local backup of `data/` and `runs/` to a folder the user chooses.
