
# multi-ai-debate-check

Measuring number accuracy and decision changes in a multi-AI debate pipeline, using fictional companies.

> This is not investment advice and does not measure investment performance. All companies and numbers are fictional.

## Summary

- **What I tested:** whether a pipeline of AI roles (three lenses, a trader, a bull/bear debate, a final trader) keeps or loses information, using fictional companies.
- **What I found:**
  - The original debate prompt made round 2 mostly repeat round 1 (similarity 0.75 and 0.71). A prompt asking for a specific rebuttal cut repetition to 0.19 and 0.24, but did not change decisions beyond noise.
  - The same input gives a different decision between runs (re-asking gave the same verdict for 83% of companies), so a same-input rerun is needed as a control.
  - In the one valid test of the hidden-rule experiment (v3c), the final trader caught 57% of the traps and the first trader 60% (difference -3.0 pp, 95% CI -12.0 to +6.0): no effect detected.
- **How I tested:** pre-registered rules, control groups, a same-input rerun to measure noise, and a pilot gate. Two of my three hidden-rule attempts (v3, v3b) could not be interpreted and are reported as such.
- **Limits:** fictional data, one model, one run per condition. Nothing here says how this works on real markets.

## Question

When several AI "roles" pass work to each other (investor lenses -> trader -> bull/bear debate -> trader), what happens to (1) the numbers they cite and (2) the final decision?

This continues my earlier work on measuring how AI outputs drift from their instructions: https://github.com/parkseyoung1215-netizen/my-tech-portfolio

## Setup

- **Data:** 30 fictional companies, 6 numbers each (revenue growth, PER, debt ratio, operating margin, 3-month price change, cash months). Generated with a fixed seed; each number is drawn independently, so combinations can be unrealistic (e.g. a loss-making company with a PER).
- **Model:** gpt-4o-mini, temperature 0.7, JSON output with `text`, `verdict` (BUY / HOLD / SELL) and `cited` (every number used, with its metric name).
- **Pipeline per company:**
  1. Solo baseline: one AI sees the fact sheet and decides.
  2. Three lenses (value, growth, momentum) see the fact sheet and each decide.
  3. Trader sees only the three lens reports (not the raw numbers) and makes a first decision.
  4. Bull (always argues BUY) and bear (always argues SELL) debate for 2 rounds, seeing only text.
  5. Trader sees the lens reports and the debate and makes the final decision.
- **v2 debate prompt:** round 2 only, "rebut one specific claim the opponent made (quote a few words) and add one new point; do not repeat". Round 1, the lens reports and the first trader decision are reused from v1.
- **Control:** the final decision is asked again with the original debate, to measure how much decisions change from randomness alone.

## What is measured

- Share of cited numbers that do not match the fact sheet (tolerance 0.051).
- Share of companies where the debate changed the trader's decision.
- Lens direction check: correlation between the verdict (BUY=1, HOLD=0, SELL=-1) and the metric each lens is supposed to care about.
- Repetition: text similarity (character level) between a side's round 1 and round 2, with bull-vs-bear round 1 as a reference.
- Quote check: whether text in quotation marks in round 2 appears word for word in the opponent's earlier text.
- 95% bootstrap confidence intervals over companies (2000 resamples).

## Results (30 companies)

**Numbers.** Cited numbers that did not match the fact sheet: 0% at almost every stage, 1% for the bear in round 1 (CI 0-3%) (n = 101-151 cited numbers per stage).

**Decisions.** Most decisions are HOLD (solo: BUY 1 / HOLD 26 / SELL 3; final trader: BUY 3 / HOLD 23 / SELL 4). The debate changed the trader's decision for 17% of companies (CI 3-30%). The final decision matched none of the three lens verdicts for 1 of 30 companies.

**Lens direction** (correlation; mostly HOLD verdicts, so noisy):

| Lens | Metric | Correlation |
|---|---|---|
| value | PER (low is better) | 0.36 |
| value | debt ratio (low is better) | 0.59 |
| growth | revenue growth | 0.58 |
| growth | operating margin | 0.08 |
| momentum | 3-month price change | 0.65 |
| solo (control) | PER / 3-month change | 0.21 / 0.18 |

**Repetition with the original debate prompt.** Round 2 was close to a repeat of round 1: similarity 0.75 (bull) and 0.71 (bear), vs 0.26 between bull and bear. About 0.1 new metrics per side were cited in round 2.

