import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(0)
B = 2000
CODE = {"UP": 1, "DOWN": -1}

def load(path):
    if not os.path.exists(path):
        return None
    rows = {}
    for l in open(path):
        try:
            r = json.loads(l)
            rows[r["company"]["id"]] = r
        except Exception:
            pass
    return rows

def v(r, stage):
    return CODE.get(r["stages"][stage].get("verdict"), 0)

def ci(vals):
    return float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))

normal = load(os.path.join(HERE, "world_A3", "runs_t0.7.jsonl"))
arms = {"X (no cash information at all)": load(os.path.join(HERE, "world_A3_nocash", "runs_t0.7.jsonl")),
        "S (15-word summaries, no verdict labels)": load(os.path.join(HERE, "world_A3", "runs_t0.7_arm_S.jsonl"))}
if normal is None:
    sys.exit("normal run (world_A3/runs_t0.7.jsonl) not found")

def compare(name, arm):
    ids = sorted(set(normal) & set(arm))
    tr = [i for i in ids if normal[i]["company"]["is_trap"]]
    ct = [i for i in ids if normal[i]["company"]["is_control"]]
    print("\n== Arm %s | %d companies in common, %d traps, %d controls ==" % (name, len(ids), len(tr), len(ct)))
    if len(tr) < 10:
        print("too few traps"); return None
    out = {}
    for stage in ("trader_pre", "trader_final"):
        a = np.array([v(normal[i], stage) == -1 for i in tr], float)     # trap caught, normal run
        b = np.array([v(arm[i], stage) == -1 for i in tr], float)        # trap caught, bottleneck arm
        d = a - b
        lo, hi = ci([d[rng.integers(0, len(d), len(d))].mean() for _ in range(B)])
        ga = np.mean([v(normal[i], stage) == -1 for i in tr]) - np.mean([v(normal[i], stage) == -1 for i in ct])
        gb = np.mean([v(arm[i], stage) == -1 for i in tr]) - np.mean([v(arm[i], stage) == -1 for i in ct])
        print("%-13s trap caught: normal %3.0f%% | arm %3.0f%% | normal - arm = %+.1f pp (95%% CI %+.1f to %+.1f) | trap-minus-control gap: normal %+.1f pp, arm %+.1f pp" %
              (stage, 100 * a.mean(), 100 * b.mean(), 100 * d.mean(), 100 * lo, 100 * hi, 100 * ga, 100 * gb))
        out[stage] = (d.mean(), lo, hi)
    noise = abs(np.mean([(v(normal[i], "trader_final") == -1) - (v(normal[i], "trader_final_rerun") == -1) for i in tr]))
    dm, lo, hi = out["trader_final"]
    ok = dm >= 0.10 and lo > 0 and dm > noise
    print("rule on trader_final: (1) >= +10 pp: %s | (2) interval excludes 0 (lower %+.1f pp): %s | (3) larger than noise %.1f pp: %s -> %s" %
          (dm >= 0.10, 100 * lo, lo > 0, 100 * noise, dm > noise, "LOSS CAUSED" if ok else "no loss detected"))
    return ok

print("Bottleneck experiment (v3d): positive control for information loss. Fictional data, one model, one run per condition.")
res = {}
for name, arm in arms.items():
    if arm is None:
        print("\n== Arm %s: not run yet ==" % name); res[name] = None; continue
    res[name] = compare(name, arm)

xk = [k for k in res if k.startswith("X")][0]
sk = [k for k in res if k.startswith("S")][0]
print("\n== Reading the result (rules from PREREGISTRATION_v3d.md) ==")
if res[xk] is None:
    print("X not run or not scoreable: the instrument check is missing, so S is not interpreted.")
elif not res[xk]:
    print("X: the measurement did NOT detect even a complete removal of the cash information -> the instrument is not sensitive enough; the earlier B (no effect) from v3c is NOT reliable. S is not interpreted.")
else:
    print("X: the measurement detects a complete removal of the cash information -> the instrument is sensitive (to a drop of this size).")
    if res[sk] is None:
        print("S: not run yet.")
    else:
        print("S: " + ("the 15-word bottleneck caused a loss of trap warnings." if res[sk] else "no loss detected from the 15-word bottleneck (the pipeline kept the warning, or the loss is smaller than the instrument can see)."))
