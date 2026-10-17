# Post-hoc comparison (NOT pre-registered): one AI alone vs the multi-AI pipeline, World A3 (v3c data).
# Usage: python3 compare_solo.py   (run inside hidden_rule/)
import json, random
from collections import Counter

rows = [json.loads(l) for l in open("world_A3/runs_t0.7.jsonl")]

def correct(r, verdict):
    return int(verdict == r["company"]["label"])

def lens_majority(r):
    vs = [r["stages"][s]["verdict"] for s in ["lens_value", "lens_growth", "lens_momentum"]]
    return Counter(vs).most_common(1)[0][0]

METHODS = {
    "solo (one AI alone)": lambda r: r["stages"]["solo"]["verdict"],
    "majority of 3 lenses": lens_majority,
    "trader before debate": lambda r: r["stages"]["trader_pre"]["verdict"],
    "trader after debate": lambda r: r["stages"]["trader_final"]["verdict"],
}

def ci(diffs, n_boot=2000, seed=0):
    rnd = random.Random(seed)
    boots = sorted(sum(rnd.choice(diffs) for _ in diffs) / len(diffs) for _ in range(n_boot))
    return boots[int(0.025 * n_boot)], boots[int(0.975 * n_boot) - 1]

for name, subset in [("all 200", rows), ("100 traps", [r for r in rows if r["company"]["is_trap"]])]:
    print("==", name, "==")
    solo = [correct(r, METHODS["solo (one AI alone)"](r)) for r in subset]
    for m, f in METHODS.items():
        c = [correct(r, f(r)) for r in subset]
        line = "%-22s accuracy %3.0f%%" % (m, 100 * sum(c) / len(c))
        if not m.startswith("solo"):
            d = [a - b for a, b in zip(c, solo)]
            lo, hi = ci(d)
            line += "   vs solo %+5.1f pp (95%% CI %+.1f to %+.1f)" % (100 * sum(d) / len(d), 100 * lo, 100 * hi)
        print(line)
