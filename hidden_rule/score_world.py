import json, os, sys, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("world")
ap.add_argument("--temp", type=float, default=0.7)
args = ap.parse_args()
WORLD = args.world.upper()
path = os.path.join(HERE, "world_" + WORLD, "runs_t%g.jsonl" % args.temp)
runs = sorted((json.loads(l) for l in open(path)), key=lambda r: r["company"]["id"])
n = len(runs)
rng = np.random.default_rng(0)
B = 2000
STAGES = ["solo", "lens_value", "lens_growth", "lens_momentum", "trader_pre", "trader_final", "trader_final_rerun"]
CODE = {"BUY": 1, "SELL": -1}
P = {s: np.array([CODE.get(r["stages"][s].get("verdict"), 0) for r in runs]) for s in STAGES}
L = np.array([1 if r["company"]["label"] == "UP" else -1 for r in runs])
TRAP = np.array([bool(r["company"].get("is_trap")) for r in runs])
print("world %s | temp %g | companies: %d | UP share: %.0f%%" % (WORLD, args.temp, n, 100 * (L == 1).mean()))
print("always predicting the majority label would be right %.0f%% of the time (context, not a result)" % (100 * max((L == 1).mean(), (L == -1).mean())))

def acc(idx, s):
    p, l = P[s][idx], L[idx]
    m = p != 0
    return float((p[m] == l[m]).mean()) if m.any() else float("nan")

def boot(fn, size):
    vals = []
    for _ in range(B):
        idx = rng.integers(0, size, size)
        vals.append(fn(idx))
    vals = np.array(vals, float)
    return float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))

if n < 5:
    sys.exit("Only %d companies in this run, too few to score." % n)
print("\n== Verdicts, coverage and accuracy among calls (BUY=UP, SELL=DOWN, HOLD=no call) ==")
allidx = np.arange(n)
for s in STAGES:
    p = P[s]
    lo, hi = boot(lambda idx, s=s: acc(idx, s), n)
    print("%-20s BUY %3d / HOLD %3d / SELL %3d | coverage %3.0f%% | accuracy among calls %3.0f%% (95%% CI %.0f-%.0f%%, calls=%d)" % (
        s, (p == 1).sum(), (p == 0).sum(), (p == -1).sum(), 100 * (p != 0).mean(), 100 * acc(allidx, s), 100 * lo, 100 * hi, (p != 0).sum()))

def decide(name, diff, lo, noise, thr):
    ok1, ok2, ok3 = diff >= thr, lo > 0, diff > abs(noise)
    print("effect rule: (1) difference >= %+.0f pp: %s | (2) 95%% CI excludes 0 (lower bound %+.1f pp): %s | (3) larger than noise |final - rerun| = %.1f pp: %s" % (
        100 * thr, ok1, 100 * lo, ok2, 100 * abs(noise), ok3))
    print("=> RESULT:", "effect found" if (ok1 and ok2 and ok3) else "no effect detected (by the pre-registered rule)")

if WORLD == "A":
    t = np.where(TRAP)[0]
    m = len(t)
    if m < 5:
        print("\nOnly %d trap companies in this run, too few to score. Run more companies (the full run has about 66)." % m)
        sys.exit(0)
    print("\n== World A primary: trap companies (n=%d): share where the verdict is NOT BUY ('trap caught') ==" % m)
    caught = {s: (P[s][t] != 1).astype(float) for s in STAGES}
    for s in STAGES:
        lo, hi = boot(lambda idx, s=s: caught[s][idx].mean(), m)
        print("%-20s %3.0f%% (95%% CI %.0f-%.0f%%)" % (s, 100 * caught[s].mean(), 100 * lo, 100 * hi))
    d = caught["trader_final"] - caught["trader_pre"]
    lo, hi = boot(lambda idx: d[idx].mean(), m)
    noise = (caught["trader_final"] - caught["trader_final_rerun"]).mean()
    print("\ntrader_final - trader_pre : %+.1f pp (95%% CI %+.1f to %+.1f)" % (100 * d.mean(), 100 * lo, 100 * hi))
    d2 = caught["trader_final_rerun"] - caught["trader_pre"]
    lo2, hi2 = boot(lambda idx: d2[idx].mean(), m)
    print("rerun - trader_pre (replication of the debate effect): %+.1f pp (95%% CI %+.1f to %+.1f)" % (100 * d2.mean(), 100 * lo2, 100 * hi2))
    print("trader_final - rerun (noise from sampling alone): %+.1f pp" % (100 * noise))
    decide("A", d.mean(), lo, noise, 0.15)
    print("\n== Where does the warning get lost? (trap companies) ==")
    for lens in ("lens_value", "lens_growth", "lens_momentum"):
        print("%-14s not BUY on %d of %d traps" % (lens, (P[lens][t] != 1).sum(), m))
    a = (P["lens_value"][t] != 1)
    print("lost at the trader : lens_value warned (not BUY) but trader_pre = BUY on %d of %d" % (((P["trader_pre"][t] == 1) & a).sum(), a.sum()))
    b = (P["trader_pre"][t] != 1)
    print("lost in the debate : trader_pre not BUY but trader_final = BUY on %d of %d (rerun: %d)" % (
        ((P["trader_final"][t] == 1) & b).sum(), b.sum(), ((P["trader_final_rerun"][t] == 1) & b).sum()))
else:
    print("\n== World %s primary: accuracy among calls, trader_final vs solo ==" % WORLD)
    def dfn(idx, a="trader_final", b="solo"):
        return acc(idx, a) - acc(idx, b)
    d = dfn(allidx)
    lo, hi = boot(dfn, n)
    noise = acc(allidx, "trader_final") - acc(allidx, "trader_final_rerun")
    print("trader_final - solo : %+.1f pp (95%% CI %+.1f to %+.1f)" % (100 * d, 100 * lo, 100 * hi))
    print("trader_final - rerun (noise from sampling alone): %+.1f pp" % (100 * noise))
    decide(WORLD, d, lo, noise, 0.10)
print("\n(Fictional data with a rule I wrote. One model, one run per condition. Not evidence about real markets.)")
