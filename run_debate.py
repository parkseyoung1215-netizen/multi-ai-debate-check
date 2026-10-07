import json, os, sys, random
MOCK = os.environ.get("MOCK") == "1"
MODEL = "gpt-4o-mini"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
KEYS = ["revenue_growth_pct", "per", "debt_ratio_pct", "op_margin_pct", "price_change_3m_pct", "cash_months"]
if not MOCK:
    from openai import OpenAI
    client = OpenAI()
usage = {"in": 0, "out": 0}

FORMAT = ('Reply ONLY with JSON: {"text": "<your analysis, 3-5 sentences, in Korean>", '
          '"verdict": "BUY" or "HOLD" or "SELL" (your current leaning), '
          '"cited": [{"metric": "<one of: ' + ", ".join(KEYS) + '>", "value": <number>}]}. '
          'Every number you use in the text must also appear in "cited" with its metric name.')

def sheet(c):
    return "Fictional company fact sheet: " + c["name"] + "\n" + "\n".join(k + " = " + str(c[k]) for k in KEYS)

def call(system, user, c):
    if MOCK:
        cited = [{"metric": k, "value": c[k] if random.random() > 0.2 else round(c[k] + 5, 1)} for k in random.sample(KEYS, 3)]
        return {"text": "mock", "verdict": random.choice(["BUY", "HOLD", "SELL"]), "cited": cited}
    r = client.chat.completions.create(model=MODEL, temperature=0.7, response_format={"type": "json_object"},
                                       messages=[{"role": "system", "content": system + " " + FORMAT}, {"role": "user", "content": user}])
    usage["in"] += r.usage.prompt_tokens
    usage["out"] += r.usage.completion_tokens
    return json.loads(r.choices[0].message.content)

ROLES = {"value": "You are a value investor. You judge companies mainly by valuation and balance-sheet safety: per, debt_ratio_pct, cash_months.",
         "growth": "You are a growth investor. You judge companies mainly by revenue_growth_pct and op_margin_pct.",
         "momentum": "You are a momentum investor. You judge companies mainly by price_change_3m_pct."}

def show(label, o):
    return "[" + label + "] (" + o.get("verdict", "?") + ") " + o.get("text", "")

def run_company(c):
    st = {}
    st["solo"] = call("You are an investment analyst. Use only the numbers given.", sheet(c) + "\nDecide BUY, HOLD or SELL.", c)
    for role, prompt in ROLES.items():
        st["lens_" + role] = call(prompt + " Use only the numbers given.", sheet(c) + "\nDecide BUY, HOLD or SELL as this investor and explain.", c)
    reports = "\n".join(show(r, st["lens_" + r]) for r in ROLES)
    st["trader_pre"] = call("You are a trader. You see only the investor reports below, not the raw data. Decide BUY, HOLD or SELL.", "Investor reports:\n" + reports, c)
    debate = ""
    for rnd in (1, 2):
        for side, stance in (("bull", "optimistic: argue why to BUY"), ("bear", "pessimistic: rebut and argue why to SELL")):
            o = call("You are the " + side + " researcher, " + stance + ". You see only the text below, not the raw data.",
                     "Investor reports:\n" + reports + "\nDebate so far:\n" + debate, c)
            st["debate_r%d_%s" % (rnd, side)] = o
            debate += show("round %d %s" % (rnd, side), o) + "\n"
    st["trader_final"] = call("You are a trader. You see only the text below, not the raw data. Decide BUY, HOLD or SELL.",
                              "Investor reports:\n" + reports + "\nDebate:\n" + debate, c)
    return st

companies = json.load(open("results_v3/companies.json"))[:N]
with open("results_v3/debate_runs.jsonl", "w") as f:
    for c in companies:
        try:
            f.write(json.dumps({"company": c, "stages": run_company(c)}, ensure_ascii=False) + "\n")
            f.flush()
            print("done", c["id"], c["name"])
        except Exception as e:
            print("FAILED", c["id"], e)
cost = usage["in"] * 0.15 / 1e6 + usage["out"] * 0.60 / 1e6
print("tokens in/out:", usage["in"], usage["out"], "est cost USD: %.4f" % cost)
