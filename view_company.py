import json, sys
name = sys.argv[1].lower()
for l in open('results_v3/debate_runs.jsonl'):
    r = json.loads(l); c = r['company']; s = r['stages']
    if name not in c['name'].lower():
        continue
    print('##########', c['name'])
    print('숫자표: PER', c['per'], '| 성장률', c['revenue_growth_pct'], '| 이익률', c['op_margin_pct'], '| 부채', c['debt_ratio_pct'], '| 3개월', c['price_change_3m_pct'], '| 현금', c['cash_months'])
    print()
    print('--- [1] 투자자 3명의 글 (트레이더 1차가 읽는 것) ---')
    for k, label in (('lens_value', '가치'), ('lens_growth', '성장'), ('lens_momentum', '모멘텀')):
        print('[%s] %s: %s' % (label, s[k]['verdict'], s[k]['text']))
    print()
    print('--- [2] 트레이더 1차 결정 ---')
    print('%s: %s' % (s['trader_pre']['verdict'], s['trader_pre']['text']))
    print()
    print('--- [3] 토론 ---')
    for k, label in (('debate_r1_bull', '1라운드 낙관파'), ('debate_r1_bear', '1라운드 비관파'), ('debate_r2_bull', '2라운드 낙관파'), ('debate_r2_bear', '2라운드 비관파')):
        print('[%s] %s' % (label, s[k]['text']))
    print()
    print('--- [4] 트레이더 최종 결정 ---')
    print('%s: %s' % (s['trader_final']['verdict'], s['trader_final']['text']))
