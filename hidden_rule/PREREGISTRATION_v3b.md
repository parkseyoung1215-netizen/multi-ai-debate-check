# Hidden-rule experiment v3b: pre-registration

Written before any run of v3b. The commit time of this file is the record. Any later change is listed under "Changes".

## Why v3b

World A (v3) found no effect of the debate by its pre-registered rule. Looking at the data afterwards (not planned in advance) showed three design problems:
1. About 80% of verdicts were HOLD, so "not BUY" mostly meant "no call" and accuracy was computed on few calls.
2. The trader already caught 83% of the traps before the debate, so there was little room to improve (ceiling).
3. Among companies that look attractive, the BUY share was similar with low cash and with enough cash. There was no sign that the cash signal was used at all.
The v3 results stay in `world_A/` unchanged.

## Setup

- Same pipeline and model as v3 (gpt-4o-mini, temperature 0.7) with one change: forced choice. Every stage must answer UP or DOWN ("Will this company's stock rise over the next 12 months? You must choose one"). There is no HOLD.
- World A2: 200 fictional companies, seed 10. 60 traps (revenue_growth_pct > 20, per < 20, cash_months < 12), 60 controls (same growth and per, cash_months 12-48) and 80 random companies. Same hidden rule as world A: DOWN if cash_months < 12, otherwise UP if revenue_growth_pct > 15, else DOWN. 10% of labels are flipped as noise.
- Stages and control rerun as in v3.

## Check 1: was the cash signal used? (precondition)

- Measure: share of DOWN verdicts for lens_value on traps minus on controls (the value lens is the one told to weigh cash_months). 95% bootstrap interval, resampling within each group.
- Precondition passed only if the difference is at least +20 percentage points and the interval excludes 0.
- If not passed: I report that the world did not test information loss, and I do not interpret the primary outcome as evidence about the debate. The numbers are still reported.

## Primary outcome (interpreted only if Check 1 passed)

- Trap caught = share of the 60 traps with verdict DOWN, trader_final vs trader_pre.
- Effect rule: (1) difference at least +10 percentage points, (2) 95% paired bootstrap interval excludes 0, (3) larger than |trader_final - trader_final_rerun| on the same outcome.
- Ceiling rule: if trader_pre already catches 85% or more of the traps, I report "no room to improve" instead of "no effect".

## Secondary outcomes

- Accuracy per stage (no HOLD, so accuracy is the share correct), with intervals and the majority-label baseline. trader_final vs solo.
- Warning lost at the trader (lens_value DOWN on a trap, trader_pre UP) and lost in the debate (trader_pre DOWN, trader_final UP).
- trader_final_rerun minus trader_pre as a replication of the debate effect.

## Next step, decided in advance (strict lenses)

- Only if Check 1 passed: run the same companies again where each lens sees only its own metrics (value: per, debt_ratio_pct, cash_months; growth: revenue_growth_pct, op_margin_pct; momentum: price_change_3m_pct). Compare trap caught at trader_pre, strict vs shared (paired by company). Information loss from the restriction counts only if strict is lower by at least 10 percentage points and the interval excludes 0.
- If Check 1 did not pass, this step is not run.

## What I will not claim

- Results hold only for fictional rules, one model, one run per condition. Nothing here says how the pipeline performs on real markets.
- If a rule is not met I report "no effect detected" or "not interpretable". I will not change rules or thresholds after seeing results.

## Changes

- Clarification, written before any run: the generator makes 60 traps, 60 controls and 80 random companies, but some random companies also meet the conditions. The analysis uses every company that meets the conditions (traps: growth > 20, per < 20, cash < 12; controls: growth > 20, per < 20, cash >= 12), so the group sizes are slightly above 60. The counts are printed when the companies are generated.
