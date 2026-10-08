import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = sys.argv[1].upper() if len(sys.argv) > 1 else "A"
SEEDS = {"A": 7, "C": 8, "B": 9}
if WORLD not in SEEDS:
    sys.exit("usage: python3 gen_world.py A|B|C")
N = 200
NOISE = 0.10
rng = random.Random(SEEDS[WORLD])

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

def is_trap(c):
    return c["revenue_growth_pct"] > 20 and c["per"] < 20 and c["cash_months"] < 12

if WORLD == "A":
    rows = [make_trap() for _ in range(60)] + [make_random() for _ in range(N - 60)]
else:
    rows = [make_random() for _ in range(N)]
rng.shuffle(rows)

def rule_label(c, z=None):
    if WORLD == "A":
        if c["cash_months"] < 12:
            return "DOWN"
        return "UP" if c["revenue_growth_pct"] > 15 else "DOWN"
    if WORLD == "B":
        return "UP" if (c["op_margin_pct"] > 10 and c["debt_ratio_pct"] < 100) else "DOWN"
    score = 0.4 * z["revenue_growth_pct"] - 0.3 * z["per"] + 0.3 * z["price_change_3m_pct"]
    return "UP" if score > 0 else "DOWN"

stats = {}
for k in ("revenue_growth_pct", "per", "price_change_3m_pct"):
    vals = [r[k] for r in rows]
    m = sum(vals) / len(vals)
    sd = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5
    stats[k] = (m, sd)

names = rng.sample([p + " " + s for p in PRE for s in SUF], N)
flip = set(rng.sample(range(N), round(NOISE * N)))
out = []
for i, r in enumerate(rows):
    z = {k: (r[k] - stats[k][0]) / stats[k][1] for k in stats}
    rl = rule_label(r, z)
    lab = ("DOWN" if rl == "UP" else "UP") if i in flip else rl
    c = {"id": i, "name": names[i]}
    c.update(r)
    c.update({"rule_label": rl, "label": lab, "flipped": i in flip, "is_trap": is_trap(r) if WORLD == "A" else False})
    out.append(c)

d = os.path.join(HERE, "world_" + WORLD)
os.makedirs(d, exist_ok=True)
json.dump(out, open(os.path.join(d, "companies.json"), "w"), ensure_ascii=False, indent=1)
up = sum(c["label"] == "UP" for c in out)
print("world", WORLD, "seed", SEEDS[WORLD], "-> saved", len(out), "companies to", os.path.join(d, "companies.json"))
print("label UP: %d (%.0f%%), DOWN: %d, flipped by noise: %d" % (up, 100 * up / N, N - up, len(flip)))
if WORLD == "A":
    print("trap companies:", sum(c["is_trap"] for c in out))
