# Results Output Index

This folder keeps the course-required filenames and also provides numbered
copies for reading. Numbered copies are now collected under `Number_data`,
`Number_tables`, and `Number_figures` folders.

Do not delete the unnumbered files. `scripts/check_handin.py` and the Streamlit
app rely on exact names such as `fund_returns.csv`, `fund_weights.csv`,
`sector_sentiment_index.csv`, and `performance_metrics.csv`.

## 00 - Output Guides

- `results/data/Number_data/00_data_output_guide.docx`
- `results/tables/Number_tables/00_tables_output_guide.docx`
- `results/figures/Number_figures/00_figures_output_guide.docx`

Purpose: Chinese quick-reference guides for understanding numbered outputs in
`Number_data`, `Number_tables`, and `Number_figures`. These guides now cover
stages 00-05 and explain how numbered files match the outer canonical files.

## 01 - Data Foundation

- `results/data/Number_data/01_equity_returns.csv`
- `results/data/Number_data/01_crypto_returns_aligned.csv`
- `results/data/Number_data/01_combined_returns_panel.csv`
- `results/data/Number_data/01_headline_daily_panel.csv`

Purpose: cleaned return and headline-panel inputs for Part B modelling.

## 02 - Portfolios And OOS Backtest

- `results/data/Number_data/02_fund_returns.csv`
- `results/data/Number_data/02_fund_weights.csv`
- `results/tables/Number_tables/02_performance_metrics.csv`
- `results/tables/Number_tables/02_latest_holdings.csv`
- `results/figures/Number_figures/02_fund_growth_of_1.png`
- `results/figures/Number_figures/02_combined_fund_drawdowns.png`
- `results/figures/Number_figures/02_combined_risk_parity_weights.png`
- `results/figures/Number_figures/02_fund_sharpe_barplot.png`
- `results/figures/Number_figures/02_fund_risk_return_scatter.png`

Purpose: investable funds, monthly walk-forward out-of-sample performance,
weights, metrics, and fact-sheet inputs.

## 03 - Sentiment And Fusion

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
- `results/figures/Number_figures/03_sector_sentiment_index.png`
- `results/figures/Number_figures/03_sector_sentiment_ranking.png`
- `results/figures/Number_figures/03_market_fear_greed_index.png`
- `results/figures/Number_figures/03_fusion_growth_comparison.png`
- `results/figures/Number_figures/03_fusion_drawdown_comparison.png`

Purpose: finance-extended VADER sentiment, sector fear/greed analytics, and
base-vs-sentiment-tilt fusion results.

## 04 - App Consumption Layer

- `results/data/app_data_manifest.csv`
- `results/tables/app_table_manifest.csv`
- `results/figures/app_page_data_map.png`
- `results/data/Number_data/04_app_data_manifest.csv`
- `results/tables/Number_tables/04_app_table_manifest.csv`
- `results/figures/Number_figures/04_app_page_data_map.png`

Purpose: documents which canonical `results/` artifacts are read by
`streamlit_app.py`. Stage 04 does not create new model data; it consumes
precomputed files from stages 02 and 03 so the app stays light and does not
rerun VADER or backtests at runtime. The unnumbered files are canonical; the
`04_` files under `Number_*` are matching stage-labelled copies.

## 05 - Report And Submission Support

- `results/figures/report_combined_asset_class_weights.png`
- `results/figures/report_projectb_workflow_data_flow.png`
- `results/data/report_data_manifest.csv`
- `results/tables/report_table_manifest.csv`
- `results/tables/numbered_file_integrity_audit.csv`
- `results/data/Number_data/05_report_data_manifest.csv`
- `results/tables/Number_tables/05_report_table_manifest.csv`
- `results/tables/Number_tables/05_numbered_file_integrity_audit.csv`
- `results/figures/Number_figures/05_report_combined_asset_class_weights.png`
- `results/figures/Number_figures/05_report_projectb_workflow_data_flow.png`

Purpose: report-supporting exhibits. `report_combined_asset_class_weights.png`
compares Combined fund Equity/Crypto weights over time across the four portfolio
methods, making the course-required portfolio-weights-over-time exhibit clearer.
`report_projectb_workflow_data_flow.png` explains how raw market/news inputs,
ETL/features, funds, sentiment, fusion, canonical results, the Streamlit app,
the Word report, and AI workflow checks connect. The `05_` files are report-stage
copies or manifests to make final report evidence easy to identify.
`numbered_file_integrity_audit.csv` records the latest content-hash check
between numbered files and their unnumbered canonical counterparts.

A copy of `report_projectb_workflow_data_flow.png` is also saved under
`report/report_projectb_workflow_data_flow.png` so it is easy to find while
editing the Word report.

## Redesign - Report-Ready Figure Alternatives

PNG files are stored under `results/figures/Redesign/png/`.
PDF files are stored under `results/figures/Redesign/pdf/`.

- `results/figures/Redesign/png/02_combined_fund_drawdowns.png`
- `results/figures/Redesign/png/02_combined_risk_parity_weights.png`
- `results/figures/Redesign/png/02_fund_growth_of_1.png`
- `results/figures/Redesign/png/02_fund_risk_return_scatter.png`
- `results/figures/Redesign/png/02_fund_sharpe_barplot.png`
- `results/figures/Redesign/png/03_fusion_drawdown_comparison.png`
- `results/figures/Redesign/png/03_fusion_growth_comparison.png`
- `results/figures/Redesign/png/03_market_fear_greed_index.png`
- `results/figures/Redesign/png/03_sector_sentiment_index.png`
- `results/figures/Redesign/png/03_sector_sentiment_ranking.png`
- `results/figures/Redesign/png/04_app_page_data_map.png`
- `results/figures/Redesign/png/05_report_combined_asset_class_weights.png`
- `results/figures/Redesign/png/05_report_projectb_workflow_data_flow.png`
- `results/figures/Redesign/pdf/02_combined_fund_drawdowns.pdf`
- `results/figures/Redesign/pdf/02_combined_risk_parity_weights.pdf`
- `results/figures/Redesign/pdf/02_fund_growth_of_1.pdf`
- `results/figures/Redesign/pdf/02_fund_risk_return_scatter.pdf`
- `results/figures/Redesign/pdf/02_fund_sharpe_barplot.pdf`
- `results/figures/Redesign/pdf/03_fusion_drawdown_comparison.pdf`
- `results/figures/Redesign/pdf/03_fusion_growth_comparison.pdf`
- `results/figures/Redesign/pdf/03_market_fear_greed_index.pdf`
- `results/figures/Redesign/pdf/03_sector_sentiment_index.pdf`
- `results/figures/Redesign/pdf/03_sector_sentiment_ranking.pdf`
- `results/figures/Redesign/pdf/04_app_page_data_map.pdf`
- `results/figures/Redesign/pdf/05_report_combined_asset_class_weights.pdf`
- `results/figures/Redesign/pdf/05_report_projectb_workflow_data_flow.pdf`

Purpose: FT-inspired redesign alternatives for all numbered Stage 02-05 PNG
figures. The redesigned set keeps the original course/canonical files unchanged
and creates report-ready alternatives with clearer titles, source notes, axes,
tables, callouts, and diagram layouts. The PNG folder is for quick Word/report
insertion; the PDF folder is for high-quality archive or later conversion.
