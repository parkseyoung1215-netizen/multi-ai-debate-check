# Pre-registration v3c (World A3)

Written before any v3c data exist. Earlier attempts: v3 (HOLD allowed, not interpretable) and v3b (Check 1 not passed).

## Question
Same as before: when AI stages pass work along (three lenses, a trader, a bull/bear debate, a final trader), does a warning get lost on the way, or does it get stronger?

## What changes from v3b, and why
- v3b failed Check 1: the value lens used the cash signal too weakly (+13.8 pp, needed +20 pp). So the signal is made stronger and simpler.
- The rule uses cash only: cash_months < 12 means DOWN, otherwise UP. Labels equal the rule exactly (no label noise).
- Traps: cash 1-6 months. Controls: cash 24-48 months. Both look attractive otherwise (revenue growth 20-60, PER 5-20). The other metrics are random.
- 100 traps + 100 controls = 200 companies (seed 12). v3b had 61 and 68.
- The decision rule is now two-sided: it can also detect a DROP in trap catching, not only an improvement.
- The strict-lens step is not part of v3c.

## Pipeline
Unchanged from v3b: gpt-4o-mini, temperature 0.7, forced UP/DOWN, three lenses, trader, 2-round bull/bear debate, final trader, plus the same-input rerun of the final trader as a noise control (run_forced.py).

## Step 1: pilot gate
- 30 companies (15 traps + 15 controls, seed 11), full pipeline, one run.
- Gate: the value lens says DOWN at least 25 pp more often on traps than on controls (point estimate only). If yes: run the main experiment. If no: stop, report "the pilot did not show enough signal", and do not run the main experiment.
- I run only one pilot. If it stops, I do not change the world and try again inside v3c.
- Pilot data are not used in the main analysis.

## Step 2: main experiment (only if the gate says GO)
Check 1 (same as v3b): value lens DOWN share on traps minus on controls is at least +20 pp and the 95% paired-bootstrap interval is above 0. If not passed, the world did not test information loss and the primary result is not interpreted.

Primary: trap caught = share of traps with verdict DOWN, trader_final vs trader_pre (95% paired bootstrap, 2000 resamples). Noise = |trader_final - trader_final_rerun| on traps.
- IMPROVEMENT: difference >= +10 pp, interval excludes 0, difference larger than noise.
- INFORMATION LOSS: difference <= -10 pp, interval excludes 0, size larger than noise.
- Otherwise: no effect detected.
- Ceiling and floor: if trader_pre catches >= 85% of traps, an improvement cannot be claimed (no room). If it catches <= 15%, a loss cannot be claimed.

Secondary (descriptive only): accuracy per stage, trader_final minus solo, where the warning was lost (lens to trader, trader to final), and the rerun replication.

## What can and cannot be detected
With 100 traps, sampling noise is about +-5 pp (v3b showed about 6 pp). Effects smaller than about 10 pp cannot be detected.

## Stated before running
I would find an improvement or a loss more interesting than no effect. That is why the rules above are fixed in advance and I will not change them after seeing results.

## What I will not claim
- Results hold only for fictional data with a rule I wrote, one model, one run per condition. Nothing here says how the pipeline performs on real markets.
- If a rule is not met I report "no effect detected" or "not interpretable".

## Changes
(none yet)
