import json, os, sys, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--temp", type=float, default=0.7)
ap.add_argument("--world", default="world_A2", help="folder with the runs")
ap.add_argument("--two-sided", action="store_true", help="v3c rule: also detect a DROP in trap catching")
ap.add_argument("--pilot", action="store_true", help="v3c pilot gate only")
ap.add_argument("--compare-strict", action="store_true", help="compare strict-lens run with the shared run")
args = ap.parse_args()
wdir = os.path.join(HERE, args.world)
STAGES = ["solo", "lens_value", "lens_growth", "lens_momentum", "trader_pre", "trader_final", "trader_final_rerun"]
CODE = {"UP": 1, "DOWN": -1}
rng = np.random.default_rng(0)
B = 2000

def load(suffix=""):
    p = os.path.join(wdir, "runs_t%g%s.jsonl" % (args.temp, suffix))
    return sorted((json.loads(l) for l in open(p)), key=lambda r: r["company"]["id"])

def ci_of(vals):
    vals = np.array(vals, float)
    return float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))

def boot(fn, size):
    return ci_of([fn(rng.integers(0, size, size)) for _ in range(B)])

def arrays(runs):
    P = {s: np.array([CODE.get(r["stages"][s].get("verdict"), 0) for r in runs]) for s in STAGES}
    L = np.array([1 if r["company"]["label"] == "UP" else -1 for r in runs])
    TRAP = np.array([bool(r["company"]["is_trap"]) for r in runs])
    CTRL = np.array([bool(r["company"]["is_control"]) for r in runs])
    return P, L, TRAP, CTRL

if args.compare_strict:
    rs, rn = load(), load("_strict")
    ids = sorted(set(r["company"]["id"] for r in rs) & set(r["company"]["id"] for r in rn))
    rs = [r for r in rs if r["company"]["id"] in ids]
    rn = [r for r in rn if r["company"]["id"] in ids]
    Ps, _, TRAPs, _ = arrays(rs)
    Pn, _, _, _ = arrays(rn)
    t = np.where(TRAPs)[0]
    a = (Ps["trader_pre"][t] == -1).astype(float)
    b = (Pn["trader_pre"][t] == -1).astype(float)
    d = b - a
    lo, hi = boot(lambda idx: d[idx].mean(), len(t))
    print("== Strict lenses vs shared sheet: trap caught (DOWN) at trader_pre, %d traps ==" % len(t))
    print("shared %.0f%% | strict %.0f%% | strict - shared = %+.1f pp (95%% CI %+.1f to %+.1f)" % (100 * a.mean(), 100 * b.mean(), 100 * d.mean(), 100 * lo, 100 * hi))
    ok = d.mean() <= -0.10 and hi < 0
    print("=> RESULT:", "information loss from the restriction found (lower by >= 10 pp, interval below 0)" if ok else "no information loss detected by the pre-registered rule")
    sys.exit(0)

runs = load()
n = len(runs)
P, L, TRAP, CTRL = arrays(runs)
tr, ct = np.where(TRAP)[0], np.where(CTRL)[0]
print(args.world, "| forced choice | temp %g | companies: %d | traps: %d | controls: %d | UP share: %.0f%%" % (args.temp, n, len(tr), len(ct), 100 * (L == 1).mean()))
print("always predicting the majority label would be right %.0f%% of the time (context, not a result)" % (100 * max((L == 1).mean(), (L == -1).mean())))
if len(tr) < 5 or len(ct) < 5:
    sys.exit("Too few traps or controls in this run to score. Run more companies.")
missing = {s: int((P[s] == 0).sum()) for s in STAGES}
if any(missing.values()):
    print("missing/invalid verdicts:", missing)

if args.pilot:
    print("\n== PILOT GATE (v3c): does the value lens use the cash signal? ==")
    for st in ["solo", "lens_value"]:
        a = (P[st][tr] == -1).mean(); b = (P[st][ct] == -1).mean()
        print("%-12s traps DOWN %3.0f%% | controls DOWN %3.0f%% | difference %+.1f pp" % (st, 100 * a, 100 * b, 100 * (a - b)))
    diff = (P["lens_value"][tr] == -1).mean() - (P["lens_value"][ct] == -1).mean()
    go = diff >= 0.25
    print("Gate (lens_value difference >= +25 pp, point estimate only): %s" % ("GO - run the main experiment" if go else "STOP - do not run the main experiment"))
    print("(Pilot data are not used in the main analysis. 15 + 15 companies is too small for any other conclusion.)")
    sys.exit(0)

print("\n== Accuracy per stage (no HOLD, so every company counts) ==")
for s in STAGES:
    c = (P[s] == L).astype(float)
    lo, hi = boot(lambda idx, c=c: c[idx].mean(), n)
    print("%-20s UP %3d / DOWN %3d | accuracy %3.0f%% (95%% CI %.0f-%.0f%%)" % (s, (P[s] == 1).sum(), (P[s] == -1).sum(), 100 * c.mean(), 100 * lo, 100 * hi))

