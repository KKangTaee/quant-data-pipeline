# Overview Market Context S&P 500 Valuation V1 Notes

Status: Active
Last Updated: 2026-07-12

## V1.2 Approved Direction

- V1.2의 최근 1년 화면에는 2025-06/09/12, 2026-03/06 공식 SEP vintage가 필요해 당시 네 release를 backfill했다. V1.4는 이 고정 범위를 Federal Reserve calendar 기반 21개 vintage로 대체했다.
- 월별 과거 지점은 월중 발표된 SEP를 다음 달부터 적용한다. 최신 EOD 지점만 기준일 이전 최신 release를 즉시 적용한다.
- target year는 관측 월의 calendar year를 선택한다.
- 시계열은 Shiller EPS가 strict historical release vintage가 아니므로 `과거 시점 재구성 시나리오`로 표시한다.
- 그래프 1은 `-2σ/-1σ/중심/+1σ/+2σ`를 대칭 표시하고, 그래프 2는 현재 자형 비교를 유지하면서 아래에 1년 흐름을 추가한다.

## V1.2 Final Implementation Decisions

- `collect_and_store_fomc_sep_history()`는 bounded official URL 집합 중 DB에 없는 release만 fetch한다. 기존 daily latest collector는 새 release 보존을 계속 담당한다.
- Shiller normalization은 EPS가 비어도 양수 price가 있으면 `data_quality=missing`, null EPS/PER row를 저장한다. Graph 1은 양수 PER만 사용하고 Graph 2 history는 마지막 양수 EPS와 basis date를 forward-fill한다.
- history의 monthly point는 release month 다음 달부터 새 SEP를 적용한다. 최신 EOD point는 exact as-of date까지 발표된 SEP를 적용한다.
- 1년 visible series는 12 points, multiple warmup은 60 completed PER months다. 실제 DB 결과는 2025-08~2026-07 12개 지점과 2025-09/12, 2026-03/06 marker를 반환했다.
- React redesign은 외부 chart dependency 없이 responsive SVG, hover inspector, actual/baseline/band/SEP legend를 사용한다.

## V1.3 Approved Decision

- DB evidence confirmed 2026-04~07 positive price rows with null EPS/PER and latest complete EPS/PER at 2026-03.
- Graph 1 distribution remains complete-only; post-March values are provisional display/current-position evidence only.
- June provisional PER is approximately `7450.03 / 261.723 = 28.47x`; July current EOD provisional PER is approximately `7575.39 / 261.723 = 28.94x`.
- Hover value changes already worked; only the inspector position was fixed by CSS. V1.3 moves it beside the selected point and flips it near the right edge.
- The earlier 1/3/5-year Graph 2 selector discussion remains deferred because the user approved this Graph 1 fix specifically.
- Distribution anchors and z-score continue to use the latest 60 complete Shiller PER observations ending 2026-03; provisional April-July values are presentation evidence only.
- July provisional PER uses current `^GSPC` EOD 7,575.39 at 2026-07-10 divided by March Shiller TTM EPS 261.723, while April-June use their stored Shiller monthly prices with the same EPS basis.
- Inspector position is calculated from the selected SVG point. It flips left after 72% of plot width and clamps the vertical anchor so high-multiple points do not clip the card at the chart top.
- V1.4 uses Federal Reserve calendar discovery rather than extending a hardcoded URL tuple. The live calendar exposed 21 parseable official releases from 2021-03-17 through 2026-06-17.
- A 60-month visible reconstruction with a 60-month rolling multiple needs 119 monthly rows including the first visible month. The loader default changed from 84 to 120 after live smoke showed 3y/5y histories truncating at 25 points.
- React receives `history_options` for `1y`, `3y`, and `5y`; selection only switches already-computed DB-backed evidence and never fetches or calculates provider data in the browser.
- Long windows retain every SEP marker line but render at most seven SEP text labels and seven x-axis labels to prevent overlap.

## Confirmed Decisions

- Exactly two primary valuation surfaces.
- Five-year/60-month log(PER) distribution is the official regime window.
- Three-year/36-month result is sensitivity evidence only.
- EPS basis should remain As-Reported across historical and current calculations.
- SPX owns valuation math; SPY is a same-date proportional conversion.
- FOMC SEP economic projections, not the interest-rate dots themselves, own GDP/PCE inputs.
- New SEP releases must be discovered and stored by vintage.
- Old Market Context visible UI must be removed.
- New visible UI must use React in the same product style as other React-backed Overview surfaces.

