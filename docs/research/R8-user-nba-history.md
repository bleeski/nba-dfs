# R8. The user's past NBA results on DraftKings: a baseline for both goals

**Date:** 2026-10-13. **Source:** DraftKings' own "contest entry history" export, saved by the user at `C:\Users\benja\Downloads\draftkings-contest-entry-history.csv` (exported 2026-10-09). Only aggregate numbers appear here; no entry keys or contest names.

**Command run:**

```
spikes/.venv/Scripts/python.exe -I spikes/history/nba_entry_history.py \
  "C:/Users/benja/Downloads/draftkings-contest-entry-history.csv" \
  spikes/history/out/<timestamp>_nba_entry_history.txt
```

Full output: `spikes/history/out/20261013-1710_nba_entry_history.txt`.

## The answer

1. **This engine is a big step up in volume.** Past NBA play was 432 entries over 263 nights (October 2023 to July 2026), a median of **1 entry and 1 contest per night**, at a median fee of $0.10. The planned "medium" volume (about 10 contests and 50 to 200 entries a night) is roughly 50 to 100 times more entries per night. VERIFIED.
2. **Washout baseline: 79.5% of past NBA nights had zero cashes** (209 of 263). That is the number Goal 2 attacks, though most of it comes from one-entry nights where washout is close to "the one lineup missed." VERIFIED.
3. **Past lineups finished below the field average.** Per-entry cash rate was 13.2% in Classic (394 entries) and 16.0% in Showdown (25 entries), while DraftKings paid a median 23.3% and 22.5% of those fields. The median finish was at the 59th percentile of the field (worse than half the field). VERIFIED. The first bar for the new engine is to cash at least at the paid share, which means at least matching the field.
4. **Top 1%: 1 finish in 394 Classic entries (0.25%)**, against the 1% an average lineup would get. VERIFIED. Two of 263 nights had a top-1% finish.
5. **DraftKings' payout depth and rake are confirmed on the user's own NBA contests.** VERIFIED.

| Measure (NBA, user's contests) | Classic | Showdown |
|---|---|---|
| Entries | 394 | 25 |
| Median share of field paid (Places_Paid / Contest_Entries) | 23.3% | 22.5% |
| 10th to 90th percentile of share paid | 0.4% to 27.8% | 15.4% to 23.3% |
| Median rake (1 minus prize pool / (fee x entries)) | 15.8% | 15.9% |
| Per-entry cash rate | 13.2% | 16.0% |
| Per-entry top-1% rate | 0.3% | 0% |

The low 10th percentile for share paid (0.4%) comes from a few satellite or winner-take-all style contests; the engine must read each contest's payout depth, not assume 23%.

## Other facts from the file

- **The export carries field size, prize pool, places paid, our place and our points for every entry.** Columns: `Sport, Game_Type, Entry_Key, Entry, Contest_Key, Contest_Date_EST, Place, Points, Winnings_Non_Ticket, Winnings_Ticket, Contest_Entries, Entry_Fee, Prize_Pool, Places_Paid`. VERIFIED. This is a second free, manual source of exact field size and paid places for every contest the user entered, available after the contest. It complements the standings zip (which has every opponent lineup but no payout table).
- Field sizes in past NBA contests: median 2,972 entries, 10th percentile 118, 90th percentile 4,756, maximum 86,215. VERIFIED.
- Game types: Classic 394, Showdown Captain Mode 25, plus a handful of WNBA, Tiers, Starting 5, Best Ball and Snake entries that are out of scope. VERIFIED. WNBA appears under the NBA sport label here too, which matches R6's finding in the lobby.

## Implications for the architecture

- **Baseline metrics for the learning loop:** per-entry cash rate against the contest's paid share, median percentile finish, top-1% rate, and washout-night rate. The engine's first-month report compares against these numbers. What it means: the user gets an honest "better than before or not" answer, with the caveat that higher volume alone lowers washout.
- **Nightly ingest of this export (optional, weekly is enough):** it gives exact field size and places paid for every contest after the fact, which calibrates the Tier 0 field-size estimate and the default payout depth. What it means: about 30 seconds of the user's time per week.
- **Washout baseline caveat:** the historical 79.5% is mostly a one-entry-per-night number. At 50 to 200 entries across about 10 contests, the engine's predicted washout will be far lower whatever it does. The meaningful Goal 2 comparison is predicted versus realized washout at the new volume, not against this history.
