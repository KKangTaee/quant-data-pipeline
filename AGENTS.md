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
- When relevant local Codex skills are available, prefer the narrower primary skill before `finance-doc-sync`:
  - `finance-backtest-web-workflow` for `app/web/backtest_*.py`, Streamlit Backtest UI, Candidate Review, Portfolio Proposal, History, Candidate Library, and runtime JSONL UI helpers
  - `finance-phase-management` for phase open / TODO / checklist / roadmap status / manual QA / closeout work
  - `finance-doc-sync` for final documentation alignment after implementation or phase status changes
- When a workstream can be split into independent investigation tracks, use available sub-agents to explore them in parallel.
- If sub-agents are unnecessary for the current task, or the current session/tooling does not make them practical, continue directly instead of blocking work.
- Before changing code in `finance` or the Streamlit finance app, first check the current script responsibility map:
  - `.note/finance/code_analysis/SCRIPT_STRUCTURE_MAP.md`
  - then the matching detailed flow document under `.note/finance/code_analysis/`
  This is the default way to locate which script owns which behavior before editing.
- Before changing code, identify which domain the task belongs to:
  - `finance/data/*`, `finance/data/db/*`: ingestion, schema, persistence
  - `finance/engine.py`, `finance/transform.py`, `finance/strategy.py`, `finance/performance.py`, `finance/display.py`, `finance/visualize.py`: backtest and analysis

## Note Rules
- Keep long-lived project notes under the top-level `.note/` directory, not inside package subdirectories.
- For `finance` work, prefer `.note/finance/` as the canonical note location.
- Store durable analysis, architecture notes, question summaries, and implementation progress as Markdown files in `.note/finance/`.
- Keep cross-phase documents at `.note/finance/` root.
- Keep `.note/finance/` root focused on top-level maps, active logs, glossary, and templates.
- Put finance operations / runtime artifact / registry / data collection operating notes under `.note/finance/operations/`.
- Put durable finance research reference notes under `.note/finance/research/`.
- Put support-track planning, plugin, skill, and workflow automation notes under `.note/finance/support_tracks/`.
- Put machine-readable finance registry JSONL files under `.note/finance/registries/`.
- Put local finance run-history JSONL files under `.note/finance/run_history/`.
- Put reusable user-saved finance setup JSONL files under `.note/finance/saved/`.
- For machine-readable persistence of current strongest candidates and important near-miss scenarios, prefer `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl` as the default append-only registry unless the scope clearly expands into a broader experiment registry.
- For Pre-Live operating records after Real-Money review, use `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` as the append-only registry. Keep it separate from `CURRENT_CANDIDATE_REGISTRY.jsonl`: current candidate registry defines the candidate, pre-live registry records watchlist / paper tracking / hold / reject / re-review operating state.
- For Paper Portfolio Tracking records after robustness / stress review, use `.note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` as the append-only ledger. Keep it separate from `PORTFOLIO_PROPOSAL_REGISTRY.jsonl`: proposal registry defines the candidate bundle, paper ledger records tracking start date, target weights, benchmark, cadence, triggers, and Phase 34 handoff state.
- For durable backtest result reports whose primary purpose is to record:
  - tested strategy settings
  - result summaries
  - portfolio search outcomes
  - reproducible backtest guides
  prefer `.note/finance/backtest_reports/` as the canonical home.
- Keep phase execution documents in `.note/finance/phases/phase*/`, but if a result-oriented backtest note becomes reusable beyond that phase, prefer creating or moving the durable report into `.note/finance/backtest_reports/` and linking it from the phase document.
- For repeated strategy experimentation, maintain strategy-specific backtest logs under `.note/finance/backtest_reports/strategies/`.
- Preferred shape:
  - strategy hub: `STRATEGY.md`
  - strategy run log: `STRATEGY_BACKTEST_LOG.md`
- When a backtest result is meaningful enough to revisit later, append it to the matching strategy backtest log instead of leaving it only in chat.
- A strategy backtest log entry should capture at minimum:
  - goal
  - time period / universe
  - key settings
  - factor set or ticker set
  - result summary
  - interpretation / next action
