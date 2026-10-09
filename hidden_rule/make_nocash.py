import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, "world_A3", "companies.json")
out_dir = os.path.join(HERE, "world_A3_nocash")
os.makedirs(out_dir, exist_ok=True)
cs = json.load(open(src))
for c in cs:
    c["cash_months_original"] = c["cash_months"]   # kept for the record; the pipeline only reads cash_months
    c["cash_months"] = 24.0                          # neutral value for every company
json.dump(cs, open(os.path.join(out_dir, "companies.json"), "w"), ensure_ascii=False, indent=1)
print("saved", len(cs), "companies to", os.path.join(out_dir, "companies.json"), "| cash_months set to 24.0 for all; traps:", sum(c["is_trap"] for c in cs), "controls:", sum(c["is_control"] for c in cs))
