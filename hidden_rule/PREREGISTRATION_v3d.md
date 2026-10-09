# Pre-registration v3d (bottleneck experiment, positive control)

Written before any v3d data exist.

## Why
v3c found no effect between the first trader and the final trader (-3.0 pp, 95% CI -12.0 to +6.0). That result only means something if the measurement can see a loss when there is one. v3d tests this: it removes information on purpose and checks whether the measurement notices.

## Data and pipeline
The same 200 companies as v3c (World A3, seed 12: 100 traps, 100 controls), the same pipeline, model (gpt-4o-mini) and temperature (0.7). The v3c run is the "normal" run.

## Arm X: instrument check
cash_months is set to 24.0 for every company (a value that is safe under the rule and the lowest in the control range), and the full pipeline runs again (run_forced.py on world_A3_nocash). The cash information is removed at the source.

## Arm S: 15-word bottleneck
The lens reports from the v3c run are reused. Each is compressed to at most 15 words by gpt-4o-mini, and the verdict labels are removed. The first trader, the debate, the final trader and the same-input rerun then run on the compressed reports (run_summary.py).

## Measure and rule (the same for both arms)
- Trap caught = share of traps with verdict DOWN, at trader_final (primary) and trader_pre (descriptive).
- Compare normal minus arm, paired by company, 95% paired bootstrap (2000 resamples). Noise = |trader_final - trader_final_rerun| on traps in the normal run.
- LOSS CAUSED: difference >= +10 pp, interval excludes 0, difference larger than noise. Otherwise: no loss detected.

## Order and how I read it
- X runs first. If X shows LOSS CAUSED, the measurement is sensitive to a drop of that size, and S is run and interpreted.
- If X does not, the measurement could not see even a complete removal of the information. Then the v3c result (no effect) is not reliable, and S is not run.

## What this can and cannot show
- X is an extreme case (total removal). Passing it shows the measurement sees drops of about that size, not smaller ones. Effects below about 10 pp cannot be detected.
- S is one specific bottleneck. A result for S says nothing about other ways information could be lost.
- Fictional data, one model, one run per condition. The arms are compared with the earlier v3c run, so sampling noise from two separate runs is included.

## Stated before running
I would find a loss from the bottleneck more interesting than none. That is why the rules are fixed in advance and I will not change them after seeing results.

## Changes
(none yet)
