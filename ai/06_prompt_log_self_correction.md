# 06 Prompt Log - AI Self-Correction

Purpose: record the final AI self-correction pass after re-reading the official ProjectB brief and checking whether the report, app evidence, and AI workflow pack still match the marking standard.

Stage: 06 - Self-correction and requirement audit
Date: 2026-08-11
Status: current correction pass completed. `report/report.pdf` has been exported and the public GitHub repository has been pushed. Final student-controlled tasks still remain: deploy the Streamlit app, open the public URL in a logged-out browser, and submit the Moodle ZIP plus links.

## Entry 1 - Re-audit the report against the ProjectB brief

### Objective

Check `report/report.docx` against `course_requirements/project_brief_FINS5545.pdf` before final submission and identify content that could lose marks.

### Prompt Summary

The student asked the assistant to read the ProjectB brief, inspect the report against the marking standard, modify the report where needed, and create a new 06 log that records AI self-correction.

### Assistant Output

The assistant extracted the official brief from the PDF and checked the report for:

- required fund exhibits
- sentiment index and fusion evidence
- Streamlit investor journey
- public GitHub and live Streamlit deployment requirements
- `report/report.pdf` submission requirement
- AI workflow transparency and correction evidence

The report already contained the required fund, sentiment, fusion, and app exhibits. The main weakness was not the modelling content, but the audit trail: the report did not yet name the new 06 self-correction log and did not clearly explain how AI-related risks were corrected.

### Risk/Issue

If the report only says that AI logs exist, it may look like passive documentation rather than critical AI workflow evidence. The rubric gives 20% to AI Workflow and Transparency, so the report and logs should show where AI output was checked, corrected, and limited.

### Student Decision

Keep the modelling outputs unchanged because they already match the required exhibits. Add targeted report text and a separate 06 log to make the AI correction process explicit.

### Verification

The report inspection found:

- 6 tables
- 12 images
- required output filenames present in report tables
- no `TODO`, `TBD`, `HUMAN EDIT`, or repeated question-mark placeholders
- no remaining main-navigation reference to the removed `Report Figures` page

### Current Status

Completed for this correction pass.

## Entry 2 - Correct report wording on deployment and localhost risk

### Objective

Clarify that the local Streamlit command is not the final submission artifact.

### Prompt Summary

The course brief requires a public GitHub repository and a live Streamlit URL for Part B. Earlier project discussion had used `http://127.0.0.1:8501` for local testing, which could confuse development checks with submission evidence.

### Assistant Output

The assistant inserted a paragraph into Section 6 of `report/report.docx` explaining that:

- the local app command is only a development check
- final grading needs a live Streamlit Community Cloud URL
- deployment should use `streamlit_app.py` from the ProjectB root
- the GitHub repository must be public at hand-in
- the app should support compare funds, fact sheets, allocations, and sentiment analytics without rerunning the research pipeline

### Risk/Issue

Submitting a localhost URL, a private GitHub repository, or an app that rebuilds VADER/backtests at runtime would fail or weaken the Station 4 implementation requirement.

### Student Decision

Keep the report honest: local testing is complete, but public deployment and the final URL are still student-controlled final tasks.

### Verification

The revised report now includes explicit wording on:

- live Streamlit Community Cloud URL
- public GitHub repository at hand-in
- `streamlit_app.py` as the app entrypoint
- precomputed `results/` artifacts as runtime inputs

### Current Status

Completed in `report/report.docx`.

## Entry 3 - Correct AI workflow transparency evidence

### Objective

Record AI mistakes, risks, and corrections in a dedicated log rather than hiding them inside general progress notes.

### Prompt Summary

The student wanted a 06-stage AI log whose purpose is to show AI self-correction.

### Assistant Output

The assistant created `ai/06_prompt_log_self_correction.md` and updated the report appendix to reference it. The log records the main AI-related correction themes:

- Word guide encoding problems were detected and repaired instead of accepted.
- A report image-count regression was detected after figure replacement and repaired.
- The `Report Figures` app page was removed from the main navigation because it was an internal audit view, not an investor journey page.
- Localhost testing was separated from final public Streamlit deployment.
- The missing `report/report.pdf` remains a manual export task rather than being falsely marked complete.

### Risk/Issue

Without a separate correction log, AI use can look like a list of outputs rather than a controlled workflow. This would be weaker against the AI transparency rubric.

### Student Decision

Use `06_prompt_log_self_correction.md` as the final audit log. Earlier numbered logs remain stage-generation logs; this file is specifically for correction evidence.

### Verification

The assistant updated:

- `report/report.docx`
- `ai/06_prompt_log_self_correction.md`
- `ai/README.md`
- `AGENTS.md`
- `ai/project_step_log.md`

Further verification is recorded in the project step log.

### Current Status

Completed for this correction pass.

## Entry 4 - Verification after self-correction

### Objective

Check that the self-correction edits did not break the report, app, or AI workflow pack.

### Prompt Summary

After the report and AI logs were updated, the assistant ran the mechanical checks again and recorded both successful checks and remaining limitations.

### Assistant Output

The assistant ran:

- `python scripts/check_handin.py`
- `python -m pytest tests -q`
- `python ..\..\tools\workflow.py word-report report\report.docx`
- `python ..\..\tools\workflow.py proofread report\report.docx`
- a custom `python-docx` inspection of `report/report.docx`
- a custom AI-log text-quality check
- the Documents render workflow for Word visual QA

### Risk/Issue

The automated Word visual render could not complete because the local machine does not have LibreOffice/`soffice` installed. This means terminal-based page rendering could not be verified here.

### Student Decision

