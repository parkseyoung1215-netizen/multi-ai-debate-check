# Hidden-rule experiment: pre-registration

Written before any run of this experiment. The commit time of this file is the record. Any later change is listed under "Changes" at the bottom.

## Question

When AI roles pass work through several stages (lenses -> trader -> bull/bear debate -> trader), does the final decision become more correct, and does a warning that one lens stresses survive the later stages?

## Setup

- Same pipeline as the first experiment. Model: gpt-4o-mini, temperature 0.7 (a temperature 0 repeat is a secondary run).
- Six fictional metrics per company, same ranges as before. The true label (UP / DOWN) comes from a hidden rule that the AI is never told. 10% of labels are flipped at random as noise.
- Stages: solo; three lenses (value, growth, momentum); trader_pre; bull/bear debate for 2 rounds; trader_final; control: trader_final asked again with the same debate.
- Scoring: BUY = predicts UP, SELL = predicts DOWN, HOLD = no call. I report accuracy among calls AND the share of companies with a call.
- Effect rule (same for all worlds): the debate counts as helping only if (1) the difference reaches the threshold below, (2) the 95% bootstrap confidence interval (2000 resamples, paired by company) excludes 0, and (3) the difference is larger than the same difference measured with the control rerun.

## World A (run first): hidden warning

- 200 companies, seed 7. About 60 are "traps": revenue_growth_pct > 20, per < 20 and cash_months < 12.
- Rule: DOWN if cash_months < 12. Otherwise UP if revenue_growth_pct > 15, else DOWN.
- Primary outcome: share of trap companies where the verdict is not BUY ("trap caught"), trader_final vs trader_pre. Threshold: +15 percentage points.
- Secondary: warning lost at the trader (lens_value not BUY, trader_pre BUY); warning lost in the debate (trader_pre not BUY, trader_final BUY); accuracy and coverage per stage; temperature 0 repeat.

## World C (second): simple weighted sum (baseline)

- 200 companies, seed 8, all random.
- Rule: UP if 0.4*z(revenue_growth_pct) - 0.3*z(per) + 0.3*z(price_change_3m_pct) > 0, else DOWN (z = standardized within the generated set).
- Primary outcome: accuracy among calls, trader_final vs solo. Threshold: +10 percentage points.

## World B (third, if time allows): two lenses must combine

- 200 companies, seed 9.
- Rule: UP only if op_margin_pct > 10 and debt_ratio_pct < 100, else DOWN.
- Primary outcome: accuracy among calls, trader_final vs solo. Threshold: +10 percentage points.

## What I will not claim

- Results hold only for these fictional rules, one model, one run per condition. Nothing here says how the pipeline performs on real markets.
- If a threshold is not met I report "no effect detected". I will not change the rule or the threshold after seeing results.

## Changes

(none yet)
