# Owner checklist: your work plan, day by day

**Changelog:** 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): Friday reordered so the test contests are entered (and the Oct 16 payout tables saved) before the checks, with C04b's check runnable as an Oct 15 drill if it slips; `dfs out "Name" --no-run` before `dfs repair` in the post-lock step; C11a's drill check after rehearsal 2 and C10's swap check on Sunday; the Drill B commands name the Oct 16 night; Sunday ends by enabling each capability whose drill passed, and Monday uses the Baseline file only if `baseline_model` is enabled; Monday's run files everything under Oct 20; salary files in the evening routine; the Showdown alternative where a pre-lock check names `classic_main` for Oct 15; the Floor check expects files within 5 minutes. 2026-10-14 (ADJUDICATION-R2 entry R2-34, final audit): standings files are downloaded the morning after each test night: Oct 14's as Thursday's first step, Oct 15's on Friday morning, Oct 16's on Saturday morning. 2026-10-14 (ADJUDICATION-R2 entry R2-33): tonight's steps for the files you sent; salary files downloaded with every entries file (they carry DraftKings' injury Status); the public-repository note. 2026-10-14: created with the final design (ADJUDICATION-R2).

This is everything you do from today through the first readout on Nov 3, in date order. Times are Central. Each step says what to do, when, and about how long it takes. You should not need any other file to follow it.

**Words used here.**
- **Build session:** open Claude Code in the `nba-dfs` folder and type `/run-chunk <ID>` (for example `/run-chunk C01`). It runs on its own for 1 to 3 hours and ends by telling you what it built, one check for you to run, and the next line to type. At the end it asks you to type `/usage` and give it the five-hour and weekly percentages. Start build sessions on your **Team seat**; keep the **Pro plan** free for evenings.
- **Terminal command:** a line starting with `uv run dfs` that you type in a terminal opened in the `nba-dfs` folder. After Friday you can also run the same commands from the **desktop launcher** (a shortcut that works with Claude closed).
- **Floor:** the simple, always-available lineup builder (valid, injury-scrubbed lineups from simple projections). **Baseline:** the full model (simulation, opponent field, prize settlement, selection). The Floor file is always uploaded first; a Baseline file replaces it only when it passes its checks.
- **Entries file:** the CSV you download from a DraftKings contest's "Edit entries" page (one per slate). **Salary file:** the CSV from "Export to CSV" on a draft page. **Always download both together:** only the salary file carries DraftKings' injury `Status` (OUT, Q), which is the engine's only injury signal in preseason. **Payout table:** the prize list on a contest's page; you copy its text into `inbox/payouts/<contest ID>.txt`.
- **Rehearsal:** a live practice on a real preseason slate with a $0.25 entry. **Drill:** a practice on saved files with the clock set back; it never touches your real records.
- **"Tight":** a file row whose game locks within about 4 minutes. It is still written; if your upload misses the lock, the lineup you uploaded before simply stays.
- **Change request:** if a build session finds a problem in the design, it writes it up in `docs/build/PROGRESS.md` and, if it cannot continue, stops and asks you. Nothing in the design changes until you say yes.

**Rules that keep you safe.** Never put files into `out/uploads/` yourself. Never put standings files in the project folder (they carry other people's names); keep them in your private standings folder. Upload to DraftKings yourself; nothing automates the site. **Your GitHub repository `bleeski/nba-dfs` is public** (checked Oct 14): the engine keeps your DraftKings files and lineups out of git, but I recommend making it private (GitHub, the repository's Settings, General, Danger Zone, Change visibility; about 1 minute).

---

## Wednesday Oct 14 (today, evening): about 45 minutes plus one build session

