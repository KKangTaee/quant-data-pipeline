# Overview Market Context US Stock Turnaround Analysis V1 Runs

Last Updated: 2026-07-15

## Intake And Design Audit

- Confirmed branch `codex/sub-dev`; existing branch is ahead of origin and only unrelated untracked research folder is dirty.
- Read finance docs index/roadmap/project map and the completed U.S. stock valuation active task.
- Inspected current selected-stock pure calculator, loader, service, combined service, Streamlit event bridge, React component, statement ledger/shadow mappings, and DB schema.
- Used the current worktree; no new worktree was created.

## Actual DB Read-Only Audit

- Queried relevant duration/instant concept coverage for LCID, RIVN, PLTR, AMD, and AAPL with `available_at <= 2026-07-15`.
- Verified RIVN/PLTR have 16-19 distinct-quarter main-flow evidence and LCID has 15-18 quarters across core flows.
- Verified direct GrossProfit tag heterogeneity and the need for same-quarter revenue-cost fallback.
- Verified asset-profile market-cap collection timestamps differ materially across symbols, so numeric EV needs a freshness gate.
- No provider call, DB write, collection action, registry append, or generated artifact was produced.

## Research Check

- SEC API/XBRL documentation supports separate instant/duration contexts and warns about fiscal/calendar period alignment.
- Damodaran supports treating negative earnings and cyclical/troubled firms with different normalization/multiple logic rather than forcing P/E.
- Piotroski supports reading profitability, cash flow, leverage/liquidity, and efficiency as separate statement signals.
- Dechow/Dichev supports preserving an accrual/cash-flow quality boundary instead of assuming reported earnings and cash conversion are identical.

## Design Documentation

- Created the six-file active task shell.
- Fixed the main conceptual ambiguity by separating selected-company V1 from universe-wide discovery V2.
- Fixed numerator/denominator consistency by using market-cap-based OCF/FCF ratios instead of EV/OCF.
- Added exact resolver, milestone, risk, freshness, readiness, UI, collection, test, and five-stage roadmap contracts.
- Placeholder scan found no `TBD`/`TODO` or incomplete implementation requirement.
- Self-review aligned the current task index/roadmap/root handoff and confirmed `git diff --check` passes.
- Implementation commands/tests have not been run because written spec review precedes code changes.

## Detailed TDD Planning

- Confirmed design commit `067cc954` is current `HEAD`; no implementation diff exists after the approved design.
- Re-read `AGENTS.md`, finance INDEX/ROADMAP/PROJECT_MAP, all six active task documents, current U.S.-stock PER calculator/loader/service/action/event/React/test boundaries, and the raw statement/profile schema.
- Expanded `PLAN.md` into exact 1차~5차 file ownership, interfaces, RED/GREEN commands, regression gates, Browser QA, documentation sync, and coherent commit units.
- Plan self-review found no uncovered design requirement or unresolved placeholder; `git diff --check` passed before the planning commit.

## 1차 — Quarter Resolver Accuracy

- RED: new turnaround tests first failed on the missing module, then on empty resolver results after a callable stub exposed the intended assertions.
- GREEN: implemented direct-quarter duration classification, cumulative `H1-Q1`, `9M-H1`, `FY-Q1-Q2-Q3`, primary-period comparative filtering, max-operand `available_at`, and operand provenance.
- GREEN: implemented instant fact isolation and PIT split-neutral weighted-share normalization that ignores split events after the requested as-of date.
- Verification: `tests.test_us_stock_turnaround` plus `tests.test_us_stock_valuation` ran 48 tests with 0 failures; target `py_compile` and `git diff --check` passed.

## 2차 — Turnaround Analysis Engine

- RED/GREEN: added canonical metric fixtures for revenue, gross profit fallback, operating/net income, OCF, CapEx, FCF proxy, EPS, diluted shares, gap-preserving TTM, YoY, and instant balance components.
- RED/GREEN: fixed independent milestone contracts for 8-quarter evidence, operating improvement, two consecutive positive TTM OCF observations, quarterly/TTM EPS separation, and PER handoff readiness.
- RED/GREEN: fixed runway, meaningful positive-operating-income interest coverage, net-debt/negative-OCF, and split-neutral dilution overlays.
- RED/GREEN: fixed valuation priority and numerator consistency, including P/FCF, P/OCF, EV/EBITDA, EV/Gross Profit, EV/Sales, direct-debt precedence, aligned statement components, freshness, USD-unit, denominator, and specialized-sector gates.
- Verification: `.venv/bin/python -m unittest tests.test_us_stock_turnaround tests.test_us_stock_valuation -v` ran 67 tests with 0 failures; target `py_compile` and `git diff --check` passed.

## 3차 — Loader, Service, Collection

- RED/GREEN: added query-spy coverage for exact selected symbol, seven fiscal years, as-of cutoff, separate duration/instant queries, relevant concept/unit filters, bounded profile and price reads, and USD share/currency evidence.
- RED/GREEN: added JSON-safe selected-stock turnaround service, `NOT_SELECTED` no-loader path, exact raw-gap action scopes, combined schema v4, unchanged S&P/PER fields, isolated turnaround failure, and positive READY PER-only recommendation.
- RED/GREEN: added optional one-symbol asset-profile collection while preserving the default broad query; symbol/CIK validation now precedes profile/price/SEC runners.
- RED/GREEN: added explicit `collect_us_stock_turnaround` Streamlit event, synchronous overview facade, partial-success preservation, and remaining-scope-only retry.
- Verification: `.venv/bin/python -m unittest tests.test_us_stock_turnaround tests.test_us_stock_valuation tests.test_market_context_valuation -v` ran 92 tests with 0 failures; touched Python modules passed `py_compile`.

## 4차 — Inner Selector And Turnaround UI

- RED/GREEN: added selected-symbol-only `PER 상대가치 | 전환 분석` source contracts and symbol-keyed local selection; a new symbol follows `recommended_analysis`, while rerenders preserve an explicit same-symbol choice without a Streamlit event.
- RED/GREEN: added color-independent milestone labels, shared 8/12/20-quarter slots, separate revenue-YoY/margin scales, TTM OCF/FCF bars, explicit zero axes, gap-safe line segments, raw/TTM/available-at inspectors, risk cards, and exact valuation-block reasons.
- Responsive: added compact selector, stacked charts, and one-column risk/collection/valuation cards at phone width without a fixed chart minimum width.
- Verification: Market Context + turnaround + existing PER regression ran 95 tests with 0 failures; `npm run build` completed 171 module transforms and refreshed the hashed `component_static` bundle; `git diff --check` passed.
