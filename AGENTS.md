# AGENTS.md

## Scope
- This repository contains multiple areas, but the primary active scope is the `finance` package.
- Unless the user explicitly asks otherwise, treat `financial_advisor` as out of scope.
- Use `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md` as the primary package context document for `finance`.
- Use `.note/finance/WORK_PROGRESS.md` as the running implementation log for `finance` work.
- Use `.note/finance/QUESTION_AND_ANALYSIS_LOG.md` as the running note file for user questions, requirement interpretation, and analysis summaries.

## Working Model
- Treat this project as a quant research workspace with two connected domains:
  - data ingestion and persistence
  - strategy research and backtesting
- Before changing code, identify which domain the task belongs to:
  - `finance/data/*`, `finance/data/db/*`: ingestion, schema, persistence
  - `finance/engine.py`, `finance/transform.py`, `finance/strategy.py`, `finance/performance.py`, `finance/display.py`, `finance/visualize.py`: backtest and analysis

## Note Rules
- Keep long-lived project notes under the top-level `.note/` directory, not inside package subdirectories.
- For `finance` work, prefer `.note/finance/` as the canonical note location.
- Store durable analysis, architecture notes, question summaries, and implementation progress as Markdown files in `.note/finance/`.
- Keep cross-phase documents at `.note/finance/` root.
- Prefer phase-specific execution/planning docs under:
  - `.note/finance/phase1/`
  - `.note/finance/phase2/`
  - `.note/finance/phase3/`
  and continue the same pattern for later phases.

## Progress Logging Rules
- For non-trivial `finance` work, update `.note/finance/WORK_PROGRESS.md` as work progresses.
- At minimum, record:
  - task start
  - major implementation milestones
  - important design decisions
  - completion status
- Keep entries concise, dated, and implementation-focused.
- Do not overwrite history; append new entries.

## Question and Analysis Logging Rules
- When the user asks for analysis, design guidance, architecture review, or feature planning related to `finance`, record the durable outcome in `.note/finance/QUESTION_AND_ANALYSIS_LOG.md`.
- Capture:
  - the user request topic
  - the interpreted goal
  - the main analysis result
  - any important follow-up decisions
- Summarize the durable result, not the full conversation transcript.

## Documentation Rules
- When a `finance` feature is added, changed, or finalized, update `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`.
- If the change is narrow and localized, update only the affected sections instead of rewriting the full document.
- If a change affects package purpose, data flow, DB tables, strategy behavior, or architectural boundaries, reflect that explicitly in the document.
- Keep the document aligned with the current code, not intended future design.
- If analysis documents were previously stored under `finance/docs`, prefer the `.note/finance/` location going forward.
- Use `.note/finance/MASTER_PHASE_ROADMAP.md` as the top-level phase roadmap.
- Use `.note/finance/FINANCE_DOC_INDEX.md` as the top-level index into finance documents.
- Use `.note/finance/FINANCE_TERM_GLOSSARY.md` as the shared glossary for recurring quant / backtest / real-money terminology.
- For phase plans, policy documents, validation rules, or real-money guidance documents, do not leave key terms as compressed jargon only.
- When a document introduces important operator-facing concepts such as universe contract, investability, turnover/cost, guardrails, or promotion criteria, add short plain-language explanations.
- Prefer a structure like:
  - what this means
  - why it matters
  so future phase documents remain understandable without requiring prior conversation context.
- When a recurring term starts appearing across multiple phase documents or UI discussions, add it to `.note/finance/FINANCE_TERM_GLOSSARY.md` instead of leaving its explanation only in chat.
- Prefer glossary entries to include:
  - `기본 설명`
  - `왜 사용되는지`
  - `예시 / 필요 상황`
- Keep the policy/technical precision, but write those documents so a future reader can understand them on first pass.

## Phase Management Rules
- Manage major `finance` work through named phases rather than ad hoc task lists.
- Before starting a substantial new workstream, decide which phase it belongs to.
- Maintain:
  - one top-level roadmap document for the whole project
  - one or more phase/chapter TODO board documents for current execution
- When a phase is active, keep its TODO board updated with:
  - grouped work areas
  - `pending` / `in_progress` / `completed` status
  - short explanations for each subtask