1. **Approve the design** (2 minutes). Tell this session "approved". Then open a fresh Claude Code session in the `nba-dfs` folder and type `/run-chunk C01` (about 1.5 to 2 hours; it builds the skeleton and contracts).
2. **Check Thursday's DraftKings slates** (5 minutes). Thursday Oct 15 has 2 games (tips 6:30 and 7:30 pm CT). If there is a Classic slate, enter one $0.25 Classic contest and one $0.25 Showdown contest. If there is no Classic slate, enter the Showdown on Thursday and plan the Classic for Friday.
3. **Build both lineups by hand** in the DraftKings browser page (10 minutes). This gives the engine a real round trip of your own lineups even if Thursday's build runs late.
4. **Export the files** (5 minutes): each contest's entries file and each slate's salary file. Leave them in Downloads.
5. **Export the Oct 20 salary files** (5 minutes): the opening-night main Classic (3 games), the night Classic (2 games), and the three Showdowns (BOS at DET, PHI at NYK, OKC at SAS). Leave them in Downloads.
6. **Tonight's test files (you already entered one $0.25 Classic and one $0.25 Showdown contest and sent the files; they are archived).** About 20 minutes across the evening:
   - **Before 6:30 pm CT: fill both lineups by hand** in the DraftKings browser page. Both entries are still blank reservations, and a blank entry shows no locked players after the tip. Build the Classic lineup with some players from the 7:30 pm ET games and at least two from DEN at LAC (10:30 pm ET).
   - **About 6:15 pm CT:** re-download the Classic salary file (it shows whether DraftKings fills the `Starting` column near tip).
   - **Between about 6:45 and 9:15 pm CT:** re-download the Classic entries file. It will show some players locked and some still open, which is exactly what the late-swap tests need.
   - **After 9:30 pm CT:** re-download the Showdown entries file.
   - Leave all of them in Downloads (or send them to a session); the next build session archives them.
   - Their standings files are Thursday's first step.
7. **Housekeeping** (5 minutes): rotate the Anthropic API key stored in plain text at `Documents\dfs-os\.env.txt`, and make sure no `ANTHROPIC_API_KEY` is set in your shell (it would silently replace your Claude login).
8. **Check after C01 finishes** (2 minutes): run `uv run dfs --help` and expect a list of commands including `night`, `status`, `out`, `in`, `start`, `swap`, `repair`, `uploaded`. Then run `uv run pytest -m smoke -q` and expect all tests to pass in under a minute.

## Thursday Oct 15: three build sessions, then rehearsal 1 (about 1 hour 15 minutes of your time)

1. **Morning** (2 minutes): download the standings files for your two Oct 14 test contests into your **private standings folder** (never the project folder).
2. **Build sessions, in order, on the Team seat:** `/run-chunk C02`, then `/run-chunk C03`, then `/run-chunk C04a`. Start each during your afternoon desk time (about 15 minutes of attention each).
   - After C02 (2 minutes): `uv run dfs status`. Expect both slates listed with tip times in Central, your entry counts, where each file was archived, and your files still in Downloads.
   - After C03 (5 minutes): `uv run dfs repair --slate classic_main` (or the Showdown slate key if Thursday had no Classic slate). Expect a file named in `out/uploads/`, a line saying it passed validation, and `uv run dfs status` showing "valid" and "pending". Upload that file in DraftKings, then `uv run dfs uploaded <that file>`; `dfs status` should now say "committed". This is the minimum rehearsal if the Floor runs late.
   - After C04a: type `/usage` and give the session both percentages. This is the **M1 usage reading**. If C01 to C04a used more than about 35% of your weekly window, the build switches to the **Floor-only** plan (the session tells you; nothing else changes for you this week except that the Baseline waits until after opening night).
3. **Save the payout tables** for your two test contests (45 seconds each): copy the payout text into `inbox/payouts/<contest ID>.txt`. The parser arrives Friday; saving them now is enough.
4. **Rehearsal 1, from about 5:00 pm CT** (about 45 minutes, on the Pro plan):
   1. Re-download both entries files **and both salary files** (3 minutes).
   2. `uv run dfs night --floor` (up to 5 minutes). Expect one upload file per slate and a one-page brief per slate showing your contests with a facts status ("default" for now), "injury status from DraftKings Status" with the salary file's download time and any players removed as OUT (no official injury reports exist in preseason), and "Goal 2 not estimated".
   3. Upload each file in DraftKings (about 2 minutes each). DraftKings must say "uploaded N of N".
   4. `uv run dfs uploaded <file>` for each file.
   5. Before each lock, re-download that entries file and run `uv run dfs status`: every slate "valid", "committed", no mismatches.
   6. After the 6:30 pm lock, re-download the Classic entries file and leave it in Downloads; the next `uv run dfs status` archives it under `data/archive/2026-10-15/`, and the fixture builder turns it into the late-swap test file.
   - If C04a was not finished by 5:00 pm: do the C03 round trip above instead; C04a finishes Friday morning.

## Friday Oct 16: two build sessions, then rehearsal 2 (about 1 hour 45 minutes of your time)

