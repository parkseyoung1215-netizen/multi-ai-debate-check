
# multi-ai-debate-check

Measuring number accuracy and decision changes in a multi-AI debate pipeline, using fictional companies.

> This is not investment advice and does not measure investment performance. All companies and numbers are fictional.

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