- If scope changes during a phase, update the phase document and TODO board rather than leaving the change only in chat.
- Before opening a new major phase, confirm the new phase direction with the user.
- When a phase reaches a practical completion point, create a phase-specific manual test checklist document under `.note/finance/phase*/`.
- The checklist should be written for user-facing verification and should cover the major features, UI paths, and validation points added during that phase.
- When sharing phase completion, include the checklist document in the final handoff so the user has a concrete test plan.
- When a phase reaches practical completion, also review the project’s durable workflow guidance and references for staleness.
- At minimum, check whether newly implemented behavior should update:
  - `AGENTS.md`
  - finance skills / `SKILL.md` instructions that are actively used for this repository
  - `.note/finance/FINANCE_DOC_INDEX.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - phase-specific reference or preparation documents
- If newly added workflows, defaults, validation rules, or operator practices changed how work should be executed in future turns, refresh those guidance/reference documents during phase closeout rather than leaving the update only in chat.
- If the review concludes that no skill/reference update is needed, record that outcome briefly in the phase closeout notes or progress log.
- Keep the project centered on the two primary product goals:
  - data collection
  - backtesting
- Treat the long-term product target as:
  - user-defined portfolio construction
  - multiple strategy implementations
  - backtest execution
  - return/risk/result visualization

## Database Rules
- When adding or changing persistence behavior, inspect `finance/data/db/schema.py` first.
- If a new table or column is introduced, update both:
  - schema definitions in `finance/data/db/schema.py`
  - the package analysis document in `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Prefer explicit UPSERT-based ingestion patterns consistent with existing `upsert_*` and `store_*` functions.
- Keep MySQL write paths idempotent where possible.

## Quant/Data Integrity Rules
- For financial statements, factors, and backtests, always consider:
  - point-in-time correctness
  - look-ahead bias risk
  - survivorship bias risk
- If a change uses accounting data in a strategy or factor workflow, check whether the logic is using `period_end` or actual filing/acceptance timing.
- Do not assume provider fields are stable or complete; verify fallback logic when extending yfinance- or EDGAR-based pipelines.

## Strategy Rules
- New strategies should fit the existing separation:
  - preprocessing in `finance/transform.py`
  - simulation logic in `finance/strategy.py`
  - orchestration in `finance/engine.py`
- If a strategy requires new inputs, prefer adding reusable transform functions before embedding preprocessing inside the strategy.
- Keep strategy outputs compatible with existing performance analysis where practical, especially:
  - `Date`
  - `Total Balance`
  - `Total Return`

## Sample and Usage Rules
- If a new core strategy or ingestion workflow is added, update `finance/sample.py` or add an equivalent usage example unless there is a clear reason not to.
- Treat `finance/sample.py` as example-plus-smoke-test code, not as the main architecture boundary.

## Configuration Rules
- Avoid introducing new hardcoded credentials or environment-specific constants.
- If touching existing hardcoded DB settings, prefer moving the code toward configurable inputs without doing unrelated refactors.

## Commit Rules
- After finishing a distinct implementation unit, create a git commit unless the user explicitly asks not to.
- Group commits by coherent feature, phase milestone, or workstream rather than one oversized commit.
- Commit messages should make the change easy to understand later:
  - use a short subject line
  - and include a concrete description of what changed and why in the commit log when appropriate
- Do not include generated artifacts, run histories, local experiment CSVs, notebook scratch files, or other machine-local outputs unless the user explicitly asks for them.

## Change Review Checklist
- Does this change affect data source boundaries?
- Does this change affect DB schema or table meaning?
- Does this change alter strategy inputs, outputs, or assumptions?
- Does this change require documentation sync in `FINANCE_COMPREHENSIVE_ANALYSIS.md`?
- If this phase is closing or handing off, does it require a phase-specific manual test checklist document?
- If this phase is closing or handing off, do `AGENTS.md`, active skills, roadmap/index docs, or phase reference docs need to be refreshed to reflect the implemented workflow?
- Does this change require an appended entry in `WORK_PROGRESS.md`?
- Does this change produce durable design or analysis knowledge that belongs in `QUESTION_AND_ANALYSIS_LOG.md`?
- Does this change introduce any point-in-time or survivorship bias risk?