1. **Morning** (2 minutes): download the standings files for your Oct 15 test contests into your **private standings folder** (never the project folder).
2. **Build sessions:** `/run-chunk C11a` first (the launcher, slash commands, safety hooks, capability flags), then `/run-chunk C04b` (injury report and payout facts; it may wait until Saturday).
3. **Enter the test contests while C11a runs, before its check** (about 17 minutes): one $0.25 Classic and one $0.25 Showdown on the 12-game slate; export their entries files and salary files; save both payout tables in `inbox/payouts/<contest ID>.txt` (45 seconds each). Re-download both salary files just before the rehearsal so the injury statuses are fresh.
4. **Checks after each build session:**
   - After C11a (5 minutes): close Claude Code; double-click the desktop launcher; run `dfs night --floor`, then `dfs out "<a player in your test lineup>" --yes`, then `dfs status`. Expect plain-language output and a repaired file naming who replaced him, with no Claude needed. Then open Claude Code and type `/status`: expect each slate's four states, what is off, the file to upload, and the one next action.
   - After C04b (2 minutes): `uv run dfs night --floor`. Expect the contest whose payout table you saved to show "verified". If C04b slips to Saturday, run its check then as a drill on Thursday's saved night instead: `uv run dfs night --floor --night 2026-10-15 --as-of "2026-10-15T17:00-05:00"` (the first line says DRILL; the Oct 15 contest whose payout table you saved on Thursday shows "verified").
