# THROWAWAY SPIKE: not engine code. Purpose: show (1) Monte Carlo error for tail probabilities and the gain from common random numbers, (2) how minutes uncertainty and shared per-game multipliers change DK point skew, tails, and double-double odds for a synthetic player. Parameters are illustrative, not fitted to real data.
import sys, datetime, io
import numpy as np

out = io.StringIO()
def p(*a):
    print(*a, file=out)

rng = np.random.default_rng(20261013)

# ---------- Part 1: Monte Carlo standard error for tail probabilities ----------
p("PART 1: Monte Carlo standard error of an estimated probability p from n sims")
p("SE = sqrt(p(1-p)/n); relative SE = SE/p")
for prob in (0.005, 0.01, 0.02, 0.05, 0.25):
    row = []
    for n in (1_000, 5_000, 10_000, 30_000, 100_000):
        se = np.sqrt(prob * (1 - prob) / n)
        row.append(f"n={n:>6}: SE={se:.4f} (rel {se/prob:5.1%})")
    p(f"p={prob:<6}", " | ".join(row))

# Common random numbers: two lineups sharing 6 of 8 players, compare P(top1%) difference
p("")
p("PART 1b: comparing two similar lineups, independent sims vs common random numbers (CRN)")
n_sims = 10_000
reps = 300
k_shared, k_diff = 6, 2
diffs_crn, diffs_ind = [], []
def lineup_scores(shared, unique):
    return shared.sum(axis=1) + unique.sum(axis=1)
field_thresh = np.quantile(rng.gamma(9.0 * 8, 4.0, size=200_000), 0.99)
for r in range(reps):
    shared = rng.gamma(9.0, 4.0, size=(n_sims, k_shared))
    ua = rng.gamma(9.0, 4.0, size=(n_sims, k_diff))
    ub = rng.gamma(9.0, 4.0, size=(n_sims, k_diff)) * 1.01

    a = lineup_scores(shared, ua) >= field_thresh
    b = lineup_scores(shared, ub) >= field_thresh
    diffs_crn.append(b.mean() - a.mean())
    shared2 = rng.gamma(9.0, 4.0, size=(n_sims, k_shared))
    ub2 = rng.gamma(9.0, 4.0, size=(n_sims, k_diff)) * 1.01
    b2 = lineup_scores(shared2, ub2) >= field_thresh
    diffs_ind.append(b2.mean() - a.mean())
p(f"mean P(top1%) lineup A ~ {a.mean():.4f}")
p(f"SD of estimated difference (B-A) across {reps} repeats, n={n_sims}: CRN={np.std(diffs_crn):.5f}, independent={np.std(diffs_ind):.5f}")
p(f"variance reduction factor from CRN: {np.var(diffs_ind)/np.var(diffs_crn):.1f}x")

# ---------- Part 2: synthetic player distribution shapes ----------
p("")
p("PART 2: synthetic starting big man, 32 projected minutes. DK scoring with DD/TD (TD assumed to also earn DD: unverified rule).")
rates = dict(pts=0.62, reb=0.34, ast=0.09, stl=0.028, blk=0.045, tov=0.06, fg3=0.03)  # per minute

def dk_points(pts, reb, ast, stl, blk, tov, fg3):
    cats = np.stack([pts, reb, ast, stl, blk], axis=1)
    n10 = (cats >= 10).sum(axis=1)
    dd = (n10 >= 2).astype(float)
    td = (n10 >= 3).astype(float)
    return pts + 0.5 * fg3 + 1.25 * reb + 1.5 * ast + 2 * stl + 2 * blk - 0.5 * tov + 1.5 * dd + 3 * td, dd, td

N = 400_000
def summarize(name, fp, dd, td, mins):
    q = np.quantile(fp, [0.01, 0.10, 0.50, 0.90, 0.99])
    m, s = fp.mean(), fp.std()
    skew = np.mean(((fp - m) / s) ** 3)
    p(f"{name:<44} mean={m:5.1f} sd={s:4.1f} skew={skew:+.2f} p01={q[0]:5.1f} p10={q[1]:5.1f} p50={q[2]:5.1f} p90={q[3]:5.1f} p99={q[4]:5.1f} P(DD)={dd.mean():.3f} P(TD)={td.mean():.4f} min_sd={np.std(mins):.1f}")

# A: fixed minutes, independent Poisson
mins_a = np.full(N, 32.0)
draw = {k: rng.poisson(v * mins_a) for k, v in rates.items()}
draw["fg3"] = np.minimum(draw["fg3"], draw["pts"] // 3)
fp, dd, td = dk_points(draw["pts"], draw["reb"], draw["ast"], draw["stl"], draw["blk"], draw["tov"], draw["fg3"])
summarize("A fixed 32 min, independent Poisson", fp, dd, td, mins_a)

# B: minutes uncertainty: normal core sd 4, cap 44, 4% early exit (injury or ejection), 8% blowout trim, 6% overtime +5
core = rng.normal(32, 4, N)
u = rng.random(N)
mins_b = core.copy()
mins_b[u < 0.04] = rng.uniform(4, 20, (u < 0.04).sum())
blow = (u >= 0.04) & (u < 0.12)
mins_b[blow] -= rng.uniform(4, 9, blow.sum())
ot = rng.random(N) < 0.06
mins_b[ot] += rng.uniform(2, 5, ot.sum())
mins_b = np.clip(mins_b, 0, 48)
draw = {k: rng.poisson(v * mins_b) for k, v in rates.items()}
draw["fg3"] = np.minimum(draw["fg3"], draw["pts"] // 3)
fp, dd, td = dk_points(draw["pts"], draw["reb"], draw["ast"], draw["stl"], draw["blk"], draw["tov"], draw["fg3"])
summarize("B minutes mixture, Poisson given minutes", fp, dd, td, mins_b)

# C: B plus per-game shared multipliers: game pace/usage factor shared by all stats (gamma, cv 0.12)
# and stat-specific overdispersion (gamma, cv 0.20) -> negative binomial counts
g = rng.gamma(1 / 0.12**2, 0.12**2, N)
draw = {}
for k, v in rates.items():
    eps = rng.gamma(1 / 0.20**2, 0.20**2, N)
    draw[k] = rng.poisson(v * mins_b * g * eps)
draw["fg3"] = np.minimum(draw["fg3"], draw["pts"] // 3)
fp, dd, td = dk_points(draw["pts"], draw["reb"], draw["ast"], draw["stl"], draw["blk"], draw["tov"], draw["fg3"])
summarize("C = B + shared game factor + NB overdispersion", fp, dd, td, mins_b)

# D: a normal with the same mean and sd as C (what a multivariate-normal sim would use)
m, s = fp.mean(), fp.std()
fpn = rng.normal(m, s, N)
q = np.quantile(fpn, [0.01, 0.10, 0.50, 0.90, 0.99])
p(f"{'D normal matched to C mean and sd':<44} mean={m:5.1f} sd={s:4.1f} skew=+0.00 p01={q[0]:5.1f} p10={q[1]:5.1f} p50={q[2]:5.1f} p90={q[3]:5.1f} p99={q[4]:5.1f}")

stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
path = f"C:/Users/benja/Documents/Claude/nba-dfs/spikes/modeling/out/{stamp}_sim_shape_and_mc_error.txt"
with open(path, "w") as f:
    f.write(out.getvalue())
print(out.getvalue())
print("wrote", path)
