# Prompt Log 05 - Report, Figures, Output Guides, and Submission

Purpose: record AI assistance used to create report-supporting guides, write and revise the formal report, redesign figures, run hand-in checks, and plan final GitHub/Streamlit submission. Streamlit app implementation belongs in `04_prompt_log_app.md`.

## Stage Status

Status: report DOCX and app are complete for the current build. Final submission still requires the student to manually export `report/report.pdf`, create/push the GitHub repository, deploy on Streamlit Cloud, and submit the Moodle ZIP plus links.

## Final Outputs

- `report/report.docx` - formal Word report source.
- `report/report_projectb_workflow_data_flow.png` - report-side copy of workflow chart.
- `results/figures/Redesign/png/` - 13 redesigned PNG figures.
- `results/figures/Redesign/pdf/` - 13 redesigned PDF figures.
- `results/data/Number_data/00_data_output_guide.docx` - numbered data guide.
- `results/tables/Number_tables/00_tables_output_guide.docx` - numbered table guide.
- `results/figures/Number_figures/00_figures_output_guide.docx` - numbered figure guide.

## Entry 1 - Generate and repair results output guides

### Objective
Create Word guide documents explaining output folders, then repair Chinese encoding issues and simplify the guides for quick reading.

### Prompt Summary
The student asked for Word guides under `results/data`, `results/tables`, and `results/figures`, then reported question-mark encoding problems, and later asked to focus only on numbered `01_`, `02_`, and `03_` outputs.

### Assistant Output
The assistant created and later regenerated output guide documents, eventually converting them into quick guides explaining numbered stage outputs and their purpose.

### Risk/Issue
PowerShell pipeline encoding corrupted Chinese text into question marks. The first guide also over-explained duplicate canonical and numbered files.

### Student Decision
Regenerate Word files through UTF-8 Python scripts and focus the guide on quick understanding rather than full data dictionaries.

### Verification
Internal DOCX text checks reported `triple_question=0`. `check_handin.py` passed, with only the report PDF reminder at that time.

### Current Status
Complete.

## Entry 2 - Split app and report prompt logs

### Objective
Separate app work from report/submission work.

### Prompt Summary
The student asked to split `04_prompt_log_app_report` into separate `04` and `05` stages.

### Assistant Output
The assistant created `ai/04_prompt_log_app.md` and `ai/05_prompt_log_report_submission.md`, removed the combined file, and updated references in `ai/README.md` and `AGENTS.md`.

### Risk/Issue
A combined app/report log would make the final AI workflow harder to audit.

### Student Decision
Use `04` for app work and `05` for report/submission work.

### Verification
Files existed after the split and `check_handin.py` passed.

### Current Status
Complete.

## Entry 3 - Generate the first ProjectB Word report

### Objective
Create a formal Word report that follows the Part B course requirements.

### Prompt Summary
The student asked to begin the report stage and generate a Word version according to `course_requirements`.

### Assistant Output
The assistant generated `report/report.docx`, covering product design, funds and OOS backtest design, fund factsheets, sentiment index, fusion, app journey, innovation, limitations, critical reflection, recommendations, references, and an appendix mapping required exhibits. It also generated `results/figures/report_combined_asset_class_weights.png` to support the required portfolio-weights-over-time exhibit.

### Risk/Issue
Risks included missing required exhibits, overclaiming sentiment performance, producing weak captions, leaving placeholders, or not creating a Word source file.

### Student Decision
Use the course-specific Part B structure and interpret the negative sentiment fusion result directly rather than hiding it.

### Verification
Structural checks found `report/report.docx`, 6 Word tables, 8 images in the first version, about 2,702 words, no question-mark corruption, no TODO markers, and no human-edit placeholders. `check_handin.py` passed at that stage.

### Current Status
Superseded by later report revisions and redesigned figures.

## Entry 4 - Generate workflow and data-flow chart

### Objective
Create a visual explanation of how ProjectB data flows through ETL, portfolios, sentiment, fusion, app, and report.

### Prompt Summary
The student asked for a flowchart explaining the overall process and how data files connect.

### Assistant Output
The assistant generated `results/figures/report_projectb_workflow_data_flow.png` and copied it to `report/report_projectb_workflow_data_flow.png`.

### Risk/Issue
The first flowchart draft was too dense. It needed separate lanes for price-return, news-sentiment, fusion, canonical results, and final products.

### Student Decision
Keep the clearer revised flowchart and preserve a copy in both `results/figures/` and `report/`.

### Verification
The PNG existed, dimensions were `2942 x 1737`, and `check_handin.py` passed.

### Current Status
Complete. The redesigned version later became Appendix Figure A1.