- Prefer phase-specific execution/planning docs under:
  - `.note/finance/phases/phase1/`
  - `.note/finance/phases/phase2/`
  - `.note/finance/phases/phase3/`
  and continue the same pattern for later phases.
- For repeated `finance` backtest-refinement work, use the repo-local hygiene helper when it is relevant:
  - `python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- For current-candidate persistence or review, use the repo-local registry helper when it is relevant:
  - `python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py list`
  - `python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate`
- For Pre-Live candidate operating records, use the repo-local pre-live registry helper when it is relevant:
  - `python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py draft-from-current <registry_id>`
  - `python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py list`
  - `python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate`
- For user-facing Pre-Live operating records, use `Backtest > Candidate Review` to inspect current candidates, create Pre-Live records, and route eligible candidates toward Portfolio Proposal / later Live Readiness.
- For user-facing Paper Portfolio Tracking records, use `Backtest > Portfolio Proposal` to inspect the Validation Pack / Phase 33 handoff, explicitly save a paper ledger row, and review saved ledger records before Final Selection work.
- Default moments to run it:
  - after a meaningful refinement/document-sync unit
  - before commit
  - before phase closeout handoff
- Treat it as a support tool, not a blocker:
  - if the script is unavailable or not informative for the current diff, continue with manual review

## Progress Logging Rules
- For non-trivial `finance` work, update `.note/finance/WORK_PROGRESS.md` as work progresses.
- At minimum, record:
  - task start
  - major implementation milestones
  - important design decisions
  - completion status
- Keep entries concise, dated, and implementation-focused.
- Do not overwrite history; append new entries.
- Treat `.note/finance/WORK_PROGRESS.md` as the canonical active work log, not as an unbounded dump of every detail forever.
- Prefer keeping the root work log as:
  - current active workstream progress
  - high-signal milestones
  - durable handoff notes
- If the root work log becomes too large or a phase closes with substantial history, prefer archiving detailed history by phase rather than by month.
- Preferred archive shape:
  - keep `.note/finance/WORK_PROGRESS.md` as the top-level current log
  - move older detailed phase history into `.note/finance/phases/phase*/PHASE*_WORKLOG.md`
  - leave a short summary/pointer in the root log instead of deleting past context
- Do not split work logs by month unless the work is genuinely month-scoped and not phase-scoped. This repository is phase-managed, so phase-based archives are the default.

## Question and Analysis Logging Rules
- When the user asks for analysis, design guidance, architecture review, or feature planning related to `finance`, record the durable outcome in `.note/finance/QUESTION_AND_ANALYSIS_LOG.md`.
- Capture:
  - the user request topic
  - the interpreted goal
  - the main analysis result
  - any important follow-up decisions
- Summarize the durable result, not the full conversation transcript.

## Documentation Rules
- Keep the repository root `README.md` aligned with the current top-level product surface and real entry points.
- When a feature or workflow change materially affects:
  - what the project does
  - how the main console is navigated
  - how the app is started
  - which user-facing capabilities are now available
  update `README.md` in the same work unit rather than leaving the summary stale.
- When a `finance` feature is added, changed, or finalized, review whether `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md` needs an update.
- Treat `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md` as the high-level current-state map for the finance system, not as an append-only implementation log.
- Update `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md` only when the change alters how a future reader should understand the current system structure, for example:
  - package purpose or product surface
  - major system layers or architectural boundaries
  - data flow, DB source-of-truth, or table meaning at a summary level
  - strategy family structure, runtime behavior, or Backtest UI workflow at a summary level
  - Real-Money, Pre-Live, promotion, guardrail, or other operator-facing concept boundaries
  - phase results that materially change the current system map
- Do not add one-off backtest results, phase progress notes, detailed call flows, table-by-table details, small UI copy changes, or minor bug-fix notes to `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`.
- If the change is narrow but does affect the current-state map, update only the affected sections instead of rewriting the full document.
- Keep the document aligned with the current code and implemented workflow. Mark future plans explicitly as future work.
- Use `.note/finance/code_analysis/` for developer-facing code flow documents.
- Keep `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md` as the high-level system map, and put detailed code modification flow in `.note/finance/code_analysis/`.
- Keep `.note/finance/code_analysis/SCRIPT_STRUCTURE_MAP.md` as the quick script responsibility map. When a code change adds a new script, renames or moves a script, splits a module, or materially changes what a script is responsible for, update this map in the same work unit.
- When code changes add or materially alter runtime flow, DB/loader flow, Backtest UI flow, strategy implementation flow, or repo-local automation scripts, update the matching `.note/finance/code_analysis/*.md` document.
- Do not update code analysis documents for small copy changes, one-off backtest results, or phase status updates unless the durable code flow changed.
- Use `.note/finance/data_architecture/` for data / DB architecture documents.
- Keep DB and table meaning, data flow, table semantics, PIT notes, look-ahead risk, survivorship risk, and stale data interpretation under `.note/finance/data_architecture/`.
- When a finance change adds or materially changes DB tables, schema meaning, ingestion sources, loader source-of-truth, PIT timing, or table semantics, update the matching `.note/finance/data_architecture/*.md` document.
- If analysis documents were previously stored under `finance/docs`, prefer the `.note/finance/` location going forward.
- Use `.note/finance/MASTER_PHASE_ROADMAP.md` as the top-level phase roadmap.
- Use `.note/finance/FINANCE_DOC_INDEX.md` as the top-level index into finance documents.
- Use `.note/finance/FINANCE_TERM_GLOSSARY.md` as the shared glossary for recurring quant / backtest / real-money terminology.
- Use `.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md` as the dedicated index for durable backtest-result Markdown reports.
- For phase plans, policy documents, validation rules, or real-money guidance documents, do not leave key terms as compressed jargon only.
- When creating or substantially rewriting a phase plan document, include at minimum:
  - `쉽게 말하면`
  - `왜 필요한가`
  - `이 phase가 끝나면 좋은 점`
  so the plan reads as an explanation of purpose and value, not only as an internal task memo.
- Use `.note/finance/PHASE_PLAN_TEMPLATE.md` as the default starting shape for new `finance` phase plan documents unless there is a strong reason to deviate.
- When opening a new `finance` phase and the work would benefit from consistent boilerplate, prefer:
  - `python3 plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py --phase <N> --title "<Phase Title>"`
  before writing the phase documents manually.
- In phase plan documents, prefer plain-language labels such as
  - `작업 단위`
  - `첫 번째 작업`
  - `다음 작업`
  instead of internal jargon like `slice`, unless the jargon is explicitly explained on the spot.
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
  - one or more phase TODO board documents for current execution
- Treat each phase plan document as a user-facing orientation aid as well as an engineering kickoff.
- If a phase plan contains priority items or workstreams with unfamiliar names, explain those terms inline or add them to the glossary instead of leaving the meaning implicit.
- When a phase is active, keep its TODO board updated with:
  - grouped work areas
  - `pending` / `in_progress` / `completed` status
  - short explanations for each subtask
- For phase-level status in roadmap and index documents, separate progress from validation instead of combining them into one status string.
- Preferred phase progress labels:
  - `planned`
  - `active`
  - `partial_complete`
  - `implementation_complete`
  - `practical_closeout`
  - `complete`
- Preferred phase validation labels:
  - `not_ready_for_qa`
  - `manual_qa_pending`
  - `manual_qa_completed`
  - `smoke_checked`
  - `superseded_by_later_phase`
  - `legacy_unknown`
  - `not_applicable`
- Treat older labels such as `completed`, `first_chapter_completed`, `completed / manual_validation_pending`, and `phase_complete / manual_validation_completed` as legacy shorthand. Explain or normalize them when editing phase indexes.
- Do not introduce a formal chapter hierarchy unless the user explicitly requests it; `first_chapter_completed` should be treated as a legacy partial-completion label.
- If scope changes during a phase, update the phase document and TODO board rather than leaving the change only in chat.
- Before opening a new major phase, confirm the new phase direction with the user.
- When a phase reaches a practical completion point, create a phase-specific manual test checklist document under `.note/finance/phases/phase*/`.
- The checklist should be written for user-facing verification and should cover the major features, UI paths, and validation points added during that phase.
- Prefer checklist items to use Markdown task checkboxes such as `[ ]` so the user can mark progress directly inside the document.
- Use `.note/finance/PHASE_TEST_CHECKLIST_TEMPLATE.md` as the default starting shape for new `finance` phase test checklist documents unless there is a strong reason to deviate.
- When handing off a checklist for user verification, treat "all checklist items checked" as the default gate before moving to the next major phase, unless the user explicitly asks to skip or defer some items.
- When sharing phase completion, include the checklist document in the final handoff so the user has a concrete test plan.
- When a phase reaches practical completion, also review the project’s durable workflow guidance and references for staleness.
- In `PHASE*_NEXT_PHASE_PREPARATION.md`, explain both:
  - why the next phase is the right direction
  - what concrete work the next phase will actually do, in plain language
- At minimum, check whether newly implemented behavior should update:
  - `AGENTS.md`
  - finance skills / `SKILL.md` instructions that are actively used for this repository
  - `.note/finance/FINANCE_DOC_INDEX.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - phase-specific reference or preparation documents
