import json, os, sys, random, time, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("world")
ap.add_argument("n", nargs="?", type=int, default=200)
ap.add_argument("--temp", type=float, default=0.7)
ap.add_argument("--workers", type=int, default=4)
args = ap.parse_args()
WORLD = args.world.upper()
MOCK = os.environ.get("MOCK") == "1"
MODEL = "gpt-4o-mini"
KEYS = ["revenue_growth_pct", "per", "debt_ratio_pct", "op_margin_pct", "price_change_3m_pct", "cash_months"]
if not MOCK:
    from openai import OpenAI
    client = OpenAI(max_retries=5)
usage = {"in": 0, "out": 0}
lock = threading.Lock()

FORMAT = ('Reply ONLY with JSON: {"text": "<your analysis, 3-5 sentences, in Korean>", '
          '"verdict": "BUY" or "HOLD" or "SELL" (your current leaning), '
          '"cited": [{"metric": "<one of: ' + ", ".join(KEYS) + '>", "value": <number>}]}. '
          'Every number you use in the text must also appear in "cited" with its metric name.')

def sheet(c):
    return "Fictional company fact sheet: " + c["name"] + "\n" + "\n".join(k + " = " + str(c[k]) for k in KEYS)

def call(system, user, c):
    if MOCK:
        return {"text": "mock", "verdict": random.choice(["BUY", "HOLD", "SELL"]), "cited": []}
    last = None
    for attempt in range(3):
        try:
            r = client.chat.completions.create(model=MODEL, temperature=args.temp, response_format={"type": "json_object"},
                                               messages=[{"role": "system", "content": system + " " + FORMAT}, {"role": "user", "content": user}])
            with lock:
                usage["in"] += r.usage.prompt_tokens
                usage["out"] += r.usage.completion_tokens
            return json.loads(r.choices[0].message.content)
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise last

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
    final_sys = "You are a trader. You see only the text below, not the raw data. Decide BUY, HOLD or SELL."
    final_user = "Investor reports:\n" + reports + "\nDebate:\n" + debate
    st["trader_final"] = call(final_sys, final_user, c)
    st["trader_final_rerun"] = call(final_sys, final_user, c)
    return st

wdir = os.path.join(HERE, "world_" + WORLD)
companies = json.load(open(os.path.join(wdir, "companies.json")))[:args.n]
out_path = os.path.join(wdir, "runs_t%g.jsonl" % args.temp)
done = set()
if os.path.exists(out_path):
    for line in open(out_path):
        try:
            done.add(json.loads(line)["company"]["id"])
        except Exception:
            pass
todo = [c for c in companies if c["id"] not in done]
print("world", WORLD, "| temp", args.temp, "| already done:", len(done), "| to run:", len(todo), "| mock:", MOCK)

def work(c):
    return c, run_company(c)

t0 = time.time()
n_ok = 0
with open(out_path, "a") as f, ThreadPoolExecutor(max_workers=args.workers) as ex:
    futs = [ex.submit(work, c) for c in todo]
    for fu in as_completed(futs):
        try:
            c, st = fu.result()
            f.write(json.dumps({"company": c, "stages": st}, ensure_ascii=False) + "\n")
            f.flush()
            n_ok += 1
            if n_ok % 5 == 0 or n_ok == len(todo):
                print("done %d/%d (%.0f s)" % (n_ok, len(todo), time.time() - t0))
        except Exception as e:
            print("FAILED a company:", e)
cost = usage["in"] * 0.15 / 1e6 + usage["out"] * 0.60 / 1e6
print("finished. tokens in/out:", usage["in"], usage["out"], "est cost USD: %.4f" % cost)
print("saved to", out_path, "(run again with the same command to fill in any FAILED companies)")
