import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# usage: python3 gen_a3.py pilot   (15 traps + 15 controls, seed 11)
#        python3 gen_a3.py main    (100 traps + 100 controls, seed 12)
MODE = sys.argv[1] if len(sys.argv) > 1 else "main"
if MODE == "pilot":
    SEED, K, DIR = 11, 15, "world_A3_pilot"
elif MODE == "main":
    SEED, K, DIR = 12, 100, "world_A3"
else:
    sys.exit("usage: gen_a3.py pilot|main")
rng = random.Random(SEED)

PRE = ["Kestrel", "Novalux", "Brightwater", "Orbitail", "Quillon", "Marrowdyne", "Fennick", "Zephyra", "Tallgrass", "Ironvale",
       "Pelagia", "Cobaltine", "Vireo", "Lumora", "Halcyon", "Strato", "Ember", "Nimbus", "Alder", "Prismatic",
       "Wexford", "Solenne", "Draymoor", "Fathom", "Glasswing", "Hollowpine", "Juniper", "Kitebright", "Lanternfly", "Mosswell",
       "Opaline", "Thistledown", "Umberfield", "Yarrow", "Zinnia"]
SUF = ["Labs", "Systems", "Works", "Grid", "Mills", "Forge", "Data", "Bio", "Row", "Arc", "Holdings", "Dynamics"]
RANGES = {"revenue_growth_pct": (-10, 60), "per": (5, 60), "debt_ratio_pct": (10, 250),
          "op_margin_pct": (-15, 35), "price_change_3m_pct": (-30, 50), "cash_months": (2, 48)}

def rnd(lo, hi):
    return round(rng.uniform(lo, hi), 1)

def make(cash_lo, cash_hi):
    c = {k: rnd(*v) for k, v in RANGES.items()}
    c["revenue_growth_pct"] = rnd(20, 60)   # looks good
    c["per"] = rnd(5, 20)                   # looks cheap
    c["cash_months"] = rnd(cash_lo, cash_hi)
    return c

# rule: cash_months < 12 -> DOWN, otherwise UP. Labels are exactly the rule (no noise).
rows = [(make(1, 6), True) for _ in range(K)] + [(make(24, 48), False) for _ in range(K)]
rng.shuffle(rows)
N = len(rows)
names = rng.sample([p + " " + s for p in PRE for s in SUF], N)
out = []
for i, (r, trap) in enumerate(rows):
    lab = "DOWN" if r["cash_months"] < 12 else "UP"
    c = {"id": i, "name": names[i]}
    c.update(r)
    c.update({"rule_label": lab, "label": lab, "flipped": False, "is_trap": trap, "is_control": not trap})
    out.append(c)

d = os.path.join(HERE, DIR)
os.makedirs(d, exist_ok=True)
json.dump(out, open(os.path.join(d, "companies.json"), "w"), ensure_ascii=False, indent=1)
print("world A3 (%s) seed %d -> saved %d companies to %s" % (MODE, SEED, N, os.path.join(d, "companies.json")))
print("traps (cash 1-6 months, label DOWN): %d | controls (cash 24-48 months, label UP): %d" % (sum(c["is_trap"] for c in out), sum(c["is_control"] for c in out)))
