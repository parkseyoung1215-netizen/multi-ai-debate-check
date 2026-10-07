import json, difflib, numpy as np
runs = [json.loads(l) for l in open('results_v3/debate_runs.jsonl')]
rng = np.random.default_rng(0)
def sim(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()
def mean_ci(v):
    v = np.array(v, float)
    b = [rng.choice(v, len(v)).mean() for _ in range(2000)]
    return "%.2f (95%% CI %.2f-%.2f, n=%d)" % (v.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5), len(v))
def txt(r, k):
    return r['stages'][k]['text']
def metrics(r, k):
    return set(x.get('metric') for x in r['stages'][k].get('cited', []))
bull = [sim(txt(r, 'debate_r1_bull'), txt(r, 'debate_r2_bull')) for r in runs]
bear = [sim(txt(r, 'debate_r1_bear'), txt(r, 'debate_r2_bear')) for r in runs]
cross = [sim(txt(r, 'debate_r1_bull'), txt(r, 'debate_r1_bear')) for r in runs]
print("== 글 유사도 (0=완전히 다름, 1=똑같음) ==")
print("낙관파 1라운드 vs 2라운드 :", mean_ci(bull))
print("비관파 1라운드 vs 2라운드 :", mean_ci(bear))
print("(기준) 같은 회사 낙관파 vs 비관파, 1라운드:", mean_ci(cross))
print()
TH = 0.7
print("== 2라운드가 1라운드와 %.1f 이상 비슷한 회사 수 ==" % TH)
print("낙관파:", sum(x >= TH for x in bull), "| 비관파:", sum(x >= TH for x in bear), "| 둘 다:", sum(a >= TH and b >= TH for a, b in zip(bull, bear)))
print()
nb = [len(metrics(r, 'debate_r2_bull') - metrics(r, 'debate_r1_bull')) for r in runs]
nr = [len(metrics(r, 'debate_r2_bear') - metrics(r, 'debate_r1_bear')) for r in runs]
print("== 2라운드에서 1라운드엔 없던 지표를 새로 인용한 평균 개수 ==")
print("낙관파: %.2f | 비관파: %.2f" % (np.mean(nb), np.mean(nr)))
print("(0.7 기준은 내가 임의로 정한 값이야. 유사도는 글자 단위 비교라서 어순이 달라지면 낮게 나올 수 있어.)")