- If newly added workflows, defaults, validation rules, or operator practices changed how work should be executed in future turns, refresh those guidance/reference documents during phase closeout rather than leaving the update only in chat.
- If the review concludes that no skill/reference update is needed, record that outcome briefly in the phase closeout notes or progress log.
- Keep near-term phase execution centered on the build foundations:
  - data collection
  - backtesting
  - validation / review workflow
- Treat the long-term product target as:
  - evidence-based investment candidate recommendation
  - portfolio construction proposal
  - user-defined portfolio construction
  - multiple strategy implementations
  - backtest execution
  - return/risk/result visualization
  - pre-live review before any actionable deployment

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

## Function Documentation Rules
- When adding a non-trivial function that owns domain logic, workflow routing, persistence conversion, scoring, validation, or cross-module handoff, add a short purpose comment immediately above it or a concise docstring inside it.
- The comment should explain what the function is responsible for, not restate the function name line-by-line.
- Trivial wrappers, obvious one-line helpers, local callbacks, and functions whose purpose is already completely clear from their name and context do not need forced comments.
- If a function is moved during refactoring, preserve or improve the existing purpose comment only when it helps future readers find the boundary.

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
- For this repository, prefer Korean commit descriptions and commit-body explanations unless the user explicitly asks for another language.
- Do not include generated artifacts, run histories, local experiment CSVs, notebook scratch files, or other machine-local outputs unless the user explicitly asks for them.

