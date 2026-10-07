import json, os
HOME = os.path.expanduser('~')
MOCK = os.environ.get("MOCK") == "1"
MODEL = "gpt-4o-mini"
KEYS = ["revenue_growth_pct", "per", "debt_ratio_pct", "op_margin_pct", "price_change_3m_pct", "cash_months"]
if not MOCK:
    from openai import OpenAI
    client = OpenAI()
usage = {"in": 0, "out": 0}
FORMAT = ('Reply ONLY with JSON: {"text": "<your analysis, 3-5 sentences, in Korean>", '
          '"verdict": "BUY" or "HOLD" or "SELL" (your current leaning), '
          '"cited": [{"metric": "<one of: ' + ", ".join(KEYS) + '>", "value": <number>}]}. '
          'Every number you use in the text must also appear in "cited" with its metric name.')
def call(system, user, c):
    if MOCK:
        import random
        return {"text": "mock", "verdict": random.choice(["BUY", "HOLD", "SELL"]), "cited": [{"metric": "per", "value": c["per"]}]}
    r = client.chat.completions.create(model=MODEL, temperature=0.7, response_format={"type": "json_object"},
                                       messages=[{"role": "system", "content": system + " " + FORMAT}, {"role": "user", "content": user}])
    usage["in"] += r.usage.prompt_tokens
    usage["out"] += r.usage.completion_tokens
    return json.loads(r.choices[0].message.content)
def show(label, o):
    return "[" + label + "] (" + o.get("verdict", "?") + ") " + o.get("text", "")
ROLES = ["value", "growth", "momentum"]
TRADER = "You are a trader. You see only the text below, not the raw data. Decide BUY, HOLD or SELL."
RULE = (" Rules for this round: (1) directly rebut one specific claim the opponent made earlier, quoting a few of their words; "
        "(2) add one new supporting point you have NOT made in your earlier messages; do not repeat earlier sentences.")

runs = [json.loads(l) for l in open(HOME + '/results_v3/debate_runs.jsonl')]
os.makedirs(HOME + '/v2/results_v3', exist_ok=True)
with open(HOME + '/v2/results_v3/debate_runs.jsonl', 'w') as out:
    for r in runs:
        c = r['company']; st = dict(r['stages'])
        try:
            reports = "\n".join(show(x, st['lens_' + x]) for x in ROLES)
            d1 = show("round 1 bull", st['debate_r1_bull']) + "\n" + show("round 1 bear", st['debate_r1_bear']) + "\n"
            old_debate = d1 + show("round 2 bull", st['debate_r2_bull']) + "\n" + show("round 2 bear", st['debate_r2_bear']) + "\n"
            st['trader_final_rerun_v1debate'] = call(TRADER, "Investor reports:\n" + reports + "\nDebate:\n" + old_debate, c)
            debate = d1
            for side, stance in (("bull", "optimistic: argue why to BUY"), ("bear", "pessimistic: rebut and argue why to SELL")):
                o = call("You are the " + side + " researcher, " + stance + ". You see only the text below, not the raw data." + RULE,
                         "Investor reports:\n" + reports + "\nDebate so far:\n" + debate, c)
                st['debate_r2_' + side] = o
                debate += show("round 2 " + side, o) + "\n"
            st['trader_final'] = call(TRADER, "Investor reports:\n" + reports + "\nDebate:\n" + debate, c)
            out.write(json.dumps({"company": c, "stages": st}, ensure_ascii=False) + "\n")
            out.flush()
            print("done", c["id"], c["name"])
        except Exception as e:
            print("FAILED", c["id"], e)
print("tokens in/out:", usage["in"], usage["out"], "est cost USD: %.4f" % (usage["in"] * 0.15 / 1e6 + usage["out"] * 0.60 / 1e6))
