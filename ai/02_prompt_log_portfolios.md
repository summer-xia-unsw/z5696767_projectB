# Prompt Log 02 - Portfolios and OOS Backtest

Purpose: record how AI helped implement the ProjectB fund construction stage: investable funds, monthly walk-forward out-of-sample backtests, fund returns, fund weights, performance metrics, latest holdings, and portfolio figures.

## Stage Status

Status: completed for the current ProjectB build.

This stage uses Stage 01 return panels. It does not use sentiment data.

## Final Outputs

Numbered reading copies:

- `results/data/Number_data/02_fund_returns.csv`
- `results/data/Number_data/02_fund_weights.csv`
- `results/tables/Number_tables/02_performance_metrics.csv`
- `results/tables/Number_tables/02_latest_holdings.csv`
- `results/figures/Number_figures/02_fund_growth_of_1.png`
- `results/figures/Number_figures/02_combined_fund_drawdowns.png`
- `results/figures/Number_figures/02_combined_risk_parity_weights.png`
- `results/figures/Number_figures/02_fund_sharpe_barplot.png`
- `results/figures/Number_figures/02_fund_risk_return_scatter.png`

Canonical runtime/course copies:

- `results/data/fund_returns.csv`
- `results/data/fund_weights.csv`
- `results/tables/performance_metrics.csv`
- `results/tables/latest_holdings.csv`
- unnumbered copies of the portfolio figures under `results/figures/`

## Entry 1 - Implement portfolio funds and OOS backtests

### Objective
Create investable funds that can be evaluated out of sample and later shown in the app and report.

### Prompt Summary
The student asked the assistant to complete the `02_prompt_log_portfolios` stage: implement portfolio construction and generate `fund_returns.csv`, `fund_weights.csv`, and `performance_metrics.csv`.

### Assistant Output
The assistant implemented `src/portfolios.py` and connected it to `scripts/run_part_b.py`. The portfolio design includes Equity, Crypto, and Combined universes; Equal Weight, Minimum Variance, Maximum Sharpe, and Risk Parity methods; 12 total funds; long-only fully invested weights; monthly walk-forward backtesting; an expanding estimation window; and performance metrics plus latest holdings.

### Risk/Issue
Main risks were look-ahead bias, wrong rebalance timing, weights not summing to 1, optimiser failures, missing equal-weight benchmark, unstable required filenames, and overclaiming in-sample optimisation as real performance.

### Student Decision
Use weights estimated before the live trading month and record `rebalance_date`, `live_start_date`, and `live_end_date`. Keep equal weight as a benchmark and save latest holdings for fund fact sheets.

### Verification
Commands used:

```powershell
..\..\.venv\Scripts\python.exe -m py_compile src\portfolios.py scripts\run_part_b.py
..\..\.venv\Scripts\python.exe scripts\run_part_b.py
..\..\.venv\Scripts\python.exe -m pytest tests\test_smoke.py -q
..\..\.venv\Scripts\python.exe scripts\check_handin.py
```

Observed checks:

- `fund_returns.csv`: 10,404 rows, 12 funds.
- `fund_weights.csv`: 17,280 rows, 12 funds.
- `performance_metrics.csv`: 12 rows.
- `latest_holdings.csv`: 281 rows.
- Maximum absolute weight-sum error: about `4e-15`.
- Look-ahead violations where `rebalance_date >= live_start_date`: `0`.
- Smoke test result: `2 passed`.
- Hand-in checker after this stage: `21 checks passed`, with reminders only for missing report and sentiment outputs at that time.

### Current Status
Complete. The portfolio outputs are the core investable products for NovaAlloc.