5. **Rehearsal 2, from about 5:00 pm CT** (60 to 75 minutes, from the launcher or `/night`):
   1. `dfs night --floor`; upload each file; `dfs uploaded <file>` for each.
   2. **News drill, timed:** at about 30, 10 and 2 minutes before a tip, pick a player in your test lineup and run `dfs out "Name"`; upload the repaired file; `dfs uploaded <file>`; re-download. Note how many minutes each took from typing the command to "committed" (tell the next session or write them in PROGRESS.md's drill log). At 2 minutes, expect the rows to be labeled "tight".
   3. Re-download before each lock.
   4. **Post-lock repair:** after the first lock, re-download the entries file, run `dfs out "<a player in a later game>" --no-run`, then `dfs repair --slate <slate>`; upload; DraftKings must accept it.
   5. If everything passed, run `dfs rehearsed floor` (it records that this version of the Floor passed).
6. **Drill check, after rehearsal 2** (5 minutes): `uv run dfs drill news --at 10 --night 2026-10-15`. Expect the first line to say DRILL, the repair timed in seconds, and the window arithmetic (the minutes to spare with a 4-minute upload); nothing in your real records changes. Note the time in PROGRESS.md's drill log next to the live times.
7. **Evening, after rehearsal, if usage allows:** `/run-chunk C05`.

## Saturday Oct 17 (no games): build sessions only (about 20 minutes of your time)

1. **Morning** (2 minutes): download the standings files for your Oct 16 test contests into your **private standings folder** (never the project folder).
2. **Before C06** (2 minutes): create a free The Odds API key and put it in `config/secrets.toml` as `odds_api_key = "<your key>"` (this file is never committed).
3. **Build sessions, in order, as far as they go:** C04b and C05 if not done Friday, then C06, C07, C08. Each ends with a "What I check" step; run it and compare with its expected result (for example, after C07 the simulation table should show stars near the top and players ruled out at zero; after C08 the most-owned player should be between about 40% and 60%).

## Sunday Oct 18 (no games): the Baseline drills (about 30 minutes of your time)

1. **Build sessions:** C08 if not done, then `/run-chunk C09`, then `/run-chunk C10`.
2. **Drill A, after C09** (10 minutes): `uv run dfs night --night 2026-10-16 --as-of "2026-10-16T17:00-05:00"`. Expect the first line to say DRILL, a Floor file per slate, then within 15 minutes a Baseline file per slate and a one-page brief. Read the brief (5 minutes): facts status shown, three Goal 1 numbers per contest, Goal 2 labeled "model estimate, uncalibrated", stars or obvious value plays at the top of exposures, sanity "passed".
3. **Drill B, after C10** (15 minutes): `uv run dfs drill news --at 30 --night 2026-10-16`, then the same with `--at 10` and `--at 2`. Expect the re-solve time and minutes to spare at 30 and 10; at 2, "re-solve skipped, repair ran, tight". Then the swap check on Thursday's saved post-lock file: `uv run dfs swap --slate classic_main --night 2026-10-15 --as-of "2026-10-15T19:00-05:00" --fixtures`. Expect the first line to say DRILL, a short diff of changed cells with every locked cell untouched, and a new file under `runs/drills/` that passes validation.
4. **Switch on what passed, Sunday night** (2 minutes): for each capability whose drill passed, run `uv run dfs enable baseline_model` (Drill A), and `uv run dfs enable resolve` and `uv run dfs enable swap_open_slots` (Drill B). A capability whose drill did not pass stays off, and the brief says so.
5. **Decision points (the sessions handle them; you just read the result):**
   - If C09 is not done by 6:00 pm, the Baseline stays off for opening night; the Floor runs.
   - If C10 is not done by **10:00 pm**, it waits until after opening night; the repair is the late-news path. Nothing new is built on Monday.

## Monday Oct 19 (no games): enter opening night and the first live Baseline run (about 50 minutes)

1. **Morning:** nothing for you. Sessions may only fix problems until noon.
2. **Afternoon** (15 minutes): enter your Oct 20 contests (about 25 to 50 entries in total to start) and save each new contest's payout table in `inbox/payouts/<contest ID>.txt` (45 seconds each).
3. **Evening, after about 5:30 pm CT** (when the day-before injury reports are out) (30 minutes):
   1. Download every Oct 20 entries file and salary file. Monday's run files everything under Oct 20, the night of the slates.
   2. `/night` (or `dfs night` from the launcher). The Floor files come first: upload each and run `dfs uploaded <file>`.
   3. If `baseline_model` is enabled (you switched it on Sunday after Drill A passed) and the Baseline's sanity check passed, upload the Baseline files too and run `dfs uploaded` for each. The Baseline file is used only when `baseline_model` is enabled; otherwise the Floor files stand.
   4. Re-download each entries file and run `/status`: every slate "valid" and "committed".
   5. Type `/usage` and record it.
   - This is the first look at this season's injury-report files. If the parser needs a fix tonight, a session makes it and runs a short replay drill; that is allowed and expected. If `/status` then shows a capability as stale, the fixing session reruns that capability's drill and records it with `dfs rehearsed` before the evening run.

## Tuesday Oct 20: opening night

You are at the laptop from 12:30 to 2:00 pm CT. First lock is **2:00 pm CT** (BOS at DET, 3:00 pm ET). Code is frozen from 1:00 pm.

| When (CT) | What you do | About |
|---|---|---|
| 12:30 pm | Download every entries file and salary file again (including contests entered after Monday) | 5 min |
| 12:45 pm | Read the news you trust; enter it with `dfs out "Name"`, `dfs in "Name"`, `dfs start "TEAM: A, B, C, D, E"`; then `/night --game-day` (or `dfs night --game-day` from the launcher) | 10 min |
| By 1:30 pm | Upload every file named; `dfs uploaded <file>` for each; re-download the BOS at DET Showdown and the main Classic entries files; `/status` shows "valid" and "committed" | 15 min |
| 2:00 pm | First lock | |
| About 5:30 pm | Re-download the PHI at NYK Showdown entries file before its 6:00 pm lock; check `/status` | 5 min |
| News any time | `dfs out "Name"` (or `/news` in a fresh session); upload the file it names; `dfs uploaded <file>` | 5 min per event |
| After 2:00 pm | For the main Classic: re-download, then `/swap` if late swap is on, otherwise `dfs repair --slate <slate>` for any ruled-out player; upload; `dfs uploaded <file>` | 5 min |
| About 8:00 pm | Re-download the OKC at SAS Showdown entries file before its 8:30 pm lock; check `/status` | 5 min |

**If news breaks and the late-news re-solve is off, slow, or Claude is unavailable**, use these five lines (they also appear at the top of every brief):

1. `uv run dfs out "Name" --no-run`
2. `uv run dfs repair --slate <slate>`
3. Upload the file it names in the browser.
4. `uv run dfs uploaded <file>`
5. `uv run dfs status`

If a row is labeled **"tight"**, upload right away; if the upload misses the lock, your earlier lineup stays in place, and the message names it.

## Wednesday Oct 21 to Monday Nov 3: the first two weeks

- **Every morning** (5 minutes): download the standings files for your flagship contests into your private standings folder. From the day chunk C13 is done, run `/results` after downloading.
- **Every evening:** the nightly routine as on opening night: download entries files and salary files, `/night`, upload the Floor file then any improved file, `dfs uploaded`, re-download before each Showdown lock and the main Classic's first lock, news with `dfs out` or `/news`, `/swap` after the first lock.
- **Build sessions, one or two a day, in this order:** C11b (the news researcher; it stays off until its drill passes and you enable it), C12, C13, C14, C16, C17, C15, then C18 and C19 by Nov 3. Each ends with a check for you.
- **Weekly** (2 minutes): download your DraftKings entry-history export.
- **Any day:** answer change requests when a session asks.
- **Monday Nov 3:** read the readout. It says whether the volume ramp gate passed (no delivery failures, accuracy beating the named baselines, real-field results); only then consider raising entries above 25 to 50 a night.
