# R6: DraftKings platform mechanics, file formats, contest details, and scoring edge cases

Prepared Tuesday Oct 13, 2026 (NBA preseason) for the NBA DFS engine design. DFS means daily fantasy sports. DK means DraftKings.

Evidence labels: **VERIFIED** means I ran it or saw it in a primary source today (command and output excerpt shown or cited to a saved output file). **SUPPORTED** means credible documentation or a third-party copy of DK data. **BET** means judgment or not yet verified.

---

## Bottom line (read this first)

1. **Do not let the engine call DraftKings' JSON endpoints, even read-only.** DK's Daily Fantasy Terms of Use (last updated 06/30/2026) list, as improper conduct that can lead to disqualification and prize forfeiture, using automated means "to obtain, collect or access any information on the Website". A nightly script that reads `api.draftkings.com` or `draftkings.com/lobby/getcontests` fits that wording. **VERIFIED** (terms text saved and quoted in section 3). What it means: the engine gets contest details from files the user downloads or pastes by hand, which costs about 2 to 8 minutes per night but keeps the user's real-money account out of risk.
2. **Showdown lists every player twice with two different IDs and the Captain salary is exactly 1.5 times the UTIL salary, always a whole $100.** CPT means Captain (the 1.5x slot); UTIL means utility (the five regular Showdown slots). **VERIFIED** on 5 real DK NBA Showdown salary files (2018 to 2021, public copies on GitHub) and 27 DK Showdown files from 2026 in other sports. Not yet seen on a 2026 NBA file (**BET** until the user exports one, see "Do today").
3. **A triple-double earns +4.5 (the +1.5 double-double bonus AND the +3 triple-double bonus).** DK's own recorded points for Russell Westbrook (57 points, 13 rebounds, 11 assists, Mar 29, 2017) are 99.75, which matches base + 4.5 and not base + 3 (98.25). Four more triple-doubles in RotoGuru's DK point logs all match +4.5; zero match +3. **VERIFIED** arithmetic on a third-party copy of a DK standings export plus RotoGuru (section 4a).
4. **The Captain 1.5x multiplier applies to the bonuses too.** In an NBA Showdown export (2020 Eastern Conference Finals Game 6), Bam Adebayo (double-double) shows 89.25 Captain points = 1.5 x (58.0 + 1.5); the other rule would give 88.5. Jayson Tatum matches the same way. **SUPPORTED** for NBA (third-party copy of a DK export plus Basketball-Reference box scores). The user's own NHL Showdown files point the same way: CPT is exactly 1.5 x FLEX on all 75 pairs (**VERIFIED**), and one of those players must have earned a bonus (**SUPPORTED** only, because it relies on NHL scoring values from 2019 to 2020 guides). Upgrade to VERIFIED for NBA with the opening-night check in section 4b.
5. **The DKEntries file does not contain field size or payouts.** The user is right. **VERIFIED.** The contest name and entry fee are in it, and a field-size estimate can be computed from them (section 3.4).
6. **Overtime counts.** Westbrook's 99.75 in an overtime game equals his full-game stats; regulation-only stats would give 80.25. **VERIFIED** DK number, OT split **SUPPORTED** (Basketball-Reference).
7. **Surprise: opening night's main Classic slate locks at 3:00 PM ET, not 7 PM.** DK's lobby lists the Oct 20 main slate (draft group 154575, 3 games) and the BOS @ DET Showdown starting 2026-10-20T19:00Z, which is 3:00 PM Eastern. **VERIFIED** in the lobby snapshot; cross-check with the schedule agent. What it means: the opening-night run must finish by early afternoon, not evening.
8. **Surprise: WNBA contests appear inside DK's NBA lobby** (118 WNBA contests in the `sport=NBA` listing, e.g. "(WNBA ATL @ GSV)"). **VERIFIED.** A team-abbreviation check will not catch them, because WNBA teams reuse NBA codes (ATL, CHI, IND, MIN, PHO, DAL, WAS, and from 2026 TOR and POR). What it means: the validator must reject any file whose Contest Name contains "WNBA" and must require every Game Info matchup and date to appear in the NBA schedule for that slate (the schedule agent owns that data).

### Do today (time-sensitive, about 3 minutes of the user's time)

Tonight's NBA preseason slates are live on DK: Classic draft group 154934 (5 games, locks 7:00 PM ET) and Showdown GSW @ LAL draft group 154936 (locks 10:00 PM ET). A "draft group" is DK's term for one slate of games with one player pool. **VERIFIED** in the lobby snapshot.

- Before lock, the user exports both salary CSVs by hand (in the DK draft screen, "Export to CSV"). That one minute turns these BETs into VERIFIED for 2026 NBA: dual CPT/UTIL IDs, exact 1.5x salary, the Showdown slot label ("UTIL" vs "FLEX"), the multi-position format, and whether the 2026 file carries the new `Status` and `Starting` columns. Cost: about 1 minute, no money.
- Optional, the user's call because it costs money: one $0.25 Showdown entry tonight produces a real 2026 NBA standings file tomorrow, which lets the engine's parser and the Captain-bonus test run on real data a week before opening night. Cost: $0.25 and about 2 minutes.
- Copy the two live rules pages into text files (section 1). Cost: about 2 minutes.

---

## 1. Live rules check

**Result: not verified against the live pages.** **VERIFIED** that I could not read them:

- A plain GET of `https://www.draftkings.com/help/rules/4/70` returned HTTP 200 but only a 24-character page ("Rules - DraftKings / Busy") plus an obfuscated script, which is a bot-detection challenge. I did not try to get around it. Saved: `spikes/dk/out/downloads/draftkings/20261013-1633_rules_nba_classic.html`.
- The WebFetch tool got HTTP 403. The built-in browser pane refused draftkings.com.
- After reading DK's terms (section 3) I stopped all automated access to DK, so no further attempts.

**Manual check (recommended once before Oct 20, then monthly):** the user opens the NBA Classic and NBA Showdown Captain Mode rules pages, selects all, copies, and pastes each into a text file in the project inbox. The engine then diffs them against the attached files. Cost: about 2 minutes per check.

**What I could confirm from the lobby JSON already on disk (VERIFIED):** game type 70 "Classic: Create an 8-player lineup while staying under the $50,000 salary cap. Includes Late Swap." and game type 81 "Showdown Captain Mode: Create your team from 1 game, while staying under the $50,000 salary cap".

