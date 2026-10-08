import json, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 10
N = 200
NOISE = 0.10
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

def make_random():
    return {k: rnd(*v) for k, v in RANGES.items()}

def make_trap():
    c = make_random()
    c["revenue_growth_pct"] = rnd(20, 60)
    c["per"] = rnd(5, 20)
    c["cash_months"] = rnd(2, 12)
    return c

def make_control():
    c = make_random()
    c["revenue_growth_pct"] = rnd(20, 60)
    c["per"] = rnd(5, 20)
    c["cash_months"] = rnd(12, 48)
    return c

def attractive(c):
    return c["revenue_growth_pct"] > 20 and c["per"] < 20

def rule_label(c):
    if c["cash_months"] < 12:
        return "DOWN"
    return "UP" if c["revenue_growth_pct"] > 15 else "DOWN"

rows = [make_trap() for _ in range(60)] + [make_control() for _ in range(60)] + [make_random() for _ in range(80)]
rng.shuffle(rows)
names = rng.sample([p + " " + s for p in PRE for s in SUF], N)
flip = set(rng.sample(range(N), round(NOISE * N)))
out = []
for i, r in enumerate(rows):
    rl = rule_label(r)
    lab = ("DOWN" if rl == "UP" else "UP") if i in flip else rl
    c = {"id": i, "name": names[i]}
    c.update(r)
    c.update({"rule_label": rl, "label": lab, "flipped": i in flip,
              "is_trap": attractive(r) and r["cash_months"] < 12,
              "is_control": attractive(r) and r["cash_months"] >= 12})
    out.append(c)

d = os.path.join(HERE, "world_A2")
os.makedirs(d, exist_ok=True)
json.dump(out, open(os.path.join(d, "companies.json"), "w"), ensure_ascii=False, indent=1)
up = sum(c["label"] == "UP" for c in out)
print("world A2 seed", SEED, "-> saved", len(out), "companies to", os.path.join(d, "companies.json"))
print("label UP: %d (%.0f%%), DOWN: %d, flipped by noise: %d" % (up, 100 * up / N, N - up, len(flip)))
print("traps:", sum(c["is_trap"] for c in out), "| controls:", sum(c["is_control"] for c in out))