**v2 prompt (rebut a specific claim).** Similarity dropped to 0.19 and 0.24, and 0 of 30 companies were >= 0.7 similar. Quotation marks appeared in round 2 for 27 (bull) and 28 (bear) of 30 companies, and in 16 and 20 of those at least one quote matched the opponent's text word for word (v1: 0). New metrics cited: 0.40 and 0.20 per company.

**Did v2 change decisions?** Not beyond noise. Re-asking the final decision with the same input gave the same verdict for 83% of companies (CI 70-93%); v1 final vs v2 final agreed for 83% (CI 70-97%). The debate changed the first decision for 17% (v1), 13% (v1 rerun) and 13% (v2).

## Limitations

- Fictional data with independent random values; nothing here says how these pipelines would perform on real markets.
- Bull and bear are forced to opposite stances, so their verdicts carry no information.
- One model, one run per condition, 30 companies. Differences smaller than roughly 15 percentage points cannot be detected.
- The number check only covers the `cited` list. It does not check how numbers are interpreted (for example, calling a debt ratio of 51.1% a "risk") or numbers written only in the free text.
- The quote check requires word-for-word matches, so it undercounts paraphrased quotes. The 0.7 similarity threshold was chosen arbitrarily.
- Explanations given by the AI are self-reported and may not be the real cause of a decision.
- Why decisions concentrate on HOLD is untested; one guess is that forced opposite arguments cancel out.
- Decisions vary between runs of the same input partly because of the sampling randomness I set (temperature 0.7). I did not test whether a lower temperature would reduce this.

## My decisions

- Why I chose value / growth / momentum as lenses: I chose the styles that I believe get the most attention today. In my view, value, growth, and momentum are the approaches that attract the most interest and focus from people. I also chose them because the three styles are different from each other.
- Why I used fictional companies instead of real ones: I wanted to use real companies, but I started with fictional ones so that I could verify the method before applying it to real data. Also, if I used real companies, people might actually believe the positive or negative results and make decisions based on them, so I chose fictional data.
- Why I added the control rerun and what it changed in how I read the results: When I found out that an AI can make different decisions for the same input, it felt like a new discovery. I had assumed that an AI gives a consistent value from repeated data, so it felt fascinating that the same input could produce different answers. I kept checking how often these changes happened, and I did not count a change in decision as an effect of the debate unless it was larger than the difference I saw when re-asking with the same input.

## How to reproduce

```
pip3 install openai numpy
read -s OPENAI_API_KEY; export OPENAI_API_KEY # paste the key, never put it in code
python3 gen_companies.py
python3 run_debate.py 30
python3 score_debate.py
python3 check_repeat.py
python3 run_debate_v2.py # reads ~/results_v3/debate_runs.jsonl, writes ~/v2/results_v3/debate_runs.jsonl
python3 compare_v2.py
cd ~/v2 && python3 ~/check_quotes.py && python3 ~/score_debate.py
```


Scripts read and write relative to the working directory or your home folder. The results from my run are in `results_v3/` (original debate) and `v2/results_v3/` (v2 debate). Use `python3 view_company.py <name>` to read one company's full chain.


## Hidden-rule experiments (v3, v3b and v3c)

Question: when a pipeline of AI stages passes work along (three analyst lenses, a trader, a bull/bear debate, a final trader), does information get lost on the way?

Setup: fictional companies with a hidden rule that I wrote (cash runway under 12 months means DOWN, otherwise fast growth means UP; 10% of labels flipped as noise in v3 and v3b, none in v3c, where the rule uses cash only). "Traps" are companies that look good (high growth, low PER) but have short cash runway. If the warning is lost between stages, the final trader should catch fewer traps than the first one. Rules and thresholds were committed before running (see `PREREGISTRATION.md`, `PREREGISTRATION_v3b.md` and `PREREGISTRATION_v3c.md`; the commit time is the record). I did not change any rule after seeing results.

### v3 (World A, HOLD allowed)
- 200 companies, 66 traps. Primary: share of traps where the verdict is not BUY, final trader vs first trader, threshold +15 pp.
- Result: no effect detected.
- Problems I found afterwards (my design mistakes): (1) allowing HOLD made "not BUY" almost the same as "defaulting to HOLD", so it did not show that the warning was used; I first read this result wrongly and retracted it after checking the control group; (2) there was little room to improve; (3) the model barely used the hidden signal.

