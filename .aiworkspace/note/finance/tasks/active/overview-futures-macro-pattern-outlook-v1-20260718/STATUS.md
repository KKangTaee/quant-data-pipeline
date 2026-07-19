# Futures Macro Pattern Outlook V1 Status

## 2026-07-19 — 60D Legend / Status Clarity / V4 Runtime Recovery

- The approved follow-up is complete: the 60-trading-day ribbon now has a visible five-color regime legend plus a striped transition legend, instead of relying on color without an on-screen key.
- Asset cards keep `관측 완료` on the current 1D / 5D / 20D observation and label each future row `전체 전망 · PROVISIONAL`, so the future distribution no longer looks like a card-wide current-data warning.
- The production React bundle was rebuilt and the stored ten-year daily rows were rematerialized without a provider call. The compatible DB snapshot is `pattern_outlook_v4_conservative_status_10y`, as of `2026-07-17`, materialized at `2026-07-19 13:48:06`.
- Browser QA confirmed 60 ribbon cells, all five regime labels plus the transition key, five observed asset cards, ten future-status rows, zero console errors, and no desktop or 420px horizontal overflow. The mobile legend wraps to two rows.
- QA screenshot: `/Users/taeho/.codex/visualizations/2026/07/19/futures-macro-ribbon-status/futures-macro-ribbon-status-qa.png` (generated, not staged).
- No probability model, publication gate, provider, DB schema, or first-entry DB-only boundary changed. Current remains observed; 5D / 20D remain provisional for the measured validation reasons already recorded below.

## 2026-07-19 — Observation Status / Ten-Year Validation Closeout

- Approved A안 roadmap `1~4` is complete: current observation status separation, asset-card current/5D/20D status separation, ten-year daily history contract, and actual ten-year backfill / re-evaluation.
- A compatible current snapshot now publishes `관측 완료 / 일부 관측 / 관측 불가`; `VERIFIED / PROVISIONAL / UNAVAILABLE` is reserved for future distributions. Current evidence is no longer downgraded because a future horizon is provisional.
- Successful `일봉 갱신` requests `10y / 1d`, stores the daily rows, and materializes `pattern_outlook_v4_conservative_status_10y`. Overview entry and `다시 읽기` remain DB-only.
- Actual refresh succeeded for all 17 symbols and UPSERTed 42,499 rows. Sixteen symbols begin on `2016-07-18`; RTY begins on `2017-07-10`; all end on `2026-07-17`.
- Actual current state is `관측 완료`. 5D has 120 independent episodes and 20D has 88; both final outlooks remain `PROVISIONAL / 방향 우위 미확인` because probability and path status are now combined conservatively.
- 5D still misses path-baseline improvement by a small margin and middle-50% coverage. 20D still misses Brier-baseline improvement, fold stability, and middle-50% coverage. Thresholds remain 30 / 60 independent episodes and were not lowered.
- Desktop Browser QA confirmed the separated current / 5D / 20D badges, fixed observed anchors, different 5D / 20D terminals, React method / trace disclosures, and zero console errors.
- QA screenshot: `/Users/taeho/.codex/visualizations/2026/07/19/futures-macro-observation-status/futures-macro-observation-status-qa.png` (generated, not staged).
- Conditional 5차 model revision is not started. It may begin only with a separately approved chronological out-of-sample design targeting the measured failures above.

## 2026-07-19 — Materialized Snapshot / React Disclosure Closeout