## Change Review Checklist
- For finance backtest refinement work, was `check_finance_refinement_hygiene.py` run when it would materially help?
- Does this change affect the project-level overview, setup flow, or main UI surface described in `README.md`?
- Does this change add, rename, move, split, or materially change the responsibility of a script? If yes, update `.note/finance/code_analysis/SCRIPT_STRUCTURE_MAP.md` and the matching detailed flow document.
- Does this change affect data source boundaries?
- Does this change affect DB schema or table meaning?
- Does this change alter strategy inputs, outputs, or assumptions?
- Does this change require documentation sync in `FINANCE_COMPREHENSIVE_ANALYSIS.md`?
- Does this change require an update to `.note/finance/code_analysis/` because a durable code flow changed?
- Does this change require an update to `.note/finance/data_architecture/` because data / DB meaning changed?
- Did newly added non-trivial functions get a short purpose comment or docstring when the intent is not obvious from the surrounding code?
- If this phase is closing or handing off, does it require a phase-specific manual test checklist document?
- If this phase is closing or handing off, do `AGENTS.md`, active skills, roadmap/index docs, or phase reference docs need to be refreshed to reflect the implemented workflow?
- Does this change require an appended entry in `WORK_PROGRESS.md`?
- Does this change produce durable design or analysis knowledge that belongs in `QUESTION_AND_ANALYSIS_LOG.md`?
- Does this change introduce any point-in-time or survivorship bias risk?
