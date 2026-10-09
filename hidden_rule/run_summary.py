import json, os, sys, random, time, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("n", nargs="?", type=int, default=200)
ap.add_argument("--temp", type=float, default=0.7)
ap.add_argument("--workers", type=int, default=4)
ap.add_argument("--world", default="world_A3", help="folder with the normal run (lens reports are reused from it)")
args = ap.parse_args()
MOCK = os.environ.get("MOCK") == "1"
MODEL = "gpt-4o-mini"
KEYS = ["revenue_growth_pct", "per", "debt_ratio_pct", "op_margin_pct", "price_change_3m_pct", "cash_months"]
if not MOCK:
    from openai import OpenAI
    client = OpenAI(max_retries=5)
usage = {"in": 0, "out": 0}
lock = threading.Lock()

FORMAT = ('Reply ONLY with JSON: {"text": "<your analysis, 3-5 sentences, in Korean>", '
          '"verdict": "UP" or "DOWN" (you must choose one, there is no neutral answer), '
          '"cited": [{"metric": "<one of: ' + ", ".join(KEYS) + '>", "value": <number>}]}. '
          'Every number you use in the text must also appear in "cited" with its metric name.')

def raw_call(system, user):
    if MOCK:
        return {"text": "mock", "summary": "mock", "verdict": random.choice(["UP", "DOWN"]), "cited": []}
    last = None
    for attempt in range(3):
        try:
            r = client.chat.completions.create(model=MODEL, temperature=args.temp, response_format={"type": "json_object"},
                                               messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
            with lock:
                usage["in"] += r.usage.prompt_tokens
                usage["out"] += r.usage.completion_tokens
            return json.loads(r.choices[0].message.content)
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise last

def call(system, user):
    return raw_call(system + " " + FORMAT, user)

def summarize(text):
    o = raw_call("You compress investor reports.",
                 'Compress the report below to at most 15 words. Keep only what matters most. Reply ONLY with JSON: {"summary": "<at most 15 words, in Korean>"}.\n' + text)
    return str(o.get("summary", ""))

ROLES = ["value", "growth", "momentum"]

def show(label, o):
    return "[" + label + "] (" + o.get("verdict", "?") + ") " + o.get("text", "")

def run_company(src):
    c, lens = src["company"], src["stages"]
    st = {}
    summ = {}
    for r in ROLES:
        summ[r] = summarize(lens["lens_" + r].get("text", ""))
        st["summary_" + r] = {"summary": summ[r]}
    reports = "\n".join("[" + r + "] " + summ[r] for r in ROLES)          # no verdict labels in this arm
    st["trader_pre"] = call("You are a trader. You see only the investor reports below, not the raw data. Decide UP or DOWN: will the stock rise over the next 12 months?",
                            "Investor reports:\n" + reports)
    debate = ""
    for rnd in (1, 2):
        for side, stance in (("bull", "optimistic: argue why the stock will go UP"), ("bear", "pessimistic: rebut and argue why the stock will go DOWN")):
            o = call("You are the " + side + " researcher, " + stance + ". You see only the text below, not the raw data.",
                     "Investor reports:\n" + reports + "\nDebate so far:\n" + debate)
            st["debate_r%d_%s" % (rnd, side)] = o
            debate += show("round %d %s" % (rnd, side), o) + "\n"
    final_sys = "You are a trader. You see only the text below, not the raw data. Decide UP or DOWN: will the stock rise over the next 12 months?"
    final_user = "Investor reports:\n" + reports + "\nDebate:\n" + debate
    st["trader_final"] = call(final_sys, final_user)
    st["trader_final_rerun"] = call(final_sys, final_user)
    return c, st

wdir = os.path.join(HERE, args.world)
src_path = os.path.join(wdir, "runs_t%g.jsonl" % args.temp)
sources = sorted((json.loads(l) for l in open(src_path)), key=lambda r: r["company"]["id"])[:args.n]
out_path = os.path.join(wdir, "runs_t%g_arm_S.jsonl" % args.temp)
done = set()
if os.path.exists(out_path):
    for line in open(out_path):
        try:
            done.add(json.loads(line)["company"]["id"])
        except Exception:
            pass
todo = [s for s in sources if s["company"]["id"] not in done]
print("arm S (15-word summaries, no verdict labels) |", args.world, "| temp", args.temp, "| already done:", len(done), "| to run:", len(todo), "| mock:", MOCK)

t0 = time.time()
n_ok = 0
with open(out_path, "a") as f, ThreadPoolExecutor(max_workers=args.workers) as ex:
    futs = [ex.submit(run_company, s) for s in todo]
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