- Approved closeout roadmap `4/4` is complete: compact snapshot persistence, daily-ingestion materialization, DB-only first entry, and React method / calculation trace disclosure. The later ten-year upgrade supersedes its initial history length.
- `일봉 갱신` now stores the refreshed daily futures rows and then materializes the current macro plus 5D / 20D outlook in `finance_meta.futures_macro_snapshot`.
- Overview first entry and `다시 읽기` only read the stored compatible snapshot. They do not fetch a provider or calculate the outlook; missing or incompatible rows instruct the user to run `일봉 갱신`.
- `방법론과 품질` now synchronizes iframe height when toggled, and `원본 데이터 / 계산 추적` is a React disclosure with compact metadata, current scores, score contributions, daily futures changes, and cautions.
- Actual materialization as of `2026-07-17` completed in 10.549s. Fresh-process DB reads measured 0.36–0.37s and browser reload to the ready workbench measured 1.877s.
- Desktop and 420px Browser QA passed. Both disclosures expanded without clipping; the three narrow-screen trace tables use internal horizontal scroll (`309px` client width versus `785–1,457px` content); latest QA server console errors were 0.
- QA screenshot: `/Users/taeho/.codex/visualizations/2026/07/19/futures-macro-materialized-snapshot/futures-macro-react-disclosures.png` (generated, not staged).

## 2026-07-19 — Asset Outlook Layout Follow-up

- Root cause: each of the five narrow asset cards repeated the horizon-level `전체 전망 · PROVISIONAL` badge in a third grid column. That column compressed the asset-specific direction into one-character Korean line wraps.
- A안 is implemented: the shared 5D / 20D publication statuses now appear once in the section heading, while each card retains only the period and its asset-specific direction.
- Status semantics and model outputs are unchanged. `PROVISIONAL` remains the correct combined probability/path publication state, and the pathway labels still use the existing median-forward-z thresholds (`>= +0.25` upward, `<= -0.25` downward, otherwise `우위 미확인`).
- Current stored output is legitimately neutral for every 5D family. At 20D, risk assets are `상방 우세` (`+0.482`), while commodities, dollar, rates, and safe haven remain inside the neutral band.
- Desktop and 420px Browser QA found one 5D badge, one 20D badge, five cards, no repeated per-card publication badge, no direction wrapping, no horizontal overflow, and zero console errors.
- QA screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/futures-macro-asset-outlook-layout-qa.png` (generated, not staged).
- Existing overall roadmap remains complete; this approved A안 follow-up is complete (`1/1`).

## 2026-07-19 — Macro Pressure Copy Follow-up

- User confirmed that the Y axis should name what it actually aggregates instead of using the broad `매크로 부담` shorthand.
- The payload now labels the axis `금리·달러·물가 압력`; all four quadrants use the same explicit 강화/완화 wording.
- This is a copy-only interpretation correction. The 5D standardized rate / dollar / inflation pressure mean, coordinates, forecast path, probability, and publication gates are unchanged.
- TDD RED failed on the old payload label, then GREEN passed after the minimal source change; the React production bundle was rebuilt.
- Actual desktop and 420px Browser QA confirmed no clipping or horizontal overflow and zero console errors.
- Overall original roadmap remains complete (`5/5`); this approved follow-up is complete (`1/1`).

## 2026-07-18

- User requested a Futures Macro improvement after closing the economic-cycle / market-context work.
- Read-only audit confirmed that today risk evidence is useful, while 1D / 1W / 1M are disconnected return views and historical validation replays only one-day state.
- User approved the recommended boundary: overall market risk regime first, asset-family direction as supporting evidence, and 5D / 20D conditional outlook rather than long-term forecasting.
- User reviewed and approved the design contract.
- User compared three UI wireframes and selected `A · 맥락→전망형`.
- Detailed TDD implementation plan is written in `PLAN.md` with seven independently reviewable tasks.
- Current stage: inline execution started; linked worktree and baseline environment are being verified before Task 1 RED.
- Baseline investigation confirmed the repository-local runner is `unittest`; the implementation plan now records unittest equivalents instead of adding pytest.
- Task 1 complete: point-in-time 1D / 5D / 20D family features reuse existing score weights and preserve trailing-only calculations.
- Task 2 complete: current regime, transition phase, 60D path / ribbon, evidence, and change conditions are separated from future probabilities.
- Task 3 complete: 5D / 20D forward outcomes use as-of volatility, and similar dates are de-overlapped by trading-row episode spacing.
- Task 4 complete: chronological publication metrics, strict 30 / 60 episode gates, unavailable-number suppression, and latest-row cache are implemented.
- Task 5 complete: the thermometer snapshot now carries the current pattern, the tab loads the conditional outlook by default, and the V2 payload separates current observation from 5D / 20D probability estimates.
- Legacy historical-validation loading is no longer part of the active render path; refresh and reload clear the new latest-marker cache.
- Task 6 complete: the React workbench now follows A안 from current regime through 5D / 20D outlook, observed path and probability zones, regime ribbon, asset pathways, and method disclosure.
- The unreferenced V1 `RecentFlowSection` and `HistoricalValidationPanel` sources were removed after repository-wide reference checks.
- Task 7 complete: actual read-only data QA, performance optimization, desktop/mobile Browser QA, final verification, and durable documentation sync are complete.
- Actual 2026-07-17 state is `mixed / transition_attempt`; 5D has 120 independent episodes and 20D has 42, both `PROVISIONAL` with `방향 우위 미확인`.
- Vectorized path statistics reduced the actual uncached build from 21.791s to 4.963s; same-marker cached reload is 0.031s and returns the identical object.
- Browser QA at `http://localhost:8512` confirmed 3 horizon cards, map + evidence, 60D ribbon, 5 asset pathways, method disclosure, 420px single-column layout with no horizontal clipping, and 0 console errors.
- Overall roadmap: 1차 design through 5차 actual QA / docs sync complete (`5/5`).
- No DB schema, provider, registry, or saved setup has been changed.
- User rejected the unreadable 60-point polyline / forecast ellipse map, then confirmed that the interim fixed categorical branches did not change geometry by horizon and approved empirical conditional paths.
- The active map now renders `20D 전 → 5D 전 → 현재` observed anchors plus one direct current-to-terminal expected-net-movement line, one terminal middle-50% arrival range, fixed-size mid-line direction markers, and one terminal marker. Stepwise medians remain validation data and are no longer connected as an apparent daily route.
- Actual QA: 5D `38/5/23/34% · 120 episodes · 5 path points`, 20D `43/10/21/26% · 42 episodes · 20 path points`; both remain `PROVISIONAL / 방향 우위 미확인`. `관측만` removes the forecast line, ranges, and terminal.
- Desktop and 420px Browser QA passed with distinct 5D / 20D coordinates, no horizontal overflow, and zero console errors. The horizon cards remain the primary numeric probability surface.

