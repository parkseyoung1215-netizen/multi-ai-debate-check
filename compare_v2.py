import json, os, numpy as np
HOME = os.path.expanduser('~')
v1 = [json.loads(l) for l in open(HOME + '/results_v3/debate_runs.jsonl')]
v2 = [json.loads(l) for l in open(HOME + '/v2/results_v3/debate_runs.jsonl')]
names2 = {r['company']['name'] for r in v2}
v1 = [r for r in v1 if r['company']['name'] in names2]
assert [r['company']['name'] for r in v1] == [r['company']['name'] for r in v2]
rng = np.random.default_rng(0)
def ci(vals):
    v = np.array(vals, float)
    b = [rng.choice(v, len(v)).mean() for _ in range(2000)]
    return "%.0f%% (95%% CI %.0f-%.0f%%, n=%d)" % (100*v.mean(), 100*np.percentile(b, 2.5), 100*np.percentile(b, 97.5), len(v))
def V(r, k):
    return r['stages'][k].get('verdict')
def agree(A, ka, B, kb):
    return [int(V(x, ka) == V(y, kb)) for x, y in zip(A, B)]
def unsupported(R, k):
    return [int(V(r, k) not in {V(r, 'lens_value'), V(r, 'lens_growth'), V(r, 'lens_momentum')}) for r in R]
print("== (대조군) 같은 입력으로 최종 결정을 다시 시켰을 때 같은 결정이 나온 비율: AI 답의 우연 정도 ==")
print("v1 최종 == v1 토론으로 다시 한 최종 :", ci(agree(v1, 'trader_final', v2, 'trader_final_rerun_v1debate')))
print()
print("== 토론 방식을 바꿨을 때 ==")
print("v1 최종 == v2 최종 :", ci(agree(v1, 'trader_final', v2, 'trader_final')))
print()
print("== 토론이 트레이더 1차 결정을 바꾼 비율 ==")
print("v1 토론          :", ci([1 - x for x in agree(v1, 'trader_pre', v1, 'trader_final')]))
print("v1 토론 (재실행) :", ci([1 - x for x in agree(v2, 'trader_pre', v2, 'trader_final_rerun_v1debate')]))
print("v2 토론          :", ci([1 - x for x in agree(v2, 'trader_pre', v2, 'trader_final')]))
print()
print("== 최종 결정이 투자자 3명 중 누구의 결정과도 안 맞는 비율 ==")
print("v1 최종          :", ci(unsupported(v1, 'trader_final')))
print("v1 최종 (재실행) :", ci(unsupported(v2, 'trader_final_rerun_v1debate')))
print("v2 최종          :", ci(unsupported(v2, 'trader_final')))
print()
print("(v1 최종과 v1 재실행의 차이가 AI 답의 우연 정도야. v2가 그 정도보다 더 달라야 토론 방식 효과라고 말할 수 있어.)")
