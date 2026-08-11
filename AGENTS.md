# AGENTS.md - NovaAlloc ProjectB AI Rules

This file records the project-specific rules I use when working with AI on FINS5545 ProjectB. It replaces the starter placeholder and is part of the graded AI workflow pack.

## Project Scope

- Project: NovaAlloc, a prototype systematic multi-asset investment app.
- Folder: `fins2026/z5696767_projectB`.
- Course part: Part B - Funds, Sentiment & App, covering Data Factory Floor Station 3 and Station 4.
- Build on my own Part A data foundation only. Do not read, copy, or rely on another student's project folder.
- Raw data must always load through `src/data_access.py`; do not commit raw `.parquet`, ZIP, API keys, or secrets.

## Required Course Outputs

The assistant must protect these required Part B outputs and exact filenames:

- `results/data/fund_returns.csv`
- `results/data/fund_weights.csv`
- `results/data/sector_sentiment_index.csv`
- `results/tables/performance_metrics.csv`
- `report/report.docx` as the editable Word source
- `report/report.pdf` as the submitted report
- `streamlit_app.py` as the deployed app entrypoint
- `.streamlit/config.toml` for deployment configuration
- numbered `ai/NN_prompt_log_*.md` files and this `AGENTS.md` as AI workflow evidence

## Modelling Rules

- Use `adjClose` for returns.
- Compute returns within each asset first; do not merge price levels and then difference.
- Cap crypto data at `2023-12-31`.
- Align crypto returns onto the equity trading calendar only after crypto returns are computed.
- Use walk-forward out-of-sample backtests only.
- Portfolio weights must be estimated using past data only.
- No look-ahead: no future returns, future sentiment, or full-sample fitted trading signals may enter a live decision.
- Rebalance monthly or less often unless the report explicitly justifies a different frequency.
- State the first live trading date, estimation window, rebalance rule, risk-free-rate assumption, and annualisation factor.
- Annualise equity and combined funds on the equity trading calendar, normally 252 days. Annualise pure crypto carefully and state the convention used.
- Keep equal-weight as a benchmark because it is a strong out-of-sample baseline.
- Treat every `(universe, method)` pair as a fund that an app user could invest in.

## Sentiment Rules

- Sentiment belongs to Part B Station 3, not the data-foundation step.
- Do not over-clean headline text before VADER-style scoring. Keep casing, punctuation, negations, and booster words.
- Deduplicate news only on exact `ticker`, `date`, and `title`; many headlines per ticker-day are normal.
- Align headlines to the same or next equity trading day before using them.
- Lag sentiment by at least one trading day before it affects any trading decision.
- Crypto has no news sentiment in this dataset; sentiment fusion applies only to equities.
- If using a finance lexicon or custom VADER extension, record the term-selection logic and any rejected terms.
- A negative fusion result is acceptable if it is look-ahead safe, measured, and explained.

## Streamlit App Rules

- The deployed app must be light.
- `streamlit_app.py` should read precomputed files from `results/`; it must not recompute backtests or run VADER at runtime.
- Runtime app dependencies belong in `requirements.txt`; build-only dependencies such as `nltk` belong in `requirements-dev.txt`.
- Do not commit `.streamlit/secrets.toml`.
- The app should support the investor journey: compare funds, open fund fact sheets, set allocation across funds, and read sentiment analytics.

## Report Rules

- Write the report for a financially literate but non-technical marker.
- Every table and figure must be referenced and interpreted in the text.
- Report must explain both performance and failure: what worked, what did not, and why.
- Include three concrete real-world recommendations.
- Keep economic interpretation in my own words. AI can help draft structure, but I must review and rewrite the reasoning.
- Use Word as the source: `report/report.docx`; export final hand-in as `report/report.pdf`.

## AI Workflow Rules

- Keep prompt logs in numbered `ai/NN_prompt_log_*.md` files, ordered by project stage. Use `04_prompt_log_app.md` for app work, `05_prompt_log_report_submission.md` for report/submission work, and `06_prompt_log_self_correction.md` for final AI self-correction evidence.
- Each log entry should include: the prompt, what AI produced, what was wrong or risky, what I changed, and how I verified it.
- Record corrections honestly, especially look-ahead bugs, calendar mistakes, solver failures, overclaiming in the report, deployment misunderstandings, formatting regressions, or AI-generated content that needed human review.
- Keep `ai/project_step_log.md` updated after each major project step.
- Before submission, run `python scripts/check_handin.py` from the ProjectB root and fix every `[FAIL]`.

## Working Commands

Run from `fins2026/z5696767_projectB` unless stated otherwise:

```powershell
..\..\.venv\Scripts\python.exe scripts\run_part_b.py
..\..\.venv\Scripts\python.exe -m pytest tests\test_smoke.py -q
..\..\.venv\Scripts\python.exe scripts\check_handin.py
streamlit run streamlit_app.py
```

## Current Build Order

1. Data foundation: ETL, returns, aligned crypto returns, headline daily panel.
2. Funds: OOS portfolio returns, weights, metrics, fact-sheet data.
3. Sentiment: VADER or finance-extended VADER, sector sentiment index, fear/greed analytics.
4. Fusion: look-ahead-safe sentiment tilt or factor for equity funds, before-vs-after evaluation.
5. App: precomputed-results dashboard and investor journey.
6. Report and submission pack: Word report, PDF, zip, public GitHub repo, live Streamlit URL.
7. Self-correction audit: re-check the brief, report, app, and AI logs; record issues in `ai/06_prompt_log_self_correction.md`.

