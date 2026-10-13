# THROWAWAY SPIKE: not engine code. Purpose: enumerate every NHL skater stat line that yields a given DK FPTS total (DK NHL skater scoring per DKNetwork/RotoWire guides) to see whether the total REQUIRES a +3 bonus; if so, CPT == 1.5x FLEX for that player shows the Captain multiplier applies to bonuses.
import itertools, sys, os, datetime

def skater(G, A, S, B, SH):
    pts = 8.5 * G + 5 * A + 1.5 * S + 1.3 * B + 2 * SH
    bonus = 3 * (G >= 3) + 3 * (S >= 5) + 3 * (B >= 3) + 3 * (G + A >= 3)
    return pts, bonus

targets = [float(x) for x in sys.argv[1:]] or [24.5]
OUT = os.path.join(os.path.dirname(__file__), "out")
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
L = []
for t in targets:
    sols = []
    for G, A, S, B, SH in itertools.product(range(5), range(6), range(16), range(8), range(3)):
        if G > S or SH > G + A:
            continue
        base, bonus = skater(G, A, S, B, SH)
        if abs(base + bonus - t) < 1e-6:
            sols.append((G, A, S, B, SH, base, bonus))
    nb = [s for s in sols if s[6] == 0]
    L.append(f"target {t}: {len(sols)} stat lines reproduce it; {len(nb)} have NO bonus")
    for s in sols:
        L.append(f"   G={s[0]} A={s[1]} SOG={s[2]} BLK={s[3]} SHP={s[4]} base={s[5]:.1f} bonus={s[6]}  -> CPT if bonus multiplied={1.5*(s[5]+s[6]):.2f}, if not={1.5*s[5]+s[6]:.2f}")
open(os.path.join(OUT, f"{stamp}_nhl_bonus_enum.txt"), "w").write("\n".join(L))
print("\n".join(L))
