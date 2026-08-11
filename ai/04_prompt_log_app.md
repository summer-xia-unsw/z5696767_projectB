# Prompt Log 04 - Streamlit App

Purpose: record AI assistance used to build, test, and maintain the ProjectB Streamlit app. Report writing and final submission records belong in `05_prompt_log_report_submission.md`.

## Stage Status

Status: completed for the current local app build.

`streamlit_app.py` reads precomputed `results/` artifacts only. It does not recompute portfolio optimisation, VADER sentiment, or fusion backtests at runtime.

Current main navigation:

- `Overview`
- `Funds`
- `Allocation`
- `Sentiment`
- `Fusion`
- `Data Health`

## Final Outputs

- `streamlit_app.py` - root Streamlit entrypoint.
- `tests/test_app.py` - Streamlit smoke/navigation tests.
- `.streamlit/config.toml` - Streamlit config.
- `.streamlit/00_local_app_interface_guide.docx` - Chinese user guide for local app pages.

## Entry 1 - Add numbered output copies for easier reading

### Objective
Make `results/data`, `results/tables`, and `results/figures` easier to read by adding stage prefixes such as `01_`, `02_`, and `03_`.

### Prompt Summary
The student asked to classify generated data and figures by stage so the output folders would be easier to understand.

### Assistant Output
The assistant updated `scripts/run_part_b.py` to keep canonical course filenames and also create numbered reading copies. It also generated `results/OUTPUT_INDEX.md`.

### Risk/Issue
Renaming required files would break `scripts/check_handin.py` and app loading.

### Student Decision
Keep canonical files for code and checks. Use numbered copies only for human reading.

### Verification
`check_handin.py` passed, with only the report PDF reminder at that time.

### Current Status
Complete. Numbered copies now support interpretation without breaking runtime paths.

## Entry 2 - Revert archive-folder organisation

### Objective
Undo the earlier idea of moving unnumbered results into `original_*` folders.

### Prompt Summary
The student said the archive-folder approach felt unsuitable and asked to return to the previous state.

### Assistant Output
The assistant restored files to the main results folders, removed `original_data`, `original_tables`, and `original_figures`, and kept the numbered reading copies.

### Risk/Issue
Archive folders made the project harder to understand and could confuse app paths.

### Student Decision
Use a simpler structure: canonical files in the root results folders and numbered files for reading support.

### Verification
`check_handin.py` passed.

### Current Status
Complete.

## Entry 3 - Build local Streamlit app from precomputed results

### Objective
Build the local Streamlit app according to the course requirements before online deployment.

### Prompt Summary
The student asked to build the local app according to `course_requirements`.

### Assistant Output
The assistant replaced the starter app with a NovaAlloc dashboard containing Overview, Funds, Allocation, Sentiment, Fusion, and Data Health pages. It added Streamlit tests in `tests/test_app.py`.

### Risk/Issue
The starter app had TODO messages and did not support the required investor journey. A deployed app must not recompute backtests or run VADER at runtime.

### Student Decision
Load canonical unnumbered files from `results/data` and `results/tables`. Keep heavy computation in `scripts/run_part_b.py`.

### Verification
Commands used:

```powershell
..\..\.venv\Scripts\python.exe -m py_compile streamlit_app.py
..\..\.venv\Scripts\python.exe -m pytest tests -q
..\..\.venv\Scripts\python.exe scripts\check_handin.py
```

The local app returned HTTP 200 during testing.

### Current Status
Complete.

## Entry 4 - Fix navigation display on smaller screens

### Objective
Fix the issue where the top navigation tabs were not fully visible.

### Prompt Summary
The student shared screenshots and asked to fix the incomplete top navigation bar.

### Assistant Output
The assistant replaced top `st.tabs` with a sidebar `st.radio` navigation menu.

### Risk/Issue
Top tabs can be squeezed on narrow screens, making pages appear missing.

### Student Decision
Use sidebar navigation for a stable app journey.

### Verification
`pytest tests -q` passed. The local app returned HTTP 200 at `http://127.0.0.1:8501`.

### Current Status
Complete.

## Entry 5 - Generate local app interface Word guide

### Objective
Create a Word guide explaining the local app URL and the purpose of each page.

### Prompt Summary
The student asked for a Word document under `.streamlit` that explains each local app page.

### Assistant Output
The assistant generated `.streamlit/00_local_app_interface_guide.docx`.

### Risk/Issue
The user could misunderstand `localhost` as a permanent online URL or misunderstand each page's role.

### Student Decision
Keep this as a user-facing explanation document only; do not make it part of app runtime.

### Verification
The `.docx` structure was valid and extracted text had `triple_question=0`.

### Current Status
Complete.

## Entry 6 - Add redesigned report figures to the app, then simplify the design

### Objective
Initially add redesigned report figures to the app, then correct the UI when the page felt like an internal file-management page.

### Prompt Summary
The student first asked to add the latest redesigned figures into the app and provide a link. Later, the student reported UI problems and said the `Report Figures` page was hard to understand.

### Assistant Output
The assistant first added a `Report Figures` page that read 13 PNG/PDF pairs from `results/figures/Redesign/`. After the student's feedback, it removed `Report Figures` from main navigation and moved the figure check into a collapsed `Data Health` section called `Report figure files - audit only`. The Overview KPI row was also redesigned so `OOS test window` no longer truncates.

### Risk/Issue
`Report Figures` was not a real investor workflow page. Leaving it in main navigation weakened the product story and made the app look like a file browser. The default Streamlit metric card also truncated the OOS date range.

### Student Decision
Use six main pages only: Overview, Funds, Allocation, Sentiment, Fusion, and Data Health. Keep report figure checks as reproducibility/audit content inside Data Health.

### Verification
Commands used:

```powershell
..\..\.venv\Scripts\python.exe -m py_compile streamlit_app.py
..\..\.venv\Scripts\python.exe -m pytest tests -q
..\..\.venv\Scripts\python.exe scripts\check_handin.py
```

Results:

- `pytest tests -q`: `5 passed`.
- After deleting `__pycache__`, `check_handin.py`: `23 checks passed`.
- Local app returned HTTP 200 at `http://127.0.0.1:8501`.

### Current Status
Complete. The app is ready for final local review and later Streamlit Cloud deployment.
