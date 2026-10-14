---
description: Start one build chunk from the build plan in this session, following the protocol in CLAUDE.md. Usage: /run-chunk C04
---

**Owns:** running exactly one build chunk end to end (read tracker, read chunk file, build, test, update tracker, commit, stop).
**Invokes:** `uv run pytest`, `uv run dfs ...`, the advisor (or an independent reviewer subagent) when stuck and before declaring done.
**Does not own:** starting the next chunk, changing the plan, nightly engine runs, pushing to the remote.

Chunk to run: `$ARGUMENTS` (a chunk ID such as `C04`; if empty, read `docs/build/PROGRESS.md` and pick the first chunk whose status is `in progress` or, failing that, the first `not started` chunk whose dependencies are all `done`, and confirm the ID with the owner before starting).

Follow the build-session protocol in `CLAUDE.md` exactly:

1. Read `docs/build/PROGRESS.md`. Report the chunk's current status in one line. If `done`, stop. If `in progress (checkpoint N)`, resume from the handoff notes.
2. Read `docs/build/chunks/<ID>-*.md`, then only the files and sections in its reading list.
3. Verify dependencies are `done`; if not, stop and name the chunk to run first.
4. Build the scope, checkpoint by checkpoint, tests passing at each.
5. Consult the advisor when stuck for more than about 20 minutes and once before declaring done; log it in `docs/research/advisor-log.md`.
6. Run the tests named in the chunk's definition of done.
7. Perform the chunk's "What I check" step and report the expected result in plain language.
8. Update `docs/build/PROGRESS.md` (status, dates, commit, usage, deviations, handoff notes, out-of-scope findings).
9. Commit with the chunk ID first in the message. Do not push.
10. Stop. End with: what was built, what the owner should check, and the one line to type next (`/run-chunk <next ID>`).

If the session runs long, stop at the last passing checkpoint, write handoff notes, commit, and tell the owner to run `/run-chunk <ID>` again in a new session.
