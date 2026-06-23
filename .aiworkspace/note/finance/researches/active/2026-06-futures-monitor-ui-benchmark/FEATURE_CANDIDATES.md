# Feature Candidates

Status: Draft
Last Updated: 2026-06-23

## Summary

The next Futures Monitor improvement should focus on layout and workflow, not new data. The highest-value slice is a Streamlit UI redesign that converts the current form/card stack into a market workbench.

## Candidate Matrix

| Candidate | Bucket | Impact | Effort | Risk | Confidence | Strategic Fit | Owner Area |
|---|---|---:|---:|---:|---:|---:|---|
| Futures Workbench Layout V1 | Now | 5 | 3 | 2 | 4 | 5 | `app/web/overview_dashboard.py`, `overview_ui_components.py` |
| Refresh Status Strip V1 | Now | 4 | 2 | 2 | 4 | 5 | `app/web/overview_dashboard.py` |
| Market Brief Hero V1 | Now | 5 | 3 | 2 | 4 | 5 | `app/web/overview_dashboard.py` |
| Weekly Flow Lane V1 | Next | 4 | 3 | 2 | 4 | 4 | `app/web/overview_dashboard.py` |
| Linked Watch Rail V1 | Next | 4 | 4 | 3 | 3 | 4 | `app/web/overview_dashboard.py` |
| Chart Annotations V1 | Later | 3 | 4 | 3 | 3 | 3 | chart render helpers |
| Full Custom Dashboard Builder | Parking Lot | 3 | 5 | 5 | 2 | 2 | platform research |

## Candidates

### Futures Workbench Layout V1

- Bucket: Now
- Problem: current page still looks like form inputs plus repeated cards.
- User workflow change: user reads context bar, market brief, weekly/evidence lane, then charts.
- Evidence: TradingView/Koyfin persistent watch context; Datadog/Grafana ownership of dashboard widgets; Toss simplification.
- Required code/data/doc areas: `app/web/overview_dashboard.py`, `app/web/overview_ui_components.py`, service contract tests, research docs.
- Dependencies: none beyond existing snapshot/read models.
- Risks: Streamlit layout limits may require careful CSS.
- Validation idea: Browser QA desktop and mobile-ish width, text overlap checks, service helper tests.
- Owner skill: future implementation should use frontend guidance plus finance task intake.
- Priority rationale: highest user-visible improvement without data boundary changes.

### Refresh Status Strip V1

- Bucket: Now
- Problem: refresh popover is large and covers the market brief.
- User workflow change: user sees stale status and can run manual refresh without losing context.
- Evidence: observability dashboards keep health visible but compact; Stripe surfaces important notifications near overview.
- Required code/data/doc areas: existing refresh UI helper and CSS.
- Dependencies: existing `run_overview_futures_ohlcv` action.
- Risks: auto-refresh settings could become less discoverable.
- Validation idea: Browser QA with menu closed/open.
- Owner skill: frontend-focused finance task.
- Priority rationale: directly addresses user complaint and screenshot pain.

### Market Brief Hero V1

- Bucket: Now
- Problem: Macro Context still reads as support cards and paragraphs.
- User workflow change: user sees one clear market statement, then support/opposition evidence.
- Evidence: Toss plain-language content placement; Koyfin dashboard summary-first pattern.
- Required code/data/doc areas: renderer and CSS only; use existing `summary_sentences`, `evidence_reading`, `weekly_context`.
- Dependencies: none.
- Risks: must avoid investment-advice wording.
- Validation idea: tests for no recommendation/trading language and Browser QA.
- Owner skill: frontend-focused finance task.
- Priority rationale: core value of Futures Monitor is market interpretation.

### Weekly Flow Lane V1

- Bucket: Next
- Problem: weekly cards do not show ranking or relation to today's state.
- User workflow change: user reads dominant weekly driver and whether it supports or conflicts with today's interpretation.
- Evidence: dashboard trend lanes and Toss simple reading order.
- Required code/data/doc areas: renderer; perhaps small helper for ranked weekly items.
- Dependencies: existing `weekly_context`.
- Risks: oversimplifying mixed macro data.
- Validation idea: helper tests for driver/support/opposition labels.
- Owner skill: frontend-focused finance task.
- Priority rationale: strengthens the user's original request for N-day flow.

### Linked Watch Rail V1

- Bucket: Next
- Problem: selected symbol chips look like input state, not monitoring workspace.
- User workflow change: symbols scan as watch rows; edit action is secondary.
- Evidence: TradingView/Koyfin/IBKR watchlists.
- Required code/data/doc areas: renderer and CSS; maybe helper for row metrics.
- Dependencies: existing `rows`.
- Risks: Streamlit multiselect still needed for editing.
- Validation idea: Browser QA, symbol count / row fallback tests.
- Owner skill: frontend-focused finance task.
- Priority rationale: gives the page a real monitor feel.

## Parking Lot

- Full custom dashboard builder.
- Drag-and-drop layout.
- Broker-like chart trading / order controls.
- Live AI signal or recommendation language.

## Rejected Ideas

- Add more diagnostic status cards: conflicts with user feedback and Real-Use Improvement Rule.
- Make raw data table more prominent: improves transparency but worsens first-screen usability.
- Direct UI provider fetch: violates project data boundary.

