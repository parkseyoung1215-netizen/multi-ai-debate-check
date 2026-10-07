import json, numpy as np
KEYS = ["revenue_growth_pct", "per", "debt_ratio_pct", "op_margin_pct", "price_change_3m_pct", "cash_months"]
runs = [json.loads(l) for l in open("results_v3/debate_runs.jsonl")]
rng = np.random.default_rng(0)
def ci(vals):
    v = np.array(vals, float)
    if len(v) == 0: return "n/a"
    b = [rng.choice(v, len(v)).mean() for _ in range(2000)]
    return "%.0f%% (95%% CI %.0f-%.0f%%, n=%d)" % (100*v.mean(), 100*np.percentile(b, 2.5), 100*np.percentile(b, 97.5), len(v))
stages = list(runs[0]["stages"].keys())
print("== Number check: share of cited numbers that do NOT match the fact sheet ==")
for s in stages:
    bad = []
    for r in runs:
        c = r["company"]
        for x in r["stages"][s].get("cited", []):
            m, v = x.get("metric"), x.get("value")
            ok = m in KEYS and isinstance(v, (int, float)) and abs(v - c[m]) <= 0.051
            bad.append(0 if ok else 1)
    print("%-20s %s" % (s, ci(bad)))
print("\n== Verdict counts per stage ==")
for s in stages:
    vs = [r["stages"][s].get("verdict") for r in runs]
    print("%-20s BUY %d / HOLD %d / SELL %d" % (s, vs.count("BUY"), vs.count("HOLD"), vs.count("SELL")))
def agree(a, b):
    return [int(r["stages"][a].get("verdict") == r["stages"][b].get("verdict")) for r in runs]
print("\n== Did the debate change the decision? ==")
print("trader_pre == trader_final :", ci(agree("trader_pre", "trader_final")))
print("solo == trader_final       :", ci(agree("solo", "trader_final")))
print("solo == trader_pre         :", ci(agree("solo", "trader_pre")))

print("\n== Lens direction check: correlation between verdict (BUY=1, HOLD=0, SELL=-1) and each metric across companies ==")
score = {"BUY": 1, "HOLD": 0, "SELL": -1}
def corr(stage, key, sign):
    x = [sign * r["company"][key] for r in runs]
    y = [score.get(r["stages"][stage].get("verdict"), 0) for r in runs]
    if len(set(y)) < 2: return "n/a (all same verdict)"
    return "%.2f" % np.corrcoef(x, y)[0, 1]
expected = [("lens_value", "per", -1, "low PER -> more BUY"), ("lens_value", "debt_ratio_pct", -1, "low debt -> more BUY"),
            ("lens_growth", "revenue_growth_pct", 1, "high growth -> more BUY"), ("lens_growth", "op_margin_pct", 1, "high margin -> more BUY"),
            ("lens_momentum", "price_change_3m_pct", 1, "high 3m return -> more BUY"),
            ("solo", "per", -1, "control: low PER"), ("solo", "price_change_3m_pct", 1, "control: high 3m return")]
for stage, key, sign, note in expected:
    print("%-14s %-22s %-6s (%s)" % (stage, key, corr(stage, key, sign), note))
print("(positive = verdict moves in the direction the lens predicts. With few companies this is noisy.)")
