# Active Finance Tasks

Status: Active
Last Verified: 2026-07-22

이 폴더는 현재 실행 중인 task 기록과, 아직 archive / done 이동을 하지 않은 retained task 기록을 함께 둔다.

현재 상태를 볼 때는 이 폴더의 모든 하위 폴더를 literal active work로 해석하지 않는다.
현재 작업은 [STATUS_MANIFEST.md](./STATUS_MANIFEST.md), 아래 `Current Active Tasks`, [Roadmap](../../docs/ROADMAP.md)을 우선 확인한다.

권장 구조:

```text
tasks/active/<task-name>/
  PLAN.md
  DESIGN.md
  STATUS.md
  NOTES.md
  RUNS.md
  RISKS.md
```

작은 단일 파일 수정에는 task 문서를 만들지 않아도 된다.
여러 파일을 건드리거나, 조사 / 설계 / QA가 필요한 작업은 active task로 관리한다.

## Current Active Tasks

| Task | Status | Notes |
|---|---|---|
| `overview-sentiment-cnn-aaii-v1-20260719` | 2/4 complete | 1차 균형형 UI와 2차 PIT 이중 저장·known-at 조회·장기 그래프를 완료했다. 다음은 독립 데이터 후보 검토다. |
| `portfolio-monitoring-chart-zoom-pan-v1-20260719` | Parallel follow-up, 2/3 complete | 구현과 자동 회귀는 완료했다. 실제 desktop/900px/420px interaction·layout·overflow Browser QA가 남아 있다. |
| `market-movers-chart-navigation-polish-v1-20260721` | Parallel follow-up, implementation complete | 재무 날짜축·exact hover·가로 drag와 가격 readout tone 구현·자동 회귀는 완료했다. 실제 Browser interaction QA가 남아 있다. |

## Recent Completed / Retained Current Work

