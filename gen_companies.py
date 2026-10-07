import json, random, os
random.seed(42)
NAMES = ["Kestrel Labs","Novalux","Brightwater","Orbitail","Quillon","Marrowdyne","Fennick","Zephyra","Tallgrass","Ironvale",
         "Pelagia","Cobaltine","Vireo Systems","Lumora","Halcyon Grid","Strato Mills","Ember Row","Nimbus Forge","Aldercress","Prismatic",
         "Wexford Bio","Solenne","Draymoor","Fathom Data","Glasswing","Hollowpine","Juniper Arc","Kitebright","Lanternfly","Mosswell"]
def make(i):
    return {"id": i, "name": NAMES[i],
            "revenue_growth_pct": round(random.uniform(-10, 60), 1),
            "per": round(random.uniform(5, 60), 1),
            "debt_ratio_pct": round(random.uniform(10, 250), 1),
            "op_margin_pct": round(random.uniform(-15, 35), 1),
            "price_change_3m_pct": round(random.uniform(-30, 50), 1),
            "cash_months": round(random.uniform(2, 48), 1)}
os.makedirs("results_v3", exist_ok=True)
json.dump([make(i) for i in range(30)], open("results_v3/companies.json", "w"), ensure_ascii=False, indent=1)
print("saved 30 fictional companies -> results_v3/companies.json")