Do not claim visual Word QA as complete through the terminal. At this point in the workflow, PDF export was still a manual final step in Word.

### Verification

Results from this pass:

- `check_handin.py`: 23 checks passed.
- `pytest`: 5 tests passed.
- `proofread`: 0 doubled-word, spacing, reference, or placeholder findings.
- `report/report.docx`: 103 paragraphs, 6 tables, 12 images after editing.
- Report text now includes `ai/06_prompt_log_self_correction.md`, public GitHub wording, live Streamlit Community Cloud wording, `streamlit_app.py`, and `report/report.pdf`.
- AI markdown logs have 0 replacement characters, 0 repeated question-mark placeholders, and 0 Chinese characters after the English-standardisation pass.
- Documents render: failed because LibreOffice/`soffice` was not found.

### Current Status

At this point in the workflow, the project passed code/app/hand-in mechanical checks. Later entries record the manual PDF export and public GitHub upload. The remaining final actions after Entry 6 are Streamlit deployment, logged-out public URL validation, Moodle ZIP upload, and submission of the public GitHub and Streamlit links.

## Entry 5 - Strengthen innovation and critical reflection after professor-style critique

### Objective

Revise the report after an independent marker-style review found that the innovation and critical-reflection sections were too short for their rubric weight.

### Prompt Summary

The student asked the assistant to modify `report/report.docx`, focusing on two high-risk findings:

- the innovation section was too short to support the 30% Innovation and Data-Driven Results criterion
- the critical-reflection section was too thin and read more like a checklist than a graduate-level interpretation

### Assistant Output

The assistant rewrote only Sections 7 and 8 of `report/report.docx`.

Section 7 now presents four evidence-backed contributions:

- the 12-fund product menu across equity, crypto, and combined universes
- the finance-aware sentiment index built from 146,830 headlines
- the look-ahead-safe sentiment fusion test with a reported negative result
- the redesigned figure system and Streamlit implementation as product evidence

Section 8 now explains why the results behaved as they did:

- simple diversification and risk parity were more reliable than maximum-Sharpe estimation
- crypto had high growth but drawdowns above 80%, so it is unsuitable as a core retail product
- the sentiment tilt likely failed because daily headline tone did not map cleanly into monthly allocation decisions
- sector aggregation, varying headline coverage, and an already defensive base fund limited the value of the tilt

The three recommendations were also made more specific and tied to product launch, sentiment validation, and governance.

### Risk/Issue

The previous report had the required exhibits, but the written argument under-used them. A marker could see the outputs as a competent baseline rather than a clearly argued original extension. The recommendations also risked sounding generic because they did not explain the economic reason behind each action.

### Student Decision

Keep all modelling outputs unchanged. Strengthen only the economic interpretation and rubric-facing argument.

### Verification

After editing:

- Section 7 increased from about 241 words to about 581 words.
- Section 8 increased from about 217 words to about 613 words.
- Full report text is about 4,747 word-like tokens including tables.
- `report/report.docx` still has 6 tables and 12 images.
- No `TODO`, `TBD`, `HUMAN EDIT`, or repeated question-mark placeholders were detected.
- Banned AI-style words checked in this pass were not found in the revised document.
- `proofread`: 0 findings.
- `check_handin.py`: 23 checks passed after auto-generated cache files were removed.
- Documents render still failed because LibreOffice/`soffice` is not installed on this machine.

### Current Status

Completed. The next step is to manually inspect the Word layout and export `report/report.pdf`.

## Entry 6 - Push final ProjectB folder to public GitHub repository

### Objective

Upload the completed ProjectB folder to the public GitHub repository required for Part B submission.

### Prompt Summary

The student created an empty public GitHub repository named `z5696767_projectB` and asked the assistant to run the local Git commands needed to upload the project.

### Assistant Output

The assistant initialized an independent Git repository inside `fins2026/z5696767_projectB`, committed the full project folder, connected it to `https://github.com/summer-xia-unsw/z5696767_projectB.git`, and pushed the `main` branch.

The initial pushed commit was:

- `1dae2d5 Initial ProjectB submission`

### Risk/Issue

The main risk was accidentally pushing the parent `fins-agent` repository instead of the standalone ProjectB folder. The assistant checked that `z5696767_projectB` did not already contain its own `.git` folder, initialized the repo inside the ProjectB directory only, and set the remote to the student's new repository.

### Student Decision

Use the GitHub repository as the public Part B code repository and keep `streamlit_app.py` at the repository root for Streamlit deployment.

### Verification

Verification after push:

- GitHub repository URL: `https://github.com/summer-xia-unsw/z5696767_projectB`
- Visibility: `PUBLIC`
- Default branch: `main`
- Remote branch: `origin/main`
- Required report file found remotely: `report/report.pdf`
- Required app/data files found remotely: `streamlit_app.py`, `requirements.txt`, `.streamlit/config.toml`, `results/data/fund_returns.csv`, `results/data/fund_weights.csv`, `results/data/sector_sentiment_index.csv`, and `results/tables/performance_metrics.csv`
- Local `check_handin.py`: 23 checks passed

### Current Status

GitHub upload is complete. The remaining final actions are Streamlit Community Cloud deployment, logged-out public URL validation, Moodle ZIP upload, and submission of the public GitHub and Streamlit links.

## Remaining Manual Student Actions

- Confirm the final GitHub repository remains public: `https://github.com/summer-xia-unsw/z5696767_projectB`.
- Deploy `streamlit_app.py` on Streamlit Community Cloud.
- Open the live app URL in a logged-out browser before submission.
- Submit the Moodle ZIP, public GitHub URL, and live Streamlit URL.
