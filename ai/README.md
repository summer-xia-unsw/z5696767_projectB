# AI Workflow Pack - NovaAlloc ProjectB

This folder records how AI was used for ProjectB. It is part of the graded AI Workflow and Transparency criterion.

## Files

- `project_step_log.md`: execution log. It records what was done, which files changed, what was produced, how it was verified, and what remains next.
- `00_prompt_log_template.md`: standard prompt-log template used for new entries.
- `01_prompt_log_data_foundation.md`: AI use for ETL/features migration and foundation outputs.
- `02_prompt_log_portfolios.md`: AI use for portfolio optimisation, out-of-sample backtests, fund returns, weights, metrics, and figures.
- `03_prompt_log_sentiment_fusion.md`: AI use for VADER-style sentiment, sector sentiment index, market fear/greed analytics, and sentiment fusion.
- `04_prompt_log_app.md`: AI use for Streamlit app implementation, local checks, UI revisions, and app documentation.
- `05_prompt_log_report_submission.md`: AI use for output guides, report writing, figure redesign, final hand-in checks, GitHub, Streamlit deployment, and submission planning.
- `06_prompt_log_self_correction.md`: AI self-correction log. It records requirement re-audits, AI-related mistakes or risks, report fixes, and remaining manual submission actions.

## Standard Entry Format

Each numbered prompt log uses the same structure:

- Objective
- Prompt Summary
- Assistant Output
- Risk/Issue
- Student Decision
- Verification
- Current Status

The project step log uses one table with these columns:

- Step
- Date
- Task
- Work Completed
- Files or Outputs
- Verification
- Next Step

## Rules Followed

- `AGENTS.md` at the project root is the active AI rule file for Codex-style work.
- Logs must be honest: they record mistakes, corrections, and checks, not only successful outputs.
- The 06 log is reserved for self-correction evidence after major audits.
- Written economic interpretation in the report must be reviewed and rewritten in the student's own words.
- The deployed app must read precomputed `results/` artifacts and must not run VADER or backtests at runtime.
- Final Part B submission requires a Moodle ZIP, a public GitHub repository link, and a public Streamlit app URL.