## Source Findings

- Shiller provides monthly price, earnings, CAPE, CPI, and 10-year rate research data.
- Shiller monthly earnings are interpolated from S&P quarterly four-quarter totals and are not strict PIT release-vintage proof.
- S&P Index Earnings exposes index earnings/estimates but automated workbook access may be restricted.
- LSEG I/B/E/S supports index aggregates and deep historical forward estimates but is licensed/deferred.

## Empirical Window Check

Using the latest complete Shiller earnings month available during design review, 2026-03:

- 3y log-multiple center: about 26.38x; current z about -0.52
- 5y log-multiple center: about 25.13x; current z about +0.11
- 10y log-multiple center: about 24.85x; current z about +0.17

This supports 5y as the primary window and 3y as regime sensitivity, not the main classification.

## 1차 Implementation Decisions

- Three finance_meta tables preserve monthly valuation, explicit EPS status/basis/release vintage, and SEP release vintage separately.
- Shiller rows are labeled `interpolated`; the collector never promotes them to strict PIT actual observations.
- S&P earnings import requires explicit `period_end`, `status`, and EPS columns. It does not infer actual/estimate from workbook formatting.
- The S&P official download can remain operator-supplied when automated access is blocked; release date is mandatory.
- SEP discovery selects the latest dated official accessible-material link and keeps every release as a separate vintage.

## 2차 Implementation Decisions

- Monthly valuation loading returns ascending months even though the DB query selects newest rows first.
- TTM evidence deduplicates a quarter by newest source release before selecting four quarters.
- A TTM value is returned only with four completed distinct quarters; fewer rows remain `INSUFFICIENT_HISTORY`.
- Official classification thresholds are log(PER) z-score `< -1 LOW`, `< 1 NEUTRAL`, `< 2 HIGH`, otherwise `EXTREME_HIGH`.
- The 36-month bucket never replaces the 60-month bucket; disagreement is exposed through `period_sensitive`.

## 3차 Implementation Decisions

- Nominal EPS sensitivity compounds SEP inputs as `(1 + real GDP) × (1 + PCE) - 1`; it does not simply add percentages.
- Conservative/baseline/optimistic use central-tendency lower/median/central-tendency upper endpoints respectively.
- SPX lower/baseline/upper scenarios combine the matching EPS sensitivity with -1σ/mean/+1σ trailing multiple values.
- SPY equivalents are proportional convenience values only and are omitted when SPX/SPY EOD dates differ.
- SEP older than 180 days relative to the SPX as-of date is marked `STALE_SEP` and blocks the index scenario.
- Mixed or non-actual EPS never enters the calculation; the read model returns Korean blocking reasons.

## 4차 Implementation Decisions

- The Market Context entrypoint owns only header + valuation render calls; old cockpit and refresh functions are no longer visible.
- React is presentation-only and receives a JSON-safe Python read model; no provider fetch or valuation formula runs in TypeScript.
- Both charts use responsive SVG and introduce no chart dependency.
- The main screen prioritizes valuation questions and evidence; source/method limitations are collapsed in a secondary disclosure.
- A compact Streamlit fallback exists only when the compiled React asset is unavailable.

## V1.1 Data Activation Decision

- Root cause 1: graph 1 was incorrectly nested under the actual-EPS readiness gate even though 1,863 Shiller monthly rows existed.
- Root cause 2: the S&P workbook connector was import-only and official automated download returned 403, leaving zero EPS rows.
- User approved an explicit hierarchy: official S&P actual quarters first, Shiller completed-quarter TTM proxy second.
- Official file acquisition stays a visible browser/manual step; the app owns validation, preview, status confirmation, vintage UPSERT, and automatic source promotion.

## V1.1 Final Implementation Decisions

- Latest user policy supersedes the planned uploader: no official workbook upload UI or download workaround is part of this implementation.
- Graph 1 derives current PER from the latest valid Shiller row and is independent of official EPS, current SPX, and SEP readiness.
- Graph 2 loader hierarchy is `official_actual` first and `interpolated_ttm_proxy` second; every selected result carries source, basis date, quality, and fallback reason.
- SEP expected EPS growth is median `real GDP + PCE`, not compounded growth. One baseline expected EPS is multiplied by the 5-year `-1σ / mean / +1σ` PER anchors.
- `current_vs_baseline_gap_pct` is positive when current SPX is above the baseline scenario and negative when below it.