## Roadmap State

- 1차 설계 계약: approved
- 2차 상세 구현 계획: written
- 3차 service / validation implementation: complete
- 4차 React Workbench V2: complete
- 5차 actual QA / docs sync: complete
- 후속 1차 readable map implementation: complete
- 후속 2차 actual QA / docs sync: complete
- 경험적 경로 후속 1차 설계: complete
- 경험적 경로 후속 2차 상세 계획: complete
- 경험적 경로 후속 3차 service / validation: complete
- 경험적 경로 후속 4차 payload / React UI: complete
- 경험적 경로 후속 5차 actual QA / docs sync: complete
- 예상 순이동 후속 1차 설계: complete
- 예상 순이동 후속 2차 TDD 구현: complete
- 예상 순이동 후속 3차 actual QA / docs sync: complete
- 관측/전망 상태 분리 1차 Python contract: complete
- 관측/전망 상태 분리 2차 React UI: complete
- 10년 검증 3차 shared ingestion/materialization contract: complete
- 10년 검증 4차 actual backfill / re-evaluation / QA: complete
- 조건부 5차 model-quality revision: not started

## Next Action

기존 전체 roadmap `5/5`, readable-map 후속 `2/2`, empirical-path 후속 `5/5`, net-direction 후속 `3/3`와 이번 권장 개선 `4/4`가 완료됐다.

