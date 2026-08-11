# Prompt Log 03 - Sentiment and Fusion

Purpose: record how AI helped implement the ProjectB sentiment stage: headline sentiment scoring, sector sentiment index, market fear/greed index, and a look-ahead-safe sentiment tilt applied to an equity fund.

## Stage Status

Status: completed for the current ProjectB build.

This stage uses the Stage 01 headline panel and Stage 02 portfolio outputs. It produces sentiment/fusion artifacts for the app and report.

## Final Outputs

Numbered reading copies:

- `results/data/Number_data/03_ticker_sentiment_scores.csv`
- `results/data/Number_data/03_sector_sentiment_index.csv`
- `results/data/Number_data/03_market_fear_greed_index.csv`
- `results/data/Number_data/03_fusion_fund_returns.csv`
- `results/data/Number_data/03_fusion_fund_weights.csv`
- `results/tables/Number_tables/03_sentiment_coverage_summary.csv`
- `results/tables/Number_tables/03_sector_sentiment_summary.csv`
- `results/tables/Number_tables/03_fusion_comparison.csv`
- `results/tables/Number_tables/03_fusion_metrics.csv`
- `results/tables/Number_tables/03_fusion_diagnostics.csv`
- sentiment and fusion figures under `results/figures/Number_figures/`

Canonical runtime/course copies:

- `results/data/sector_sentiment_index.csv`
- `results/data/ticker_sentiment_scores.csv`
- `results/data/market_fear_greed_index.csv`
- `results/data/fusion_fund_returns.csv`
- `results/data/fusion_fund_weights.csv`
- unnumbered sentiment/fusion tables and figures

## Entry 1 - Build sentiment index and sentiment-fusion extension

### Objective
Score news headlines, build a sector sentiment index, lag the signal for trading safety, and test whether sentiment improves a portfolio.

### Prompt Summary
The student asked the assistant to begin the next stage according to the course requirements, after the portfolio/OOS backtest stage was complete.

### Assistant Output
The assistant implemented `src/sentiment.py`, `src/fusion.py`, and the sentiment/fusion sections of `scripts/run_part_b.py`. The sentiment model uses NLTK VADER with a small finance lexicon extension, converts compound scores to a 0-100 fear/greed scale, aggregates sector sentiment, records news coverage, creates a market fear/greed index, and generates lagged live sentiment variables. The fusion test applies a fixed-strength sector sentiment tilt to `Equity - Minimum Variance` and compares it with the base fund.

### Risk/Issue
Risks included over-cleaning headlines before VADER, treating missing sentiment as clean neutrality, using same-day sentiment in trading, using full-sample z-scores as live signals, applying equity news sentiment to crypto, and hiding a negative fusion result.

### Student Decision
Keep text features usable for VADER, use lagged sentiment for trading, do not assign equity-news sentiment to crypto, and use a fixed tilt strength of `0.15` rather than tuning after observing performance.

### Verification
Commands used:

```powershell
..\..\.venv\Scripts\python.exe -m py_compile src\sentiment.py src\fusion.py scripts\run_part_b.py
..\..\.venv\Scripts\python.exe scripts\run_part_b.py
..\..\.venv\Scripts\python.exe -m pytest tests\test_smoke.py -q
..\..\.venv\Scripts\python.exe scripts\check_handin.py
```

Observed checks:

- `ticker_sentiment_scores.csv`: 37,962 rows.
- `sector_sentiment_index.csv`: 9,832 rows.
- `market_fear_greed_index.csv`: 1,006 rows.
- `fusion_fund_returns.csv`: 753 rows.
- `fusion_fund_weights.csv`: 1,800 rows.
- Sector sentiment lag violations: `0`.
- Fusion weight-sum maximum absolute error: about `8e-16`.
- Fusion lag violations: `0`.
- Sentiment tilt reduced Sharpe from `0.550199` to `0.481774`.
- Smoke test result: `2 passed`.
- Hand-in checker after this stage: `22 checks passed`, with only the missing report PDF reminder at that time.

### Current Status
Complete. The project has a standalone sentiment index and a look-ahead-safe fusion result. The negative fusion result is treated as evidence to interpret, not as a result to hide.
