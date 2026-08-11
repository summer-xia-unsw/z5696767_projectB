# Prompt Log 01 - Data Foundation

Purpose: record how AI helped move the student's own ProjectA data foundation into ProjectB and generate the Stage 01 return/headline inputs used by portfolios, sentiment, app, and report.

## Stage Status

Status: completed for the current ProjectB build.

This stage created cleaned returns and a headline daily panel. It did not build portfolios, sentiment scores, fusion results, app UI, or report text.

## Final Outputs

Numbered reading copies:

- `results/data/Number_data/01_equity_returns.csv` - equity daily returns.
- `results/data/Number_data/01_crypto_returns_aligned.csv` - crypto returns aligned to the equity trading calendar.
- `results/data/Number_data/01_combined_returns_panel.csv` - combined equity and crypto returns.
- `results/data/Number_data/01_headline_daily_panel.csv` - ticker-day headline panel for later sentiment scoring.

Canonical runtime copies:

- `results/data/equity_returns.csv`
- `results/data/crypto_returns_aligned.csv`
- `results/data/combined_returns_panel.csv`
- `results/data/headline_daily_panel.csv`

## Entry 1 - Understand ProjectB requirements before coding

### Objective
Understand what ProjectB requires before changing code, especially how Part B builds on the student's own Part A foundation and how Week 08, Week 09, and Week 10 materials affect the task.

### Prompt Summary
The student asked the assistant not to start implementation yet, but to read the ProjectB `course_requirements` files and study Week 08, Week 09, and Week 10 so the task could be planned correctly.

### Assistant Output
The assistant identified that ProjectB requires out-of-sample investable funds, fund returns, fund weights, performance metrics, headline sentiment scoring, sector sentiment index, sentiment/fund fusion, a Streamlit app, a Word/PDF report, AI workflow logs, a public GitHub repository, and a live Streamlit URL.

### Risk/Issue
Starting to code without reading the brief could lead to missing required outputs, mixing Part A and Part B tasks, or creating a ProjectB folder that cannot run independently.

### Student Decision
Use a staged workflow: data foundation first, then portfolios, sentiment/fusion, app, report, and final deployment.

### Verification
The assistant matched the brief and checker-required filenames:

- `results/data/fund_returns.csv`
- `results/data/fund_weights.csv`
- `results/data/sector_sentiment_index.csv`
- `results/tables/performance_metrics.csv`

### Current Status
Complete. The requirements review guided all later stages.

## Entry 2 - Migrate ProjectA ETL/features into ProjectB

### Objective
Bring the student's own ProjectA ETL/features logic into ProjectB and generate the base returns/headline panel inside ProjectB.

### Prompt Summary
The student asked to start by migrating ProjectA ETL/features into ProjectB and generating the ProjectB base returns/headline panel.

### Assistant Output
The assistant updated ProjectB's own files:

- `src/etl.py`
- `src/features.py`
- `scripts/run_part_b.py`

Implemented work included date normalisation, cleaned equity prices, crypto capped at `2023-12-31`, headline deduplication, equity daily returns from `adjClose`, crypto returns aligned after return computation, a combined returns panel, and a headline daily panel.

### Risk/Issue
The main risks were accidentally depending on ProjectA paths and computing crypto returns after calendar alignment. Both would weaken reproducibility and introduce wrong returns.

### Student Decision
Keep all logic inside ProjectB. Compute returns first, then align crypto returns to the equity trading calendar. Keep sentiment scoring out of this stage because it belongs to Stage 03.

### Verification
Commands used:

```powershell
..\..\.venv\Scripts\python.exe scripts\run_part_b.py
..\..\.venv\Scripts\python.exe -m pytest tests\test_smoke.py -q
```

Observed outputs:

- `equity_returns.csv`: 50,250 rows, 50 tickers.
- `crypto_returns_aligned.csv`: 10,060 rows, 10 crypto tickers.
- `combined_returns_panel.csv`: 60,310 rows, 60 assets.
- `headline_daily_panel.csv`: 37,962 ticker-day rows.
- Smoke test result: `2 passed`.

### Current Status
Complete. Stage 01 provides the input layer for portfolios and sentiment.
