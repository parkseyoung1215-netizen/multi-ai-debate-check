import json, re
runs = [json.loads(l) for l in open('results_v3/debate_runs.jsonl')]
Q = r'["“”‘’\'「」『』]'
pat = re.compile(Q + r'([^"“”‘’\'「」『』]{4,}?)' + Q)
def norm(s):
    return re.sub(r'\s+', '', s)
def quotes(t):
    return [norm(m) for m in pat.findall(t)]
def txt(r, k):
    return r['stages'][k]['text']
rows = {'낙관파': [], '비관파': []}
for r in runs:
    for side, k2, opp in (('낙관파', 'debate_r2_bull', ['debate_r1_bear']), ('비관파', 'debate_r2_bear', ['debate_r1_bull', 'debate_r2_bull'])):
        qs = quotes(txt(r, k2))
        opp_text = norm(' '.join(txt(r, o) for o in opp))
        found = [q for q in qs if q in opp_text]
        rows[side].append((len(qs) > 0, len(found) > 0))
n = len(runs)
print("== 2라운드 글에서 상대 글을 따옴표로 인용했는지 (회사 %d개 기준) ==" % n)
for side, v in rows.items():
    print("%s: 따옴표 인용이 있는 회사 %d개 | 그중 인용구가 상대 글에 실제로 있는 회사 %d개" % (side, sum(a for a, b in v), sum(b for a, b in v)))
print("(따옴표 안 문장이 상대 글에 글자 그대로 있어야 '실제 인용'으로 셌어. 의역해서 반박한 경우는 못 세.)")
