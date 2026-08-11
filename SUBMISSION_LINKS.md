# ProjectB Submission Links

Student folder: `z5696767_projectB`

## Public Links

- GitHub repository: <https://github.com/summer-xia-unsw/z5696767_projectB>
- Live Streamlit app: <https://novaalloc.streamlit.app>

## Key Files In This ZIP

- Report PDF: `report/report.pdf`
- Report Word source: `report/report.docx`
- Streamlit entrypoint: `streamlit_app.py`
- App configuration: `.streamlit/config.toml`
- AI workflow evidence: `AGENTS.md` and `ai/`
- Required app artifacts:
  - `results/data/fund_returns.csv`
  - `results/data/fund_weights.csv`
  - `results/data/sector_sentiment_index.csv`
  - `results/tables/performance_metrics.csv`

## Deployment Notes

The deployed Streamlit app reads precomputed CSV artifacts from `results/`.
It does not recompute portfolio backtests or sentiment scoring at runtime.

The public app was deployed from the GitHub `main` branch with entrypoint
`streamlit_app.py`.
