# THROWAWAY SPIKE: not engine code. Purpose: summarize the user's past DraftKings NBA entries
# (contest mix, field sizes, payout depth, cash rate, top-1% rate, nightly washout rate) from
# DraftKings' own contest-entry-history export. Reads a file path given as argv[1]; writes a summary.
import sys, re, datetime as dt
import pandas as pd

src = sys.argv[1]
out = sys.argv[2]
df = pd.read_csv(src)
nba = df[df["Sport"] == "NBA"].copy()

def money(x):
    try:
        return float(str(x).replace("$", "").replace(",", ""))
    except ValueError:
        return float("nan")

for c in ["Entry_Fee", "Prize_Pool", "Winnings_Non_Ticket"]:
    nba[c] = nba[c].map(money)
nba["Winnings_Ticket"] = nba["Winnings_Ticket"].map(money)
nba["date"] = pd.to_datetime(nba["Contest_Date_EST"]).dt.date
nba["paid_share"] = nba["Places_Paid"] / nba["Contest_Entries"]
nba["pct_rank"] = nba["Place"] / nba["Contest_Entries"]
nba["cashed"] = (nba["Winnings_Non_Ticket"].fillna(0) > 0) | (nba["Winnings_Ticket"].fillna(0) > 0) | (nba["Place"] <= nba["Places_Paid"])
k = (nba["Contest_Entries"] * 0.01).apply(lambda v: max(1, int(v)))
nba["top1"] = nba["Place"] <= k
nba["is_showdown"] = nba["Entry"].str.contains("Showdown|Captain|@", case=False, regex=True)

lines = []
P = lines.append
P(f"source rows total={len(df)}  NBA rows={len(nba)}")
P(f"NBA date range: {nba['date'].min()} to {nba['date'].max()}  nights={nba['date'].nunique()}")
P("\nGame_Type counts:\n" + nba["Game_Type"].value_counts().to_string())
P("\nContest_Entries (field size) quantiles:\n" + nba["Contest_Entries"].describe(percentiles=[.1,.25,.5,.75,.9]).round(1).to_string())
P("\nEntry_Fee quantiles:\n" + nba["Entry_Fee"].describe(percentiles=[.1,.25,.5,.75,.9]).round(2).to_string())
P("\nPlaces_Paid / Contest_Entries (payout depth) by Game_Type:")
P(nba.groupby("Game_Type")["paid_share"].describe(percentiles=[.1,.5,.9]).round(3).to_string())
P("\nRake check (1 - prize_pool / (fee x entries)), median by Game_Type:")
nba["rake"] = 1 - nba["Prize_Pool"] / (nba["Entry_Fee"] * nba["Contest_Entries"])
P(nba.groupby("Game_Type")["rake"].median().round(3).to_string())
P("\nPer-entry cash rate and top-1% rate by Game_Type:")
P(nba.groupby("Game_Type").agg(entries=("cashed","size"), cash_rate=("cashed","mean"), top1_rate=("top1","mean"), median_pct_rank=("pct_rank","median")).round(3).to_string())
nights = nba.groupby("date").agg(entries=("cashed","size"), contests=("Contest_Key","nunique"), cashes=("cashed","sum"), top1=("top1","sum"))
nights["washout"] = nights["cashes"] == 0
P(f"\nNights: {len(nights)}  washout nights (zero cashes): {int(nights['washout'].sum())}  rate={nights['washout'].mean():.3f}")
P("Entries per night quantiles:\n" + nights["entries"].describe(percentiles=[.1,.5,.9]).round(1).to_string())
P("Contests per night quantiles:\n" + nights["contests"].describe(percentiles=[.1,.5,.9]).round(1).to_string())
P("\nWashout rate by entries-per-night bucket:")
nights["bucket"] = pd.cut(nights["entries"], [0,2,5,10,20,50,1000])
P(nights.groupby("bucket", observed=True)["washout"].agg(["size","mean"]).round(3).to_string())
P(f"\nNights with at least one top-1% finish: {int((nights['top1']>0).sum())} of {len(nights)}")
P("\nEntries per contest (our multi-entry depth) quantiles:")
P(nba.groupby("Contest_Key").size().describe(percentiles=[.5,.9]).round(1).to_string())
open(out, "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