**Internal differences between the two attached files (VERIFIED by reading both):**

| Topic | Classic file | Showdown file |
|---|---|---|
| Postponed game | Game disabled, its players score 0; DK decides by 11:59 PM ET on game day | All contests cancelled and refunded |
| Only one game left active | All contests cancelled and refunded | Not applicable (one game by design) |
| Scoring Period adjustment deadline | "before 12:00am ET on the day after the Game Set is scheduled to start" | "before 12:00am ET on the date the Game Set is scheduled" |
| Stats provider named | STATS LLC (now Stats Perform; possibly stale wording, BET) | Not named |
| Roster rule | 8 players from at least 2 different NBA games | 6 players, must include both teams (so at most 5 from one team) |
| Captain | Not applicable | 1.5x points, costs more salary, a player cannot be both CPT and UTIL |

Neither file states a per-team maximum for Classic. DK NBA Classic has no team cap beyond the 2-game rule (**SUPPORTED**: pydfs-lineup-optimizer's DK NBA settings encode only `min_games = 2`).

---

## 2. File formats

### 2.1 Salary CSV (DKSalaries.csv)

**Columns (VERIFIED on 54 files in Downloads, Aug to Oct 2026):** `Position, Name + ID, Name, ID, Roster Position, Salary, Game Info, TeamAbbrev, AvgPointsPerGame`, then in 2026 files also `Status` (54 of 54 files) and `Starting` (43 of 54). Public NBA files from Dec 2024, Jan 2026 and Mar 2026 have only the first nine columns (**SUPPORTED**, GitHub copies), so `Status` and `Starting` were added recently. Rule for the engine: read columns by header name and tolerate extra columns.

Other format facts, all **VERIFIED**:
- Encoding is UTF-8 with a byte-order mark (the first three bytes are `ef bb bf`), and lines end in CRLF. A naive parser sees the first header as `\ufeffPosition`.
- `Name + ID` is always exactly `Name (ID)` (0 mismatches in about 13,000 rows).
- `Salary` is a whole number of dollars, always a multiple of $100. NBA Classic minimum is $3,000 (**SUPPORTED**, 2024 to 2026 NBA files).
- `AvgPointsPerGame` has 1 decimal in 2026 salary files and 2 decimals in the player list embedded in DKEntries files.
- `Status` values seen in 2026 (other sports): blank, IL, OUT, Q, IR, DTD, D, WD. NBA values are not yet seen (**BET**: likely O, Q, GTD or OUT).
- Player names have no accents (e.g., "Luka Doncic", "Nikola Jokic") in the NBA (2018 to 2026), MLB, NFL and NHL files checked; a few DK soccer names do keep accents (output `out/20261013-1659_format_checks.txt`, section 5). Other NBA data sources use accents, so name matching must fold accents either way.
- Byte-order mark and CRLF findings above, and the salary-increment counts, are recorded in `out/20261013-1659_format_checks.txt` (sections 1 and 5).

**Multi-position eligibility (SUPPORTED on three public NBA Classic files, Dec 2024 to Mar 2026):** `Position` shows the player's DK positions; `Roster Position` lists every Classic slot he may fill:

| Position | Roster Position |
|---|---|
| PG | PG/G/UTIL |
| SG | SG/G/UTIL |
| SF | SF/F/UTIL |
| PF | PF/F/UTIL |
| C | C/UTIL |
| PG/SG | PG/SG/G/UTIL |
| SG/SF | SG/SF/F/G/UTIL |
| SF/PF | SF/PF/F/UTIL |
| PF/C | PF/C/F/UTIL |
| PG/SF | PG/SF/F/G/UTIL |

Note the order "F/G" (not "G/F") and that a C is never G or F eligible. The engine should split `Roster Position` on "/" and treat it as the eligibility set, never re-derive it. In Showdown files `Roster Position` is just `CPT` or `UTIL` and `Position` still shows the real positions.

**Game Info (VERIFIED):** `AWAY@HOME MM/DD/YYYY HH:MMAM|PM ET`, for example `LAD@ATL 10/06/2026 06:00PM ET`. Time is US Eastern local time (EDT in October, EST later), 12-hour clock. Soccer uses `AAA vs BBB`; golf uses the tournament name. pydfs-lineup-optimizer's DK importer also handles the literal values `In Progress` and `Final`, which DK puts in Game Info for games that have started when you export mid-slate (**SUPPORTED**). Postponed games may show other text (**BET**; parser must fail closed).

### 2.2 Showdown: each player twice, two IDs (the dual-ID claim)

**VERIFIED for NBA on historical files, VERIFIED for 2026 in other sports, BET for 2026 NBA until tonight's export.**

Command and output excerpt (`spikes/dk/inspect_salary_csvs.py`, output `out/20261013-1643_salary_csv_inspect_github.txt`):

```
python -I inspect_salary_csvs.py out/downloads/github "*.csv"
('draftfast_nba_showdown_salaries.csv', ['CPT','UTIL'], 64 rows, 32 pairs, 0 pairs with same ID, {'exact': 32})
('fantasyfire_MIN_DEN_showdown.csv',    ['CPT','UTIL'], 66 rows, 33 pairs, 0 same ID, {'exact': 33})
('tmatis_rockets_lakers.csv',           ['CPT','UTIL'], 72 rows, 36 pairs, 0 same ID, {'exact': 36})
('rtelmore_DKSalaries-251018.csv',      ['CPT','UTIL'], 66 rows, 33 pairs, 0 same ID, {'exact': 33})
('camandrewz_nba_classic.csv' (actually a 2021 Finals Showdown), 33 pairs, 0 same ID, {'exact': 33})
=== UTIL salaries with odd hundreds (1.5x ends in 50): 0
```

Example pair (2019 WAS @ OKC): `Russell Westbrook (11915876)` CPT $18,600 and `Russell Westbrook (11915844)` UTIL $12,400. Different IDs, CPT = 1.5 x UTIL.

Findings:
- Every Showdown player appears in one CPT row and one UTIL row with **different IDs**. The ID you put in a slot decides the price, so a UTIL ID in the CPT slot is invalid.
- CPT salary is **exactly** 1.5 x UTIL in 189 NBA pairs and 2,252 pairs from 2026 MLB/NFL/NHL files. UTIL salaries always come in $200 steps, so 1.5x is always a whole $100 and **no rounding ever happens**. NBA Showdown UTIL minimum is $1,000 (CPT $1,500).
- In every file the UTIL ID equals the CPT ID minus the number of players, but this is a pattern, not a rule (**BET**). The engine must pair rows by `Name` plus `TeamAbbrev`, never by ID arithmetic.
- **Slot label trap (VERIFIED):** NBA and MLB Showdown use `UTIL`; NFL and NHL Showdown use `FLEX` (in both the salary CSV and the DKEntries header). The validator must read slot labels from the downloaded file's header, never hardcode them.

### 2.3 Entries CSV (DKEntries.csv, the "Edit Entries" download)

**VERIFIED** on raw downloads in Downloads (MLB, NFL, NHL, 2026). Entry IDs redacted below.

```
Entry ID,Contest Name,Contest ID,Entry Fee,CPT,FLEX,FLEX,FLEX,FLEX,FLEX,,Instructions
<ENTRYID>,NHL Showdown $150 Quarter Jukebox (CHI @ VGK),196048725,$0.25,,,,,,,,1. Column A lists all of your contest entries for this draftgroup
<ENTRYID>,...,$1,,,,,,,,2. Your current lineup is listed next to each entry (blank for reservations)
...,3. You can change the lineup for an entry by entering the IDs of the players in the row next to that entry
...,4. Use data from the Name+ID column or the ID column; you cannot use just the player's name
...,5. For faster processing only include entries you are changing in the file you upload
,,,,,,,,,,,Position,Name + ID,Name,ID,Roster Position,Salary,Game Info,TeamAbbrev,AvgPointsPerGame
```

- Columns: `Entry ID, Contest Name, Contest ID, Entry Fee`, then one column per roster slot in DK's slot order, a blank column, then `Instructions`. Classic MLB header: `P,P,C,1B,2B,3B,SS,OF,OF,OF`. NBA Classic should be `PG,SG,SF,PF,C,G,F,UTIL` and NBA Showdown `CPT,UTIL,UTIL,UTIL,UTIL,UTIL` (**SUPPORTED**: a 2019 DK NBA Showdown upload template on GitHub has header `CPT,UTIL,UTIL,UTIL,UTIL,UTIL,,Instructions`).
- To the right: five instruction lines, a blank line, then the full player list (9 columns, no `Status`/`Starting`). Entry rows keep going down the left side while the player list runs down the right side on the same rows, so the parser must split by column position, not by row.
- **No field size, no payout table, no max-entries number.** **VERIFIED.** Only the contest name (which sometimes includes tags like "[150 Entry Max]" or "[Single Entry]", and often the prize pool such as "$100K") and the entry fee as text like `$0.25`. Some names contain double spaces; keep them byte-for-byte.
- **One file per draft group.** Instruction 1 says so. Several contests on the same slate appear as separate rows with different Contest IDs. Classic and each Showdown game are separate draft groups, so they come in separate files. The file does not contain the draft group ID; the engine identifies the slate from the embedded player list (games and dates).
- Encoding: no byte-order mark, CRLF line endings (**VERIFIED**, `out/20261013-1659_format_checks.txt` section 1). Blank lineup cells mean a reserved entry with no lineup yet.
- **The embedded player list matches the salary CSV exactly for the same slate.** For the CHI @ VGK NHL Showdown, 158 of 158 IDs match with identical Roster Position, Salary and Name; 0 IDs on only one side (**VERIFIED**, same output, section 6). What it means: the validator should check uploads against the player list inside the most recently downloaded DKEntries file (DK generated it closest to upload time, so it reflects any pool correction), and use the salary CSV as a cross-check and as the only source of `Status`.
- **What the upload accepts:** player IDs from the `ID` column or `Name + ID` strings, never names alone (instruction 4, **VERIFIED** text). Only rows you change need to be included (instruction 5). Recommendation: write bare numeric IDs, which removes any ambiguity from names with commas or accents, at zero cost.

**Blank upload template (different file, for brand-new lineups):** header is just the slot labels; instructions include "You can create up to 500 lineups per file" (**SUPPORTED**, 2019 DK NBA Showdown template on GitHub). The engine should use the Edit Entries path, because it fills entries the user already paid for.

### 2.4 Standings CSV (contest-standings-<contestId>.zip)

**VERIFIED** on 12 of the user's 2026 standings files (MLB, NHL, soccer; Classic and Showdown), usernames redacted. Output: `spikes/dk/out/20261013-1632_standings_inspect.txt`.

- The zip holds one CSV with a byte-order mark and LF line endings. Header: `Rank, EntryId, EntryName, TimeRemaining, Points, Lineup, (blank), Player, Roster Position, %Drafted, FPTS`.
- **Left table (one row per entry):** `EntryName` is the username, with ` (n/m)` appended when that user has several entries, e.g. `<USER> (15/20)` meaning entry 15 of 20. Ranks can tie. Points can carry floating-point noise such as `103.18001` or `93.149994`, so round to 2 decimals.
- **Lineup string:** `SLOT Player SLOT Player ...`. In 2026 files the slots appear in **alphabetical order of slot label**, not roster order: MLB `1B 2B 3B C OF OF OF P P SS`, NHL `C C D D G UTIL W W W`, Showdown `CPT FLEX FLEX FLEX FLEX FLEX`. A 2017 NBA file used roster order (`PG SG SF PF C G F UTIL`) and a 2017 NFL file used no clear order (**SUPPORTED**), so DK has changed this before. For NBA 2026 expect `C F G PF PG SF SG UTIL` and `CPT UTIL UTIL UTIL UTIL UTIL` (**BET**). Parse by matching known player names from the salary file, not by splitting on spaces (mononyms appear with a double space, e.g. `F  Evanilson`).
- **"LOCKED" in a lineup string** means that slot's player has not started yet and is hidden from other users. Standings downloaded mid-slate are full of it (e.g. `1B LOCKED 2B Ozzie Albies ...`, TimeRemaining 51). Final standings have none. TimeRemaining is remaining player time (for NBA, player-minutes; **BET** on exact units).
- **Right table (one row per player per slot used):** `Player, Roster Position, %Drafted, FPTS`. A player appears once for each slot he was used in, with that slot's ownership. Examples: `Kevin McGonigle SS 12.84%` and `Kevin McGonigle 3B 3.56%`; `Connor McDavid C 53.83%` and `UTIL 2.69%`. For Showdown, the CPT row and FLEX/UTIL row are separate and the CPT row's FPTS is 1.5x: `Jack Eichel FLEX 45.72% 24.5` and `Jack Eichel CPT 24.96% 36.75`. Total ownership of a player = sum of his rows. `%Drafted` is text with a % sign.
- Sanity check passed: for 414 lineups across three files, `Points` equals the sum of the right-table FPTS of the lineup's players, to 0.01 (`out/20261013-1659_format_checks.txt` section 3).
- Rows after the right table ends have 9 fields, not 11; the parser must accept ragged rows (same output).
- **Rounding (SUPPORTED):** NBA UTIL points are multiples of 0.25, so CPT points can have 3 decimals (85.875). The public NBA export shows `85.88`. Whether DK sums 85.875 or 85.88 into lineup Points is unknown (open question).

### 2.5 Late swap (editing after some games lock)

"Late swap" means changing players in games that have not started after earlier games have locked. Classic NBA has it (lobby text "Includes Late Swap", **VERIFIED**).

Workflow (**SUPPORTED** by DK's instructions plus tool guides): the user re-downloads DKEntries for the draft group, the engine edits only unlocked slots, the user uploads the edited file on the same page. Facts:
- **Locked players appear as `Name (ID) (LOCKED)` in the re-downloaded DKEntries file.** **VERIFIED** in a mid-slate 2026 MLB DKEntries file (87 locked cells, 63 open cells across 15 entries; example `Gerrit Cole (43828848) (LOCKED)`; `out/20261013-1659_format_checks.txt` section 2).
- A locked player cannot be added or removed (attached rules). Any swap involving a game made after its real-life start (even if it started early) gets the lineup disqualified and refunded (attached rules). So "locked" = scheduled start time or the moment DK's feed shows the game started, whichever is first.
- What DK does with a `(LOCKED)` suffix in an uploaded cell, and the exact error wording when a locked slot is changed, are **not documented anywhere I could find** (**BET**: DK rejects that entry row and accepts the others). Safe rule: in the upload, write the same player ID that is already locked in that slot, unchanged, and never move a locked player to another slot.
- DK's upload page reports a count like "successfully uploaded 4 of 4 lineups" (**SUPPORTED**, tool guide). The engine should ask the user to read back that count; anything less than all rows means some rows were rejected.
- Mobile caveat: the DK app cannot download the CSV; a browser is needed (**SUPPORTED**).

---

## 3. Contest details and DraftKings' terms

### 3.1 What the public lobby JSON returns (one request, made before reading the terms)

`GET https://www.draftkings.com/lobby/getcontests?sport=NBA` returned HTTP 200, 1.4 MB, 1,852 contests, 17 draft groups, 8 game types. **VERIFIED.** Saved: `out/downloads/draftkings/20261013-1633_lobby_nba.json`; analysis: `out/20261013-1637_lobby_analysis.txt`.

Contest fields that came back: `a` (entry fee), `attr` (flags such as IsGuaranteed, IsDoubleUp, IsWinnerTakeAll, IsQualifier), `crownAmount`, `crownsAwarded`, `cs`, `cso`, `dg` (draft group ID), `ec`, `fpp`, `freeWithCrownCash`, `freeWithCrowns`, `fwt`, `gameType`, `gameTypeId`, `id` (contest ID), `ir`, `isBonusFinalized`, `isOwner`, `isSnakeDraft`, `m` (maximum field size), `mec` (maximum entries per user), `n` (name), `nt` (entries so far), `payoutDescriptionMetadata`, `pd` (prize text), `po` (prize pool), `pt`, `rl`, `rlc`, `rll`, `s`, `sa`, `sd` (start time, UTC epoch milliseconds), `sdstring` ("Tue 3:00PM"), `so`, `ssd`, `startTimeType`, `tix`, `tmpl` (contest template ID), `uc`, `ulc`.

- The meanings of `m`, `mec`, `nt` are confirmed by consistency: every "[Single Entry]" name has `mec` 1 (55 of 55), every "[N Entry Max]" name has `mec` N (14 of 14), and `nt` never exceeds `m` (1,474 of 1,474). **VERIFIED.**
- `payoutDescriptionMetadata` holds only the top prize or total (1 item in 1,846 contests, 0 in 6). **The full payout table is not in the lobby.** It lives in the contest-detail endpoint, which I did not call (see 3.2).
- Draft group fields: `DraftGroupId, ContestTypeId, StartDate` (UTC), `StartDateEst` (Eastern local time despite the name), `GameCount, ContestStartTimeSuffix` (e.g. " (BOS @ DET)"), `GameTypeId, DraftGroupTag, GameSetKey`.
- Game types: 70 Classic, 81 Showdown Captain Mode, 112 In-Game Showdown (H2), 73 Tiers, 343 Single Stat Points, 188 Snake, 170 Best Ball, 193 Snake Showdown.
- Opening night (Oct 20) is already listed: Classic main draft group 154575 (3 games, 3:00 PM ET), Classic "(Night)" 154827 (2 games, 7:00 PM ET), Showdowns 154825 BOS @ DET 3:00 PM, 154826 PHI @ NYK 7:00 PM, 154829 OKC @ SAS 9:30 PM ET. Flagship: "NBA $600K Opening Tip Off [$200K to 1st]", $20, 150-max, 35,294 maximum entries.

`contests/v1/contests/{id}` and `draftgroups/v1/draftgroups/{id}/draftables` were **not called**, so I cannot report their fields. NBA dual IDs were verified from public salary files instead (2.2).

### 3.2 DraftKings Terms of Use on automated access

Source: DraftKings Daily Fantasy Terms of Use, https://www.draftkings.com/help/terms, "Last Updated 06/30/2026". **VERIFIED** (text saved as `out/downloads/draftkings/terms_text.txt`). Brief quotes:

- Conduct deemed improper includes using automated means "to obtain, collect or access any information on the Website". The parenthetical names "harvesting bots, robots, parser, spiders or screen scrapers" and the clause ends "for any purpose".
- A separate item bans automated means to interact with the site, listing "creating a lineup, and editing a lineup". (Our design already keeps uploads manual.)
- Consequence: DK "may disqualify any entrant from a Contest, refuse to award benefits or prizes" and can require prizes be returned.
- Content is provided "for your information and personal use only".
- Useful for modeling: "In the event of a tie, prizes are divided evenly".

**Assessment (BET, plain reading, not legal advice):** a few read-only scripted calls per night to public JSON would still be "automated means ... to access information", and the clause has no exception for low volume or public endpoints. `robots.txt` does not block `/lobby/getcontests` (it blocks `/lineup/`, `/contest/`, `/draft/` and others), but robots.txt is not permission; the terms govern. The risk lands on the user's real-money account (disqualification, prize forfeiture), so the right architecture keeps every DK interaction manual. If the user wants the convenience, the low-cost path is to email DK support and ask for written permission for a handful of read-only requests per night (BET on the answer).

**Disclosure of requests I made today, all before reading the terms except the terms page itself (VERIFIED, log files in `spikes/dk/out/`):** 16:33 rules page (200, bot challenge); 16:33 `lobby/getcontests?sport=NBA` (200); 16:34 `help/terms` (200); 16:34 `www.draftkings.com/robots.txt` (200); 16:34 `api.draftkings.com/robots.txt` (404). Also one WebFetch of the rules page (403) and one blocked browser-pane attempt. All anonymous, no cookies, about 1 per second. I made no further DK requests after reading the terms. The saved lobby file was used offline for this research only and should not become an engine input.

Other sources I own:
- **RotoGrinders** terms (https://rotogrinders.com/terms-of-service, page stamp 2024-09-15): users may not use "unauthorized automated means to gather data from or about the Service". **VERIFIED.** Hand-reading for one-time research is fine; no nightly dependency.
- **RotoGuru**: no terms page found; footer says NBA data is licensed from Uncommon Cents LLC, all rights reserved; and "RotoGuru will not be producing stats for the 2021-22 NBA season". **VERIFIED.** Useful only for historical scoring checks; not a nightly source.
- **FantasyCruncher**: terms page not located (`/terms` returned only a menu). **BET**: assume similar restrictions; no nightly dependency.

### 3.3 Manual fallback for field size and payouts

Recommended three tiers (**BET** on minutes):

| Tier | What the user does | What the engine gets | Minutes per night |
|---|---|---|---|
| 0, default | Nothing extra (the DKEntries file is already downloaded) | Contest name, entry fee, prize pool from the name when present; estimated maximum field = prize pool / (fee x 0.85); payout curve from the contest class (section 5) | 0 |
| 1, exact | For each contest not seen before: open the contest in the lobby, click the contest name to open Contest Details, note "Entries x / y" and "Max entries per user", open the Prize Payouts tab, select the payout table, copy, paste into `inbox/payouts/<contestId>.txt` | Exact maximum field, entry limit, full payout table | About 45 seconds per new contest; 3 to 8 minutes on the first nights, falling to 1 to 2 minutes once recurring contests are cached by name, fee and size |
| 2, truth | Next morning download the standings zip (already planned for ownership) | Actual entries (row count), actual ownership, actual points | About 20 seconds per contest |

The field-size estimate works because DK's GPP rake is a steady 15 to 16 percent (GPP means guaranteed prize pool tournament; rake is DK's cut): for the Opening Tip Off, 600,000 / (20 x 0.85) = 35,294, exactly the listed maximum (**VERIFIED**). What it means: the engine can run every night without any manual step and simply gets more exact when the user pastes payout tables.

---

## 4. Scoring edge cases (discriminating tests)

DK NBA scoring per the attached files: point +1, made 3-pointer +0.5, rebound +1.25, assist +1.5, steal +2, block +2, turnover -0.5, double-double +1.5, triple-double +3, double-double and triple-double counted from points, rebounds, assists, blocks, steals, max 1 of each per player. "Base" below means everything except the two bonuses.

### 4a. Does a triple-double get +4.5 (both bonuses) or only +3?

**Answer: +4.5.** Formula A = base + 3; formula B = base + 1.5 + 3.

| Game | Line (PTS, 3PM, REB, AST, STL, BLK, TO) | Base | A (+3) | B (+4.5) | Recorded | Source of recorded number |
|---|---|---|---|---|---|---|
| Westbrook @ ORL, 2017-03-29 (OT) | 57, 6, 13, 11, 3, 0, 7 | 95.25 | 98.25 | **99.75** | **99.75** | DK standings export, contest 39051001 (public copy); RotoGuru also 99.75 |
| Westbrook @ ATL, 2021-05-10 | 28, 3, 13, 21, 0, 0, 3 | 75.75 | 78.75 | **80.25** | **80.25** | RotoGuru DK log; FantasyLabs (May 12, 2021) says "at least 80.25" DK points in 4 of 5 games |
| Doncic @ SAC, 2020-01-15 | 25, 0, 15, 17, 0, 0, 6 | 66.25 | 69.25 | **70.75** | **70.75** | RotoGuru; line confirmed on Basketball-Reference |
| Westbrook vs POR, 2020-01-15 | 31, 2, 11, 12, 1, 0, 1 | 65.25 | 68.25 | **69.75** | **69.75** | RotoGuru |
| Fultz @ LAL, 2020-01-15 | 21, 0, 11, 10, 1, 0, 1 | 51.25 | 54.25 | **55.75** | **55.75** | RotoGuru |

Worked example, Westbrook 2017: 57 + (6 x 0.5 = 3) + (13 x 1.25 = 16.25) + (11 x 1.5 = 16.5) + (3 x 2 = 6) + 0 - (7 x 0.5 = 3.5) = 95.25; plus 4.5 = 99.75.

Controls (same DK export, double-double only, expect +1.5): Chris Paul 27 pts, 13 ast: base 52.75 + 1.5 = 54.25, DK 54.25. Stephen Curry 29 pts, 11 ast: 52.25 + 1.5 = 53.75, DK 53.75. No-bonus control: Isaiah Thomas 51.25 = DK 51.25. Across all 80 RotoGuru lines tested: 4 of 4 triple-doubles match B and 0 match A; 13 of 13 double-doubles and 63 of 63 no-bonus lines match. DK's own FPTS equals RotoGuru's for all 9 players present in both files.

Commands: `spikes/dk/scoring_formula_test.py` (output `out/20261013-1639_scoring_formula_test.txt`) and `spikes/dk/dk_vs_rotoguru.py` (output `out/20261013-1650_dk_vs_rotoguru_20170329.txt`). Label: **VERIFIED** arithmetic; the DK numbers come from a third-party copy of a DK export and RotoGuru, so the source is **SUPPORTED** grade. The rule has been stable since at least 2017; re-confirm on opening night with the user's own standings file (same check as 4b).

### 4b. Does the Captain 1.5x apply to the bonuses?

**Answer: yes, Captain points = 1.5 x (base + bonus).**

NBA evidence (2020 ECF Game 6, MIA 125 BOS 113, public copy of a DK Showdown export; box scores from Basketball-Reference):

| Player | Line (PTS, 3PM, REB, AST, STL, BLK, TO) | Base | Bonus | 1.5 x (base + bonus) | 1.5 x base + bonus | DK CPT FPTS |
|---|---|---|---|---|---|---|
| Bam Adebayo | 32, 0, 14, 5, 1, 0, 2 | 58.00 | 1.5 (DD) | **89.25** | 88.50 | **89.25** |
| Jayson Tatum | 24, 3, 7, 11, 2, 1, 2 | 55.75 | 1.5 (DD) | **85.875** | 85.125 | **85.88** (displayed to 2 decimals) |

Cross-sport evidence from the user's own DK files: all 75 CPT/FLEX pairs across three NHL Showdown files have CPT FPTS exactly 1.5 x FLEX FPTS (**VERIFIED**, `out/20261013-1637_captain_ratio_check.txt`). That equality only discriminates if someone earned a bonus. Jack Eichel (FLEX 24.5, CPT 36.75) probably did: I enumerated every NHL stat line that gives 24.5 under DK NHL scoring (goal 8.5, assist 5, shot 1.5, block 1.3, plus +3 bonuses), and all 9 such lines include at least one +3 bonus, so if bonuses were not multiplied his CPT score would be 35.25 or 33.75, not 36.75 (`spikes/dk/nhl_bonus_enumeration.py`). This part is **SUPPORTED** only: the scoring values come from 2019 to 2020 DKNetwork and RotoWire guides, and a RotoGrinders article titled "NHL DFS Scoring Changes on DraftKings" turned up in search but I did not read it, so DK may have changed NHL scoring since. The NBA conclusion stands on the Celtics and Heat file alone. RotoWire's Dec 16, 2025 NBA Showdown article also says the Captain "earns 1.5x of their final DKFP total" (**SUPPORTED**).

**Opening-night check to make this VERIFIED for 2026 NBA (cost: zero extra minutes, runs on the standings file the user downloads anyway):** for every player in the Showdown standings right table who has both a CPT row and a UTIL row, assert CPT FPTS = 1.5 x UTIL FPTS within 0.01. For any of them with a double-double (from the box score), the bonus-not-multiplied rule would give CPT = 1.5 x UTIL - 0.75 (or - 2.25 for a triple-double), so the equality alone discriminates. Run the same file through the 4a check for any triple-double.

### 4c. Other edge cases worth a regression test

| Rule | Status | Test |
|---|---|---|
| Only PTS, REB, AST, BLK, STL count toward DD/TD (not 3PM, not turnovers) | SUPPORTED (rules text); consistent with all 80 lines | Synthetic: 10 pts, 10 turnovers, 9 rebounds scores no bonus |
| Max one DD and one TD bonus; a quadruple-double gets +4.5 total | SUPPORTED (rules "Max 1 Per Player"); no real example tested | Synthetic: 10/10/10/10 line gets base + 4.5 |
| 3-pointer bonus is +0.5 on top of the 3 points (a made three = 3.5) | VERIFIED via formula match on 80 lines with 3PM | Curry line above |
| Turnovers -0.5 each | VERIFIED (same) | Doncic 6 TO line |
| Inactive or DNP players score 0, no replacement | VERIFIED cross-sport (NHL standings list drafted players with 0.00, e.g. at CPT and FLEX); SUPPORTED NBA (Celtics-Heat file lists several 0s) | Standings player with no minutes = 0 |
| Overtime stats count | VERIFIED DK total 99.75 equals full game; regulation-only would be 80.25 (no triple-double without OT, since his OT line was 7 pts, 4 reb, 2 ast per Basketball-Reference) | Westbrook 2017-03-29 |
| Postponed game: Classic disables the game (players 0), Showdown cancels and refunds | SUPPORTED (attached rules) | Validator flags any lineup with a disabled game; scoring treats it as 0 |
| Suspended game: only stats before suspension count | SUPPORTED (attached rules) | Fixture with partial stats |
| Captain points can have 3 decimals (x.125, x.375, x.625, x.875); DK displays 2 | SUPPORTED (85.875 shown as 85.88) | Engine stores quarter-points exactly; compare to DK with 0.01 tolerance |
| Ties split prizes evenly | VERIFIED (terms text) | Payout simulator splits tied ranks |

---

## 5. Contest structure facts for modeling

From today's lobby snapshot (**VERIFIED**, 1,852 NBA contests, Oct 13 and Oct 20 slates). "Field size" here is the maximum (`m`); "single-entry" and "N-max" refer to entries allowed per user.

| Class | Count | Field size median (max) | Entry fee median | Rake median |
|---|---|---|---|---|
| Classic single-entry (field > 20) | 196 | 23 (5,945) | $3 | 13% |
| Classic 3-max | 32 | 105 (3,963) | $1.50 | 15% |
| Classic 20-max | 37 | 297 (35,671) | $0.25 | 16% |
| Classic 150-max | 10 | 8,380 (71,343) | $5 | 16% |
| Showdown single-entry | 101 | 23 (594) | $3 | 13% |
| Showdown 3-max | 10 | 112 (118) | $1 | 15% |
| Showdown 20-max | 24 | 1,189 (8,917) | $0.25 | 16% |
| Showdown 150-max | 9 | 5,112 (13,071) | $5 | 16% |
| Small single-entry (3 to 20 players) | 1,055 | 5 | $10 | 10% |

- **Entries per user are capped near 3 percent of the field.** In 92 of 122 multi-entry contests, max entries per user = min(150, floor(0.03 x field)); the others are 20-max contests where the nominal cap is lower. Example: "$350K Power Dunk", 875 entries, 26 per user. **VERIFIED.**
- **Top-heaviness:** first prize is 17 to 33 percent of the pool in the big GPPs (Opening Tip Off 33.3 percent, $200K Showdown Fadeaway 25 percent, $60K Zone 16.7 percent). **VERIFIED** from contest names.
- **Share of field paid and minimum cash (SUPPORTED, DK NFL contests, 4for4, Jan 2022):** 20 to 27 percent of entries paid; minimum cash 1.5x to 2.0x the entry fee; rake 10 percent at high stakes, 15.9 percent at low stakes. Examples: 20-max $1, 178,359 entries, 26.3 percent paid, 1.5x min cash; single-entry $100, 4,444 entries, 20.1 percent paid, 1.5x; 3-max $5, 9,512 entries, 21 percent paid, 2.0x. DK uses the same payout templates across sports (BET). Exact NBA payout tables need Tier 1 of the manual fallback.
- What it means for the engine: model each contest from its class with these defaults, and replace with the exact pasted table when available; the 3 percent cap means a 150-lineup portfolio only fits in fields of 5,000 or more.

---

## Open questions

1. Does the 2026 NBA Showdown CSV use `UTIL` (expected) or `FLEX`, and does it carry `Status`/`Starting`? Resolved by tonight's manual export.
2. What exactly does DK do with an uploaded cell that still carries ` (LOCKED)`, and what is the error wording when a locked slot is changed? Test on a $0.25 contest during a preseason late swap or on opening night.
3. Does DK sum Captain points at 3 decimals (85.875) or the displayed 2 (85.88) into lineup Points? Check the first NBA Showdown standings file.
4. What text appears in `Game Info` and `Status` for an NBA player whose game is postponed? Not observable until it happens; parser must fail closed.
5. Is the Oct 20 3:00 PM ET start real (BOS @ DET) or a DK placeholder? Schedule agent to confirm.
6. Will DK grant written permission for a few read-only lobby or contest-detail requests per night? Only if the user wants to ask.
7. Do the live rules pages still match the attached files (for example the STATS LLC wording)? Resolved by the 2-minute manual copy.

## Implications for the architecture

- **All DK data enters through files the user downloads or pastes.** Inbox folders: `salaries/`, `entries/`, `payouts/`, `standings/`, `rules/`. What it means: no account risk, at about 2 to 8 minutes of user time per night.
- **The engine never derives IDs, slot labels, or eligibility.** It reads them from the latest downloaded files. What it means: format drift (FLEX vs UTIL, new columns) cannot produce an invalid upload.
- **Every output file goes through one deterministic validator, and the engine refuses to emit a file that fails.** What it means: the user never receives an invalid upload; a failure costs a re-run, not a rejected entry.
- **Late swap is a separate mode keyed on the re-downloaded DKEntries file.** What it means: the user re-downloads before each late-swap window (about 30 seconds each), and the engine only touches unlocked slots.
- **Post-contest learning uses the standings zip** (actual ownership by slot, actual points, CPT vs UTIL ownership) and runs the 4a and 4b scoring checks automatically every night. What it means: scoring-rule drift is caught the morning after it happens.

### Validator checklist (must all pass before a file is written)

File and slate integrity
- [ ] Salary file and entries file belong to the same draft group: every player ID in the entries' embedded player list exists in the salary file with the same Roster Position and Salary, and dates in Game Info match the slate date.
- [ ] Lineups are validated against the embedded player list of the most recently downloaded DKEntries file; the salary CSV is a cross-check and the source of `Status`.
- [ ] Reject the file if any Contest Name contains "WNBA", and require every Game Info matchup and date to appear in the NBA schedule for that slate (team codes alone cannot tell NBA from WNBA).
- [ ] Slot labels and their order are copied from the downloaded DKEntries header, not hardcoded.
- [ ] Output keeps `Entry ID, Contest Name, Contest ID, Entry Fee` byte-for-byte from the latest download (including double spaces), contains no Entry ID absent from that download, and no more rows per contest than the download.
- [ ] Output encoding and line endings mirror the downloaded DKEntries file (UTF-8 without byte-order mark, CRLF).
- [ ] Each edited slot cell is a bare integer player ID (no "12345678.0" spreadsheet artifacts, no names alone).
- [ ] Rows the engine did not change are left out of the upload, per DK instruction 5, so untouched locked cells are never rewritten.
- [ ] Every slot in every output row is filled (no partial lineups).

Classic lineup rules
- [ ] Exactly 8 players, one per header slot.
- [ ] Each player's `Roster Position` (split on "/") contains the slot label he is placed in.
- [ ] No player ID appears twice in a lineup.
- [ ] Total salary is at most $50,000 (integer arithmetic).
- [ ] Players come from at least 2 different games.
- [ ] No player from a disabled or postponed game (hard fail), and a warning for any `Status` of OUT/O.

Showdown lineup rules
- [ ] Exactly 1 CPT slot and 5 UTIL (or FLEX, as the header says) slots.
- [ ] The CPT slot holds an ID whose row says `CPT`; each UTIL slot holds an ID whose row says `UTIL`/`FLEX`.
- [ ] The same person (paired by Name plus TeamAbbrev) is not in both CPT and UTIL.
- [ ] Total salary, using the salary of the exact ID chosen, is at most $50,000.
- [ ] Both teams are represented (at most 5 from one team).

Late swap rules
- [ ] Every cell that was `(LOCKED)` in the latest download, or whose game start time is at or before now plus a safety margin, contains the same player ID in the same slot. PROVISIONAL: whether DK accepts that cell as a bare ID, as `Name (ID)`, or only with the ` (LOCKED)` suffix is Open Question 2; settle it with the first $0.25 late-swap test before relying on it.
- [ ] No newly inserted player belongs to a game that has started or starts within the safety margin (Game Info `In Progress`/`Final` counts as started).
- [ ] The edited file is checked against a DKEntries file downloaded after the most recent lock time.

Upload hygiene
- [ ] No more than 500 lineups per uploaded file.
- [ ] After upload, the user confirms DK's "uploaded N of N" count matches the file's row count; any shortfall is logged.

---

## Sources

DraftKings (primary)
- DraftKings Daily Fantasy Terms of Use, last updated 06/30/2026: https://www.draftkings.com/help/terms (saved text: `spikes/dk/out/downloads/draftkings/terms_text.txt`)
- DK NBA lobby JSON, fetched once at 16:33 on 2026-10-13: https://www.draftkings.com/lobby/getcontests?sport=NBA (saved, analyzed offline)
- DK robots.txt: https://www.draftkings.com/robots.txt
- DK NBA Classic rules page (not readable, bot challenge): https://www.draftkings.com/help/rules/4/70
- User's own DK files in `C:\Users\benja\Downloads`: 54 DKSalaries CSVs, raw DKEntries downloads, 12 contest-standings zips (2026, MLB/NFL/NHL/soccer/golf)
- Attached rules: `NBA Classic.txt`, `NBA Showdown Captain Mode.txt`

Public copies of DK files (GitHub, read via `gh api`, untrusted data, saved under `spikes/dk/out/downloads/github/`). GitHub code search ran under the user's logged-in `gh` account; results from the quarantined owner were filtered out by name and never opened.
- NBA Showdown salaries 2019 and upload template: https://github.com/BenBrostoff/draftfast/tree/master/draftfast/test/data
- NBA Showdown salaries: https://github.com/bballboy8/Fantasy-Fire (MIN_vs_DEN_Showdown.csv), https://github.com/tmatis12/datafiles (DraftKings_Rockets_Lakers.csv), https://github.com/rtelmore/optimization-class-project (src/DKSalaries-251018.csv), https://github.com/camandrewz/DraftKingsMoneyball (Basketball/data), https://github.com/galactusaurus/roster_opt (WNBA 2025)
- NBA Classic salaries 2024 to 2026: https://github.com/fadcrush/dfs-optimizer-engine, https://github.com/jackdegen/nba-props, https://github.com/ntran4869/linopt_nba
- NBA DK standings 2017-03-29 (contest 39051001): https://github.com/royh21k/royh21k.github.io (NBA on DraftKings/Final)
- NBA Showdown standings, 2020 ECF Game 6: https://github.com/LeihuaYe/Bootstrap_in_R (Celtics_Heat_Game_6_Actual.csv)
- pydfs-lineup-optimizer DK importer and settings: https://github.com/DimaKudosh/pydfs-lineup-optimizer
- LOCKED parsing example: https://github.com/JonnyRank/nba-dfs-optimizer (src/nba_optimizer/utils.py)

Stats and DK point logs
- RotoGuru DK NBA daily logs (semicolon format), dates 2017-03-29, 2019-03-20, 2020-01-15, 2021-04-03, 2021-05-10: http://rotoguru1.com/cgi-bin/hyday.pl?game=dk&mon=5&day=10&year=2021&scsv=1 (and sibling dates)
- Basketball-Reference box scores (3 page reads): https://www.basketball-reference.com/boxscores/201703290ORL.html, https://www.basketball-reference.com/boxscores/202001150SAC.html, https://www.basketball-reference.com/boxscores/202009270MIA.html

Articles and terms
- RotoWire, NBA DFS DraftKings NBA Cup Showdown strategy, Dec 16, 2025: https://www.rotowire.com/basketball/article/nba-dfs-picks-draftkings-nba-cup-showdown-strategy-for-tuesday-december-16-100777
- FantasyLabs, NBA DFS Breakdown, May 12, 2021: https://www.fantasylabs.com/?p=128563
- 4for4, Best NFL DFS GPPs, Week 18 2021 (published Jan 5, 2022): https://www.4for4.com/2021/w18/best-nfl-dfs-gpps-play-week-18
- DKNetwork NHL scoring guide: https://dknetwork.draftkings.com/2020/07/02/beginner-nhl-dfs-scoring/ ; RotoWire DFS Hockey 101: https://www.rotowire.com/hockey/article/dfs-hockey-101-how-to-play-on-draftkings-47353
- RotoGrinders Terms of Service: https://rotogrinders.com/terms-of-service
- The Solver late swap tutorial: https://thesolver.com/tutorials/late-swap ; Stokastic upload guide: https://www.stokastic.com/articles/dfs-strategy/how-to-upload-dfs-lineups-to-draftkings
- Legal Sports Report on DK scripting policy history: https://www.legalsportsreport.com/2197/draftkings-scripting-controversy/

## Appendix: spike scripts and outputs

All in `C:\Users\benja\Documents\Claude\nba-dfs\spikes\dk\`, each starting with the THROWAWAY SPIKE line; outputs in `out\`.

| Script | Purpose | Output |
|---|---|---|
| inspect_salary_csvs.py | Columns, Game Info, Status, CPT/UTIL pairing and 1.5x check | 20261013-1631_salary_csv_inspect.txt, 20261013-1643_salary_csv_inspect_github.txt |
| nba_classic_positions.py | Position to Roster Position map for NBA Classic | 20261013-1643_nba_classic_positions.txt |
| inspect_standings.py | Standings format, LOCKED, (n/m), right table | 20261013-1632_standings_inspect.txt |
| captain_ratio_check.py | CPT = 1.5 x FLEX in user's NHL Showdown files | 20261013-1637_captain_ratio_check.txt |
| nhl_bonus_enumeration.py | Shows Eichel's 24.5 requires a bonus | 20261013-1638_nhl_bonus_enum.txt |
| scoring_formula_test.py | TD +3 vs +4.5 on RotoGuru logs | 20261013-1639_scoring_formula_test.txt |
| dk_vs_rotoguru.py | DK export FPTS vs RotoGuru, 2017-03-29 | 20261013-1650_dk_vs_rotoguru_20170329.txt |
| fetch_dk_public.py | The DK requests listed in 3.2 (not to be rerun) | 20261013-1633_fetchlog_*.json, 20261013-1634_fetchlog_terms.json |
| fetch_page.py | RotoGuru, RotoGrinders, FantasyCruncher page reads | downloads/<source>/ |
| format_checks.py | BOM/line endings, LOCKED cells, Points = sum FPTS, ragged rows, accents, salary increments, embedded list vs salary CSV | 20261013-1659_format_checks.txt |
| analyze_lobby.py, lobby_field_semantics.py | Offline lobby analysis | 20261013-1637_lobby_analysis.txt, 20261013-1647_lobby_top_prize_share.txt, 20261013-1654_lobby_field_semantics.txt |