print("\n== Check 1: was the cash signal used? DOWN share on traps minus on controls ==")
def check(stage):
    a = (P[stage][tr] == -1).astype(float)
    b = (P[stage][ct] == -1).astype(float)
    diff = a.mean() - b.mean()
    vals = [a[rng.integers(0, len(a), len(a))].mean() - b[rng.integers(0, len(b), len(b))].mean() for _ in range(B)]
    lo, hi = ci_of(vals)
    return a.mean(), b.mean(), diff, lo, hi
for s in STAGES:
    a, b, diff, lo, hi = check(s)
    print("%-20s traps DOWN %3.0f%% | controls DOWN %3.0f%% | difference %+.1f pp (95%% CI %+.1f to %+.1f)" % (s, 100 * a, 100 * b, 100 * diff, 100 * lo, 100 * hi))
a, b, diff, lo, hi = check("lens_value")
passed = diff >= 0.20 and lo > 0
print("Check 1 (lens_value, needs >= +20 pp and interval above 0): %s" % ("PASSED" if passed else "NOT PASSED"))
if not passed:
    print("-> The world did not test information loss. The primary outcome below is for reference only and is NOT interpreted.")

print("\n== Primary: trap caught = share of traps with verdict DOWN, trader_final vs trader_pre (n=%d traps) ==" % len(tr))
caught = {s: (P[s][tr] == -1).astype(float) for s in STAGES}
for s in STAGES:
    lo, hi = boot(lambda idx, s=s: caught[s][idx].mean(), len(tr))
    print("%-20s %3.0f%% (95%% CI %.0f-%.0f%%)" % (s, 100 * caught[s].mean(), 100 * lo, 100 * hi))
d = caught["trader_final"] - caught["trader_pre"]
lo, hi = boot(lambda idx: d[idx].mean(), len(tr))
noise = (caught["trader_final"] - caught["trader_final_rerun"]).mean()
d2 = caught["trader_final_rerun"] - caught["trader_pre"]
lo2, hi2 = boot(lambda idx: d2[idx].mean(), len(tr))
print("\ntrader_final - trader_pre : %+.1f pp (95%% CI %+.1f to %+.1f)" % (100 * d.mean(), 100 * lo, 100 * hi))
print("rerun - trader_pre (replication): %+.1f pp (95%% CI %+.1f to %+.1f)" % (100 * d2.mean(), 100 * lo2, 100 * hi2))
print("trader_final - rerun (noise from sampling alone): %+.1f pp" % (100 * noise))
ok1, ok2, ok3 = d.mean() >= 0.10, lo > 0, d.mean() > abs(noise)
print("effect rule (improvement): (1) >= +10 pp: %s | (2) interval excludes 0 (lower %+.1f pp): %s | (3) larger than noise %.1f pp: %s" % (ok1, 100 * lo, ok2, 100 * abs(noise), ok3))
pre = caught["trader_pre"].mean()
if args.two_sided:
    dn1, dn2, dn3 = d.mean() <= -0.10, hi < 0, -d.mean() > abs(noise)
    print("effect rule (drop):        (1) <= -10 pp: %s | (2) interval excludes 0 (upper %+.1f pp): %s | (3) larger than noise: %s" % (dn1, 100 * hi, dn2, dn3))
    if ok1 and ok2 and ok3:
        verdict = "no room to improve (trader_pre already catches >= 85% of traps)" if pre >= 0.85 else "IMPROVEMENT found (final catches more traps than first trader)"
    elif dn1 and dn2 and dn3:
        verdict = "no room to fall (trader_pre catches <= 15% of traps)" if pre <= 0.15 else "INFORMATION LOSS found (final catches fewer traps than first trader)"
    else:
        verdict = "no effect detected (by the pre-registered rule)"
else:
    if pre >= 0.85:
        verdict = "no room to improve (trader_pre already catches >= 85% of traps)"
    else:
        verdict = "effect found" if (ok1 and ok2 and ok3) else "no effect detected (by the pre-registered rule)"
print("=> RESULT:", verdict, "" if passed else "[NOT interpreted: Check 1 not passed]")

print("\n== Secondary ==")
acc = lambda s: (P[s] == L).astype(float)
da = acc("trader_final") - acc("solo")
lo, hi = boot(lambda idx: da[idx].mean(), n)
print("accuracy trader_final - solo: %+.1f pp (95%% CI %+.1f to %+.1f)" % (100 * da.mean(), 100 * lo, 100 * hi))
a = (P["lens_value"][tr] == -1)
print("lost at the trader : lens_value DOWN but trader_pre UP on %d of %d traps" % (((P["trader_pre"][tr] == 1) & a).sum(), a.sum()))
b = (P["trader_pre"][tr] == -1)
print("lost in the debate : trader_pre DOWN but trader_final UP on %d of %d traps (rerun: %d)" % (((P["trader_final"][tr] == 1) & b).sum(), b.sum(), ((P["trader_final_rerun"][tr] == 1) & b).sum()))
print("\n(Fictional data with a rule I wrote. One model, one run per condition. Not evidence about real markets.)")
