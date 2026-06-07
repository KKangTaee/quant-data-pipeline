# Recommendation

## One-Line Recommendation

Rebuild `Reference > Guides` as a task-first `Reference Center`, keep the current portfolio-selection guide as one journey, and add product-wide journeys, status definitions, record maps, and troubleshooting playbooks in phased work.

## Why This Direction

The current Guides screen is not broken; it is too narrow for the product it now supports.
The finance console has grown into a DB-backed workflow covering Overview, Ingestion, Backtest, Practical Validation, Final Review, Operations, and Portfolio Monitoring.
Users need a reference surface that answers operational questions across those screens.

External patterns support this:

- QuantConnect: research process and pitfalls are explicit before backtesting.
- TradingView: strategy result interpretation is split into overview, performance, trades, risk, and metric definitions.
- Koyfin: help is category/search driven and tied to dashboards, views, portfolios, and reports.
- IBKR PortfolioAnalyst: reporting, allocation, performance, planning, and benchmarks are separated into explainable widgets/reports.
- testfolio: portfolio analysis is framed around what users model, inspect, and compare, with clear educational boundaries.

## Recommended 1st Build Scope

### Step 1. Reference Center Shell

- Replace the current hero-first page with a compact task-first landing.
- Keep top navigation path unchanged: `Reference > Guides`.
- First screen sections:
  - `오늘 무엇을 확인하려나요?` task cards.
  - `현재 제품 흐름` compact map.
  - `자주 막히는 상태` quick links.
  - `현재 Portfolio Selection Guide 열기`.

### Step 2. Structured Guide Catalog

- Create a small structured catalog for journeys, terms, records, and playbooks.
- Keep it Streamlit-free if placed under `app/services`.
- Render catalog rows through `app/web/reference_guides.py`.

### Step 3. Preserve And Rehome Current Guide

- Keep current route selector and Go / Review / Stop content as `Journey: 후보를 모니터링 후보로 보내기`.
- Update copy to match current 1~4 flow and `Operations > Portfolio Monitoring` naming.
- Remove or lower legacy Candidate Packaging / Portfolio Proposal references from user-facing first path.

### Step 4. Add Minimum Viable New Journeys

- `Daily Market Context`: Overview / Futures / sentiment / event calendar.
- `Data Freshness Repair`: Ingestion / System Data Health / run artifacts.
- `Candidate Creation`: Backtest Analysis / source handoff.
- `Evidence Review`: Practical Validation / Final Review.
- `Monitoring After Selection`: Portfolio Monitoring / scenario update.

### Step 5. Add Minimum Troubleshooting Playbooks

- `Overview / Futures data가 stale일 때`
- `Practical Validation NOT_RUN이 있을 때`
- `Final Review 후보가 보이지 않을 때`
- `Portfolio Monitoring scenario가 stale일 때`

## Recommended Next Phase After 1st Build

| Phase | Output | Why |
| --- | --- | --- |
| 1차 | Reference Center shell + current guide rehomed | 현재 Reference의 방향을 새 제품 구조에 맞추는 최소 사용자 가치. |
| 2차 | Journey guides + troubleshooting playbooks | 실제 운영 중 막히는 질문을 Reference에서 바로 찾게 함. |
| 3차 | Searchable concept/status dictionary + Glossary cross-link | `NOT_RUN`, blocker, Data Trust, provider coverage 같은 용어 오해를 줄임. |
| 4차 | Contextual links from Overview / Backtest / Practical Validation / Monitoring | 사용자가 문제를 보는 화면에서 관련 Reference로 바로 이동. |
| 5차 | Docs alignment + Browser QA + drift guard | canonical docs와 UI guide 간 drift를 줄이고 회귀를 방지. |

## What Not To Do Yet

- Do not add live approval, broker order, account sync, or auto rebalance language.
- Do not execute ingestion / refresh / replay actions inside Reference.
- Do not make Reference a marketing landing page.
- Do not merge or delete `Reference > Glossary` in the first pass.
- Do not auto-generate all Reference copy from markdown docs without product review.
- Do not rewrite registries, saved setups, run history, or generated artifacts.

## Decision Rules

Proceed when:

- The user approves `Reference Center` as the target direction.
- 1차 scope is limited to Guides page IA/content/render and docs alignment.
- No new persistence or provider fetch behavior is introduced.
- Existing portfolio-selection guide remains reachable.
- Browser QA verifies desktop and narrow viewport text does not overlap.

## Final Recommendation

Proceed with 1차 only after approval:

1. Build the Reference Center shell.
2. Rehome the existing portfolio-selection guide as a journey.
3. Add minimum journeys for Overview, Ingestion/Data Health, Backtest, Validation/Final Review, and Portfolio Monitoring.
4. Add the first troubleshooting playbooks for stale data and blocked validation states.

After 1차, review with Browser before deciding whether to continue into 2차/3차. This keeps the revamp useful immediately while avoiding a large speculative rewrite.
