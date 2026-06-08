# Feature Candidates

Scoring: 1 low, 5 high.

| Priority | Candidate | Impact | Effort | Risk | Confidence | Fit | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| P0 | Reference Center landing IA | 5 | 2 | 1 | 5 | 5 | Build first. |
| P0 | Structured guide catalog read model | 4 | 3 | 2 | 4 | 5 | Build with landing to reduce future drift. |
| P1 | Journey guides for current product surfaces | 5 | 3 | 2 | 4 | 5 | Build after landing skeleton. |
| P1 | Searchable status / concept dictionary | 4 | 3 | 2 | 4 | 4 | Build after core journeys. |
| P1 | Troubleshooting playbooks | 5 | 3 | 2 | 4 | 5 | Build with data freshness and validation examples. |
| P2 | Contextual links from other screens | 4 | 4 | 3 | 3 | 4 | Add after Reference anchors stabilize. |
| P2 | Docs alignment / drift check | 3 | 2 | 1 | 5 | 5 | Do after UI scope is approved. |

## P0. Reference Center Landing IA

Goal:

- Replace the current single-purpose first screen with a compact Reference Center landing.
- Keep the current `Portfolio Selection Guide` as a journey inside the page.
- Add task cards for data, Overview, candidate creation, validation, final decision, monitoring, troubleshooting.

Evidence:

- Audit: current page is strong for portfolio selection but weak for product-wide operation.
- Benchmark: Koyfin help starts from categories; testfolio distinguishes model/inspect/related tools; TradingView separates result sections.

Dependencies:

- `app/web/reference_guides.py`
- optional structured catalog module, likely `app/services/reference_guide_catalog.py` or a small `app/web/reference_guides_content.py`

Success criteria:

- First viewport answers "what do I need help with?"
- User can reach portfolio-selection guide in one click.
- User can reach data freshness / stale UI troubleshooting in one click.
- No registry write, DB write, provider fetch, or job execution is added.

## P0. Structured Guide Catalog Read Model

Goal:

- Move static journey / concept / record / playbook content into structured rows.
- Keep Streamlit render code focused on layout.

Evidence:

- Audit: current one-file design increases copy drift and makes review harder.
- Benchmark: mature docs expose sections, contents, related docs, and repeatable templates.

Dependencies:

- Existing import boundary: app services/runtime should stay Streamlit-free.
- If placed under `app/services`, catalog must not import Streamlit or web modules.

Success criteria:

- Catalog can be imported by tests without loading Streamlit.
- Journey cards, concept rows, and playbooks are data objects with stable keys.
- UI render remains read-only.

## P1. Journey Guides For Current Product Surfaces

Goal:

- Add five to six journeys that map current product screens and records:
  market context, data freshness, candidate creation, validation/final decision, monitoring, archive/recovery.

Evidence:

- Audit: Reference does not cover Overview/Ingestion/Operations sufficiently.
- Benchmark: Koyfin and IBKR explain dashboards, portfolios, allocations, reports, and planning in separate sections.

Dependencies:

- Current canonical docs: `PRODUCT_DIRECTION.md`, `PORTFOLIO_SELECTION_FLOW.md`, `SYSTEM_BOUNDARIES.md`, `DATA_FLOW_MAP.md`.

Success criteria:

- Each journey has owner screen, safe actions, generated records, stop conditions, and downstream screen.
- Journey copy matches current navigation names: `Portfolio Monitoring`, not only legacy `Selected Portfolio Dashboard`.

## P1. Searchable Status / Concept Dictionary

Goal:

- Give users a quick way to interpret status labels and evidence terms without reading long docs.

Evidence:

- TradingView has separate metric definitions; current finance statuses are numerous and easy to misread.

Dependencies:

- Existing `Reference > Glossary`.
- Backtest captions already mention Guides / Glossary in several places.

Success criteria:

- Search / filter finds common labels: `NOT_RUN`, `REVIEW`, `BLOCKED`, `Data Trust`, `Provider Coverage`, `selection gate`.
- Each result states whether it can block progression and where to fix it.

## P1. Troubleshooting Playbooks

Goal:

- Convert repeated support issues into short user-facing operational playbooks.

Evidence:

- Recent Futures Monitor stale-refresh issue shows users need "what to check next" guidance.
- Benchmark help centers reserve space for FAQ / limitations / adjacent articles.

Dependencies:

- Overview and Ingestion runbooks.
- Data / system health screen ownership boundaries.

Success criteria:

- Playbooks cover stale Overview/Futures data, missing provider snapshots, `NOT_RUN`, blocked Final Review source picker, stale monitoring scenario.
- Each playbook identifies safe action and stop condition.

## Parking Lot

- AI chat inside Reference.
- Full-text indexing of every markdown doc.
- Auto-generating Reference from docs without review.
- Broker/live-trading readiness guide.
- PDF/exported product manual.
- Rewriting `Reference > Glossary` in the same first pass.