### v3b (World A2, forced UP/DOWN)
- Fix: the model must choose UP or DOWN, and there is a control group (same growth and PER, cash runway 12 months or more): 200 companies, 61 traps, 68 controls.
- Pre-registered precondition (Check 1): the value lens must say DOWN at least 20 pp more often on traps than on controls, with the 95% interval above 0. Otherwise the world did not test information loss and the main result must not be interpreted.
- Result: Check 1 not passed. Difference +13.8 pp (95% CI -1.7 to +28.9). So the main result is reported for reference only and is not interpreted. The strict-lens step was not run, as pre-registered.
- Noise: asking the final trader the same question again gave a trap/control gap of +20 pp (95% CI +2.6 to +35.9) by sampling alone. Accuracy at every stage was 49-58%, close to the 52% you get by always guessing UP.
- Before the full run I ran a 5-company smoke test and did not look at its results.


### v3c (World A3, stronger signal)
- Changes from v3b (pre-registered in `PREREGISTRATION_v3c.md`, committed before any v3c run): the rule uses cash only (cash < 12 months means DOWN); traps have 1-6 months of cash and controls 24-48; 100 traps and 100 controls; the decision rule is two-sided (it can also detect a drop); a 30-company pilot had to show the value lens uses the cash signal (at least +25 pp) before the main run.
- Pilot: value lens difference +33.3 pp, gate passed (15 + 15 companies, not used in the main analysis).
- Check 1 passed: value lens DOWN on 87% of traps vs 66% of controls, +21.0 pp (95% CI +9.0 to +31.0). The margin is small.
- Primary result: no effect detected. The final trader caught 57% of traps vs 60% for the first trader, -3.0 pp (95% CI -12.0 to +6.0), within noise (+1.0 pp). This does not prove there is no loss: a drop of up to about 12 pp cannot be excluded.
- The debate changed 13 of 60 trap verdicts the first trader got right; re-asking the final trader with the same input changed 12. The debate step looks like sampling noise here.
- Not pre-registered, descriptive only: the value lens said DOWN on 87% of traps, the first trader on 60%; for 27 of the 87 traps the lens warned and the trader said UP. If a warning is lost, this lens-to-trader step is a candidate, but the value lens also says DOWN on 66% of controls, so I do not draw a conclusion from it.
- Cost: pilot $0.07, main run $0.45.

### What I take from this
- v3 and v3b could not answer the question. v3c was the first valid test, and it found no effect between the first trader and the final trader (final minus first: -3.0 pp, 95% CI -12.0 to +6.0).
- What I learned is about the measurement: sampling noise at this sample size is as large as the effect I was looking for, and a weak signal makes the whole experiment uninterpretable. The pre-registered precondition stopped me from reading noise as a result.
- Limits: fictional data, one model (gpt-4o-mini), one run per condition, one rule. This says nothing about real markets.
- Cost: about $0.45 per full run.
  

### My decisions (v3, v3b and v3c)
- Why I chose this question: I am mainly interested in whether AI produces better answers by passing work through stages. But if information disappears along the way, couldn't it get worse? That curiosity is why I chose this question.
- What I did when v3 did not work: I expected v3 to turn out as I predicted, but it did not, and when I compared it with the control group I realized my first reading was wrong. I decided that removing the HOLD option was necessary for a clear check, so I redesigned the experiment that way.
- What I did when Check 1 failed: The result did not pass the criterion I had set in advance, so I could not interpret the main result and did not. I also did not run the next step, because it depends on passing Check 1. I did not change the rule after seeing the result.
- What I learned: I think I realized two things from these experiments. First, the AI behaved the way I had imagined: it is often inconsistent. I saw that the same input can give different answers. Second, connected to this, I had trusted the AI because it tries to give the best answer in each situation, but I came to think that I should not trust a result right away just because I see it.
- Why I decided to run v3c: So far, several problems meant that I had not yet gotten a usable answer. I still wanted an answer: can a debate lead to a better answer, or does it get worse when information disappears? Even though the result did not come out as I expected, I wanted to keep trying and I think it was meaningful.
- What I decided after v3c: B (no effect) is also part of the result. I accept that getting the result I wanted is not easy. I may design a new setup and run another experiment.

### Files
- `hidden_rule/gen_world.py`, `run_world.py`, `score_world.py`: v3 (results in `hidden_rule/world_A/`)
- `hidden_rule/gen_a2.py`, `run_forced.py`, `score_forced.py`: v3b (results in `hidden_rule/world_A2/`)
- `hidden_rule/gen_a3.py`, `run_forced.py` (with `--world`), `score_forced.py` (with `--world --two-sided --pilot`): v3c (results in `hidden_rule/world_A3/` and the pilot in `hidden_rule/world_A3_pilot/`)
- Pre-registrations: `hidden_rule/PREREGISTRATION.md`, `hidden_rule/PREREGISTRATION_v3b.md`, `hidden_rule/PREREGISTRATION_v3c.md`