## Entry 5 - Add Stage 04/05 results markers and organise numbered folders

### Objective
Continue the numbered-output system for app and report stages and move numbered files into dedicated Number folders.

### Prompt Summary
The student asked to add `04` and `05` prefixes to data, table, and figure outputs, then asked to collect numbered files into `Number_data`, `Number_tables`, and `Number_figures`.

### Assistant Output
The assistant created app/report manifests, app page-data map, report figure copies, and moved all `00_` to `05_` files into Number folders. It also updated `scripts/run_part_b.py` and `results/OUTPUT_INDEX.md` so future numbered outputs go to the same Number folder structure.

### Risk/Issue
Moving canonical unnumbered files would break `streamlit_app.py` and `check_handin.py`.

### Student Decision
Move only files beginning with two digits and an underscore. Keep canonical files in the main results folders.

### Verification
Checked that root results folders had no numbered files, Number folders contained the expected files, `pytest` passed, caches were cleaned, and `check_handin.py` returned `23 checks passed`.

### Current Status
Complete.

## Entry 6 - Verify numbered files against canonical files and clean results

### Objective
Check whether numbered files match the canonical files and remove only useless temporary files.

### Prompt Summary
The student asked to verify consistency between Number folders and outer canonical files, then clean blank or useless data while preserving `.gitkeep` files.

### Assistant Output
The assistant compared numbered/canonical files by size and SHA256 hash, added missing canonical support files where appropriate, created `numbered_file_integrity_audit.csv`, removed a zero-byte mistaken file and Word lock files, and preserved `.gitkeep` placeholders.

### Risk/Issue
Deleting canonical files would break the app, report, and hand-in checker. Deleting `.gitkeep` files would remove intended placeholder files.

### Student Decision
Delete only temporary or clearly erroneous files. Keep canonical outputs and `.gitkeep` placeholders.

### Verification
Final audit found no missing or inconsistent mapped files, no unwanted zero-byte files except intended `.gitkeep`, no lock files, and `check_handin.py` returned `23 checks passed`.

### Current Status
Complete.

## Entry 7 - Update Number folder Word guides

### Objective
Update the `00_*_output_guide.docx` files inside Number folders to reflect the current `00` to `05` output structure.

### Prompt Summary
The student asked to update the `00` guides based on the current Numbered results.

### Assistant Output
The assistant regenerated:

- `results/data/Number_data/00_data_output_guide.docx`
- `results/tables/Number_tables/00_tables_output_guide.docx`
- `results/figures/Number_figures/00_figures_output_guide.docx`

### Risk/Issue
The guides could become stale after files were moved or cleaned.

### Student Decision
Keep the guides aligned with the actual folder structure and explain canonical-vs-numbered file relationships.

### Verification
The three Word guides had `triple_question=0`, covered stages `00` to `05`, and `check_handin.py` passed.

### Current Status
Complete.

## Entry 8 - Revise report after updated course requirements

### Objective
Revise `report/report.docx` after the student updated `course_requirements`, improving logical flow and course alignment.

### Prompt Summary
The student asked the assistant to review the updated course requirement files and revise the report so tables and figures connect logically rather than appearing as isolated descriptions.

### Assistant Output
The assistant revised the report to strengthen the path from funds to sentiment to fusion to app deployment. It added more explanation of VADER, the small finance lexicon extension, false-neutral finance headlines, 0-100 fear/greed scores, lagged z-score trading signals, and the negative fusion result.

### Risk/Issue
During one edit pass, image paragraph indexes shifted and three image paragraphs were accidentally replaced. The assistant detected this because the Word image count dropped from 8 to 5, then repaired the report by reinserting the missing figures.

### Student Decision
Keep the stronger course-focused narrative and preserve required figures. Treat the negative sentiment tilt as evidence and explain it honestly.

### Verification
After repair, the report had about 3,406 word tokens, 6 tables, 8 images, no question-mark corruption, no TODO markers, and no human-edit placeholders. The Word helper reported no proofread findings. `check_handin.py` passed.

### Current Status
Superseded by redesigned figure update.

## Entry 9 - Redesign report figures in a consistent FT-inspired style

### Objective
Improve report figure quality using a consistent, professional visual style and save both PNG and PDF versions.

### Prompt Summary
The student asked to redesign `02_combined_fund_drawdowns`, `02_combined_risk_parity_weights`, `02_fund_growth_of_1`, `02_fund_risk_return_scatter`, and then all remaining figures using the same professional logic.

### Assistant Output
The assistant created or updated redesign scripts:

- `scripts/redesign_combined_drawdowns.py`
- `scripts/redesign_combined_risk_parity_weights.py`
- `scripts/redesign_fund_growth_of_1.py`
- `scripts/redesign_fund_risk_return_scatter.py`
- `scripts/redesign_remaining_figures.py`

Generated output:

- 13 PNG files in `results/figures/Redesign/png/`
- 13 PDF files in `results/figures/Redesign/pdf/`

The redesigns used warm FT-inspired backgrounds, restrained grids, clearer percent axes, right-side scorecards, selective callouts, small multiples where helpful, and source/method notes.

### Risk/Issue
The figures could become visually crowded or inconsistent. Some early versions had label overlap and text overflow.

### Student Decision
Keep the redesigned suite as report-ready output while preserving original canonical figures.

### Verification
All 13 PNG and 13 PDF files were generated. Layout issues in the app page-data map and workflow chart were fixed after additional passes. Redesign scripts compiled, caches were removed, and `check_handin.py` returned `23 checks passed`.

### Current Status
Complete.

## Entry 10 - Update the Word report with redesigned figures

### Objective
Replace the report's original figures with redesigned figures and update captions, references, and appendix mapping.

### Prompt Summary
The student asked to update `report/report.docx` using the latest redesigned images.

### Assistant Output
The assistant updated `report/report.docx`, refreshed `report/report_projectb_workflow_data_flow.png`, and created `scripts/update_report_with_redesign_figures.py`. The report now includes 12 inline images, including new risk-return, sector-ranking, app page-data, and appendix workflow figures.

### Risk/Issue
Figure replacement can leave stale captions, duplicate media, broken references, or mismatched appendix exhibit mapping.

### Student Decision
Use the redesigned figures as the formal report visuals and update the written logic to connect Table 1 through Figures 1-5, sentiment exhibits, fusion comparison, app journey, and appendix workflow.

### Verification
Checks found `101` paragraphs, 6 tables, 12 inline images, 18 captions, 12 actual media files, no question-mark corruption, no TODO markers, no human-edit markers, and no stale fusion reference. `check_handin.py` returned `23 checks passed`. The repo `word-report` and `proofread` helpers reported no findings.

### Current Status
Complete, with one limitation: LibreOffice/`soffice` is not installed, so terminal-based Word-to-PNG visual QA could not be performed. The student still needs to open Word manually, check page breaks, and export `report/report.pdf`.

## Entry 11 - Clarify final submission, GitHub Public, and Streamlit deployment sequence

### Objective
Record the final hand-in requirement and clarify whether GitHub/Streamlit deployment happens after local work is complete.

### Prompt Summary
The student asked what must be submitted, how the app is uploaded, how to make the GitHub repo Public, and whether the correct sequence is to finish all local tasks first, then upload to GitHub and deploy to Streamlit.

### Assistant Output
The assistant reviewed `PROJECT_BRIEF.md`, `SUBMISSION_CHECKLIST.md`, `docs/STUDENT_DEPLOY.md`, and Streamlit deployment guidance. It confirmed that the final Part B submission requires:

- one Moodle ZIP of the full `z5696767_projectB` folder
- a public GitHub repository link
- a live public Streamlit app URL

The assistant also confirmed the correct sequence:

1. Finish all local work.
2. Check the local Streamlit app.
3. Export `report/report.pdf` from Word.
4. Run `scripts/check_handin.py`.
5. Make `z5696767_projectB` an independent GitHub repository.
6. Push the full project folder, including precomputed `results/` artifacts.
7. Set the GitHub repository to Public before hand-in.
8. Deploy `streamlit_app.py` from that repository on Streamlit Community Cloud.
9. Submit the Moodle ZIP, public GitHub link, and public Streamlit URL.

### Risk/Issue
The main risks are submitting a `localhost` URL, deploying from the parent `fins-agent` repository instead of the ProjectB folder, leaving the GitHub repo private at hand-in, forgetting to commit precomputed `results/` artifacts, or submitting without `report/report.pdf`.

### Student Decision
Treat GitHub and Streamlit as final deployment steps after the local report/app are complete. Do not submit `http://127.0.0.1:8501`; use the public `*.streamlit.app` URL generated by Streamlit Cloud.

### Verification
The assistant checked the current folder state:

- `z5696767_projectB` is not yet an independent Git repository.
- `gh` and `git` are installed locally.
- `check_handin.py` returned `23 checks passed`.
- `report/report.docx` exists.
- `report/report.pdf` was not found in the folder at the time of this check, so the student must export it from Word before final submission.

### Current Status
Deployment is not yet complete. The next required student actions are PDF export, independent GitHub repo creation/push, Streamlit Cloud deployment, public visibility checks, and Moodle submission.