| Task | Status | Notes |
|---|---|---|
| `final-review-liquidity-evidence-copy-v1-20260722` | Latest completed record, 2/2 | stable liquidity proof status와 Gate는 유지하고 Level3 카드 제목·현황·설명·기준만 사용자 문구로 변환했다. |
| `practical-validation-final-review-route-fix-v1-20260722` | Latest completed record, 3/3 | 저장/이동 intent를 fragment callback 선소비에서 분리하고 stable validation id 중복 append를 막아 방금 인계한 후보의 Final Review를 한 번의 클릭으로 연다. |
| `today-contributor-performance-cards-v1-20260722` | Latest completed record, 4/4 | Today의 기여 상위 2·하위 2를 현금흐름 조정 종목 수익률과 포트폴리오 누적 기여를 분리한 compact card로 정리하고 actual Browser QA를 완료했다. |
| `portfolio-monitoring-initial-setting-correction-v1-20260721` | Completed record, 4/4 | 최초 요청 시작일과 수량을 append-only revision으로 함께 정정하고 새 DB 시장일·종가·최초 투자금부터 성과를 다시 계산한다. |
| `overview-economic-cycle-intramonth-nowcast-v1-20260721` | Completed record, 4/4 | 월말 canonical history를 보존하면서 날짜별 intramonth nowcast와 평일 fail-closed 증분 갱신을 완료했다. |
| `overview-futures-macro-probabilistic-state-outlook-v2-20260720` | Completed record, 3/3 | completed-session same-state target과 nested rolling-origin gate를 완료했고 actual 5D/20D는 `NO_EDGE`로 비공개다. |
| `portfolio-monitoring-reference-help-removal-v1-20260721` | Completed record, 2/2 | 중복 contextual help를 제거하고 canonical Reference Center의 journey·scenario·stale 안내를 보존했다. |
| `market-movers-period-refresh-chart-fix-v1-20260721` | Completed record, 3/3 | Weekly/Monthly bounded refresh, 신규 상장 기간 eligibility, 날짜축·tooltip과 선택 기간별 수익률을 완료했다. |
| `reference-center-react-v1-20260720` | Completed record, 4/4 | Search-first React Reference, curated catalog/drift guard, stable contextual deep link, legacy Guides/Glossary removal과 responsive Browser QA를 완료했다. |
| `operations-portfolio-monitoring-only-v1-20260719` | Completed record | Operations를 Portfolio Monitoring 단일 화면으로 정리하고 Ingestion 기록·로그·failure 기능은 보존했다. |
| `overview-futures-macro-pattern-outlook-v1-20260718` | Completed record | 10년 compact snapshot, 관측·전망 상태 분리, 5D 120개·20D 88개 독립 episode 재검증과 actual responsive QA를 완료했다. |
| `backtest-analysis-level1-decision-workspace-v1-20260717` | Completed record | 1~15차 Level1 one-shell과 Portfolio Mix React one-shell 구현·QA를 완료했다. |
| `practical-validation-audit-evidence-absorption-v1-20260719` | Completed record | raw source/replay/validation UI를 제거하고 compact provenance를 Step 1/2/4에 흡수하는 전체 roadmap `3/3`을 완료했다. |
| `backtest-component-static-distribution-v1-20260719` | Completed record | 원래 12개와 merge 후 Portfolio Mix를 포함한 Backtest React component 13개의 canonical Git 배포 산출물을 `component_static/`으로 통일했다. |
| `institutional-13f-openfigi-mapping-v1-20260718` | Completed record | 무료 OpenFIGI current resolution, error-preserving UPSERT, safe loader precedence, curated-manager actual backfill과 Browser QA를 전체 roadmap `4/4`로 완료했다. |
| `institutional-portfolios-context-first-redesign-v1-20260718` | Completed record | 선택 기관 context hero, coverage / comparison gate, full holdings explorer, explicit security search, mapped / unresolved flow와 actual responsive QA를 전체 roadmap `4/4`로 완료했다. |
| `overview-economic-cycle-sp500-actual-eps-registration-v1-20260718` | Completed implementation / external input pending | 공식 S&P Index Earnings workbook parser, release-vintage persistence, PIT loader와 Ingestion 등록 경로는 완료했다. 실제 workbook과 발표일 등록 전까지 actual TTM EPS는 자료 부족을 유지한다. |
| `overview-market-context-turnaround-derived-quarter-provenance-v1-20260716` | Completed record | Explicit concept family의 확정 FY/Q1/Q2/Q3로 missing Q4를 안전하게 산출하고 per-metric/TTM provenance와 `공시 기반 산출` 표시를 추가했다. |
| `overview-market-context-turnaround-stage-semantics-fix-v1-20260716` | Completed record | AAPL canonical `USD per share` EPS reader를 복구하고, 6개 rail에서 전환 신호·이미 양수·PER 적용 가능·흑자지만 개선폭 미달을 독립적으로 구분했다. |
| `overview-market-context-us-stock-freshness-refresh-v1-20260715` | Completed record | 선택 종목 cached UI를 DB-only로 열고, 마지막 완료 NYSE 거래일보다 자료가 뒤처질 때만 상단 single CTA로 exact scope를 갱신한다. profile/price는 CIK 없이 실행하고 SEC statement만 identity를 요구한다. |
| `overview-market-context-us-stock-turnaround-analysis-v1-20260715` | Completed record | 미국 개별주식 내부에 `PER 상대가치 | 전환 분석`을 추가하고 quarterly filing 기반 영업·현금 전환, survival risk, stage-appropriate valuation readiness를 selected-company 범위로 구현했다. |
| `overview-market-context-us-stock-valuation-v1-20260714` | Completed record | searchable 미국 개별주 DB-only PER 상대가치, split-neutral filing-aware TTM, 부분 1/3/5년 history와 explicit selected-symbol 수집 경계를 구현했다. |
| `institutional-portfolios-security-detail-chart-layout-v1-20260712` | Completed record | Selected-security detail now uses overview/context cards, full-width stored-OHLCV chart row with volume/navigator, and lower scrollable holder list. |
| `institutional-portfolios-watchlist-mapping-v1-20260712` | Completed record | Expanded guru aliases and DB-backed watchlist lookup, alias-prioritized manager search, ambiguous CUSIP-symbol guardrails, and distinct selected-security price states. |
| `institutional-portfolios-two-tier-tabs-v1-20260712` | Completed record | Workbench tabs now use primary `포트폴리오 / 종목 분석` tabs with context-specific secondary tabs. |
| `institutional-portfolios-portfolio-security-ia-v1-20260712` | Completed record | Workbench tabs now separate manager portfolio views from ticker/security analysis views. |
| `institutional-portfolios-interactive-security-chart-v1-20260712` | Completed record | Selected-security chart now uses stored OHLCV payload with hover tooltip, dotted guides, range slider, pan controls, and line/candle mode. |
| `institutional-portfolios-holding-chart-refresh-v1-20260712` | Completed record | Selected-security chart can resolve stored DB prices through safe CUSIP-symbol mapping and trigger bounded OHLCV collection when missing. |
| `institutional-portfolios-live-sec13f-v1-20260709` | Completed record | SEC official 13F live data path, refresh status, watchlist rail, secondary refresh action, conservative CUSIP-symbol enrichment, docs, and Browser QA. |
| `institutional-portfolios-react-workbench-v1-20260709` | Completed record | React visual workbench for Institutional Portfolios first screen, with preview fallback and visual payload contract. |
| `final-review-evidence-closure-contract-v1-20260712` | Completed record | Level2 actionable gap을 Final Review 승격 전에 닫고, Final Review의 accepted limit / Monitoring transfer / defer / block terminal state와 measured-only score impact를 구현했다. |
| `overview-market-context-sp500-valuation-v1-20260712` | Completed record | Market Context를 Shiller 상대 멀티플과 FOMC SEP 기반 1/3/5년 SPX valuation scenario의 두 React 그래프로 교체했다. |
| `practical-validation-recheck-handoff-loop-fix-v1-20260712` | Completed record | 자료 보강 뒤 replay를 강제 초기화하고, Flow 2 재검증과 새 validation 저장 전에는 Final Review 이동을 막는다. Final Review는 source별 최신 validation만 사용한다. |
| `practical-validation-pre-final-enrichment-gate-v1-20260712` | Completed record | 해결 가능한 필수 provider gap을 Practical Validation 승격 전 blocker로 바꾸고, Final Review의 legacy / stale 검토서는 2단계 재검증 전 읽기 전용 복구 상태로 제한했다. |
| `final-review-readable-review-evidence-v1-20260711` | Completed record | `남은 판단 근거`를 사용자 언어와 개선 행동으로 바꾸고, 실행 가능한 provider gap만 같은 후보의 Practical Validation 보강 화면으로 연결했다. |
| `final-review-guidance-actionability-v1-20260711` | Completed record | 10개 Monitoring 패턴을 structured applicability/action state로 바꾸고, 첫 화면 최대 6개 행동 가이드, 접힌 technical trace, Level2/Final Review stage ownership, 총평 직후 해석 4행을 구현했다. |
| `portfolio-workflow-legacy-reset-rebuild-20260711` | Completed record | 기존 6개 Final Review 후보를 current source → Practical Validation → Final Review schema로 재생성하고 Monitoring setup을 새 decision ID에 연결했다. legacy `SAVED_PORTFOLIOS.jsonl`은 요청대로 제거했다. |
| `final-review-candidate-selection-integration-v1-20260710` | Completed record | Final Review standalone `Step 1 / Candidate Board`를 제거하고, Review Queue / 검토 대상 selector / 후보 비교 상세를 Decision Desk 아래 후보 선택 패널로 통합했다. |
| `final-review-sentiment-scope-cleanup-v1-20260710` | Completed record | Final Review first-read에서 CNN / AAII 시장심리 패널과 raw detail expander를 제거했다. 시장심리 해석은 `Workspace > Overview > Sentiment`가 소유하고, Final Review gate / score / 저장 / Monitoring signal에는 연결하지 않는다. |
| `practical-validation-flow4-action-center-v1-20260709` | Completed record | Practical Validation Flow 4 `데이터 보강 대상`과 기존 Python 수집 버튼을 `데이터 보강 / 수집 실행` action center로 묶고, 버튼 주변에 `수집하는 것 / 하지 않는 것 / 실행 후 다음 단계`를 명확히 표시한다. |
| `practical-validation-flow4-data-action-board-v1-20260709` | Completed record | Practical Validation Flow 4 now reads `카테고리별 검증 결과 -> 데이터 보강 대상 / 액션 -> 상세 근거 / 원자료`; React board is display-only and Python keeps provider collection / validation / gate / persistence boundaries. |
| `practical-validation-flow-gating-evidence-ia-v1-20260708` | Completed record | Flow 2 current-session replay gates Flow 3 / Flow 4 / Flow 5 rendering and Flow 4 lower evidence IA was lowered behind provider action flow. |
| `practical-validation-category-empty-state-v1-20260708` | Completed record | Flow 4 visible category result hides REVIEW-only / empty groups while retaining them in the internal read model. |
| `post-merge-docs-flow-refresh-20260708` | Completed record | 2026-07-08 master 병합 후 current pointer, code flow docs, Overview surface names, and runbook boundaries were refreshed without changing code behavior or registry / saved JSONL. |
| `practical-validation-boundary-cleanup-v1-20260708` | Completed record | Practical Validation Flow 3 / Flow 4 visible UI now separates current validation fix work from Final Review judgment items. |
| `practical-validation-flow4-final-review-handoff-v1-20260708` | Completed record | Flow 4 reduced Final Review-only REVIEW items from current validation problem detail; later Boundary Cleanup removed the visible handoff count from Flow 3 / Flow 4. |
| `practical-validation-flow4-outcome-taxonomy-v1-20260708` | Completed record | Flow 4 outcome labels separate pass, recheck-needed, Final Review judgment, and blocked meanings while preserving `Current=REVIEW` where appropriate. |
| `practical-validation-required-taxonomy-refactor-v1-20260708` | Completed record | `validation_efficacy` ownership was narrowed to method-strength checks; replay, benchmark, PIT, survivorship, provider freshness, and robustness stay with their owner modules. |
| `practical-validation-required-taxonomy-audit-v1-20260708` | Completed record | Practical Validation 1차 필수 검증의 current row inventory와 owner matrix를 정리했다. `validation_efficacy` 중복 소유권을 확인했고, 다음 코드 작업은 method-strength 축소와 owner-module gate refactor다. |
| `backtest-symbol-resolver-v1-20260708` | Completed record | Backtest Quality / Value Factor Readiness can distinguish stale price data from ticker-change symbol identity issues and store active repair metadata without rewriting source ticker identity. |
| `backtest-factor-readiness-action-ui-v1-20260707` | Completed record | Strict factor readiness UI now shows affected tickers, impact, and bounded repair actions instead of raw diagnostic fields. |
| `backtest-coverage-provider-gap-refresh-v1-20260707` | Completed record | Backtest Data Trust Coverage 최신화 no-row provider gap result no longer re-renders the retry action card; persistent provider/source gap symbols are excluded from refresh targets. |
| `practical-validation-flow4-action-steps-v3-20260707` | Completed record | Practical Validation Flow 4 `해결 방법` now renders numbered action steps instead of a slash-joined paragraph. |
| `practical-validation-flow4-action-guide-v2-20260707` | Completed record | Practical Validation Flow 4 criteria cards show `검증한 것 / 해결해야 할 항목 / 해결 방법 / 통과 기준 / 위치`, with location demoted to supporting context. |
| `practical-validation-flow4-resolution-guide-v1-20260707` | Completed record | Practical Validation Flow 4 introduced `resolution_guide` so location-only guidance became a user-facing action guide. |
| `practical-validation-flow3-conclusion-summary-v1-20260706` | Completed record | Practical Validation Flow 3 now reads as a compact validation conclusion summary. Detailed issue cause / module details moved to Flow 4. |
| `practical-validation-category-results-v1-20260706` | Completed record | Practical Validation Flow 4 now reads as category-first validation results. Selected-route preflight is separated into handoff summary, stress / construction / sentiment gate severity is reduced where appropriate. |
| `practical-validation-flow3-clarity-v1-20260706` | Completed record | Practical Validation Flow 3 first-read surface cleanup. Removed duplicate control center / alert / badge layers and made the React Fix Queue focus on Final Review movement judgment, first fix work, and compact evidence summary. |
| `practical-validation-entry-simplification-v1-20260705` | Completed record | Practical Validation default entry removed contextual Reference help and context-only sentiment overlay, renamed the command center, and changed custom cards / Fix Queue React surfaces to white square surfaces. |
| `practical-validation-taxonomy-roadmap-v1-20260705` | Completed record | Practical Validation V1-V8 taxonomy and implementation round. Workspace read model, 5-flow page, read-only React Fix Queue, Flow 3 workspace panel, normalized status display, and durable docs alignment were completed. |
| `fundamental-source-migration-p8-final-docs-runbook-alignment` | Completed record | 재무제표 source migration 1~9차 closeout. EDGAR statement shadow를 canonical financial statement path로, broad yfinance fundamentals / factors를 legacy compatibility로 durable docs와 runbook에 정렬했다. |
| `fundamental-source-migration-p7-legacy-yfinance-decommission` | Completed record | Ingestion active UI에서 broad yfinance fundamentals / factors 실행 카드를 제거하고, old run history / saved replay용 action handlers와 broad Quality Snapshot compatibility를 유지했다. |
| `gtaa-result-cadence-monthly-valuation-20260629` | Completed record | GTAA `interval` now means strategy-owned rebalance cadence, not input row thinning. Month-end runtime appends the latest common trading day row at or before the requested end date, so non-rebalance months can still show candidate signal / valuation context. |
| `overview-final-cleanup-v33-v36-20260629` | Completed record | `Workspace > Overview` V33-V36. UI component bodies now live under `app/web/overview/components/*`, `overview_dashboard.py` is a 1-export wrapper, `app/services/overview_market_intelligence.py` was removed, and Data Health scope / coverage counts separate direct Market Context from reference / dedicated-tab sources. |
| `overview-service-split-v25-v32-20260629` | Completed record | `Workspace > Overview` V25-V32. Overview market intelligence read-model bodies now live in `app/services/overview/{market_context,market_movers,events,sentiment,data_health,why_it_moved}.py` instead of the old monolithic service facade. |
| `overview-legacy-dashboard-removal-v17-v24-20260625` | Completed record | `Workspace > Overview` V17-V24. Remaining helper ownership was moved into `app/web/overview/*_helpers.py`, `app/web/overview/legacy_dashboard.py` was deleted, and `overview_dashboard.py` now keeps explicit compatibility exports. QA passed with py_compile, Overview contract tests, legacy import scan, and Browser QA. |
| `overview-tab-helper-extraction-v11-v16-20260625` | Completed record | `Workspace > Overview` V11-V16. Market Context, Events, Futures Macro, Market Movers, and Sentiment entry modules now call tab-local helper bridge modules instead of importing `legacy_dashboard.py` directly. |
| `overview-legacy-cleanup-v6-v10-20260625` | Completed record | `Workspace > Overview` V6-V10. Navigation moved to `app/web/overview/navigation.py`, IA read-model ownership moved to `app/services/overview/ia.py`, confirmed unused standalone wrappers / Candidate Ops helpers were removed, and guard tests prevent reintroduction. |
| `overview-structure-split-v2-v5-20260625` | Completed record | `Workspace > Overview` V2-V5. Primary tab modules own tab orchestration, component surfaces and service surfaces were introduced, and Overview boundary guard contracts now protect active page / tab / component / service ownership. |
| `overview-tab-module-split-v1-20260625` | Completed record | `Workspace > Overview` V1. `overview_dashboard.py` became a compatibility wrapper, active page shell moved to `app/web/overview/page.py`, and primary tab entry modules were added for Market Context, Market Movers, Futures Macro, Sentiment, and Events. |
| `overview-primary-nav-pill-v1-20260623` | Completed record | `Workspace > Overview` primary navigation now uses a compact custom pill nav with Korean primary labels and English secondary labels instead of the default-looking Streamlit segmented/radio selector. Query-param tab slugs keep direct tab selection stable. No provider / schema / registry / saved / validation / monitoring / trade semantics changed. |
| `overview-primary-tab-soft-remove-v1-20260623` | Completed record | `Workspace > Overview` primary tab soft-remove. `Futures Monitor` and `Sector / Industry` are no longer primary selector options; old selected values fall back to `Market Context`. Futures / sector services and helper renderers are retained for now, with no provider / schema / registry / saved / trading boundary changes. |
| `overview-lazy-tab-render-v20-20260622` | Completed record | `Workspace > Overview` V20 follow-up. Top-level deep tabs switched to selected-tab lazy rendering with `Market Context` as default. Current primary tab membership is superseded by `overview-primary-tab-soft-remove-v1-20260623`; Candidate Ops dashboard snapshot loading remains deferred to its selected branch. |
| `overview-market-context-macro-meaning-gradient-v19-20260622` | Completed record | `Overview > Market Context` V19 follow-up. Historical analog / Macro conditioned comparison matrix cells now use clearer green/red return gradients, and reference-only T10Y3M / VIXCLS / BAA10Y cards explain what each current value means without changing hard-condition or data boundaries. |
| `overview-market-context-analog-usability-v12-20260621` | Completed record | `Overview > Market Context` V12 follow-up. Historical analog selected-as-of common price basis mismatch now has a bounded price-basis refresh action, the basis/method area is deduped into compact summary + collapsed technical details, and core/support asset outcomes render as matrix/summary before detailed tables. |
| `overview-market-context-session-basis-v9-20260620` | Completed record | `Overview > Market Context` V9 follow-up. 휴장 / 장외 시간에는 `오늘의 시장 브리프` 대신 마지막 거래일 또는 현재 세션 기준 브리프로 읽고, 장중 snapshot age만으로 현재 보강 이슈를 띄우지 않도록 보정했다. |
| `overview-market-context-source-actionability-v8-20260620` | Completed record | `Overview > Market Context` V8 follow-up. Events estimate caveats는 `참고 제한`, Data Health는 `관리 메타`로 분리하고, top `자료 상태`와 source confidence summary는 보강 가능한 자료만 unresolved로 세도록 고쳤다. |
| `overview-market-context-smart-refresh-v7-20260620` | Completed record | `Overview > Market Context` V7 follow-up. Events를 브리프에서 낮추고, smart refresh / full refresh fallback / result reflection을 정리했다. |
| `overview-market-context-brief-context-absorption-v6-20260620` | Completed record | `Overview > Market Context` V6 follow-up. `브리프 신뢰도` 독립 섹션을 제거하고, Events / Futures 자료 제한은 `오늘의 시장 브리프`의 시장맥락 결론으로 흡수했다. |
| `overview-market-context-brief-confidence-v5-20260620` | Completed record | `Overview > Market Context` V5 follow-up. `오늘의 시장 브리프`는 움직임 / 확산 / Futures-Macro 3행 market story로 유지하고, Events / 자료 기준은 별도 `브리프 신뢰도` 영역으로 분리했다. |
| `overview-market-context-brief-findings-integration-v4-20260620` | Completed record | `Overview > Market Context` V4 follow-up. `맥락 검토 결과` rail의 P1/P2 중복을 제거하고 Events / 자료 신뢰도 caveat를 `오늘의 시장 브리프` 안으로 통합했다. |
| `overview-market-context-context-findings-v3-20260620` | Completed record | `Overview > Market Context` V3 follow-up. `다음 맥락 체크` user action checklist를 `맥락 검토 결과`로 바꾸고, 가격 움직임 / Futures-Macro / Events / 자료 신뢰도 caveat를 결론, 해석 영향, 자료 기준으로 보여준다. |
| `overview-market-context-futures-conditioned-analog-v3b-20260618` | Completed record | `Overview > Market Context` 3차-B. 3차-A의 GLD `Macro 조건 포함 pilot`에 stored futures daily OHLCV 기반 Rate Pressure proxy (`ZN=F` / `ZB=F`) 조건 1개를 추가했다. FRED / events / sentiment / 새 provider / schema / loader는 열지 않았다. |
| `overview-market-context-macro-conditioned-analog-pilot-v1-20260618` | Completed record | `Overview > Market Context` 3차-A. Historical analog broad 결과는 유지하면서 `Macro 조건 포함 pilot` 별도 영역을 추가했고, 추가 조건은 stored GLD price proxy context 1개만 사용했다. Futures / FRED rates / events / sentiment는 deferred / disabled / insufficient condition으로 표시한다. |
| `overview-market-context-analog-asof-window-v2-20260618` | Completed record | `Overview > Market Context` 2차. Historical analog에 latest / 과거 기준 시점 replay와 5D / 20D / monthly pattern window controls를 추가했고, existing DB 기준 bounded replay와 full PIT replay 한계를 분리한 기록이다. |
| `overview-market-context-source-action-flow-v1-20260618` | Completed record | `Overview > Market Context` 1차. `next_checks`를 실제 source/action checklist로 렌더링하고, Data Health / Events 확인 이유와 action, source confidence footer action hint, historical analog 기준일 / 자료기간 / 계산식 표시를 보강한 기록이다. |
| `finance-integration-doc-merge-skill-20260617` | Completed record | `finance-integration-review`에 `.aiworkspace/note/finance` 문서 충돌 전용 checklist를 추가해, latest/current pointer와 root handoff log를 손실 없이 자연스럽게 병합하도록 강화한 기록이다. |
| `overview-market-movers-period-refresh-v1-20260616` | Completed record | `Overview > Market Movers` period refresh UX. Daily keeps intraday snapshot / auto refresh controls; Weekly / Monthly / Yearly now expose an EOD price-history manual refresh action through the existing Overview action facade and OHLCV job boundary. |
| `overview-market-context-analog-readability-v5-20260616` | Completed record | `Overview > Market Context` V5. Historical analog OK state now explains the similarity rule before statistics, shows a compact summary strip / first-read conclusion, and splits detailed rows into core vs supporting assets without changing the context-only calculation. |
| `overview-market-context-analog-repair-v4-20260615` | Completed record | `Overview > Market Context` V4. Historical analog `자료 부족`을 부족 ETF / row evidence / `보조 갱신` OHLCV repair action으로 연결하고, `자료 기준 / 출처 상태` summary에 정상 / 확인 / 부족 count와 source pill을 표시한 기록이다. |
| `overview-market-context-historical-analog-v1-20260615` | Completed record | `Overview > Market Context` historical analog MVP. Current sector leadership을 sector ETF proxy로 연결하고, coverage가 충분할 때만 5D / 20D / 60D historical analog summary를 보여주는 context-only 기록이다. Sector ETF coverage가 부족하면 V4 repair action으로 이어진다. |
| `overview-market-context-events-data-trust-v1-20260612` | Completed record | `Overview > Market Context / Events` 3차. 주요 macro event read model을 recent 7D + upcoming 관점으로 보강하고, Macro Week Lane recent/upcoming split, compact Market Context event cue, BLS CPI/PPI abbreviation parser coverage를 추가한 기록이다. |
| `risk-parity-dual-momentum-5b-20260610` | Completed record | Backtest 5B. Risk Parity Trend의 inverse-vol / guardrail / low-vol overweight diagnostics와 Dual Momentum의 trend-rejected cash proxy / concentration / whipsaw diagnostics를 result row/meta와 기존 Selection History에서 읽게 한 기록이다. |
| `global-relative-strength-5a-20260609` | Completed record | Backtest 5A. Global Relative Strength 전략 runtime / transform / result bundle 고도화. 새 evidence/log/workbench 패널과 registry / saved JSONL / run_history / generated artifact write는 제외했다. |
| `backtest-analysis-direction-reset-20260609` | Completed record | Backtest 4차 4C. Backtest Analysis를 전략 실행 / 비교 / 후보 생성 중심으로 되돌리고, Reference / evidence / governance / ETF workbench 패널은 `전략 개발 참고` advanced control 뒤에 숨긴다. |
| `etf-rerun-matrix-workbench-20260608` | Completed record | Backtest 4차 4B. GRS / Risk Parity / Dual Momentum의 rerun scenario matrix를 보여주고, 선택한 ETF 전략만 session-only로 실행해 compact result evidence를 표시한다. |
| `etf-current-anchor-workbench-20260608` | Completed record | Backtest 4차 4A. 기존 run history / Practical Validation source handoff row를 읽어 GRS / Risk Parity / Dual Momentum의 current-anchor readiness와 missing evidence를 read-only로 보여준다. |
| `etf-evidence-expansion-20260608` | Completed record | Backtest 3차 3D. GRS / Risk Parity / Dual Momentum의 current anchor / near miss / not-ready reason / required evidence / next workflow를 read-only로 보여준다. |
| `risk-on-momentum-governance-20260608` | Completed record | Backtest 3차 3C. Risk-On Momentum 5D의 Daily Swing research evidence와 deferred validation / review / monitoring governance module을 read-only로 보여준다. |
| `strict-annual-etf-bridge-20260608` | Completed record | Backtest 3차 3B. Strict Annual 3종 + GTAA / Equal Weight bridge를 read-only로 정리해 component role / validation gap / recommended workflow를 보여준다. |
| `strategy-evidence-inventory-direction-panel-20260608` | Completed record | Backtest 3차 3A. Strategy Evidence Inventory / Direction Panel을 read-only로 구현해 catalog strategy별 maturity / evidence / next action을 보여준다. |
| `distinct-strategy-portfolio-discovery-20260609` | Completed record | GTAA U3 85% / GRS Compact 10% / Risk Parity Trend 5% distinct-family 후보를 Final Review decision `final_distinct_strategy_gtaa_u3_grs_risk_parity_20260609`와 Monitoring setup `selected_dashboard_portfolio_distinct_strategy_gtaa_grs_rp_20260609`까지 등록한 기록이다. |
| `portfolio-discovery-final-review-monitoring-20260608` | Completed record | 현행 전략 전체를 탐색해 GTAA U5 20% / GTAA U3 75% / GRS Compact 5% all-ETF 후보를 Final Review / Portfolio Monitoring chain까지 등록한 기록이다. |
| `overview-data-health-ingestion-handoff-v1-20260608` | Completed record | `Workspace > Overview > Data Health` 상단에 priority-ranked read-only handoff lane을 추가해 stale / missing / failed / partial / due target을 owning collection surface로 연결한 기록이다. |
| `overview-macro-context-cockpit-v1-20260608` | Completed record | `Workspace > Overview` 상단에 기존 DB-backed market context / sentiment / events / data-health snapshot을 합성한 summary-first cockpit을 추가한 기록이다. |
| `merge-review-fixes-20260608` | Completed record | sub-dev / main-dev master merge review 후 Reference internal link, Reference V4 status, catalog test assertion을 바로잡은 기록이다. |
| `reference-drift-guard-qa-polish-v5-20260608` | Completed record | contextual Reference help가 Glossary term / Reference link boundary에서 drift되지 않도록 guard와 표시 polish를 추가한 5차 기록이다. |
| `reference-contextual-links-v4-20260608` | Completed record | 주요 Backtest / Operations 화면에 read-only Reference help expander를 연결한 4차 기록이다. |
| `reference-glossary-concept-dictionary-v3-20260607` | Completed record | `Reference > Guides`와 `Reference > Glossary`가 같은 Streamlit-free concept dictionary와 search helper를 쓰도록 통합한 3차 기록이다. |
| `reference-guides-journey-playbooks-v2-20260607` | Completed record | `Reference > Guides`의 journey 상세, failure state, troubleshooting check step, evidence location을 확장한 2차 기록이다. |
| `reference-guides-center-v1-20260607` | Completed record | `Reference > Guides`를 task-first Reference Center로 개편하고, 기존 portfolio-selection guide를 `Portfolio Selection Journey`로 보존한 기록이다. |
| `futures-monitor-stale-refresh-fix-20260607` | Completed record | Overview Futures Monitor가 현재 UTC lookback 밖의 최신 저장 1m candle을 `Missing`처럼 숨기지 않고, latest stored candle 기준으로 차트를 표시하면서 stale status를 유지하도록 고친 기록이다. |
| `operations-v2-closeout-20260608` | Completed record | Operations Overview V2 5차 closeout. 1차~4차 개편을 최종 QA / runbook / durable docs 기준으로 닫고 normal top-navigation QA path와 direct route diagnostic을 분리한 기록이다. |
| `operations-review-queue-refinement-20260608` | Completed record | Operations Overview V2 4차. Today's Operations Queue를 priority / evidence / metric 기반 review queue로 재정렬해 setup blocker, system run failure, scenario freshness, open review, routine monitoring을 분리한 기록이다. |
| `operations-evidence-health-strip-20260607` | Completed record | Operations Overview V2 3차. Operations Console 상단에 Evidence Health mini strip을 추가해 scenario freshness / selected evidence readiness / open review / system run health를 한 줄로 확인하게 한 기록이다. |
| `operations-portfolio-first-summary-20260607` | Completed record | Operations Overview V2 2차. Operations Console 상단에 Portfolio Monitoring Status summary를 추가해 active portfolio / assigned strategy / stale scenario / blocked / missing / open review / next review를 먼저 읽게 한 기록이다. |
| `operations-cockpit-cleanup-20260607` | Completed record | Operations Overview V2 1차 cleanup. 사용자-facing Operations Overview에서 archive / development-history decision table과 roadmap 흔적을 제거하고 Portfolio Monitoring / System Data Health 중심 cockpit copy로 정리한 기록이다. |
| `refactor-round-closeout-20260607` | Completed record | 10차 구조정리 라운드 closeout. 5차~9차 리팩토링 기준선을 감사하고, 남은 Backtest Compare / Overview / Operations split 후보를 후속 작업으로 분리한 기록이다. |
| `backtest-compare-components-split-20260607` | Completed record | 9차 Backtest Compare Streamlit split first pass. Portfolio Mix Builder visual shell을 `app/web/backtest_compare_components.py`로 이동하고 `app/web/backtest_compare.py`를 실행 / 상태 orchestration 중심으로 낮춘 기록이다. |
| `ingestion-diagnostic-facade-20260607` | Completed record | 7차 대형 Streamlit 파일 분해 7B. Ingestion read-only diagnostic orchestration을 `app/services/ingestion_diagnostics.py`로 이동하고 `app/web/ingestion_console.py`는 렌더 / 세션 상태에 집중하게 한 기록이다. |
| `runtime-backtest-strict-family-split-20260607` | Completed record | 8차 runtime 대형 파일 분해 8C. `app/runtime/backtest.py`의 strict quality / value / quality-value annual and quarterly runtime wrapper family를 `app/runtime/backtest_strict.py`로 이동하고 public facade import를 유지한 기록이다. |
| `runtime-backtest-real-money-split-20260607` | Completed record | 8차 runtime 대형 파일 분해 8B. `app/runtime/backtest.py`의 real-money / guardrail / benchmark / deployment readiness helper family를 `app/runtime/backtest_real_money.py`로 이동하고 public facade import를 유지한 기록이다. |
| `runtime-backtest-risk-on-momentum-split-20260607` | Completed record | 8차 runtime 대형 파일 분해 8A. `app/runtime/backtest.py`의 Risk-On Momentum 5D runtime slice를 `app/runtime/backtest_risk_on_momentum.py`로 이동하고 public facade import를 유지한 기록이다. |
| `streamlit-ingestion-console-split-20260607` | Completed record | 7차 대형 Streamlit 파일 분해 7A. `streamlit_app.py`를 Finance Console shell로 낮추고 `Workspace > Ingestion` render/state/job UI를 `app/web/ingestion_console.py`로 분리한 기록이다. |
| `overview-ingestion-action-boundary-20260607` | Completed record | 6차 수집 / 조회 경계 정리. Overview bounded refresh를 `app/jobs/overview_actions.py` action facade로 모으고, Overview UI의 직접 ingestion / automation / run-history import를 제거한 기록이다. |
| `code-boundary-refactor-audit-20260607` | Completed record | 5차 코드 구조 감사 / 리팩토링 기준선. UI / service / runtime / jobs / finance layer 경계, 대형 파일, 다음 refactor 우선순위를 정리한 기록이다. |
| `post-merge-verification-handoff-20260607` | Completed record | 4차 검증 및 handoff. 1차~3차 결과 검증과 다음 작업자 read order / remaining decisions를 정리한 기록이다. |
| `post-merge-active-state-cleanup-20260607` | Completed record | 3차 active task / phase 상태 정리. 대량 이동 없이 manifest / README / roadmap 기준으로 current state를 정리한 기록이다. |
| `post-merge-boundary-docs-alignment-20260607` | Completed record | 2차 구조 / 경계 문서 정리. UI / service / runtime / loader / DB / storage boundary를 durable docs에 맞춘 기록이다. |
| `post-merge-docs-alignment-20260607` | Completed record | 1차 post-merge docs alignment. 현재 제품 흐름 / 완료된 merged work / active 상태를 정리한 기록이다. |

## Retained Work Records

- 이 폴더에는 완료된 과거 task가 다수 남아 있다.
- 상세 구현 근거, 실행 로그, QA 결과를 찾을 때는 관련 task 폴더의 `STATUS.md`, `RUNS.md`, `NOTES.md`, `RISKS.md`를 확인한다.
- 2026-06-08 기준 194개 task folder가 retained record로 남아 있다. 대량 이동 / archive migration은 별도 승인된 migration task에서 처리한다.