Ten-year actual validation has 120 independent 5D episodes and 88 independent 20D episodes. 5D probability quality passes but path error / coverage fail; 20D Brier improvement / fold stability / coverage fail. Both remain `PROVISIONAL`.
다음 작업은 필수가 아니다. 사용자가 별도로 승인하면 `RISKS.md`의 측정 실패를 기준으로 조건부 5차 model-quality revision을 새 설계부터 시작한다.

## 2026-07-18 Conditional Path Readability Follow-up

- User found the three q25~q75 boxes, large endpoint arrows, current marker, and terminal marker too concentrated to read.
- User approved A안: preserve the empirical path and four-quadrant color system, render only the selected horizon terminal range as one subtle shaded rectangle, and keep probability / validation logic unchanged.
- Approved marker contract: current `r=10`, terminal `r=8`, fixed 9-unit arrows with `markerUnits=userSpaceOnUse`, arrows on mid-line direction segments rather than endpoint circles.
- Approved copy: `5일 후 예상 위치` / `20일 후 예상 위치`; detailed episode and q25~q75 text leaves the graph and stays in reading / method disclosure.
- Written design: `CONDITIONAL_PATH_READABILITY_DESIGN.md`.
- Implementation plan: `CONDITIONAL_PATH_READABILITY_PLAN.md`.
- Implementation commits: `ef6d1973` terminal-only range, `3ed91a05` fixed mid-line direction markers and production bundle.
- Actual Browser QA: observed `0/0/0/0` forecast layers; 5D step-5 box `1`, path/direction/terminal `1/1/1`; 20D step-20 box `1`, path/direction/terminal `1/1/1`. Current/terminal labels do not overlap their circles.
- At 420px the workbench and document both measured `clientWidth == scrollWidth` (`377px`); all graph labels stayed inside the canvas and console errors were 0.
- QA screenshot: `/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-single-range-qa.png` (generated, not staged).
- Current stage: conditional-path readability roadmap complete (`5/5`).
- Stable-coordinate follow-up complete: selected-horizon auto-fit was replaced with one shared 5D / 20D visible-data coordinate system in `766dada9`; hidden intermediate q25/q75 no longer stretches the scale.
- Actual Browser QA found the same three anchor coordinates in `관측만 / 5D / 20D`: `(456.8966, 175.9529)`, `(306.1657, 130.9592)`, `(193.1737, 206.1591)`. The selected forecast line, terminal, and step-5/step-20 range still change by horizon.
- At 420px the workbench and document both measured `clientWidth == scrollWidth` (`377px`), all graph labels stayed inside the canvas, and console errors were 0. Stable-coordinate roadmap is complete (`3/3`).
- QA screenshot: `/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-stable-coordinate-qa.png` (generated, not staged).

## 2026-07-19 Net Direction Follow-up

- User noted that the dashed forecast appeared to reverse direction repeatedly. Root cause: each step's componentwise median was calculated independently across similar episodes, so connecting all steps looked like one coherent route even though it was not one representative historical path.
- Approved UI contract: render one direct dashed `현재 → 말일 예상 중앙 위치` line, keep the terminal range / circle / fixed direction marker, and retain stepwise service/payload statistics only for validation.
- TDD implementation commit: `9e40341c`. The common bound now uses observed anchors and both terminal/ranges; hidden intermediate medians no longer affect scale.
- Actual Browser QA: 5D and 20D each rendered one SVG `line`, and its start/end exactly matched the current/terminal circle centers. 5D terminal `(226.801050, 192.529943)` and 20D terminal `(256.660352, 186.525904)` differed while all three observed anchor tuples stayed identical.
- `관측만` forecast/range/direction/terminal counts were `0/0/0/0`. Desktop and 420px had no horizontal overflow, all graph labels stayed inside the canvas, and console errors were 0.
- QA screenshot: `/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-net-direction-qa.png` (generated, not staged).
