# Risks

Status: Active
Last Updated: 2026-07-16

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Approved research direction is mistaken for completed implementation | High | Link to the approved design and keep every roadmap stage explicitly unimplemented until verified. |
| Users treat a phase probability as an investment recommendation | High | Keep the surface as context, show alternatives, and exclude portfolio actions. |
| Model estimate is mistaken for an NBER declaration | High | Use `모델 추정` copy and render official NBER history separately. |
| UI is delivered before evidence quality is valid | High | Gate UI on a vintage-aware read model and rolling-origin results. |

## Technical Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Revised data leaks into historical forecasts | High | Store/read vintages by forecast origin and test unreleased-data exclusion. |
| Four-state labels are unstable or arbitrary | High | Publish operational semantics, compare to OECD quadrants, and evaluate against NBER two-state history. |
| Rare recessions make a complex model overfit | High | Prefer parsimonious features, naive baselines, regularization, and event-level validation. |
| Ragged release dates create false freshness | High | Track observation date, release/vintage date, expected cadence, and per-series staleness. |
| Direct +1M/+2M probabilities are poorly calibrated | High | Use separate horizon calibration and withhold probabilities if thresholds fail. |
| COVID dominates model scale and transition estimates | Medium | Use robust scaling, volatility-state checks, and episode sensitivity analysis. |
| OECD CLI revisions change recent quadrants | Medium | Preserve vintages and treat OECD CLI as a benchmark/feature, not ground truth. |
| External official series change or disappear | Medium | Keep a source catalog, fallback policy, and explicit missing-data degradation. |
| Existing macro readers break after schema changes | High | Add backward-compatible views/loaders and regression tests before migration. |

## Research Gaps

| Gap | Why it matters | Follow-up |
| --- | --- | --- |
| Exact ALFRED acquisition mode and API-key policy | Determines whether historical vintages can be bootstrapped automatically | Validate selected-series coverage and key-free/manual fallback during design/implementation planning. |
| Final core series list | Too many inputs increase revision and overfit risk; too few miss breadth | Prototype a focused catalog and compare factor stability. |
| Four-state label construction | NBER provides only two official states | Compare transparent level×momentum labels with constrained Markov alternatives. |
| Probability publication threshold | A model can rank states without being calibrated enough for percentages | Set quantitative acceptance criteria in the implementation plan. |
| Fiscal-policy measurement | The study note treats fiscal policy as a core force, but monthly real-time fiscal impulse is difficult | Keep qualitative/event context in V1 and research a durable source later. |
| Gold and dollar data contract | Useful market context but not required for the real-activity engine | Add only if official/licensed storage and transformation rules are clear. |
| Visual density and mobile hierarchy | Clock, ribbon, probabilities, and evidence can crowd one screen | Validate a wireframe before UI implementation and run 420px QA. |
