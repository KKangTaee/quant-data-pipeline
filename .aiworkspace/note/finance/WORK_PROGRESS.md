# Finance Work Progress

## Purpose
This file is the current, concise implementation log for `finance` package work.

Keep here:
- current active workstream
- recent major milestones
- durable handoff notes

Detailed historical logs were archived on `2026-04-13`.

## Active Pointers

- current phase board:
  - none. Open a new phase only after the user approves a concrete scope.
- latest completed phase:
  - [Phase 13 First-Cycle Hardening Closeout](./phases/done/phase13-hardening-cycle-closeout.md)
- current roadmap:
  - [Finance Roadmap](./docs/ROADMAP.md)
- overview operations runbook:
  - [Overview Market Intelligence Runbook](./docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md)
- current code map:
  - [Finance Project Map](./docs/PROJECT_MAP.md)
- current candidate summary:
  - Current active task is none.
  - Latest completed task is [overview-futures-macro-pattern-outlook-v1-20260718](./tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/STATUS.md). Futures Macro를 현재 1D/5D/20D 체제와 5D/20D 조건부 전망으로 개편했고, 후속 교정에서 세 관측 anchor와 유사 episode 기반 5D/20D 중앙 경로·가운데 50% 범위로 바꿨다.
  - Previous completed task is [overview-economic-cycle-asset-signal-copy-v1-20260717](./tasks/active/overview-economic-cycle-asset-signal-copy-v1-20260717/STATUS.md). 자산별 미국 경기 신호·실제 가격·두 신호 관계와 5/21/63거래일 표기를 사용자 언어로 정리했다.
  - Previous completed task is [overview-economic-cycle-gold-dollar-price-confirmation-v1-20260717](./tasks/active/overview-economic-cycle-gold-dollar-price-confirmation-v1-20260717/STATUS.md). 금·달러를 분리하고 저장 일봉의 1주·1개월·3개월 가격 흐름과 경제 배경의 일치·불일치를 표시한다.
  - Previous completed task is [overview-economic-cycle-asset-context-v1-20260716](./tasks/active/overview-economic-cycle-asset-context-v1-20260716/STATUS.md). 정적 시장 질문을 evidence 기반 자산별 확인 포인트로 바꾸고 우호/부담/혼재/자료 부족, 두 근거, 바뀌는 조건을 2×2 카드로 표시한다.
  - Previous completed task is [overview-market-context-economic-cycle-provisional-hybrid-v2-20260716](./tasks/active/overview-market-context-economic-cycle-provisional-hybrid-v2-20260716/STATUS.md). 유효 LIMITED 확률을 잠정 추정으로 공개하고 READY/계산불가와 분리했으며, 최근 12개월 2×2 hover 경로·실제 월수 기반 최근 60개월+2개월 ribbon·actual 122 snapshot 보존을 완료했다.
  - Previous completed task is [overview-market-context-us-economic-cycle-v1-20260716](./tasks/active/overview-market-context-us-economic-cycle-v1-20260716/STATUS.md). 17-series vintage/PIT engine과 horizon별 publication gate를 구현했다.
  - Previous completed task is [overview-market-context-turnaround-derived-quarter-provenance-v1-20260716](./tasks/active/overview-market-context-turnaround-derived-quarter-provenance-v1-20260716/STATUS.md). Explicit concept family의 확정 공시로 missing Q4를 안전하게 산출하고 provenance와 `공시 기반 산출` 표시를 1차~4차로 완료했다.
  - Previous completed Overview / Market Context task is [overview-market-context-turnaround-stage-semantics-fix-v1-20260716](./tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/STATUS.md). AAPL canonical EPS reader와 six-rail transition/already-positive semantics를 1차~3차로 완료했다.
  - Previous completed Overview / Market Context task is [overview-market-context-us-stock-freshness-refresh-v1-20260715](./tasks/active/overview-market-context-us-stock-freshness-refresh-v1-20260715/STATUS.md). Cached selected-stock UI는 DB-only로 유지하고 stale repair는 explicit single action으로 제한한다.
  - Previous completed Nasdaq task is [overview-market-context-nasdaq100-coverage-repair-action-v1-20260713](./tasks/active/overview-market-context-nasdaq100-coverage-repair-action-v1-20260713/STATUS.md).
  - Recent completed Institutional Portfolios task is [institutional-portfolios-security-detail-chart-layout-v1-20260712](./tasks/active/institutional-portfolios-security-detail-chart-layout-v1-20260712/STATUS.md).
  - Previous completed Institutional Portfolios task is [institutional-portfolios-watchlist-mapping-v1-20260712](./tasks/active/institutional-portfolios-watchlist-mapping-v1-20260712/STATUS.md).
  - Recent completed Final Review task is [final-review-evidence-closure-contract-v1-20260712](./tasks/active/final-review-evidence-closure-contract-v1-20260712/STATUS.md). It closes Level2 actionable gaps and records Final Review accepted-limit / Monitoring / defer terminal states.
  - Previous completed Overview / Market Context task is [overview-market-context-sp500-valuation-v1-20260712](./tasks/active/overview-market-context-sp500-valuation-v1-20260712/STATUS.md).
  - Latest completed Practical Validation / Final Review boundary task is [practical-validation-recheck-handoff-loop-fix-v1-20260712](./tasks/active/practical-validation-recheck-handoff-loop-fix-v1-20260712/STATUS.md).
  - Previous completed Practical Validation / Final Review boundary task is [practical-validation-pre-final-enrichment-gate-v1-20260712](./tasks/active/practical-validation-pre-final-enrichment-gate-v1-20260712/STATUS.md).
  - Latest completed Final Review UX task is [final-review-readable-review-evidence-v1-20260711](./tasks/active/final-review-readable-review-evidence-v1-20260711/STATUS.md).
  - Previous completed Final Review UX task is [final-review-decision-flow-simplification-v1-20260711](./tasks/active/final-review-decision-flow-simplification-v1-20260711/STATUS.md).
  - Latest completed portfolio workflow reset is [portfolio-workflow-legacy-reset-rebuild-20260711](./tasks/active/portfolio-workflow-legacy-reset-rebuild-20260711/STATUS.md).
  - Previous completed Final Review UX task is [final-review-investment-report-redesign-v1-20260711](./tasks/active/final-review-investment-report-redesign-v1-20260711/STATUS.md).
  - Previous completed Final Review UX task is [final-review-confirmed-review-flow-v1-20260711](./tasks/active/final-review-confirmed-review-flow-v1-20260711/STATUS.md).
  - Previous completed Final Review top UX task is [final-review-top-ux-cleanup-v1-v4-20260709](./tasks/active/final-review-top-ux-cleanup-v1-v4-20260709/STATUS.md).
  - Previous completed Final Review scorecard task is [final-review-detailed-scorecard-v1-v6-20260709](./tasks/active/final-review-detailed-scorecard-v1-v6-20260709/STATUS.md).
  - Current active Practical Validation UI task is none.
  - Latest completed Practical Validation UI task is [practical-validation-stage-ownership-v1](./tasks/active/practical-validation-stage-ownership-v1/STATUS.md).
  - Previous completed Practical Validation UI task is [practical-validation-flow4-action-center-v1-20260709](./tasks/active/practical-validation-flow4-action-center-v1-20260709/STATUS.md).
  - Previous completed Practical Validation UI task is [practical-validation-flow4-data-action-board-v1-20260709](./tasks/active/practical-validation-flow4-data-action-board-v1-20260709/STATUS.md).
  - Latest completed docs / code-flow refresh is [post-merge-docs-flow-refresh-20260708](./tasks/active/post-merge-docs-flow-refresh-20260708/STATUS.md).
  - Latest completed structure work is Refactor Round Closeout 10차 in [refactor-round-closeout-20260607](./tasks/active/refactor-round-closeout-20260607/AUDIT.md).
  - Recent merged work is grouped as Overview / Market Context, Backtest Analysis, Practical Validation / Final Review, Operations / Portfolio Monitoring, and UI / Engine Boundary.
  - Current active phase is still none; new phase work requires a user-approved concrete scope.

## Recent Milestones

- Overview Futures Macro Pattern Outlook V1:
  - `today shock -> current pattern -> default 5D / 20D conditional outlook -> evidence / ribbon / asset pathways -> method` 흐름으로 개편했다.
  - 실제 2026-07-17 snapshot은 혼재 체제 / 전환 시도이며 5D 120개, 20D 42개 독립 episode 모두 `PROVISIONAL`, 방향 우위 미확인이다.
  - 후속 UI 교정에서 관측 지도는 `20D 전 → 5D 전 → 현재` 실선으로 단순화하고, 고정 체제 분기를 유사 episode의 5D·20D step별 중앙 이동 점선과 세 시점의 가운데 50% 범위로 교체했다.
  - 경로 좌표는 `현재 위치 + 표준화된 조건부 이동`이며 probability/path 시간순 검증을 분리한다. 실제 5D 5점과 20D 20점은 서로 다른 경로이고 모두 `PROVISIONAL`이다.
  - 상세 구현·성능·QA 근거는 [active task](./tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/STATUS.md)에 있다.

### Overview / Market Context Track

- Economic Cycle Asset Signal Copy V1:
  - `경제 국면: 회복` 반복을 제거하고 금·달러는 `미국 경기 신호 / 실제 가격 / 두 신호 관계`, 나머지는 `현재 환경`으로 읽게 했다.
  - Actual 금은 `금을 지지 / 하락 / 서로 다른 방향`, 달러는 `달러에 부담 / 상승 / 서로 다른 방향`이며 5/21/63거래일을 명시한다.
  - Focused 35 tests, React build, actual read model, HTTP 200, desktop/420px overflow와 console error 0건을 확인했다.
- Economic Cycle Gold / Dollar Price Confirmation V1:
  - 금과 달러를 별도 카드로 분리하고 `GC=F` / `DX-Y.NYB` 저장 일봉의 5/21/63거래일 가격 흐름을 경제 배경과 독립 표시한다.
  - Actual 2026-07-16은 금 `하락 확인`, 달러 `상승 확인`이며 두 카드 모두 2026-06-30 경제 배경과 불일치한다. 달러의 1주 하락도 1·3개월 상승과 함께 그대로 보인다.
  - 33개 focused tests, futures 계약 선택 테스트, React build, compile/diff check를 통과했다. 연속선물 롤 효과와 비실시간 원천 경계는 화면과 문서에 유지한다.
- Economic Cycle Asset Context V1:
  - 정적 네 문장을 `자산별 확인 포인트` 2×2 카드로 교체하고 상태 → 두 근거 → 바뀌는 조건 순서로 읽게 했다.
  - 네 canonical factor를 자산별로 번역하되 우호/부담 차이가 작으면 `혼재`, 비중립 근거가 두 개 미만이면 `자료 부족`으로 남긴다.
  - Actual 2026-06-30은 채권·금리 혼재, 주식 부담, 금·달러 우호, 원자재 혼재다. 수익률·매매 신호와 별도 provider 수집은 추가하지 않았다.
- Economic Cycle Provisional Hybrid V2:
  - `잠정 모델 추정 / 검증된 모델 추정 / 판단 불가`를 유효 확률·publication status·계산 가능성으로 분리했다.
  - 원형 clock을 2×2 국면 좌표, 최근 12개월 실선, 현재~+2M 점선, 최근 60개월+2개월 ribbon으로 교체했다. DB의 121개월 replay는 유지한다.
  - 60개월 전환 뒤 남아 있던 121열 CSS를 실제 history 개수 기반 grid로 바꿔 ribbon이 전체 너비를 채우게 했고, Cycle Map 지점은 hover/focus 때만 날짜·우세 국면·확률·추정 상태를 표시한다.
  - Actual 현재/+1M/+2M은 모두 회복 우세 `46.7% / 40.5% / 47.4%`의 PROVISIONAL이며 threshold와 PIT 원칙은 유지했다. desktop/420px console·overflow QA를 통과했다.
- U.S. Economic Cycle V1:
  - 현재·1개월 후·2개월 후의 회복/확장/둔화/침체 확률을 vintage-aware 데이터와 rolling-origin publication gate로 계산하는 17개 TDD task를 `5/5` 완료했다.
  - raw vintage -> strict as-of feature/label/model -> approved artifact/snapshot -> DB-only service/UI 경계와 `경제 사이클 | S&P 500 | 미국 개별주식` selector를 구현했다.
  - Actual bootstrap 뒤 h0/h1/h2는 publication gate 미통과로 `LIMITED`다. V2가 계산 결과와 검증 상태를 분리했다. 상세는 [task status](./tasks/active/overview-market-context-us-economic-cycle-v1-20260716/STATUS.md)를 본다.
- Overview Market Context turnaround stage semantics V1:
  - `USD per share` diluted EPS를 turnaround duration reader에 포함해 AAPL PER/turnaround TTM EPS를 `7.90`으로 정렬했다.
  - backend threshold는 유지하고, 6개 rail에서 전환 `MET`, 이미 양수인 UI-local `ESTABLISHED`, 미확인을 구분했다. AAPL/RIVN actual과 desktop/420px Browser QA를 완료했다.
  - focused 118 tests/build/compile은 통과했고, monolithic discovery는 기존과 같은 4 failures/154 Streamlit isolation errors다.
- Nasdaq-100 적정구간 119개월 warmup V1:
  - READY valuation의 1/3/5년 이력 부족을 SEP가 아닌 60개월 rolling warmup 문제로 설명하고, 선택 기간별 필요/현재 월 수와 별도 보강 action을 연결했다.
  - actual repair는 172,240 rows를 저장해 READY 월을 62에서 66으로 늘렸다. acquired/delisted 및 foreign issuer 무료 원천 gap 때문에 71/95/119개월 요구에는 미달하며 합성 없이 partial 상태를 유지한다.
  - focused/full service tests, React build, desktop/420px Browser QA 상세는 [task status](./tasks/active/overview-market-context-nasdaq100-scenario-history-warmup-v1-20260713/STATUS.md)를 본다.
- Nasdaq-100 60개월 coverage repair action V1:
  - blocker 카드에 `60개월 가치평가 자료 보강`을 추가하고 planner -> canonical EPS/EOD 수집 -> strict rematerialization을 같은 화면에서 동기 실행하도록 연결했다.
  - SEC가 basic/diluted EPS를 동일값으로 공시한 actual concept을 보수적 fallback으로 허용해 local actual DB를 60/60 READY로 복구했다.
  - focused tests, React build, desktop/420px Browser QA를 완료했다. 상세는 [task status](./tasks/active/overview-market-context-nasdaq100-coverage-repair-action-v1-20260713/STATUS.md)를 본다.

### Institutional Portfolios Track

- Institutional Portfolios Security Detail Chart Layout V1 2026-07-12:
  - `.aiworkspace/note/finance/tasks/active/institutional-portfolios-security-detail-chart-layout-v1-20260712/`에서 `종목 분석 > 종목 상세` 1차~3차를 완료했다.
  - 선택 종목 / 포트폴리오 내 위치 overview card, full-width stored-OHLCV chart row, volume/navigator lower area, 하단 scrollable holder list로 재배치했다.
  - DB / ingestion / provider / recommendation / trading boundary는 변경하지 않았다.
- Institutional Portfolios Two-Tier Tabs V1 2026-07-12:
  - `.aiworkspace/note/finance/tasks/active/institutional-portfolios-two-tier-tabs-v1-20260712/`에서 React workbench tab IA를 상위 `포트폴리오 / 종목 분석` 탭과 context-specific 하위 탭으로 분리했다.
  - 기존 한 줄 group-label 탭의 시각적 어색함을 줄였고, DB / ingestion / provider / trading boundary는 변경하지 않았다.
- Institutional Portfolios Portfolio / Security IA V1 2026-07-12:
  - `.aiworkspace/note/finance/tasks/active/institutional-portfolios-portfolio-security-ia-v1-20260712/`에서 React workbench tab IA를 `포트폴리오`와 `종목 분석` 그룹으로 나눴다.
  - `요약 / 전체 보유`는 manager portfolio view로, `종목 상세 / 기관 보유 랭킹`은 ticker / security analysis view로 읽히게 했다.
  - 기존 보유 기관 조회 기능은 `종목 상세` 안의 보유 기관 리스트로 유지했고, DB / ingestion / provider / trading boundary는 변경하지 않았다.
- Institutional Portfolios Interactive Security Chart V1 2026-07-12:
  - `.aiworkspace/note/finance/tasks/active/institutional-portfolios-interactive-security-chart-v1-20260712/`에서 보유기관조회 선택 종목 차트를 stored OHLCV 기반 interactive chart로 개선했다.
  - 라인 / 캔들 toggle, hover tooltip, crosshair, high-low dotted guides, range slider, pan controls를 추가했고, UI external fetch / 추천 / live trading 경계는 그대로 유지했다.
  - Browser QA에서 AAPL chart stage, range, guide, hover tooltip / crosshair 생성과 current-port console error 없음까지 확인했다.
- Institutional Portfolios React Workbench V1 2026-07-09:
  - `.aiworkspace/note/finance/tasks/active/institutional-portfolios-react-workbench-v1-20260709/`에서 1차~6차 scope를 진행했다.
  - `Workspace > Institutional Portfolios`를 table-first / ingestion-like 화면에서 React visual workbench로 바꿨다. 첫 화면은 manager rail, allocation donut, top holdings, reported quarter changes, sector exposure를 보여주고, holdings click은 institutional interest drill-down event로 연결한다.
  - DB empty 상태는 clearly labeled preview로 표시하며, raw DB error는 setup expander에만 둔다. 13F delayed / no trade signal / no live workflow boundary는 유지했다.
- Institutional Portfolios Workspace V1 2026-07-08:
  - `.aiworkspace/note/finance/tasks/active/institutional-portfolios-workspace-v1-20260708/`에서 1차~6차 scope를 진행했다.
  - `Workspace > Institutional Portfolios`를 Market Movers와 분리된 delayed SEC Form 13F research surface로 추가하고, SEC official dataset ingestion / schema / loader / service / UI / docs / runbook을 연결했다.
  - 13F 45일 지연, shorts / cash / derivatives / hedge omission, CUSIP-symbol mapping caveat를 visible boundary로 남겼고, Backtest / Practical Validation / Final Review / Operations live workflow에는 연결하지 않았다.
### Overview / Market Interest Track

- Overview Market Movers 상단 action / Monthly 짧은 이력 V1:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-top-actions-monthly-history-v1-20260711/`에서 긴 버튼 detail을 버튼 밖 한 줄 설명으로 분리했다.
  - FDXF/HONA의 Monthly 반복 갱신 원인을 provider 가용 이력 31/1 rows로 확인하고 `limited_price_history` evidence를 저장해 같은 full-window 수집 제안을 제거했다.
  - 146 focused tests, React build, DB live preflight, Browser QA를 통과했다.
- Overview Market Movers 섹션 제목 통일 V1:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-section-title-unification-v1-20260711/`에서 섹터 breadth의 외부 중복 divider를 제거했다.
  - React/fallback 모두 `SECTOR BREADTH / 섹터 / 시장 확산 맥락 / 설명 / 상태`를 고정 섹션 헤더로 사용하고, 현재 breadth headline은 결과 요약으로 낮췄다.
  - Market Movers focused 79 tests, React build, Browser QA를 통과했으며 데이터 계산/provider/DB/registry 의미는 변경하지 않았다.
- Overview Market Movers 애널리스트 출처 보드:
  - `.aiworkspace/note/finance/tasks/active/overview-market-interest-source-board-20260709/`에서 `애널리스트 관심`의 링크 묶음 expander를 `출처별 확인 상태` 보드로 바꿨다.
  - Yahoo/yfinance는 세션 전용 구조화 단서로, MarketWatch / WSJ Markets / Nasdaq.com은 `원문 교차확인` 상태로 분리해 표시한다.
  - 자동 크롤링, DB 저장, 추천 / 점수화 / 매매 신호는 추가하지 않았다.
- Overview Market Movers 시장 관심 뉴스 / SEC 분리:
  - `.aiworkspace/note/finance/tasks/active/overview-market-interest-news-sec-split-20260709/`에서 선택 종목 `시장 관심` 패널의 `뉴스 리스트`와 `SEC 공시 촉매`를 별도 evidence section으로 분리했다.
  - Form 144처럼 제목이 form명뿐인 SEC metadata는 `SEC Form 144 · 제한/지배주식 매각 예정 통지`로 표시해 뉴스 기사와 혼동하지 않게 했다.
  - 13F는 계속 `기관 보유 배경 · 13F 지연 자료`로 분리하며, 추천 / 점수화 / 매매 신호 / body 저장 / DB schema 변경은 추가하지 않았다.
- Overview Market Movers 시장 관심 근거 V2:
  - `.aiworkspace/note/finance/tasks/active/overview-market-interest-evidence-v2-20260708/`에서 1차~5차 follow-up을 진행했다.
  - `시장 관심 근거 확인`이 선택 종목 뉴스 / 한국어 뉴스 / SEC metadata를 함께 조회하고, `시장 관심` 탭 안에서 `애널리스트 관심`, `뉴스 리스트`, `SEC 공시 촉매`, `기관 보유 배경 · 13F 지연 자료`, `출처/원문 링크`를 구분해 보여준다.
  - FMP/Finnhub/Naver API credential integration, 13F DB ingestion, body 저장, 추천 / 점수화 / 매매 신호는 추가하지 않았다.
- Overview Market Movers 시장 관심 근거 V1:
  - `.aiworkspace/note/finance/tasks/active/overview-market-interest-evidence-v1-20260708/`에서 1차~4차 selected-symbol 조사 보조 패널을 개발했다.
  - Market Movers 선택 종목 하단에 수동 `시장 관심 근거 확인` action과 `시장 관심` 탭을 추가해 애널리스트 / 뉴스·SEC / 13F 지연 맥락 / 원문 링크를 확인하게 했다.
  - 추천, 점수화, 자동 catalyst 판정, 매수·매도 신호, article/report/filing body 저장, 13F DB ingestion은 추가하지 않았다.
### Practical Validation / Final Review Track

- Practical Validation Pre-Final Enrichment Gate V1:
  - 실행 가능한 operability / holdings·exposure / required macro gap을 Practical Validation 승격 전 blocker로 분리했다. 수집 성공 뒤에도 Flow 2 재검증과 새 validation 저장 전에는 Final Review 이동이 활성화되지 않는다.
  - Final Review의 legacy / stale 검토서는 과거 근거 열람과 2단계 복구 navigation만 허용하고 Decision Desk, recommendation, 판단 저장을 `2단계 재검증 필요`로 잠갔다.
  - Browser QA에서 단계 요약 일관성, 복구 handoff, 비활성 판단 CTA, 760px no-overflow를 확인했다. registry / saved / run history / generated screenshot은 커밋하지 않았다.
- Final Review Readable Review Evidence V1:
  - `남은 판단 근거`를 사용자 언어의 검증명, 현재 확인 내용, 판단 이유, 개선 행동으로 정리하고 raw source / 기준일은 접힌 상세로 낮췄다.
  - 수집 가능한 provider gap만 같은 후보의 Practical Validation 보강 화면으로 넘기며 기간 밖 / 미구현 / source 탐색 / 사용자 판단은 별도 행동으로 분리했다.
  - focused tests 59개, React build, py_compile, diff check, 760px Browser QA와 2단계 handoff를 통과했다. 실제 수집 / 판단 저장과 registry / saved / run history write는 실행하지 않았다.
- Final Review Decision Flow Simplification V1:
  - 총평과 4행 해석 직후에 route / 판단 사유 / gate 기반 CTA를 배치해 Level1 / Level2와 같은 판단 action 흐름으로 정리했다.
  - React는 decision intent만 전달하고 Python이 save evaluation, 자동 Decision ID, route template, append를 소유한다. 판단 사유는 사용자가 직접 입력해야 CTA가 활성화된다.
  - Evidence Appendix와 Saved Decisions ledger를 Final Review에서 제거했다. selected row 운영 확인은 Portfolio Monitoring에서 이어지며 기존 decision JSONL은 보존했다.
  - 계약 테스트 137개, React build, py_compile, diff check, Browser QA를 통과했고 QA 중 registry write는 실행하지 않았다.
- Final Review Responsive Evidence V1:
  - REVIEW impact header에만 2열 selector를 적용하고 내부 audit trace는 전체 폭 1열로 고정해 축소 화면의 카드 찌그러짐을 제거했다.
  - 긴 lifecycle / provider 근거는 카드 내부에서 줄바꿈하고 compact / mobile에서 header, tab, trace label을 단계적으로 쌓는다.
  - React build, focused contract test, py_compile, diff check, 900px / 680px Browser QA를 통과했다. Python evidence 계약과 registry / saved / run history는 변경하지 않았다.
- Final Review Guidance Actionability V1:
  - 10개 Monitoring 패턴을 named evidence adapter 기반 4개 상태로 판정하고, 첫 화면 최대 6개에 `현재 진단 / 의미 / 변화 조건 / 다음 행동`을 표시했다. source / 기준일 / technical path는 접힌 상세에 남겼다.
  - Level2 REVIEW를 Final Review 직접 결정, 2단계 인수 제한, Monitoring 조건, blocker로 분리하고 총평 직후 성과 / 위험 / 근거 신뢰도 / Monitoring 적합성 4행을 배치했다.
  - focused tests 53개, React build, py_compile, diff check, Browser QA를 통과했다. registry / saved / run history와 generated QA screenshot은 커밋하지 않았다.
- Portfolio Workflow Legacy Reset / Rebuild:
  - 기존 Final Review 후보 6개를 current source → Practical Validation → Final Review 판단으로 재생성했다. 모든 stored-period runtime replay가 PASS였고 새 validation은 workspace / REVIEW role 계약을 포함한다.
  - schema-v3 monitoring decision 6개와 Portfolio Monitoring setup 3개를 새 ID로 연결했으며 legacy `SAVED_PORTFOLIOS.jsonl`은 사용자 요청으로 제거했다.
  - focused unittest 5개, py_compile, data-chain invariant, diff check는 통과했다. Browser QA는 localhost URL 보안 정책 때문에 미실행이다.
- Final Review Investment Report Redesign V1:
  - 외부 Investment Report card와 중복 상태 / Handoff 기술 용어를 제거하고 투자 매력도 / 근거 신뢰도 / Monitoring 준비도를 분리했다.
  - open REVIEW 개수 자동 감점 / cap을 제거하고 REVIEW trace, 총평 / 강점과 약점 / 저장 전 질문, 10개 조건부 패턴 가이드와 세 개 상세 탭을 구현했다.
  - focused tests 53개, React build, py_compile, diff check, Browser QA를 통과했으며 generated screenshot과 run history는 stage하지 않았다.
- Final Review Confirmed Review Flow V1:
  - stable key 후보 선택, visible Review Queue 제거, `최종 검토서 확인` session boundary와 stale report 차단을 1차~2차로 완료했다.
  - Level2 REVIEW 다섯 role은 `Final Review 확인 필요`에서 점수 반영 / 저장 전 확인 / Monitoring 이관 / blocker 행동으로 읽으며 React는 표시만 맡는다.
  - focused tests 53개와 Browser QA를 통과했고, 재검증 / provider fetch / registry write / live approval 경계는 변경하지 않았다.
- Final Review Candidate Selection Integration V1:
  - `.aiworkspace/note/finance/tasks/active/final-review-candidate-selection-integration-v1-20260710/`에서 standalone `Step 1 / Candidate Board`와 중복 4-card lane summary를 제거했다.
  - Review Queue, `검토 대상` selector, 후보 비교 상세는 Decision Desk 아래 후보 선택 패널로 통합했고, 투자 검토서 / Decision Cockpit / 판단 저장 / Evidence Appendix는 의미형 섹션으로 이어진다.
  - score / gate / 저장 / provider fetch / registry write / Portfolio Monitoring handoff 계산은 변경하지 않았다. Browser QA screenshot은 generated artifact로 남겼다.
- Final Review Sentiment Scope Cleanup V1:
  - `.aiworkspace/note/finance/tasks/active/final-review-sentiment-scope-cleanup-v1-20260710/`에서 Final Review first-read의 CNN / AAII market sentiment panel과 detail expander를 제거했다.
  - Final Review는 Decision Desk 이후 후보 선택 패널 / 투자 검토서 / Decision Cockpit을 바로 이어서 읽고, 자세한 심리 해석은 `Workspace > Overview > Sentiment`에 둔다.
  - 시장심리는 Final Review gate / score / 저장 / Candidate Board priority / Monitoring signal을 바꾸지 않으며, timing / rebalance 활용은 별도 research 전까지 구현하지 않는다.
- Final Review Top UX Cleanup V1-V4:
  - `.aiworkspace/note/finance/tasks/active/final-review-top-ux-cleanup-v1-v4-20260709/`에서 Final Review 상단 안내, 후보 현황, compact 시장심리 context, timing / rebalance research 경계를 1차~4차로 개발 / QA / 커밋했다.
  - first-read surface는 후보 수, 선택 가능, 보류 / 재검토, 숨김, 저장된 판단, Monitoring 연결을 먼저 보여주고, Reference help와 1~5 guide card는 상단에서 제거했다.
  - 후속 `final-review-sentiment-scope-cleanup-v1-20260710`에서 CNN / AAII sentiment는 Final Review first-read에서 제거하고, `Workspace > Overview > Sentiment`가 상세 해석을 소유하도록 정리했다.
- Final Review Level3 React V2-V6:
  - `.aiworkspace/note/finance/tasks/active/final-review-level3-react-v2-v6-20260709/`에서 Final Review 투자 검토서, Level2 REVIEW disposition, 점수 체계, 저장 / Monitoring handoff summary, 약점 개선안 read-only flow를 개발 / QA / 커밋 순서로 완료했다.
  - React component는 표시와 intent만 맡고, score / recommendation / REVIEW 분류 / handoff 판단 / weakness proposal은 Python `backtest_evidence_read_model`이 만든다.
  - registry / saved JSONL 기존 row는 재작성하지 않았고, run_history / generated QA artifacts는 stage하지 않았다. live approval / broker order / auto rebalance 경계도 변경하지 않았다.
- Final Review Level3 Storage Boundary V1:
  - `.aiworkspace/note/finance/tasks/active/final-review-level3-redesign-analysis-v1-20260709/`에서 Final Review 판단 record와 Portfolio Monitoring handoff 경계를 분리했다.
  - `SELECT_FOR_PRACTICAL_PORTFOLIO` / 보류 / 거절 / 재검토는 모두 Final Review 판단으로 append 가능하며, Monitoring 후보는 selected-route gate 통과 row의 `monitoring_candidate`만 읽는다.
  - registry / saved JSONL 기존 row는 재작성하지 않았고, live approval / broker order / auto rebalance 경계도 변경하지 않았다.
- Practical Validation Stage Ownership V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-stage-ownership-v1/`에서 REVIEW role taxonomy와 Flow4 visibility contract를 정리했다.
  - Flow4는 적용된 REVIEW-only Practical Validation category를 숨기지 않고 `데이터 주의` / `2단계 실용성 주의`로 표시하며, Final Review / Monitoring 항목은 보조 참고로 낮춘다.
  - Flow4 provider-facing wording은 `ETF 운용사 / 공식 외부 데이터` 중심으로 낮췄고, Browser QA는 fresh server `http://localhost:8517`에서 확인했다.
  - React / Streamlit UI는 표시만 맡고, replay / provider collection / validation calculation / gate / persistence는 기존 Python service/runtime 경계에 남긴다.
- Practical Validation Flow4 Action Center V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-action-center-v1-20260709/`에서 Flow 4의 `데이터 보강 대상` / `Provider 보강 액션` split를 `데이터 보강 / 수집 실행` action center로 재정렬했다.
  - 수집 버튼 주변에 `수집하는 것 / 하지 않는 것 / 실행 후 다음 단계`를 보여주고, raw 보강 작업 상세는 `상세 근거 / 원자료`로 낮췄다.
  - React는 계속 props 표시만 맡고, 외부 데이터 수집 / replay / validation calculation / gate / persistence는 Python service/runtime 경계에 남긴다.
- Practical Validation Flow4 Data Action Board V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-data-action-board-v1-20260709/`에서 Flow 4 visible order를 `카테고리별 검증 결과 -> 데이터 보강 대상 / 액션 -> 상세 근거 / 원자료`로 정리했다.
  - visible `단계별 검증 소유권` expander와 별도 `수집 대상 근거` expander를 제거하고, Python workspace read model의 `data_action_board`를 표시 전용 React board로 렌더링한다.
  - React는 provider/FRED/API/DB fetch, validation calculation, provider collection, replay, gate, registry/saved write를 하지 않는다. Browser QA에서 Final Review preview 반복 노출을 제거한 상태까지 확인했다.
- Practical Validation Category Empty State V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-category-empty-state-v1-20260708/`에서 Flow 4 `카테고리별 검증 결과`의 `보강 항목 없음` 노출을 정리했다.
  - `visible_criteria_detail_groups`를 추가해 REVIEW-only / empty category는 내부 read model에 남기되 Flow 3 / Flow 4 visible category result에서는 숨긴다.
  - Flow 3 React fallback도 `보강 항목 없음`을 통과처럼 해석하지 않게 정리했다. Final Review 화면 재구성은 다음 차수로 남겼다.
- Post-Merge Docs / Code Flow Refresh 2026-07-08:
  - `.aiworkspace/note/finance/tasks/active/post-merge-docs-flow-refresh-20260708/`에서 master 병합 후 공용 docs, status manifests, Overview runbook / data flow docs를 current state로 정렬했다.
  - Current Overview primary tabs는 `Market Context`, `Market Movers`, `Futures Macro`, `Sentiment`, `Events`로 문서화했고, legacy `Futures Monitor` / `Sector / Industry` primary surface 표현을 낮췄다.
  - 코드 리뷰 중 Overview Data Health handoff / Market Context cockpit의 legacy label drift를 발견해 service contract와 tests를 `Futures Macro` / `Market Movers` 기준으로 보정했다.
- Practical Validation Boundary Cleanup V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-boundary-cleanup-v1-20260708/`에서 Flow 3 / Flow 4 visible UI를 Practical Validation 전용 결론과 보강 원인으로 정리했다.
  - Flow 3은 Final Review 이동 가능 / 보류와 REVIEW count를 제거하고 `보강 후 재검증`, 실패 category, 검증 category만 보여준다.
  - Flow 4는 `Final Review 참고`, `Final Review 이동 요약`, legacy gate technical expander를 렌더링하지 않는다. Final Review 화면 재구성은 다음 차수로 남겼다.
- Practical Validation Flow4 Final Review Handoff V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-final-review-handoff-v1-20260708/`에서 Flow 4가 Final Review 판단 항목을 상세 문제처럼 보여주는 중복을 줄였다.
  - 당시 Flow 4 main board는 `통과 / 보강 후 재검증 / 실전 사용 어려움` 중심으로 읽고, REVIEW 항목을 `Final Review 참고` count로 낮췄다. 후속 Boundary Cleanup V1에서 이 visible count도 Flow 3 / Flow 4에서 제거했다.
  - Final Review 화면 재구성, gate threshold, registry / saved JSONL, provider ingestion, live approval / order semantics는 변경하지 않았다.
- Practical Validation Flow4 Outcome Taxonomy V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-outcome-taxonomy-v1-20260708/`에서 Flow 4 outcome layer와 `Current=REVIEW` 보존 회귀를 구현했다.
  - Flow 4는 이제 `통과 / 보강 후 재검증 / Final Review 판단 / 실전 사용 어려움`을 먼저 보여주며, 최신 replay가 REVIEW이면 NEEDS_INPUT으로 강등하지 않는다.
  - BacktestRuntimeContractTests 67개, py_compile, diff check, Browser QA를 통과했다. Registry / saved JSONL, provider ingestion, live approval / order / auto rebalance 경계는 변경하지 않았다.
- Practical Validation Required Taxonomy Refactor V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-required-taxonomy-refactor-v1-20260708/`에서 2차~6차를 개발 / QA / 커밋 순서로 진행했다.
  - `validation_efficacy` service는 walk-forward / OOS / regime split 방법론 검증만 소유하고, replay / benchmark / provider / PIT / survivorship / robustness는 각 owner module로 분리했다.
  - Flow 4와 Final Review는 user-facing `Validation Method Strength` / `Stress / Robustness` taxonomy를 사용한다. Registry / saved JSONL, provider ingestion, live approval / order / auto rebalance 경계는 변경하지 않았다.
- Practical Validation Required Taxonomy Audit V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-required-taxonomy-audit-v1-20260708/`에서 1차 필수 검증의 current row inventory와 owner matrix를 정리했다.
  - 핵심 결론은 `validation_efficacy`가 source / replay / benchmark / provider / PIT / survivorship / robustness를 중복 소유하고 있으므로, 다음 코드 작업에서 walk-forward / OOS / regime 중심의 method-strength module로 축소해야 한다는 것이다.
  - 이번 task는 설계 / handoff 기록이며 Python service, gate threshold, UI, registry / saved JSONL은 변경하지 않았다.
- Backtest Factor Readiness Action UI V1:
  - Quality / Value strict form의 Factor Readiness를 내부 진단값 카드에서 `문제 / 티커 / 해결 방법 / action` 중심 React panel로 바꿨다.
  - 가격 보강은 Backtest OHLCV refresh service, statement gap은 targeted Extended Statement Refresh로 연결했다.
  - 자세한 기록: [task status](./tasks/active/backtest-factor-readiness-action-ui-v1-20260707/STATUS.md)
- Backtest Coverage Provider Gap Refresh V1:
  - `.aiworkspace/note/finance/tasks/active/backtest-coverage-provider-gap-refresh-v1-20260707/`에서 Coverage 최신화 no-row provider gap 반복 클릭 문제를 수정했다.
  - 명백한 persistent provider/source gap 심볼은 refresh plan에서 제외하고, rows_written=0 + unresolved 결과는 retry action card를 다시 렌더링하지 않는다.
  - OHLCV provider / DB schema / universe 선정 정책 / registry / saved JSONL 경계는 변경하지 않았다.
- Practical Validation Flow 4 Action Steps V3:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-action-steps-v3-20260707/`에서 Flow 4 `해결 방법`을 slash-joined 문단이 아니라 번호형 `action_steps`로 바꿨다.
  - Audit row의 non-PASS `Next Action`은 구체 단계로 우선 사용하고, provider / DB 보강과 Flow 2 재검증 같은 후속 조치는 별도 단계로 보여준다.
  - Validation threshold / replay / provider ingestion / registry / Final Review policy / live approval 경계는 변경하지 않았다.
- Practical Validation Flow 4 Resolution Guide V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-resolution-guide-v1-20260707/`에서 Flow 4 `보강 위치`를 구조화된 resolution guide로 바꿨다.
  - Criteria card는 이제 `검증한 것 / 부족한 것 또는 확인할 것 / 해야 할 일 / 확인 위치`를 보여주며, audit row의 non-PASS `Criteria`와 `Next Action`을 우선 사용한다.
  - Validation threshold / replay / provider ingestion / registry / Final Review policy / live approval 경계는 변경하지 않았다.
- Backtest PIT Universe V1:
  - `.aiworkspace/note/finance/tasks/active/backtest-pit-universe-v1-20260707/`에서 1차~5차를 개발 / QA / 커밋 순서로 완료했다.
  - Quality / Value strict coverage에 `PIT Monthly Snapshot Universe`를 추가해 사전 저장된 월말 membership을 리밸런싱일별로 읽게 했다.
  - V1은 DB price와 latest-known statement shares 기반 근사 PIT large-cap universe이며, 공식 지수 편입 이력 / float-adjusted market cap feed는 후속 provider phase로 남겼다.
- Backtest Candidate Analysis Hardening V1:
  - `.aiworkspace/note/finance/tasks/active/backtest-candidate-analysis-hardening-v1-20260706/`에서 1차~4차를 개발 / QA / 커밋 순서로 완료했다.
  - 전략 / variant 변경 시 이전 백테스트 결과를 숨기고, Data Trust가 limited / warning / error면 Practical Validation 진입을 차단한다.
  - Quality / Value strict preset 기준을 `finance_meta.nyse_asset_profile` 기반 US stock market-cap order로 명시했고, Price Freshness Preflight를 React component로 전환했다.
  - 가격 업데이트가 `finance_price.nyse_price_history`에 OHLCV row를 저장하면 기존 결과를 stale로 숨기고 같은 설정의 `Run Backtest` 재실행을 요구한다.
- Practical Validation Flow 4 Labels V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-labels-v1-20260706/`에서 Flow 4 이름을 `근거 Workbench`에서 `검증 기준 상세`으로 정리했다.
  - 카테고리 title emphasis를 강화하고, `보강 위치`를 내부 audit 이름이 아니라 `검증 기준 상세 · 데이터 품질 / Provider 보강` 같은 화면 기준 위치명으로 통일했다.
  - Validation threshold / replay / provider collection / registry / Final Review policy / live approval 경계는 변경하지 않았다.
- Practical Validation Flow 3 Conclusion Summary V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-flow3-conclusion-summary-v1-20260706/`에서 Flow 3을 Fix Queue가 아니라 `검증 결론` first-read surface로 전환했다.
  - Flow 3은 Final Review 이동 가능 / 보류와 카테고리별 `통과 / 실패 / 확인 필요`만 compact하게 보여주고, 상세 원인 / 보강 기준 / module table은 Flow 4로 낮췄다.
  - React component compatibility path와 Streamlit fallback을 함께 갱신했고, 반복 안전 문구와 guide-like `현재 문제 / 완료 기준 / 보강 위치` block은 Flow 3에서 제거했다.
- Practical Validation Category Results V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-category-results-v1-20260706/`에서 Flow 4를 `카테고리별 검증 결과` 중심으로 바꿨다.
  - `selected_route_preflight`는 검증 category가 아니라 `Final Review 이동 요약`으로 분리했고, stress / construction / sentiment gate severity를 후보 특성에 맞게 낮췄다.
  - Service contract와 Flow 3 / Flow 4 source contract tests, Backtest refactor boundary tests를 통과했다.
- Practical Validation Validation Audit:
  - `.aiworkspace/note/finance/researches/active/2026-07-practical-validation-validation-audit/`에서 현재 Practical Validation module / board / gate 구조를 감사했다.
  - 결론은 Flow 4 메인을 `Final Review로 넘기기 전 확인 기준`이 아니라 `카테고리별 검증 결과`로 바꾸고, Final Review 이동 가능성은 파생 handoff summary로 낮추는 것이다.
  - 유지할 core blocker는 source / latest replay / benchmark / PIT / survivorship / cost / liquidity이고, stress / construction / provider / macro / sentiment는 후보 특성에 맞춰 review 또는 조건부로 낮추는 방향이다.
- Practical Validation Issue Summary V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-issue-summary-v1-20260706/`에서 Flow 3 / Flow 4의 guide-like 설명을 issue / criteria summary 중심으로 다시 정리했다.
  - 당시 Flow 3 React surface는 이슈 / 보강 기준을 먼저 보여줬으나, 이후 `practical-validation-flow3-conclusion-summary-v1-20260706`에서 `검증 결론` 요약으로 대체했다.
  - Flow 4 criteria board는 기준별 `상태 / 통과한 기준 / 남은 문제 / 판정`을 먼저 요약하고, 기술 기준 상세는 뒤로 낮췄다.
  - Gate threshold / replay execution / provider collection / registry persistence / live approval 경계는 변경하지 않았다.
- Practical Validation Flow 3 Clarity V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-flow3-clarity-v1-20260706/`에서 Flow 3 중복 요약을 정리했다.
  - Flow 3의 별도 validation control center와 alert / badge 반복을 제거했다. 당시 first-read surface는 `Final Review 이동 판단 -> 먼저 해결할 일 -> 근거 요약`이었고, 이후 Conclusion Summary V1에서 카테고리별 결론만 남겼다.
  - Validation gate / registry / provider 수집 / Final Review handoff persistence / live approval 경계는 변경하지 않았다.
- Practical Validation Entry Simplification V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-entry-simplification-v1-20260705/`에서 Practical Validation 첫 진입 화면을 정리했다.
  - 기본 진입에서 Reference help와 context-only 시장 심리 overlay를 제거하고, command title을 `Final Review 이동 전 검증 상태`로 바꿨다.
  - Practical Validation HTML/CSS helper와 Fix Queue React component를 흰색 직선형 surface로 맞췄다. Validation gate / registry / provider / sentiment service 의미는 변경하지 않았다.
- Practical Validation Taxonomy Roadmap V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-taxonomy-roadmap-v1-20260705/`에서 Practical Validation 개편 V1-V8을 개발 / QA / 커밋 순서로 완료했다.
  - 주요 결과는 workspace read model, Final Review readiness wording, 5-flow 화면, read-only React Fix Queue, Flow 3 workspace panel split, first-read status normalization이다.
  - registry / saved JSONL, provider 수집, validation threshold, Final Review selected-route 저장 정책, live approval / broker / auto rebalance 경계는 변경하지 않았다.
### Earlier Overview / Data Track

- Overview Market Movers 기본지표 그래프 2026-07-08:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-fundamental-charts-20260708/`에서 1차~4차를 완료했다.
  - 기존 PER / EPS / 당기순이익 표는 유지하고, 하단에 PER / EPS / 당기순이익 / 유동비율 / FCF 지표 탭과 연간 / 분기 막대 그래프를 추가했다.
  - 차트는 `why_it_moved` research snapshot payload를 렌더링하며 UI가 DB/provider를 직접 읽지 않는다. Focused tests, py_compile, diff check, Browser QA를 통과했다.
- Overview Events calendar scope research 2026-07-07:
  - `.aiworkspace/note/finance/researches/active/2026-07-events-calendar-scope/`에 Events 수집 범위 리서치를 추가했다.
  - 결론은 S&P 500 / Nasdaq-100 / portfolio-watchlist / major-cap earnings를 Events의 first-class coverage로 올리고, official macro / market structure calendar와 분리해 표시하는 것이다.
  - 구현은 진행하지 않았다. 후속 Events UX 구현은 기존 `.aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/` 차수 계획과 연결한다.
- Overview Events calendar taxonomy 2차 2026-07-07:
  - `.aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/`에서 2차 taxonomy/schema/read-model contract를 완료했다.
  - `market_event_calendar`는 nullable taxonomy fields를 받고, Events snapshot은 `market_events_snapshot_v2` with family/source-authority/universe count maps를 제공한다.
  - 다음 차수는 official macro / fixed-income calendar collector expansion이다.
- Overview Events official macro / fixed-income 3차 2026-07-07:
  - `collect_macro_calendar`가 BLS JOLTS/ECI, BEA PCE, Census indicators, ISM PMI, Treasury auctions까지 official event row로 저장할 수 있게 확장됐다.
  - Treasury auction은 fixed-income calendar context이며 Events source evidence일 뿐 signal/action으로 해석하지 않는다.
  - 다음 차수는 S&P 500 / Nasdaq-100 / portfolio-watchlist / major-cap earnings universe expansion이다.
- Overview Events React workbench 4차~8차 2026-07-07:
  - Earnings universe, market-structure calendar, service-owned workbench payload, React scaffold, and brief/refresh command UX까지 완료했다.
  - Events React command band는 DB 화면 새로고침과 provider/job 수집 갱신을 분리하고, Python helper가 FOMC/Macro/Market Structure/Earnings refresh action을 계속 소유한다.
  - 다음 차수는 9차 이벤트 레일 / 자료 신뢰 / calendar hover-density 개선이다.
- Overview Events React workbench 9차 2026-07-07:
  - React workbench에 type/source-state display filters, filtered event rails, trust sections, hoverable calendar day buckets, weekly density bars, and collapsed raw evidence appendix를 추가했다.
  - Calendar / density는 일정 밀도와 stale/review 상태 근거만 보여주며 신호나 action으로 해석하지 않는다.
  - 다음 차수는 10차 final docs sync / Browser QA / commit hygiene closeout이다.
- Overview Events React workbench 10차 closeout 2026-07-07:
  - Project Map, Data Flow Map, Overview Market Intelligence runbook에 Events React workbench ownership, service payload boundary, refresh command split, and QA procedure를 반영했다.
  - Final QA passed: Events/event calendar contract classes, OverviewAutomationContractTests, py_compile, React build, diff check, desktop/mobile Browser QA on `localhost:8502`.
  - Browser QA screenshots are local generated artifacts and remain uncommitted.
- Overview Market Movers Ticker Change Repair 2026-07-07:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-ticker-change-repair-20260707/`에서 1차~5차를 완료했다.
  - `market_symbol_alias` candidate / active alias store, Market Movers `티커 변경 복구 적용` action, and intraday `quote_symbol` alias lookup were added.
  - 운영 순서는 `티커 변경 복구 적용` 후 `일중 스냅샷 갱신`이다. Active alias는 quote lookup만 바꾸고 universe symbol은 유지한다.
  - 검증은 focused RED/GREEN contracts, `py_compile`, `git diff --check`, Browser QA로 기록했다.
- Overview Futures Macro Evidence / Original Data UX:
  - `.aiworkspace/note/finance/tasks/active/overview-futures-macro-evidence-original-data-ux-20260706/`에서 1차~5차 후속 개선을 진행했다.
  - React `현재 근거`와 하단 `계산 근거 / 원본 표`의 역할을 분리했고, historical validation은 `현재 해석의 과거 일관성` / `비슷한 과거 상태` / 방향성 적용 여부로 읽게 정리했다.
  - `과거 점검`은 최근 흐름 / 현재 근거 사이의 독립 카드형 섹션으로 분리했고, 설명 / 상태 / CTA / 결과 타일을 한 surface 안에서 관리한다.
  - Futures Macro React workbench는 하나의 iframe을 유지하면서 내부를 `매크로 컨텍스트`, `최근 흐름`, `과거 점검` 카드 섹션으로 분리했다.
  - 원본표는 `현재 점수 -> 구성 기여 -> 선물 일봉 변화 -> 과거 표본` 순서로 재명명했고, React evidence item은 score label / symbol / z-score metadata를 보존한다.
  - 후속으로 `현재 근거`를 `CurrentEvidencePanel`로 분리해 `매크로 컨텍스트` 내부에 배치했고, 하단 disclosure를 `원본 데이터 / 계산 추적`으로 바꿔 세 React 섹션을 검산하는 raw appendix로 정리했다.
- Overview Futures Macro React UX 6차:
  - `.aiworkspace/note/finance/tasks/active/overview-futures-macro-react-ux-20260705/`의 1차~6차 개선을 완료했다.
  - 8517 current-code Browser QA에서 React iframe, `저신호 / 관망`, lazy validation `대기`, `1W` / `1M` controls를 확인했다. iframe button click dispatch는 자동화 좌표 제한으로 수동/별도 도구 확인 대상으로 남겼다.
  - 최종 검증과 hygiene check 후 closeout commit으로 닫았다.
- Overview Futures Macro React UX 5차:
  - `.aiworkspace/note/finance/tasks/active/overview-futures-macro-react-ux-20260705/`에서 historical validation을 DB materialization 없이 process cache로 재사용하도록 정리했다.
  - Cache key는 selected symbols / years / latest futures daily marker / proxy price marker / current summary identity를 포함하고, `일봉 갱신` / `다시 읽기`는 session validation과 process cache를 함께 비운다.
  - DB smoke 기준 첫 validation은 약 7.31초, 같은 key cache hit는 약 0.045초였다. 다음은 6차 final QA/docs closeout이다.
- Overview Futures Macro React UX 4차:
  - `.aiworkspace/note/finance/tasks/active/overview-futures-macro-react-ux-20260705/`에서 `혼재된 매크로 흐름`의 top-level compatibility를 유지하면서 subtype / regime hint / mixed reason을 세분화했다.
  - 새 subtype은 금리 부담 완화 속 성장 약세, 달러 압력 Risk-Off 후보, 원자재 약세 + 수요 둔화 후보, 위험선호/안전자산 상충 전환 구간, 저신호 관망을 구분한다.
  - FuturesMacroThermometer contract 20개, Overview contract 144개, `py_compile`, `git diff --check`를 통과했다. 다음은 5차 validation cache/materialization decision이다.
- Overview Futures Macro React UX 2차:
  - `.aiworkspace/note/finance/tasks/active/overview-futures-macro-react-ux-20260705/`에서 `futures_macro_workbench` React/Vite component와 Python wrapper를 추가했다.
  - React는 command strip, 현재 macro brief, score chips, 최근 1주 흐름, validation state, evidence drawer를 렌더링하고 Python은 DB 읽기 / validation 계산 / refresh action / raw tables를 계속 소유한다.
  - Overview contract 144개, `py_compile`, `npm run build`, snapshot payload smoke, `git diff --check`를 통과했다. 다음은 3차 1W / 1M reading-flow expansion이다.
- Overview Futures Macro React UX 1차:
  - `.aiworkspace/note/finance/tasks/active/overview-futures-macro-react-ux-20260705/`에서 Futures Macro 첫 진입 병목을 historical validation 동기 계산으로 확인하고 lazy/on-demand 경계로 분리했다.
  - 탭 진입은 `include_validation=False` snapshot만 읽고, `과거 점검 불러오기`가 validation / confidence를 session state에 저장한다.
  - `일봉 갱신` / `다시 읽기`는 session validation state를 clear한다. 다음은 2차 React component MVP다.
- Overview Market Movers Tab Actions / Statement Refresh:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-tab-actions-statement-refresh-20260702/`에서 선택 종목 조사 탭 액션을 분리했다.
  - News 탭은 뉴스 / 한국어 뉴스 metadata만, SEC 공시 탭은 SEC metadata와 필요한 재무제표 수집 action을 소유한다.
  - 재무제표 수집은 Overview UI direct fetch가 아니라 `app/jobs/overview_actions.py` selected-symbol facade를 통해 기존 Ingestion EDGAR statement refresh job으로 위임한다.
- Ingestion Console Structure V1:
  - `.aiworkspace/note/finance/tasks/active/ingestion-console-structure-v1-20260701/`에서 Ingestion 수집 화면을 1~4차로 정리했다.
  - collection workbench는 `일상 운영 / 검증 데이터`, `수동 복구 / 진단`, `실행 기록 / 결과` 3개 section으로 나뉘고, 기존 우측 column의 최근 수집 / 누적 실행 기록 / 상세 / 로그 / 실패 artifact는 기록 section으로 이동했다.
  - 공용 영역에는 최신 실행 결과 요약과 next action을 먼저 보여주고, 운영용 alias와 수동 복구 entry의 관계는 job brief에서 설명한다.
- Ingestion Manual Job State And Elapsed Time V1:
  - `.aiworkspace/note/finance/tasks/active/ingestion-manual-job-state-elapsed-v1-20260701/`에서 수동 수집 섹션 선택 상태와 실행 경과 시간 표시를 보강했다.
  - Ingestion collection section은 `st.pills` 기반 session state로 유지하고, manual job scheduling은 `collection_section` / `ui_started_at`을 job state에 저장한다.
  - Browser QA는 실제 EDGAR 수집 실행 없이 수동 섹션 전환과 화면 오류 부재를 확인했다.
- Fundamental Source Migration P0-P3:
  - `.aiworkspace/note/finance/tasks/active/fundamental-source-migration-p0-current-state-recheck/`부터 `p3-quarterly-correctness-gate/`까지 1~4차를 순차 진행했다.
  - Source contract는 `legacy_broad_yfinance`와 `sec_edgar_statement_shadow/strict`로 분리했고, Market Movers annual financials는 EDGAR statement shadow 우선으로 전환했다.
  - P3에서는 quarterly `10-K` / `10-K/A` full-year flow가 분기값으로 소비되지 않도록 shadow write/read policy gate를 추가했다.
- Fundamental Source Migration P4:
  - `.aiworkspace/note/finance/tasks/active/fundamental-source-migration-p4-backtest-strategy-migration/`에서 Backtest Analysis 기본 진입을 `Quality + Value / Strict Annual` statement annual path로 옮겼다.
  - Portfolio Mix Builder 기본 조합은 `Quality + Value`, `GTAA`, `Equal Weight`로 맞췄고, broad `Quality Snapshot`은 legacy replay / compatibility path로만 남겼다.
- Fundamental Source Migration P5:
  - `.aiworkspace/note/finance/tasks/active/fundamental-source-migration-p5-ingestion-workflow-cleanup/`에서 Ingestion operational refresh 흐름을 EDGAR annual statement refresh 우선으로 정리했다.
  - `Legacy broad yfinance fundamentals / factors`는 compatibility / explicit comparison path로 낮췄고, statement refresh result는 coverage / freshness / failed / next action 중심으로 해석한다.
  - 운영 절차는 [EDGAR Financial Statement Refresh Runbook](./docs/runbooks/EDGAR_FINANCIAL_STATEMENT_REFRESH.md)에 남겼다.
- Fundamental Source Migration P6:
  - `.aiworkspace/note/finance/tasks/active/fundamental-source-migration-p6-coverage-expansion-source-qa/`에서 DB-backed `Statement Universe Coverage QA`를 추가했다.
  - SP500 / Top1000 / Top2000 / Nasdaq annual statement shadow coverage를 reason group으로 설명하고, broad yfinance statement fallback 없이 targeted diagnosis / refresh / shadow rebuild로 이어지게 했다.
  - 2026-06-30 DB smoke 기준 annual shadow coverage는 SP500 94.04%, Top1000 95.3%, Top2000 47.65%, Nasdaq universe unresolved다.
- Overview Market Movers Redesign V2 1차:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-redesign-v2-01-20260629/`에서 사용자의 prototype UI 피드백을 1~6차 재설계 흐름으로 전환했다.
  - 1차는 새 데이터 / provider 없이 Market Movers의 화면 언어를 `변동 종목`, `랭킹 기준`, `상승 / 하락 / 거래량 / 이상 거래량 / 섹터`로 정리했다.
  - Benchmark 근거는 `.aiworkspace/note/finance/researches/active/2026-06-market-movers-redesign-v2-benchmark/`에 남겼고, 2차부터 metric-card 중심 화면을 market-board형 list / tape로 재구성한다.
### Earlier Backtest Track

- Backtest Policy Signal Help Board V1:
  - `.aiworkspace/note/finance/tasks/active/backtest-policy-signal-help-board-v1-20260705/`에서 `검증 기준 상세`을 1차 기준 category board + click help UI로 개선했다.
  - `Data Trust`, `Execution Source`, `Validation Source` 중심으로 무엇을 검증했는지 `plain_explanation` / `checked_items`로 보여준다.
  - 2차 review focus 상세 목록은 Backtest Analysis에서 제거하고, Practical Validation source snapshot / entry gate로 이어서 확인한다.
- Backtest Policy Signal Gate V7-V11:
  - `.aiworkspace/note/finance/tasks/active/backtest-policy-signal-gate-v7-v11-20260703/`에서 `검증 신호 · Policy Signals`와 `2차 실전성 검증 Handoff`의 gate 의미를 정리했다.
  - Practical Validation entry gate와 Portfolio Mix strict compare gate를 분리했고, `promotion_decision=hold`는 2차 진입 blocker가 아니라 review focus로 보존한다.
  - Candidate draft / Practical Validation source / component replay contract는 `handoff_readiness_snapshot`과 `entry_gate`를 함께 보존한다.
- Backtest Handoff Before Detail Tabs V1:
  - `.aiworkspace/note/finance/tasks/active/backtest-handoff-before-detail-tabs-v1-20260702/`에서 Run Backtest 직후 `2차 실전성 검증 Handoff`를 상세 결과 탭 위로 올렸다.
  - 현재 latest run 흐름은 `전략 결과/KPI -> 데이터 기준 요약 -> 실전성 검증 Handoff -> 상세 결과 탭`이다.
  - Handoff scoring, Practical Validation source handoff, registry / saved / validation persistence는 변경하지 않았다.
- Backtest Data Trust Heading Integrated V1:
  - `.aiworkspace/note/finance/tasks/active/backtest-data-trust-heading-integrated-v1-20260701/`에서 standalone `데이터 기준 요약` heading을 제거하고 Data Trust custom panel 내부 title로 흡수했다.
  - `먼저 볼 결론`은 panel 내부 읽기 cue로 유지해 KPI band와 Data Trust panel 사이의 시각적 이질감을 줄였다.
  - Data Trust 계산 모델, strategy runtime, result bundle schema, registry / saved / validation persistence는 변경하지 않았다.
- Backtest Result KPI Band V1:
  - `.aiworkspace/note/finance/tasks/active/backtest-result-kpi-band-v1-20260701/`에서 Run Backtest 결과 헤더와 핵심 성과 metric을 하나의 KPI band로 통합했다.
  - 기존 pill-like 기준 정보는 보조 기준선으로 낮추고, 별도 metric row는 latest run 기본 path에서 제거했다.
  - Strategy runtime, result bundle schema, registry / saved / validation persistence는 변경하지 않았다.
- Backtest Result Flow Reorder V1:
  - `.aiworkspace/note/finance/tasks/active/backtest-result-flow-reorder-v1-20260701/`에서 Run Backtest 직후 결과 화면을 `전략 결과 -> 핵심 성과 -> 데이터 기준 -> 상세 결과 -> 실전 검증 Handoff` 순서로 재정렬했다.
  - `Latest Backtest Run` 제목을 제거하고 전략명 기반 결과 헤더를 추가했다.
  - Strategy runtime, result bundle schema, registry / saved / validation persistence는 변경하지 않았다.
- Backtest Data Trust Summary Redesign V1:
  - `.aiworkspace/note/finance/tasks/active/backtest-data-trust-summary-redesign-v1-20260701/`에서 `Latest Backtest Run`의 Data Trust 영역을 한국어 `데이터 기준 요약` 패널로 재구성했다.
  - 기존 영어 metric card / raw badge 중심 표시와 중복 reading row / 세부 기준 expander를 제거하고, `계산 기준일 / 가격 기준 / 사용 데이터 / 검토 큐` 요약과 `이번 실행 검토 큐`를 같은 패널에 둔다.
  - Strategy runtime, result bundle schema, registry / saved / validation persistence는 변경하지 않았다.
- Backtest Latest Run Cleanup V1:
  - `.aiworkspace/note/finance/tasks/active/backtest-latest-run-cleanup-v1-20260701/`에서 Run Backtest 직후 결과 화면의 상단 `Execution Summary`와 Latest Run guide card를 제거했다.
  - 결과 화면은 `Data Trust Summary`, 전략 metric, next action, 조건부 결과 탭 중심으로 유지한다.
  - Strategy runtime, result bundle, registry / saved / validation persistence는 변경하지 않았다.
- Streamlit Native Pages Sidebar Fix:
  - `.aiworkspace/note/finance/tasks/active/streamlit-native-pages-sidebar-fix-20260630/`에서 cold/direct Backtest startup이 native Streamlit sidebar를 노출하던 원인을 정리했다.
  - Root cause는 `streamlit_app.py`의 top navigation과 `app/web/pages/backtest.py` legacy auto-discovery가 동시에 존재한 것이다.
  - Backtest shell은 `app/web/backtest_page.py`로 이동했고, `app/web/pages/`에는 user-facing `.py` page를 두지 않는 회귀 테스트를 추가했다.
- GTAA Result Cadence Monthly Valuation V1:
  - `.aiworkspace/note/finance/tasks/active/gtaa-result-cadence-monthly-valuation-20260629/`에서 GTAA `interval`을 input row thinning이 아니라 strategy-owned rebalance cadence로 보정했다.
  - GTAA month_end runtime은 월말 row 뒤에 요청 종료일 이하 최신 공통 거래일 row를 보강한다.
  - 2026-06-29 DB smoke 기준 결과 종료일은 `2026-03-16`이며, 이는 `SOXX/MTUM/QUAL/USMV` 가격 coverage가 그 날짜에서 멈춘 최신 공통일이다.
- Overview Final Cleanup V33-V36:
  - `.aiworkspace/note/finance/tasks/active/overview-final-cleanup-v33-v36-20260629/`에서 남은 1순위~4순위 cleanup을 순서대로 진행했다.
  - `app/web/overview_ui_components.py`는 23줄 compatibility facade로 줄었고 renderer body는 `app/web/overview/components/*`가 소유한다.
  - `app/web/overview_dashboard.py`는 `render_overview_dashboard` 1개 export만 남겼고, `app/services/overview_market_intelligence.py`는 삭제했다.
  - `app/services/overview/data_health.py`는 unused import를 제거하고 direct Market Context vs reference context `Scope` / coverage counts를 제공한다.
- Overview Service Split V25-V32:
  - `.aiworkspace/note/finance/tasks/active/overview-service-split-v25-v32-20260629/`에서 25차~32차를 순서대로 진행했고 각 차수마다 red test, focused QA, py_compile을 수행했다.
  - `app/services/overview_market_intelligence.py`는 7,788줄 구현체에서 96줄 compatibility facade로 축소했다.
  - Overview service bodies는 `app/services/overview/{market_context,market_movers,events,sentiment,data_health,why_it_moved}.py`가 도메인별로 소유한다.
- Overview Legacy Dashboard Removal V17-V24:
  - `.aiworkspace/note/finance/tasks/active/overview-legacy-dashboard-removal-v17-v24-20260625/`에서 17차~24차를 순서대로 진행했고 각 차수마다 focused tests, Overview contract, py_compile, Browser QA를 수행했다.
  - `app/web/overview/legacy_dashboard.py`를 삭제했고, `app/web/overview_dashboard.py`는 필요한 compatibility helper만 explicit export하는 wrapper로 바꿨다.
  - Market Context / Market Movers / Futures Macro / Sentiment / Events tab-local helpers가 active Streamlit glue와 refresh/render helper를 소유한다.
  - QA screenshots는 local generated artifact로만 보존한다.
- Overview Tab Helper Extraction V11-V16:
  - `.aiworkspace/note/finance/tasks/active/overview-tab-helper-extraction-v11-v16-20260625/`에서 11차~16차를 순서대로 진행했고 각 차수마다 focused tests, Overview contract, py_compile, Browser QA를 수행했다.
  - Active primary tab entrypoint는 `app/web/overview/{tab}.py`, tab-local Streamlit glue는 `app/web/overview/{tab}_helpers.py`가 소유하도록 정리했다.
  - `legacy_dashboard.py`는 active page / tab owner가 아니라 lower-level compatibility helper surface로 남겼고, active primary tab files는 직접 import하지 않는다.
  - QA screenshots는 local generated artifact로만 보존한다.
- Overview Structure Split V2-V5:
  - `.aiworkspace/note/finance/tasks/active/overview-structure-split-v2-v5-20260625/`에서 Overview 구조 분리 2차~5차를 순서대로 완료했다.
  - Primary tab orchestration은 `app/web/overview/*` entry module이 소유하고, visual component surface는 `app/web/overview/components/*`, service read-model surface는 `app/services/overview/*`로 분리했다.
  - 5차에서는 service surface Streamlit-free, component surface service/data import 금지, active page/tab direct job/data import 금지, thin compatibility wrapper guard를 추가했다.
  - 각 차수별 focused test, Overview contract, py_compile, Browser QA를 수행했고 QA screenshots는 local generated artifact로만 보존한다.
- Overview Futures Macro Refresh State V1:
  - `.aiworkspace/note/finance/tasks/active/overview-futures-macro-refresh-state-v1-20260624/`에서 `선물 매크로` 탭의 최신일 표시 / cache 갱신 경로를 점검했다.
  - DB의 1D futures row는 16개 core symbol 모두 `2026-06-24`까지 들어와 있었고, stale 표시 원인은 열려 있는 앱 프로세스의 15분 snapshot cache와 탭-local refresh control 부재로 좁혔다.
  - 최신 stored daily candle marker를 snapshot cache key에 포함하고, `일봉 매크로 갱신` / `최신 데이터 다시 읽기` 버튼을 `Futures Macro` 탭에 추가했다.
- Overview Futures Macro Mixed Substates V1:
  - `.aiworkspace/note/finance/tasks/active/overview-futures-macro-mixed-substates-v1-20260624/`에서 `혼재된 매크로 흐름` fallback에 하위 맥락을 추가했다.
  - 상위 scenario label은 historical validation compatibility를 위해 그대로 유지하고, `sub_scenario`, `regime_hint`, `mixed_reason`만 read model / brief hero에 노출한다.
  - 이번 1차는 저장된 futures 일봉 score만 사용하며 FRED / VIX / credit spread 기반 전문 macro score 확장은 2차 후보로 남겼다.
- Overview Futures Macro Tab Split V1:
  - `.aiworkspace/note/finance/tasks/active/overview-futures-macro-tab-split-v1-20260624/`에서 `선물 매크로` primary tab을 추가했다.
  - `시장 맥락` 기본 로드는 futures macro historical validation과 historical analog를 제외하고 movement / breadth / sentiment / events / data 중심의 light cockpit을 렌더링한다.
  - `선물 매크로` 탭은 저장된 futures 일봉 기반 macro 진단과 과거 validation을 소유한다.
  - `nyse_price_history` 최신 raw date 조회는 `MAX(date)` 대신 latest row ordering query로 바꿨다.
- Overview Market Context Load Gate Removal V1:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-load-gate-removal-v1-20260624/`에서 `시장 맥락 불러오기` gate를 제거했다.
  - Market Context는 전처럼 선택 즉시 cockpit body를 렌더링한다.
  - Internal `st.pills` text-tab underline navigation과 no-anchor switching은 유지했다.
  - Cold timing 기준 느린 경로는 `load_overview_macro_context_cockpit` fan-out이며, 특히 futures macro validation이 약 7.8초로 가장 컸다.
- Overview Nav Internal Lazy Load V1:
  - `.aiworkspace/note/finance/tasks/active/overview-nav-internal-lazy-load-v1-20260623/`에서 Overview primary tabs를 anchor/link navigation에서 내부 `st.pills` selector로 교체했다.
  - 사용자 제공 reference처럼 plain text tabs + active red underline으로 보이게 하고, `?overview_tab=market-movers` slug는 호환 입력으로만 유지한다.
  - 이 작업에서 추가했던 `시장 맥락 불러오기` gate는 `overview-market-context-load-gate-removal-v1-20260624`에서 제거됐다.
  - 범위는 navigation/loading polish이며 provider / schema / registry / saved / validation / monitoring / trading boundary는 그대로 유지했다.
- Overview Primary Nav Pill V1:
  - `.aiworkspace/note/finance/tasks/active/overview-primary-nav-pill-v1-20260623/`에서 Overview primary navigation을 기본 Streamlit segmented/radio 느낌에서 compact custom pill nav로 바꿨다.
  - Korean primary labels와 English secondary labels를 함께 두고, `?overview_tab=market-movers` 같은 query-param slug로 직접 탭 선택을 유지한다.
  - 이 anchor 기반 visual polish는 `overview-nav-internal-lazy-load-v1-20260623`에서 내부 widget 기반 underline text tabs로 대체됐다.
  - 범위는 visual/navigation polish이며 provider / schema / registry / saved / validation / monitoring / trading boundary는 그대로 유지했다.
- Overview Primary Tab Soft Remove V1:
  - `.aiworkspace/note/finance/tasks/active/overview-primary-tab-soft-remove-v1-20260623/`에서 Overview primary navigation을 네 탭으로 줄였다.
  - `Futures Monitor`와 `Sector / Industry` standalone tabs는 primary selector / lazy dispatch에서 제거했고, 기존 selected value는 `Market Context`로 fallback한다.
  - Futures / sector service와 helper renderer는 물리 삭제하지 않았고, provider / schema / registry / saved / validation / monitoring / trading boundary는 그대로 유지했다.
- Futures Monitor Workbench V1.1:
  - `.aiworkspace/note/finance/tasks/active/futures-monitor-workbench-v1_1-20260623/`에서 Workbench V1 후속 UX/UI 개선을 완료했다.
  - `자료 갱신` module이 1분봉 / 일봉 매크로 / 화면 reload / 확인 방식을 소유하고, context bar는 버튼 문구 반복 없이 상태만 요약한다.
  - `근거 해석 / 원본 데이터`는 `현재 근거 상태 -> 과거 점검 요약 -> 자료 관리 -> 원본 표` 순서로 재정렬했다.
  - Focused 98 tests, py_compile, `git diff --check`, Browser QA가 통과했다. Screenshot artifacts는 local generated artifact로만 보존한다.
- Futures Monitor Workbench Layout V1:
  - `.aiworkspace/note/finance/tasks/active/futures-monitor-workbench-layout-v1-20260623/`에서 benchmark guide를 코드로 옮겨 `Workspace > Overview > Futures Monitor`를 workbench형 기본 화면으로 재구성했다.
  - 기본 화면은 `context bar -> compact watch strip -> market brief hero -> weekly flow lane -> chart workspace` 순서로 읽고, 심볼 편집 / 갱신 설정 / 원본 근거 / provider diagnostics는 접힌 상세로 낮췄다.
  - Focused helper contract 4개, Overview/Futures contract 95개, py_compile, `git diff --check`, Browser QA가 통과했다.
- Futures Monitor UI benchmark:
  - `.aiworkspace/note/finance/researches/active/2026-06-futures-monitor-ui-benchmark/`에서 Toss Securities를 포함한 5개 UX/UI benchmark 축을 정리했다.
  - 결론은 다음 구현이 copy polish가 아니라 `context bar -> market brief hero -> weekly flow lane -> linked watch/chart workspace`로 가는 workbench redesign이어야 한다는 것이다.
- Futures Monitor Dedup UX V1:
  - `.aiworkspace/note/finance/tasks/active/futures-monitor-dedup-ux-v1-20260623/`에서 `Workspace > Overview > Futures Monitor` 기본 화면의 중복 노출을 정리했다.
  - Command center / Macro Context / Live Chart의 정보 소유권을 분리해 provider run rows와 latest candle detail은 기본 화면에서 낮추고 diagnostics에 남겼다.
  - Focused Futures contract 91개, py_compile, `git diff --check`, Browser QA가 통과했다.
- Futures Monitor UX/UI V3:
  - `.aiworkspace/note/finance/tasks/active/futures-monitor-ux-ui-v3-20260622/`에서 `Workspace > Overview > Futures Monitor` 1차~4차 UX/UI 개선을 완료했다.
  - 상단 watch group / data refresh UX를 한글 중심으로 단순화하고, Macro Context에 오늘 기준 해석 + 최근 1주 흐름 + 근거 해석 카드를 추가했다.
  - 원본 표는 `근거 해석 / 원본 데이터` 하단으로 낮췄고, Browser QA 스크린샷은 local generated artifact로만 보존한다.
  - Boundary stayed Overview context-only: no provider/schema/registry/saved write, no validation gate, monitoring signal, approval, order, or auto rebalance.
- Overview IA Cleanup V22:
  - `.aiworkspace/note/finance/tasks/active/overview-ia-cleanup-v22-20260622/`에서 Overview primary tab을 시장 context drilldown 중심으로 정리했다.
  - `Data Health`는 Market Context source / refresh evidence와 Operations / Ingestion 소유로 낮췄고, `Candidate Ops`는 Overview render path에서 제거했다.
  - `Sector / Industry`는 유지하되 raw table을 `상세 표`로 낮췄다. registry / saved JSONL, run history, provider / DB schema, Backtest / validation / monitoring / trade semantics는 바꾸지 않았다.
- historical full archive:
  - [WORK_PROGRESS_ARCHIVE_20260413.md](/Users/taeho/Project/quant-data-pipeline/.aiworkspace/note/finance/archive/WORK_PROGRESS_ARCHIVE_20260413.md)
- historical archive note:
  - archived before the 2026-05 `.aiworkspace/note/finance` rebuild; use task/phase docs for detailed current work history.

## Entries

## 2026-07-12 KST - Master Merge Conflict Integration

- `finance/data/db/schema.py`에서 Institutional 13F schema 6개와 S&P 500 valuation / EPS / SEP schema 3개를 독립 group으로 모두 보존했다.
- Finance durable docs와 root handoff logs는 Institutional Portfolios, Final Review, Market Context 변경을 함께 유지하되 current/latest task pointer를 실제 HEAD 이력 기준 하나로 정렬했다.
- master에 포함된 registry / saved reset migration은 기존 승인된 task 결과로 보존하고, untracked QA PNG는 병합 대상에서 제외했다.
- 검증은 JSONL 21행, staged Python compile, Institutional Portfolios 39개, S&P 500 valuation 37개, evidence closure 18개, GRS 5개를 통과했다. Service contracts는 805개 중 804개가 통과했고, 양쪽 baseline에 공통인 Sentiment React source-contract 1건은 별도 후속으로 남겼다.

### 2026-07-02 - Market Movers investigation actions are tab-local
- Completed `.aiworkspace/note/finance/tasks/active/overview-market-movers-tab-actions-statement-refresh-20260702/` after the user approved splitting selected-symbol investigation actions.
- Replaced the combined `뉴스·공시 메타데이터 조회` action with News-tab metadata and SEC-tab metadata actions.
- Added SEC-tab `필요 재무제표 수집` that calls `run_overview_market_mover_statement_refresh` for the selected symbol and keeps elapsed-time result context in place.
- Verification passed: focused red-green contracts, compact metadata regressions, OverviewAutomation / OverviewMarketIntelligence contract classes, py_compile, `git diff --check`, and Browser QA without live EDGAR collection.

### 2026-07-01 - Ingestion manual collection section now survives job reruns
- Completed `.aiworkspace/note/finance/tasks/active/ingestion-manual-job-state-elapsed-v1-20260701/` after the user approved fixing the manual financial statement collection UX.
- Replaced the Ingestion collection `st.tabs` with a session-state `st.pills` selector and stored `collection_section` / `ui_started_at` on scheduled jobs.
- Running job banner and large-job progress captions now include elapsed time.
- Browser QA confirmed manual section selection renders the manual cards without the expanded daily operational body; screenshot is local generated artifact only.

### 2026-06-30 - Streamlit native pages sidebar removed from cold Backtest startup
- Completed `.aiworkspace/note/finance/tasks/active/streamlit-native-pages-sidebar-fix-20260630/`.
- Moved Backtest shell from `app/web/pages/backtest.py` to `app/web/backtest_page.py` so Streamlit no longer auto-discovers a legacy sidebar page alongside the Finance Console top navigation.
- Added a service contract guard preventing user-facing `.py` files under `app/web/pages/`.
- Durable maps now point future Backtest UI edits at `app/web/backtest_page.py` plus `app/web/backtest_*.py`.

### 2026-06-29 - GTAA result cadence now separates monthly valuation from rebalance cadence
- Completed `.aiworkspace/note/finance/tasks/active/gtaa-result-cadence-monthly-valuation-20260629/` after the user clarified that non-rebalance months should still show new candidate signals.
- GTAA sample/runtime paths no longer call `.interval(interval)` before strategy execution; `GTAA3Strategy(rebalance_interval=...)` owns actual holdings change cadence.
- Added latest-common-trading-day row supplementation after month-end filtering, so current partial-period valuation can appear when all requested tickers have data for that trading day.
- Verification passed: focused GTAA tests, ETF runtime contract tests, service contract tests, py_compile, DB-backed smoke, and `git diff --check`.

### 2026-06-25 - Overview Legacy Dashboard Removal V17-V24
- Completed `.aiworkspace/note/finance/tasks/active/overview-legacy-dashboard-removal-v17-v24-20260625/` after the user approved continuing 17차~24차 sequentially with QA after each phase.
- Removed `app/web/overview/legacy_dashboard.py` and replaced the old wrapper re-export loop in `app/web/overview_dashboard.py` with explicit compatibility exports.
- Moved remaining helper ownership into `app/web/overview/*_helpers.py`, including Market Context refresh, Market Movers refresh / Why It Moved helpers, Futures Macro panel/models, Sentiment, and Events.
- Verification passed: py_compile, Overview contract 112 tests, legacy import scan, and Browser QA; final QA screenshot is `overview-legacy-dashboard-removal-v24-final-qa.png`.

### 2026-06-25 - Overview Structure Split V2-V5
- Completed `.aiworkspace/note/finance/tasks/active/overview-structure-split-v2-v5-20260625/` after the user asked to continue 2차~5차 sequentially with QA after each phase.
- V2 moved tab-level orchestration into `app/web/overview/*`; V3 added domain component surfaces; V4 added domain service surfaces; V5 added boundary guard contracts.
- Verified each phase with focused contracts, py_compile, Overview contract, and Browser QA; final V5 Browser QA screenshot is `overview-structure-split-v5-qa.png`.
- Remaining structural cleanup is physical extraction from `legacy_dashboard.py` and `overview_market_intelligence.py`, not another UI-only polish pass.

### 2026-06-25 - Overview Tab Helper Extraction V11-V16
- Completed `.aiworkspace/note/finance/tasks/active/overview-tab-helper-extraction-v11-v16-20260625/` after the user approved continuing 11차~16차 sequentially with QA after each phase.
- Added `market_context_helpers.py`, `events_helpers.py`, `futures_macro_helpers.py`, `market_movers_helpers.py`, and `sentiment_helpers.py` under `app/web/overview/`.
- Active Overview tab entry modules no longer import `legacy_dashboard.py` directly; low-level compatibility helpers remain there behind tab-local helper bridge modules.
- Verified each phase with focused contracts, py_compile, Overview contract, and Browser QA; final V16 Browser QA screenshot is `overview-tab-helper-extraction-v16-sentiment-qa.png`.

### 2026-06-24 - Overview Market Context Load Gate Removal V1
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-load-gate-removal-v1-20260624/` after the user rejected the extra `시장 맥락 불러오기` step.
- Removed the explicit Market Context load gate and restored immediate Market Context body rendering when selected.
- Measured the load path: cold cockpit about 15.8s; largest parts were futures macro validation, sector leadership, market movers, and historical analog.
- Boundaries stayed unchanged: no provider/schema/DB/registry/saved write, no validation/monitoring/trading semantics.

### 2026-06-23 - Overview Nav Internal Lazy Load V1
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-nav-internal-lazy-load-v1-20260623/` after the user reported the previous tab nav behaved like link navigation and startup was too slow.
- Replaced rendered tab anchors with internal `st.pills` state and styled it as plain text tabs with a red active underline per the user-provided reference.
- Added first-entry lazy gate so default `Market Context` did not call `load_overview_macro_context_cockpit` until `시장 맥락 불러오기`; this gate was removed on 2026-06-24.
- Boundaries stayed unchanged: no provider/schema/DB/registry/saved write, no physical service deletion, no validation/monitoring/trading semantics.

### 2026-06-23 - Overview Primary Nav Pill V1
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-primary-nav-pill-v1-20260623/` after the user asked whether the current tab bar could be more designed.
- Replaced the default-looking Streamlit segmented/radio selector with a scoped compact pill nav for `Market Context`, `Market Movers`, `Sentiment`, and `Events`.
- Added query-param slugs for direct tab selection and verified `?overview_tab=market-movers` with Browser QA.
- Superseded by `overview-nav-internal-lazy-load-v1-20260623`, which removed rendered anchors and kept switching inside the current browser session.
- Boundaries stayed unchanged: no provider/schema/DB/registry/saved write, no validation/monitoring/trading semantics.

### 2026-06-23 - Overview Primary Tab Soft Remove V1
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-primary-tab-soft-remove-v1-20260623/` after the user decided `Futures Monitor` and `Sector / Industry` did not have clear enough standalone product value.
- Removed both labels from the Overview primary selector and renderer dispatch, so stale selected values fall back to `Market Context`.
- Synced Overview docs to current primary tabs: `Market Context`, `Market Movers`, `Sentiment`, `Events`.
- Boundaries stayed unchanged: no provider/schema/DB/registry/saved write, no physical deletion of service/helper code, no validation/monitoring/trading semantics.

### 2026-06-23 - Futures Monitor Workbench V1.1
- Opened and completed `.aiworkspace/note/finance/tasks/active/futures-monitor-workbench-v1_1-20260623/` for the user-requested Workbench V1 follow-up.
- Unified refresh actions into `자료 갱신`, separated live 1분봉 and macro daily 1D states, and kept provider/schema/registry/saved boundaries unchanged.
- Replaced guide-like evidence wording with current-state evidence counts and added current-scenario validation summary before raw tables.
- Verification passed: focused 98 tests, py_compile, `git diff --check`, Browser QA with generated screenshots.

### 2026-06-23 - Futures Monitor Workbench Layout V1
- Opened and completed `.aiworkspace/note/finance/tasks/active/futures-monitor-workbench-layout-v1-20260623/` after the user approved implementing the benchmark-led Futures Monitor redesign.
- Replaced the default command-center/card feel with a workbench context bar, compact watch strip, market brief hero, weekly flow lane, and chart workspace question.
- Moved symbol selection and refresh mode controls into collapsed edit/settings areas while preserving the existing DB-backed read-only data boundary.
- Boundaries stayed unchanged: no provider/schema/registry/saved write, no live trading/order/recommendation/monitoring signal semantics.

### 2026-06-23 - Futures Monitor UI benchmark with Toss Securities
- Opened `.aiworkspace/note/finance/researches/active/2026-06-futures-monitor-ui-benchmark/` after the user asked whether external UX/UI benchmarking was needed and requested Toss Securities to be included.
- Benchmarked five pattern classes: TradingView / Koyfin, IBKR-style professional workspaces, Datadog / Grafana, Stripe / Linear, and Toss Securities.
- Recommended next build is a Streamlit workbench redesign using current DB-backed read models: compact context bar, market brief hero, weekly flow lane, linked watch/chart workspace, and evidence disclosures.
- Boundaries remain read-only Overview context only; no live trading, broker order, provider/schema change, or investment recommendation semantics.

### 2026-06-23 - Futures Monitor Dedup UX V1
- Opened and completed `.aiworkspace/note/finance/tasks/active/futures-monitor-dedup-ux-v1-20260623/` after the user asked whether the Futures Monitor default surface still had duplicate exposure.
- Consolidated default ownership: command center owns page state / next action / top move, Macro hero owns scenario, support strip owns confidence / validation, Live Chart owns chart context and symbol-level state.
- Added regression contracts for default-surface duplication and shortened Macro confidence values to avoid repeating card titles.
- Boundaries stayed unchanged: read-only Overview context only, no provider/schema/registry/saved write, and no validation / monitoring / trading semantics.

### 2026-06-22 - Futures Monitor UX/UI V3 1차~4차
- Opened and completed `.aiworkspace/note/finance/tasks/active/futures-monitor-ux-ui-v3-20260622/` after the user approved sequential 1차~4차 development for `Workspace > Overview > Futures Monitor`.
- Simplified the Futures Monitor controls and `데이터 갱신` popover, added recent 1-week macro context from stored 1D futures rows, and rendered evidence interpretation before raw data tables.
- Added service contract coverage for `weekly_context` and Korean evidence reading; compile, focused service tests, and Browser QA passed.
- Boundaries stayed unchanged: read-only Overview market context only, no schema/provider change, no registry / saved write, and no validation / monitoring / trading semantics.

### 2026-06-22 - Overview Market Context Source / Refresh UX V21
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-source-refresh-ux-v21-20260622/` after user feedback that `근거: 자료 기준 / 출처 상태` and `필요 자료 보강` still looked like prototype diagnostic UI.
- Reworked source confidence into `자료 상태 요약`, `시장 브리프 직접 자료`, `참고 / 관리 자료`, and `보강 판단` flow.
- Reworked refresh assist so no-action state omits the disabled smart-refresh button and keeps only compact status plus full-refresh fallback.
- Boundaries stayed unchanged: DB-backed stored snapshots only, existing Overview action boundary, no provider fetch during render, no schema / registry / saved write, and no validation / monitoring / trading semantics.

### 2026-06-22 - Overview Market Context Macro Intersection V18
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-intersection-v18-20260622/` after user noted that applying GLD before rate futures could look order-dependent.
- Added `macro_condition_counts` so Macro conditioned analog distinguishes broad sample, GLD same-state count, Rate Pressure futures same-state count, futures-computable count, and final GLD / futures intersection count.
- Updated the Macro basis bar to `기본 유사 맥락 기준` / `GLD 같은 상태` / `금리선물 같은 상태` / `두 조건 모두`, while the conditioned result matrix still uses the final intersection sample.
- Boundaries stayed unchanged: no new bucket rule, provider, schema, persistence, registry / saved write, validation, monitoring, or trading semantics.

### 2026-06-21 - Overview Market Context Macro Polish V17
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-polish-v17-20260621/` after user feedback that Macro condition steps still did not explain what GLD / rate-futures conditions meant and the reference Macro backdrop still looked text-heavy.
- Added one-line condition meaning inside the Macro basis bar for broad sector ETF vs SPY analog pool, current-like GLD bucket, and current-like `ZN=F` / `ZB=F` rate-pressure bucket.
- Reworked reference-only T10Y3M / VIXCLS / BAA10Y backdrop into Korean state badges, current values, same-state ratio bars, and compact source labels.
- Boundaries stayed unchanged: DB-backed read model only, no render-time provider fetch, no schema / registry / saved write, no new hard Macro condition, and no validation / monitoring / trading semantics.

### 2026-06-21 - Overview Market Context Analog / Macro UX V11
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-macro-ux-v11-20260621/` after user feedback that historical analog and Macro conditioned comparison still looked prototype-like and over-carded.
- Reworked historical analog into a basis bar, method grid, summary strip, and `먼저 볼 점` / `주의할 점` split.
- Moved Macro conditioned comparison into a separate sibling section with funnel, broad-vs-conditioned lanes, condition-role groups, and dimension audit details.
- Boundaries stayed unchanged: DB-backed read model only, no render-time provider fetch, no schema / registry / saved write, no FRED / events / sentiment hard conditioning, and no validation / monitoring / trading semantics.

### 2026-06-20 - Overview Market Context Session Basis V9
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-session-basis-v9-20260620/` after user feedback that a weekend / closed market should not read as `오늘의 시장 브리프`.
- Connected the existing NYSE session helper to Market Context so open sessions keep `오늘의 시장 브리프`, while weekends / holidays show `마지막 거래일 시장 브리프` with the previous trading date as basis.
- Closed-session intraday elapsed-age stale states no longer create `현재 이슈만 보강` actions; genuinely failed / missing sources can still surface as actionable.
- Boundaries stayed unchanged: DB-backed snapshots only, no render-time provider fetch, no schema / registry / saved write, and no validation / monitoring / trading semantics.

### 2026-06-20 - Overview Market Context Source Actionability V8
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-source-actionability-v8-20260620/` after user feedback that Events and Data Health still appeared as unresolved `자료 확인 필요` even though smart refresh excluded Events and Data Health is management meta.
- Added source-confidence actionability metadata and made top `자료 상태` count only actionable refresh items.
- Events estimate caveats now show as `참고 제한`; Data Health now shows as `관리 메타`; the source ledger separates `브리프 자료` from `참고 / 관리 메타`.
- Boundaries stayed unchanged: DB-backed snapshots only, no render-time provider fetch, no schema / registry / saved write, and no validation / monitoring / trading semantics.

### 2026-06-20 - Overview Market Context Smart Refresh V7
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-smart-refresh-v7-20260620/` after user feedback that Events caveats were not actual market-context conclusions and the refresh action should target current issues instead of always running every job.
- Kept `오늘의 시장 브리프` to movement, breadth, and Futures/Macro rows; Events now stays in timeline/source evidence and `refresh_plan.excluded_items`.
- Added `refresh_plan` plus `현재 이슈만 보강` smart refresh and kept `전체 Market Context 자료 보강` as fallback through the existing Overview action facade.
- Boundaries stayed unchanged: DB-backed snapshots only, no render-time provider fetch, no schema / registry / saved write, and no validation / monitoring / trading semantics.

### 2026-06-20 - Overview Market Context Brief Context Absorption V6
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-context-absorption-v6-20260620/` after user feedback that `브리프 신뢰도` still felt like a guide rather than necessary Market Context content.
- Removed the independent `브리프 신뢰도` section and `brief_caveats` payload.
- Folded event limitations into an optional `이벤트 배경` brief row and Futures data-health limitations into the `Futures/Macro 배경` row only when Futures/OHLCV freshness actually limits macro interpretation.
- Boundaries stayed unchanged: DB-backed snapshots only, no render-time provider fetch, no schema / registry / saved write, and no validation / monitoring / trading semantics.

### 2026-06-20 - Overview Market Context Brief Confidence V5
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-confidence-v5-20260620/` after user feedback that Events / data caveats inside `오늘의 시장 브리프` did not read like market brief conclusions.
- Returned `오늘의 시장 브리프` to three core rows: movement, breadth, and Futures/Macro background.
- Added a separate `브리프 신뢰도` section for Events / 자료 기준 so those rows adjust reading strength rather than becoming market conclusions.
- Boundaries stayed unchanged: DB-backed snapshots only, no render-time provider fetch, no schema / registry / saved write, and no validation / monitoring / trading semantics.

### 2026-06-20 - Overview Market Context Brief Findings Integration V4
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-findings-integration-v4-20260620/` after user feedback that V3 `맥락 검토 결과` still repeated P1/P2 content already present in the main brief.
- Moved Events / 자료 신뢰도 caveat into the `오늘의 시장 브리프` sequence and stopped rendering `context_findings` / `next_checks` as a default separate findings rail.
- Removed the now-empty reading-flow call before historical analog controls; historical analog / source confidence remain below the 기준 controls.
- Boundaries stayed unchanged: DB-backed snapshots only, no render-time provider fetch, no schema / registry / saved write, and no validation / monitoring / trading semantics.

### 2026-06-20 - Overview Market Context Context Findings V3
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-context-findings-v3-20260620/` after user feedback that `다음 맥락 체크` still told the user to inspect other tabs instead of producing conclusions.
- Added `context_findings` to the Market Context cockpit read model and rendered `맥락 검토 결과` with conclusion / interpretation impact / evidence / freshness for price movement, Futures / Macro, Events, and Data Health caveat.
- Kept boundaries unchanged: stored DB-backed snapshots only, Overview bounded refresh facade only, no provider fetch during render, no schema / registry / saved write, and no validation / monitoring / trading semantics.
- Verification details and Browser QA screenshot are in the task `RUNS.md`; generated screenshot is not staged.

### 2026-06-19 - Overview Market Context Macro Dimension Audit V3C
- Opened and completed `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-dimension-audit-v3c-20260619/` for the approved 3차-C Market Context historical analog follow-up.
- Added `macro_dimension_audit` under `Macro 조건 포함 pilot` and rendered `맥락 차원 상태` so users can see actual conditions, stored FRED preview dimensions, and event / sentiment deferred context.
- Actual hard conditions remain sector ETF vs SPY, GLD price proxy, and `ZN=F` / `ZB=F` Rate Pressure futures proxy; FRED / events / sentiment are not hard historical filters.
- Verification details and Browser QA screenshot are in the task `RUNS.md`; generated screenshot is not staged.

### 2026-06-18 - Overview Market Context Macro-Conditioned Analog Pilot V1
- Opened `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-conditioned-analog-pilot-v1-20260618/` for the approved 3차-A `Macro 조건 포함` pilot.
- Preserved the existing broad historical analog and added a separate pilot payload/UI block that filters broad anchors with one additional stored-data condition: GLD price proxy safe-haven / gold context.
- The pilot now shows used conditions, insufficient conditions, excluded/deferred conditions, sample reduction reason, and sample quality.
- Boundary stayed Overview-only and context-only: no new provider, loader, schema, FRED collection, events/sentiment conditioning, UI render fetch, validation gate, monitoring signal, or trading semantics.

### 2026-06-18 - Overview Market Context Analog As-Of Window V2
- Opened `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-asof-window-v2-20260618/` for the approved 2차 `참고: 과거 유사 맥락` 기준 시점 / 패턴 기간 expansion.
- Extended the historical analog read model and UI so users can compare `latest` or a selected 기준일 with `5D` / `20D` / `monthly` pattern windows while keeping the existing positive rate / median / best / worst / sample table.
- As-of replay is bounded by existing DB data: price history is filtered to the selected 기준일, while full point-in-time sector leadership still requires an approved historical universe / sector snapshot read path.
- Boundary stayed Overview-only and context-only: no new provider, schema, persistence path, registry / saved JSONL write, macro-conditioned analog, Backtest / Practical Validation / Final Review / Operations core logic, or trading semantics.

### 2026-06-17 - Finance Integration Doc Merge Skill
- Opened `.aiworkspace/note/finance/tasks/active/finance-integration-doc-merge-skill-20260617/` after the user approved strengthening the existing merge-review skill.
- Added `references/doc-merge-conflict-checklist.md` to `finance-integration-review` for `.aiworkspace/note/finance` Markdown conflicts.
- Mirrored the repo-local skill source to the installed runtime skill under `~/.codex/skills`.
- Boundary stayed workflow-only: no automatic conflict resolver, registry / saved rewrite, task archive migration, or generated artifact cleanup.

### 2026-06-16 - Overview Market Movers Period Refresh V1
- Opened `.aiworkspace/note/finance/tasks/active/overview-market-movers-period-refresh-v1-20260616/` for the approved Market Movers period refresh UX fix.
- Kept Daily refresh behavior intact: intraday snapshot refresh, auto refresh option, universe refresh, and screen reload remain Daily-only.
- Added Weekly / Monthly / Yearly EOD price-history manual refresh through the existing Overview action facade and OHLCV ingestion job boundary.
- Boundary stayed Market Movers-only: no Market Context / Futures / Events / Backtest / Operations / historical analog changes, no provider/schema/registry/saved change, and no non-daily auto refresh.

### 2026-06-16 - Overview Market Context Analog Readability V5
- Opened `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-readability-v5-20260616/` after the user approved 1차~3차 for `참고: 과거 유사 맥락` readability.
- Reworked the historical analog OK state so the user reads the similarity definition, summary strip, and `먼저 읽을 결론` before the detailed statistics table.
- Split detailed rows into `핵심 자산 요약` and `보조 자산 참고` while keeping the existing sector ETF relative-strength calculation.
- Boundary stayed Overview-only and context-only: no calculation change, macro/futures/event conditioning, provider/schema/storage change, validation / monitoring / trading semantics, or render-time fetch.

### 2026-06-15 - Overview Market Context Analog Repair V4
- Opened `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-repair-v4-20260615/` after the user approved making historical analog `자료 부족` actionable and visibly different.
- Added generalized historical analog coverage gaps plus a bounded Overview OHLCV repair action; live QA targeted `Communication Services -> XLC`, confirming the flow is not hard-coded to Technology / XLK.
- Source confidence now shows normal / review / missing counts and key source pills before the disclosure is opened.
- Boundary stayed Overview-only: no new provider, schema, loader, CSV upload, registry / saved JSONL write, validation / monitoring / trading semantics, or automatic render-time fetch.

### 2026-06-15 - Overview Market Context Section Flow V1 1차
- Opened `.aiworkspace/note/finance/tasks/active/overview-market-context-section-flow-v1-20260615/` after the user approved splitting the hybrid Market Context surface into clearer reading sections.
- Kept the top cockpit focused on headline, 5-cell tape, sector pressure map, and event timeline; moved `시장 브리프`, `해석할 때 같이 볼 변수`, `과거 유사 맥락 참고`, and source confidence into sibling reading-flow sections.
- Browser QA confirmed 1 cockpit, 1 reading flow, 4 reading sections, no brief/cue text inside the top cockpit, and 390px mobile no-horizontal-overflow behavior.
- Boundary stayed Overview-only: no provider fetch, schema/persistence change, registry / saved JSONL write, validation / monitoring / trading semantics, or dashboard-editor interactivity.

### 2026-06-15 - Overview Market Context Hybrid Visual V1 1차
- Opened `.aiworkspace/note/finance/tasks/active/overview-market-context-hybrid-visual-v1-20260615/` after the user approved mixing benchmark option 1 and 3.
- Reworked `Workspace > Overview > Market Context` into a card-light hybrid cockpit: 5-cell tape, sector pressure map, event timeline, existing evidence rows, historical analog disclosure, and source confidence disclosure.
- Browser QA confirmed desktop render plus 390px mobile no-horizontal-overflow behavior; screenshot artifact is `overview-market-context-hybrid-visual-v1-qa.png`.
- Boundary stayed Overview-only: no provider fetch, schema/persistence change, registry / saved JSONL write, validation / monitoring / trading semantics, or dashboard-editor interactivity.

### 2026-06-15 - Overview Market Context Historical Analog V1 4차
- Opened `.aiworkspace/note/finance/tasks/active/overview-market-context-historical-analog-v1-20260615/` for the 4차 Market Context follow-up.
- Added a context-only `과거 유사 맥락 참고` MVP: current sector leadership resolves through a generic sector ETF proxy map, checks DB price coverage, and only computes 5D / 20D / 60D historical forward-return summaries when coverage is sufficient.
- Local DB currently maps `Industrials -> XLI`, but `XLI` has only 63 daily rows, so the live UI shows `자료 부족` with the coverage reason rather than forcing an analog result.
- Boundary stayed Overview-only: no prediction model, recommendation / trade signal, Backtest / Validation / Final Review / Operations connection, schema/provider change, registry write, or saved JSONL write.

### 2026-06-12 - Backtest Direction Reset Research
- Opened `.aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/` to re-audit Backtest Analysis, strategy runtime, validation handoff, history replay, and saved replay product direction.
- Conclusion: Backtest Analysis should stay centered on execution / comparison / candidate source / replay, while evidence / governance / diagnostics should become compact handoff or downstream validation / review / monitoring context.
- 4C execution-first reset and 5A/5B runtime/result contract hardening remain retained work; strict quarterly 5C and Risk-On downstream promotion remain deferred pending explicit approval.
- Added `DEVELOPMENT_SESSION_GUIDE.md` with phased session prompts, scope, non-scope, completion criteria, and verification handoff.

### 2026-06-10 - Overview Market Context UX V3 1차~4차
- Opened `.aiworkspace/note/finance/tasks/active/overview-market-context-ux-v3-20260610/` for `Overview > Market Context` first-screen UX polish.
- Reworked the first tab to show market context summary, data-state separation, next check order, core/supporting card hierarchy, and secondary refresh placement.
- Kept the boundary read-only / DB-backed: no provider fetch, schema change, registry / saved JSONL write, validation / monitoring / trading semantics.
- Browser QA confirmed root `/` renders the new cockpit; direct `/overview` still shows Streamlit's Page not found modal and is recorded in task risks.

### 2026-06-10 - Risk Parity / Dual Momentum 5B
- Opened and completed `.aiworkspace/note/finance/tasks/active/risk-parity-dual-momentum-5b-20260610/` for Backtest 5B.
- Improved Risk Parity Trend row/meta contracts for volatility window, eligible universe, inverse-vol weights, cash-only reasons, guardrail cash-only state, and low-vol overweight interpretation.
- Improved Dual Momentum row/meta contracts for top-N selection, trend rejection, cash proxy retention, concentration, and selection-change / whipsaw interpretation.
- Reused existing Selection History; no new Backtest Analysis panel, registry / saved JSONL / run history write, provider fetch, Practical Validation, Final Review, or Monitoring behavior change.

### 2026-06-09 - Global Relative Strength 5A
- Opened and completed `.aiworkspace/note/finance/tasks/active/global-relative-strength-5a-20260609/` for Backtest 5A.
- Improved GRS runtime / strategy / result bundle contracts: strategy owns rebalance cadence, score windows / weights are preserved, cash proxy and benchmark contract metadata are retained, and risky ETF gaps can flow to exclusion metadata.
- Added GRS cash / top-N concentration row diagnostics and connected them to the existing Selection History surface without adding a new evidence / log / workbench panel.
- Registry / saved JSONL / run history / generated artifacts were kept out of scope.

### 2026-06-09 - Backtest Analysis Direction Reset 4C
- Opened and completed `.aiworkspace/note/finance/tasks/active/backtest-analysis-direction-reset-20260609/` for Backtest 4차 4C.
- Reordered Backtest Analysis so strategy execution / comparison / candidate creation appears before Reference / evidence / governance panels.
- Added a Streamlit-free research board placement model and hid Reference help plus 3A~4B evidence / governance / ETF workbench panels behind `전략 개발 참고`.
- Strategy runtime, DB schema, registry / saved JSONL, run history, generated artifacts, provider fetch, Practical Validation, Final Review, and Monitoring behavior were not changed.

### 2026-06-08 - Backtest ETF Rerun Matrix Workbench 4B
- Opened and completed `.aiworkspace/note/finance/tasks/active/etf-rerun-matrix-workbench-20260608/` for Backtest 4차 4B.
- Added a Streamlit-free ETF rerun matrix service and Backtest Analysis workbench panel for GRS / Risk Parity / Dual Momentum.
- The matrix shows 9 session-only scenarios and runs only the selected ETF strategy into session state; it does not write run history, registries, saved setups, validation results, final decisions, monitoring logs, or provider snapshots.
- Verification and Browser QA screenshot are in the task `RUNS.md` / `STATUS.md`.

### 2026-06-08 - Backtest ETF Current Anchor Workbench 4A
- Opened and completed `.aiworkspace/note/finance/tasks/active/etf-current-anchor-workbench-20260608/` for Backtest 4차 4A.
- Added a Streamlit-free ETF current-anchor read model and Backtest Analysis workbench panel for GRS / Risk Parity / Dual Momentum.
- The workbench reads existing run history and Practical Validation source handoff rows to show latest run evidence, source evidence, missing evidence, and next action without reruns or registry writes.
- Verification, Browser QA screenshot, and remaining 4B handoff are in the task `RUNS.md` / `STATUS.md`.

### 2026-06-08 - Backtest ETF Evidence Expansion 3D
- Opened and completed `.aiworkspace/note/finance/tasks/active/etf-evidence-expansion-20260608/` for Backtest 3차 3D.
- Added a Streamlit-free ETF evidence expansion read model and Backtest Analysis read-only panel for GRS / Risk Parity / Dual Momentum.
- The panel shows current anchor, near miss, not-ready reason, required evidence, and next workflow without current candidate promotion or durable write side effects.
- Actual rerun matrix, strategy hub / report, and current candidate promotion remain separate approval scopes.

### 2026-06-08 - Backtest Risk-On Momentum Governance 3C
- Opened and completed `.aiworkspace/note/finance/tasks/active/risk-on-momentum-governance-20260608/` for Backtest 3차 3C.
- Added a Streamlit-free governance readiness read model and Backtest Analysis read-only panel for Risk-On Momentum 5D.
- Practical Validation module execution, Final Review route, Portfolio Monitoring daily signal policy, and downstream promotion remain deferred approval scopes.

### 2026-06-08 - Backtest Strict Annual / ETF Bridge 3B
- Opened and completed `.aiworkspace/note/finance/tasks/active/strict-annual-etf-bridge-20260608/` for Backtest 3차 3B.
- Added a Streamlit-free strict annual + GTAA / Equal Weight bridge read model and Backtest Analysis bridge panel.
- The bridge shows role, target use, Practical Validation evidence, recommended workflow, deferred exclusions, and storage / route boundaries without writing registry / saved / run history / validation / final decision rows.
- Verification, Browser QA screenshot, and remaining 3C / 3D handoff are in the task `RUNS.md` / `STATUS.md`.

### 2026-06-08 - Backtest Strategy Evidence Inventory 3A
- Opened and completed `.aiworkspace/note/finance/tasks/active/strategy-evidence-inventory-direction-panel-20260608/` for Backtest 3차 3A.
- Added Streamlit-free strategy catalog / evidence inventory read models and a read-only Backtest Analysis Direction Panel for all catalog strategies.
- Risk-On Momentum 5D remains governance deferred; strict quarterly variants remain prototype / contract-smoke; strict annual 3종 + GTAA / Equal Weight are the first evidence-mature group.
- Verification, boundary check, Browser QA screenshot, and remaining 3B / 3C / 3D handoff are in the task `RUNS.md` / `STATUS.md`.

### 2026-06-08 - Backtest Strategy Direction 2차 Research
- Opened `.aiworkspace/note/finance/researches/active/2026-06-backtest-strategy-direction/` as the 2차 analysis / direction bundle for Backtest strategy work.
- Documented strategy inventory, weakness matrix, internal benchmark baseline, feature candidates, recommendation, risks, and next-session handoff.
- Recommended 3차 work start with read-only Strategy Evidence Inventory / Direction Panel, then strict annual + GTAA / Equal Weight bridge.
- Deferred implementation, registry / saved JSONL writes, roadmap commitment, Risk-On Momentum governance, quarterly maturation, and live trading boundaries to approved future scopes.

### 2026-06-08 - Merge Review Fixes
- Opened `.aiworkspace/note/finance/tasks/active/merge-review-fixes-20260608/` after sub-dev / main-dev master merge review.
- Fixed Reference contextual help internal links to use configured Streamlit page targets instead of direct markdown `/guides` / `/glossary` links.
- Marked Reference Contextual Links V4 plan as completed and tightened the Reference Guides catalog required-key test assertion.
- Verification and Browser QA confirm Backtest / Operations Reference help and normal Reference navigation.

### 2026-06-08 - Operations V2 Closeout 5차
- Opened `.aiworkspace/note/finance/tasks/active/operations-v2-closeout-20260608/` for Operations Overview V2 5차 closeout.
- Confirmed normal browser QA path is root `/` -> top navigation -> `Operations Overview`; this path reaches `/operations` without the Page not found dialog.
- Added `docs/runbooks/OPERATIONS_OVERVIEW_QA.md` for Operations Overview QA, direct-route diagnostic, focused tests, and artifact hygiene.
- Operations V2 is closed as 1차 archive cleanup, 2차 portfolio summary, 3차 Evidence Health, 4차 review queue, 5차 QA/docs closeout. Archive helper deletion remains a separate audit / migration decision.

### 2026-06-08 - Operations Review Queue Refinement 4차
- Opened `.aiworkspace/note/finance/tasks/active/operations-review-queue-refinement-20260608/` for Operations Overview V2 4차.
- Refined Today's Operations Queue into a priority / evidence / metric ordered review queue.
- Queue ordering now separates setup blockers, system run failure, scenario freshness, open review, routine monitoring, and no-selected-row guidance.
- Boundary remains read-only: no provider DB detail fetch, registry / saved JSONL rewrite, scenario execution change, archive helper deletion, broker order, account sync, or auto rebalance.

### 2026-06-07 - Operations Evidence Health Strip 3차
- Opened `.aiworkspace/note/finance/tasks/active/operations-evidence-health-strip-20260607/` for Operations Overview V2 3차.
- Added an Evidence Health mini strip between Portfolio Monitoring Status and Today's Operations Queue.
- The strip summarizes scenario freshness, selected evidence readiness, open review, and system run health from already-loaded selected dashboard / portfolio setup / run history payloads.
- Boundary remains read-only: no provider DB detail fetch, registry / saved JSONL rewrite, scenario execution change, archive data deletion, broker order, account sync, or auto rebalance.

### 2026-06-07 - Operations Portfolio First Summary 2차
- Opened `.aiworkspace/note/finance/tasks/active/operations-portfolio-first-summary-20260607/` for Operations Overview V2 2차.
- Added a Portfolio Monitoring Status summary before the daily queue in `Operations > Operations Overview`.
- Summary reads selected dashboard / monitoring portfolio setup for active portfolio, assigned strategy, stale / pending scenario metadata, blockers, missing references, open review, target snapshot, and next review.
- Boundary remains read-only: no registry / saved JSONL rewrite, Portfolio Monitoring scenario execution change, archive data deletion, broker order, account sync, or auto rebalance.

### 2026-06-07 - Operations Cockpit Cleanup 1차
- Opened `.aiworkspace/note/finance/tasks/active/operations-cockpit-cleanup-20260607/` for Operations Overview V2 1차 cleanup.
- Removed user-facing archive / development-history artifacts from `Operations > Operations Overview`; Portfolio Monitoring and System / Data Health remain the only primary Operations lanes.
- Updated docs and tests around the new `operations_overview_v2` read model.
- Next Operations V2 steps remain portfolio-first status summary, evidence health mini strip, and review queue refinement.

### 2026-06-07 - Refactor Round Closeout 10차
- Opened `.aiworkspace/note/finance/tasks/active/refactor-round-closeout-20260607/` as the 10차 structure / refactor baseline closeout record.
- Audited 5차~9차 outputs, large-file residuals, `.note/finance` path risk, and UI / engine boundary posture.
- Closed the current refactor round as a usable baseline; remaining splits are explicit follow-up candidates, not active work.
- Next candidates are Backtest Compare form / replay / weighted-result splits, a future large-surface refactor round, or physical task / phase archive migration.

### 2026-06-07 - Backtest Compare Components Split 9차
- Opened `.aiworkspace/note/finance/tasks/active/backtest-compare-components-split-20260607/` as the 9차 Backtest Compare Streamlit split first-pass record.
- Added `app/web/backtest_compare_components.py` for Portfolio Mix Builder CSS, flow stepper, section heading, and component result card render.
- `app/web/backtest_compare.py` remains the Compare orchestration owner for strategy execution, saved replay, weighted bundle creation, registry handoff, and Practical Validation handoff.
- Remaining follow-up candidates are saved replay / weighted result / strategy-specific form body splits.

### 2026-06-07 - Ingestion Diagnostic Facade 7B
- Opened `.aiworkspace/note/finance/tasks/active/ingestion-diagnostic-facade-20260607/` as the 7차 large Streamlit split 7B record.
- Added `app/services/ingestion_diagnostics.py` as the Streamlit-free facade for price window preflight, Price Stale Diagnosis, Statement Coverage Diagnosis, and Statement PIT Inspection.
- `app/web/ingestion_console.py` now renders diagnostic panels and stores session-state results without directly importing diagnostic jobs, financial statement source inspection, or loader modules.
- 7차 is now closed as 7A Ingestion Console split plus 7B diagnostic facade; next structure candidate remains Backtest Compare Streamlit split.

### 2026-06-07 - Runtime Backtest Strict Family split 8차
- Opened `.aiworkspace/note/finance/tasks/active/runtime-backtest-strict-family-split-20260607/` as the 8차 runtime large-file split 8C record.
- Moved strict quality / value / quality-value annual and quarterly runtime wrapper implementation from `app/runtime/backtest.py` into `app/runtime/backtest_strict.py`.
- Kept `app.runtime.backtest` strict runners and helper functions as public compatibility imports used by UI / services / replay tests.
- At the time of this 8C split, 7B Ingestion diagnostic facade was still a follow-up; it was completed later in `ingestion-diagnostic-facade-20260607`.

### 2026-06-07 - Runtime Backtest Real-Money split 8차
- Opened `.aiworkspace/note/finance/tasks/active/runtime-backtest-real-money-split-20260607/` as the 8차 runtime large-file split 8B record.
- Moved real-money / guardrail / benchmark / deployment readiness helper implementation from `app/runtime/backtest.py` into `app/runtime/backtest_real_money.py`.
- Kept `app.runtime.backtest` constants and helper functions as public compatibility imports used by UI / services / replay tests.
- Follow-up remains strict quality / value family runtime wrapper split.

### 2026-06-07 - Runtime Backtest Risk-On Momentum split 8차
- Opened `.aiworkspace/note/finance/tasks/active/runtime-backtest-risk-on-momentum-split-20260607/` as the 8차 runtime large-file split record.
- Moved Risk-On Momentum 5D DB runtime orchestration from `app/runtime/backtest.py` into `app/runtime/backtest_risk_on_momentum.py`.
- Kept `app.runtime.backtest.run_risk_on_momentum_5d_backtest_from_db` as the public compatibility import used by UI / services.
- Follow-up remains real-money / guardrail contract split and strict quality / value family split.

### 2026-06-07 - Streamlit Ingestion Console split 7차
- Opened `.aiworkspace/note/finance/tasks/active/streamlit-ingestion-console-split-20260607/` as the 7차 large Streamlit file split record.
- Moved `Workspace > Ingestion` render / session state / job scheduling / diagnostics UI from `app/web/streamlit_app.py` into `app/web/ingestion_console.py`.
- `app/web/streamlit_app.py` is now the Finance Console shell for runtime marker, navigation, page wrappers, and glossary.
- Follow-up remains Ingestion diagnostic facade extraction and then the next large Streamlit surface split.

### 2026-06-07 - Overview / Ingestion action boundary 6차
- Opened `.aiworkspace/note/finance/tasks/active/overview-ingestion-action-boundary-20260607/` as the 6차 collection / read boundary task.
- Added `app/jobs/overview_actions.py` as the bounded Overview refresh facade and routed Overview market snapshot, futures, events, sentiment, quote-gap diagnostics, browser auto refresh, and run-history append through it.
- `app/web/overview_dashboard.py` no longer imports `app.jobs.ingestion_jobs`, `app.jobs.overview_automation`, or `app.jobs.run_history` directly.
- Durable docs now define Ingestion as the primary collector console and Overview as a context surface with approved bounded refresh through the action facade.

### 2026-06-07 - Code boundary / refactor baseline audit 5차
- Opened `.aiworkspace/note/finance/tasks/active/code-boundary-refactor-audit-20260607/` as the 5차 structure audit record.
- Verified UI / engine boundary checker PASS, Streamlit imports remain under `app/web`, production `app.services` / `app.runtime -> app.web` reverse import was not found, and local Streamlit health returned `ok`.
- Identified next refactor baseline: Overview / Ingestion action boundary first, then Ingestion Console split, Backtest Compare split, runtime facade split, legacy compatibility catalog, and verification hardening.
- No code behavior, registry / saved JSONL, DB schema, ingestion collector, runtime execution, push, or PR was changed.

### 2026-06-07 - Post-merge verification / handoff 4차
- Opened `.aiworkspace/note/finance/tasks/active/post-merge-verification-handoff-20260607/` as the 4차 verification and handoff record.
- Verified docs-only hygiene, active state pointers, manifest presence, stale pointer absence, and latest cleanup commits.
- Added `HANDOFF.md` with next read order, current product interpretation, remaining decisions, and default do-not-stage boundaries.
- No code, registry / saved JSONL rewrite, `.note/` cleanup, UI QA, DB / ingestion / backtest run, push, or PR was included.

### 2026-06-07 - Post-merge active state cleanup 3차
- Opened `.aiworkspace/note/finance/tasks/active/post-merge-active-state-cleanup-20260607/` as the 3차 cleanup record.
- Reviewed retained state: `tasks/active` has 170 task folders and `phases/active` has 11 phase board folders.
- Added task / phase `STATUS_MANIFEST.md` files and aligned README / roadmap / index pointers so current active task and phase read as none.
- No folder mass-move, registry / saved JSONL rewrite, `.note/` cleanup, or code behavior change was included.

### 2026-06-07 - Post-merge boundary docs alignment 2차
- Opened `.aiworkspace/note/finance/tasks/active/post-merge-boundary-docs-alignment-20260607/` as the current 2차 docs task.
- Added `docs/architecture/SYSTEM_BOUNDARIES.md` as the layer / product-surface / storage boundary checkpoint.
- Aligned architecture / data / flow maps around `finance/data -> DB -> loaders -> runtime/services -> app/web`, context-only evidence, and Operations > Portfolio Monitoring storage boundaries.
- No code, registry / saved JSONL rewrite, `.note/` cleanup, or active task / phase folder migration was included.

### 2026-06-07 - Post-merge docs alignment 1차
- Opened `.aiworkspace/note/finance/tasks/active/post-merge-docs-alignment-20260607/` after reviewing the master merge state.
- Reframed durable docs around the current product flow: Ingestion / Overview context -> Backtest Analysis -> Practical Validation -> Final Review -> Operations Console -> Portfolio Monitoring.
- `ROADMAP.md` now separates current state, recently merged work, completed foundations, retained active-folder records, and next decisions.
- No code, registry / saved JSONL, `.note/` cleanup, or active task / phase folder migration was included in this 1차 pass.

### 2026-06-07 - Overview Market Sentiment V1 3차
- Implemented 3차 in `.aiworkspace/note/finance/tasks/active/overview-market-sentiment-v1/`.
- CNN Fear & Greed / AAII market sentiment context overlay now appears in `Backtest > Final Review` and `Operations > Portfolio Monitoring` as a read-only market backdrop, sharing the same DB-backed read model used by Practical Validation.
- Boundary remains context-only: no selected-route gate change, monitoring signal, registry rewrite, saved setup mutation, live approval, broker order, account sync, or auto rebalance.
- Verification closeout details are in the task `RUNS.md`.

### 2026-06-07 - Market Movers Why It Moved Google News KR RSS
- Updated `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/` so `Why It Moved > 한국어 뉴스` uses keyless Google News KR RSS metadata/snippet instead of Naver credentialed API lookup.
- The lane remains button-triggered, selected-ticker-only, session-only, and limited to `제목 / 출처 / 게시 시각 / 단서 / 열기`; SEC filings remain table-only.
- No article body, AI summary, sentiment, catalyst classifier, DB schema, registry JSONL, or saved JSONL write path was added.
- Verification and Browser QA evidence are in task `RUNS.md`; screenshot `why-it-moved-google-news-kr-rss-qa-20260607.png` remains generated/untracked.

### 2026-06-06 - Market Movers Why It Moved Korean News Metadata
- Added a `한국어 뉴스` lane to `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/` while keeping SEC filings table-only after the rollback.
- `간단 메타데이터 조회` now includes Naver News Search API metadata/snippet when credentials are configured; missing credentials show setup guidance and do not fail the whole lookup.
- Boundaries remain manual/session-only: no article body, AI summary, sentiment, catalyst classifier, DB schema, registry JSONL, or saved JSONL write path was added.
- Verification and Browser QA evidence are in the task `RUNS.md`; screenshot `why-it-moved-korean-news-metadata-qa-fresh-20260606.png` remains generated/untracked.

### 2026-06-04 - Market Movers Why It Moved V1.6 UX Pass
- Implemented `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/` V1.6 investigation board.
- `Overview > Market Movers > Why It Moved` now shows movement summary header, metadata status strip, button-only compact metadata fetch, and `Investigation Leads` sections for News / SEC / collapsed External Searches.
- Boundary remains manual and session-only: no automatic catalyst judgement, AI summary, article / filing body collection, DB schema, registry JSONL, or saved setup write was added.
- Verification evidence is in task `RUNS.md`; Browser QA screenshot is `why-it-moved-v16-browser-qa-20260604.png` and remains generated/untracked.

### 2026-06-04 - Market Movers Why It Moved Review Follow-up
- Stabilized `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/` after UX/code review.
- Compact metadata now distinguishes provider partial failure with `PARTIAL` instead of green `OK`.
- The six outbound research buttons were removed; external searches now live in a collapsed clickable-link table with Korean Google / Naver rows preserved.
- Why It Moved is still treated as a prototype-level manual investigation panel; next UX pass should improve information hierarchy before adding classifier, persistence, or provider expansion.

### 2026-06-03 - Market Movers Why It Moved V1.5
- Expanded `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/` from Catalyst Links into `Overview > Market Movers > Why It Moved`.
- The panel shows selected Return / Volume rank ticker identity, movement context, outbound research links, and button-triggered compact news / SEC metadata in session state only.
- Boundary remains manual investigation: no automatic catalyst judgement, AI summary, article / filing body collection, DB schema, registry JSONL, saved setup, broker/account, order, live approval, or auto rebalance path was added.
- Verification evidence and residual risks are in the task `RUNS.md` / `RISKS.md`; Browser QA screenshot is `why-it-moved-panel-focused-qa-20260603.png` and remains generated/untracked.

### 2026-06-03 - Market Movers Catalyst Links V1
- Added Catalyst Links to `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/`.
- `Overview > Market Movers` now lets users pick Return Rank / Volume Rank tickers and open Yahoo Finance, Google News, SEC company search, and IR / earnings search start points.
- Link queries include period / coverage / rank / symbol / name context; no AI summary, article body collection, web crawling, provider fetch, DB schema, registry, saved setup, broker/account, order, live approval, or auto rebalance path was added.
- Verification evidence and residual risks are in the task `RUNS.md` / `RISKS.md`; Browser QA screenshot is `market-movers-catalyst-links-qa-20260603.png` and remains generated/untracked.

### 2026-06-03 - Futures Monitor Live Charts Missing Fix
- Fixed `.aiworkspace/note/finance/tasks/active/futures-market-monitoring-mvp-v1/` follow-up for `Overview > Futures Monitor`.
- Root cause was yfinance returning empty `1d / 1m` data for active futures symbols while `2d / 1m` returned usable candles.
- Collector now retries empty 1d / 1m symbols once with 2d / 1m, records `fallback_retries`, and keeps stale / missing warnings visible.
- Refreshed current Pre-open Core data and restarted 8501; Browser QA confirmed Live Futures Charts at `6/6 symbols` with Provider Run `success`.

### 2026-06-05 - Overview Market Sentiment V1
- Completed `.aiworkspace/note/finance/tasks/active/overview-market-sentiment-v1/` 1차 scope.
- CNN Fear & Greed and AAII Sentiment Survey now collect into `finance_meta.macro_series_observation`; actual smoke wrote 348 rows: CNN 260, AAII 88.
- `Workspace > Overview` now has a Sentiment tab after Futures Monitor, plus Ingestion manual refresh and Data Health Market Sentiment target.
- User-review follow-up improved Sentiment from raw prototype cards into a guided context workflow: mixed-neutral headline, data confidence, 6-step analysis check, CNN driver split, AAII pessimism context, and next checks.
- Follow-up learning polish now keeps the 6 analysis items visible as `지금 결론 / 왜 이렇게 보나 / 강한 신호 / 약한 신호 / 그래서 어떻게 보나 / 다음 확인`, and adds CNN component learning notes for all 7 components.
- Verification passed: focused service contracts, py_compile/chart smoke, actual collector smoke, Browser QA on `http://127.0.0.1:8502`, and screenshot `overview-market-sentiment-v1-qa.png`.
- Remaining roadmap: 2차 Practical Validation context overlay, 3차 scheduled ops hardening if needed.

### 2026-06-02 - Selected Dashboard Monitoring First UX V1
- Completed `.aiworkspace/note/finance/tasks/active/selected-dashboard-monitoring-first-ux-v1/`.
- `Operations > Selected Portfolio Dashboard` now opens with Active Portfolio Monitoring Scenario above the portfolio shelf, with distinct no portfolio / no strategy / configured-not-run / executed states.
- Portfolio card selection, portfolio name / description edit, strategy board, and `포트폴리오 시나리오 업데이트` moved below the hero; lower readiness / provider / freshness / open issue evidence remains lazy detail for one selected strategy.
- Verification passed so far: py_compile, focused Selected Portfolio service contracts, and `git diff --check`; Browser QA is the remaining closeout check.
- No Final Review row mutation, saved setup cleanup, DB schema, broker/account, order, live approval, monitoring auto-write, or auto rebalance path was added.

### 2026-06-02 - Futures Macro Thermometer Historical Validation V1
- Completed implementation task `.aiworkspace/note/finance/tasks/active/futures-macro-thermometer-validation-v1/`.
- Macro Thermometer now attaches point-in-time historical validation, Interpretation Confidence, current scenario sample / hit-rate evidence, score threshold sensitivity, score-forward-return relationships, and separated strong / weak / conflicting evidence.
- 5y / 1d core futures backfill smoke succeeded for 16/16 symbols with 20,138 rows; validation smoke produced 1,198 PIT dates with futures targets only.
- Boundary remains read-only market context: no prediction guarantee, registry/saved write, live approval, order, alert, broker/account sync, or auto rebalance.

### 2026-06-02 - Selected Dashboard Manual Scenario Run V1
- Completed `.aiworkspace/note/finance/tasks/active/selected-dashboard-manual-scenario-run-v1/`.
- Strategy add / slot edit now changes saved setup only; current scenario results are keyed by portfolio / slot / selected decision and start / end / balance signature so stale results are not counted as fresh.
- `포트폴리오 시나리오 업데이트` runs pending / stale strategies by default and `전체 재실행` forces a full refresh; individual strategy evidence is opened for one selected strategy instead of eager-rendered tabs.
- Verification passed: py_compile, focused Selected Portfolio contracts, `git diff --check`, Browser text QA, and screenshot `selected-dashboard-manual-scenario-run-v1-qa.png`.
- Full scenario replay can still be slow because selected strategy contracts are replayed sequentially; no async worker, DB schema, broker/account, order, live approval, monitoring auto-write, or auto rebalance path was added.

### 2026-06-01 - Selected Dashboard Product Polish V1
- Completed `.aiworkspace/note/finance/tasks/active/selected-dashboard-product-polish-v1/`.
- Sections 1~3 now render as fixed-height portfolio shelf -> selected portfolio command band -> compact strategy board -> portfolio-wide scenario cockpit.
- Delete controls moved into collapsed `포트폴리오 관리`; detailed strategy / performance tables moved into expanders.
- Browser QA screenshot `selected-dashboard-product-polish-v1-qa.png`, py_compile, focused Selected Portfolio contracts, and `git diff --check` passed.
- Section 4 Monitoring Signals / evidence was intentionally left unchanged; no DB schema, Final Review row, broker/account, order, live approval, monitoring auto-write, or auto rebalance path was added.

### 2026-06-01 - Selected Dashboard Portfolio Flow Redesign V1
- Completed `.aiworkspace/note/finance/tasks/active/selected-dashboard-portfolio-flow-redesign-v1/`.
- At that task closeout, `Operations > Selected Portfolio Dashboard` changed to `1. 나의 포트폴리오` -> `2. 포트폴리오 상세 / 전략 구성` -> `3. 모니터 시나리오`, with Final Review handoff / readiness / provider / audit evidence moved below the scenario workflow. Later Monitoring First UX V1 moved the scenario hero above setup.
- Dashboard saved state now supports backward-compatible strategy slots with selected decision / start / latest-end mode / balance / memo while preserving legacy `selected_decision_ids`.
- Verification passed: py_compile, full `tests.test_service_contracts` 222 tests, `git diff --check`, and Browser QA screenshot `selected-dashboard-portfolio-flow-redesign-v1-qa.png`.
- No Final Review decision rows, DB schema, provider fetch, broker/account sync, live approval, order, monitoring auto-write, or auto rebalance path was added.

### 2026-06-01 - Removed stale Phase 14 active pointers
- Removed the stale active Phase 14 pointer from durable index / roadmap / root handoff logs.
- Deleted the abandoned `phase14-second-cycle-prioritization` active phase docs and `phase14-board-open` active task docs from the current workspace map.
- Phase 13 carry-forward material remains source material only; no second-cycle phase is currently active.
- No code, DB schema, registry JSONL, saved setup, broker/account, order, live approval, or auto rebalance path was touched.

### 2026-06-01 - Final Decision Registry Naming Cleanup
- Renamed the current selected decision registry from `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` to `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`.
- Archived legacy collision is now named `FINAL_PORTFOLIO_SELECTION_DECISIONS_V1.jsonl`; active JSONL remains 4 GRS selected rows plus the existing Selected Dashboard and saved setup files.
- Runtime consumers, Selected Dashboard source contracts, reference guide copy, and durable storage / flow docs now point to the canonical current file name.
- Verification kept selected rows `4`, dashboard rows `4`, assigned references `4`, missing references `0`; no DB, broker/account, order, live approval, or auto rebalance path was touched.

### 2026-06-01
- Completed dry-run candidate sweep in `.aiworkspace/note/finance/tasks/active/final-review-pass-candidate-search-20260601/`.
- Found two fresh Final Review selected-route pass candidates without registry/saved persistence: `GRS Liquid Macro Top2` and `GTAA Default Top3`.
- Best current candidate is `GRS Liquid Macro Top2` at CAGR `13.31%`, MDD `-17.75%`, Sharpe `1.12`, Practical Validation replay PASS, selected-route preflight ready, and Final Review selected gate Ready.
- Lower-MDD follow-up found `GRS Macro Top1 MA200` at CAGR `18.03%`, MDD `-12.43%`, Sharpe `1.18`, selected-route ready; lower-drawdown top=2 alternative is `GRS QQQ Gold Bonds Top2 MA150` at CAGR `12.94%`, MDD `-8.81%`, Sharpe `1.31`.
- Completed `.aiworkspace/note/finance/tasks/active/etf-dynamic-promotion-policy-contract-v1/`.
- ETF dynamic strategies now carry strict-compatible promotion policy thresholds from Backtest Analysis source contract through execution dispatch, compare overrides, Practical Validation replay, and candidate source snapshots.
- Fresh `GRS Liquid Macro Top2` verification passed: source has `promotion_min_net_cagr_spread=-0.02`, Practical Validation replay PASS, selected-route preflight `select_ready`, and Final Review selected gate Ready.
- Final Review gate policy was not relaxed; proof-deficient Equal Weight-style missing net-cost / turnover evidence remains blocked by selected-route preflight.
- Completed `.aiworkspace/note/finance/tasks/active/selected-dashboard-monitoring-portfolio-v1/`.
- `Operations > Selected Portfolio Dashboard` now starts with `1. 나의 포트폴리오`, stores dashboard setup in `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`, and lets users add Final Review selected candidates one by one without same-portfolio duplicates.
- Monitoring Scenario now uses virtual start / end / capital, with latest DB market date as the default end, and Monitoring Signals / Open Issues / optional Preflight / same-portfolio transition comparison are organized after scenario execution.
- Verification passed: compile/import checks, focused Selected Portfolio service contracts, full `tests.test_service_contracts` 217 tests, `git diff --check`, and Browser QA screenshot `selected-dashboard-monitoring-portfolio-v1-qa.png`.
- Completed `.aiworkspace/note/finance/tasks/active/selected-dashboard-live-readiness-followup-v1/`.
- `Operations > Selected Portfolio Dashboard` now shows Open Issues / Follow-up and Deployment Readiness tabs sourced from selected Final Decision V2 snapshots and existing read-only dashboard evidence.
- Deployment Readiness remains preflight-only: no live approval, order, broker/account connection, monitoring auto-write, or auto rebalance behavior was added.
- Candidate recheck found 2 Practical Validation rows, 1 Final Review eligible GTAA row, and 0 selected-route pass; non-GTAA candidates exist only in legacy current/proposal registries, so no fresh selected row was appended.
- Completed `.aiworkspace/note/finance/tasks/active/final-review-selection-readiness-gate-v1/`.
- Final Review now uses `selection_gate_policy_snapshot` for `SELECT_FOR_PRACTICAL_PORTFOLIO` save readiness and preserves the older stricter audit as `deployment_readiness_policy_snapshot`.
- Default `REVIEW` findings become `open_review_items`; hard blockers / critical missing evidence still block selected-route save.
- Weighted mix Practical Validation source conversion now preserves component `weight_reason`, role source, and compact cost / turnover / net-cost evidence snapshots.
- Verification passed: `py_compile`, targeted Practical Validation / Final Review service contracts, and full `tests.test_service_contracts` 211 tests.

### 2026-05-31
- Session closeout docs aligned for master merge handoff at the time: `docs/INDEX.md`, `docs/ROADMAP.md`, `docs/PROJECT_MAP.md`, and task logs then described the former selected-route-only Final Review save policy and the current candidate search outcome. This storage rule was superseded by the 2026-07-09 Final Review Level3 storage boundary work.
- Opened `.aiworkspace/note/finance/tasks/active/non-gtaa-final-selection-candidate-search-20260531/`.
- Non-GTAA dry-runs found several Practical Validation / Final Review evidence-ready candidates, but no fresh candidate passed the current selected-route gate for V2 `SELECT_FOR_PRACTICAL_PORTFOLIO` save.
- Existing legacy V1 Final Review registry contains one non-GTAA Quality selected row; a read-only handoff dry-run maps it to one dashboard row, but the current V2 dashboard source remains empty until an explicit migration seed is approved.
- Adjusted Final Review official save policy after user feedback: new durable Final Decision V2 rows are created only for `SELECT_FOR_PRACTICAL_PORTFOLIO` when selected-route gate passes.
- Hold / reject / re-review now remain status guidance and compatibility read paths, not new official save actions; Selected Dashboard continues to read selected rows only.
- Completed `.aiworkspace/note/finance/tasks/active/final-review-commercial-ux-v1/`.
- Final Review now opens as a user-facing Decision Desk: command center, flow rail, Candidate Board lane cards, visual Decision Cockpit, Final Decision Action, Evidence Appendix, and Decision History / Dashboard Handoff.
- No validation scoring, selected-route gate criteria, DB schema, provider fetch, live approval, order, account sync, or auto rebalance behavior was changed; the later selection-only follow-up narrowed which Final Decision V2 routes can be newly written.
- Completed `.aiworkspace/note/finance/tasks/active/final-review-selected-dashboard-handoff-v1/`.
- Final Review Saved Decision Review and `Operations > Selected Portfolio Dashboard` now share a read-only handoff review for selected rows, dashboard row build, monitorable / blocked counts, checklist, and destination.
- No new registry, monitoring log auto-write, report auto-write, live approval, order, account sync, or auto rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/final-review-saved-decision-review-v1/`.
- Final Review saved final decisions now render as a read-only review ledger with summary counts, route filter, focused detail tabs, operator decision view, Decision Dossier reuse, packet tab, and raw JSON tab.
- No validation rerun, new registry, report auto-write, live approval, order, account sync, or auto rebalance behavior was added; next natural slice is Selected Dashboard handoff polish.
- Completed `.aiworkspace/note/finance/tasks/active/final-review-decision-record-v1/`.
- Final Review final decision input now shows a Decision Record Checklist, selected-route guide badges, route-specific record templates, and explicit live approval / order disabled boundary.
- Initial Decision Record V1 displayed gate-suggested non-select routes for blocked candidates; the later selection-only save follow-up kept those routes as status / compatibility guidance instead of new official save actions.
- Completed `.aiworkspace/note/finance/tasks/active/final-review-candidate-board-v1/`.
- Final Review Candidate Board now ranks Gate-passed candidates by review usefulness and shows select-ready / hold / blocked counts, first-review candidate, review queue, primary reason, and next action.
- This is read-only display priority only; no validation scoring, source eligibility, provider fetch, JSONL schema, live approval, order, account sync, or auto rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/final-review-evidence-appendix-v1/`.
- Final Review now reads as Candidate Board -> Decision Cockpit -> Final Decision Record -> Evidence Appendix, so detailed Practical Validation / Robustness / Paper Observation / Investability Packet evidence is a read-only appendix rather than the main action.
- No validation scoring, selected-route policy, DB schema, provider fetch, JSONL registry schema, live approval, order, account sync, or auto rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/final-review-decision-cockpit-v1/`.
- Final Review now shows Gate-passed Practical Validation candidates in a Candidate Board and surfaces selected-route state, suggested decision, Must Fix / Must Review rows, and monitoring seed in a Decision Cockpit before the final decision record.
- No DB schema, provider fetch, new registry, monitoring log auto-write, waiver persistence, live approval, order, account sync, or auto rebalance behavior was added.
- Fixed Practical Validation Save & Move JSONL persistence failure caused by DB `Decimal` scalar values in compact data coverage evidence.
- Clean V2 selection registry append now normalizes DB / pandas scalar payloads before JSONL write; no gate policy or validation scoring change.

### 2026-05-30
- Practical Validation `1. 선택 후보 확인` now shows the saved Backtest Analysis source snapshot as Summary / Equity Curve / Result Table / Components before profile and replay checks.
- This is a read-only display change; it does not rerun backtests, rewrite registries, or change Final Review gate policy.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-commercial-ux-v1/` second visual pass.
- Practical Validation now uses `app/web/backtest_practical_validation_components.py` as a dedicated workbench shell for the top command center, section headers, cards, step rail, gate alert, and Save & Move panel.
- Validation service contracts, module gate policy, provider collection behavior, and registry storage boundaries were not changed.
- Closed Backtest Analysis 1단계 기준 문서: `.aiworkspace/note/finance/docs/flows/BACKTEST_ANALYSIS_STAGE1_CLOSEOUT.md`.
- Current Stage 1 boundary is now explicit: Single Strategy / Portfolio Mix 후보 생성, 1차 readiness, and Practical Validation handoff only.
- Candidate comparison as a separate read-only tool, saved mix inspector polish, weighted mix cost / turnover aggregation, and profile-specific thresholds remain follow-up candidates outside this closeout.
- Completed `.aiworkspace/note/finance/tasks/active/backtest-portfolio-mix-builder-ux-v1/`.
- Portfolio Mix Builder post-run UI now reads as `Component 실행 -> Weight 구성 -> Mix 후보 판단 -> Practical Validation`, with component result cards, 4 tabs, and raw/detail evidence lowered into expanders.
- No backtest calculation, DB schema, JSONL registry, saved setup policy, live approval, order, or auto rebalance behavior was added.
- Verification passed: py_compile, `git diff --check`, full `unittest tests.test_service_contracts` 133 tests, and Browser smoke with default Equal Weight + GTAA run on `http://127.0.0.1:8502/backtest`.
- Completed `.aiworkspace/note/finance/tasks/active/backtest-portfolio-mix-builder-flow-v1/`.
- Backtest Analysis now shows `Portfolio Mix Builder`; legacy `Compare & Portfolio Builder` routes still normalize to the new mode.
- The mix builder now treats component runs as inputs, then gates the weighted mix as one 1차 후보 before Practical Validation handoff; individual strategy handoff is no longer the main action in this flow.
- Verification passed: py_compile, full `tests.test_service_contracts` 133 tests, `git diff --check`, and Browser smoke on `http://127.0.0.1:8502/backtest`.
- Completed `.aiworkspace/note/finance/tasks/active/backtest-practical-validation-handoff-gate-v1/`.
- Backtest `실전성 검증으로 보내기` now requires first-stage Candidate Readiness to have no Promotion / execution source / validation source blocker.
- Disabled handoff now shows concise blocker reasons, and the handoff area is displayed as a status card; no live approval, order, auto rebalance, or new storage model was added.
- Completed `.aiworkspace/note/finance/tasks/active/backtest-real-money-readiness-efficacy-v1/`.
- Backtest Real-Money 1차 readiness now scores Promotion / execution source checks / validation source checks without reusing later-stage probation / monitoring fields.
- Turnover / cost output now shows estimation status, and Backtest split-period wording no longer presents the 1차 check as formal OOS validation.
- Completed `.aiworkspace/note/finance/tasks/active/backtest-real-money-stage-boundary-v1/`.
- Backtest Real-Money now presents `Suggested Route`, `Next Validation Focus`, and `Execution Preview` as first-pass candidate readiness, while later paper observation / monitoring / final execution decisions stay outside Backtest Analysis.
- Verification passed: targeted py_compile, `git diff --check`, targeted legacy label search, and Browser smoke on `http://127.0.0.1:8502/backtest`.
- Completed `.aiworkspace/note/finance/tasks/active/real-money-promotion-route-absorption-v1/`.
- Real-Money now treats the old `Shortlist` value as `Promotion Suggested Route`, not as a separate validation stage.
- No runtime calculation, DB schema, JSONL registry, user memo / preset storage, live approval, order, or auto rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/phase13-integrated-qa-final-closeout/`.
- Phase 13 closeout summary added at `.aiworkspace/note/finance/phases/done/phase13-hardening-cycle-closeout.md`.
- First hardening cycle is complete as an investability evidence workflow; it is not broker-grade trading, live approval, account sync, order, or auto rebalance readiness.
- Next work should open only after the user chooses a second-cycle direction from `phase13-residual-risk-carry-forward-v1/CARRY_FORWARD_MATRIX.md`.
- Completed `.aiworkspace/note/finance/tasks/active/phase13-residual-risk-carry-forward-v1/`.
- Remaining Phase 8~12 / Phase 13 risks are now split into current limitations, second-cycle candidates, explicit first-cycle out-of-scope items, and safe / unsafe final closeout wording.
- Next task is `phase13-integrated-qa-final-closeout`.
- Completed `.aiworkspace/note/finance/tasks/active/phase13-docs-runbook-alignment-v1/`.
- Durable data / flow / glossary docs now point to Final Decision V2 and the Phase 13 storage boundary; added `.aiworkspace/note/finance/docs/runbooks/PHASE_CLOSEOUT_QA.md`.
- This handed off to `phase13-residual-risk-carry-forward-v1`, now complete.
- Completed `.aiworkspace/note/finance/tasks/active/phase13-storage-data-boundary-audit-v1/`.
- DB-backed data / workflow JSONL compact evidence / saved setup / run artifact / Selected Dashboard read-only storage boundaries were audited with no immediate code defect found.
- No registry / saved / run history / run artifact / Playwright output change was created by this task; this handed off to `phase13-docs-runbook-alignment-v1`, now complete.
- Completed `.aiworkspace/note/finance/tasks/active/phase13-gate-validation-qa-matrix-v1/`.
- Practical Validation / Final Review / Selected Dashboard gate severity QA found no immediate code defect; full `tests.test_service_contracts` passed, 126 tests.
- This handed off to `phase13-storage-data-boundary-audit-v1`, now complete.

### 2026-05-29
- Completed `.aiworkspace/note/finance/tasks/active/phase13-cycle-inventory-v1/`.
- Phase 8~12 1차 hardening cycle을 weakness / mitigation / evidence surface / service contract / verification / residual risk inventory로 정리했다.
- No code, DB schema, new JSONL registry, user memo / preset storage, monitoring log auto-write, account integration, order, approval, or auto rebalance behavior was added.
- Next task is `phase13-gate-validation-qa-matrix-v1`.
- Completed `.aiworkspace/note/finance/tasks/active/allocation-drift-evidence-boundary-v1/`.
- Added `selected_allocation_drift_evidence_boundary_v1` and Dashboard boundary display for optional Actual Allocation.
- Actual Allocation remains manual / session-only evidence with no raw input persistence, alert persistence, monitoring log auto-write, account / broker integration, order, or auto rebalance.
- Next task is `decision-dossier-continuity-operations-v1`.
- Completed `.aiworkspace/note/finance/tasks/active/selected-monitoring-source-map-v1/`.
- Source map confirmed Selected Dashboard already has read-only readiness / freshness / provider / timeline / comparison / drift / dossier evidence.
- Main gaps: Current Candidate Registry replay dependency, readiness / freshness policy split, Review Signals / Recheck Comparison threshold duplication, and session-only monitoring evidence clarity.
- Next task is `recheck-readiness-freshness-contract-v1`.
- Opened `.aiworkspace/note/finance/phases/active/phase12-selected-monitoring-recheck-operations/`.
- Phase 12 focuses on selected monitoring / recheck operations after Final Review selection.
- Next task is `selected-monitoring-source-map-v1`; start by mapping current Selected Portfolio Dashboard readiness / freshness / provider / timeline / signal / comparison / drift / continuity sources.
- No new JSONL registry, automatic monitoring log append, user memo, preset, account integration, approval, order, or auto rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/phase11-integrated-qa-closeout/`.
- Phase 11 closeout summary added at `.aiworkspace/note/finance/phases/done/phase11-portfolio-construction-risk-controls.md`.
- Integrated verification passed: Phase 11 service / web compile, full `tests.test_service_contracts` 112 tests, UI / engine boundary checker, finance refinement hygiene, and `git diff --check`.
- Next hardening target is Phase 12 selected monitoring / recheck operations.
- Completed `.aiworkspace/note/finance/tasks/active/construction-risk-gate-policy-v1/`.
- Final Review selected-route gate policy now treats Construction Risk / Risk Contribution / Component Role / Weight audit routes and non-PASS row criteria as blocker or review-required evidence.
- Verification passed: targeted py_compile, `FinalReviewEvidenceReadModelContractTests` 24 tests, and full `tests.test_service_contracts` 112 tests.
- Next task is `phase11-integrated-qa-closeout`.
- Completed `.aiworkspace/note/finance/tasks/active/component-role-weight-discipline-v1/`.
- Added read-only `component_role_weight_audit_v1` for explicit role source coverage, profile-aware max weight, role concentration, profile intent fit, weight rationale coverage, and storage boundary.
- Practical Validation and Final Review now display the Component Role / Weight Audit and preserve it in final decision snapshots / evidence rows; selected-route gate enforcement remains 11-5 scope.
- Verification passed: targeted py_compile, `ComponentRoleWeightAuditContractTests` 4 tests, and full `tests.test_service_contracts` 109 tests.
- Next task is `construction-risk-gate-policy-v1`.
- Completed `.aiworkspace/note/finance/tasks/active/correlation-risk-contribution-contract-v1/`.
- Added read-only `risk_contribution_audit_v1` for component return matrix coverage, pairwise correlation, max risk contribution proxy, drop-one dependency, source strength, and storage boundary.
- Practical Validation and Final Review now display the Risk Contribution Audit and preserve it in final decision snapshots / evidence rows; selected-route gate enforcement remains 11-5 scope.
- Verification passed: targeted py_compile, `RiskContributionAuditContractTests` 4 tests, and full `tests.test_service_contracts` 105 tests.
- Next task is `component-role-weight-discipline-v1`.
- Completed `.aiworkspace/note/finance/tasks/active/concentration-overlap-exposure-contract-v1/`.
- Added read-only `construction_risk_audit_v1` for component weight concentration, provider look-through coverage, top holding, holdings overlap, dominant asset, and unknown exposure.
- Practical Validation and Final Review now display the Construction Risk Audit and preserve it in final decision snapshots; selected-route gate enforcement remains 11-5 scope.
- Verification passed: targeted py_compile, `ConstructionRiskAuditContractTests` 3 tests, and full `tests.test_service_contracts` 101 tests.
- Next task is `correlation-risk-contribution-contract-v1`.
- Completed `.aiworkspace/note/finance/tasks/active/construction-risk-source-map-v1/`.
- Source map confirmed existing Practical Validation diagnostics, provider look-through board, Robustness Lab sensitivity, and Final Review gate can seed Phase 11 without new storage.
- Main gap is ownership / selected-route visibility: construction risk is currently split across provider coverage and stress robustness evidence.
- Next task is `concentration-overlap-exposure-contract-v1`; start by wrapping existing component weight, top holding, top overlap, dominant asset, unknown exposure, and provider coverage evidence into a read-only contract.
- Opened `.aiworkspace/note/finance/phases/active/phase11-portfolio-construction-risk-controls/`.
- Phase 11 focuses on portfolio construction risk controls: concentration, overlap, correlation, risk contribution, component role, and profile-aware weight discipline.
- Next task is `construction-risk-source-map-v1`; start by mapping current Practical Validation / Look-through / Robustness Lab / Final Review gate construction risk sources before implementation.
- No new JSONL registry, user memo, preset, approval, order, or auto rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/phase10-integrated-qa-closeout/`.
- Phase 10 closeout summary added at `.aiworkspace/note/finance/phases/done/phase10-walkforward-oos-regime-validation.md`.
- Integrated verification passed: Phase 10 service / loader compile, full `tests.test_service_contracts` 98 tests, UI / engine boundary checker, finance refinement hygiene, and `git diff --check`.
- Next hardening target is Phase 11 portfolio construction risk controls.
- Completed `.aiworkspace/note/finance/tasks/active/validation-efficacy-gate-policy-refinement-v2/`.
- Final Review selected-route gate policy now surfaces Validation Efficacy row-level walk-forward / OOS / regime gaps as blocker or review-required evidence.
- This is read-only gate evidence refinement; no new JSONL registry, user memo, preset, approval, order, or auto rebalance behavior was added.
- Next task is `phase10-integrated-qa-closeout`.
- Completed `.aiworkspace/note/finance/tasks/active/regime-split-validation-v1/`.
- Added DB-backed FRED macro history regime split evidence and connected `regime_split_validation` to Practical Validation / Validation Efficacy Audit.
- Missing / short / proxy-only regime evidence is not treated as PASS; no new DB schema, JSONL registry, user memo, preset, approval, order, or auto rebalance behavior was added.
- Next task is `validation-efficacy-gate-policy-refinement-v2`.
- Completed `.aiworkspace/note/finance/tasks/active/oos-holdout-validation-contract-v1/`.
- Added benchmark-aligned in-sample / out-sample holdout evidence and connected `oos_holdout_validation` to Practical Validation / Validation Efficacy Audit.
- Missing / short / proxy-only OOS evidence is not treated as PASS; no new JSONL registry, user memo, preset, approval, order, or auto rebalance behavior was added.
- Next task is `regime-split-validation-v1`.
- Completed `.aiworkspace/note/finance/tasks/active/walkforward-split-contract-v1/`.
- Added `app/services/backtest_temporal_validation.py` and connected compact walk-forward evidence to Practical Validation / Validation Efficacy Audit.
- Missing / short / proxy-only walk-forward evidence is not treated as PASS; no new JSONL registry, user memo, preset, approval, order, or auto rebalance behavior was added.
- Next task is `oos-holdout-validation-contract-v1`.
- Completed `.aiworkspace/note/finance/tasks/active/walkforward-oos-source-map-v1/`.
- Source map found reusable Practical Validation curve / benchmark / replay plumbing and existing runtime rolling / OOS metadata.
- Main gap: temporal evidence is not yet an explicit Validation Efficacy / Final Review gate row; next task is `walkforward-split-contract-v1`.
- No new JSONL registry, user memo, preset, approval, order, or auto rebalance behavior was added.
- Opened `.aiworkspace/note/finance/phases/active/phase10-walkforward-oos-regime-validation/`.
- Phase 10 focuses on walk-forward / out-of-sample / regime split validation so good full-period backtests are not over-trusted.
- Next task is `walkforward-oos-source-map-v1`; start by mapping current Practical Validation / Robustness Lab / replay / result metadata sources before implementation.
- No new JSONL registry, user memo, preset, approval, order, or auto rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/phase9-integrated-qa-closeout/`.
- Phase 9 closeout summary added at `.aiworkspace/note/finance/phases/done/phase9-cost-slippage-liquidity-realism.md`.
- Integrated verification passed: Phase 9 touched service compile, UI / engine boundary checker, full `tests.test_service_contracts` 90 tests, finance refinement hygiene, and `git diff --check`.
- Next hardening target is Phase 10: walk-forward / out-of-sample / regime split validation.
- Completed `.aiworkspace/note/finance/tasks/active/backtest-realism-gate-policy-refinement-v1/`.
- Final Review gate policy now surfaces failing Backtest Realism row criteria, including cost / slippage sensitivity and liquidity gaps, in selected-route evidence.
- Row-level `NEEDS_INPUT` maps to blocker severity and `REVIEW` maps to review-required; no waiver, memo, preset, approval, order, or auto rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/cost-slippage-sensitivity-audit-v1/`.
- Backtest Realism Audit now reads `cost_slippage_sensitivity_contract_v1` and shows a separate cost / slippage sensitivity row.
- Explicit cost / slippage sensitivity can PASS; generic robustness-only sensitivity stays REVIEW, and missing cost / net curve baseline stays NEEDS_INPUT.
- No new JSONL registry, memo, preset, raw run artifact, DB schema, provider fetch, approval, order, or auto rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/liquidity-capacity-evidence-v1/`.
- Provider operability context now emits compact capacity metrics, and Backtest Realism Audit reads `liquidity_capacity_contract_v1`.
- Fresh official actual provider evidence is the strong liquidity PASS path; stale / partial / bridge-proxy / legacy pass-only evidence stays REVIEW or NEEDS_INPUT.
- No new JSONL registry, memo, preset, DB schema, UI direct provider fetch, approval, order, or auto rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/net-cost-curve-application-v1/`.
- Runtime now emits compact `net_cost_curve_contract_v1` metadata, and Practical Validation / Backtest Realism Audit preserve gross-net cost proof without new workflow persistence.
- Backtest Realism Audit now separates measurable net cost impact from zero-cost, missing-turnover, legacy-flag-only, and missing-proof cases.
- Next Phase 9 task is `liquidity-capacity-evidence-v1`; keep it DB/provider/loader-backed and avoid UI direct fetch.
- Completed `.aiworkspace/note/finance/tasks/active/turnover-rebalance-evidence-v1/`.
- Runtime now emits compact `turnover_evidence_contract_v1` metadata and does not fabricate turnover when holdings columns are missing.
- Backtest Realism Audit separates holdings-derived turnover, legacy estimate, cadence-only, and missing turnover evidence.
- No new JSONL registry, user memo, preset, approval, order, or auto rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/cost-model-source-contract-review-v1/`.
- Runtime now emits compact `cost_model_source_contract_v1` metadata showing when transaction cost is applied to the net result curve.
- Practical Validation source snapshots preserve cost model evidence, and Backtest Realism Audit treats cost bps without application proof as REVIEW.
- No new JSONL registry, user memo, preset, approval, order, or auto rebalance behavior was added.
- Opened `.aiworkspace/note/finance/phases/active/phase9-cost-slippage-liquidity-realism/`.
- Phase 9 focuses on cost / slippage / turnover / liquidity / capacity realism in Backtest Realism and selected-route decisions.
- Next task is `cost-model-source-contract-review-v1`; start by mapping current cost metadata source and proof gaps before runtime changes.
- Completed `.aiworkspace/note/finance/tasks/active/phase8-integrated-qa-closeout/`.
- Phase 8 is closeout complete; summary added at `.aiworkspace/note/finance/phases/done/phase8-investability-data-evidence-expansion.md`.
- Integrated verification passed: lifecycle path compile check, full `tests.test_service_contracts` 79 tests, and `git diff --check`.
- Next hardening target is Phase 9: cost / slippage / turnover / liquidity realism.

### 2026-05-28
- Completed `.aiworkspace/note/finance/tasks/active/lifecycle-audit-scoring-v1/`.
- Data Coverage Audit now separates lifecycle evidence metrics for actual coverage, actual non-covering rows, current snapshots, SEC identity cross-check, computed partial rows, and actual delisting rows.
- This is read-only audit scoring; it adds no DB table, ingestion collector, workflow JSONL, memo, preset, approval, order, or rebalance behavior.
- Completed `.aiworkspace/note/finance/tasks/active/computed-snapshot-lifecycle-v1/`.
- Added `finance/data/computed_lifecycle.py` and `run_collect_computed_snapshot_lifecycle()` to summarize repeated current snapshot lifecycle rows as DB `computed_from_snapshots` partial evidence.
- Data Coverage Audit now requires `coverage_status=actual` before lifecycle evidence can make survivorship PASS; no workflow JSONL, memo, preset, approval, order, or rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/sec-cik-exchange-crosscheck-v1/`.
- Added `finance/data/sec_company_tickers.py` and `run_collect_sec_company_ticker_crosscheck()` to store SEC current CIK / ticker / exchange association as DB lifecycle `listing_observed` partial identity evidence.
- The collector adds no workflow JSONL, memo, preset, approval, order, or rebalance behavior, and does not loosen survivorship PASS criteria.
- Completed `.aiworkspace/note/finance/tasks/active/symbol-directory-snapshot-ingestion-v1/`.
- Added `finance/data/symbol_directory.py` and `run_collect_symbol_directory_snapshots()` to store Nasdaq public Symbol Directory current rows as DB lifecycle `listing_observed` partial evidence.
- The collector adds no workflow JSONL, memo, preset, approval, order, or rebalance behavior, and does not loosen survivorship PASS criteria.
- Completed `.aiworkspace/note/finance/tasks/active/historical-membership-source-review-v1/`.
- Source review found Nasdaq Daily List is the strongest corporate-action source but subscription / approval based, so Phase 8 free-source-first implementation should not start there.
- Next Phase 8 implementation is `symbol-directory-snapshot-ingestion-v1`, using public Nasdaq Symbol Directory current files as DB lifecycle `listing_observed` partial evidence.
- Opened `.aiworkspace/note/finance/phases/active/phase8-investability-data-evidence-expansion/` as the official Phase 8 board for the 1차 hardening cycle.
- Completed `.aiworkspace/note/finance/tasks/active/symbol-lifecycle-event-fields-v1/`.
- `nyse_symbol_lifecycle` now has event semantics for lifecycle rows: NYSE current listing snapshot rows are `listing_observed` partial evidence, and SEC Form 25 rows are `delisting` actual evidence.
- The change updates DB schema / writers / loader / contracts and adds no new workflow JSONL, memo, preset, approval, order, or rebalance behavior.
- Completed `.aiworkspace/note/finance/tasks/active/sec-form25-ingestion-ui-v1/`.
- `Workspace > Ingestion > Practical Validation Provider Snapshots` now has a `Delisting Evidence` tab that runs the SEC Form 25 lifecycle evidence collector.
- The UI writes only through the existing DB collector path and adds no new workflow JSONL, memo, preset, report file, approval, order, or rebalance behavior.
- Completed `.aiworkspace/note/finance/tasks/active/sec-form25-delisting-backfill-v1/`.
- Added SEC EDGAR Form 25 / 25-NSE delisting collector and ingestion job wrapper that write compact actual delisting evidence to `finance_meta.nyse_symbol_lifecycle`.
- Form 25 evidence is treated as delisting evidence, not complete historical membership or active-listing proof. No workflow JSONL, memo, preset, report file, approval, order, or rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/historical-universe-survivorship-v1/`.
- Added `nyse_symbol_lifecycle` schema, NYSE listing lifecycle UPSERT path, lifecycle coverage loader, and Data Coverage / Validation Efficacy survivorship integration.
- Current listing snapshots remain partial evidence; only requested-period historical / delisting lifecycle evidence can make survivorship control PASS. No workflow JSONL, memo, preset, approval, order, or rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/integrated-investability-gate-qa-v1/`.
- Final Review evidence read model now has integrated contract coverage for all-ready, multi-review, and multi-blocker investability gate combinations.
- This QA added no DB write, new JSONL registry, memo, preset, approval, order, or rebalance behavior.
- Completed `.aiworkspace/note/finance/tasks/active/data-coverage-gate-policy-link-v1/`.
- Data Coverage Audit now participates in the profile-aware gate policy: `NEEDS_INPUT` / `BLOCKED` blocks selected-route, and `REVIEW` requires hold / re-review before selection.
- This uses the existing investability packet and selected-route gate; no DB write, new JSONL registry, memo, preset, approval, order, or rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/data-coverage-hardening-v1/`.
- Practical Validation and Final Review now show a read-only Data Coverage Audit for DB price window coverage, provider freshness, PIT replay / period coverage, universe listing, survivorship / delisting control, and storage boundary.
- The audit reads existing DB loader summaries and compact validation evidence; it does not create a new JSONL registry, memo, preset, approval, order, or rebalance behavior.
- Completed `.aiworkspace/note/finance/tasks/active/backtest-realism-gate-policy-link-v1/`.
- Backtest Realism Audit now participates in the profile-aware gate policy: `NEEDS_INPUT` / `BLOCKED` blocks selected-route, and `REVIEW` requires hold / re-review before selection.
- This uses the existing investability packet and selected-route gate; no DB write, new JSONL registry, memo, preset, approval, order, or rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/backtest-realism-hardening-v1/`.
- Practical Validation and Final Review now show a read-only Backtest Realism Audit for transaction cost, turnover, liquidity / operability, net performance policy, rebalance timing, tax / account scope, and execution boundary gaps.
- The audit reads existing result metadata / compact validation evidence and feeds the investability packet / saved evidence rows; no DB write, new JSONL registry, memo, preset, approval, order, or rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/validation-efficacy-gate-policy-link-v1/`.
- Validation Efficacy Audit now participates in the profile-aware gate policy: `NEEDS_INPUT` / `BLOCKED` blocks selected-route, and `REVIEW` requires hold / re-review before selection.
- This uses the existing investability packet and selected-route gate; no DB write, new JSONL registry, memo, preset, approval, order, or rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/validation-efficacy-hardening-v1/`.
- Practical Validation and Final Review now show a read-only Validation Efficacy Audit for runtime replay, period coverage, benchmark parity, provider freshness, robustness, PIT / look-ahead, survivorship / universe, and execution/storage boundary gaps.
- The audit uses existing compact evidence only; no DB write, new JSONL registry, user memo, preset, approval, order, or rebalance behavior was added.
- Follow-up gate policy link is complete; next implementation track is Data Coverage Hardening.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-v2-p3-closeout-qa/`.
- Practical Validation V2 P3 selected monitoring integration is now closeout complete: continuity, recheck comparison, recheck readiness, symbol freshness, and selected provider evidence passed service / boundary QA.
- Next work should open a new task / phase for validation efficacy, backtest realism, or data coverage hardening rather than extending P3.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-v2-p3-selected-provider-evidence/`.
- Selected Dashboard Performance Recheck now shows read-only provider evidence for selected component ticker weights, existing DB provider / holdings / exposure context, and compact look-through summary.
- `NOT_RUN`, partial, stale, or missing provider evidence is visible before relying on selected monitoring; no provider collection, JSONL write, monitoring log, memo, preset, approval, order, or rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-v2-p3-symbol-freshness/`.
- Selected Dashboard Performance Recheck now shows read-only symbol freshness for replay portfolio tickers and benchmark tickers.
- Missing / stale price DB symbols are visible before running recheck; no OHLCV collection, monitoring log, memo, preset, approval, order, or rebalance behavior was added.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-v2-p3-recheck-readiness/`.
- Selected Dashboard Performance Recheck now shows read-only readiness for DB latest market date, replay contract coverage, default period, and execution/storage boundary.
- This does not collect data, save monitoring logs, create memo/preset records, approve orders, or rebalance.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-v2-p3-recheck-comparison/`.
- Selected Dashboard Review Signals now includes a read-only Recheck Evidence Comparison for CAGR, MDD, benchmark spread, component coverage, and period coverage.
- Missing / failed Performance Recheck remains `NEEDS_INPUT`; no DB/JSONL monitoring log, memo, preset, report, approval, order, or auto rebalance write was added.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-v2-p3-continuity-check/`.
- Selected Portfolio Dashboard now shows a read-only Final Review -> Selected Dashboard continuity check.
- The continuity check verifies selected route, investability packet, component target, review trigger, timeline connection, Performance Recheck input, and execution/storage boundary without auto-writing monitoring logs.
- Completed Practical Validation V2 P2 closeout in `.aiworkspace/note/finance/tasks/active/practical-validation-v2/`.
- Verified provider context / look-through / robustness / Final Review service contracts with `tests/test_service_contracts.py`.
- P2 is now closed; next decision is whether to open P3 for Final Review handoff QA and Selected Portfolio Dashboard monitoring connection.
- Completed `.aiworkspace/note/finance/tasks/active/structured-waiver-policy-v1/`.
- Added `.aiworkspace/note/finance/docs/flows/STRUCTURED_WAIVER_POLICY.md`.
- Policy: current implementation remains `waiver_supported=False`; future waiver cannot apply to `BLOCK` and can only consider structured, expiring `REVIEW_REQUIRED` gaps.
- Closed out `.aiworkspace/note/finance/phases/active/investability-decision-foundation/` as implementation complete.
- Added `.aiworkspace/note/finance/phases/done/investability-decision-foundation.md` as the concise closeout summary.
- Carry-forward decisions are now structured waiver policy, provider snapshot PIT/as-of requirement, and Practical Validation V2 P3 scope.
- Completed `.aiworkspace/note/finance/tasks/active/decision-dossier-report-v1/`.
- Final Review saved records and Selected Portfolio Dashboard can now render/download a read-only markdown Decision Dossier.
- Dossier generation reads existing final decision evidence and optional session timeline; it does not auto-write report files, monitoring logs, orders, or approval rows.
- Next recommended step is Investability Decision Foundation phase closeout or structured waiver policy decision.
- Completed `.aiworkspace/note/finance/tasks/active/selected-monitoring-timeline-v1/`.
- Selected Portfolio Dashboard now has a read-only Timeline tab for Final Review selection, evidence gate, Performance Recheck, Actual Allocation drift, and review trigger preview.
- Timeline generation does not append monitoring logs, create user memo storage, approve orders, or trigger auto rebalance.
- Next implementation candidate is `decision-dossier-report-v1`.
- Completed `.aiworkspace/note/finance/tasks/active/robustness-lab-v1/`.
- Practical Validation now builds a compact `robustness_lab_board` from existing stress / rolling / sensitivity / overfit evidence.
- Practical Validation, Final Review, and final decision evidence rows read the same board without adding a new JSONL registry or storing raw perturbation artifacts.
- Next implementation candidate is `selected-monitoring-timeline-v1`.
- Completed `.aiworkspace/note/finance/tasks/active/look-through-exposure-board-v1/`.
- Provider context now includes a compact `look_through_board` for holdings / exposure asset buckets, top holdings, overlap, and ETF-level coverage.
- Practical Validation and Final Review display the board without adding a new JSONL registry or duplicating full holdings rows.
- Next implementation candidate is `robustness-lab-v1`.
- Completed `.aiworkspace/note/finance/tasks/active/data-provenance-coverage-v1/`.
- Provider context schema v2 now carries compact source mix, freshness, as-of range, stale symbols / series, and coverage weights.
- Stale ETF provider snapshot evidence now downgrades otherwise-PASS provider diagnostics to REVIEW; no DB schema or JSONL registry was added.
- Next implementation candidate is `look-through-exposure-board-v1`.
- Completed `.aiworkspace/note/finance/tasks/active/storage-governance-audit-v1/`.
- Added `.aiworkspace/note/finance/docs/data/STORAGE_GOVERNANCE.md` as the durable DB / JSONL / saved setup / run artifact boundary.
- Main investability chain remains `PORTFOLIO_SELECTION_SOURCES -> PRACTICAL_VALIDATION_RESULTS -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2`; no registry rewrite or new JSONL was added.
- Followed by `data-provenance-coverage-v1`.
- Opened `.aiworkspace/note/finance/phases/active/investability-decision-foundation/` as the Phase 0 baseline for investability workflow hardening.
- Completed `.aiworkspace/note/finance/tasks/active/validation-gate-hardening-v1/`.
- Added profile-aware gate policy snapshot to `app/services/backtest_evidence_read_model.py` and Final Review display.
- Final decision rows now keep compact `gate_policy_snapshot`; no new JSONL registry was added.
- Next investability foundation choice is storage governance audit versus data provenance / coverage.
- Opened `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/` for Workspace Overview Market Movers polish.
- Market Movers second pass adds selected-coverage browser auto refresh, volume rank, sector-colored positive return bars, and previous-period momentum context while keeping provider collection inside existing job wrappers.
- Completed the Overview browser-session auto refresh workstream under `.aiworkspace/note/finance/tasks/active/overview-browser-auto-refresh/`.
- Market Movers refresh UX is now a unified `데이터 갱신` status / action bar with manual vs browser-auto mode, second-by-second countdown UI, compact snapshot metadata, S&P 500 Daily-only browser-safe auto refresh, and Overview visual tokens / components split into `app/web/overview_ui_components.py`.
- Completed Events UX redesign under `.aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/`: source summary, refresh popover, mini source status cards, Agenda / Calendar / Quality / Raw views, and reduced-width-safe filters.
- Completed market session banner under `.aiworkspace/note/finance/tasks/active/overview-market-session-banner/`: Overview now shows NYSE open / close in KST first, ET second, with weekend / holiday / early-close handling.
- Completed Sector / Industry trend polish under `.aiworkspace/note/finance/tasks/active/overview-mi-sector-leadership-trend/`: S&P 500 / Top1000 / Top2000 leadership, longer trend windows, positive group ticker leaders, intraday daily path, EOD fallback explanation, loading spinner, and short cache.
- Merge handoff: Overview Market Intelligence is now a production baseline for daily use. Remaining local dirty state is generated run history only; do not stage `.aiworkspace/note/finance/run_history/*.jsonl` unless explicitly requested.

### 2026-05-28
- Completed `.aiworkspace/note/finance/tasks/active/overview-mi-market-movers-ops-hardening/`.
- Added Market Movers daily snapshot coverage %, richer refresh-state fields, and DB-only status auto-check for SP500 / TOP1000 / TOP2000.
- Moved the Market Movers refresh bar into the timed DB reload fragment so stale / due guidance can update without automatic provider collection.
- Completed `.aiworkspace/note/finance/tasks/active/overview-mi-events-calendar-ux/`.
- Added Events `Days Until`, `Importance`, and `Focus` read-model fields, plus Focus / Calendar / Table tabs with an Importance filter.
- Events calendar now stacks counts by event type so FOMC, Macro, and Earnings rows are distinguishable at a glance.
- Completed `.aiworkspace/note/finance/tasks/active/overview-mi-earnings-quality-hardening/`.
- Added earnings symbol diagnostics for missing / outside-window / provider-error cases, surfaced diagnostics in Ingestion and Overview refresh results, and added Events `Quality Action` read-model guidance.
- Completed `.aiworkspace/note/finance/tasks/active/overview-mi-bls-ics-import/`.
- Added official BLS `.ics` file import fallback for Macro Calendar so CPI / PPI / Employment Situation rows can be stored when backend BLS requests return HTTP 403.
- Ingestion Macro tab now exposes `.ics` upload/import; Data Health treats `import_bls_macro_calendar_ics` as a Macro Calendar refresh path.
- Completed 4차 production UX for `.aiworkspace/note/finance/phases/active/overview-market-intelligence-productionization/`.
- Added Market Movers Rank / Sector Pulse tabs, Sector / Industry Heatmap / Table tabs, and Events Calendar / Table views with window/source/validation filters.
- Updated runbook, phase acceptance notes, roadmap, and task handoff docs. Remaining future candidates are macro calendar sources, official earnings IR parsing, and scheduled refresh automation.
- Opened `.aiworkspace/note/finance/phases/active/overview-market-intelligence-productionization/`.
- Recommended formalization path: 1차 prototype complete, 2차 production baseline, 3차 earnings/events production, 4차 UX/automation polish.
- Next implementation task is `Task 2-01 Refresh State And Diagnostics Baseline`.
- Completed phase closeout under `.aiworkspace/note/finance/tasks/active/overview-market-intelligence-closeout/`.
- Added `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md` for Market Movers, FOMC, and earnings prototype refresh operations.
- Updated phase plan/design/integration wording so Events is no longer described as a placeholder; closeout QA passed.
- Completed Task 6 under `.aiworkspace/note/finance/tasks/active/overview-earnings-prototype/`.
- Added bounded yfinance earnings calendar collection into `market_event_calendar` as `EARNINGS`, wired Ingestion prototype controls and Overview Events filter/refresh.
- Local smoke wrote 3 earnings rows for `AAPL`, `MSFT`, `NVDA`; service contract tests passed.
- Completed Task 5 under `.aiworkspace/note/finance/tasks/active/overview-fomc-collector/`.
- Added Fed official FOMC calendar collection into `finance.data.market_intelligence`, wrapped it as `collect_fomc_calendar`, and wired Ingestion / Overview Events to `market_event_calendar`.
- Local smoke wrote 16 FOMC rows for 2026/2027; service contract tests passed.
- Next overview-market-intelligence item is production hardening / UX follow-up for Events or broader event sources.

### 2026-05-27
- Completed Task 7-04 under `.aiworkspace/note/finance/tasks/active/practical-validation-diagnostics-split/`.
- Moved `source_components_dataframe` into `app/services/backtest_practical_validation_source.py` and pinned diagnostics compatibility exports with `__all__`.
- Task 7 `practical-validation-diagnostics-split` is complete; next cleanup slice is Task 8 runtime wrapper cleanup.
- Completed Task 7-03 under `.aiworkspace/note/finance/tasks/active/practical-validation-diagnostics-split/`.
- Added `app/services/backtest_practical_validation_stress_sensitivity.py` for rolling validation, stress windows, baseline challenge, sensitivity interpretation, correlation risk, market context, and overfit audit helpers.
- Diagnostics service now focuses more on component context assembly and the 12 diagnostic result orchestration.
- Followed by Task 7-04 orchestration import / public contract cleanup.
- Completed Task 7-02 under `.aiworkspace/note/finance/tasks/active/practical-validation-diagnostics-split/`.
- Added `app/services/backtest_practical_validation_curve_context.py` for compact curve snapshots, curve normalize, DB price proxy, component curve combination, and monthly/window helpers.
- Compare and Candidate Review now import compact curve snapshot helpers directly from the curve context service helper.
- Followed by Task 7-03 stress / sensitivity helper extraction.
- Completed Task 7-01 under `.aiworkspace/note/finance/tasks/active/practical-validation-diagnostics-split/`.
- Added `app/services/backtest_practical_validation_source.py` for validation profile and Clean V2 selection source builders.
- Diagnostics service remains the public compatibility surface, while direct Compare / Candidate Review / Practical Validation service imports now use the source helper module.
- Followed by Task 7-02 curve context helper extraction.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-helper-boundary/`.
- Moved Practical Validation curve helper to `app/services/backtest_practical_validation_curve.py`.
- Moved provider context adapter to `app/services/backtest_practical_validation_provider_context.py`.
- Boundary lint now reports no `app.services/app.runtime -> app.web` advisories; next cleanup task is diagnostics service split.
- Opened `.aiworkspace/note/finance/phases/active/ui-engine-boundary-cleanup/`.
- Completed Task 0 audit at `.aiworkspace/note/finance/tasks/active/ui-engine-boundary-cleanup-audit/`.
- Task 0 originally found 3 Practical Validation helper advisories; Task 6 resolved them.
- Next task is `7. practical-validation-diagnostics-split`.

### 2026-05-20
- Completed `.aiworkspace/note/finance/tasks/active/runtime-package-boundary/`.
- `5-01`: moved `app/web/runtime` to `app/runtime` and updated repo imports to `app.runtime`.
- `5-02`: moved Candidate Library replay helper to `app/runtime/candidate_library.py`.
- Boundary lint now scans both `app/services` and `app/runtime`; remaining advisories are Practical Validation web helper dependencies.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-diagnostics-service-boundary/`.
- Moved the large Practical Validation diagnostic builder from `app/web` to `app/services/backtest_practical_validation_diagnostics.py`.
- Practical Validation service, Compare, and Candidate Review now import diagnostic/source/compact curve helpers from the service boundary.
- Added diagnostics service contract coverage to `tests/test_service_contracts.py`.
- Added `.aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` as a repo-local UI-engine boundary lint helper.
- The helper hard-fails on Streamlit usage in `app/services` / `app/runtime` and staged generated / registry / saved artifacts, while reporting current `app.services/app.runtime -> app.web` imports as advisory transition debt.
- Completed `.aiworkspace/note/finance/tasks/active/evidence-read-model-boundary/`.
- Added `app/services/backtest_evidence_read_model.py` so Final Review saved decision rows and Selected Dashboard evidence rows share a Streamlit-free read model.
- `ui-engine-boundary-foundation` implementation slices are now complete; next decision is phase closeout QA or a follow-up boundary phase.
- Completed `.aiworkspace/note/finance/tasks/active/practical-validation-service-boundary/`.
- Added `app/services/backtest_practical_validation.py` as the Streamlit-free Practical Validation source/result append and handoff contract boundary.
- `app/web/backtest_practical_validation_helpers.py` no longer imports Streamlit; UI modules apply service handoff contracts to session state.
- Next implementation slice in the phase: `evidence-read-model-boundary`.

### 2026-05-19
- Opened the active phase `.aiworkspace/note/finance/phases/active/ui-engine-boundary-foundation/`.
- Created the first audit task at `.aiworkspace/note/finance/tasks/active/ui-engine-boundary-audit/`.
- Durable direction: keep Streamlit for now and introduce `app/services` as the UI-engine boundary.
- Completed the first implementation task `.aiworkspace/note/finance/tasks/active/backtest-execution-service-boundary/` by moving Single Backtest dispatch / error normalization to `app/services/backtest_execution.py`.
- Started `.aiworkspace/note/finance/tasks/active/compare-service-boundary/` and moved manual compare execution loop / error normalization to `app/services/backtest_compare_execution.py`.
- Moved the compare strategy runner catalog / defaults to `app/services/backtest_compare_catalog.py`; UI now injects current preset dictionaries as `ComparePresetCatalog`.
- Moved weighted portfolio bundle construction to `app/services/backtest_weighted_portfolio.py` and data-only result helper logic to `app/services/backtest_result_read_model.py`.
- Moved saved portfolio replay execution / data assembly to `app/services/backtest_saved_portfolio_replay.py`; UI keeps session state, history append, notices, and render side effects.
- Next implementation slice: start `practical-validation-service-boundary`.

### 2026-05-13
- Renamed the product direction research workspace from `.aiworkspace/note/finance/research/` to `.aiworkspace/note/finance/researches/`.
- Updated AGENTS, durable docs, active task notes, and product research skills to use `researches/active/<research-id>/`.
- Synced the global finance skill mirrors after the path rename.

### 2026-05-13
- Set `.aiworkspace/note/finance/researches/` as the canonical workspace for product direction research output.
- Added `researches/README.md` plus `active/` and `done/` folders for audit, benchmark, feature candidate, recommendation, source, and risk notes.
- Updated AGENTS, docs index/project map/roadmap, and the product research skills so actual research outputs go to `researches/active/<research-id>/`.
- `tasks/active/` remains for execution records such as skill/workflow changes.

### 2026-05-13
- Completed Product Research Skill Stage 1 for future finance roadmap research.
- Added the active task at `.aiworkspace/note/finance/tasks/active/product-research-skill-stage1/`.
- New validated stage-1 skills are `finance-product-audit`, `finance-benchmark-research`, and `finance-feature-opportunity`.
- The intent is to validate the research workflow before later packaging a dedicated product-research plugin.

### 2026-05-13
- Renamed finance worktrees / branches to the new role names:
  - `candidate-search` -> `research` / `codex/research`
  - `phase` -> `main-dev` / `codex/main-dev`
  - `ux-ui-polishing` -> `sub-dev` / `codex/sub-dev`
- Updated active workspace guidance and skill-system notes so future routing uses `main-dev`, `research`, and `sub-dev`.

### 2026-05-13
- Migrated legacy `code_analysis/` into the new document system.
- Moved current-state developer flow docs into:
  - `.aiworkspace/note/finance/docs/architecture/`
  - `.aiworkspace/note/finance/docs/flows/`
  - `.aiworkspace/note/finance/docs/runbooks/`
- Moved Practical Validation V2 planning docs into `.aiworkspace/note/finance/tasks/active/practical-validation-v2/`.
- Rewrote the old portfolio selection redesign guide as the current-state `PORTFOLIO_SELECTION_FLOW.md`.
- Removed the old `.aiworkspace/note/finance/code_analysis/` folder and updated active references to the new paths.

### 2026-05-11
- Updated finance document-writing guidance for future phase / planning documents.
- Updated:
  - `AGENTS.md`
  - `.aiworkspace/note/finance/PHASE_PLAN_TEMPLATE.md`
  - `.aiworkspace/note/finance/docs/runbooks/AUTOMATION_SCRIPTS.md`
  - `.aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py`
  - local finance phase/doc-sync skill guidance
- Durable decision:
  - New or substantially rewritten plan documents should use `이걸 하는 이유?` as the plain-language purpose/value section.
  - Separate plain-summary and end-benefit sections are no longer required.

### 2026-05-11
- Updated Practical Validation V2 P2 provider connector planning after source / ingestion direction review.
- Updated:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/PROVIDER_CONNECTORS.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/CONNECTOR_AND_STRESS_PLAN.md`
- Durable decision:
  - P2 development starts with provider data collection through `finance/data/*` ingestion and MySQL persistence.
  - Practical Validation / Dashboard must read provider data through loaders, not remote-fetch from the UI.
  - Official issuer / FRED sources are preferred; `yfinance`, `nyse_asset_profile`, and price-history ADV remain bridge / fallback evidence.

### 2026-05-11
- Reframed Practical Validation V2 P2 around diagnostic normalization rather than provider collection as the end goal.
- Updated:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/IMPLEMENTATION_PLAN.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/CONNECTOR_AND_STRESS_PLAN.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/PROVIDER_CONNECTORS.md`
- Durable decision:
  - P2 means normalizing the incomplete Practical Validation diagnostics among the 12 patterns.
  - Provider / holdings / macro ingestion is the implementation method, not the product goal.
  - P2 target diagnostics are primarily 2, 3, 5, 6, 7, 9, 10, and 11.

### 2026-05-11
- Completed Practical Validation V2 P2-0 target diagnostic contract.
- Updated:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/CONNECTOR_AND_STRESS_PLAN.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/PROVIDER_CONNECTORS.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/IMPLEMENTATION_PLAN.md`
- Durable decision:
  - P2-0 fixed the target diagnostics as 2, 3, 5, 6, 7, 9, 10, and 11.
  - Each target diagnostic now has an actual-data requirement, bridge/proxy fallback, `NOT_RUN` / `REVIEW` condition, and compact evidence boundary.
  - Next work is P2-1: schema / ingestion field contract based on the P2-0 diagnostic contract.

### 2026-05-10
- Clarified `NOT_RUN` handling for Final Review route in Practical Validation docs.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - `NOT_RUN` is not a pass. It means the diagnostic was not executed because data or implementation is missing.
  - Final Review can still receive candidates with some `NOT_RUN` domains, but critical `NOT_RUN` domains must be explicitly acknowledged.
  - Missing core prices or similarly dangerous gaps should be treated as `BLOCKED`, not soft `NOT_RUN`.

### 2026-05-10
- Clarified proxy classification and holdings look-through wording in Practical Validation design docs.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - Proxy classification means using ticker-level category proxies when holdings data is unavailable.
  - Holdings look-through means checking ETF internal constituents and top holding overlap.
  - Missing holdings coverage should be shown as `NOT_RUN`, not as pass.

### 2026-05-10
- Changed Practical Validation design-question status tables to a single checklist table.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - Use one table with `확인 여부`, `질문`, and `결정 / 기본 방향` columns instead of splitting design questions into completed and remaining sections.
  - Mark confirmed items as `O` and implementation-time choices as `X`.

### 2026-05-10
- Refreshed Practical Validation open design questions.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - Practical Validation design questions are now split into `결정 완료` and `남은 구현 선택`.
  - Remaining implementation choices are rolling window defaults, cost assumptions, baseline proxy set, sensitivity perturbation grid, stress window defaults, and future sentiment connector timing.

### 2026-05-10
- Finalized Korean-facing Validation Profile wording for Practical Validation design.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/FINANCE_TERM_GLOSSARY.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - User-facing profile labels should be Korean: 방어형, 균형형, 성장형, 전술 / 헤지형, 사용자 지정.
  - Internal ids remain English for code / JSON stability.
  - The 5 profile questions are portfolio purpose, tolerated drawdown, expected holding period, product / complexity allowance, and desired improvement versus simple alternatives.
  - Invariant hard blockers mean validation failures that cannot be waived by an aggressive profile.

### 2026-05-10
- Clarified Practical Validation terminology and future sentiment connector scope.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/FINANCE_TERM_GLOSSARY.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - Sentiment Overlay remains a required future Practical Validation module, but the first implementation can keep it as `NOT_RUN` / future connector until the core validation flow is stable.
  - Future sentiment work should start with FRED-based VIX / Credit Spread / Yield Curve snapshots and keep Fear & Greed optional.
  - Asset Allocation Profile means the expected asset exposure character used to interpret equity, bond, cash, gold, commodity, inverse, and leveraged allocation fit.

### 2026-05-10
- Refined the Practical Validation diagnostics design with Validation Profile behavior.
- Updated:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - Practical Validation should ask 3~5 questions to create a Validation Profile, then use that profile to adjust thresholds, domain weights, blocker / review interpretation, and user-intent mismatch warnings.
  - The profile should not skip diagnostic domains. Available domains should still be attempted, while invariant hard blockers such as Data Trust failure, weight total error, missing core prices, execution boundary violations, and large leveraged / inverse mismatch remain strict.
- Current status:
  - Product code was not changed. This is a document-only design refinement before implementation.

### 2026-05-10
- Documented the Practical Validation investment diagnostics direction.
- Created:
  - `.aiworkspace/note/finance/researches/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`
- Updated:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`
  - `.aiworkspace/note/finance/researches/README.md`
  - `.aiworkspace/note/finance/FINANCE_DOC_INDEX.md`
  - `.aiworkspace/note/finance/docs/architecture/README.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Durable decision:
  - Practical Validation should not be only an upstream evidence summary. It should use upstream evidence as input, then run portfolio-level practical diagnostics such as asset allocation fit, concentration / overlap, correlation / risk contribution, macro / sentiment context, stress / scenario, alternative portfolio challenge, leveraged / inverse suitability, ETF operability, and robustness / overfit review.
- Current status:
  - Product code was not changed. This is a research and development guide update for the next implementation unit.

### 2026-05-03
- Opened Phase 34 `Final Portfolio Selection Decision Pack`.
- Created:
  - `.aiworkspace/note/finance/phases/phase34/PHASE34_FINAL_PORTFOLIO_SELECTION_DECISION_PACK_PLAN.md`
  - `.aiworkspace/note/finance/phases/phase34/PHASE34_CURRENT_CHAPTER_TODO.md`
  - `.aiworkspace/note/finance/phases/phase34/PHASE34_FINAL_DECISION_CONTRACT_FIRST_WORK_UNIT.md`
  - `.aiworkspace/note/finance/phases/phase34/PHASE34_TEST_CHECKLIST.md`
  - `.aiworkspace/note/finance/phases/phase34/PHASE34_COMPLETION_SUMMARY.md`
  - `.aiworkspace/note/finance/phases/phase34/PHASE34_NEXT_PHASE_PREPARATION.md`
- Synced:
  - roadmap, document index, work log, question log, and comprehensive analysis current-state references
- Current status:
  - Phase 34 is `active` / `not_ready_for_qa`
  - first work unit, final decision contract and storage boundary, is completed
  - next work unit is decision evidence pack calculation criteria
- Durable takeaway:
  - Phase 34 is not live approval or order execution. It will read Phase 33 paper ledger records and create a final selection / hold / reject / re-review decision pack.

### 2026-05-03
- Closed Phase 33 after the user confirmed the checklist was complete.
- Updated:
  - marked Phase 33 as `complete` / `manual_qa_completed`
  - preserved the user's checked `PHASE33_TEST_CHECKLIST.md`
  - synced Phase33 TODO, completion summary, next-phase preparation, roadmap, doc index, comprehensive analysis, work log, and question log
- Durable takeaway:
  - Phase 33 is closed. Phase 34 can start as the Final Portfolio Selection Decision Pack phase, reading the saved Paper Portfolio Tracking Ledger but still staying separate from live approval or order execution.

### 2026-05-03
- Completed Phase 33 implementation units 1~4 and moved the phase to manual QA handoff.
- Implemented:
  - `app/web/runtime/paper_portfolio_ledger.py` append / load helper for `.aiworkspace/note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`
  - `Backtest > Portfolio Proposal` Paper Tracking Ledger Draft / Save controls under Validation Pack
  - saved Paper Tracking Ledger review surface with source, target weights, benchmark, cadence, triggers, raw JSON
  - Phase34 handoff route calculation for saved ledger records
- Synced:
  - Phase33 TODO, checklist, completion summary, next-phase preparation, work-unit docs
  - README, AGENTS, script map, Backtest UI flow, operations guide, glossary, roadmap, doc index, comprehensive analysis
- Validation:
  - focused py_compile passed
  - paper ledger helper smoke passed
- Current status:
  - Phase 33 is `implementation_complete` / `manual_qa_pending`
  - user manual QA should use `PHASE33_TEST_CHECKLIST.md`
- Durable takeaway:
  - Phase 33 creates an explicit paper tracking ledger record, but it is still not paper PnL automation, final selection, live approval, or order execution.

### 2026-05-03
- Closed Phase 32 after the user confirmed the checklist was complete.
- Updated:
  - marked Phase 32 as `complete` / `manual_qa_completed`
  - synced Phase 32 TODO, checklist, completion summary, next-phase preparation, roadmap, doc index, work log, question log, README, and comprehensive analysis
  - kept the Phase 32 Robustness / Stress surface as read-only validation and handoff, not proposal save, paper ledger save, live approval, or final selection
- Durable takeaway:
  - Phase 32 is closed, and Phase 33 can begin as the paper tracking ledger phase.

### 2026-05-03
- Opened Phase 33 `Paper Portfolio Tracking Ledger`.
- Created:
  - `.aiworkspace/note/finance/phases/phase33/PHASE33_PAPER_PORTFOLIO_TRACKING_LEDGER_PLAN.md`
  - `.aiworkspace/note/finance/phases/phase33/PHASE33_CURRENT_CHAPTER_TODO.md`
  - `.aiworkspace/note/finance/phases/phase33/PHASE33_LEDGER_CONTRACT_FIRST_WORK_UNIT.md`
  - `.aiworkspace/note/finance/phases/phase33/PHASE33_TEST_CHECKLIST.md`
  - `.aiworkspace/note/finance/phases/phase33/PHASE33_COMPLETION_SUMMARY.md`
  - `.aiworkspace/note/finance/phases/phase33/PHASE33_NEXT_PHASE_PREPARATION.md`
- Synced:
  - roadmap, document index, work log, question log, and comprehensive analysis current-state references
- Current status:
  - Phase 33 is `active` / `not_ready_for_qa`
  - first work unit is paper ledger row contract and storage boundary
- Durable takeaway:
  - Phase 33 is not final selection or live approval. It starts the append-only paper tracking ledger needed before Phase 34 final selection decision work.

### 2026-04-20
- Reorganized section 3 of `FINANCE_COMPREHENSIVE_ANALYSIS.md` so current architecture and phase history are separated.
- Changed:
  - renamed section 3 to `현재 시스템 구조와 phase별 구현 히스토리`
  - added `3-1. 현재 시스템 구조` as the current architecture reading path
  - added `3-2. Phase별 구현 히스토리` as a grouped phase timeline from Phase 1~25
  - moved the previous mixed chronological narrative under `3-3. 상세 구현 메모`
  - changed the old `Phase 14 Practical Closeout` UI status sentence to read as a historical note rather than current state
- Durable takeaway:
  - The comprehensive analysis now keeps deep implementation notes but no longer asks users to read mixed phase history as the current architecture explanation.

### 2026-04-20
- Added a user-facing entry layer to `FINANCE_COMPREHENSIVE_ANALYSIS.md` without removing the deep technical context.
- Changed:
  - clarified the document's three roles: readable system map, agent deep reference, and durable implementation context
  - added a quick reading guide by purpose
  - added a one-page current system summary across data collection, persistence, loader/runtime, strategy engine, web UI, and review/pre-live layers
  - added reading rules so older implementation notes are preserved as history while current state is checked against roadmap/work logs
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` remains the deep system reference, but it now has a clearer human-readable entry point.

### 2026-04-20
- Refined the `FINANCE_DOC_INDEX.md` earlier-phase section after user feedback.
- Changed:
  - replaced the single long `Earlier Phase Detail` table with one subsection per phase for Phase 1~18
  - added managed documents where relevant, including plan, TODO, work unit, checklist, completion, next-phase prep, decisions, gates, and validation notes
  - kept the scope controlled by listing representative managed documents instead of every historical file
- Durable takeaway:
  - Both recent and earlier phases are now navigable by phase, while the index still avoids becoming a full archive dump.

### 2026-04-20
- Reorganized `FINANCE_DOC_INDEX.md` as a navigation-first finance document map.
- Changed:
  - reduced the index from a long explanatory list into a shorter phase-oriented guide
  - added a "지금 먼저 볼 문서" section for Phase 25 active work
  - split top-level docs, operating files, backtest reports, recent phases, earlier phases, support track, data/runtime references, research references, and archives
  - moved detailed backtest result lookup guidance toward `backtest_reports/BACKTEST_REPORT_INDEX.md`
- Durable takeaway:
  - `FINANCE_DOC_INDEX.md` should now act as a document map, not another long explanation document.

### 2026-04-20
- Closed `Phase 24` and opened `Phase 25`.
- Changed:
  - accepted the completed `PHASE24_TEST_CHECKLIST.md` manual QA state
  - marked `PHASE24_CURRENT_CHAPTER_TODO.md`, `PHASE24_COMPLETION_SUMMARY.md`, and `PHASE24_NEXT_PHASE_PREPARATION.md` as Phase 24 closeout / Phase 25 handoff documents
  - bootstrapped the Phase 25 document bundle
  - rewrote the Phase 25 plan, TODO, checklist, completion draft, next-phase draft, and first work-unit note around `Pre-Live Operating System And Deployment Readiness`
  - fixed the Phase 25 boundary as `Real-Money 검증 신호 = per-run diagnostic signal` and `Pre-Live 운영 점검 = paper / watchlist / hold / re-review operating process`
  - synced `MASTER_PHASE_ROADMAP.md`, `FINANCE_DOC_INDEX.md`, and durable analysis logs
- Durable takeaway:
  - Phase 24 is closed as a completed new-strategy implementation bridge, and Phase 25 is now active as a pre-live operating-system development phase, not a live trading or investment approval phase.

### 2026-04-20
- Clarified the Phase 25 boundary between existing Real-Money validation and future pre-live operation workflow.
- Decision:
  - `Real-Money 검증 신호` = per-backtest diagnostic surface for transaction cost, benchmark, drawdown, liquidity, ETF operability, promotion status
  - `Pre-Live 운영 점검` = Phase 25 workflow for paper tracking, watchlist, hold/review decisions, monitoring notes, and re-collection/re-validation actions
- Updated:
  - `Reference > Guides > 테스트에서 상용화 후보 검토까지 사용하는 흐름`
  - `FINANCE_TERM_GLOSSARY.md`
  - `PHASE24_NEXT_PHASE_PREPARATION.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `QUESTION_AND_ANALYSIS_LOG.md`

### 2026-04-20
- Corrected the `Global Relative Strength` malformed price-row handling policy after user QA feedback.
- Decision:
  - do not silently remove or repair a malformed price row to extend the backtest result window
  - keep the conservative common rebalance-date behavior so `IWM`'s `2026-03-17` missing close naturally limits the run to the last clean common rebalance date
  - surface the issue through `malformed_price_rows` metadata and a Korean warning so the operator can inspect or re-collect the source price row
- Validation expectation:
  - the same `2016-01-01 -> 2026-04-20` default run should end at `2026-02-27` until the malformed `IWM` source row is fixed or re-collected
- Documentation hygiene:
  - reviewed index impact; no new durable document was added, so `FINANCE_DOC_INDEX.md` did not need a structural update

### 2026-04-20
- Fixed a follow-up Phase 24 QA issue where `Global Relative Strength` stopped at `2026-02-27` even when the selected end date was `2026-04-20`.
- Root cause:
  - `IWM` had one DB row on `2026-03-17` with empty OHLC values
  - `add_ma` treated that empty `Close` inside the rolling window as invalid and dropped all later MA rows until the rolling window recovered
  - month-end alignment therefore lost March/April common dates and the result stopped at February
- Implemented:
  - `add_ma` now removes rows with missing price values before calculating moving averages
  - Global Relative Strength now records those removed malformed rows in `malformed_price_rows` metadata and result warnings
  - real-money warning strings shown under "이번 실행에서 같이 봐야 할 주의사항" were translated to Korean-oriented copy
- Validation:
  - `.venv` default `Global Relative Strength` runtime smoke for `2016-01-01 -> 2026-04-20` now ends at `2026-04-17`, the latest available DB trading date
  - the same smoke surfaces `IWM 1건(2026-03-17)` as a malformed price-row warning
  - `.venv/bin/python -m py_compile finance/transform.py app/web/runtime/backtest.py finance/sample.py`
- Documentation hygiene:
  - reviewed index impact; no new durable document was added, so `FINANCE_DOC_INDEX.md` did not need a structural update

### 2026-04-20
- Fixed a Phase 24 QA issue in `Global Relative Strength` single-strategy execution.
- Root cause:
  - default preset included `EEM`, but the current DB only had recent `EEM` price rows
  - after `MA200` and 12-month relative-strength warmup, `EEM` became an empty transformed series
  - strict date intersection then failed with `공통 Date가 없습니다.`
- Implemented:
  - DB-backed Global Relative Strength now excludes risky tickers that have insufficient transformed price history
  - excluded tickers are preserved in result metadata as `excluded_tickers`
  - UI/runtime warnings explain that the ticker was excluded and that DB price data should be refreshed before interpreting the result
- Validation:
  - `.venv` default preset runtime smoke now succeeds with `EEM` excluded
  - compact custom universe runtime smoke still succeeds with no excluded tickers
  - `.venv/bin/python -m py_compile finance/sample.py app/web/runtime/backtest.py`

### 2026-04-20
- Continued Phase 24 with the UI / replay integration pass for `Global Relative Strength`.
- Implemented:
  - strategy catalog registration for single and compare strategy selectors
  - `Backtest > Single Strategy` form with universe, cash ticker, top, interval, score horizons, trend filter, and ETF real-money contract inputs
  - `Compare & Portfolio Builder` strategy-specific box and compare runner override support
  - history payload / load-into-form / run-again roundtrip for `cash_ticker`, cadence, score, and trend settings
  - saved portfolio replay override preservation for the new strategy
- Validation:
  - `python3 -m py_compile app/web/backtest_strategy_catalog.py app/web/runtime/backtest.py app/web/runtime/history.py app/web/pages/backtest.py`
  - `.venv` catalog/history smoke
  - `.venv` DB-backed runtime smoke
  - `.venv` compare runner smoke
- Status:
  - Phase 24 is now `practical_closeout / manual_validation_pending`.
  - Next step is user QA via `PHASE24_TEST_CHECKLIST.md`.
- Guidance sync:
  - refreshed `finance-strategy-implementation` skill guidance so future user-facing strategy additions include catalog / single UI / compare / history / saved replay handoff checks.

### 2026-04-19
- Continued Phase 23 implementation with the first quarterly contract parity pass.
- Implemented:
  - quarterly single-strategy UI now shows `Portfolio Handling & Defensive Rules`
  - quarterly payloads now carry weighting, rejected-slot handling, risk-off, and defensive ticker contract values
  - quarterly compare forms now expose the same portfolio handling contract controls
  - quarterly history load-into-form restores the same contract values
  - quarterly runtime wrappers accept and pass these contracts to the DB-backed strict statement shadow execution path
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py app/web/runtime/backtest.py finance/sample.py`
  - `.venv` import/signature smoke for the three quarterly strict prototype runners

### 2026-04-19
- Opened `Phase 23 Quarterly And Alternate Cadence Productionization`.
- Created and rewrote the Phase 23 plan / TODO / checklist / completion / next-phase documents so the phase is clearly framed as product development, not investment analysis.
- Added the first work-unit document:
  - `.aiworkspace/note/finance/phases/phase23/PHASE23_QUARTERLY_PRODUCTIONIZATION_FRAME_FIRST_WORK_UNIT.md`
- Current reading:
  - quarterly strict family already has execution paths
  - Phase 23 will harden UI, payload, compare/history/replay, and representative validation before Phase 24 new strategy expansion

### 2026-04-18
- Started a user-requested GTAA investable portfolio search outside the current presets.
- Used sub-agents for:
  - GTAA runtime / promotion metadata path discovery
  - conservative ETF universe exploration
  - offensive ETF universe exploration
- Re-ran the strongest ideas in the main environment with `.venv/bin/python` and current DB-backed `run_gtaa_backtest_from_db`.
- Result:
  - compact ETF sleeves produced `real_money_candidate` GTAA candidates without relaxing ETF AUM/spread gates
  - broader high-CAGR universes were rejected because current ETF operability/profile coverage pushed them back to `hold`
  - saved the durable report at `.aiworkspace/note/finance/backtest_reports/strategies/GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md`
  - appended the result to the GTAA strategy log and candidate registry

### 2026-04-16
- Split the roadmap tail into two clearer roles:
  - `현재 위치` now behaves like a status board
  - `지금부터의 큰 흐름` now behaves like a next-step guide
- Removed:
  - duplicated reading-order guidance that overlapped between the two sections
- Result:
  - the roadmap reads more like a single coherent document and less like two overlapping summaries

### 2026-04-16
- Reworked the roadmap summary section that used to read as a special `Phase 18~25 Draft Big Picture`.
- Changed it into:
  - `다음 단계 한눈에 보기 (Phase 18 ~ 25)`
  - a quick-reading summary that clearly says it does not replace the actual phase descriptions above
- Result:
  - the roadmap now feels less like it has a second special roadmap embedded inside it
  - `Phase 18 ~ 25` is easier to read as a continuation of the same master roadmap

### 2026-04-16
- Clarified roadmap semantics after user review:
  - `Phase 18` is still in-progress from a backlog perspective
  - `Phase 19` and `Phase 20` are fully manual-validation completed
  - `Phase 5 first chapter` was a historical chapter label, not a hidden active second chapter
  - `support track` remains a parallel tooling lane, not a main finance phase
- Updated the roadmap so these distinctions read more directly.

### 2026-04-16
- Refreshed `MASTER_PHASE_ROADMAP.md` after the user pointed out that the reading order had become awkward.
- Reordered:
  - `Phase 6` and `Phase 16` back into their natural chronological positions
  - `현재 위치` / `Phase 18~25 Draft Big Picture` / `앞으로의 운영 방식` into a cleaner tail structure
- Synced:
  - `Phase 19` status now reads as `phase complete / manual_validation_completed`
  - active pointer now follows `Phase 21` as the next main phase board
- Result:
  - the roadmap now reads as a real phase sequence again instead of a mix of historical notes and later inserts

### 2026-04-16
- Rebased the roadmap after the user pointed out that the old `Phase 21` was not really product work.
- Applied:
  - previous `Research Automation And Experiment Persistence` work is now treated as a support track, not a main finance phase
  - the main roadmap was redesigned so the new `Phase 21` is `Integrated Deep Backtest Validation`
  - new `Phase 21` plan / TODO / checklist / next-phase docs now reflect deep validation instead of agent/plugin setup
- Result:
  - the project phase sequence is back on the product path:
    validation -> portfolio-level construction -> quarterly productionization -> new strategy expansion -> pre-live readiness

### 2026-04-16
- Reviewed Phase 21 QA documents after Phase 20 workflow naming/validation changes.
- Outcome:
  - `PHASE21_TEST_CHECKLIST.md` itself did not need major target changes because it validates scripts, registry, and docs rather than Phase 20 UI buttons
  - added one explicit note so future QA readers know the Phase 20 button rename is not the core Phase 21 test target
  - updated `PHASE21_NEXT_PHASE_PREPARATION.md` so it no longer assumes Phase 20 operator workflow is still the main open question

### 2026-04-16
- User-facing Phase 20 checklist confirmation is now complete.
- Closed:
  - `PHASE20_CURRENT_CHAPTER_TODO.md` -> `phase complete / manual_validation_completed`
  - `PHASE20_COMPLETION_SUMMARY.md` -> reflects checklist completion
  - `PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md` -> status synced to completion
- Meaning:
  - current candidate -> compare -> weighted -> saved -> replay/load-back workflow is now considered closed at the manual validation level

### 2026-04-16
- Phase 20 saved-portfolio QA exposed one real replay bug and one lingering UX gap.
- Fixed:
  - `Replay Saved Portfolio` could fail when stored compare overrides still contained legacy keys such as `factor_freq`
    that the current strict-annual runtime wrappers no longer accept
  - compare replay now filters unsupported kwargs against the current runner signature before execution
- Clarified:
  - `Save This Weighted Portfolio` now explains what `Portfolio Name` and `Description` are for
  - `Portfolio Name` starts from the current source label or strategy combination so the saved name reads less like an empty form
  - the saved-portfolio re-entry button now reads as `Load Saved Setup Into Compare`
    so it feels more like "restore settings" than "edit this record in place"

### 2026-04-15
- Applied a Phase 20 QA-driven UX clarification pass to `Current Candidate Re-entry`.
- Added:
  - clearer explanation that current candidate re-entry fills the compare form rather than running compare immediately
  - clearer explanation for `Load Current Anchors` and `Load Lower-MDD Near Misses`
  - registry-source explanation that the list is curated from `CURRENT_CANDIDATE_REGISTRY.jsonl`, not auto-filled by every run
  - a `What Changed In Compare` summary card that shows selected strategies, period, and key overrides after load

### 2026-04-15
- Fixed a strict-annual shadow sample parity bug found during manual backtest validation.
- Cause:
  - strict annual runtime wrappers started passing `rejected_slot_handling_mode`
    to the shadow DB sample entrypoints,
    but the three shadow helpers in `finance/sample.py`
    still only accepted the older boolean pair.
- Applied the fix to:
  - quality strict annual shadow path
  - value strict annual shadow path
  - quality+value strict annual shadow path
- Result:
  - the shadow sample entrypoints now accept the explicit rejected-slot handling contract
    and normalize it back into legacy flags before execution.

### 2026-04-15
- Continued Phase 20 through practical closeout.
- Added the second operator-workflow hardening unit:
  - compare source context now carries into weighted portfolio and saved portfolio flows
  - `Current Compare Bundle` summary now explains what the current compare run came from
  - saved portfolio actions and detail tabs were renamed/expanded to make next actions clearer
- Synced:
  - Phase 20 closeout docs
  - roadmap / doc index
  - finance analysis
  - current candidate registry guide
- Current reading:
  - Phase 20 is now `practical closeout / manual_validation_pending`
  - main remaining step is the user-facing checklist

### 2026-04-13
- Compressed the root work log into a concise active-context version.
- Moved the previous full log to:
  - `.aiworkspace/note/finance/archive/WORK_PROGRESS_ARCHIVE_20260413.md`
- Added a one-page current-candidate summary and code-flow/operator docs so future backtest refinement work can restart faster.

### 2026-04-13
- Continued Phase 16 as a downside-focused practical refinement track for both `Value` and `Quality + Value`.
- Confirmed `Value` current best practical point still remains:
  - `Top N = 14 + psr`
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `real_money_candidate / paper_probation / review_required`
- Confirmed the most useful lower-MDD `Value` near-miss:
  - `+ pfcr`
  - `CAGR = 27.22%`
  - `MDD = -21.16%`
  - but `production_candidate / watchlist`

### 2026-04-13
- Confirmed new `Quality + Value` current strongest practical point:
  - `net_margin -> operating_margin`
  - `ocf_yield -> pcr`
  - `operating_income_yield -> por`
  - `Top N = 10`
  - `Candidate Universe Equal-Weight`
  - `CAGR = 31.82%`
  - `MDD = -26.63%`
  - `real_money_candidate / small_capital_trial / review_required`

### 2026-04-13
- Added repo-local Codex workflow support artifacts:
  - current candidate summary
  - backtest refinement code-flow guide
  - runtime artifact hygiene guide
  - repo-local plugin scaffold:
    - `.aiworkspace/plugins/quant-finance-workflow`
  - repo-local skill draft:
    - `finance-backtest-candidate-refinement`
  - first practical plugin script:
    - `.aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`

### 2026-04-13
- Promoted the finance refinement hygiene script into an explicit operating rule.
- Synced:
  - `AGENTS.md`
  - `operations/RUNTIME_ARTIFACT_HYGIENE.md`
- Default usage points are now:
  - after meaningful refinement/doc-sync units
  - before commit
  - before phase closeout

### 2026-04-13
- Closed Phase 16 as a bounded downside-refinement phase.
- `Value`:
  - current best practical point remains `Top N = 14 + psr`
  - `28.13% / -24.55% / real_money_candidate / paper_probation / review_required`
  - lower-MDD near-miss `+ pfcr` improved `MDD` to `-21.16%` but only reached `production_candidate / watchlist`
- `Quality + Value`:
  - current strongest practical point remains
    `operating_margin + pcr + por + per + Top N 10 + Candidate Universe Equal-Weight`
  - `31.82% / -26.63% / real_money_candidate / small_capital_trial / review_required`
  - lower-MDD alternatives existed, but all weakened gate quality
- Synced:
  - Phase 16 closeout docs
  - strategy hubs / backtest logs
  - roadmap / doc indexes

### 2026-04-14
- Clarified compare / weighted portfolio / saved portfolio workflow semantics.
- Current reading:
  - `Compare` = research surface for side-by-side strategy inspection
  - `Weighted Portfolio` = monthly composite of compared strategies
  - `Saved Portfolio` = replayable research artifact for compare -> builder -> rerun
- Durable note:
  - weighted bundles do not create new real-money / promotion / shortlist / deployment semantics on their own
  - Phase 17 should document them as operator bridges, not as independent candidate gates

### 2026-04-14
- Opened Phase 17 as a structural downside-improvement phase.
- Synced:
  - phase kickoff plan
  - current board
  - structural lever inventory first pass
  - candidate consolidation fit review first pass
  - code-flow guide
  - repo-local refinement skill reference
- Current reading:
  - immediate main track:
    - strict annual structural downside levers
  - secondary/supporting track:
    - weighted portfolio / saved portfolio as operator bridge
- Current first-slice recommendation:
  - `partial cash retention` before broader defensive-sleeve or weighting redesign

### 2026-04-14
- Clarified near-term development order before Phase 17 implementation.
- Current order:
  - first:
    - existing core strategy structural refinement
  - second:
    - candidate consolidation / operator bridge cleanup
  - later:
    - new strategy or wider expansion work
- Durable takeaway:
  - new strategy work is still planned,
    but it is intentionally behind the current `Value / Quality + Value` structural downside-improvement track

### 2026-04-14
- Implemented the first Phase 17 structural lever slice:
  - strict annual `partial cash retention`
- Wired through:
  - `finance.strategy.quality_snapshot_equal_weight(...)`
  - strict annual DB-backed sample/runtime wrappers
  - strict annual single / compare forms
  - selection interpretation / warnings / input params
- Current rule:
  - applies only when `Trend Filter` partially rejects raw selected names
  - does not replace full-cash `market regime` / guardrail risk-off behavior
- Verification:
  - `py_compile` passed
  - synthetic smoke confirmed
    - `off` = survivor reweighting
    - `on` = rejected slots retained as cash
  - representative DB-backed rerun is still gated by local shadow-factor data availability

### 2026-04-14
- Ran the first Phase 17 representative rerun on real current anchors.
- Cases:
  - `Value` current practical anchor:
    - `Top N = 14 + psr`
    - `Trend Filter = on`
    - `cash retention off/on`
  - `Quality + Value` strongest practical point:
    - strongest factor set
    - `Trend Filter = on`
    - `cash retention off/on`
- Result:
  - `partial cash retention` worked and materially lowered `MDD` in both families
  - but both cases still stayed `hold / blocked`
  - main pattern:
    - downside improved strongly
    - cash share rose materially
    - return drag remained too large for practical gate rescue
- Updated:
  - Phase 17 representative rerun report
  - strategy hubs
  - strategy backtest logs
  - current candidate summary
- Next priority:
  - `defensive sleeve risk-off` over another cash-only follow-up

### 2026-04-14
- Implemented the second Phase 17 structural lever slice:
  - strict annual `defensive sleeve risk-off`
- Wired through:
  - `finance.strategy.quality_snapshot_equal_weight(...)`
  - strict annual DB-backed sample/runtime wrappers
  - strict annual single / compare forms
  - warning / meta / interpretation surface
- Important correction:
  - defensive sleeve ticker was separated from strict annual candidate-universe filtering
  - this removed the false `Liquidity Excluded Count` inflation that appeared in the first rerun
- Representative rerun result after the correction:
  - `Value` current anchor:
    - gate unchanged
    - `MDD` slightly worse
  - `Quality + Value` current strongest point:
    - gate unchanged
    - `MDD` slightly worse
- Durable takeaway:
  - `defensive sleeve risk-off` is now implemented and verifiable
  - but it did not produce a same-gate lower-MDD rescue on the current anchors
  - next structural lever priority moves to `concentration-aware weighting`

### 2026-04-14
- Reviewed strict annual reuse points for `concentration-aware weighting`.
- Key finding:
  - no existing rank-based taper/capped position-weight contract was found in the strict annual family
  - the safest first slice remains the `quality_snapshot_equal_weight(...)` rebalancing block after top-N selection
- Reusable runtime contract:
  - keep `strategy_key` / `snapshot_mode` / `snapshot_source` / `factor_freq` / `universe_contract` / dynamic universe fields aligned with the current strict annual wrappers

### 2026-04-14
- Implemented the third Phase 17 structural lever slice:
  - strict annual `concentration-aware weighting`
- Wired through:
  - `finance.strategy.quality_snapshot_equal_weight(...)`
  - strict annual DB-backed sample/runtime wrappers
  - strict annual single / compare forms
  - warning / meta / interpretation surface
- Current contract:
  - `equal_weight`
  - `rank_tapered`
- Representative rerun result:
  - `Value` current anchor:
    - gate unchanged

### 2026-04-15
- Started the first real Phase 20 implementation unit.
- Added a `Current Candidate Re-entry` surface inside `Compare & Portfolio Builder`.
- Current anchors and lower-MDD near-misses can now be sent back into compare without manually rebuilding the full strict annual contract.
- Synced:
  - Phase 20 first work-unit document
  - phase TODO board
  - roadmap / doc index
  - finance comprehensive analysis
- Validation:
  - `py_compile`
  - `.venv` import smoke
  - current candidate registry helper smoke
    - `MDD` worse
    - `Rolling Review` also weakened
  - `Quality + Value` current strongest point:
    - gate unchanged
    - `CAGR` higher
    - but `MDD` worse
- Durable takeaway:
  - `concentration-aware weighting` is now implemented and verifiable
  - but it did not produce a same-gate lower-MDD rescue on the current anchors
  - next active question moves to
    Phase 17 closeout vs next structural lever reprioritization

### 2026-04-14
- Closed Phase 17 as a structural downside-improvement phase.
- Practical closeout reading:
  - `partial cash retention`
  - `defensive sleeve risk-off`
  - `concentration-aware weighting`
  first three slices are now implemented and representative-rerun verified
- Common conclusion:
  - no same-gate lower-MDD exact rescue was found for
    current `Value` / `Quality + Value` anchors
  - current practical anchors remain unchanged
- Synced:
  - Phase 17 completion summary
  - next-phase preparation
  - manual test checklist
  - roadmap / finance doc index
- Follow-up review:
  - examined a possible first slice for filling trend-rejected raw top-N slots with next-ranked eligible names
  - safest candidate insertion point is still the strict annual rebalancing block in `finance/strategy.py`
  - this redesign should be treated as a separate interpretation lane from `partial cash retention` and `rank_tapered`, not as a cosmetic tweak to either one

### 2026-04-14
- Opened Phase 18 as `Larger Structural Redesign`.
- Implemented first slice:
  - strict annual `Fill Rejected Slots With Next Ranked Names`
- Wired through:
  - `finance.strategy.quality_snapshot_equal_weight(...)`
  - strict annual DB-backed sample/runtime wrappers
  - strict annual single / compare forms
  - history / rerun / interpretation surface
- New durable result/meta fields:
  - `Rejected Slot Fill Enabled`
  - `Rejected Slot Fill Active`
  - `Rejected Slot Fill Ticker`
  - `Rejected Slot Fill Count`
  - `rejected_slot_fill_enabled`
- Representative rerun first pass:
  - `Value` trend-on probe:
    - cash drag와 downside 개선 방향은 확인됐지만
      still `hold / blocked`
    - meaningful redesign reference로는 남지만
      current practical anchor replacement는 아니었다
  - `Quality + Value` trend-on probe:
    - `CAGR`, `MDD`, cash share improved
    - but still `hold / blocked`
- Durable takeaway:
  - next-ranked eligible fill is a meaningful larger-redesign lane
  - first pass does not replace the current practical anchors
  - next follow-up should stay in Phase 18 rather than reopening bounded tweak work

### 2026-04-14
- Re-ran Phase 18 `next-ranked eligible fill` around the actual `Value` practical anchor.
- Scope:
  - `base + psr`, `Top N = 12~16`
  - `base + psr + pfcr`, `Top N = 12~16`
  - `Trend Filter = on`, `rejected_slot_fill_enabled = on`
- Result:
  - no same-gate lower-MDD rescue was found
  - all anchor-near candidates remained `hold / blocked`
  - best lower-MDD near-miss was:
    - `base + psr + pfcr`, `Top N = 13`
    - `24.47% / -24.89% / hold / blocked`
- Durable takeaway:
  - Phase 18 first slice should be kept as a meaningful redesign reference,
    not as a rescued replacement candidate
  - next work should shift to Phase 18 second-slice prioritization

### 2026-04-14
- User direction changed Phase 18 from rerun-first to implementation-first.
- Current rule:
  - broader deep backtest / wider rescue search is paused
  - new implementation slices should be followed only by
    compile / import smoke and minimal representative validation
- Synced:
  - Phase 18 plan
  - current board
  - roadmap
  - finance doc index
- Durable takeaway:
  - next active work is not another broad rerun cycle
  - it is selecting and implementing the Phase 18 second slice first

### 2026-04-14
- Rebased the upper roadmap from current `Phase 18` status through a new `Phase 25` draft.
- Current reading:
  - `Phase 18~21`
    - implementation / operator / automation backlog
  - `Phase 22`
    - integrated deep backtest validation restart
  - `Phase 23~25`
    - portfolio candidate / new strategy / pre-live operator workflow expansion
- Synced:
  - master roadmap
  - roadmap rebase draft
  - finance doc index
- Durable takeaway:
  - current discussion point is no longer just the next slice,
    but whether this `Phase 19~25` sequence matches the user's desired long-term direction

### 2026-04-14
- Rewrote the `Phase 19~25` roadmap explanation in plainer language.
- Focus:
  - what each future phase means
  - why it should happen
  - why the proposed order is natural
- Synced:
  - `MASTER_PHASE_ROADMAP.md`
  - `support_tracks/ROADMAP_REBASE_PHASE18_TO_PHASE25_20260414.md`
- Durable takeaway:
  - the roadmap now reads less like a phase title list
    and more like an execution narrative the user can review before deciding direction

### 2026-04-14
- Started `Phase 19` in implementation-first mode.
- First slice:
  - strict annual `Rejected Slot Handling Contract`
  - replaces the operator-facing two-checkbox reading with one explicit handling mode
- Implemented:
  - new explicit mode constants/helpers in `finance.sample`
  - runtime compatibility bridge in `app/web/runtime/backtest.py`
  - single / compare / history / prefill sync in `app/web/pages/backtest.py`
- Validation:
  - `python3 -m py_compile finance/sample.py app/web/runtime/backtest.py app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for the same modules
- Synced:
  - phase19 kickoff docs
  - roadmap
  - finance doc index
  - finance comprehensive analysis
- Durable takeaway:
  - Phase 19 first slice favors contract clarity and legacy compatibility over broad rerun coverage

### 2026-04-14
- Completed `Phase 19` second slice for history / interpretation cleanup.
- Changed:
  - strict annual selection history now preserves rejected-slot fill / cash-retention execution details for interpretation
  - interpretation summary now shows `Rejected Slot Handling`, `Filled Events`, `Cash-Retained Events`
  - history table hides internal booleans and shows operator-facing contract language instead
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
- Synced:
  - phase19 TODO/doc
  - finance comprehensive analysis
  - finance doc index
- Durable takeaway:
  - Phase 19 now covers not only form/runtime contract clarity but also history/interpretation readability for the same handling semantics

### 2026-04-14
- Completed `Phase 19` third slice for risk-off / weighting interpretation cleanup.
- Changed:
  - strict annual selection history now shows `Weighting Contract`, `Risk-Off Contract`, `Risk-Off Reasons`
  - interpretation summary now shows `Weighting Contract`, `Risk-Off Contract`, `Defensive Sleeve Activations`
  - row-level interpretation now distinguishes
    - full cash risk-off
    - defensive sleeve rotation
    - final weighting contract
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
- Synced:
  - phase19 TODO/doc
  - finance comprehensive analysis
  - finance doc index
- Durable takeaway:
  - Phase 19 interpretation cleanup now covers the three main structural contract lanes:
    rejected-slot handling, weighting, and risk-off

### 2026-04-14
- Closed out `Phase 19` at practical closeout / manual_validation_pending.
- Added:
  - `PHASE19_COMPLETION_SUMMARY.md`
  - `PHASE19_NEXT_PHASE_PREPARATION.md`
  - `PHASE19_TEST_CHECKLIST.md`
- Synced:
  - `PHASE19_CURRENT_CHAPTER_TODO.md`
  - `MASTER_PHASE_ROADMAP.md`
  - `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - Phase 19 is now handed off as a documentation/contract stabilization phase with manual UI validation still pending

### 2026-04-14
- Rewrote the `Phase 19` kickoff plan in much plainer language.
- Focus:
  - what this phase is doing
  - why it is needed before deep backtest resumes
  - what difficult terms like `contract`, `slice`, `payload`, `minimal validation` mean
- Synced:
  - `PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md`
  - `FINANCE_TERM_GLOSSARY.md`
- Durable takeaway:
  - the Phase 19 plan now reads as an operator-facing explanation, not just an internal engineering memo

### 2026-04-14
- Updated future phase-plan writing guidance.
- Changed:
  - `AGENTS.md` now requires new or heavily rewritten phase plan docs to include
    - `쉽게 말하면`
    - `왜 필요한가`
    - `이 phase가 끝나면 좋은 점`
  - `Phase 19` kickoff doc now explains the current priority-item jargon inline
- Durable takeaway:
  - future phase plans should be readable as orientation documents, not just compressed planning notes

### 2026-04-14
- Finalized the `Phase 19` kickoff document into a template-style operator-friendly plan.
- Added:
  - `.aiworkspace/note/finance/PHASE_PLAN_TEMPLATE.md`
- Synced:
  - `AGENTS.md`
  - `FINANCE_DOC_INDEX.md`
  - `PHASE19_CURRENT_CHAPTER_TODO.md`
- Durable takeaway:
  - future phase plan documents now have a reusable default shape instead of being rewritten ad hoc each time

### 2026-04-14
- Tightened `Phase 19` strict annual contract UX based on checklist feedback.
- Changed:
  - `Weighting Contract`, `Risk-Off Contract`, `Rejected Slot Handling Contract` now use clearer section titles and labels in strict annual single/compare forms
  - each contract now shows a plain-language "current selection" explanation
  - `Defensive Sleeve Tickers` now explains that it is only used for `Defensive Sleeve Preference` during full risk-off
- Synced:
  - `PHASE19_TEST_CHECKLIST.md`
  - `PHASE19_CURRENT_CHAPTER_TODO.md`
  - `FINANCE_TERM_GLOSSARY.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `FINANCE_DOC_INDEX.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - Phase 19 contract language is now easier to find and read from the form itself, not only from history or docs

### 2026-04-14
- Standardized future phase test checklist workflow.
- Changed:
  - `AGENTS.md` now requires user-facing phase test checklists to prefer Markdown task checkboxes like `[ ]`
  - new `.aiworkspace/note/finance/PHASE_TEST_CHECKLIST_TEMPLATE.md` added as the default checklist template
  - active `PHASE19_TEST_CHECKLIST.md` converted to checkbox-style verification items
- Durable takeaway:
  - future phase handoffs now have a clearer "user checks items directly, then we move on" workflow

### 2026-04-14
- Refined strict annual contract help text based on live Phase 19 checklist feedback.
- Changed:
  - `Rejected Slot Handling Contract` tooltip now explains each option as separate bullet-style items instead of one long sentence
  - `Risk-Off Contract` tooltip now explains what `portfolio-wide risk-off` means in plain Korean
  - overlay contract intro now states that `Weighting Contract`, `Rejected Slot Handling Contract`, and `Risk-Off Contract` are always-on handling rules, not enable/disable toggles
- Synced:
  - `PHASE19_TEST_CHECKLIST.md`
  - `FINANCE_TERM_GLOSSARY.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - contract UI now answers both "what does this option mean?" and "is this always active?" directly from the form

### 2026-04-14
- Reorganized strict annual advanced inputs into separate overlay and handling sections.
- Changed:
  - single / compare strict annual forms now split
    - `Overlay`
    - `Portfolio Handling & Defensive Rules`
  - `Trend Filter` / `Market Regime` stay in `Overlay`
  - `Rejected Slot Handling Contract` / `Weighting Contract` / `Risk-Off Contract` / `Defensive Sleeve Tickers` move into `Portfolio Handling & Defensive Rules`
- Durable takeaway:
  - overlay trigger logic and post-overlay portfolio handling are now easier to distinguish from the form structure itself

### 2026-04-14
- Simplified strict annual handling-contract captions after live UX feedback.
- Changed:
  - removed repetitive `위치:` phrasing from contract captions
  - rewrote `Rejected Slot Handling Contract`, `Risk-Off Contract`, `Weighting Contract` captions around
    - what situation each contract handles
    - easy plain-language summary
    - how it differs from neighboring contracts
  - portfolio handling intro now uses bullet-style role summary instead of compressed inline prose
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
- Durable takeaway:
  - the form now explains contract purpose directly, without relying on repeated location hints

### 2026-04-14
- Clarified strict annual `Risk-Off Contract` wording after additional UX feedback.
- Changed:
  - replaced vague `보수 모드` / `full risk-off` phrasing in strict annual form help with
    - "factor 포트폴리오 전체를 멈추고 현금 또는 방어 ETF로 전환"
    - "포트폴리오 전체를 쉬어야 할 때"
  - aligned `Risk-Off Contract`, `Defensive Sleeve Tickers`, overlay intro, and interpretation summary around the same plain-language meaning
  - synced glossary/comprehensive analysis wording to the same concept
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - users can now read `Risk-Off Contract` as a portfolio-wide transition rule without having to infer what `보수 모드` means

### 2026-04-14
- Tightened History / Selection History UX after Phase 19 checklist confusion.
- Changed:
  - `Backtest > History` now explains that a `history run` means one saved backtest record
  - selected history record drilldown now uses clearer labels like `Selected History Run`, `Saved Run Summary`, `Saved Input & Context`
  - strict annual history drilldown now explicitly says detailed `Selection History` / `Interpretation Summary` are checked after `Run Again` or `Load Into Form`
  - latest result selection tabs now read
    - `Selection History Table`
    - `Interpretation Summary`
    - `Selection Frequency`
  - `Selection History Table` now states that the `Interpretation` column is the row-level explanation
  - `Interpretation Summary` now states which contract / event fields should be checked first
- Synced:
  - `FINANCE_TERM_GLOSSARY.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - users can now find the correct history surface faster and distinguish saved-record review from live selection-history drilldown

### 2026-04-14
- Fixed confusing `History` action flow for strict annual records.
- Changed:
  - `Run Again` from `Backtest > History` now reruns immediately, then moves the UI to `Single Strategy` so the refreshed `Latest Backtest Run` is visible right away
  - `Load Into Form` still moves to `Single Strategy`, but now clearly says it only loads inputs and does not refresh results until the user runs the form
  - added `Back To History` shortcut after `Load Into Form` so the user is not left without an obvious way back
  - updated history warning copy to reference `Selection History Table` / `Interpretation Summary` with current labels
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - history actions now better match user expectation: rerun shows refreshed results, while load-into-form is explicitly framed as input prefill only

### 2026-04-15
- Refined Phase 19 closeout docs to better match the user's actual checklist progress and reading flow.
- Changed:
  - `PHASE19_CURRENT_CHAPTER_TODO.md` now marks manual UI validation as `in_progress` instead of `pending`
  - `PHASE19_COMPLETION_SUMMARY.md` now explains completed work in plainer language under `쉽게 말하면`
  - `PHASE_PLAN_TEMPLATE.md` now uses `작업 단위` language instead of `slice`
  - `AGENTS.md` now explicitly prefers plain-language work-unit labels in future phase plan documents
  - `PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md` was aligned to the same `작업 단위` wording
- Validation:
  - finance refinement hygiene script
- Durable takeaway:
  - phase plan and closeout docs now better match user-facing review flow and avoid internal jargon where it is not helpful

### 2026-04-15
- Phase 19 manual checklist gate is now treated as completed.
- Changed:
  - `PHASE19_CURRENT_CHAPTER_TODO.md` now marks manual UI validation actual run as `completed`
  - `PHASE19_COMPLETION_SUMMARY.md` now reflects `manual_validation_completed`
- Durable takeaway:
  - Phase 19 can now be treated as fully closed from a user-verification standpoint, and the next phase discussion can proceed without leaving the validation gate ambiguous

### 2026-04-15
- Opened Phase 20 as the next active workstream after Phase 19 closeout.
- Changed:
  - created `PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md`
  - created `PHASE20_CURRENT_CHAPTER_TODO.md`
  - created `PHASE20_OPERATOR_WORKFLOW_INVENTORY_FIRST_PASS.md`
  - updated `MASTER_PHASE_ROADMAP.md` phase20 status to `in_progress`
  - synced `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - the project is now treating candidate reuse, compare-to-portfolio flow, and saved-portfolio re-entry as the main active operator workflow problem

### 2026-04-15
- Completed a practical Phase 21 automation/persistence baseline in one work unit.
- Changed:
  - added `bootstrap_finance_phase_bundle.py` to open a new phase document bundle from the repo templates
  - added `manage_current_candidate_registry.py` and seeded `.aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`
  - updated `check_finance_refinement_hygiene.py` so candidate-facing doc work can also review the machine-readable candidate registry
  - created `PHASE21` kickoff, work-unit, closeout, next-phase, and checklist documents
  - synced `AGENTS.md`, plugin/skill docs, roadmap, doc index, registry guide, runtime artifact guidance, and finance comprehensive analysis
- Validation:
  - `python3 -m py_compile .aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate`
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py --phase 99 --title "Automation Smoke Example" --dry-run`
  - finance refinement hygiene script
- Durable takeaway:
  - the repo now has a reusable automation baseline for phase kickoff and current-candidate persistence, which lowers repeated setup cost before later deep validation phases

### 2026-04-15
- Phase 20 QA feedback led to another compare-surface UX cleanup.
- Changed:
  - moved current candidate re-entry out of the space between the compare title and the main `Strategies` control
  - kept strategy selection as the first visible compare action
  - reorganized the current candidate helper into a secondary expander with a smaller `What This Does` explanation block
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import importlib; import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - compare now reads as a primary strategy-selection surface first, while current candidate re-entry behaves like a supporting shortcut instead of competing for top-of-screen attention

### 2026-04-15
- Phase 20 QA also surfaced excessive divider usage inside `Compare & Portfolio Builder`.
- Changed:
  - removed top-level dividers between compare results, weighted portfolio builder, and saved portfolios
  - clarified in the saved-portfolio caption that this area is the next step after compare and weighted builder, not a separate top-level workflow
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - the compare page now relies on section headings instead of repeated horizontal lines, and saved portfolios remains in the same tab because it still behaves like the final step of the same operator workflow

### 2026-04-15
- Phase 20 QA found that current candidate re-entry button labels still read too much like internal jargon.
- Changed:
  - renamed `Load Current Anchors` to `Load Recommended Candidates`
  - renamed `Load Lower-MDD Near Misses` to `Load Lower-MDD Alternatives`
  - renamed the custom picker expander to `Pick Specific Candidates Manually`
  - added one-line explanations under each quick action so users can tell why there are two buttons and when to use each
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - current candidate re-entry now explains “대표 후보 불러오기 / 더 낮은 MDD 대안 불러오기 / 직접 선택” in plain language instead of forcing users to decode internal portfolio-search terms

### 2026-04-15
- Phase 20 QA still found the current candidate re-entry block hard to scan as one mixed section.
- Changed:
  - split the surface into `Quick Bundles` and `Pick Manually` tabs
  - kept the two quick-load buttons together in the first tab
  - moved the candidate table and manual picker into the second tab
  - added an explicit note that this list does not auto-populate from new backtest runs or Markdown docs; it reads active rows from `CURRENT_CANDIDATE_REGISTRY.jsonl`
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - current candidate re-entry now reads as two clearer modes: quick bundle load vs manual pick, and the registry source rule is visible in the UI instead of only in supporting docs

### 2026-04-15
- Phase 20 QA then pointed out that the post-load `What Changed In Compare` card still felt too abstract.
- Changed:
  - changed the card title/phrasing so it reads as a form-update guide instead of an internal status block
  - replaced `Source`, `Label`, `Period` wording with more direct phrases about how the bundle was loaded and what period was auto-filled
  - added a short “where to check” section and a clearer next-step instruction
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - the compare prefill confirmation card now explains the loaded bundle in task-oriented language instead of assuming the user already understands source/label terminology

### 2026-04-15
- Phase 20 QA also asked whether the compare prefill summary was drifting from the actual candidate settings.
- Changed:
  - checked the current-candidate registry -> compare prefill override mapping for top N, benchmark, trend filter, market regime, weighting, risk-off, and universe contract
  - confirmed the current code maps those core fields consistently for the active candidate rows
  - expanded the `Compare Form Updated` table to show `Weighting Contract` and `Risk-Off Contract` alongside `Trend Filter` and `Market Regime`
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `.venv/bin/python` registry-to-prefill smoke check for current candidate rows
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - the current candidate compare prefill path does not appear to be silently loosening key strict-annual settings, and the confirmation table now exposes more of the actual loaded contract

### 2026-04-15
- Phase 20 QA then pointed out that compare `Strategy-Specific Advanced Inputs` still split family selection from the actual selected snapshot settings.
- Changed:
  - turned `Quality Family`, `Value Family`, `Quality + Value Family` into `Quality`, `Value`, `Quality + Value`
  - kept the variant selector at the top of each family section
  - rendered the selected variant's actual settings directly inside the same family expander instead of in a separate snapshot expander lower in the form
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - compare advanced inputs now read more like GTAA and other strategies: choose the family variant once, then adjust that variant immediately in the same section

### 2026-04-15
- Phase 20 QA also asked for a clearer explanation of `Candidate Universe Equal-Weight` inside strict annual `Benchmark Contract`.
- Changed:
  - rewrote the `Benchmark Contract` tooltip in plain language so the two options read as
    "compare to one benchmark ETF" vs "compare to a simple equal-weight portfolio built from the same candidate universe"
  - expanded the selected-state caption for `Candidate Universe Equal-Weight` so the user can understand the meaning without opening glossary docs
  - added a dedicated glossary entry for `Candidate Universe Equal-Weight`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - strict annual benchmark choice is now easier to read as an operator decision: external ETF reference vs simple equal-weight baseline from the same candidate pool

### 2026-04-15
- Phase 20 QA then found that `Candidate Universe Equal-Weight / SPY` still looked like a single mixed benchmark label in compare summaries.
- Changed:
  - split compare prefill summary output into `Benchmark Contract` and `Benchmark Ticker / Reference`
  - changed current candidate registry contract summary so equal-weight cases read as
    `Benchmark Candidate Equal-Weight | Reference Ticker SPY`
    instead of an ambiguous slash-joined label
  - added an explanatory caption in the compare update card when equal-weight benchmark contract is active
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - finance refinement hygiene script
- Durable takeaway:
  - the UI now shows that equal-weight benchmark and SPY are not the same object: one is the benchmark contract, the other can remain a separate reference ticker

### 2026-04-15
- Phase 20 QA asked to make the strict-annual input field itself reflect that distinction too.
- Changed:
  - initially tried contract-dependent field naming, but this was not reliable inside the current submit-based Streamlit form
  - switched to a more robust fixed label: `Benchmark / Guardrail / Reference Ticker`
  - added a plain-language caption explaining how to read the field under each benchmark contract
  - kept prefill summary lines using `Reference Ticker` wording for equal-weight cases
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - in the current form architecture, a stable neutral field label plus contract-dependent explanation is less confusing than trying to live-swap the field name

### 2026-04-15
- Phase 20 QA then confirmed that the neutral single-field approach still felt indirect in practice.
- Changed:
  - separated strict-annual `Real-Money Contract` into two explicit inputs:
    - `Benchmark Ticker`
    - `Guardrail / Reference Ticker`
  - kept `Comparison Baseline` and `Guardrail / Reference` as separate concepts in the form so the user can read
    "what do we compare against?" and "what does the guardrail watch?" independently
  - propagated the same split through single strategy, compare prefill, history/meta, runtime bundle input params, and shadow sample entrypoints
  - updated compare summary copy so equal-weight benchmark rows explain the split using the new two-column wording
- Validation:
  - `python3 -m py_compile finance/sample.py app/web/runtime/backtest.py app/web/pages/backtest.py`
  - `.venv/bin/python -c "import finance.sample; import app.web.runtime.backtest; import app.web.pages.backtest"`
- Reviewed:
  - `FINANCE_DOC_INDEX.md`는 새 durable 문서가 추가된 턴이 아니라서 이번 작업 단위에서는 별도 갱신이 필요하지 않다고 판단
- Durable takeaway:
  - the final UX model is no longer "one ticker field with two meanings"; benchmark baseline and guardrail reference are now first-class separate inputs

### 2026-04-15
- Phase 20 QA then asked for one more UX pass: when `Ticker Benchmark` is chosen, `Guardrail / Reference Ticker` should feel optional, and when `Candidate Universe Equal-Weight` is chosen, `Benchmark Ticker` should stop looking required.
- Changed:
  - `Ticker Benchmark` mode now shows:
    - `Benchmark Ticker`
    - `Guardrail / Reference Ticker (Optional)`
    with copy that says leaving the guardrail field blank means "same as benchmark"
  - `Candidate Universe Equal-Weight` mode now hides the benchmark ticker input and explains that the benchmark curve is auto-built from the candidate universe
  - compare/prefill/history summaries now display `Same as Benchmark Ticker` when no separate guardrail ticker was explicitly set
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
- Durable takeaway:
  - the operator now reads benchmark baseline and guardrail reference as separate decisions, with the optional/same-as-benchmark case made explicit in the UI

### 2026-04-15
- Phase 20 QA then reported that trying to make fields hide/show based on `Benchmark Contract` still felt awkward in practice.
- Changed:
  - confirmed the root cause was the current `st.form` structure: changing a widget inside the form does not immediately rerun the section
  - removed the experimental layout-refresh button approach
  - returned to a simpler UX where `Benchmark Contract`, `Benchmark Ticker`, and `Guardrail / Reference Ticker (Optional)` are always visible together
  - rewrote the captions so the user can understand:
    - `Ticker Benchmark`: benchmark ticker is the direct comparison baseline
    - `Candidate Universe Equal-Weight`: benchmark ticker is not used for the equal-weight baseline itself
    - `Guardrail / Reference Ticker (Optional)`: tied to underperformance / drawdown guardrails regardless of benchmark contract
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
- Durable takeaway:
  - within the current form architecture, "always visible + clearer explanation" is less frustrating than contract-dependent hide/show

### 2026-04-15
- Phase 20 QA then pushed one step further: `Guardrail / Reference Ticker` should not live in `Real-Money Contract` at all because it conceptually belongs to guardrails, not benchmark comparison.
- Changed:
  - moved `Guardrail / Reference Ticker (Optional)` out of `Real-Money Contract` and into the `Guardrails` expander
  - kept `Benchmark Contract` and `Benchmark Ticker` inside `Real-Money Contract`
  - updated the copy so the screen now reads as:
    - `Real-Money Contract` = comparison baseline
    - `Guardrails` = underperformance / drawdown stop rules plus their reference ticker
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
- Durable takeaway:
  - the benchmark baseline and the guardrail reference now live in the same places as their actual behavioral meaning, which is much easier to understand in the UI

### 2026-04-15
- Phase 20 QA then pointed out that `Compare Form Updated` should hide values that are not actually used by the loaded contract.
- Changed:
  - when `Benchmark Contract = Candidate Universe Equal-Weight`, the compare summary now leaves `Benchmark Ticker` blank
  - when both underperformance and drawdown guardrails are off, the compare summary now leaves `Guardrail / Reference Ticker` blank
  - kept `Same as Benchmark Ticker` only for cases where a guardrail is on but no separate reference ticker was explicitly entered
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
- Durable takeaway:
  - the compare summary is now closer to a true "active settings" view: unused values stay empty instead of looking meaningful

### 2026-04-15
- Phase 20 QA then hit a follow-up compare strict-annual runtime error after the `Guardrail / Reference Ticker` field was moved into `Guardrails`.
- Changed:
  - removed one stale `guardrail_reference_ticker` assignment that still lived in the compare `Quality Snapshot (Strict Annual)` path
  - kept the compare strict-annual guardrail reference flow fully inside the `Guardrails` expander, matching the single-strategy path
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- Durable takeaway:
  - the compare strict-annual UI now uses the same guardrail-reference ownership model as the single-strategy UI, so the late `NameError` regression is removed.

### 2026-04-16
- Phase 20 QA then pointed out that the information block above `Weighted Portfolio Builder` still read like an internal context card instead of an operator-friendly "what am I combining?" view.
- Changed:
  - rewrote the builder intro copy in plain language so the section reads as "compare에서 본 전략을 어떤 비중으로 섞는 단계"
  - replaced the old `Current Compare Bundle` style card with a clearer `What You Are Combining` summary
  - the summary now shows:
    - where this compare result came from
    - which period is being combined
    - how many strategies are in scope
    - a compact strategy table with `Strategy / Period / CAGR / MDD / Promotion`
  - kept saved-portfolio re-entry weights visible only when they actually exist, as context rather than as the main headline
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- Durable takeaway:
  - weighted-builder context now starts from "what we are combining" instead of "what internal compare bundle object exists," which is easier to read during QA and normal operator use.

### 2026-04-16
- Phase 20 QA then requested that divider placement in `Compare & Portfolio Builder` match the visual grouping more naturally.
- Changed:
  - removed the divider directly under `Quick Re-entry From Current Candidates`
  - added a divider between `Strategy Comparison` and `Weighted Portfolio Builder`
  - added a divider between `Weighted Portfolio Builder` and `Saved Portfolios`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- Durable takeaway:
  - dividers now separate the three main operator stages instead of splitting the compare entry tools from the compare form.

### 2026-04-16
- Phase 20 QA then showed that the checklist itself had started lagging behind the renamed UI labels.
- Changed:
  - updated `PHASE20_TEST_CHECKLIST.md` to use current on-screen names first
  - added an old-name -> current-UI-name mapping block
  - made each section more explicit about where the tester should look on screen
  - aligned the weighted/saved divider checks with the current layout
- Durable takeaway:
  - once UI wording starts changing during QA, the checklist should follow the current labels quickly or it stops being a good test guide.

### 2026-04-16
- Closed `Phase 18` as `practical_closeout / manual_validation_pending` instead of keeping the remaining structural backlog open as an active blocker.
- Changed:
  - created `PHASE18_COMPLETION_SUMMARY.md`
  - created `PHASE18_NEXT_PHASE_PREPARATION.md`
  - created `PHASE18_TEST_CHECKLIST.md`
  - updated `PHASE18_CURRENT_CHAPTER_TODO.md` so the remaining second-slice idea is now treated as deferred backlog rather than current active work
  - updated `PHASE18_LARGER_STRUCTURAL_REDESIGN_PLAN.md` so the current phase reading points toward closeout and handoff
- Durable takeaway:
  - `Phase 18` already produced meaningful redesign evidence, but not anchor replacement evidence, so the right next step is closeout plus handoff rather than one more structural slice.

### 2026-04-16
- Started the new main `Phase 21` reading as `in_progress` and aligned the top-level roadmap/doc index to that state.
- Changed:
  - updated `PHASE21_INTEGRATED_DEEP_BACKTEST_VALIDATION_PLAN.md` to explicitly treat `Phase 18` remaining structural ideas as future options
  - updated `PHASE21_CURRENT_CHAPTER_TODO.md` to reflect kickoff progress and the `Phase 18` closeout decision
  - synced `MASTER_PHASE_ROADMAP.md` and `FINANCE_DOC_INDEX.md` so they now read as:
    - `Phase 18` = practical closeout / manual validation pending
    - `Phase 21` = in progress
- Durable takeaway:
  - the main track is now clearer: we are not opening more structural redesign first, we are validating the current annual-strict candidates and portfolio bridge in one shared frame.

### 2026-04-16
- Continued `Phase 21` with the first real work unit: validation frame definition.
- Changed:
  - created `PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md`
  - fixed the common rerun frame to:
    - `2016-01-01 ~ 2026-04-01`
    - `US Statement Coverage 100`
    - `Historical Dynamic PIT Universe`
  - fixed the family rerun packs to the current registry-backed candidates:
    - `Value` current anchor / lower-MDD near-miss
    - `Quality` current anchor / cleaner alternative
    - `Quality + Value` current anchor / lower-MDD weaker-gate alternative
  - fixed the representative bridge frame to:
    - `Load Recommended Candidates`
    - near-equal weighted bundle
    - representative saved portfolio replay
  - fixed phase21 report and strategy-log naming rules before actual reruns
- Durable takeaway:
  - `Phase 21` is now in a true execution-ready state: the next step is no longer "define the frame" but "run the pack."

### 2026-04-16
- Ran the first actual `Phase 21` rerun pack for `Value`.
- Changed:
  - reran:
    - current anchor `Top N = 14 + psr`
    - lower-MDD alternative `Top N = 14 + psr + pfcr`
  - confirmed in the shared `Phase 21` frame that:
    - current anchor stays `real_money_candidate / paper_probation / review_required`
    - lower-MDD alternative still remains `production_candidate / watchlist / review_required`
  - created `backtest_reports/phase21/PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - created `backtest_reports/phase21/README.md`
  - synced `VALUE_STRICT_ANNUAL.md`, `VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`, `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`, phase21 TODO, and the report indexes
- Durable takeaway:
  - `Value` does not need a candidate replacement right now; the current anchor remains the practical reference point even in the integrated validation frame.

### 2026-04-16
- Ran the second actual `Phase 21` rerun pack for `Quality`.
- Changed:
  - reran:
    - current anchor `capital_discipline + LQD + trend on + regime off + Top N 12`
    - cleaner alternative `capital_discipline + SPY + trend on + regime off + Top N 12`
  - confirmed in the shared `Phase 21` frame that:
    - current anchor still remains the practical reference point
    - cleaner alternative still remains a comparison-only surface rather than a replacement
  - created `backtest_reports/phase21/PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - synced `QUALITY_STRICT_ANNUAL.md`, `QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md`, `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`, phase21 TODO, and the report indexes
- Durable takeaway:
  - `Quality` also does not need a candidate replacement right now; the `LQD` anchor remains the practical point, and the `SPY` version remains useful mainly as a cleaner comparison surface.

### 2026-04-17
- Ran the third actual `Phase 21` rerun pack for `Quality + Value`.
- Changed:
  - reran:
    - current strongest point `operating_margin + pcr + por + per + Top N 10`
    - lower-MDD alternative with the same factor set and `Top N 9`
  - confirmed in the shared `Phase 21` frame that:
    - current strongest point remains `real_money_candidate / small_capital_trial / review_required`
    - `Top N 9` has stronger raw metrics but still drops to `production_candidate / watchlist / review_required`
  - created `backtest_reports/phase21/PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - synced `QUALITY_VALUE_STRICT_ANNUAL.md`, `QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`, `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`, phase21 TODO, and the report indexes
- Durable takeaway:
  - `Quality + Value` remains the strongest blended representative anchor, but the very attractive `Top N 9` alternative still needs weaker-gate handling before it can replace the anchor.

### 2026-04-17
- Ran the `Phase 21` representative portfolio bridge validation.
- Changed:
  - rebuilt the `Load Recommended Candidates` source bundle from:
    - `Value` current anchor
    - `Quality` current anchor
    - `Quality + Value` current anchor
  - built the representative weighted portfolio with:
    - `33 / 33 / 34`
    - `Date Alignment = intersection`
  - validated saved portfolio replay by reconstructing the saved compare context and portfolio context
  - created `backtest_reports/phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md`
  - updated Phase 21 completion / next-phase docs and candidate summary
- Durable takeaway:
  - the portfolio bridge is reproducible and meaningful enough for Phase 22 portfolio-level candidate construction, but portfolio-level promotion semantics still need to be designed before treating it as a production candidate.

### 2026-04-17
- Refined `Phase 21` QA wording after checklist review.
- Changed:
  - added `Validation Frame` to the shared finance glossary
  - rewrote the Phase 21 plan wording around deferred Phase 18 structural backlog, current anchors, and lower-MDD rescue candidates in plainer language
  - updated the Phase 21 checklist so validation frame verification points directly to the glossary
- Durable takeaway:
  - Phase 21 manual QA should now read as a user-facing validation guide rather than an internal shorthand memo.

### 2026-04-17
- Clarified where to verify `Phase 21` family-level integrated rerun results during manual QA.
- Changed:
  - expanded `PHASE21_TEST_CHECKLIST.md` section 2 with direct links to the phase21 archive, the three family rerun reports, and the strategy hub / backtest log documents
  - recorded the clarification in the Phase 21 TODO board
- Durable takeaway:
  - family-level rerun QA should start from `.aiworkspace/note/finance/backtest_reports/phase21/README.md`, then inspect the `Value`, `Quality`, and `Quality + Value` rerun reports.

### 2026-04-17
- Refined `Phase 21` manual QA decision guidance and annual strict backtest log readability.
- Changed:
  - added 유지 / 교체 / 보류 판단 기준 to `PHASE21_TEST_CHECKLIST.md`
  - standardized the three annual strict backtest logs to read newest-first and end with a compact recent decision summary table
  - moved misplaced `2026-04-14` concentration-aware weighting entries in `Value` and `Quality + Value` logs back into date order
  - updated the shared backtest log template and indexes so future logs follow the same pattern
- Durable takeaway:
  - manual QA should use report interpretation plus gate status, not raw CAGR/MDD alone, when checking whether a candidate is maintained, replaced, or deferred.

### 2026-04-17
- Clarified `Phase 21` portfolio bridge validation locations during manual QA.
- Changed:
  - updated `PHASE21_TEST_CHECKLIST.md` section 3 to point to `PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md` as the official rerun report
  - separated the document report from the UI verification path:
    - `Weighted Portfolio Builder`
    - `Weighted Portfolio Result`
    - `Saved Portfolios`
    - `Replay Saved Portfolio`
  - recorded the clarification in the Phase 21 TODO board
- Durable takeaway:
  - `weighted portfolio / saved portfolio rerun report` should be read as the Phase 21 Markdown report, while the Streamlit UI is the optional replay/visual verification path.

### 2026-04-17
- Rewrote the `Phase 21` portfolio bridge validation report for readability.
- Changed:
  - restructured `PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md` around:
    - what the document is
    - the conclusion first
    - plain-language terms
    - why the three annual strict strategies were used
    - validation flow
    - weighted / saved replay results
    - what the result does and does not prove
    - Phase 22 questions
  - clarified that `FIRST_PASS` means first validation, not final portfolio recommendation
  - synced the Phase 21 archive README, report index, finance doc index, and TODO board
- Durable takeaway:
  - the portfolio bridge report should now read as a workflow validation report rather than an AI-looking result dump.

### 2026-04-17
- Aligned the `Phase 21` manual checklist with the rewritten portfolio bridge report.
- Changed:
  - updated `PHASE21_TEST_CHECKLIST.md` section 3 so QA follows the new report flow:
    - conclusion first
    - why the three strategies were grouped
    - validation flow
    - what the result does and does not prove
    - Phase 22 questions
  - recorded the checklist alignment in the Phase 21 TODO board
- Durable takeaway:
  - portfolio bridge QA now checks whether the report is clearly framed as workflow validation, not as final portfolio winner selection.

### 2026-04-17
- Reorganized the full `Phase 21` test checklist for readability.
- Changed:
  - rewrote `PHASE21_TEST_CHECKLIST.md` around a consistent structure:
    - what to verify
    - where to verify it
    - concrete checkbox items
  - converted scattered location notes into tables for validation frame, family reruns, portfolio bridge, and closeout
  - kept existing user QA checkmarks while making section 3 less noisy and easier to follow
  - synced the Phase 21 TODO board and finance doc index
- Durable takeaway:
  - Phase 21 QA should now be executable from top to bottom without asking where each evidence item lives.

### 2026-04-17
- Closed `Phase 21` after user checklist completion and opened `Phase 22`.
- Changed:
  - marked `PHASE21_CURRENT_CHAPTER_TODO.md` and `PHASE21_COMPLETION_SUMMARY.md` as `phase_complete / manual_validation_completed`
  - created the `Phase 22 Portfolio-Level Candidate Construction` phase bundle with the repo-local bootstrap helper
  - rewrote the Phase 22 plan from template text into a plain-language kickoff document
  - created `PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md`
  - added `Portfolio-Level Candidate`, `Portfolio Bridge`, `Saved Portfolio Replay`, and `Date Alignment` to the shared glossary
  - synced `MASTER_PHASE_ROADMAP.md` and `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - Phase 22 is now active, and the immediate next work is to turn the Phase 21 `33 / 33 / 34` portfolio bridge into a controlled baseline portfolio candidate pack rather than treating it as a final winner.

### 2026-04-17
- Completed the first `Phase 22` baseline portfolio candidate pack report.
- Changed:
  - created `backtest_reports/phase22/README.md`
  - created `backtest_reports/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md`
  - clarified that the `Phase 21` `33 / 33 / 34` label is a near-equal shorthand, while the saved definition is `[33.33, 33.33, 33.33]` normalized to equal thirds
  - fixed the baseline portfolio status as `baseline_candidate / portfolio_watchlist / not_deployment_ready`
  - reviewed `CURRENT_CANDIDATE_REGISTRY.jsonl`; validation passes, but no append was made because portfolio-level candidate registry semantics are not defined yet
  - synced Phase 22 TODO/checklist, roadmap, finance doc index, backtest report index, and current practical candidate summary
- Durable takeaway:
  - `phase22_annual_strict_equal_third_baseline_v1` is now the first portfolio-level baseline candidate pack, but not a final portfolio winner.

### 2026-04-17
- Completed the second `Phase 22` benchmark / guardrail / weight-scope work unit.
- Changed:
  - created `PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md`
  - set the primary portfolio benchmark to `phase22_annual_strict_equal_third_baseline_v1`
  - kept `SPY` as market context rather than the Phase 22 primary gate
  - clarified that component benchmarks remain component-level quality checks, not portfolio-level benchmarks
  - defined portfolio-level guardrail as report-level warning, not an actual trading rule
  - narrowed next weight alternatives to `25 / 25 / 50` and `40 / 40 / 20`
  - added `Portfolio-Level Benchmark`, `Portfolio-Level Guardrail`, and `Weight Alternative` to the glossary
  - synced Phase 22 TODO/checklist, roadmap, finance doc index, and backtest report index
- Durable takeaway:
  - the next actual validation step is no longer open-ended; rerun only the two scoped weight alternatives against the equal-third baseline.

### 2026-04-17
- Completed the `Phase 22` weight alternative first-pass rerun.
- Changed:
  - reran the saved portfolio compare context for `Value / Quality / Quality + Value` strict annual anchors
  - compared official equal-third baseline `[33.33, 33.33, 33.33]` against `25 / 25 / 50` and `40 / 40 / 20`
  - created `PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - reconciled the earlier `33 / 33 / 34` Phase 21 near-equal metric with the Phase 22 official equal-third baseline metric
  - updated the Phase 22 TODO, checklist, completion summary, next-phase prep, roadmap, finance doc index, and backtest report index
- Durable takeaway:
  - `25 / 25 / 50` improves raw return but creates `Quality + Value` concentration, while `40 / 40 / 20` lowers drawdown only slightly while giving up CAGR; equal-third remains the Phase 22 primary portfolio baseline.

### 2026-04-17
- Prepared `Phase 22` for manual validation.
- Changed:
  - marked the Phase 22 TODO board as `manual_validation_ready`
  - finalized the Phase 22 checklist around portfolio candidate semantics, baseline report, saved replay, benchmark / guardrail policy, and weight alternative rerun
  - synced the completion summary, next-phase preparation, roadmap, and finance doc index with the manual QA handoff state
- Durable takeaway:
  - Phase 22 implementation/reporting work is ready for user checklist QA; the next decision is closeout vs one more diversified-component portfolio check.

### 2026-04-18
- Polished the `Phase 22` plan and checklist entry point during manual QA.
- Changed:
  - rewrote `PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md` around purpose, necessity, minimum candidate conditions, actual execution order, and checklist usage
  - removed the duplicated feel between `목적` and `쉽게 말하면` by combining the explanation into `목적: 쉽게 말하면`
  - updated `PHASE22_TEST_CHECKLIST.md` section 1 so the user can see exactly which document sections to read and what each checkbox means
  - synced the Phase 22 TODO board and finance doc index
- Durable takeaway:
  - Phase 22 QA should now start from a clearer orientation document, not a phase memo that expects prior chat context.

### 2026-04-18
- Clarified the `Phase 22` development-validation boundary during manual QA.
- Changed:
  - updated the Phase 22 plan to state that the phase is not selecting a live investment portfolio
  - clarified that `Value / Quality / Quality + Value` are representative fixtures for portfolio workflow validation, not a final recommended allocation
  - clarified that the equal-third baseline is a development-validation comparison baseline, not an investment benchmark
  - updated the Phase 22 baseline report and checklist with the same boundary
- Durable takeaway:
  - Phase 22 should be read as portfolio-construction workflow validation for the quant program, not as final portfolio research or live-deployment approval.

### 2026-04-18
- Refreshed the master roadmap after the user identified phase drift risk.
- Changed:
  - added a product development direction section to `MASTER_PHASE_ROADMAP.md`
  - fixed the default roadmap stance as development-first, not investment-analysis-first
  - clarified that user-requested backtests / analysis can still be run during QA, but should be recorded as explicit analysis rather than phase direction drift
  - realigned `Phase 23~25` toward quarterly / alternate cadence productionization, new strategy implementation bridge, and validation / pre-live scaffolding
  - synced Phase 22 next-phase prep, completion summary, TODO, checklist, doc index, and glossary terms
- Durable takeaway:
  - After Phase 22 QA, the default next move is to close the portfolio workflow development-validation phase and return to core product implementation, starting with quarterly / alternate cadence productionization.

### 2026-04-19
- Closed `Phase 22` after user checklist completion.
- Changed:
  - accepted the completed `PHASE22_TEST_CHECKLIST.md` manual QA state
  - marked `PHASE22_CURRENT_CHAPTER_TODO.md` and `PHASE22_COMPLETION_SUMMARY.md` as `phase complete / manual_validation_completed`
  - refreshed `PHASE22_NEXT_PHASE_PREPARATION.md` so it reads as a Phase 23 handoff rather than a pending QA draft
  - synced `MASTER_PHASE_ROADMAP.md` and `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - Phase 22 is now closed as portfolio workflow development validation, not as investment portfolio approval. The next default main phase is `Phase 23 Quarterly And Alternate Cadence Productionization`.

### 2026-04-19
- Advanced `Phase 23` representative quarterly smoke validation.
- Changed:
  - ran DB-backed smoke runs for `Quality / Value / Quality + Value` strict quarterly prototypes with `AAPL / MSFT / GOOG`, 2021-01-01~2024-12-31, and non-default portfolio handling contracts
  - found that common result bundle meta did not preserve `weighting_mode`, `rejected_slot_handling_mode`, `rejected_slot_fill_enabled`, and `partial_cash_retention_enabled`
  - fixed `build_backtest_result_bundle()` so portfolio handling contract meta is preserved for history / load-into-form workflows
  - created `PHASE23_QUARTERLY_CONTRACT_SMOKE_VALIDATION_FIRST_PASS.md`
  - synced Phase 23 TODO, completion summary, checklist, finance analysis, and backtest report index
- Durable takeaway:
  - quarterly strict family now passes DB-backed smoke validation for portfolio handling contract delivery and meta preservation; remaining Phase 23 validation is UI-level history / saved replay confirmation.

### 2026-04-19
- Prepared `Phase 23` for manual validation.
- Changed:
  - added quarterly portfolio handling contract fields to persisted backtest history records
  - updated history payload rebuild so `Run Again` and `Load Into Form` preserve `weighting_mode`, `rejected_slot_handling_mode`, and related flags
  - updated saved portfolio strategy overrides so `Replay Saved Portfolio` preserves quarterly rejected-slot handling semantics
  - verified result bundle meta -> history record -> history payload -> saved portfolio override roundtrip with a representative quarterly smoke bundle
  - created `PHASE23_HISTORY_AND_SAVED_REPLAY_CONTRACT_ROUNDTRIP_THIRD_WORK_UNIT.md`
  - synced Phase 23 TODO, checklist, completion summary, next-phase prep, roadmap, finance analysis, and doc index
- Durable takeaway:
  - Phase 23 code-level work is now manual-validation-ready; the remaining gate is user UI QA through `PHASE23_TEST_CHECKLIST.md`.

### 2026-04-19
- Refined `Phase 23` compare QA UX after user checklist feedback.
- Changed:
  - confirmed the Compare variant refresh issue came from `Variant` selectboxes living inside `st.form()`
  - moved `Quality / Value / Quality + Value` compare variant selectors outside the form into a dedicated `Strategy Variants` section
  - kept `Advanced Inputs > Strategy-Specific Advanced Inputs` as the detailed settings area for the currently selected variant
  - avoided the previously rejected Apply/Refresh button pattern
  - rewrote unclear Phase 23 checklist items around concrete screen locations: `Data Requirements`, `Statement Shadow Coverage Preview`, `Universe Contract`, and `Strategy Variants`
  - created `PHASE23_COMPARE_VARIANT_IMMEDIATE_REFRESH_FOURTH_WORK_UNIT.md`
- Durable takeaway:
  - Annual / Quarterly changes in Compare should now immediately refresh the lower advanced option UI without extra buttons, and the checklist is more directly testable.

### 2026-04-19
- Flattened the `Phase 23` compare input layout after follow-up UX feedback.
- Changed:
  - removed the compare `st.form()` wrapper and `Advanced Inputs` expander from the compare configuration area
  - moved `Start Date`, `End Date`, `Timeframe`, and `Option` into a shared `Compare Period & Shared Inputs` section
  - moved Annual / Quarterly variant selectors into each `Quality / Value / Quality + Value` strategy box
  - replaced strategy-level expanders with border boxes while keeping lower `Overlay`, `Portfolio Handling`, real-money, and guardrail expanders intact
  - kept a single `Run Strategy Comparison` action button and avoided the rejected Apply / Refresh pattern
  - synced the Phase 23 checklist, fourth work-unit note, TODO board, completion summary, next-phase prep, roadmap, doc index, finance analysis, and question log
- Durable takeaway:
  - Compare QA should now read as common execution inputs first, then one visible box per selected strategy, with variant selection and settings in the same box.

### 2026-04-19
- Tightened `Phase 23` compare/history QA details after checklist feedback.
- Changed:
  - wrapped strict quarterly compare `Trend Filter` and `Market Regime` inputs inside the same `Overlay` expander used by annual strict compare paths
  - kept `Portfolio Handling & Defensive Rules` as the adjacent lower expander for quarterly rejected-slot, weighting, and risk-off settings
  - changed `Back To History` after `Load Into Form` to use a panel-switch callback so the History panel is requested before the radio widget renders
  - rewrote Phase 23 checklist section 3 to explain where to verify saved compare context, saved portfolio context, history run, load-into-form, run-again, and replay saved portfolio
- Durable takeaway:
  - Quarterly compare QA now has the same top-level section rhythm as annual strict, and the checklist distinguishes history rerun from saved portfolio replay.

### 2026-04-19
- Refined the finance phase checklist writing rule after Phase 23 QA feedback.
- Changed:
  - removed the standalone `용어 기준` block from `PHASE23_TEST_CHECKLIST.md`
  - moved the relevant screen paths directly into each section 3 checkbox
  - updated `PHASE_TEST_CHECKLIST_TEMPLATE.md` so future checklists avoid separate glossary-like blocks and instead write exact UI paths inside checklist items
  - updated `FINANCE_DOC_INDEX.md` so the checklist-template entry mentions the same location-first rule
  - synced `PHASE23_CURRENT_CHAPTER_TODO.md` with the checklist wording cleanup
- Durable takeaway:
  - Future finance checklists should be action/location-first: each checkbox should say where to go and what to verify.

### 2026-04-20
- Closed `Phase 23` and opened `Phase 24`.
- Changed:
  - accepted the user's Phase 23 completion signal and marked the remaining checklist item complete
  - updated `PHASE23_CURRENT_CHAPTER_TODO.md`, `PHASE23_COMPLETION_SUMMARY.md`, and `PHASE23_NEXT_PHASE_PREPARATION.md` to `phase complete / manual_validation_completed`
  - bootstrapped `phase24` docs from the finance phase bundle helper
  - rewrote the Phase 24 plan, TODO, checklist, completion draft, next-phase draft, and first work-unit note for the new strategy expansion / research-to-implementation bridge
  - selected `Global Relative-Strength Allocation With Trend Safety Net` as the first implementation candidate because it is price-only, ETF-based, monthly, and compatible with the current DB-backed strategy infrastructure
  - synced `MASTER_PHASE_ROADMAP.md` and `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - Phase 24 is now active as a development phase for adding a new strategy family, not as an investment-performance analysis phase.

### 2026-04-20
- Ran a user-requested `GTAA` expanded-universe follow-up.
- Changed:
  - re-tested the existing compact `SPY / QQQ / GLD / IEF` `Top = 2` candidate through the latest DB date `2026-04-17`
  - added `TLT` to form a clean 6 ETF core: `SPY / QQQ / GLD / IEF / LQD / TLT`
  - found a new expanded `Top = 1`, `Interval = 8`, `1M / 3M / 6M` candidate with `21.50% CAGR`, `-6.49% MDD`, and `real_money_candidate / paper_probation / paper_only`
  - confirmed the same 6 ETF core with `Top = 2`, `Interval = 4`, `1M / 3M / 6M` remains `production_candidate / watchlist / watchlist_only`
  - documented the result in `GTAA_EXPANDED_UNIVERSE_FOLLOWUP_20260420.md` and synced the GTAA strategy hub, backtest log, report index, current candidate summary, and candidate registry
- Durable takeaway:
  - ticker breadth improved the aggressive GTAA paper candidate, but the balanced 2-holding representative remains the compact `SPY / QQQ / GLD / IEF` candidate until expanded `Top = 2` validation improves.

### 2026-04-20
- Advanced `Phase 24` first new strategy implementation.
- Changed:
  - added `Global Relative Strength` core simulation in `finance.strategy`
  - added DB-backed helper/defaults in `finance.sample`
  - added web runtime wrapper `run_global_relative_strength_backtest_from_db`
  - verified targeted `py_compile`, synthetic strategy smoke, runtime import smoke, and DB-backed smoke run
  - created `PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md`
  - synced Phase 24 TODO, completion draft, next-phase prep, roadmap, doc index, backtest report index, and finance analysis
- Durable takeaway:
  - `Global Relative Strength` is now implemented at core/runtime level, but it is not yet exposed in `Backtest` UI, compare, history, or saved replay.

### 2026-04-20
- Reorganized the `FINANCE_COMPREHENSIVE_ANALYSIS.md` detailed implementation memo governance.
- Changed:
  - clarified that `3-3. 상세 구현 메모` is a legacy archive, not the current source of truth
  - added a management policy for where future current-state, phase, backtest, glossary, candidate, and workflow records should live
  - added a short future-record template with date, phase, category, affected area, source, and re-review condition
  - added a topic index so the long legacy memo can be searched without treating every old note as current behavior
- Durable takeaway:
  - Future finance implementation notes should not be appended indefinitely to `3-3`; new details should be routed to the correct canonical document and only summarized in the comprehensive analysis when they affect current system behavior.

### 2026-04-20
- Established the first finance code analysis documentation system.
- Changed:
  - created `.aiworkspace/note/finance/docs/architecture/` as the developer-facing place for durable code flow documents
  - added flow docs for backtest runtime, data/DB pipeline, web backtest UI, strategy implementation, and automation scripts
  - updated `FINANCE_COMPREHENSIVE_ANALYSIS.md` so it remains the high-level map and points detailed code flow readers to `docs/architecture/`
  - updated `FINANCE_DOC_INDEX.md`, `AGENTS.md`, and the active `finance-doc-sync` skill guidance to include the new code analysis update rule
- Durable takeaway:
  - Future code changes should update `docs/architecture/` only when the durable code flow changes; small copy edits, one-off results, and phase status updates should stay out of those developer flow documents.

### 2026-04-20
- Slimmed `FINANCE_COMPREHENSIVE_ANALYSIS.md` now that `docs/architecture/` exists.
- Changed:
  - reduced section 4 from detailed file-by-file code notes to a concise system layer table
  - reduced section 12 from long strategy/contract implementation history to a compact code entrypoint map
  - reduced section 18 to a short automation baseline table
  - moved durable strategy contract and runtime interpretation details into `docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md` and `docs/architecture/BACKTEST_RUNTIME_FLOW.md`
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` should now stay as the high-level map, while detailed developer flow should live under `.aiworkspace/note/finance/docs/architecture/`.

### 2026-04-20
- Established the first finance data architecture documentation system.
- Changed:
  - created `.aiworkspace/note/finance/data_architecture/` as the place for data flow, DB schema map, table semantics, and PIT/data-quality notes
  - moved the detailed meaning of sections 5~7 out of `FINANCE_COMPREHENSIVE_ANALYSIS.md` into dedicated data architecture documents
  - reduced `FINANCE_COMPREHENSIVE_ANALYSIS.md` sections 5~7 to high-level flow, DB, and table-semantics summaries
  - updated `FINANCE_DOC_INDEX.md`, `AGENTS.md`, and the active `finance-doc-sync` skill guidance to include the new data architecture update rule
- Durable takeaway:
  - Future DB/table/source-of-truth or PIT/data-quality meaning changes should update `data_architecture/`, while the comprehensive analysis should keep only the top-level data map.

### 2026-04-20
- Refreshed `FINANCE_COMPREHENSIVE_ANALYSIS.md` sections 8~18 using the current finance documentation set.
- Changed:
  - updated sections 8~9 from older ETF/sample-strategy framing to the current product / strategy / portfolio / pre-live layer view
  - condensed sections 10~11 into current limitation and data-quality summaries that point to `data_architecture/`
  - rewrote section 12 as a code entrypoint map that points to `docs/architecture/`
  - updated sections 13~18 to reflect the current development boundary, Phase 25 pre-live direction, future data priorities, and automation / persistence baseline
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` now acts as a high-level orientation map for the current product, while detailed code, DB, phase, and result records are delegated to their canonical sub-documents.

### 2026-04-20
- Tightened the update policy for `FINANCE_COMPREHENSIVE_ANALYSIS.md`.
- Changed:
  - updated `AGENTS.md` so `FINANCE_COMPREHENSIVE_ANALYSIS.md` is reviewed after finance changes but updated only when the high-level current-state map changes
  - updated `FINANCE_COMPREHENSIVE_ANALYSIS.md` and `FINANCE_DOC_INDEX.md` to state that one-off results, phase progress, detailed call flows, and table-level semantics belong in the specialized docs
  - updated the active `finance-doc-sync` skill with the same rule
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` should show the big picture of the current system, not absorb every implementation detail or experiment record.

### 2026-04-20
- Split the legacy detailed implementation memo out of `FINANCE_COMPREHENSIVE_ANALYSIS.md`.
- Changed:
  - moved the long former `3-3. 상세 구현 메모` into `.aiworkspace/note/finance/archive/FINANCE_COMPREHENSIVE_ANALYSIS_LEGACY_IMPLEMENTATION_NOTES_20260420.md`
  - replaced the root `3-3` section with a short archive pointer and future record-routing rule
  - updated `FINANCE_DOC_INDEX.md` and `.aiworkspace/note/finance/archive/README.md` so the archive is discoverable
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` is now much closer to a current-state map, while legacy implementation history remains preserved but out of the main reading path.

### 2026-04-20
- Clarified the finance product goal versus current phase boundary.
- Changed:
  - updated `FINANCE_COMPREHENSIVE_ANALYSIS.md` so the project goal is not described as merely data collection and backtesting
  - clarified that the long-term target is an evidence-based investment candidate recommendation and portfolio construction proposal program
  - updated `MASTER_PHASE_ROADMAP.md`, `AGENTS.md`, and the active `finance-doc-sync` skill to separate final product target from near-term development / validation phase execution
- Durable takeaway:
  - Strong backtest results are not automatic live recommendations, but the product being built is intended to support investment candidate and portfolio proposal workflows after sufficient validation.

### 2026-04-21
- Organized loose root finance Markdown documents into purpose-specific folders.
- Changed:
  - moved operations / runtime / registry / ingestion reference docs under `.aiworkspace/note/finance/operations/`
  - moved daily market update notes under `.aiworkspace/note/finance/operations/daily_market_update/`
  - moved research reference docs under `.aiworkspace/note/finance/researches/`
  - moved support-track discussion docs under `.aiworkspace/note/finance/support_tracks/`
  - moved the legacy backtest refinement flow guide under `.aiworkspace/note/finance/docs/architecture/`
  - updated `FINANCE_DOC_INDEX.md`, active links, and added folder README files
- Durable takeaway:
  - `.aiworkspace/note/finance/` root should now stay focused on top-level maps, active logs, glossary, and templates.

### 2026-04-21
- Standardized phase status terminology for finance roadmap/index documents.
- Changed:
  - added a `Phase 상태값 읽는 법` section to `FINANCE_DOC_INDEX.md`
  - initially normalized recent phase status labels to underscore-based canonical values such as `phase_complete / manual_validation_completed`
  - aligned the `MASTER_PHASE_ROADMAP.md` current-position status summary with the same labels
  - added `Phase Status` to `FINANCE_TERM_GLOSSARY.md`
  - updated `AGENTS.md` and the active `finance-doc-sync` skill so future phase indexes use the same status vocabulary
- Durable takeaway:
  - This was immediately refined into the split-column progress / validation model below, because that is easier to read than one combined status string.

### 2026-04-21
- Refined the phase status model to split progress status from validation status.
- Changed:
  - updated `FINANCE_DOC_INDEX.md` so the phase quick map now has separate `진행 상태`, `검증 상태`, and `다음 확인` columns
  - updated `MASTER_PHASE_ROADMAP.md` current-position summary to the same split-column model
  - updated `FINANCE_TERM_GLOSSARY.md`, `AGENTS.md`, and the active `finance-doc-sync` skill to prefer split phase status labels
  - clarified that `first_chapter_completed` is legacy partial-completion wording, not a signal to introduce a formal chapter hierarchy
- Durable takeaway:
  - Future phase management should stay phase-based, not chapter-based, and should separate work progress from QA/validation status.

### 2026-04-21
- Advanced Phase 25 from boundary definition into Pre-Live candidate record persistence.
- Changed:
  - added `.aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py`
  - defined `.aiworkspace/note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` as the append-only Pre-Live operating-state registry
  - added `.aiworkspace/note/finance/operations/PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md`
  - added `PHASE25_PRE_LIVE_CANDIDATE_RECORD_CONTRACT_SECOND_WORK_UNIT.md`
  - updated Phase 25 plan, TODO, checklist, completion draft, next-phase draft, roadmap, doc index, comprehensive analysis, automation guide, AGENTS, and active finance-doc-sync guidance
- Validation:
  - `py_compile` passed for the new pre-live registry helper and hygiene helper
  - `manage_pre_live_candidate_registry.py validate` passes with an empty registry
  - `manage_current_candidate_registry.py validate` still passes for existing current candidate records
- Durable takeaway:
  - `CURRENT_CANDIDATE_REGISTRY.jsonl` defines the candidate; `PRE_LIVE_CANDIDATE_REGISTRY.jsonl` records how that candidate is handled before live use.

### 2026-04-21
- Advanced Phase 25 into the operator review workflow work unit.
- Changed:
  - added `PHASE25_OPERATOR_REVIEW_WORKFLOW_THIRD_WORK_UNIT.md`
  - extended `manage_pre_live_candidate_registry.py` with `draft-from-current <registry_id>`
  - mapped current candidate Real-Money signals into default Pre-Live statuses:
    `paper_probation -> paper_tracking`, `watchlist -> watchlist`, blockers -> `hold`, reject/fail signals -> `reject`, otherwise `re_review`
  - kept the workflow safe by making draft output the default and requiring `--append` for actual registry writes
  - updated Phase 25 TODO, checklist, completion draft, next-phase draft, operations guide, automation guide, doc index, comprehensive analysis, AGENTS, and active finance-doc-sync guidance
- Validation:
  - `py_compile` passed for `manage_pre_live_candidate_registry.py`
  - `draft-from-current value_current_anchor_top14_psr` outputs a valid `paper_tracking` draft
  - `draft-from-current value_lower_mdd_near_miss_pfcr` outputs a valid `watchlist` draft
- Durable takeaway:
  - Phase 25 now has a helper/report-based entry point for converting current candidates into Pre-Live operating drafts, without automatically approving or saving anything.

### 2026-04-21
- Added the Phase 25 Pre-Live Review UI entry point.
- Changed:
  - added `Pre-Live Review` as a fourth Backtest panel
  - added a current-candidate-to-Pre-Live review UI in `app/web/pages/backtest.py`
  - users can select a current candidate, review Real-Money signals, choose a Pre-Live status, edit operator reason / next action / review date, inspect the JSON draft, and save explicitly
  - saved active records are shown in the same panel's `Pre-Live Registry` tab
  - added `PHASE25_PRE_LIVE_REVIEW_UI_FOURTH_WORK_UNIT.md`
  - updated Phase 25 TODO, checklist, completion/next docs, roadmap, doc index, comprehensive analysis, Pre-Live guide, and web UI flow docs
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv/bin/python` import of `app.web.pages.backtest` passed
- Durable takeaway:
  - Phase 25 implementation is now ready for user manual QA. The UI still does not enable live trading; it only records pre-live operating state.

### 2026-04-21
- Clarified the Phase 25 Real-Money vs Pre-Live boundary after user QA feedback.
- Changed:
  - updated the first Phase 25 work-unit document so Pre-Live is not described as status labels only
  - defined the Pre-Live "next action record" as an action package:
    `operator_reason`, `next_action`, `review_date`, `tracking_plan.cadence`, `tracking_plan.stop_condition`, `tracking_plan.success_condition`, and supporting docs
  - updated the Phase 25 plan, Pre-Live registry guide, glossary, and checklist to say that status alone is not the distinguishing feature
- Durable takeaway:
  - `pre_live_status` can resemble Real-Money promotion / shortlist labels. The actual Pre-Live distinction is the recorded operating plan for what to check next, when to review, and when to stop or advance.

### 2026-04-21
- Closed Phase 25 after user manual QA completion.
- Changed:
  - updated Phase 25 TODO, completion summary, next-phase preparation, and checklist to `complete / manual_qa_completed`
  - synced `MASTER_PHASE_ROADMAP.md`, `FINANCE_DOC_INDEX.md`, and `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - recorded that no additional `AGENTS.md` or skill guidance change was needed at closeout because Pre-Live registry and QA closeout rules were already reflected
- Validation:
  - Phase 25 checklist was completed by the user before closeout
- Durable takeaway:
  - Phase 25 is closed as a Pre-Live operating-record workflow, not as live trading or automatic investment approval.

### 2026-04-21
- Opened Phase 26 and documented the Phase 26~30 roadmap direction.
- Changed:
  - created the Phase 26 document bundle for `Foundation Stabilization And Backlog Rebase`
  - added the first Phase 26 work-unit document for phase status and backlog rebase
  - updated `MASTER_PHASE_ROADMAP.md` with Phase 26~30:
    Phase 26 foundation stabilization, Phase 27 data integrity, Phase 28 strategy family parity, Phase 29 candidate review workflow, Phase 30 portfolio proposal / pre-live monitoring
  - updated `FINANCE_DOC_INDEX.md`, `FINANCE_COMPREHENSIVE_ANALYSIS.md`, and `FINANCE_TERM_GLOSSARY.md`
- Durable takeaway:
  - Live Readiness / Final Approval is intentionally deferred until after Phase 30. Phase 26 starts by stabilizing backlog and foundation gaps before new product expansion.

### 2026-04-21
- Completed Phase 26 implementation handoff.
- Changed:
  - added `PHASE26_BACKLOG_REBASE_AND_FOUNDATION_GAP_MAP.md`
  - reclassified Phase 8, 9, 12~15, and 18 as `complete / superseded_by_later_phase`
  - separated Phase 27 data integrity, Phase 28 strategy parity, Phase 29 candidate review, and Phase 30 portfolio proposal inputs
  - updated roadmap, doc index, glossary, comprehensive analysis, AGENTS, and active finance-doc-sync guidance for the new validation label
  - finalized the Phase 26 checklist for user QA
- Validation:
  - documentation consistency and hygiene checks are the relevant checks for this document-only phase
- Durable takeaway:
  - No old pending phase is an immediate blocker before Phase 27. Old pending checklists are now historical references or later-phase inputs, not active QA gates.

### 2026-04-22
- Clarified Phase 26 QA wording and next-phase handoff format.
- Changed:
  - replaced the ambiguous Phase 26 term `input` with user-facing wording: `다룰 주제`
  - added a short plain-language Phase 18 explanation to `PHASE26_BACKLOG_REBASE_AND_FOUNDATION_GAP_MAP.md`
  - expanded `PHASE26_NEXT_PHASE_PREPARATION.md` with a `다음 phase에서 실제로 할 작업` section for Phase 27
  - updated the phase bundle helper, checklist template, and `AGENTS.md` so future next-phase handoff docs explain both why the next phase is natural and what work it will actually do
- Durable takeaway:
  - Future next-phase preparation docs should not stop at "why next"; they should also show the concrete work the user should expect in the next phase.

### 2026-04-22
- Closed Phase 26 after user manual QA completion.
- Changed:
  - marked `PHASE26_TEST_CHECKLIST.md` final closeout items as completed
  - updated Phase 26 TODO, completion summary, next-phase preparation, roadmap, doc index, and comprehensive analysis to `complete / manual_qa_completed`
- Validation:
  - Phase 26 checklist was completed by the user before closeout
- Durable takeaway:
  - Phase 26 is closed. Phase 27 can now open as the data integrity / backtest trust layer.

### 2026-04-22
- Opened Phase 27 and implemented the first data-trust visibility unit.
- Changed:
  - created the Phase 27 document bundle for `Data Integrity And Backtest Trust Layer`
  - added `Data Trust Summary` to the latest Backtest result view
  - added requested vs actual result end, result row count, excluded ticker, malformed price row, and price freshness summary metadata to backtest result bundles
  - connected Global Relative Strength to the same price-freshness preflight used by strict annual workflows, with Korean warning copy for stale / mismatched ticker data
  - updated roadmap, document index, comprehensive analysis, code-flow notes, and data-quality notes for the new Phase 27 trust-layer behavior
- Validation:
  - `python3 -m py_compile app/web/runtime/backtest.py app/web/pages/backtest.py` passed
  - `.venv/bin/python` import of `app.web.runtime.backtest` and `app.web.pages.backtest` passed
  - `git diff --check` passed
- Durable takeaway:
  - Phase 27 starts by making backtest data boundaries visible before deeper strategy work: users should see when the requested end date, actual result end date, stale ticker data, excluded tickers, or malformed rows affect the interpretation of a run.

### 2026-04-22
- Closed Phase 27 after user manual QA completion.
- Changed:
  - marked Phase 27 TODO, completion summary, next-phase preparation, and checklist as `complete / manual_qa_completed`
  - synced `MASTER_PHASE_ROADMAP.md`, `FINANCE_DOC_INDEX.md`, and `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - kept Phase 28 handoff focused on strategy family parity, cadence completion, and family-level UX / metadata consistency
- Validation:
  - Phase 27 checklist was completed by the user before closeout
- Durable takeaway:
  - Phase 27 is closed. `Data Trust Summary`, `price_freshness`, excluded ticker details, and result-window metadata are now the baseline trust-layer concepts for later strategy family parity work.

### 2026-04-22
- Opened Phase 28 and implemented the first strategy-family parity visibility unit.
- Changed:
  - created the Phase 28 document bundle for `Strategy Family Parity And Cadence Completion`
  - added `Strategy Capability Snapshot` to `Backtest > Single Strategy`
  - added the same capability snapshot inside selected strategy boxes in `Compare & Portfolio Builder`
  - documented annual strict, quarterly prototype, Global Relative Strength, GTAA, and ETF strategy support differences
  - updated roadmap, document index, comprehensive analysis, web UI flow docs, and Phase 28 checklist draft
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` candidate review note helper smoke passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - finance refinement hygiene check passed
  - `git diff --check` passed
- Durable takeaway:
  - Phase 28 starts by making strategy family differences visible before adding or equalizing more functionality. The current focus is "what does this strategy currently support?" rather than new strategy discovery.

### 2026-04-22
- Implemented Phase 28 history replay / load parity visibility.
- Changed:
  - added `History Replay / Load Parity Snapshot` under `Backtest > History > Selected History Run`
  - expanded new backtest history records with result-window, price freshness, excluded ticker, malformed price row, and guardrail reference metadata
  - documented the second Phase 28 work unit and synced roadmap, index, comprehensive analysis, and code-flow notes
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py app/web/runtime/history.py` passed
- Durable takeaway:
  - Phase 28 now lets users inspect whether a saved history run contains the key settings needed for `Load Into Form` or `Run Again` before pressing either action.

### 2026-04-22
- Implemented Phase 28 saved portfolio replay / load parity visibility.
- Changed:
  - added `Saved Portfolio Replay / Load Parity Snapshot` under `Backtest > Compare & Portfolio Builder > Saved Portfolios`
  - added a compact `Strategy Override Summary` for saved portfolio records
  - preserved `weights_percent` in saved portfolio replay history context
  - documented the third Phase 28 work unit and synced roadmap, index, comprehensive analysis, and code-flow notes
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` saved portfolio parity helper smoke passed
- Durable takeaway:
  - Saved Portfolio is now easier to inspect before replay: users can see whether compare inputs, strategy overrides, weights, and date alignment are present before loading or rerunning.

### 2026-04-22
- Extended Phase 28 Data Trust visibility into compare, weighted portfolio, and saved replay flows.
- Changed:
  - added a `Data Trust` tab to `Strategy Comparison`
  - added a `Component Data Trust` tab to `Weighted Portfolio Result`
  - persisted strategy/component data trust rows in compare and weighted portfolio history context
  - documented the fourth Phase 28 work unit and synced roadmap, index, comprehensive analysis, and code-flow notes
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` strategy data trust helper smoke passed
- Durable takeaway:
  - Compare and weighted portfolio results now expose the component data conditions behind the result, so users can distinguish performance differences from date-window or data-quality differences.

### 2026-04-23
- Completed Phase 28 Real-Money / Guardrail parity visibility.
- Changed:
  - added a `Real-Money / Guardrail` tab to Strategy Comparison
  - added `History Real-Money / Guardrail Scope` under selected history records
  - added `Saved Portfolio Real-Money / Guardrail Scope` under saved portfolio replay/load parity
  - documented the fifth Phase 28 work unit and moved Phase 28 to implementation complete / manual QA pending
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` Real-Money / Guardrail parity helper smoke passed
  - `git diff --check` passed
  - finance refinement hygiene check passed
- Durable takeaway:
  - Phase 28 does not force annual strict Real-Money / Guardrail behavior onto quarterly prototype or ETF strategies. It now shows each strategy family's intended validation scope before compare, history replay, or saved portfolio replay.

### 2026-04-23
- Fixed Saved Portfolio name suggestion refresh during Phase 28 QA.
- Changed:
  - `Save This Weighted Portfolio` now derives the default portfolio name from the latest weighted portfolio strategy names and weights
  - the `Portfolio Name` input resets when the weighted portfolio strategy / weight / date alignment signature changes
  - manual name edits are preserved while the same weighted portfolio result is still active
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` weighted portfolio name suggestion helper smoke passed
  - `git diff --check` passed
- Durable takeaway:
  - Saving a new weighted portfolio after rebuilding with different strategies should no longer retain the previous portfolio name by accident.

### 2026-04-23
- Closed Phase 28 after user manual QA completion.
- Changed:
  - marked the remaining Phase 28 checklist items as completed based on the user's QA completion confirmation
  - moved Phase 28 status to `complete` / `manual_qa_completed`
  - synced Phase 28 closeout summary, next-phase handoff, master roadmap, document index, and comprehensive analysis
- Validation:
  - finance refinement hygiene check passed
  - `git diff --check` passed
- Durable takeaway:
  - Phase 28 is closed. The next planned development phase is Phase 29 `Candidate Review And Recommendation Workflow`.

### 2026-04-23
- Opened Phase 29 and implemented the first Candidate Review workflow unit.
- Changed:
  - bootstrapped the Phase 29 document bundle for `Candidate Review And Recommendation Workflow`
  - added `Backtest > Candidate Review` as a dedicated panel
  - added a candidate review board for active `CURRENT_CANDIDATE_REGISTRY.jsonl` rows
  - added candidate detail inspection, suggested next step, and Pre-Live Review handoff
  - reused current candidate compare re-entry inside Candidate Review
  - synced roadmap, document index, comprehensive analysis, web UI flow docs, glossary, and README
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` import smoke for candidate review helper columns passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - finance refinement hygiene check passed after root log sync
  - `git diff --check` passed
- Durable takeaway:
  - Phase 29 starts by making current candidates readable as review objects before sending them to compare or Pre-Live. This is a candidate review workflow, not live approval.

### 2026-04-23
- Implemented Phase 29 result-to-candidate-review handoff.
- Changed:
  - added `Candidate Review Handoff` under `Latest Backtest Run`
  - added `Review As Candidate Draft` to selected history run actions
  - added `Candidate Intake Draft` tab under `Backtest > Candidate Review`
  - candidate drafts now show suggested record type, result snapshot, Real-Money signal, data trust snapshot, and settings snapshot
  - documented the second Phase 29 work unit and synced roadmap, index, glossary, web UI flow, current candidate registry guide, and README
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` helper smoke passed
- Durable takeaway:
  - Latest/history results can now be reviewed as candidate drafts without automatically writing to `CURRENT_CANDIDATE_REGISTRY.jsonl`.

### 2026-04-23
- Implemented Phase 29 Candidate Review Note workflow.
- Changed:
  - added `.aiworkspace/note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl` as the append-only target for operator candidate review decisions
  - added `Save As Candidate Review Note` under `Backtest > Candidate Review > Candidate Intake Draft`
  - added `Review Notes` tab to inspect saved candidate review notes
  - kept Candidate Review Note separate from `CURRENT_CANDIDATE_REGISTRY.jsonl`, Pre-Live approval, and investment recommendation
  - synced Phase 29 docs, roadmap, doc index, glossary, operations guide, web UI flow docs, comprehensive analysis, and README
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` review note -> registry draft helper smoke passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - finance refinement hygiene check passed
  - `git diff --check` passed
- Durable takeaway:
  - Candidate Intake Drafts now have a safe persistence step for human review decisions without automatically promoting the draft into the current candidate registry.

### 2026-04-23
- Implemented Phase 29 Review Note to Current Candidate Registry Draft workflow.
- Changed:
  - added `Prepare Current Candidate Registry Row` under `Backtest > Candidate Review > Review Notes`
  - selected review notes can now generate editable current candidate registry row previews
  - added explicit `Append To Current Candidate Registry` action
  - disabled registry append for `Reject For Now` review notes
  - synced Phase 29 fourth work-unit docs, checklist, roadmap, doc index, glossary, guides, web UI flow docs, comprehensive analysis, and README
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
- Durable takeaway:
  - Review notes can be promoted into candidate registry rows only through an explicit preview-and-append step. This remains candidate persistence, not investment approval or live trading readiness.

### 2026-04-23
- Moved Phase 29 into implementation handoff state.
- Changed:
  - updated Phase 29 progress status to `implementation_complete`
  - kept validation status at `manual_qa_pending`
  - synced Phase 29 TODO, completion summary, next-phase preparation, checklist, master roadmap, and document index
- Durable takeaway:
  - Phase 29 implementation is complete. The next gate is user checklist QA, not Phase 30 development yet.

### 2026-04-23
- Clarified Candidate Board sample-candidate boundary for Phase 29 QA.
- Changed:
  - documented that existing Candidate Board rows are sample / seed registry candidates for workflow QA, not automatic Single Strategy selections
  - added future development note for Candidate Board maturation into a real candidate lifecycle board
  - updated Phase 29 checklist so the user can QA with the correct sample-data interpretation
- Durable takeaway:
  - Candidate Board needs later-phase refinement, especially source distinction, sample/archive handling, and safe non-automatic candidate recommendation flow.

### 2026-04-23
- Fixed Phase 29 Candidate Review -> Compare prefill for GTAA sample candidates.
- Changed:
  - added a GTAA registry `contract` -> compare override fallback for current candidate rows without explicit `compare_prefill`
  - normalized registry risk-off wording such as `cash_only_or_defensive_bond_preference` into the executable GTAA mode `defensive_bond_preference`
  - updated Phase 29 checklist / TODO / handoff docs and the Backtest UI flow code analysis note
  - reviewed `FINANCE_DOC_INDEX.md`; no index update was needed because no new document was introduced
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv` smoke confirmed both GTAA recommended and lower-MDD registry rows now produce compare prefill payloads
- Durable takeaway:
  - The previous warning was not a user-actionable issue. GTAA seed candidates now have a usable Compare re-entry path through their stored registry contract.

### 2026-04-28
- Closed Phase 29 after user manual QA completion.
- Changed:
  - marked remaining Phase 29 checklist items as completed based on user QA completion confirmation
  - moved Phase 29 status to `complete` / `manual_qa_completed`
  - synced Phase 29 TODO, completion summary, next-phase preparation, master roadmap, doc index, and comprehensive analysis
  - recorded that Phase 30 should start with product-flow reorientation and `backtest.py` module-boundary planning before new portfolio proposal implementation
- Validation:
  - `git diff --check` passed
- Durable takeaway:
  - Phase 29 is closed. The next step is not immediate feature expansion; it is to make the post-Phase-29 operating flow understandable and plan a gradual Backtest UI refactor boundary.

### 2026-04-28
- Opened Phase 30 and completed the first product-flow / refactor-boundary work unit.
- Changed:
  - bootstrapped the Phase 30 document bundle for `Portfolio Proposal And Pre-Live Monitoring Surface`
  - updated the main Guide's `테스트에서 상용화 후보 검토까지 사용하는 흐름` to the post-Phase-29 flow:
    Data Trust -> Single Strategy -> Real-Money Signal -> Compare -> Candidate Draft -> Candidate Review Note -> Current Candidate Registry -> Candidate Board / Pre-Live -> Portfolio Proposal -> Live Readiness
  - documented the `backtest.py` refactor boundary in `BACKTEST_UI_FLOW.md` and the Phase 30 first work-unit note
  - synced Phase 30 status in roadmap, document index, comprehensive analysis, TODO, completion summary, and checklist draft
- Validation:
  - `python3 -m py_compile app/web/streamlit_app.py app/web/pages/backtest.py` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed after root logs were reviewed and updated
  - `git diff --check` passed
- Durable takeaway:
  - Phase 30 is active, but not yet in Portfolio Proposal implementation. The first completed unit makes the user flow understandable again and sets a conservative boundary for future `backtest.py` module extraction.

### 2026-04-28
- Completed the second Phase 30 work unit: Portfolio Proposal contract definition.
- Changed:
  - added `.aiworkspace/note/finance/phases/phase30/PHASE30_PORTFOLIO_PROPOSAL_CONTRACT_SECOND_WORK_UNIT.md`
  - defined the minimum proposal row contract: objective, component candidates, proposal roles, target weights, risk constraints, evidence snapshot, open blockers, and operator decision
  - proposed `.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` as a future append-only storage location without creating the file or implementing append behavior yet
  - updated Phase 30 TODO, checklist, completion summary, roadmap, doc index, glossary, web UI flow docs, and comprehensive analysis
- Validation:
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
  - `git diff --check` passed
  - Playwright browser smoke confirmed the `Pre-Live Feedback` tab renders under `Backtest > Portfolio Proposal`
- Durable takeaway:
  - Phase 30 can now move toward either Proposal UI / persistence or a small Backtest UI module split with a clearer definition of what a Portfolio Proposal is.

### 2026-04-28
- Completed the third Phase 30 work unit: registry JSONL I/O helper split.
- Changed:
  - added `app/web/runtime/candidate_registry.py`
  - moved current candidate registry, candidate review note, and pre-live registry JSONL read / append helpers out of `app/web/pages/backtest.py`
  - exported the helper functions and registry path constants from `app/web/runtime/__init__.py`
  - kept Candidate Review UI, Pre-Live UI, compare prefill behavior, row schemas, file paths, append-only behavior, and Streamlit session state keys unchanged
  - synced Phase 30 TODO, checklist, completion summary, plan, roadmap, doc index, comprehensive analysis, and web UI flow docs
- Validation:
  - `python3 -m py_compile app/web/runtime/candidate_registry.py app/web/runtime/__init__.py app/web/pages/backtest.py` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate` passed
  - `.venv/bin/python` import smoke for current candidate / pre-live / review note loaders passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
  - `git diff --check` passed
- Durable takeaway:
  - This is the first actual `backtest.py` code split in Phase 30, but it is intentionally narrow: registry I/O only. Candidate Review / Pre-Live display logic remains in `backtest.py` for later targeted refactors.

### 2026-04-28
- Completed the fourth Phase 30 work unit: Portfolio Proposal Draft UI / persistence.
- Changed:
  - added `app/web/runtime/portfolio_proposal.py`
  - exported proposal registry helpers from `app/web/runtime/__init__.py`
  - added `Backtest > Portfolio Proposal` with `Create Proposal Draft` and `Proposal Registry` tabs
  - allowed current candidates to be grouped into a proposal draft with objective, proposal type, status, candidate roles, target weights, weight reasons, blocker checks, and operator decision
  - added `.aiworkspace/note/finance/operations/PORTFOLIO_PROPOSAL_REGISTRY_GUIDE.md`
  - synced Phase 30 TODO, checklist, completion summary, plan, next-phase prep, roadmap, doc index, glossary, comprehensive analysis, web UI flow docs, and README
- Validation:
  - `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py` passed
  - `.venv/bin/python` import smoke for proposal registry path / append helper / loader passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
  - `git diff --check` passed
- Durable takeaway:
  - Phase 30 now has the first implemented Portfolio Proposal draft surface. It remains proposal-draft persistence only, not live approval, optimizer output, or order instruction.

### 2026-04-28
- Completed the fifth Phase 30 work unit: Portfolio Proposal Monitoring Review.
- Changed:
  - added `Backtest > Portfolio Proposal > Monitoring Review`
  - added monitoring summary rows for saved proposal drafts
  - added selected proposal detail review with objective, construction, component monitoring, blockers, review gaps, operator decision, and JSON inspect
  - defined `blocked`, `needs_review`, and `review_ready` as monitoring summary states, not live approval states
  - synced Phase 30 TODO, checklist, completion summary, plan, next-phase prep, roadmap, doc index, glossary, comprehensive analysis, web UI flow docs, operations guide, and README
- Validation:
  - `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py` passed
  - `.venv/bin/python` smoke for proposal monitoring helper functions passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
  - `git diff --check` passed
- Durable takeaway:
  - Phase 30 proposal drafts can now be saved and then reviewed as monitoring objects. This still does not approve live trading, create orders, or optimize portfolio weights.

### 2026-04-28
- Completed the sixth Phase 30 work unit: Portfolio Proposal Pre-Live Feedback.
- Changed:
  - added `Backtest > Portfolio Proposal > Pre-Live Feedback`
  - compared proposal saved Pre-Live snapshots with current active Pre-Live registry records
  - added component-level saved/current Pre-Live status, status drift, review overdue, tracking cadence, and current next action readouts
  - added feedback gap detection for missing active Pre-Live records, status drift, hold/reject/re-review with active weight, and overdue review dates
  - synced Phase 30 TODO, checklist, completion summary, plan, next-phase prep, roadmap, doc index, glossary, comprehensive analysis, web UI flow docs, operations guide, and README
- Validation:
  - `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py` passed
  - `.venv/bin/python` smoke for Pre-Live feedback helper functions passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
  - `git diff --check` passed
- Durable takeaway:
  - Portfolio Proposal can now be checked against the current Pre-Live operating state without mutating proposal rows or Pre-Live records.

### 2026-04-28
- Completed the seventh Phase 30 work unit: Portfolio Proposal Paper Tracking Feedback.
- Changed:
  - added `Backtest > Portfolio Proposal > Paper Tracking Feedback`
  - compared proposal saved evidence snapshots with current active Pre-Live `result_snapshot` metrics
  - added component-level saved/current CAGR, saved/current MDD, delta, performance signal, tracking cadence, stop condition, and success condition readouts
  - added feedback gap detection for missing active Pre-Live records, non-`paper_tracking` status, missing saved/current metrics, CAGR / MDD deterioration, and missing tracking cadence
  - moved Phase 30 to `implementation_complete` / `manual_qa_pending`
  - synced Phase 30 TODO, checklist, completion summary, plan, next-phase prep, roadmap, doc index, glossary, comprehensive analysis, web UI flow docs, operations guide, and README
- Validation:
  - `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py` passed
  - `.venv/bin/python` smoke for Paper Tracking Feedback helper functions passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
  - `git diff --check` passed
  - Playwright browser smoke confirmed `Backtest > Portfolio Proposal > Paper Tracking Feedback` renders; existing Streamlit subpath `_stcore` 404 console messages were observed
- Durable takeaway:
  - Phase 30 product functionality is now ready for user manual QA. Additional `backtest.py` module splitting is intentionally deferred to a separate special refactor task.

### 2026-04-28
- Refined the Reference guide's `테스트에서 상용화 후보 검토까지 사용하는 흐름` after user direction.
- Changed:
  - kept the guide as an 11-step product/user flow instead of expanding Phase 30 into many implementation steps
  - updated step 11 from future-oriented `Phase 30 이후` wording to the implemented `Backtest > Portfolio Proposal` path
  - framed Monitoring Review, Pre-Live Feedback, and Paper Tracking Feedback as checks inside the Portfolio Proposal step, not separate major workflow steps
- Durable takeaway:
  - The guide now reflects Phase 30 at the correct level of abstraction: a portfolio proposal review step before future Live Readiness / Final Approval, not a list of Phase 30 work-unit details.

### 2026-04-28
- Started Phase 30 manual walkthrough support for the 1~11 guide flow.
- Verified current candidate registry and reran the GTAA Balanced Top-2 candidate through `run_gtaa_backtest_from_db`.
- Selected `gtaa_real_money_balanced_top2_ief_20260418` as the first practice portfolio candidate because current runtime shows `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Probation=paper_tracking`, `Deployment=paper_only`, `Validation=normal`, `ETF Operability=normal`, and no blockers.
- No code changes were made; this was an operator-flow analysis and QA handoff step.

### 2026-04-28
- Added a user-facing Guide section for reading GTAA Risk-Off candidates.
- Changed:
  - added `Reference > Guides > GTAA Risk-Off 후보군 보는 법`
  - explained that `Defensive Tickers` do not expand the GTAA universe by themselves
  - documented that only the intersection of GTAA Tickers and Defensive Tickers can become usable defensive fallback candidates
  - added the current GTAA Balanced Top-2 example where `IEF` is the only usable defensive fallback candidate
  - updated the Phase 30 checklist so this Guide section is included in manual QA
- Durable takeaway:
  - The walkthrough now has an explicit explanation for why `TLT / LQD / BIL` are not active fallback candidates unless they are also included in the GTAA universe.

### 2026-04-28
- Added an explicit Guide rule for passing from step 4 to step 5 in the 1~11 workflow.
- Changed:
  - added `4단계에서 5단계로 넘어가는 최소 기준` under `Reference > Guides > 테스트에서 상용화 후보 검토까지 사용하는 흐름`
  - documented the minimum Compare-entry criteria as `Promotion Decision != hold`, `Deployment != blocked`, and no unresolved core blocker
  - clarified that this is a Compare-entry criterion, not live trading approval
  - synced the Phase 30 checklist, current TODO, doc index, work log, and question log
- Durable takeaway:
  - Operators can now decide whether a candidate has cleared Hold resolution and can move to Compare without treating the signal as final investment approval.

### 2026-04-28
- Added a Real-Money next-step readiness surface for the 1~11 workflow.
- Changed:
  - added `5단계 Compare 진입 평가` to `Real-Money > 현재 판단`
  - scored Compare-entry readiness out of 10 from Promotion Decision, Deployment Readiness, and Core Blocker status
  - displayed the verdict, next action, progress bar, blocking reasons, review reasons, and score calculation table
  - synced Phase 30 checklist, current TODO, web backtest UI flow, work log, and question log
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - GTAA Balanced Top-2 smoke evaluation returned `8.5 / 10` and `5단계 Compare 진행 가능`
- Durable takeaway:
  - Real-Money now gives an explicit Compare-entry signal before the operator digs into detailed checklist rows.

### 2026-04-29
- Clarified the Real-Money Compare-entry readiness score threshold.
- Changed:
  - added UI copy explaining that `8.0 / 10` is a clean Compare-entry pass
  - clarified that below `8.0 / 10` can still proceed conditionally when the three core criteria pass
  - synced the web backtest UI flow and question log
- Durable takeaway:
  - The score now reads as an operator aid, while the actual stop/go gate remains Promotion non-hold, Deployment non-blocked, and no core blocker.

### 2026-04-29
- Reorganized the Reference guide layout after manual QA feedback.
- Changed:
  - moved `4단계에서 5단계로 넘어가는 최소 기준` out of `테스트에서 상용화 후보 검토까지 사용하는 흐름`
  - added a separate `Reference > Guides > 단계 통과 기준` section for stop/go criteria
  - kept the 1~11 workflow section as a pure step-by-step guide that starts directly at 1단계
  - synced the Phase 30 checklist, current TODO, doc index, work log, and question log
- Durable takeaway:
  - Stage flow guidance and stage pass criteria are now separated, so operators can read the workflow first and consult criteria only when deciding whether to move forward.

### 2026-04-29
- Corrected the documentation scope for the 1~11 walkthrough support session.
- Changed:
  - removed session-specific GTAA Risk-Off, 4->5 pass, and Real-Money readiness checklist items from the Phase 30 QA checklist / TODO
  - created `.aiworkspace/note/finance/operations/BACKTEST_1_TO_11_WALKTHROUGH_SESSION.md` as the separate home for practice questions, candidate examples, and walkthrough-specific UI notes
  - updated the finance doc index and operations README so the walkthrough session is discoverable outside the phase docs
- Durable takeaway:
  - Phase documents should not absorb ad hoc practice-session guidance unless the user explicitly asks to change that phase's QA scope.

### 2026-04-29
- Clarified the correct step-5 Compare path for a new strategy in the walkthrough session.
- Changed:
  - documented that `Candidate Review > Send To Compare` and `Load Recommended Candidates` are registry quick re-entry tools, not the first path for a new unregistered strategy
  - added the direct `Backtest > Compare & Portfolio Builder` path for recreating the single-run contract in Compare
  - noted the current same-family compare limitation and the need to use benchmark / alternative family comparisons first
- Durable takeaway:
  - Step 5 starts from the tested strategy contract itself; registry shortcuts are only for candidates that already exist in current candidate registry.

### 2026-04-29
- Added a Compare-to-Candidate-Draft readiness surface for the 1~11 walkthrough.
- Changed:
  - added `6단계 Candidate Draft 진입 평가` to Compare results
  - scored the selected compare candidate out of 10 from Compare Run, Data Trust, Real-Money Gate, and Relative Evidence
  - added a direct `Send Selected Strategy To Candidate Draft` button for pass / conditional pass cases
  - documented the GTAA Balanced Top-2 compare test setup in the walkthrough session
  - synced the web backtest UI flow, work log, and question log without touching Phase 30 QA docs
- Durable takeaway:
  - Step 5 now has a visible stop/go signal for entering step 6, mirroring the earlier 4->5 readiness box.

### 2026-04-29
- Ran a runtime smoke for the walkthrough's step-5 Compare setup.
- Result:
  - compared GTAA Balanced Top-2, Equal Weight same universe, Global Relative Strength same universe, and Risk Parity Trend default universe
  - GTAA Balanced Top-2 remained the strongest candidate in the smoke run with CAGR 17.88% and MDD -8.39%
  - the new Candidate Draft readiness evaluation returned `9.0 / 10` and `6단계 Candidate Draft 조건부 진행 가능`
- Durable takeaway:
  - The walkthrough now has a concrete compare set and expected smoke result for the user's manual test.

### 2026-04-29
- Reorganized the Reference Guides page for the 1~11 walkthrough support session.
- Changed:
  - grouped Real-Money promotion, Real-Money Contract, and GTAA Risk-Off explanations under `핵심 개념 가이드`
  - made each 1~11 workflow step an expander under `1~11 단계 실행 흐름`
  - made 4->5 and 5->6 pass criteria expanders under `단계 통과 기준`
  - refreshed the `지금 먼저 보면 좋은 문서` and file path list to point at current operations / code analysis / registry docs instead of older Phase 12/13 checklists
  - synced the walkthrough operations note and web backtest UI flow doc without touching Phase 30 QA docs
- Validation:
  - `.venv/bin/python -m py_compile app/web/streamlit_app.py` passed
- Durable takeaway:
  - Guides now separates core concepts, ordered workflow, stop/go criteria, and reference files so the walkthrough can be followed without mixing practice notes into phase QA docs.

### 2026-04-29
- Clarified interval / rebalance interval semantics after walkthrough feedback.
- Changed:
  - added a Guides expander explaining that `option=month_end` makes interval values row cadence, not week counts
  - clarified `1 = monthly / roughly 4 weeks`, `4 = every fourth month-end row`, and `12 = annual`
  - updated Equal Weight input help text in single and compare forms
  - updated the walkthrough note to explain why the GTAA smoke used `Rebalance Interval = 4` and when Equal Weight should use `1`
- Durable takeaway:
  - Operators should use `Rebalance Interval = 1` for a literal monthly / roughly 4-week Equal Weight benchmark under `month_end`; `4` only matches the existing GTAA candidate's slower cadence.

### 2026-04-29
- Split Compare Candidate Draft score from Data Trust gate warnings.
- Changed:
  - removed the hard `6.4 / 10` score cap from the `6단계 Candidate Draft 진입 평가`
  - changed short actual-end / requested-end mismatches into `Data Trust WARNING` instead of a score-capping blocker
  - added a visible `Data Trust` gate metric beside `Draft Score`
  - kept true blocking cases, such as price freshness error or a result period gap over 31 days, as `Data Trust BLOCKED`
  - synced the walkthrough note, web backtest UI flow doc, and Guides pass-criteria copy
- Durable takeaway:
  - Draft Score now reflects compare evidence, while Data Trust tells the operator whether the evidence is clean, warning-level, or blocked.

### 2026-04-29
- Added comparator-selection guidance for the 1~11 walkthrough.
- Changed:
  - added `Reference > Guides > Compare 대상 선정법`
  - documented meaningful comparator roles: naive baseline, market benchmark, adjacent alternative, risk baseline, and existing strong candidate
  - clarified in the walkthrough that Compare is only useful when the comparator set can explain whether the candidate deserves to remain
  - synced the web backtest UI flow doc and question log
- Durable takeaway:
  - Step 5 is not just "run any comparison"; it is the step where the operator chooses defensible comparator roles and checks whether the candidate still has a reason to proceed.

### 2026-04-29
- Added a concrete comparator-selection example for the GTAA walkthrough.
- Changed:
  - added a `GTAA Balanced Top-2` scenario table under `Reference > Guides > Compare 대상 선정법`
  - mirrored the same example in `.aiworkspace/note/finance/operations/BACKTEST_1_TO_11_WALKTHROUGH_SESSION.md`
  - clarified what each comparator tests and what a pass interpretation would look like
- Durable takeaway:
  - Operators now have both comparator categories and a concrete GTAA example for deciding what "meaningful Compare" means before moving to Candidate Draft.

### 2026-04-29
- Combined Candidate Draft intake and Review Note save into one user-facing step.
- Changed:
  - updated `Candidate Review > Candidate Intake Draft` copy to present step 6 as `Candidate Intake & Review Note 저장`
  - added a `6단계 Intake 저장 준비` readiness box that checks candidate identity/source, result snapshot, Data Trust, Real-Money signal, settings snapshot, and operator reason / next action
  - disabled `Save Candidate Review Note` until the intake readiness check passes
  - redefined Guides steps so step 7 is now Review Notes registry-candidate decision and step 8 remains explicit current candidate registry append
  - synced the walkthrough session note and web backtest UI flow doc without touching Phase 30 QA docs
- Durable takeaway:
  - Candidate Draft 확인과 Review Note 저장은 one-step intake workflow이고, registry append는 still a separate explicit decision.

### 2026-04-29
- Added step-7 registry scope gating for saved Candidate Review Notes.
- Changed:
  - added `7단계 Registry 후보 범위 판단` in `Backtest > Candidate Review > Review Notes`
  - classified saved Review Notes into Current Candidate / Near Miss / Scenario / Stop before registry append
  - disabled append when the selected Record Type does not match the step-7 scope
  - preserved compare readiness evidence in Candidate Review Notes and copied it into registry review context
  - synced Guides, walkthrough session notes, and web backtest UI flow without touching Phase 30 QA docs
- Durable takeaway:
  - Step 7 now decides how far a saved Review Note can travel; only a matched scope proceeds to explicit step-8 registry append.

### 2026-04-29
- Merged the previous step-7 scope decision and step-8 registry append into one user-facing step.
- Changed:
  - updated Guides so step 7 is `Current Candidate Registry에 남길 범위 결정 및 저장`
  - removed the separate step that treated `Append To Current Candidate Registry` as its own user-facing stage
  - renumbered Candidate Board / Pre-Live / Portfolio Proposal to follow the merged registry step
  - updated Candidate Review copy so append is presented as the save action inside step 7
  - synced walkthrough and web backtest UI flow docs without touching Phase 30 QA docs
- Durable takeaway:
  - Button-level persistence actions should stay inside the broader decision step instead of becoming standalone workflow stages.

### 2026-04-29
- Added duplicate-safe registry append and step-8 Candidate Board operating readiness.
- Changed:
  - confirmed repeated `Append To Current Candidate Registry` clicks were appending duplicate revisions for the same Review Note while the Board showed only the latest `registry_id` row
  - added a Review Notes duplicate guard that disables append for an already saved Review Note unless the operator explicitly checks a new-revision override
  - added `8단계 Candidate Board 운영 판단` with `PRE_LIVE_READY`, `COMPARE_REVIEW_READY`, and `BOARD_HOLD` routes
  - added route actions to open a ready current candidate in Pre-Live Review or open the Compare picker for near-miss / scenario candidates
  - synced Guides, walkthrough session notes, and web backtest UI flow docs without touching Phase 30 QA docs
- Durable takeaway:
  - Step 8 is a route-reading step: only `PRE_LIVE_READY` moves to Pre-Live; compare-ready alternatives return to Compare instead of being treated as failures.

### 2026-04-29
- Merged the former 6 / 7 / 8 user-facing steps into one Candidate Packaging step.
- Changed:
  - reframed Candidate Review as `6단계 Candidate Packaging` instead of separate Draft / Registry / Board workflow steps
  - updated Compare handoff copy to `Send Selected Strategy To Candidate Packaging`
  - renamed the intake, registry, and board readiness boxes to `Candidate Packaging 저장 준비`, `Registry 후보 범위 판단`, and `Candidate Packaging 종합 판단`
  - reduced Guides from 1~10 to 1~8 steps: 6 Candidate Packaging, 7 Pre-Live Review, 8 Portfolio Proposal
  - synced the walkthrough session note and web backtest UI flow doc without touching Phase 30 QA docs
- Durable takeaway:
  - Candidate Packaging is not a new quant validation layer; it is one packaging gate that turns a compared candidate into a machine-readable, Pre-Live-ready operating candidate.

### 2026-04-29
- Refactored the Candidate Review UX into one sequential Candidate Packaging flow.
- Changed:
  - removed the primary `Candidate Board / Candidate Intake Draft / Review Notes / Inspect Candidate / Send To Compare` tab workflow from `Backtest > Candidate Review`
  - rebuilt the screen as `1. Draft 확인 / Review Note 저장`, `2. Registry 저장`, `3. Pre-Live 진입 평가`
  - kept the existing manual save buttons and readiness gates, but placed them in the order a user actually follows after step-5 Compare
  - moved saved board and compare re-entry into lower auxiliary expanders
  - synced Guides, walkthrough notes, and the web backtest UI flow doc without touching Phase 30 QA docs
- Durable takeaway:
  - Candidate Review is now a single operator flow, not a collection of tabs that force the user to discover the workflow order.

### 2026-04-29
- Improved the handoff from Candidate Packaging registry save to Pre-Live route evaluation.
- Changed:
  - added `registry_id` to current candidate selection labels so repeated GTAA / same-title candidates can be distinguished
  - after `Append To Current Candidate Registry`, stored the appended row's `registry_id` and `revision_id` in session state
  - auto-selected the just-appended row in `3. Pre-Live 진입 평가`
  - added a visible "방금 저장한 후보" summary card with Registry ID, Revision ID, Source Review Note, and Recorded At
  - synced the walkthrough session note and web backtest UI flow doc
- Durable takeaway:
  - The operator no longer has to guess which candidate in the Packaging selectbox came from the immediately preceding registry append.

### 2026-04-29
- Extracted the Candidate Review render flow from `backtest.py`.
- Changed:
  - added `app/web/pages/backtest_candidate_review.py`
  - moved the `Candidate Review` / `Candidate Packaging` screen render logic into the new module
  - kept `_render_candidate_review_workspace()` in `backtest.py` as a thin wrapper so panel routing remains unchanged
  - left shared helpers and registry conversion helpers in `backtest.py` for this first behavior-preserving split
  - synced the web backtest UI flow document
- Durable takeaway:
  - Candidate Review can now be edited from a focused module before adding more Pre-Live workflow work.

### 2026-04-29
- Split Candidate Review render code from Candidate Review helper logic.
- Changed:
  - added `app/web/pages/backtest_candidate_review_helpers.py`
  - moved Candidate Review readiness evaluation, Review Note conversion, registry row conversion, and display helper functions out of `backtest.py`
  - changed `app/web/pages/backtest_candidate_review.py` to import helper logic directly instead of aliasing helper functions from `backtest.py`
  - kept cross-panel handoff functions such as current-candidate compare prefill in `backtest.py` for now
  - synced README, comprehensive analysis, and web backtest UI flow docs
- Verification:
  - `.venv/bin/python -m py_compile app/web/pages/backtest.py app/web/pages/backtest_candidate_review.py app/web/pages/backtest_candidate_review_helpers.py` passed
  - Streamlit smoke checked `Backtest > Candidate Review` on localhost and confirmed the Candidate Packaging screen renders
- Durable takeaway:
  - Candidate Review now has a clearer two-file boundary: render in `backtest_candidate_review.py`, 판단 / 변환 / scoring helper in `backtest_candidate_review_helpers.py`.

### 2026-04-29
- Added repository guidance for script responsibility mapping and function-purpose comments.
- Changed:
  - updated `AGENTS.md` so agents check `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md` and the matching code analysis flow doc before finance code edits
  - added `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md` as the quick script responsibility map
  - updated `docs/architecture/README.md` and `FINANCE_DOC_INDEX.md` to point future code work to the new map
  - added a function documentation rule for new non-trivial domain / workflow / persistence / scoring helpers
- Durable takeaway:
  - Future finance code changes should keep script responsibility documentation current when modules are added, moved, split, or materially repurposed.

### 2026-04-30
- Refactored the Pre-Live Review UX into a sequential step-7 operating check.
- Changed:
  - removed the primary `Create From Current Candidate / Pre-Live Registry` tab workflow from `Backtest > Pre-Live Review`
  - rebuilt the screen as `1. 운영 후보 확인`, `2. 운영 상태 / 추적 계획 결정`, `3. Portfolio Proposal 진입 평가`, `4. 저장 및 다음 단계`
  - added a 10-point Portfolio Proposal readiness evaluation with route labels such as `PORTFOLIO_PROPOSAL_READY`, `WATCHLIST_ONLY`, `PRE_LIVE_HOLD`, `REJECTED`, and `SCHEDULED_REVIEW`
  - preserved direct Pre-Live entry while auto-selecting candidates opened from Candidate Packaging
  - moved saved Pre-Live registry inspection into a lower auxiliary expander
  - moved Candidate Review render/helper modules outside `app/web/pages/` to avoid Streamlit exposing them as standalone pages
- Verification:
  - `.venv/bin/python -m py_compile app/web/pages/backtest.py app/web/backtest_candidate_review.py app/web/backtest_candidate_review_helpers.py app/web/streamlit_app.py` passed
  - Streamlit smoke checked `Backtest > Pre-Live Review` and confirmed the sequential step-7 screen renders with the new readiness box
- Durable takeaway:
  - Pre-Live Review is now an operating-state decision step, not a tabbed persistence utility.

### 2026-04-30
- Clarified candidate-specific Pre-Live status recommendation vs operator final decision.
- Changed:
  - renamed the step-7 status metric to `System Suggested Status`
  - renamed the saved selectbox to `Operator Final Status`
  - added a visible recommendation reason derived from the selected current candidate's Real-Money signal and blockers
  - added a warning when the operator intentionally chooses a final status different from the system suggestion
  - synced the web backtest UI flow document
- Durable takeaway:
  - Pre-Live status is still operator-controlled, but the UI now makes the candidate-specific system recommendation and the saved human decision visibly separate.

### 2026-04-30
- Extracted the Pre-Live Review render flow and helper logic from `backtest.py`.
- Changed:
  - added `app/web/backtest_pre_live_review.py` for the `Backtest > Pre-Live Review` sequential step-7 UI
  - added `app/web/backtest_pre_live_review_helpers.py` for status suggestion, draft conversion, readiness scoring, and registry display helpers
  - kept `backtest.py` as the Backtest panel router with a thin Pre-Live wrapper
  - preserved the existing Pre-Live registry runtime helper and session-state keys
  - synced README, comprehensive analysis, script structure map, and web backtest UI flow docs
- Durable takeaway:
  - Candidate Review and Pre-Live Review now follow the same render/helper module split pattern, lowering the cost of future 7단계 workflow edits.

### 2026-04-30
- Improved Pre-Live Review summary readability on narrow screens.
- Changed:
  - replaced long-string `st.metric` blocks in Pre-Live Review with wrapping status cards
  - applied the card layout to the top summary and the step-2 Promotion / Shortlist / Deployment / System Suggested Status signals
  - kept the underlying Pre-Live scoring, draft, registry, and session-state behavior unchanged
- Durable takeaway:
  - Long candidate status strings no longer collapse into ellipses in the main Pre-Live Review signal summary.

### 2026-04-30
- Improved long route/readiness labels in Candidate Review and Pre-Live Review.
- Changed:
  - added `app/web/backtest_ui_components.py` with shared wrapping status cards and a route/readiness panel
  - replaced `st.metric` route summaries in `Candidate Review > Pre-Live 진입 평가` and `Pre-Live Review > Portfolio Proposal 진입 평가`
  - preserved the existing progress bars, criteria tables, route decisions, and button gating
  - synced README, comprehensive analysis, script structure map, and web backtest UI flow docs
- Durable takeaway:
  - Route labels such as `PORTFOLIO_PROPOSAL_READY` and `PRE_LIVE_READY` now wrap inside a decision panel instead of being truncated.

### 2026-04-30
- Cleaned up the Backtest page shell and navigation.
- Changed:
  - removed the duplicate in-page `Backtest` heading under the top-level Backtest page title
  - changed the visible Backtest navigation from a six-item radio list to a Streamlit segmented workflow selector
  - kept the main workflow focused on `Single Strategy -> Compare & Portfolio Builder -> Candidate Review -> Pre-Live Review -> Portfolio Proposal`
  - moved `History` out of the main workflow navigation and exposed it as a `Run History` utility button while preserving existing History behavior and handoff routes
  - synced README, comprehensive analysis, script structure map, and web backtest UI flow docs
- Verification:
  - `.venv/bin/python -m py_compile app/web/pages/backtest.py app/web/streamlit_app.py app/web/backtest_ui_components.py app/web/backtest_candidate_review.py app/web/backtest_pre_live_review.py` passed
  - Streamlit smoke checked `/backtest`, confirmed the duplicate title is gone, the segmented workflow renders, `Run History` opens the history surface, and selecting a workflow panel returns to that panel
- Durable takeaway:
  - History remains available for replay and candidate handoff, but it is no longer presented as a core step in the candidate review workflow.

### 2026-04-30
- Moved Backtest run history into the Operations navigation.
- Changed:
  - added `app/web/backtest_history.py` as the `Operations > Backtest Run History` page shell
  - added a new `Backtest Run History` page under the `Operations` top navigation group
  - removed the visible `Run History` button and hidden History panel route from the Backtest workflow selector
  - kept the Backtest workflow focused on `Single Strategy -> Compare & Portfolio Builder -> Candidate Review -> Pre-Live Review -> Portfolio Proposal`
  - preserved history actions: `Load Into Form`, `Run Again`, and `Review As Candidate Draft` now switch back into the Backtest workflow after preparing the relevant session state
  - updated Candidate Review copy to point to `Operations > Backtest Run History`
  - synced README, comprehensive analysis, script structure map, and web backtest UI flow docs
- Verification:
  - `.venv/bin/python -m py_compile app/web/streamlit_app.py app/web/backtest_history.py app/web/pages/backtest.py app/web/backtest_candidate_review.py` passed
  - Streamlit smoke checked the top navigation: `Operations > Backtest Run History` renders the persistent backtest history surface, and `Backtest` no longer shows a Run History utility button
- Durable takeaway:
  - Backtest is now visually reserved for candidate-building workflow, while persisted backtest history is treated as an Operations audit / replay surface.

### 2026-04-30
- Completed the second Backtest Run History module split.
- Changed:
  - moved the persistent history inspector, selected-record detail view, replay parity snapshot, and History action buttons into `app/web/backtest_history.py`
  - added `app/web/backtest_history_helpers.py` for history table rows, replay payload reconstruction, field parity summaries, and Real-Money / Guardrail scope helper tables
  - removed the moved history render/helper bodies from `app/web/pages/backtest.py`
  - kept actual backtest rerun execution delegated to `backtest.py` so History does not own strategy runtime behavior
  - synced script structure and web backtest UI flow docs
- Verification:
  - `python3 -m py_compile app/web/backtest_history.py app/web/backtest_history_helpers.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - `uv run python` import smoke confirmed `backtest_history_helpers`, `backtest_history`, and the Backtest parity renderer import load correctly
- Durable takeaway:
  - `backtest.py` is now shorter by the History inspector/replay helper block, and future Run History edits should start in `app/web/backtest_history.py` or `app/web/backtest_history_helpers.py`.

### 2026-04-30
- Merged the standalone Pre-Live Review workflow into Candidate Review.
- Changed:
  - removed the `Pre-Live Review` Backtest panel from the main workflow navigation
  - moved Pre-Live status suggestion, draft generation, readiness scoring, and registry display helper logic into `app/web/backtest_candidate_review_helpers.py`
  - deleted the standalone `app/web/backtest_pre_live_review.py` and `app/web/backtest_pre_live_review_helpers.py` scripts
  - expanded `Backtest > Candidate Review > 3. 운영 상태 저장 및 Portfolio Proposal 진입 평가` so a ready current candidate can save a Pre-Live operating record and then open Portfolio Proposal from the same screen
  - kept `PRE_LIVE_CANDIDATE_REGISTRY.jsonl` and runtime append/load semantics intact because Portfolio Proposal still reads those operating records
  - synced README, comprehensive analysis, script structure map, web backtest UI flow, and Guides copy
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_candidate_review_helpers.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
- Durable takeaway:
  - Pre-Live remains an operating-record concept, but it is no longer a separate Backtest tab or script pair. Future UI edits for this step should start in Candidate Review.

### 2026-04-30
- Improved Candidate Review orientation without adding long explanatory copy.
- Changed:
  - added shared Backtest UI components for an artifact pipeline and input/action/output step summaries
  - replaced the Candidate Packaging flow table with a five-card artifact chain: Draft, Review Note, Current Candidate, Pre-Live Record, Proposal Ready
  - added compact input/action/output cards to the three Candidate Review sections
  - changed `Registry 후보 범위 판단` from metric columns to the same wrapping route/readiness panel style used by Candidate Packaging and Portfolio Proposal readiness
  - synced the script structure map and web backtest UI flow docs
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_ui_components.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - Streamlit smoke checked `Backtest > Candidate Review`; the artifact pipeline, step summaries, and Registry scope panel render correctly
- Durable takeaway:
  - Candidate Review now explains its workflow through compact visual structure rather than large instructional text blocks.

### 2026-04-30
- Refined Candidate Review after visual review feedback.
- Changed:
  - removed the per-section Input / Action / Output card grids because they made the page feel busier
  - replaced them with thin `왜 / 결과` brief strips
  - simplified `2. Registry 저장` by keeping the Scope route panel visible and moving detailed criteria / previous registry rows into collapsed expanders
  - reduced visible Registry row inputs to ID, record type, title, notes, and the next-step selection label; moved advanced strategy identity fields into a collapsed section
  - changed Registry metadata and Pre-Live signal summaries from large cards to compact badge strips
  - trimmed `3. 운영 상태 저장 및 Portfolio Proposal 진입 평가` so Candidate Review shows only the selected candidate's core state, operating decision, and proposal route by default, with recent-candidate identity details hidden behind an expander
  - added a Streamlit copy-shortcut guard so normal Cmd/Ctrl+C does not bubble into Streamlit's clear-cache shortcut handler
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_ui_components.py app/web/streamlit_app.py app/web/pages/backtest.py` passed
  - Streamlit smoke checked `Backtest > Candidate Review`; artifact pipeline remains, step guidance is shown as `왜 / 결과`, Registry advanced identity fields and detailed criteria are collapsed, and Cmd/Ctrl+C no longer opens the clear-cache modal
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
- Durable takeaway:
  - Candidate Review should keep the artifact pipeline, but per-section guidance should stay thin and action-centered.

### 2026-04-30
- Simplified Candidate Review step 3 into candidate confirmation plus operating-record save.
- Changed:
  - renamed step 3 to `운영 기록 저장 및 Portfolio Proposal 이동`
  - replaced the visible `Candidate Packaging 종합 판단` panel with a compact `선택 후보 확인` block
  - merged the separate `Pre-Live 운영 상태 / 추적 계획 저장` and `Portfolio Proposal 진입 평가` blocks into `운영 기록 저장 및 다음 단계 판단`
  - changed the default view to show `Save Record`, `Next Route`, `Proposal`, and `Blockers` as compact badges above the save/open buttons
  - moved detailed route criteria into collapsed expanders
  - synced Guides copy and web backtest UI flow docs
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_ui_components.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - Streamlit smoke checked `Backtest > Candidate Review`; step 3 now renders as `선택 후보 확인` plus `운영 기록 저장 및 다음 단계 판단`, and the old separate Proposal readiness panel is gone
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
- Durable takeaway:
  - Step 3 should read as `select candidate -> save operating record -> open Proposal if the saved record qualifies`, not as a second full Candidate Packaging evaluation.

### 2026-04-30
- Restored the shared route/readiness judgment pattern inside Candidate Review step 3.
- Changed:
  - added the common route/readiness panel back to `운영 기록 저장 및 다음 단계 판단` so the next-step judgment remains visually consistent with `저장 범위 판단`
  - kept the Promotion / Shortlist / Deployment / Suggested badges as the candidate signal summary
  - moved `운영 기록 / 다음 단계 판단 기준`, `Pre-Live Record JSON Preview`, and `Selected Candidate Detail` into one collapsed `상세 보기` area with tabs
  - moved the `Save Pre-Live Record` and `Open Portfolio Proposal` buttons into a bordered `저장 및 이동` action block before the details
  - synced the web backtest UI flow doc
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_ui_components.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
- Durable takeaway:
  - Candidate Review step 3 should preserve a common next-step judgment panel, but keep secondary details behind one collapsed area so the save/open actions are easy to find.

### 2026-04-30
- Repositioned Candidate Review step 3 next-step judgment above the operating-record inputs.
- Changed:
  - widened and rebalanced the shared route/readiness panel so long route labels break at underscores instead of mid-word
  - moved `다음 단계 진행 판단` above `운영 상태 / 추적 계획 입력` while keeping it driven by the current input values
  - kept the panel in the same bordered format as `저장 범위 판단`, including progress and success/warning/error status
  - left Save / Open buttons before the collapsed detail area
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_candidate_review.py app/web/backtest_ui_components.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - Streamlit smoke checked `Backtest > Candidate Review` on port `8512`; `다음 단계 진행 판단` now appears above `운영 상태 / 추적 계획 입력`, Save/Open actions remain before `상세 보기`, and route/readiness cards do not horizontally overflow at 900px / 600px viewport widths
  - `git diff --check` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
- Durable takeaway:
  - Candidate Review should show the pass/fail route judgment before the operator writes or saves the operating record, because the judgment explains why saving is available.

### 2026-04-30
- Reworked Backtest > Portfolio Proposal into a single construction-draft flow toward future Live Readiness.
- Changed:
  - split Portfolio Proposal render logic into `app/web/backtest_portfolio_proposal.py`
  - split proposal row creation, readiness scoring, monitoring, Pre-Live feedback, and paper tracking feedback helpers into `app/web/backtest_portfolio_proposal_helpers.py`
  - reduced `app/web/pages/backtest.py` to a Portfolio Proposal wrapper call for this panel
  - replaced the old five-tab proposal surface with `1. Proposal 후보 확인`, `2. 목적 / 역할 / 비중 설계`, `3. Proposal 저장 및 다음 단계 판단`
  - added a Live Readiness route/readiness panel with `LIVE_READINESS_CANDIDATE_READY`, `PROPOSAL_DRAFT_READY`, and `PROPOSAL_BLOCKED` routes
  - moved saved proposal monitoring / Pre-Live feedback / paper tracking feedback into one collapsed support area
  - refreshed Reference > Guides copy for the new Portfolio Proposal / Live Readiness boundary
  - updated the walkthrough session note so 6단계 Candidate Packaging and 7단계 Portfolio Proposal match the implemented flow
  - fixed shared status cards so numeric `0` displays as `0` instead of `-`
- Verification:
  - `.venv/bin/python -m py_compile app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py app/web/backtest_ui_components.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - Streamlit smoke checked `Backtest > Portfolio Proposal` on port `8513`; the new three-step flow rendered, selecting `GTAA review candidate` produced `LIVE_READINESS_CANDIDATE_READY`, and `Save Portfolio Proposal Draft` became enabled
  - `git diff --check` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
- Durable takeaway:
  - Portfolio Proposal should remain a Backtest tab, but it should read as one lightweight construction-draft step between Candidate Review and future Live Readiness, not as several separate record-review stages.

### 2026-04-30
- Split Backtest > Portfolio Proposal into single-candidate direct readiness and multi-candidate construction paths.
- Changed:
  - added a `단일 후보 직행 평가` mode for one selected current candidate
  - added direct readiness scoring with `LIVE_READINESS_DIRECT_READY`, `LIVE_READINESS_DIRECT_REVIEW_REQUIRED`, and `LIVE_READINESS_DIRECT_BLOCKED`
  - made direct mode use implicit role `core_anchor`, target weight `100%`, and capital scope `paper_only` without writing a new proposal draft
  - kept `포트폴리오 초안 작성` for two or more candidates, where role / target weight / reason are real proposal inputs
  - clarified that `Proposal Components` is construction selection, not strategy comparison
  - synced Guides, Portfolio Proposal registry guide, web Backtest UI flow, walkthrough note, and the high-level finance map
- Verification:
  - `python3 -m py_compile app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py` passed
  - `python3 -m py_compile app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py app/web/pages/backtest.py app/web/streamlit_app.py` passed
  - Streamlit smoke checked `Backtest > Portfolio Proposal` on port `8514`; selecting `GTAA review candidate` opened `단일 후보 직행 평가`, showed `Proposal Draft=저장 불필요`, and rendered `LIVE_READINESS_DIRECT_READY`
  - `git diff --check` passed
  - `python3 .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` passed
- Durable takeaway:
  - Portfolio Proposal should not force a save loop for a single candidate; proposal draft persistence is mainly for multi-candidate construction or intentionally documented allocation proposals.

### 2026-04-30
- Reworked Workspace > Overview into a registry-backed quant dashboard.
- Changed:
  - added `app/web/overview_dashboard.py` for Overview rendering
  - added `app/web/overview_dashboard_helpers.py` for current candidate, Pre-Live, proposal, history, saved portfolio aggregation
  - replaced the old static start guide with KPI cards, review-priority Top 3 candidates, candidate funnel chart, next actions, recent activity, and collapsed system snapshot
  - moved runtime/build details into the `System Snapshot` expander instead of the top of the page
  - updated README, script structure map, web Backtest UI flow, and high-level finance map for the new Overview modules
- Verification:
  - `.venv/bin/python -m py_compile app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py app/web/streamlit_app.py` passed
  - `.venv/bin/python` snapshot load returned 12 current candidates, 2 paper tracking records, 30 recent runs, and a Top 3 candidate list
  - Streamlit smoke checked `Workspace > Overview` on port `8515`; KPI cards, Top 3 candidate cards, funnel chart, next actions, recent activity, and collapsed system snapshot rendered
- Durable takeaway:
  - Overview should behave like the front dashboard for the quant workflow, showing current candidates and next actions rather than acting as a static start guide.

### 2026-04-30
- Split the remaining large Backtest page shell into workflow modules.
- Changed:
  - reduced `app/web/pages/backtest.py` to a thin Backtest page shell and workflow panel dispatcher
  - added `app/web/backtest_common.py` for shared presets, session state, panel routing, strategy input widgets, real-money / guardrail inputs, and status label helpers
  - added `app/web/backtest_single_strategy.py`, `app/web/backtest_single_forms.py`, and `app/web/backtest_single_runner.py` for Single Strategy orchestration, strategy-specific forms, and DB-backed run dispatch
  - added `app/web/backtest_compare.py` for Compare & Portfolio Builder, weighted portfolio builder, saved portfolio load / replay, and current-candidate compare prefill
  - added `app/web/backtest_result_display.py` for latest result / compare result / data trust / real-money detail / selection history display helpers
  - updated `streamlit_app.py`, `backtest_history.py`, and `backtest_candidate_review.py` to import the new module boundaries instead of reaching through the page shell
  - synced the script structure map, web Backtest UI flow, and high-level finance map
- Verification:
  - `.venv/bin/python -m py_compile app/web/pages/backtest.py app/web/backtest_common.py app/web/backtest_single_strategy.py app/web/backtest_single_forms.py app/web/backtest_single_runner.py app/web/backtest_compare.py app/web/backtest_result_display.py app/web/backtest_history.py app/web/backtest_candidate_review.py app/web/streamlit_app.py` passed
  - `.venv/bin/python` import smoke passed for the Backtest shell and new Backtest modules
  - Streamlit smoke checked `Workspace > Overview` and `Backtest` on port `8516`; `Single Strategy`, `Compare & Portfolio Builder`, `Candidate Review`, and `Portfolio Proposal` rendered after the split
- Durable takeaway:
  - `app/web/pages/backtest.py` should stay a page shell. Future Single / Compare / result display work should land in the matching `app/web/backtest_*.py` module instead of growing the page entry again.

### 2026-04-30
- Archived the existing local finance runtime JSONL records and started a fresh candidate registry run.
- Found and saved a GTAA candidate that reaches the current 7-step workflow boundary:
  - `GTAA Clean-6 AOR Top-1`
  - universe `SPY, QQQ, GLD, IEF, LQD, TLT`
  - `top=1`, `interval=2`, `score=3M/12M`, `trend=MA200`, `risk_off=cash_only`
  - formal benchmark `AOR`
  - `CAGR=15.3395%`, `MDD=-13.9675%`, `Promotion=real_money_candidate`
- Persisted:
  - `BACKTEST_RUN_HISTORY.jsonl`
  - `CANDIDATE_REVIEW_NOTES.jsonl`
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`
  - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`
- Verification:
  - `manage_current_candidate_registry.py validate` passed with 1 registry row
  - `manage_pre_live_candidate_registry.py validate` passed with 1 pre-live row
  - Portfolio Proposal direct readiness evaluated as `LIVE_READINESS_DIRECT_READY`, score `10.0`, blockers `0`
- Durable takeaway:
  - For this GTAA candidate, `AOR` is the appropriate formal multi-asset benchmark for the current gate. `SPY` remains useful as a reference, but using `SPY` as the formal promotion benchmark turns the same candidate into `hold` because of rolling worst-excess validation caution.

### 2026-05-01
- Found and saved a second GTAA candidate under the user's follow-up constraints:
  - universe size 6~15, selected universe `SPY, QQQ, GLD, IEF, LQD, TLT`
  - `top=2`, `interval=3`, `score=1M/3M/6M`, `trend=MA200`, `risk_off=cash_only`
  - formal benchmark `AOR`
  - `CAGR=12.8073%`, `MDD=-11.5626%`, `Sharpe=2.0147`
  - `Promotion=real_money_candidate`, `ETF Operability=normal`, `Validation=normal`
- Persisted:
  - review note `candidate_review_note_a152594509dd`
  - current candidate `gtaa_current_candidate_clean6_aor_top2_i3_1m3m6m`
  - Pre-Live record `pre_live_gtaa_current_candidate_clean6_aor_top2_i3_1m3m6m`
- Verification:
  - `manage_current_candidate_registry.py validate` passed with 2 registry rows
  - `manage_pre_live_candidate_registry.py validate` passed with 2 pre-live rows
- Durable takeaway:
  - The top-2 interval-3 candidate is less aggressive than the top-1 candidate, but it is a cleaner second practice candidate because drawdown is lower and Sharpe is higher while still passing the same AOR-based Real-Money gate.

### 2026-05-01
- Searched for a higher-CAGR GTAA candidate under the same top/interval/universe constraints.
- Selected and saved:
  - `GTAA Clean-6 AOR Top-2 High CAGR`
  - universe `SPY, QQQ, GLD, IEF, LQD, TLT`
  - `top=2`, `interval=2`, `score=1M/12M`, `trend=MA150`, `risk_off=cash_only`
  - formal benchmark `AOR`
  - `CAGR=15.2174%`, `MDD=-8.8783%`, `Sharpe=1.9630`
  - `Promotion=real_money_candidate`, `ETF Operability=normal`, `Validation=normal`
- Persisted:
  - review note `candidate_review_note_d12013649150`
  - current candidate `gtaa_current_candidate_clean6_aor_top2_i2_1m12m_ma150`
  - Pre-Live record `pre_live_gtaa_current_candidate_clean6_aor_top2_i2_1m12m_ma150`
- Verification:
  - `manage_current_candidate_registry.py validate` passed with 3 registry rows
  - `manage_pre_live_candidate_registry.py validate` passed with 3 pre-live rows
- Durable takeaway:
  - The high-CAGR top-2 candidate meets the user's tightened target better than the interval-3 candidate: CAGR is above 15% while MDD is below 9%.

### 2026-05-01
- Added an Operations-owned Candidate Library for saved candidate replay.
- Changed:
  - added `app/web/backtest_candidate_library.py` to inspect saved current candidates and matched Pre-Live records
  - added `app/web/backtest_candidate_library_helpers.py` to join registry rows, build candidate tables, reconstruct ETF replay payloads, and re-run saved contracts
  - added `Operations > Candidate Library` to the Streamlit navigation
  - updated Backtest guidance to point run history to `Backtest Run History` and saved candidate replay to `Candidate Library`
  - clarified the Compare-side saved portfolio area as `Saved Weighted Portfolios`, separate from saved candidate replay
  - synced README, script structure map, web Backtest UI flow, and high-level finance map
- Verification:
  - `.venv/bin/python -m compileall app/web/backtest_candidate_library.py app/web/backtest_candidate_library_helpers.py app/web/streamlit_app.py app/web/pages/backtest.py app/web/backtest_compare.py` passed
  - Candidate Library helper load returned 3 current candidates and built a GTAA replay payload from the saved registry contract
  - GTAA candidate replay reproduced the stored candidate snapshot: `rows=63`, `End Balance=42653.22`, `CAGR=15.3395%`, `MDD=-13.9675%`
  - Streamlit smoke checked `Operations > Candidate Library` on port `8517`; candidate table, snapshot cards, replay button, rebuilt Data Trust / Summary tabs rendered without console errors after adding the missing shared compare chart helper to `backtest_result_display.py`
- Durable takeaway:
  - Saved candidates and saved weighted portfolios are different artifact types. Candidate Library is a 보관함 / 재검토 tool for current candidates, while Compare keeps weighted portfolio outputs created by the portfolio builder.

### 2026-05-01
- Searched `Quality Snapshot (Strict Annual)` for a candidate that can be used in the current 7-step practice workflow.
- Search frame:
  - `US Statement Coverage 100 / 300 / 500`
  - `Historical Dynamic PIT Universe`
  - `topN 3~10`
  - target `CAGR >= 20%`, `MDD >= -15%`
- Selected candidate:
  - `US Statement Coverage 100`, `topN=8`, `AOR` formal benchmark
  - factors `roe, roa, net_margin, asset_turnover, current_ratio`
  - `Trend Filter MA250`, `retain_unfilled_as_cash`, `cash_only`
  - underperformance guardrail `3M / -5%`
  - drawdown guardrail `12M / -12% strategy threshold / 5% gap threshold`
  - `CAGR=20.02%`, `MDD=-13.42%`, `Sharpe=1.3957`
  - `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Deployment=review_required`
- Coverage 300 / 500 did not produce exact hits in the bounded search.
- Durable takeaway:
  - This Quality candidate is a valid 7-step practice candidate when the formal benchmark is `AOR`.
  - It has not been appended to review/current/pre-live registries yet; saving should be done after the user confirms they want to persist this candidate.

### 2026-05-01
- Re-searched `Quality Snapshot (Strict Annual)` for a cleaner GTAA-like deployment path after the user asked whether the previous `review_required` candidate could be improved into a registry-ready candidate.
- Finding:
  - The earlier `CAGR 20% / MDD -13%` Quality candidate remains `review_required` because guardrail trigger / monitoring review signals stay active.
  - A clean `paper_only` candidate was found, but CAGR drops below the original 20% requirement.
- Clean paper-only candidate:
  - `US Statement Coverage 100`, `Historical Dynamic PIT`
  - factors `roe, roa, cash_ratio, debt_to_assets`
  - `topN=10`, `Trend MA250`, `retain_unfilled_as_cash`, `cash_only`, benchmark `AOR`
  - `CAGR=14.38%`, `MDD=-14.56%`, `Sharpe=1.2490`
  - `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Deployment=paper_only`
- Durable takeaway:
  - There are two Quality practice choices:
    - higher-return `review_required` candidate: closer to the user's numeric return target
    - lower-return `paper_only` candidate: cleaner registry / Pre-Live practice path

### 2026-05-01
- Improved the Real-Money detail surface used by Candidate Library replay results.
- Changed:
  - replaced truncation-prone `st.metric` rows in the Real-Money overview with wrapping status cards
  - applied the same card layout to Promotion, Shortlist, Probation / Monitoring, and Deployment Readiness sub-sections
  - kept the existing checklist/detail tables, but moved long status and next-step strings into card values/details so narrower browser widths do not collapse them into `...`
- Verification:
  - `.venv/bin/python -m compileall app/web/backtest_result_display.py app/web/backtest_candidate_library.py app/web/backtest_ui_components.py` passed
  - direct import check for `app.web.backtest_result_display._render_real_money_details` passed

### 2026-05-01
- Searched `Quality + Value Snapshot (Strict Annual)` for a practice candidate under the user's expanded constraints.
- Search frame:
  - `US Statement Coverage 100 / 300 / 500 / 1000` considered through local reruns and sub-agent sweeps
  - `Historical Dynamic PIT Universe`
  - `topN 3~10`
  - target `CAGR >= 25%`, `MDD >= -20%`
  - factor sets with at least 3 factors, mixing quality and value factors
- Selected candidate:
  - `US Statement Coverage 100`, `topN=10`, ticker benchmark `SPY`
  - quality factors `roe, roa, operating_margin, asset_turnover, current_ratio`
  - value factors `book_to_market, earnings_yield, sales_yield, pcr, por`
  - `reweight_survivors`, `cash_only`, trend / market regime off
  - underperformance guardrail `12M / -5%`
  - drawdown guardrail `12M / -15% strategy threshold / 3% gap threshold`
  - `CAGR=29.25%`, `MDD=-18.64%`, `Sharpe=1.5222`
  - `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Deployment=review_required`
- Durable takeaway:
  - This Quality + Value candidate meets the user's CAGR/MDD target and can be used as a Candidate Review / Portfolio Proposal practice candidate.
  - A Coverage 500 exact-performance hit was rejected as a workflow candidate because full runtime marked it `hold / blocked` due to liquidity / validation caution.

### 2026-05-01
- Registered the selected `Quality + Value Snapshot (Strict Annual)` practice candidate through the machine-readable workflow artifacts.
- Saved records:
  - `CANDIDATE_REVIEW_NOTES.jsonl`: `candidate_review_note_qv_cov100_top10_spy_mdd20`
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`: `quality_value_current_candidate_cov100_top10_spy_mdd20`
  - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`: `pre_live_quality_value_current_candidate_cov100_top10_spy_mdd20`
- Verification:
  - reran full runtime before append: `CAGR=29.2522%`, `MDD=-18.6392%`, `Sharpe=1.5222`
  - gate: `real_money_candidate / paper_probation / review_required`
  - `manage_current_candidate_registry.py validate` passed with 4 rows
  - `manage_pre_live_candidate_registry.py validate` passed with 4 rows
  - Candidate Library helper loaded the candidate with `paper_tracking` Pre-Live status
- Note:
  - Candidate Library lists the candidate now. Strict annual equity replay support was added on 2026-05-02.

### 2026-05-01
- Rechecked the `review_required` issue after the user asked for a cleaner candidate with `Promotion=real_money_candidate`, `Shortlist=paper_probation`, and `Deployment=paper_only`.
- Finding:
  - `Quality + Value` variants could keep stronger CAGR, but no exact `paper_only` deployment candidate was found before stopping the bounded/sub-agent sweep.
  - The clean exact hit was the lower-return `Quality Snapshot (Strict Annual)` candidate.
- Registered records:
  - `CANDIDATE_REVIEW_NOTES.jsonl`: `candidate_review_note_quality_cov100_top10_aor_ma250_paper_only`
  - `CURRENT_CANDIDATE_REGISTRY.jsonl`: `quality_current_candidate_cov100_top10_aor_ma250_paper_only`
  - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`: `pre_live_quality_current_candidate_cov100_top10_aor_ma250_paper_only`
- Verification:
  - candidate result: `CAGR=14.38%`, `MDD=-14.56%`, `Sharpe=1.2490`
  - gate: `real_money_candidate / paper_probation / paper_only`
  - `manage_current_candidate_registry.py validate` passed with 5 rows
  - `manage_pre_live_candidate_registry.py validate` passed with 5 rows
  - Candidate Library helper loaded the candidate with `paper_tracking` Pre-Live status

### 2026-05-02
- Fixed Candidate Library replay for saved strict annual equity candidates after the user hit the ETF-only replay warning on `Quality + Value Coverage 100 Top-10`.
- Changed:
  - extended `app/web/backtest_candidate_library_helpers.py` replay support from ETF-only families to `quality_snapshot_strict_annual`, `value_snapshot_strict_annual`, and `quality_value_snapshot_strict_annual`
  - restored strict annual contract fields from current candidate registry rows, including factors, topN, dynamic PIT universe, trend / market regime, guardrails, benchmark, liquidity filters, and promotion thresholds
- Verification:
  - `.venv/bin/python -m compileall app/web/backtest_candidate_library_helpers.py app/web/backtest_candidate_library.py` passed
  - Candidate Library replay helper rebuilt `quality_current_candidate_cov100_top10_aor_ma250_paper_only` with 124 result rows and gate `real_money_candidate / paper_probation / paper_only`
  - Candidate Library replay helper rebuilt `quality_value_current_candidate_cov100_top10_spy_mdd20` with 124 result rows and gate `real_money_candidate / paper_probation / review_required`

### 2026-05-02
- Checked the saved `Quality + Value Coverage 100 Top-10` Candidate Library replay after the user could not see `2026-03-31` in the Result Table.
- Finding:
  - backend replay result contains `2026-03-31`; final four result dates are `2026-01-30`, `2026-02-27`, `2026-03-31`, `2026-04-01`
  - the extra `2026-04-01` row is the requested end-date valuation row, while `2026-03-31` is the normal March month-end row
- Changed:
  - translated strict annual runtime warnings for dynamic PIT universe, history/liquidity filters, trend/market regime/risk-off, and underperformance/drawdown guardrails into Korean
- Verification:
  - `.venv/bin/python -m compileall app/web/runtime/backtest.py` passed
  - Candidate Library replay warnings for `quality_value_current_candidate_cov100_top10_spy_mdd20` are now displayed in Korean

### 2026-05-02
- Reorganized finance phase documents under a single phase parent folder after the user pointed out `.aiworkspace/note/finance` root document fragmentation.
- Changed:
  - moved root-level numbered phase folders into `.aiworkspace/note/finance/phases/phase1` through `.aiworkspace/note/finance/phases/phase30`
  - added `.aiworkspace/note/finance/phases/README.md` as the phase document landing page
  - updated phase links and workflow references in roadmap / doc index / analysis / code-analysis / operation docs
  - updated `bootstrap_finance_phase_bundle.py` to create future phase bundles under `.aiworkspace/note/finance/phases/phase<N>/`
  - updated `check_finance_refinement_hygiene.py` phase-doc classification for the new path
- Verification:
  - no numbered phase directories remain directly under `.aiworkspace/note/finance`
  - old `.aiworkspace/note/finance/phaseN` references are removed from active docs and scripts

### 2026-05-02
- Reorganized finance JSONL files into purpose-specific folders after the user asked whether registry and history files should also be folder-managed.
- Changed:
  - moved durable registry files under `.aiworkspace/note/finance/registries/`
  - moved local run history under `.aiworkspace/note/finance/run_history/`
  - moved saved portfolio setup storage under `.aiworkspace/note/finance/saved/`
  - updated Streamlit runtime path constants, registry helper scripts, hygiene helper classification, UI path copy, and durable operations docs
  - added README files for `registries/`, `run_history/`, and `saved/`
- Decision:
  - registries are durable app-readable operating data
  - run history remains generated / local execution state
  - saved portfolio JSONL is reusable setup storage, not a candidate approval registry

### 2026-05-03
- Opened Phase 31 preparation after the user approved the Phase 31~35 direction toward final real-money portfolio candidate selection.
- Created the Phase 31 document bundle under `.aiworkspace/note/finance/phases/phase31/`.
- Defined Phase 31 as `Portfolio Risk And Live Readiness Validation`, not as a duplicate Live Readiness decision-record phase.
- Added the first work-unit document for `Portfolio Risk Input And Validation Contract`.
- Decision:
  - Phase 31 should read existing current candidate, Pre-Live, and Portfolio Proposal registries first.
  - It should start as a read-only validation pack and avoid creating a new approval registry unless a later phase clearly needs one.
  - Phase 30 remains `implementation_complete / manual_qa_pending`; Phase 31 opens as `active / not_ready_for_qa`.

### 2026-05-03
- Completed Phase 31 implementation for `Portfolio Risk And Live Readiness Validation`.
- Changed:
  - added Phase 31 validation helpers in `app/web/backtest_portfolio_proposal_helpers.py`
  - normalized direct single-candidate and proposal draft inputs into one validation input shape
  - added validation result fields for route, score, blockers, paper tracking gaps, review gaps, component rows, checks, and Phase 32 handoff summary
  - rendered Validation Pack surfaces in `Backtest > Portfolio Proposal` for direct single-candidate review, in-progress proposal drafts, and saved proposal review
  - kept the feature read-only: no new approval registry, no live approval, no optimizer
- Documentation:
  - synced Phase 31 TODO, completion summary, checklist, next phase preparation, roadmap, doc index, README, comprehensive analysis, and Backtest UI flow docs
- Verification:
  - `.venv/bin/python -m py_compile app/web/streamlit_app.py app/web/pages/backtest.py app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py` passed
  - helper smoke confirmed one direct candidate can route to `READY_FOR_ROBUSTNESS_REVIEW`
  - helper smoke confirmed a two-candidate proposal with overlap routes to `NEEDS_PORTFOLIO_RISK_REVIEW`
- Status:
  - Phase 31 is now `implementation_complete / manual_qa_pending`
  - user QA should use `.aiworkspace/note/finance/phases/phase31/PHASE31_TEST_CHECKLIST.md`

### 2026-05-03
- Refined Phase 31 QA feedback around in-progress Portfolio Proposal validation.
- Changed:
  - removed duplicate weight-sum reporting from `Blocking Scope`, so a 100% target-weight issue is surfaced as `Portfolio Construction` with an actionable correction
  - added `blocking_guidance` messages such as target weight must sum to 100% and active proposals need at least one `core_anchor`
  - added a `Proposal Role / Target Weight 사용법` expander inside `Backtest > Portfolio Proposal`
  - clarified the Phase 31 checklist item for "Validation Pack does not auto-save or approve"
  - added Proposal Role usage notes to the glossary and Backtest UI flow document
- Decision:
  - `PROPOSAL_BLOCKED` for GTAA + Quality is normal when target weights do not sum to 100% or no active `core_anchor` remains.
  - The issue was not the validation logic but the lack of actionable UI guidance.

### 2026-05-03
- Fixed Phase 31 Portfolio Proposal save feedback after the user reported no visible reaction from `Save Portfolio Proposal Draft`.
- Finding:
  - the proposal draft was being appended to `.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`
  - the success message disappeared because the UI called `st.rerun()` immediately after `st.success`
  - repeated clicks could append the same Proposal ID multiple times
- Changed:
  - moved the save success message into session state so it remains visible after rerun
  - reset the Proposal ID after a successful save so the next draft gets a fresh default id
  - added duplicate Proposal ID blocking with an explicit "change Proposal ID" instruction

### 2026-05-03
- Refined Phase 31 Portfolio Proposal UX after the user noted saved proposal feedback looked awkward in the single-candidate direct path.
- Changed:
  - removed the saved proposal feedback section from the single-candidate direct path
  - kept single-candidate review focused on direct Live Readiness readiness plus Portfolio Risk / Validation Pack
  - moved saved proposal validation / monitoring / feedback into the multi-candidate proposal draft path as `4. 저장된 Portfolio Proposal 확인`
  - updated the save success copy to point to the new saved proposal section
- Decision:
  - single candidates should proceed as direct next-stage inputs without proposal draft save/list UX
  - saved proposal lists belong to the portfolio construction flow where two or more candidates are being composed

### 2026-05-03
- Refined the Phase 31 manual QA checklist after the saved proposal UX move.
- Changed:
  - preserved the user's existing checked QA items
  - replaced the stale `보조 도구: Saved Proposals / Feedback` verification path with `4. 저장된 Portfolio Proposal 확인`
  - added checks that saved proposal lists appear only in the multi-candidate proposal construction flow
  - added a QA reset note for deleting `.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`

### 2026-05-03
- Renamed the Phase 31 validation expander label after the user pointed out that `Phase 32 handoff` sounded like an internal phase term.
- Changed:
  - UI label changed from `Validation 기준 / Phase 32 handoff` to `검증 기준 / 다음 단계 안내`
  - caption now describes this as a read-only check for the next robustness validation step
  - Phase 31 checklist and Backtest UI flow notes now use the same user-facing wording

### 2026-05-03
- Clarified the Phase 31 manual QA checklist after the user found the `다음 단계 안내 확인` section hard to verify.
- Changed:
  - explained that QA does not need to force all four validation routes
  - added concrete checks for `Validation Route`, `Next Action`, and the `검증 기준 / 다음 단계 안내` expander
  - added route interpretation tables to the checklist and next-phase preparation document

### 2026-05-03
- Closed Phase 31 after the user confirmed Phase 31 closeout.
- Changed:
  - marked remaining Phase 31 checklist items as completed based on the user's QA completion signal
  - moved Phase 31 status to `complete` / `manual_qa_completed`
  - synced Phase 31 TODO, completion summary, next-phase preparation, roadmap, doc index, README, and comprehensive analysis
  - kept Phase 30 as `implementation_complete` / `manual_qa_pending`
- Next direction:
  - Phase 32 can open as `Robustness And Stress Validation Pack` when the user approves the next phase start.
- Hygiene:
  - `check_finance_refinement_hygiene.py` was run.
  - Current candidate registry changes were not needed because Phase 31 closeout changed docs / QA status only, not candidate rows.

### 2026-05-03
- Created narrower local Codex skills after the user approved splitting `finance-doc-sync`.
- Changed:
  - added `/Users/taeho/.codex/skills/finance-backtest-web-workflow/SKILL.md`
  - added `/Users/taeho/.codex/skills/finance-phase-management/SKILL.md`
  - narrowed `/Users/taeho/.codex/skills/finance-doc-sync/SKILL.md` so it is treated as final documentation alignment, not the primary implementation skill
  - updated `AGENTS.md` and support track docs with the intended skill usage order
- Decision:
  - Phase32 Backtest UI work should start with `finance-backtest-web-workflow` or `finance-phase-management`, then use `finance-doc-sync` for final alignment.
- Hygiene:
  - `check_finance_refinement_hygiene.py` was run.
  - Current candidate registry changes were not needed because this was skill / workflow guidance work, not candidate data work.

### 2026-05-03
- Opened Phase 32 `Robustness And Stress Validation Pack` after the user approved moving on from Phase 31.
- Changed:
  - created `.aiworkspace/note/finance/phases/phase32/` plan / TODO / checklist / summary / next-phase preparation documents
  - added `Robustness / Stress Validation Preview` under `Backtest > Portfolio Proposal` Validation Pack
  - expanded validation input rows with period, contract, benchmark, CAGR / MDD, and compare evidence snapshots
  - added robustness route / score / blockers / input gaps / suggested sweeps for single candidate, in-progress proposal, and saved proposal validation
  - updated roadmap, doc index, Backtest UI flow docs, glossary, README, and comprehensive analysis for Phase 32 active status
- Decision:
  - Phase 32 first work unit is a read-only robustness input preview.
  - It does not run period split backtests, parameter sensitivity sweeps, live approval, or final portfolio selection yet.
- Hygiene:
  - py_compile, helper smoke, diff check, and finance refinement hygiene checks were run.
  - current candidate and Pre-Live registry validation passed; no registry row edits were needed.
  - Existing unrelated strategy logs, `uv.lock`, archived reset files, phase12 temp CSVs, and generated proposal registry artifact were left unstaged.

### 2026-05-03
- Completed Phase 32 implementation work units 2 through 4 after the user asked to continue through checklist handoff.
- Changed:
  - added `phase32_stress_summary_v1` stress / sensitivity result contract
  - added `Stress / Sensitivity Summary` table to the Portfolio Proposal Validation Pack
  - added Phase33 paper ledger handoff route / score / requirements
  - updated saved proposal validation summary rows with `Phase33 Handoff`
  - created Phase32 second / third / fourth work-unit documents
  - moved Phase32 to `implementation_complete` / `manual_qa_pending`
- Decision:
  - Phase32 remains read-only and does not execute period split backtests, benchmark sensitivity runners, parameter sweeps, paper ledger persistence, live approval, or final selection.
  - `Result Status = NOT_RUN` means the stress result contract is ready but no actual stress runner has filled results yet.
- Hygiene:
  - py_compile, saved proposal helper smoke, registry validation, diff check, Streamlit server health check, and finance refinement hygiene checks were run.

### 2026-05-03
- Closed Phase 32 after the user confirmed the checklist was complete.
- Changed:
  - preserved the user's checked Phase32 checklist items
  - moved Phase32 status to `complete` / `manual_qa_completed`
  - synced Phase32 TODO, completion summary, next phase preparation, roadmap, doc index, and comprehensive analysis
- Next direction:
  - Phase33 `Paper Portfolio Tracking Ledger` can open when the user approves the next phase start.
  - Phase30 remains `implementation_complete` / `manual_qa_pending` and is not changed by Phase32 closeout.
- Hygiene:
  - `check_finance_refinement_hygiene.py` was run.
  - Current candidate / Pre-Live registry validation passed; no registry row edits were needed.
### 2026-05-03
- Completed Phase 34 implementation work units 1 through 4 after the user asked to finish the phase through checklist handoff.
- Changed:
  - added `app/web/runtime/final_selection_decisions.py` and runtime exports for `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`
  - added Final Selection Decision evidence, save-readiness, row-building, display, and Phase35 handoff helpers
  - added `Final Selection Decision Pack`, `Save Final Selection Decision`, and saved final decision review under `Backtest > Portfolio Proposal`
  - created Phase34 second / third / fourth work-unit documents and updated checklist, completion summary, next-phase preparation, roadmap, doc index, operations guides, README, code-analysis docs, and comprehensive analysis
- Decision:
  - Phase34 final decision records are append-only selection / hold / reject / re-review judgments.
  - They are not live approval, broker orders, or automatic trading instructions.
  - Phase35 should read selected final decisions as input for a post-selection operating guide.
- Hygiene:
  - py_compile and helper smoke were run during implementation.
  - Existing unrelated strategy logs, `uv.lock`, archived reset files, phase12 temp CSVs, generated registries, and run history artifacts were left unstaged.

### 2026-05-03
- Reworked Phase 34 after the user challenged the repeated save-button flow.
- Changed:
  - split final validation / observation / judgment into a new `Backtest > Final Review` panel
  - kept `Backtest > Portfolio Proposal` focused on single-candidate direct readiness, multi-candidate proposal draft save, and saved proposal feedback
  - added `app/web/backtest_final_review.py` and `app/web/backtest_final_review_helpers.py`
  - removed the old Paper Ledger / Final Selection save surfaces from the active Portfolio Proposal flow
  - changed the user-facing final save action to `최종 검토 결과 기록`
  - moved paper observation criteria into the final review record instead of requiring a separate main-flow Paper Ledger save
  - rebuilt the Phase34 checklist around Portfolio Proposal boundary, Final Review source selection, validation / observation, final record, and Phase35 handoff
  - synced README, AGENTS, code analysis docs, operations guides, roadmap, doc index, glossary, comprehensive analysis, and Phase34 docs
- Decision:
  - Paper Portfolio Tracking Ledger remains as a compatibility / operating artifact.
  - The main Phase34 user flow is now `Portfolio Proposal draft -> Final Review -> 최종 검토 결과 기록`.
  - Final Review records remain append-only final select / hold / reject / re-review judgments, not live approval or orders.

### 2026-05-04
- Closed Phase 34 after the user confirmed `PHASE34_TEST_CHECKLIST.md` was complete.
- Changed:
  - preserved the user's checked Phase34 checklist items
  - moved Phase34 status to `complete` / `manual_qa_completed`
  - opened Phase35 `Post-Selection Operating Guide` as `active` / `not_ready_for_qa`
  - created the Phase35 plan / TODO / completion summary / next-phase preparation / checklist placeholder bundle under `.aiworkspace/note/finance/phases/phase35/`
  - synced roadmap, doc index, comprehensive analysis, glossary, phase docs, and durable logs
- Decision:
  - Phase35 starts from Phase34 `SELECT_FOR_PRACTICAL_PORTFOLIO` final review records.
  - Phase35 will turn selected records into rebalance / stop / reduce / re-review operating guidance.
  - Phase35 is not live approval, broker order, auto-trading, or an optimizer.
- Hygiene:
  - This was a documentation / phase-management closeout and kickoff unit.
  - Existing unrelated strategy logs, `uv.lock`, generated registries, run history artifacts, archived reset files, and phase12 temp CSVs were left unstaged.

### 2026-05-04
- Completed Phase 35 implementation work units 1 through 4 after the user asked to proceed through checklist handoff.
- Changed:
  - added `Backtest > Post-Selection Guide` as the final workflow panel
  - added `app/web/backtest_post_selection_guide.py` and helper logic for selected final decision input, readiness, operating policy, guide row creation, and saved guide review
  - added `app/web/runtime/post_selection_guides.py` and `.aiworkspace/note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl` as the append-only operating guide registry path
  - connected Final Review to Post-Selection Guide with a navigation button
  - updated Phase35 work-unit docs, checklist, roadmap, doc index, comprehensive analysis, README, AGENTS, code analysis docs, operations guide, glossary, and active skill guidance
- Decision:
  - Phase35 stores operating rules separately from final decisions so selection judgment and operating policy do not overwrite each other.
  - The user-facing action is one clear `운영 가이드 기록` button.
  - Post-Selection Guide remains disabled for live approval, broker order, and auto-trading.
- Hygiene:
  - py_compile and selected final decision input smoke were run.
  - Existing unrelated strategy logs, `uv.lock`, generated registries, run history artifacts, archived reset files, and phase12 temp CSVs were left unstaged.

### 2026-05-04
- Reworked Phase 35 after the user challenged the repeated save-button pattern.
- Changed:
  - removed the active `운영 가이드 기록` append-only save flow from `Backtest > Post-Selection Guide`
  - removed `app/web/runtime/post_selection_guides.py` and runtime exports for a separate post-selection operating guide registry
  - changed Post-Selection Guide into a no-extra-save final investment guide surface that reads Final Review decision records
  - added plain-language final verdict mapping: 투자 가능 후보 / 투자하면 안 됨 / 내용 부족 / 재검토 필요
  - changed Phase35 readiness routes to `FINAL_INVESTMENT_GUIDE_READY`, `FINAL_INVESTMENT_GUIDE_NEEDS_INPUT`, and `FINAL_INVESTMENT_GUIDE_BLOCKED`
  - updated the Phase35 checklist and durable docs so Final Review remains the source of truth and Phase35 is a read / preview surface
- Decision:
  - Phase35 should not create another required registry after Final Review.
  - Final Review's final selection decision remains the durable judgment.
  - Post-Selection Guide confirms final investment readiness and operating-before-live rules without creating live approval, broker orders, or auto-trading.

### 2026-05-04
- Simplified Phase35 again after the user concluded the separate Post-Selection Guide step was still too heavy for the current product stage.
- Changed:
  - removed the active Post-Selection Guide panel from Backtest workflow navigation
  - deleted `app/web/backtest_post_selection_guide.py` and `app/web/backtest_post_selection_guide_helpers.py`
  - kept `Backtest > Final Review` as the final active portfolio-selection panel
  - added saved final decision investment verdict display so final records read as 투자 가능 후보 / 내용 부족 / 투자하면 안 됨 / 재검토 필요
  - replaced Post-Selection navigation from Final Review with a disabled `Live Approval / Order` boundary action
  - rewrote Phase35 TODO, plan, work-unit docs, completion summary, next preparation, and checklist around `Portfolio Proposal -> Final Review -> 최종 판단 완료`
  - synced README, AGENTS, code-analysis docs, operations guides, roadmap, index, glossary, and comprehensive analysis to the simplified flow
- Decision:
  - The active user workflow ends at Final Review.
  - `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` is the final judgment source of truth.
  - No separate post-selection registry or active post-selection panel should be added unless the user explicitly reopens that design.

### 2026-05-04
- Fixed a Final Review saved-record display issue after the user noticed legacy Phase35 operating-guide wording in `기록된 최종 검토 결과 확인`.
- Changed:
  - added a Final Review status display translation layer for saved final decision rows
  - mapped existing selected / hold / reject / re-review records to current Final Review end-state wording
  - stopped showing legacy `Phase 35 운영 가이드 작성 가능` verdict / next action text in the route panel
  - updated the Phase35 checklist to include this regression check
- Decision:
  - Existing final decision JSON rows are not rewritten.
  - Legacy `phase35_handoff` data can remain in raw JSON for compatibility, but the UI should explain the record as Final Review completion.

### 2026-05-04
- Updated `Reference > Guides` after the user asked to align the guide with the current final-candidate workflow.
- Changed:
  - expanded the guide execution flow from the stale 1~7 / 1~8 framing to the current 1~10 flow
  - added a core concept guide for `Portfolio Proposal -> Final Review -> 최종 판단 완료`
  - updated stage pass criteria for 7->8, 8->9, 9->10, and final decision interpretation
  - refreshed the guide's document / file list with proposal, paper ledger, and final decision guide / registry paths
  - synced `BACKTEST_UI_FLOW.md`, the historical walkthrough note, and `FINANCE_DOC_INDEX.md` so they no longer imply a separate active Live Readiness / Post-Selection step
- Decision:
  - `Backtest > Final Review > 기록된 최종 검토 결과 확인` is the current final check for whether a portfolio was selected as a practical candidate.
  - Portfolio Proposal UI may still contain legacy `Live Readiness` route labels, but the current user-facing interpretation is Final Review input readiness.
  - `SELECT_FOR_PRACTICAL_PORTFOLIO` means selected as a practical candidate, not live approval, broker order, or auto-trading.

### 2026-05-04
- Improved `Reference > Guides > 문서와 파일 > 주요 파일 경로` after the user asked for clearer JSONL explanations.
- Changed:
  - split the file-path section into tabs for candidate review records, runtime / reusable records, and the full path list
  - added a visual JSONL storage map that explains what each registry stores, where it is created, and how to read it
  - clarified the difference between candidate notes, current candidate registry, Pre-Live records, proposal drafts, paper ledger compatibility rows, final selection decisions, run history, and saved portfolios
- Decision:
  - JSONL files should not be presented as bare paths in the guide.
  - The guide should make clear that only `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` is the final candidate-selection judgment source, while run history and saved portfolios are replay / reuse records.

### 2026-05-04
- Lightened repeated operator judgment UX after the user approved the proposed improvement direction.
- Changed:
  - changed Candidate Review Pre-Live input from `Operator Final Status` framing to `추천 운영 상태 확인` / `운영 상태 확인`
  - moved Candidate Review operating memo, next action, and review date into an optional expander with defaults
  - changed Portfolio Proposal `Operator Decision` framing to `Proposal 저장 상태`
  - moved Portfolio Proposal memo and next review date into an optional expander with defaults
  - added a Final Review notice that only the Final Review `최종 판단` is the main practical-candidate decision surface
  - moved Final Review decision id, operating constraints, and next action into an advanced expander
  - updated Phase35 TODO / checklist / completion summary and Backtest UI flow docs
- Decision:
  - The registry contracts remain unchanged.
  - Intermediate records stay useful as preparation / operating notes, but they should not feel like repeated final decisions.

### 2026-05-04
- Fixed a Final Review dataframe serialization warning reported by the user.
- Changed:
  - converted mixed numeric / string `Current` values in the inline paper observation checks to strings before rendering
- Decision:
  - The warning was not a final review logic failure, but it was a real UI hygiene issue because Streamlit logged an Arrow conversion traceback on each Final Review visit.

### 2026-05-04
- Captured the Phase35-after product gap after the user asked to save the discussion as a Markdown note.
- Changed:
  - added `.aiworkspace/note/finance/operations/FINAL_SELECTED_PORTFOLIO_OPERATIONS_DASHBOARD_GAP_20260504.md`
  - registered the note in `.aiworkspace/note/finance/operations/README.md` and `.aiworkspace/note/finance/FINANCE_DOC_INDEX.md`
- Decision:
  - The next most natural product direction is a final-selected portfolio operations dashboard, not another candidate-selection save/review step.

### 2026-05-05
- Improved `Backtest > Compare & Portfolio Builder` after the user asked to make GTAA / Equal Weight mix creation and saved portfolio reuse easier to understand.
- Changed:
  - split the Compare workspace into `전략 비교` and `저장 Mix 다시 열기` tabs
  - kept compare execution, weighted portfolio construction, result review, and save CTA in the `전략 비교` tab
  - moved saved portfolio list / load / replay / delete into the `저장 Mix 다시 열기` tab
  - added quick allocation buttons for `GTAA 70 / EW 30` and `GTAA 50 / EW 50`
  - renamed save/replay UI wording toward `Portfolio Mix` so saved setups are not confused with candidate registries
- Decision:
  - `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl` remains the persistence location because these rows are reusable replay setups, not append-only candidate / proposal / final-decision registry rows.

### 2026-05-05
- Added Equal Weight Real-Money first-pass support after the user noticed its Compare 진입 평가 lacked a proper Real-Money judgment.
- Changed:
  - added Equal Weight runtime Real-Money hardening with cost-adjusted result, benchmark overlay, price freshness, ETF operability policy, promotion / shortlist / deployment metadata
  - added Equal Weight Real-Money Contract inputs in Single Strategy and Compare strategy boxes
  - preserved Equal Weight Real-Money fields in saved Portfolio Mix overrides and Candidate Library replay payloads
  - updated Backtest UI / runtime flow docs and the finance comprehensive map to reflect the new Equal Weight boundary
- Verification:
  - `py_compile` passed for the touched Backtest UI/runtime modules
  - DB-backed Equal Weight smoke confirmed `real_money_hardening`, `promotion_decision`, `shortlist_status`, and `deployment_readiness_status` are now emitted
- Note:
  - the tested Equal Weight baskets currently report `etf_operability_status=caution` because asset profile coverage is partial, so they may still be `hold/blocked`; that is now an explicit gate result rather than a missing judgment.

### 2026-05-05
- 정리 / 검증:
  - user request에 따라 `Equal Weight Dividend Growth 4 (DGRW/SCHD/TDIV/VIG)` current candidate에 `inactive` tombstone row를 append해 Candidate Library 최신 active view에서 제외했다.
  - Equal Weight ETF Real-Money gate 검증을 위해 주요 ETF 후보군의 `nyse_asset_profile` AUM / bid / ask metadata를 yfinance 기반 idempotent UPSERT로 보강했다.
  - `Equal Weight Growth/Commodity 4 (QQQ/SOXX/XLE/IAU)`는 보강 후 `real_money_candidate / paper_probation / paper_only`, CAGR 19.96%, MDD -19.71%, SPY CAGR 13.67%, SPY MDD -24.80%로 runtime 재검증을 통과했다.
- 후보 탐색:
  - 배당 ETF 포함 Equal Weight 후보군을 3~5개 symbol, SPY 초과 CAGR, MDD 20% 이하 기준으로 재탐색했다.
  - 가장 깔끔한 후보는 `IAU / QQQ / SOXX / VIG / XLE`, annual rebalance였다. Runtime 기준 CAGR 18.31%, MDD -19.27%, `real_money_candidate / paper_probation / paper_only`를 만족한다.
  - SCHD 포함 후보는 성과상 SPY를 초과하는 조합이 있었지만, 현재 rolling validation에서 `hold/blocked` 또는 `watchlist_only`로 남아 10단계 실습 후보로는 VIG 포함 5종 후보가 더 깨끗하다.
  - user request에 따라 `Equal Weight Dividend+Growth Balanced 5 (IAU/QQQ/SOXX/VIG/XLE)`를 Current Candidate Registry에 active row로 append해 Candidate Library에 노출했다.

### 2026-05-05
- GTAA SPY benchmark 후보 탐색:
  - user request에 따라 `SPY`를 formal benchmark로 두고 `top=2~4`, universe 6~12개, `interval<=3` 조건의 GTAA 후보를 병렬 탐색했다.
  - 가장 깔끔한 후보는 `QQQ / SOXX / MTUM / QUAL / USMV / IAU / IEF / TLT`, `top=2`, `interval=3`, `1M/6M/12M`, `MA250`, `cash_only`였다.
  - Runtime 재검증 결과 `CAGR=18.97%`, `MDD=-18.10%`, `SPY CAGR=13.36%`, `SPY MDD=-15.90%`, `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Deployment=paper_only`, `Validation=normal`을 만족했다.
  - 더 높은 CAGR 후보(`SPY/QQQ/SOXX/XLE/XLU/XLV/IEF/IAU`)도 있었지만 `Deployment=review_required`로 남아 10단계 실습 후보로는 위 후보가 더 깨끗하다.
  - 결과를 `GTAA_BACKTEST_LOG.md`에 append했다. Candidate Library 등록은 아직 하지 않았다.

### 2026-05-05
- GTAA SPY benchmark 저MDD 후보 재탐색:
  - user request에 따라 수익률을 조금 낮추더라도 `MDD<=15%`, `CAGR>=16~17%`, `top=2~4`, `interval<=3`, 10단계 통과 조건을 만족하는 후보를 추가 탐색했다.
  - 대표 후보는 `QQQ / SOXX / MTUM / QUAL / USMV / IAU / IEF / TLT`, `top=3`, `interval=3`, `1M/6M`, `MA250`, `cash_only`, `Benchmark=SPY`였다.
  - Runtime 재검증 결과 `CAGR=19.35%`, `MDD=-11.03%`, `SPY CAGR=13.36%`, `SPY MDD=-15.90%`, `Promotion=real_money_candidate`, `Shortlist=paper_probation`, `Deployment=paper_only`, `Validation=normal`을 만족했다.
  - 결과를 `GTAA_BACKTEST_LOG.md`에 append했다. Candidate Library 등록은 아직 하지 않았다.

### 2026-05-05
- GTAA SPY Low-MDD 후보 Candidate Library 등록:
  - user request에 따라 `GTAA SPY Low-MDD Style Top-3` 후보를 `.aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`에 active current candidate row로 append했다.
  - `registry_id=gtaa_current_candidate_spy_low_mdd_style_top3_i3_1m6m_ma250`.
  - Registry validation 결과 required field 누락 없이 통과했다.

### 2026-05-05
- Equal Weight + GTAA mix 후보 탐색:
  - user request에 따라 `GTAA SPY Low-MDD Style Top-3`와 함께 쓸 Equal Weight 후보를 symbol 3~5개, interval 6~12개월, benchmark `SPY`, 10단계 통과, MDD 15% 근처 조건으로 탐색했다.
  - 엄격히 Equal Weight 단독 `MDD<=15%`와 `Promotion=real_money_candidate / Deployment=paper_only / Validation=normal`을 동시에 만족하는 후보는 찾지 못했다.
  - 대표 실사용 후보는 `QQQ / SOXX / XLE / XLU / GLD`, annual rebalance다. 단독 기준 `CAGR=17.55%`, `MDD=-18.98%`, `Promotion=real_money_candidate`, `Deployment=paper_only`, `Validation=normal`.
  - `GTAA 70 / EW 30` mix는 `CAGR=18.74%`, `MDD=-10.30%`, `Sharpe=2.51`; `GTAA 60 / EW 40` mix는 `CAGR=18.52%`, `MDD=-10.04%`, `Sharpe=2.54`.
  - 결과를 `EQUAL_WEIGHT.md`와 `EQUAL_WEIGHT_BACKTEST_LOG.md`에 기록했다.

### 2026-05-06
- Portfolio Mix 저장:
  - user request에 따라 `GTAA SPY Low-MDD Style Top-3 60% + Equal Weight Growth/Sector/Gold 5 40%` mix를 `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl`에 저장했다.
  - `portfolio_id=portfolio_gtaa_spy_low_mdd_60_ew_growth_sector_gold_40`.
  - 저장 row는 `Compare & Portfolio Builder > 저장 Mix 다시 열기`에서 다시 불러와 replay할 수 있는 reusable setup이다.

### 2026-05-06
- Compare 결과 노출 흐름 수정:
  - user report에 따라 `Run Strategy Comparison` 또는 `Replay Saved Mix` 후 5단계 Compare 결과가 눈에 보이지 않는 문제를 확인했다.
  - 원인은 saved mix replay 후에도 사용자가 `저장 Mix 다시 열기` 영역에 머물 수 있고, compare 결과가 `전략 비교` 영역 안쪽에 렌더링되어 결과가 숨은 것처럼 보이는 UX였다.
  - `Compare & Portfolio Builder` 내부 전환을 상태 기반 선택 UI로 바꾸고, replay / load / 새 compare 실행 후에는 `전략 비교` 화면으로 돌아오게 했다.
  - 최신 compare 결과는 `전략 비교` 화면 상단의 `5단계 Compare 결과` 박스에 먼저 렌더링하도록 이동했다.
  - 후속 bugfix: Streamlit widget key를 생성 후 직접 수정해 발생한 `backtest_compare_workspace_mode cannot be modified` 오류를 막기 위해, 화면 전환은 `backtest_compare_workspace_mode_request` pending flag로 요청하고 다음 rerun에서 widget 생성 전 적용하도록 변경했다.

### 2026-05-06
- Compare 단계 표현 변경 롤백 및 작업 규칙 보강:
  - user request에 따라 직전 `Compare 통과 판단 단계 표현 정리` 커밋을 revert했다. `Replay Saved Mix` 화면 전환 오류 수정은 유지했다.
  - user feedback을 반영해 단순 label 변경으로 UX / 단계 혼란을 해결하려 하지 말고, 먼저 흐름 구조와 stage ownership을 설명한 뒤 `진행할까요?` 확인을 받도록 `AGENTS.md`에 지침을 추가했다.
  - 향후 Compare / Candidate Review 단계 개편은 5단계 확인 위치와 6단계 handoff가 자연스럽게 이어지는 화면 구조를 먼저 제안한 뒤 진행한다.

### 2026-05-06
- Compare 5단계 / 6단계 handoff UX 개편:
  - user confirmation 후 `5단계 Compare 결과` 안에서 6단계 평가가 섞여 보이던 구조를 개선했다.
  - Compare 결과 상단에 `5단계 Compare 검증 보드`를 두고 PASS / CONDITIONAL / FAIL, Readiness, Data Trust, 4개 검증 기준을 명시적으로 보여주도록 변경했다.
  - `Send Selected Strategy To Candidate Review` 버튼은 `다음 행동` 영역으로 분리해, 버튼을 누른 뒤부터 6단계 Candidate Review가 시작된다는 경계를 화면에 남겼다.
  - `Replay Saved Mix`는 `저장 Mix Replay 결과`와 `구성 전략 Compare 검증`을 나누어 표시해 mix 자체 결과와 개별 전략 handoff 검증을 구분하게 했다.
  - `Reference > Guides`와 `BACKTEST_UI_FLOW.md`의 5단계 / 6단계 설명을 같은 흐름으로 갱신했다.

### 2026-05-06
- Saved Mix replay UX 후속 개편:
  - user confirmation 후 `Replay Saved Mix`가 더 이상 `전략 비교` 화면으로 강제 이동하지 않도록 변경했다.
  - `저장 Mix 다시 열기` 화면 안에서 replay 결과, `Portfolio Mix 검증 보드`, weighted portfolio 상세 결과를 바로 확인하게 했다.
  - mix 검증 보드는 `Saved Mix Replay`, `Mix Data Trust`, `Component Real-Money`, `Workflow Registry`를 따로 보여주며, saved mix setup과 5~10단계 workflow registry 기록을 구분한다.
  - `portfolio_gtaa_spy_low_mdd_60_ew_growth_sector_gold_40` 같은 saved setup은 replay 성과가 있어도 proposal / final review registry에 기록되지 않았으면 `Workflow Registry=NOT RECORDED`로 표시된다.
  - `Reference > Guides`와 `BACKTEST_UI_FLOW.md`를 같은 경계로 갱신했다.

### 2026-05-06
- Saved Mix -> Portfolio Proposal handoff 정리:
  - user confirmation 후 `저장 Mix 다시 열기 > Portfolio Mix 검증 보드`에서 workflow 기록이 없는 saved mix를 바로 `Portfolio Proposal` 초안으로 보낼 수 있게 했다.
  - 이 경로는 단일 후보를 만드는 `Candidate Review`가 아니라, 이미 비중이 정해진 portfolio mix를 proposal draft로 남기는 경로임을 UI와 Guides에 명시했다.
  - Portfolio Proposal은 saved mix prefill이 있을 때 전용 작성 화면을 먼저 보여주고, 저장 시 `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl`의 setup과 `.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` workflow 기록을 연결한다.
  - Final Review에서 saved mix proposal을 읽을 때 component contract / benchmark / universe / compare evidence가 빠지지 않도록 proposal evidence snapshot을 보강했다.

### 2026-05-06
- Phase36 시작:
  - user confirmation에 따라 `Final-Selected Portfolio Monitoring And Rebalance Operations` phase를 열었다.
  - Phase36의 첫 구현 목표는 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`을 새로 쓰는 것이 아니라, Final Review에서 이미 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 선정된 row를 읽어 `Operations > Selected Portfolio Dashboard`에서 운영 대상으로 보여주는 것이다.
  - 이번 작업에서는 current price / account holding 기반 drift 계산과 주문 초안은 제외하고, 최종 선정 포트폴리오 목록 / 상태 / target allocation / evidence / disabled execution boundary를 먼저 구현한다.

### 2026-05-06
- Phase36 first pass 구현 완료:
  - `app/web/runtime/final_selected_portfolios.py` read model을 추가해 Final Review selected decision row를 dashboard row와 status summary로 변환했다.
  - `Operations > Selected Portfolio Dashboard` page를 추가해 summary cards, selected portfolio table, status / source / benchmark filters, target allocation, evidence checks, operator next action, disabled execution boundary를 표시한다.
  - Phase36 plan / TODO / first work unit / checklist / completion / next-phase preparation과 roadmap / index / code analysis / comprehensive map / README / Guides를 동기화했다.
  - Verification: `PYTHONPYCACHEPREFIX=/tmp/codex_pycache python3 -m py_compile ...`, runtime helper smoke, `git diff --check`, `check_finance_refinement_hygiene.py` 통과.
  - 남은 gate는 사용자 manual QA다.

### 2026-05-06
- Phase36 current weight / drift check 구현:
  - user request에 따라 Phase36 QA를 마지막으로 미루고 다음 작업을 계속 진행했다.
  - `build_selected_portfolio_drift_check` helper를 추가해 component별 target weight와 operator가 입력한 current weight를 비교한다.
  - `Operations > Selected Portfolio Dashboard` 상세에 `Current Weight / Drift Check`를 추가했다.
  - `Rebalance threshold`, `Watch threshold`, `Total tolerance`를 입력받고 `DRIFT_ALIGNED`, `DRIFT_WATCH`, `REBALANCE_NEEDED`, `DRIFT_INPUT_INCOMPLETE`로 read-only 판정한다.
  - 실제 DB current price 조회, account holding 연결, broker order, auto rebalance는 계속 제외했다.

### 2026-05-06
- Phase36 value / holding input drift check 확장:
  - `finance/loaders/price.py`에 symbol별 latest price 조회 helper를 추가했다.
  - `build_selected_portfolio_current_weight_inputs` helper를 추가해 current value 또는 shares x price 입력을 current weight로 변환한다.
  - `Operations > Selected Portfolio Dashboard`의 drift check 입력 모드를 current weight 직접 입력, current value 입력, shares x price 입력으로 확장했다.
  - shares x price 입력에서는 DB latest close를 보조로 불러올 수 있지만, 값은 저장하지 않고 account holding 자동 연결 / 주문 생성도 하지 않는다.
  - Phase36 문서, roadmap / index / code analysis / comprehensive map / README를 value / holding input 기준으로 동기화했다.

### 2026-05-06
- Phase36 drift alert / review trigger preview 추가:
  - `build_selected_portfolio_drift_alert_preview` helper를 추가해 drift check 결과를 운영 경고 없음 / 관찰 경고 / 리밸런싱 검토 경고 / 입력 확인 경고로 변환했다.
  - `Operations > Selected Portfolio Dashboard` 상세에서 Final Review review trigger와 drift alert row를 함께 보여준다.
  - 이 preview는 alert registry를 저장하지 않고, live approval / broker order / auto rebalance도 계속 disabled로 둔다.
  - Phase36 checklist / completion / next phase preparation과 roadmap / index / code analysis / comprehensive map / README를 alert preview 기준으로 동기화했다.

### 2026-05-06
- Guides 포트폴리오 플로우 맵 UX polish 시작:
  - user request에 따라 `Reference > Guides`의 1~10 단계 실행 흐름을 선형 텍스트만으로 읽기 어렵다는 문제를 확인했다.
  - 단일 후보, 다중 후보 portfolio proposal, saved mix, 재검토 / blocker 경로를 시각적 flow map으로 분리해 보여주는 Guide 보강을 진행한다.
  - 변경 범위는 `app/web/streamlit_app.py`와 Backtest UI flow 문서 동기화로 제한하고, core finance 로직과 JSONL runtime artifact는 수정하지 않는다.
- 구현:
  - `Reference > Guides`의 `1~10 단계 실행 흐름` 앞에 `포트폴리오 플로우 맵`을 추가했다.
  - 경로 선택은 단일 후보, 여러 후보 포트폴리오, 저장 Mix, 재검토 / 막힘 경로로 나누고, 각 경로를 카드형 순서도 / 사용 상황 / 생략되는 단계 / 생성 또는 참조 기록 표로 보여준다.
  - `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`의 Guides 묶음 설명을 다섯 묶음 기준으로 동기화했다.
- 검증:
  - `py_compile`로 `app/web/streamlit_app.py`, `app/web/pages/backtest.py`, `app/web/backtest_*.py`를 확인했다.
  - worktree Streamlit 서버를 `127.0.0.1:8502`에 띄우고 `Reference > Guides`에서 플로우 맵 렌더링과 경로 선택 동작을 확인했다.
  - `git diff --check`와 finance refinement hygiene helper를 통과했다.

### 2026-05-06
- Guides 제품형 UX 개편:
  - user feedback에 따라 `Reference > Guides`가 실습 문서 목록처럼 보이고, flow map도 카드 나열에 가까운 문제를 확인했다.
  - Guide 렌더링을 `app/web/reference_guides.py`로 분리하고, `streamlit_app.py`는 page shell / navigation 중심 책임을 유지하게 했다.
  - 첫 화면을 `Portfolio Selection Guide` hero, 경로 선택, route summary, GraphViz 기반 `Portfolio Flow`, `Decision Gates`, `Reference Drawer`, 접힘 `System status` 구조로 개편했다.
  - Runtime / Build는 사용자의 첫 guide 경험에서 제외하고 하단 `System status`로 낮췄다.
  - 외부 dependency는 추가하지 않았고, GraphViz 렌더링 실패 시 compact visual fallback을 사용하도록 했다.
  - 검증: `py_compile`, `git diff --check`, finance refinement hygiene helper를 통과했고, `127.0.0.1:8502/guides`에서 GraphViz flowchart 렌더링과 route selector 동작을 확인했다.

### 2026-05-06
- Guides 단계 해석 보강:
  - user feedback에 따라 GraphViz flowchart는 좋아졌지만 노드 내용이 얕고, 기존 1~10 단계 위치감이 약해진 문제를 확인했다.
  - `Reference > Guides`에 선택 경로별 핵심 checkpoint 카드와 `전체 1~10 단계` compact timeline을 추가했다.
  - timeline은 단일 후보, 여러 후보 포트폴리오, 저장 Mix, 막힘 해결 경로에 따라 `필수`, `반복`, `직행`, `선행`, `생략`, `보류` 같은 상태 라벨을 다르게 보여준다.
  - GraphViz node 문구도 `Run + Data Trust`, `Review + Registry`, `Validation + Decision`처럼 조금 더 정보성 있게 보강하되, 긴 설명은 timeline / checkpoint 패널로 분리했다.

### 2026-05-06
- Guides 경로 라벨 / 배치 polish:
  - user feedback에 따라 `저장 Mix`, `막힘 해결`, `이 경로의 핵심 단계`, `현재 경로 / 다음 행동` 카드가 무엇을 의미하는지 애매한 문제를 확인했다.
  - Guide 선택지를 `단일 후보`, `여러 후보 묶음`, `저장된 비중 조합`, `보류 / 재검토`로 정리했다.
  - `전체 1~10 단계에서 현재 위치`를 선택 버튼 바로 아래로 올리고, 그 아래에 `선택한 경로 요약`, `Portfolio Flow`, 선택 경로별 checkpoint를 배치했다.
  - 여러 후보 묶음 경로는 Candidate Review 저장이 선행이고 Portfolio Proposal은 이미 저장된 후보를 묶는 화면이라는 ownership을 문구로 명확히 했다.

### 2026-05-06
- Phase36 Selected Portfolio Dashboard 목적 재설계:
  - user feedback에 따라 기존 dashboard가 JSON inspection / drift 입력 화면처럼 보여 선정 포트폴리오의 성과 모니터링 목적이 흐려지는 문제를 확인했다.
  - `Operations > Selected Portfolio Dashboard`를 Snapshot / Performance Recheck / What Changed / Allocation Check / Audit 구조로 재배치했다.
  - Performance Recheck는 Final Review에서 선정된 component의 replay contract를 사용자가 지정한 start / end와 virtual capital로 다시 실행해 최신 성과, benchmark spread, component contribution, 강한 / 약한 기간을 보여준다.
  - raw JSON은 접힘 Audit 영역으로 이동했고, 실제 보유 drift는 optional advanced Allocation Check로 낮췄다.
  - Phase36 plan / TODO / first work unit / completion / next-phase preparation / checklist와 roadmap / doc index / comprehensive map / README / code analysis flow를 동기화했다.
  - Verification: `py_compile`, performance recheck defaults / replay smoke, `git diff --check`, finance refinement hygiene helper, Streamlit `127.0.0.1:8505` browser smoke를 통과했다.

### 2026-05-07
- Phase36 Selected Portfolio Dashboard UX 구조 polish:
  - user feedback에 따라 데이터 출처 / 운영 대상 목록 / Snapshot / Performance Recheck / Allocation / Operator Context의 좁은 화면 배치와 의미 연결 문제를 확인했다.
  - 데이터 출처와 화면 경계는 wrapping card와 접힘 registry path로 바꿨다.
  - 운영 대상 목록은 compact table, 짧은 portfolio selector, responsive filter layout으로 정리했다.
  - Snapshot은 selection summary와 Portfolio Blueprint로 재구성하고 target allocation을 포트폴리오 정의 영역으로 이동했다.
  - Performance Recheck 결과는 `Summary`, `Equity Curve`, `Result Table`, `What Changed`, `Contribution`, `Extremes` tab으로 분리했다.
  - Operator Context는 `Monitoring Playbook`으로 바꿔 Selection Evidence / Review Triggers / Holding Drift Check / Execution Boundary를 같은 흐름에서 읽게 했다.
  - Verification: py_compile, `git diff --check`, finance refinement hygiene helper, Streamlit browser smoke, 390px narrow viewport smoke 통과.

### 2026-05-07
- Phase36 Monitoring Playbook Trigger Board 정리:
  - user feedback에 따라 기존 Review Triggers tab이 operator note와 trigger list를 나열하는 수준이라 운영 판단 보드로 보기 어렵다는 문제를 확인했다.
  - Review Triggers tab을 `Trigger Board`로 바꾸고, Final Review evidence / CAGR deterioration / MDD expansion / benchmark underperformance / Holding drift row를 표시하게 했다.
  - Trigger Board는 최신 Performance Recheck 결과와 Holding Drift Check 입력 상태를 읽어 `Clear`, `Watch`, `Breached`, `Needs Input`으로 번역한다.
  - operator reason / constraints / next action / 원본 trigger list는 `Original Operator Notes` expander로 낮췄다.
  - Trigger Board와 drift 결과는 계속 read-only이며 새 registry row나 주문 row를 만들지 않는다.

### 2026-05-07
- Phase36 Selected Portfolio Dashboard flow 재정렬:
  - user feedback에 따라 source boundary, 운영 대상 필터, Portfolio Blueprint, Monitoring Playbook, Holding Drift Check가 주 성과 재검증 흐름을 흐리는 문제를 확인했다.
  - 데이터 출처 / registry path / raw JSON은 `Audit / Developer Details`로 낮추고, 운영 대상이 1개일 때는 compact selected portfolio picker만 보여주게 했다.
  - Snapshot은 단일 component 100% target allocation table을 접힘 details로 낮추고, Performance Recheck setup은 Original End / DB Latest badge와 primary 실행 버튼으로 재배치했다.
  - Monitoring Playbook을 `Portfolio Monitoring`으로 바꾸고 `Review Signals`, `Why Selected`, `Actual Allocation`, `Audit` 흐름으로 정리했다.
  - Holding Drift Check는 `Actual Allocation Check`로 바꿔 current value 입력을 기본으로 두고, shares x price / current weight / threshold 설정은 advanced 영역으로 낮췄다.
  - Actual Allocation 결과는 사용자가 `Update Review Signals`를 누를 때만 Review Signals에 반영하도록 변경했다.

### 2026-05-06
- Ops Review 운영 대시보드 개편:
  - user confirmation에 따라 기존 `Ops Review`의 최근 결과 / history / logs / failure CSV 나열형 UI를 운영 상태 판독 화면으로 개편했다.
  - 렌더링 책임을 `app/web/ops_review.py`로 분리하고, `streamlit_app.py`는 page entry와 navigation만 유지하게 했다.
  - 상단 triage flow, run health cards, action inbox, 선택 run inspector, failure CSV / related logs / artifact index, 다음 이동 안내, system snapshot을 추가했다.
  - job 실행은 `Workspace > Ingestion`, backtest replay는 `Operations > Backtest Run History`, 후보 replay는 `Operations > Candidate Library`가 맡는 경계를 UI와 flow 문서에 명시했다.

### 2026-05-07
- Compare / saved mix 검증 ownership 정리:
  - user feedback에 따라 `Load Saved Mix Into Compare -> Run Strategy Comparison -> 5단계 Compare 결과` 흐름이 저장 mix 검증처럼 보이는 UX 문제를 확인했다.
  - Compare workspace를 `개별 전략 비교`와 `저장된 비중 조합` 용어로 분리하고, 5단계 Compare 보드는 개별 전략 후보만 Candidate Review로 넘기는 판단임을 명시했다.
  - 저장 mix 화면의 primary action은 `Mix 재실행 및 검증`으로 바꾸고, 기존 load action은 `전략 비교에서 수정하기`라는 편집 / 재구성 경로로 낮췄다.
  - GTAA `interval > 1`, `month_end`에서 요청 종료일이 다음 정상 cadence close 전이면 Data Trust hard block이 아니라 cadence-aligned review로 해석하도록 Compare data trust helper를 보정했다.
  - `Portfolio Mix 검증 보드`는 saved mix의 replay, mix data trust, component Real-Money, workflow registry 기록 여부를 mix-level로 읽고 `포트폴리오 후보 초안으로 보내기`로 Portfolio Proposal에 연결한다.
  - `Reference > Guides`와 `BACKTEST_UI_FLOW.md`를 새 용어와 단계 ownership 기준으로 동기화했다.

### 2026-05-08
- Backtest 후보 선정 workflow 3단계 재설계 사전 분석:
  - user feedback에 따라 Candidate Review / Portfolio Proposal / Final Review가 반복 저장과 중복 비중 조합처럼 보이는 구조를 깊게 분석했다.
  - sub-agent 4개 트랙으로 navigation / Candidate Review registry / Portfolio Proposal-Final Review schema / Guides 문서 영향을 분리 조사했다.
  - 구현 전 기준 문서 `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`를 추가했다.
  - 핵심 판단은 5개 panel label을 바로 3개로 치환하지 않고, visible stage와 legacy internal route를 먼저 분리하는 것이다.
  - 아직 제품 코드는 수정하지 않았다. 다음 단계는 사용자가 guide 방향을 확인한 뒤 route foundation부터 구현하는 것이다.

### 2026-05-10
- Backtest 후보 선정 workflow 재설계 가이드 보강:
  - user feedback에 따라 기존 JSONL을 꼭 main source로 유지하지 않고 archive한 뒤 Clean V2 저장 구조로 다시 시작하는 옵션을 문서화했다.
  - `PORTFOLIO_SELECTION_SOURCES`, `PRACTICAL_VALIDATION_RESULTS`, `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2`, `SELECTED_PORTFOLIO_MONITORING_LOG`, `SAVED_PORTFOLIO_MIXES`의 역할을 정리했다.
  - 사용자가 `Backtest Analysis -> Practical Validation -> Final Review -> Selected Portfolio Dashboard`를 어떻게 지나 최종 후보 선정과 사후관리를 하는지 end-to-end flow를 추가했다.
  - 제품 코드는 아직 수정하지 않았다. 다음 구현은 Clean V2 storage foundation과 route/stage 분리부터 시작하는 것이 맞다.

### 2026-05-10
- Backtest 후보 선정 workflow Clean V2 1차 구현:
  - `Backtest Analysis -> Practical Validation -> Final Review` 3단계 stage routing을 추가하고 legacy panel request를 새 stage로 매핑했다.
  - `app/web/runtime/portfolio_selection_v2.py`를 추가해 selection source, practical validation result, final decision v2, monitoring log, saved mix helper를 정의했다.
  - Single / History / Compare focused strategy / Saved Mix handoff가 Clean V2 selection source를 만들고 Practical Validation으로 이동하도록 연결했다.
  - Final Review는 Practical Validation result를 읽어 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`에 저장하고, Selected Portfolio Dashboard는 V2 decision registry를 읽도록 바꿨다.
  - 기존 Candidate Review / Portfolio Proposal 코드는 삭제하지 않고 legacy compatibility로 유지했다.

### 2026-05-10
- Compare weighted mix Practical Validation handoff UX 보강:
  - user feedback에 따라 방금 만든 weighted portfolio mix를 저장 mix round-trip 없이 Practical Validation으로 보낼 수 없는 문제를 확인했다.
  - `Weighted Portfolio Result` 아래에 `현재 Mix를 Practical Validation으로 보내기` action을 추가해 mix 전체를 Clean V2 selection source로 저장하게 했다.
  - 저장 mix의 `전략 비교에서 수정하기`는 기존 stale compare / weighted 결과를 숨기고, 저장된 전략 / 기간 / 세부 설정 / weight를 form-first 상태로 다시 채우도록 조정했다.
  - Compare / saved mix 문구와 `BACKTEST_UI_FLOW.md`를 Clean V2 Practical Validation ownership 기준으로 갱신했다.

### 2026-05-10
- Portfolio Mix 검증 보드 legacy 문구 정리:
  - user feedback에 따라 saved mix 판정 문구에 남아 있던 `5~10단계 workflow 통과 기록` 표현을 Clean V2 기준으로 교체했다.
  - saved mix 기록 참조 확인 대상에 `PORTFOLIO_SELECTION_SOURCES`, `PRACTICAL_VALIDATION_RESULTS`, `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2`, `SELECTED_PORTFOLIO_MONITORING_LOG`를 추가했다.

### 2026-05-10
- Practical Validation V2 검증 설계 조사 / 문서화:
  - user request에 따라 현재 Practical Validation이 실제로 검증하는 항목과 실전 후보 검증으로 부족한 부분을 정리했다.
  - CFA backtesting / GIPS / SEC performance presentation / SR 11-7 model validation / overfitting / transaction cost / ETF liquidity reference를 조사해 검증 domain으로 번역했다.
  - `.aiworkspace/note/finance/tasks/active/practical-validation-v2/DESIGN.md`를 추가하고, source contract, replay, benchmark, rolling, drawdown, stress, cost, investability, sensitivity, overfit, monitoring plan domain과 구현 우선순위를 정리했다.
  - 제품 코드는 아직 수정하지 않았다. 다음 작업은 사용자가 설계를 확인한 뒤 Slice 1 domain board부터 구현하는 것이 맞다.
- Practical Validation V2 중복 검증 위험 보강:
  - user feedback에 따라 Practical Validation 이전 단계의 Data Trust / Real-Money / Compare / Saved Mix gate와 V2 설계가 겹칠 수 있는 지점을 확인했다.
  - Practical Validation은 upstream runtime / compare / saved mix 검증을 반복하지 않고 `origin`과 `source_ref`를 남겨 상속 / 통합 / 신규 계산 domain을 분리해야 한다고 정리했다.
  - 설계 문서에 Stage Ownership Matrix와 중복 감점 방지 원칙을 추가했다.
- Practical Validation V2 rolling / cost 기본값 확정:
  - user confirmation에 따라 profile별 rolling window 기본값을 방어형 24개월, 균형형 36개월, 성장형 60개월, 전술 / 헤지형 24개월, 사용자 지정 36개월로 정리했다.
  - cost assumption은 거래 수수료 / bid-ask spread / slippage / 세금성 비용을 포함한 거래비용 가정이며, MVP 기본값은 one-way 10 bps로 시작한다고 문서화했다.
  - research / design 문서의 설계 질문 상태에서 rolling window와 cost assumption 항목을 `O`로 변경했다.
- Practical Validation V2 stress calendar / sentiment connector 보강:
  - user request에 따라 2000년 이후 미국 증시 shock event를 `practical_validation_stress_windows_v1.json` static reference data로 추가했다.
  - stress window는 포트폴리오 curve / benchmark curve를 정적 이벤트 구간으로 잘라 return, MDD, benchmark spread를 계산하는 검증 preset으로 정리했다.
  - sentiment connector는 VIX / credit spread / yield curve 같은 market-context 지표를 Practical Validation에 snapshot으로 붙이는 후속 data adapter라고 문서화했다.
  - research / design 문서의 stress window 설계 질문 상태를 `O`로 변경했다.
- Practical Validation V2 baseline / sensitivity / trial-count 설계 완료:
  - user confirmation에 따라 Alternative Portfolio Challenge 1차 baseline을 SPY, QQQ, 60/40 proxy, cash-aware baseline으로 확정하고 All Weather-like proxy는 후속으로 정리했다.
  - sensitivity perturbation grid는 주요 window perturbation, mix weight +/- 5%p, drop-one, 기존 runtime 지원 범위의 strategy-specific 작은 설정 변경으로 시작한다고 문서화했다.
  - run_history trial count는 원본 파일을 저장하지 않고 `overfit_audit` local summary만 validation row에 선택적으로 남기는 방식으로 정리했다.
- Practical Validation V2 sentiment connector 설계 질문 완료:
  - user confirmation에 따라 sentiment connector는 1차 core 이후 후속 module로 붙이고, FRED 기반 VIX / credit spread / yield curve snapshot부터 시작한다고 확정했다.
  - 해당 데이터는 trade signal이나 hard blocker가 아니라 market-context evidence로만 사용한다고 research / design 문서에 반영했다.
- Practical Validation V2 core 구현:
  - `PRACTICAL_VALIDATION_RESULT_SCHEMA_VERSION`을 2로 올리고, 검증 프로필 / 5개 사용자 답변 / profile threshold resolver를 추가했다.
  - Practical Validation result에 Input Evidence와 12개 Practical Diagnostics board를 추가했다. 현재 구현은 asset allocation proxy, concentration / exposure, stress window coverage, alternative baseline placeholder, leveraged / inverse suitability, cost assumption, local trial count summary, monitoring baseline seed를 생성한다.
  - 아직 실제 return matrix 기반 correlation / risk contribution, baseline replay, stress 구간 성과 재계산, ETF expense / spread / ADV, macro / sentiment connector는 `NOT_RUN` 또는 `REVIEW`로 명시한다.
  - Practical Validation 화면은 profile 입력과 diagnostics board를 표시하고, BLOCKED가 없을 때만 Final Review로 보낸다.
  - Final Review 화면과 final decision snapshot은 Practical Diagnostics 요약 / NOT_RUN critical domain / profile evidence를 함께 읽도록 연결했다.
- Practical Validation V2 정량 진단 1차 보강:
  - profile별 domain weight와 score breakdown을 추가해 검증 profile 변경이 score 산정에 반영되도록 했다.
  - Backtest Analysis handoff에서 compact monthly result curve snapshot을 저장하고, 기존 source는 DB price proxy curve로 계산을 시도하도록 했다.
  - rolling validation, static stress window return / MDD / benchmark spread, SPY / QQQ / 60/40 / cash-aware baseline challenge, component correlation / risk contribution proxy, drop-one / weight +5%p sensitivity를 Practical Diagnostics에 연결했다.
  - ETF operability는 DB price / volume proxy와 one-way cost assumption으로 1차 확인하고, macro / sentiment는 FRED connector 전까지 benchmark price-action proxy로 표시한다.
  - Final Review에는 profile score breakdown, curve evidence, rolling evidence를 snapshot으로 남기도록 연결했다.
- Practical Validation V2 남은 구현 계획 문서화:
  - user request에 따라 추가 개발 전 검토용 문서 `.aiworkspace/note/finance/tasks/active/practical-validation-v2/IMPLEMENTATION_PLAN.md`를 추가했다.
  - 현재 구현 완료 범위와 proxy / NOT_RUN / REVIEW로 남은 범위를 12개 diagnostics domain별로 정리했다.
  - 다음 개발 순서를 helper split, actual runtime replay, benchmark parity, validation inspector, strategy-specific sensitivity, provider connector, Final Review / Selected Dashboard 고도화 순으로 제안했다.
  - 제품 코드는 수정하지 않았고, 사용자가 문서를 검토한 뒤 첫 구현 단위를 확정하는 상태다.
- Practical Validation V2 P0 actual replay / provenance 구현:
  - user confirmation에 따라 helper split, actual runtime replay, curve provenance, benchmark parity hardening을 단계별로 구현했다.
  - `backtest_practical_validation_curve.py`와 `backtest_practical_validation_replay.py`를 추가해 curve/parity와 기존 runtime replay 책임을 분리했다.
  - Practical Validation 화면에 `실제 전략 replay 실행` 버튼을 추가했고, 자동 실행 없이 사용자가 명시 실행할 때만 기존 strategy runtime을 호출한다.
  - validation result schema를 v3로 올리고 `curve_provenance`, `benchmark_parity`, `replay_attempt`를 저장하도록 했다.
  - ETF holdings-level look-through, expense / spread / AUM, FRED macro / sentiment connector는 아직 후속으로 남겼다.
- Practical Validation V2 P0 최신 재검증 의미 보정:
  - user feedback에 따라 동일 기간 replay가 Practical Validation에서 충분한 검증 가치가 있는지 재검토했다.
  - 3번 구간을 `최신 데이터 기준 전략 재검증`으로 바꾸고, 기본 모드는 DB 최신 시장일까지 종료일을 확장한 기존 strategy runtime 재검증으로 조정했다.
  - `저장 기간 그대로 재현`은 보조 모드로 남겼고, validation result schema를 v4로 올려 mode, 저장 기간, 요청 기간, 실제 기간, 최신 시장일, 확장 일수, period coverage, curve provenance를 남기도록 했다.
  - 실제 실행은 성공했지만 component cadence / date alignment 때문에 portfolio curve가 요청 종료일까지 오지 못하면 `period_coverage=REVIEW`로 표시하도록 했다.
  - 관련 code analysis 문서와 comprehensive analysis를 최신 재검증 기준으로 갱신했다.

### 2026-05-11
- Practical Validation V2 P2 개발 문서 정리:
  - user request에 따라 P2 실행 계획 문서 `.aiworkspace/note/finance/tasks/active/practical-validation-v2/CONNECTOR_AND_STRESS_PLAN.md`를 추가했다.
  - provider / DB / loader 상세 설계 문서 `.aiworkspace/note/finance/tasks/active/practical-validation-v2/PROVIDER_CONNECTORS.md`를 추가했다.
  - P2 범위를 Cost / Liquidity / ETF Operability connector, ETF holdings / sector look-through, Macro / Sentiment connector, Stress Interpretation, strategy-specific sensitivity runtime 경계로 정리했다.
  - `IMPLEMENTATION_PLAN.md`, `docs/architecture/README.md`, `FINANCE_DOC_INDEX.md`에 새 문서 링크를 반영했다.
  - 제품 코드는 수정하지 않았다. 다음 작업은 provider connector 첫 구현 단위 확정 후 진행한다.
- Practical Validation V2 provider 문서 compact 관리:
  - user feedback에 따라 별도 data collection plan 문서를 만들지 않기로 했다.
  - ETF holdings, macro series, sentiment series 수집 계획을 기존 `.aiworkspace/note/finance/tasks/active/practical-validation-v2/PROVIDER_CONNECTORS.md` 안에 합쳤다.
  - P2 문서 역할을 `P2 전체 계획`과 `provider 수집 / schema / loader 상세 설계` 두 개로 고정했다.
- Practical Validation V2 P2-1 schema / ingestion field 계약 확정:
  - P2-0에서 정한 8개 정상화 대상 진단을 실제 수집 / 저장 / 로딩 가능한 데이터 계약으로 변환했다.
  - 신규 table 후보를 `etf_operability_snapshot`, `etf_holdings_snapshot`, `etf_exposure_snapshot`, `macro_series_observation` 4개로 고정했다.
  - 각 table의 business key, actual / partial / bridge / proxy / NOT_RUN 판정 기준, ingestion 함수 계약, loader compact context 반환 기준을 문서화했다.
  - 제품 코드는 아직 수정하지 않았다. 다음 작업은 P2-2 Cost / Liquidity / ETF Operability schema와 수집 foundation 구현이다.
- Practical Validation V2 P2-2A ETF operability bridge/proxy foundation 구현:
  - `finance/data/db/schema.py`에 `PROVIDER_SCHEMAS["etf_operability_snapshot"]`를 추가했다.
  - `finance/data/etf_provider.py`를 추가해 기존 `nyse_price_history`와 `nyse_asset_profile` 기반 `db_bridge` operability snapshot을 생성하고 UPSERT 저장하게 했다.
  - `finance/loaders/provider.py`와 loader export를 추가해 `load_etf_operability_snapshot()` read path를 제공했다.
  - 현재 구현은 official issuer actual data 수집이 아니라 bridge/proxy foundation이다. expense ratio, NAV, premium/discount, official leverage/inverse metadata는 P2-2B actual provider 수집에서 보강한다.
  - code analysis / data architecture / comprehensive analysis 문서를 새 table과 loader 경계에 맞춰 갱신했다.
- Practical Validation V2 P2-2B ETF operability official issuer row 초기 구현:
  - `finance/data/etf_provider.py`에 iShares / SSGA / Invesco official page adapter를 추가했다.
  - 초기 source map은 iShares `AOR`, `IEF`, `TLT`, SSGA / SPDR `SPY`, `BIL`, `GLD`, Invesco `QQQ`다.
  - official row는 `etf_operability_snapshot`에 `source=ishares|ssga|invesco`, `source_type=official`, `coverage_status=actual|partial|missing|error`로 저장한다.
  - smoke ingestion 결과 `AOR/IEF/TLT/SPY/BIL/GLD`는 `actual`, `QQQ`는 official QQQ page에서 expense ratio / inception만 확보되어 `partial`로 저장됐다.
  - Practical Validation 진단 연결은 아직 하지 않았고 P2-5에서 loader context를 12개 진단에 연결한다.
- Practical Validation V2 P2-3 ETF holdings / exposure foundation 구현:
  - `finance/data/db/schema.py`에 `etf_holdings_snapshot`, `etf_exposure_snapshot` schema를 추가했다.
  - `finance/data/etf_provider.py`에 iShares holdings CSV, SSGA daily holdings XLSX, Invesco holdings / sector API adapter를 추가했다.
  - holdings는 기본 `canonical_refresh`로 fund / as_of_date / source 범위를 삭제 후 재저장하고, exposure는 holdings aggregate와 provider aggregate sector row를 저장한다.
  - smoke ingestion 결과 holdings는 `AOR/IEF/TLT/SPY/BIL/QQQ` 703 rows actual, `GLD`는 row-level holdings source pending으로 missing 처리됐다.
  - exposure smoke 결과 asset class / sector / country / currency exposure 49 rows actual이 저장되고 loader에서 SPY / QQQ sector aggregate를 확인했다.
  - Practical Validation 진단 연결은 아직 하지 않았고 P2-5에서 Asset Allocation Fit / Concentration / Exposure 진단에 연결한다.
- Practical Validation V2 P2-4 macro / sentiment market-context foundation 구현:
  - `finance/data/db/schema.py`에 `macro_series_observation` schema를 추가했다.
  - `finance/data/macro.py`를 추가해 FRED `VIXCLS`, `T10Y3M`, `BAA10Y` series를 API 또는 official CSV download로 수집하고 UPSERT 저장하게 했다.
  - FRED API key는 hardcode하지 않고 `FRED_API_KEY` 또는 함수 인자로만 받으며, key가 없으면 official CSV download를 사용한다.
  - `finance/loaders/macro.py`와 loader export를 추가해 observation range 조회와 기준일 snapshot / staleness 조회를 제공했다.
  - smoke ingestion 결과 2026-01-01~2026-05-11 구간에서 265 rows를 저장했고, 2026-05-11 기준 3개 series 모두 `snapshot_status=actual`로 로딩됐다.
  - Practical Validation 진단 연결은 아직 하지 않았고 P2-5에서 Regime / Macro Suitability와 Sentiment / Risk-On-Off Overlay 진단에 연결한다.
- Practical Validation V2 P2-5A provider snapshot ingestion UI / job wrapper 연결:
  - `app/jobs/ingestion_jobs.py`에 `run_collect_etf_operability_provider()`, `run_collect_etf_holdings_exposure()`, `run_collect_macro_market_context()`를 추가했다.
  - `Workspace > Ingestion > Practical Validation Provider Snapshots`에서 ETF operability, ETF holdings / exposure, macro context 수집을 실행할 수 있게 했다.
  - 이 단계는 Practical Validation 진단 점수 연결이 아니라, DB snapshot을 채우는 운영 실행 지점 연결이다. 12개 diagnostics provider context 연결은 P2-5B에서 진행한다.
  - smoke 결과 `AOR` operability `success 1 row`, `AOR` holdings / exposure `success 17 rows`, `VIXCLS` 2026-01-01~2026-01-05 macro `success 2 rows`를 확인했다.
- Practical Validation V2 P2-5B provider context diagnostics 연결:
  - `app/web/backtest_practical_validation_connectors.py`를 추가해 ETF operability / holdings / exposure / FRED macro loader 결과를 compact provider context로 변환했다.
  - Practical Validation 2, 3, 5, 6, 9, 10번 진단이 DB provider snapshot을 proxy보다 우선 사용하도록 연결했다.
  - official provider row가 부족하고 bridge / proxy만 있으면 `PASS`로 보이지 않도록 `REVIEW`와 `db_bridge` / `price_proxy` origin을 남기게 했다.
  - Practical Validation과 Final Review 화면에 Provider Coverage 요약 table을 추가했고, Final Review decision snapshot에는 compact provider coverage만 저장한다.
  - smoke 결과 AOR 기준 provider coverage는 operability / exposure / macro `PASS`, holdings concentration `REVIEW`로 표시되고 JSON serialization이 통과했다.

### 2026-05-12
- Practical Validation V2 provider snapshot 기준일 보정:
  - 2026-05-11 `saved_portfolio_mix` source에서 ETF Operability / Holdings Exposure가 수집 후에도 `NOT_RUN`으로 보이는 현상을 확인했다.
  - 원인은 source의 backtest `actual_end=2026-02-28`을 provider snapshot 조회 기준일로 사용해, 2026-05월에 수집된 provider row를 loader가 제외한 것이었다.
  - provider snapshot은 실전 투입 전 현재 검증 근거이므로 조회 기준일을 Practical Validation 실행일로 변경했다.
  - 같은 source 기준으로 operability는 38.5%, holdings / exposure는 30.5% coverage까지 읽히며, 전체 11개 ETF 중 미수집 symbol은 partial `REVIEW`로 남는 것을 확인했다.
- Practical Validation Provider Data Gaps UI / 일괄 수집 보강:
  - Provider Coverage 아래에 ETF별 `Operability / Holdings / Exposure` 부족 여부와 source map 상태를 표시하도록 했다.
  - 같은 화면에서 부족한 operability는 official 또는 DB bridge collector로 보강하고, holdings / exposure는 현재 connector source map이 있는 ETF만 일괄 수집할 수 있게 했다.
  - source map이 없는 ETF는 `connector mapping 필요`로 표시해, 단순 미수집과 connector 미지원 상태를 분리했다.
  - provider context coverage 계산에서 `missing/error` row가 covered symbol로 오해되지 않도록 보정했다.
- Practical Validation V2 provider source map discovery 구현:
  - `finance_meta.etf_provider_source_map` schema를 추가하고, `nyse_etf` + `nyse_asset_profile` 기반으로 ETF별 issuer endpoint / parser mapping을 발견해 저장하게 했다.
  - `finance/data/etf_provider.py`에 iShares product list, SSGA holdings XLSX pattern, Invesco holdings / sector API pattern 검증 경로를 추가했다.
  - `GLD`, `IAU` 같은 금 현물 ETF는 row-level stock holdings가 아니라 `commodity_gold` parser로 100% gold holdings / exposure를 저장하게 했다.
  - Ingestion의 Practical Validation Provider Snapshots에 `Provider Source Map` tab을 추가했고, Practical Validation Provider Data Gaps 버튼은 먼저 source map discovery를 실행한 뒤 수집 plan을 다시 계산한다.
  - smoke 결과 `GLD/IAU/MTUM/QUAL/SOXX/USMV/XLE/XLU` source map 16개 verified row를 저장했고, holdings / exposure 수집은 522 holdings rows, 81 exposure rows를 저장했다.
  - 2026-05-11 `saved_portfolio_mix` source 기준으로 Practical Validation holdings / exposure coverage가 100% actual로 올라가고 `connector mapping needed` 목록이 비는 것을 확인했다.
- Practical Validation V2 operability / sensitivity REVIEW 해석 보강:
  - ETF operability 판정에서 `0.0` spread를 missing으로 오해하던 값을 명시적으로 유효값으로 처리했다.
  - 같은 ETF에 official partial row와 DB bridge row가 함께 있으면 빈 field를 병합해 판단하고, evidence source를 `invesco + db_bridge`처럼 표시하게 했다.
  - saved mix 기준으로 `QQQ`는 official expense ratio와 DB bridge AUM / ADV / spread를 합쳐 PASS, `XLU`는 0.00% spread를 정상 인식해 PASS로 바뀌었다.
  - Robustness / Sensitivity는 window perturbation을 curve 기반으로 계산하고, summary 문구를 "일부 계산 완료 / strategy-specific runtime은 별도 실행 필요"로 분리했다.
- Practical Validation V2 P2-6 stress / sensitivity interpretation 구현:
  - Stress / Scenario Diagnostics가 covered stress window와 실제 계산 완료 window를 분리해, compact monthly curve 때문에 daily replay가 필요한 구간을 `REVIEW` trigger로 표시하게 했다.
  - Stress interpretation row에 worst computed MDD, benchmark spread, return shock, 현재 macro / exposure lens를 추가했다.
  - Robustness / Sensitivity는 rolling / window / component dependency / weight tilt / strategy runtime follow-up을 별도 interpretation row로 요약하게 했다.
  - Practical Validation과 Final Review의 Robustness summary에서 Stress / Sensitivity Interpretation tab을 읽을 수 있게 했다.
- Backtest report content-oriented migration:
  - user feedback에 따라 `candidates/point_in_time/`를 현재 후보 폴더처럼 유지하지 않기로 했다.
  - Value / Quality / Quality + Value rerun 근거는 전략별 backtest log에 남아 있으므로 standalone candidate report를 제거했다.
  - weighted portfolio baseline / weight alternative / saved replay 근거는 `validation/runtime/WEIGHTED_PORTFOLIO_REPLAY_VALIDATION.md`로 내용 중심 재작성했다.
  - validation smoke report 파일명은 phase 번호 대신 `QUARTERLY_CONTRACT_RUNTIME_SMOKE`, `GLOBAL_RELATIVE_STRENGTH_RUNTIME_SMOKE`, `GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE`로 정리했다.
  - backtest report README / INDEX / migration / validation README를 새 구조에 맞춰 갱신했다.
- Data architecture 문서 docs/data 마이그레이션:
  - 기존 `.aiworkspace/note/finance/data_architecture/`의 `DATA_FLOW_MAP`, `DB_SCHEMA_MAP`, `TABLE_SEMANTICS`, `DATA_QUALITY_AND_PIT_NOTES`를 `.aiworkspace/note/finance/docs/data/`로 이동했다.
  - `docs/data/README.md`를 데이터 문서 입구로 확장해 읽는 순서, DB 그룹, JSONL boundary, 갱신 기준을 합쳤다.
  - `AGENTS.md`, `FINANCE_COMPREHENSIVE_ANALYSIS.md`, `FINANCE_DOC_INDEX.md`, phase / operations README, Practical Validation P2 계획의 data 문서 경로를 새 canonical 위치로 갱신했다.
  - 기존 `.aiworkspace/note/finance/data_architecture/` 폴더는 제거했다.
- Documentation System Rebuild Reference / Glossary 1차 안전장치:
  - `Reference > Guides`가 md 본문을 읽는 구조가 아니라 `app/web/reference_guides.py`의 guide text와 문서 경로 목록을 렌더링하는 구조임을 확인했다.
  - `Reference > Glossary`는 실제 md를 읽는 화면이므로 기존 root glossary 본문을 `.aiworkspace/note/finance/docs/GLOSSARY.md`로 승격하고 앱 읽기 경로를 새 docs 구조로 바꿨다.
  - `Reference > Guides`의 old root / operations / phase36 / code_analysis 문서 경로를 새 `.aiworkspace/note/finance/docs/` 문서 경로로 교체했다.
  - 삭제 전 1차 안전장치만 완료했으며, 남은 legacy root / operations / research / support 문서의 흡수 여부 판단은 다음 단계로 남겼다.
- Documentation System Rebuild 2차 legacy 흡수:
  - legacy root current-state docs는 새 `docs/INDEX.md`, `PROJECT_MAP.md`, `ROADMAP.md`, `GLOSSARY.md`로 대체 가능한 것으로 정리했다.
  - operations registry guide 핵심은 `.aiworkspace/note/finance/registries/README.md`에 current Selection V2 / legacy compatibility 기준으로 흡수했다.
  - runtime artifact hygiene, external research, config externalization 원칙은 `docs/runbooks/README.md`로 축약했다.
  - `research/practical_validation_stress_windows_v1.json`은 런타임 reference data로 확인되어 `.aiworkspace/note/finance/docs/data/`로 이동하고 `STRESS_WINDOW_FILE` 경로를 갱신했다.
  - Practical Validation investment diagnostics research 참조는 active task `DESIGN.md`에 흡수된 기준으로 바꿨고, 3차 삭제 후보 / 유지 주의사항을 doc-system-rebuild `NOTES.md`, `RISKS.md`에 기록했다.
- Documentation System Rebuild 3차 legacy 제거:
  - 새 docs 구조로 대체된 root current-state docs, `archive/`, `operations/`, 남은 `research/`, `support_tracks/`를 제거했다.
  - 기존 `phases/phase1`~`phases/phase36` 상세 문서는 현재 구현과 맞지 않는 legacy history로 보고 제거했다.
  - phase plan / checklist template은 삭제하지 않고 `.aiworkspace/note/finance/docs/runbooks/templates/`로 이동했다.
  - `bootstrap_finance_phase_bundle.py`는 새 template 경로를 읽고 `.aiworkspace/note/finance/phases/active/phase<N>/`에 bundle을 생성하도록 갱신했다.
  - `registries/`, `saved/`, root handoff log, active task docs는 보존했다.
- README 대규모 재작성:
  - 오래된 구현 목록 중심 README를 제거하고, 현재 finance 제품 boundary / 사용 흐름 / quick start / 문서 map 중심으로 다시 작성했다.
  - 사용자-facing program flow를 Mermaid chart로 추가해 `Ingestion -> Backtest Analysis -> Practical Validation -> Final Review -> Selected Portfolio Dashboard` 흐름을 첫 화면에서 이해할 수 있게 했다.
  - 상세 구현과 active progress는 README에 중복하지 않고 `.aiworkspace/note/finance/docs/`와 active task 문서로 연결하는 구조로 정리했다.
- Root handoff log 운영 지침 추가:
  - `WORK_PROGRESS.md`와 `QUESTION_AND_ANALYSIS_LOG.md`는 root handoff map으로 유지하고, 상세 기록은 active task 문서로 보내는 기준을 `AGENTS.md`와 `docs/runbooks/README.md`에 추가했다.
  - root log는 작업 단위당 3~5줄 milestone / decision 중심으로 남기고, 실행 명령 / 긴 분석 / 시행착오는 `RUNS.md`, `NOTES.md`, `DESIGN.md`로 분리한다.
- Skill System Rebuild 1차:
  - `.aiworkspace/note/finance/tasks/active/skill-system-rebuild/`를 열고 stale skill path 보정 작업을 기록했다.
  - `finance-backtest-web-workflow`, `finance-db-pipeline`, `finance-factor-pipeline`, `finance-strategy-implementation`, `finance-doc-sync`가 새 `.aiworkspace/note/finance/docs/` 구조를 참조하도록 수정했다.
  - legacy `finance-phase-management` skill은 삭제했고, roadmap에 skill rebuild active track을 추가했다.
- Skill System Rebuild 2차:
  - 새 `finance-task-management` skill을 만들어 task 분류, active task 운영, root handoff log 관리를 담당하게 했다.
  - Backtest UI / DB / factor / strategy skill은 domain implementation skill로 경계를 보정하고, `finance-doc-sync`는 closeout alignment skill로 좁혔다.
  - `AGENTS.md`와 skill-system-rebuild task 문서에 skill routing 기준과 검증 결과를 기록했다.
- Skill System Rebuild 3차:
  - finance project skill 원본을 repo-local `.aiworkspace/plugins/quant-finance-workflow/skills/`로 옮기고, global `~/.codex/skills/finance-*`는 mirror 설치본으로 동기화했다.
  - 6개 finance skill의 `SKILL.md`를 trigger / first-read / core workflow 중심으로 줄이고, 긴 domain rule은 `references/`로 분리했다.
  - 4차에는 plugin placeholder와 실제 skill trigger / 설치 흐름 검증이 남아 있다.
- AI Workspace Migration:
  - `.note/finance`와 `plugins/quant-finance-workflow`를 `.aiworkspace/note/finance`, `.aiworkspace/plugins/quant-finance-workflow` canonical 구조로 이동했다.
  - 코드 / 문서 / skill의 주요 경로를 새 AI workspace 기준으로 갱신하고 `.aiworkspace/README.md`를 추가했다.
  - run history의 기존 로컬 수정은 새 위치에 unstaged artifact로 보존한다.
- Skill System Rebuild 3차 post-migration 보강:
  - repo-local `finance-backtest-candidate-refinement` skill에 남아 있던 old phase report 중심 표현을 새 `reports/backtests` / registry-backed candidate evidence 흐름으로 정리했다.
  - 7개 repo-local finance skill의 `agents/openai.yaml` default prompt를 `$skill-name` 명시 방식으로 보정했다.
  - 활성 6개 finance skill mirror를 다시 동기화했고, 다음 작업은 4차 plugin placeholder / trigger 점검이다.
- Skill System Rebuild 4차 완료:
  - `quant-finance-workflow` plugin manifest에서 TODO placeholder와 없는 hooks / MCP / app / asset 참조를 제거했다.
  - `.agents/plugins/marketplace.json`이 실제 plugin root인 `./.aiworkspace/plugins/quant-finance-workflow`를 가리키도록 수정했다.
  - repo-local 7개 skill, global mirror 6개 skill, marketplace path, manifest JSON 검증을 완료했다.
- Skill System Rebuild taxonomy 보정:
  - 사용자가 정의한 공통 workflow 4개 + 구현 domain 4개 구조로 skill bundle을 다시 맞췄다.
  - `finance-task-management`는 `finance-task-intake`로 rename했고, `finance-integration-review`, `finance-runbook-maintainer`를 추가했다.
  - `finance-backtest-candidate-refinement`는 phase worktree 공통 skill에서 제거했다.
- AI Workspace README 갱신:
  - `.aiworkspace/README.md`를 현재 `note/finance`와 `plugins/quant-finance-workflow` 구조 기준으로 재작성했다.
  - 4 workflow + 4 domain skill taxonomy, 읽는 순서, artifact / registry 경계, skill 검증 명령을 첫 관문 문서에 반영했다.
- Product Research 2단계 UI platform 조사:
  - Streamlit 기반 UX/UI를 Python quant engine + API + React/Next.js 구조로 분리할지 검토하는 active research bundle을 열었다.
  - 현행 `app/web` 구조, Streamlit coupling, session state 사용, durable workflow docs를 audit했다.
  - 공식 문서/제품 페이지 기준으로 Streamlit, FastAPI, Next.js, Dash, QuantConnect, QuantRocket, OpenBB, TradingView, Composer를 비교했다.
  - 결론과 산출물은 `.aiworkspace/note/finance/researches/active/2026-05-ui-platform-research/RECOMMENDATION.md`부터 보면 된다.
- Product Research 3단계 skill hardening:
  - 2단계 UI platform research 실행 복기 결과를 `.aiworkspace/note/finance/tasks/active/product-research-skill-stage3/`에 기록했다.
  - `finance-task-intake`, `finance-product-audit`, `finance-benchmark-research`, `finance-feature-opportunity`가 research run과 skill hardening, product surface 분류, architecture benchmark, pilot/roadmap 구분을 더 명확히 안내하도록 보강했다.
  - repo-local skill source와 global `~/.codex/skills` mirror 정합성 검증을 완료했다.
- Product Research 4단계 반복 run - Backtest Report Productization:
  - `Backtest Result / Strategy Report` 제품화 주제로 `.aiworkspace/note/finance/researches/active/2026-05-backtest-report-productization/` 리서치 번들을 작성했다.
  - 현행 `reports/backtests`, Streamlit result display, run history, validation/final review replay 구조를 audit했다.
  - QuantConnect, QuantRocket, TradingView, QuantStats/pyfolio, NautilusTrader 패턴을 바탕으로 `BacktestReportPack + Markdown draft generator`를 다음 구현 후보로 추천했다.
- Product Research 5단계 plugin workflow hardening:
  - `.aiworkspace/note/finance/tasks/active/product-research-plugin-stage5/`에서 product research workflow를 plugin 수준으로 고정했다.
  - `finance-product-research-workflow` orchestration skill과 research bundle bootstrap/check helper script를 추가했다.
  - 기존 두 active research bundle 검증, skill quick validation, plugin JSON validation, mirror sync를 완료했다.
- Product Research plugin 분리:
  - product research 관련 4개 skill과 helper script 2개를 별도 `.aiworkspace/plugins/quant-finance-product-research/` plugin으로 이동했다.
  - 기존 `quant-finance-workflow`는 task intake / doc sync / integration / runbook / implementation skill 중심으로 가볍게 정리했다.
  - marketplace에 두 plugin을 모두 등록하고 skill validation, script dry-run, active research bundle check, mirror sync를 완료했다.
- Service Contract Tests:
  - `.aiworkspace/note/finance/tasks/active/service-contract-tests/`를 열고 UI-engine boundary 후속 QA를 단일 task로 진행했다.
  - `tests/test_service_contracts.py`를 추가해 Practical Validation handoff와 Final Review evidence read model contract를 `unittest`로 검증한다.
  - 검증 명령은 `.aiworkspace/note/finance/docs/runbooks/README.md`와 script map / project map에 반영했다.
- Provider Gap Collection Boundary:
  - `.aiworkspace/note/finance/tasks/active/provider-gap-collection-boundary/`를 열고 Practical Validation Provider Data Gaps 수집 책임을 service로 이동했다.
  - `app/web/backtest_practical_validation.py`는 provider gap 표시 / 버튼 / session state만 맡고, `app/services/backtest_practical_validation.py`가 row / plan / ingestion orchestration을 맡는다.
  - `tests/test_service_contracts.py`에 provider gap plan / mocked job orchestration contract를 추가했다.
- Practical Validation Replay Service Boundary:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-replay-service-boundary/`를 열고 Streamlit-free replay helper를 `app/services/backtest_practical_validation_replay.py`로 이동했다.
  - Practical Validation UI는 replay mode 선택 / 버튼 / session state / 결과 표시만 맡고, service가 recheck plan과 actual replay result를 만든다.
  - `tests/test_service_contracts.py`에 replay plan / blocked replay contract를 추가했다.
- UI Engine Boundary Cleanup Task 8:
  - `.aiworkspace/note/finance/tasks/active/runtime-wrapper-cleanup/`를 열고 `app/runtime/backtest.py` 함수군과 public caller surface를 지도화했다.
  - `build_backtest_result_bundle`을 `app/runtime/backtest_result_bundle.py`로 분리하되 `app.runtime.backtest` / `app.runtime` public export는 유지했다.
  - result bundle compatibility / shape contract tests를 추가했고 다음 작업은 Task 9 boundary contract hardening이다.
- UI Engine Boundary Cleanup Task 9 / phase closeout:
  - `.aiworkspace/note/finance/tasks/active/boundary-contract-hardening/`에서 `app.services/app.runtime -> app.web` import를 boundary lint hard failure로 승격했다.
  - `tests/test_service_contracts.py`에 boundary checker behavior contract를 추가했고 service contract suite는 22 tests로 확장됐다.
  - `ui-engine-boundary-cleanup` phase는 Task 6~9 완료 상태로 closeout했다.
- Canonical Finance Note Paths:
  - `.aiworkspace/note/finance/tasks/active/canonical-finance-note-paths/`를 열고 legacy `.note/finance` 직접 참조를 정리했다.
  - `app/workspace_paths.py`를 추가해 `registries`, `saved`, `run_history`, `run_artifacts`, docs path를 canonical `.aiworkspace/note/finance` 기준으로 통일했다.
  - Overview browser smoke에서 Current Candidates / Paper Tracking / Proposal Drafts / Recent Runs가 canonical JSONL 데이터를 읽는 것을 확인했다.
- Product Research - Investable Workflow Gap Analysis:
  - `.aiworkspace/note/finance/researches/active/2026-05-investable-workflow-gap-analysis/` 리서치 번들을 생성했다.
  - 현재 Backtest -> Practical Validation -> Final Review -> Selected Dashboard 흐름을 audit하고 QuantConnect, Bloomberg PORT, Morningstar X-Ray, IBKR PortfolioAnalyst, Portfolio Lab, CFA / FINRA / NBER 근거와 비교했다.
  - 1차 추천은 `Investability Evidence Packet`, `Validation Gate Hardening`, `Assumption Disclosure`, `Source Breadcrumb`를 먼저 확정하고 개발하는 방향이다.
- Investability Evidence Packet V1:
  - `.aiworkspace/note/finance/tasks/active/investability-evidence-packet-v1/`를 열고 Final Review evidence packet / selected-route gate를 구현했다.
  - 새 JSONL registry는 만들지 않고, 기존 Final Review decision row에 compact packet snapshot만 연결했다.
  - service contract 26 tests, UI-engine boundary check, Browser smoke를 통과했다.
- Phase 12 Recheck Readiness / Freshness Contract V1:
  - `.aiworkspace/note/finance/tasks/active/recheck-readiness-freshness-contract-v1/`에서 Selected Dashboard recheck operations preflight를 구현했다.
  - Final Review embedded replay contract를 우선 사용하고 Current Candidate Registry를 fallback으로 쓰는 resolver를 추가했다.
  - 다음 작업은 `selected-provider-evidence-staleness-contract-v1`이며 `.aiworkspace/note/finance/phases/active/phase12-selected-monitoring-recheck-operations/`에서 이어서 본다.
- Phase 12 Selected Provider Evidence Staleness Contract V1:
  - `.aiworkspace/note/finance/tasks/active/selected-provider-evidence-staleness-contract-v1/`에서 provider evidence freshness / coverage policy를 구현했다.
  - stale actual evidence, partial / missing look-through coverage, missing required provider areas가 PASS처럼 보이지 않도록 Dashboard와 service contract를 강화했다.
  - 다음 작업은 `recheck-comparison-review-signal-policy-v1`이며 Phase 12 문서에서 12-4로 이어진다.
- Phase 12 Recheck Comparison Review Signal Policy V1:
  - `.aiworkspace/note/finance/tasks/active/recheck-comparison-review-signal-policy-v1/`에서 `selected_review_signal_policy_v1`을 구현했다.
  - Review Signals의 CAGR / MDD / benchmark spread rows는 Recheck Comparison에서 파생되고, preflight / provider route도 같은 signal board에 반영된다.
  - 다음 작업은 `allocation-drift-evidence-boundary-v1`이며 Phase 12 문서에서 12-5로 이어진다.
- Phase 12 Decision Dossier Continuity Operations V1:
  - `.aiworkspace/note/finance/tasks/active/decision-dossier-continuity-operations-v1/`에서 `selected_decision_source_consistency_v1`을 구현했다.
  - Decision Dossier, Continuity, Timeline, Review Signals가 같은 Final Decision V2 source contract를 표시하고, session evidence는 read-only context로 남긴다.
  - 다음 작업은 `phase12-integrated-qa-closeout`이며 Phase 12 문서에서 12-7로 이어진다.
- Phase 12 Integrated QA Closeout:
  - `.aiworkspace/note/finance/tasks/active/phase12-integrated-qa-closeout/`에서 Phase 12 전체 compile / service contract / boundary / hygiene / diff / storage boundary 검증을 완료했다.
  - closeout summary는 `.aiworkspace/note/finance/phases/done/phase12-selected-monitoring-recheck-operations.md`에 남겼다.
  - 다음 대상은 Phase 13 first-cycle hardening closeout이다.
- Phase 13 Board Open:
  - `.aiworkspace/note/finance/phases/active/phase13-hardening-cycle-closeout/`를 열고 1차 hardening cycle closeout 범위를 정의했다.
  - 13-1부터 13-6까지 inventory / gate QA / storage audit / docs-runbook sync / residual risk / final closeout task split을 만들었다.
  - 다음 작업은 `phase13-cycle-inventory-v1`이다.
- Backtest Analysis UX Checkpoint V1:
  - `.aiworkspace/note/finance/tasks/active/backtest-analysis-ux-checkpoint-v1/`에서 Backtest Analysis 결과 화면의 Stage / 검증 체크포인트 언어를 분리했다.
  - Runtime payload를 접힌 Developer Payload로 낮추고, Latest Backtest Run / Data Trust / Next Action / Real-Money Candidate Readiness UI를 정리했다.
  - 새 DB / JSONL / 사용자 메모 저장 없이 기존 Clean V2 handoff만 더 명확하게 표시했다.
- Overview Market Intelligence research:
  - `.aiworkspace/note/finance/researches/active/2026-05-overview-market-intelligence/`를 열고 Overview 개편 feasibility를 조사했다.
  - Coverage 1000/2000 top movers와 sector / industry leadership은 기존 DB price/profile로 가능하다는 결론을 남겼다.
  - FOMC calendar는 low-risk next slice, earnings calendar는 provider/API/persistence 결정 이후로 분리했다.
- Overview Market Intelligence first slice:
  - `.aiworkspace/note/finance/phases/active/overview-market-intelligence/`와 `.aiworkspace/note/finance/tasks/active/overview-market-intelligence-first-slice/`에서 scope lock 후 구현했다.
  - `app/services/overview_market_intelligence.py`가 local DB 기반 market movers와 sector / industry leadership snapshot을 생성한다.
  - Overview는 Market Movers / Sector-Industry / Events / Candidate Ops 탭 구조로 바뀌었고, calendar ingestion은 후속 task로 남겼다.
- Overview Market Intelligence S&P 500 intraday slice:
  - `.aiworkspace/note/finance/tasks/active/overview-market-intelligence-sp500-intraday/`에서 S&P 500 current universe와 daily previous-close snapshot 방향을 구현했다.
  - `finance/data/market_intelligence.py`와 `finance_price.market_intraday_snapshot` / `finance_meta.market_universe_member`가 추가됐다.
  - Market Movers는 S&P 500 / Top1000 / Top2000, yearly period, sector filter, missing diagnostics를 제공한다.
  - 상단 controls를 segmented control bar와 refresh status bar로 다듬고, S&P 500 daily snapshot이 5분 기준으로 stale이면 update-needed dot / 버튼이 보이도록 했다.
  - S&P 500 snapshot refresh 기본 경로를 Yahoo quote batch fast path로 바꾸고, yfinance 5m OHLCV를 fallback으로 남겼다. Local smoke에서 503개 quote snapshot 저장은 6.514초가 걸렸다.
  - Streamlit이 이전 job-wrapper import를 잡은 상태에서 `quote_batch_size` TypeError가 나던 UI click path를 수정했고, 재시작 후 브라우저에서 503개 snapshot 저장이 7.377초로 완료되는 것을 확인했다.
  - Top1000 / Top2000 daily intraday refresh를 같은 `market_intraday_snapshot` 저장 구조로 확장했다. Local smoke에서 Top1000은 1000 rows / 9.322초, Top2000은 2000 rows / 16.0초로 저장됐고 Overview가 intraday snapshot을 우선 표시한다.
- Overview Market Intelligence Task 4 / Market Event DB Structure:
  - `.aiworkspace/note/finance/tasks/active/overview-market-events-schema/`를 열고 `finance_meta.market_event_calendar` schema를 추가했다.
  - `finance/data/market_intelligence.py`에 event row normalize, `event_key` 기반 UPSERT, date-range read helper를 추가했다.
  - Local DB smoke에서 requested common event columns가 생성된 것을 확인했고, 다음 task는 FOMC collector다.
- Overview Market Intelligence 2차 production baseline:
  - `.aiworkspace/note/finance/phases/active/overview-market-intelligence-productionization/`의 2차 task 2-01~2-03을 완료했다.
  - Market Movers는 refresh state와 missing recommended action을 보여주고, Events는 official / provider estimate / stale estimate read model을 제공한다.
  - 2차 acceptance checklist와 runbook을 정리했고, 다음 단계는 3차 earnings source validation이다.
- Overview Market Intelligence 3차 earnings production baseline:
  - 3차 task 3-01~3-03을 완료해 earnings row에 source validation / lifecycle metadata를 저장한다.
  - yfinance earnings estimate는 선택적으로 Nasdaq earnings calendar와 cross-check하고, 변경된 이전 estimate는 superseded / stale 상태로 정리한다.
  - Ingestion은 latest movers 외에 S&P 500 / Top1000 / Top2000 low-frequency batch 수집을 지원하며 다음 단계는 4차 visuals / calendar UX polish다.
- Overview Market Intelligence 5차 ops hardening:
  - `.aiworkspace/note/finance/tasks/active/overview-mi-ops-hardening/`에서 Overview `Data Health` 탭을 추가했다.
  - Data Health는 DB freshness와 local `WEB_APP_RUN_HISTORY.jsonl`을 결합해 6개 수집 대상의 OK / Stale / Missing / Failed / Partial 상태와 next action을 보여준다.
  - Overview refresh buttons가 실행 결과를 local web app run history에 남기도록 연결했고, service contract / browser smoke 검증을 완료했다.
- Overview Market Intelligence 6차 macro calendar:
  - `.aiworkspace/note/finance/tasks/active/overview-mi-macro-calendar/`에서 BLS / BEA official macro release calendar collector를 추가했다.
  - Events는 `Macro` filter와 `Refresh Macro Calendar` 버튼을 제공하고, Data Health는 Macro Calendar coverage를 7번째 운영 대상으로 표시한다.
  - Local smoke에서 BEA GDP 13개 row 저장은 성공했고, BLS는 HTTP 403으로 차단되어 partial failure로 노출되는 것을 확인했다.
- Overview MI Sector / Industry trend:
  - `.aiworkspace/note/finance/tasks/active/overview-mi-sector-leadership-trend/`에서 Sector / Industry Leadership을 최신 랭킹 + 기간별 추세 화면으로 개편했다.
  - Coverage는 S&P 500 / Top1000 / Top2000을 지원하고, Period는 Daily / Weekly / Monthly로 선택한다.
  - Daily 1개월, Weekly 3개월, Monthly 6개월 trend rows를 DB price history에서 계산하며 browser smoke와 service contract 56 tests를 통과했다.
- Overview MI Sector / Industry detail polish:
  - Sector / Industry trend horizon을 Daily 3개월, Weekly 6개월, Monthly 1년으로 확장했다.
  - Trend Groups multiselect로 라인별 표시를 제어하고, 양수 그룹에는 티커 리더 bar / return-share donut 상세를 추가했다.
  - Service contract 56 tests, module compile, browser smoke를 통과했다.
- Overview MI Sector / Industry daily intraday:
  - Sector / Industry `Daily`는 Market Movers와 같은 `market_intraday_snapshot`을 우선 읽도록 연결했다.
  - Latest Ranking / Positive Group Detail은 `Previous Close -> latest quote` 기준으로 계산하고, Weekly / Monthly는 기존 EOD DB 기준을 유지한다.
  - UI에 Return Window와 Price Mode를 표시해 intraday / EOD 기준 차이를 드러냈다.
- Overview MI Events calendar UX:
  - Events `Calendar` 탭에 월 선택 가능한 7열 월간 달력 그리드를 추가했다.
  - 기존 event count chart와 날짜별 리스트는 그대로 유지해 월간 조망과 세부 스캔을 함께 제공한다.
  - Service contract 56 tests, module compile, desktop/mobile browser smoke를 통과했다.
- Overview Market Movers quote gap diagnostics:
  - `missing quote row` 심볼만 대상으로 Yahoo single quote, 5D history, DB EOD price, asset profile, 필요 시 yfinance fast_info evidence를 비교하는 1차 진단을 추가했다.
  - Overview `Coverage Diagnostics`에 `Diagnose Missing Quotes` 버튼과 diagnosis / confidence / recommended action 테이블을 연결했다.
  - 1차는 evidence-based hint이며 별도 delisting / halt 확정 판정은 하지 않는다.
- Overview scheduled refresh automation:
  - `.aiworkspace/note/finance/tasks/active/overview-scheduled-refresh-automation/`에서 브라우저 없이 Overview ingestion job을 실행하는 1차 자동화 task를 열었다.
  - `app/jobs/overview_automation.py`는 profile별 cadence, US market-hours guard, lock, dry-run, scheduled run history metadata를 처리하는 run-once CLI다.
  - Data Health는 auto / manual run, next auto due, failure streak를 표시하고, quote gap 진단은 `market_data_issue`에 반복 issue로 누적된다.
  - cron / launchd / 외부 automation 실제 등록은 다음 단계에서 이 CLI를 주기 호출하는 방식으로 붙일 수 있다.
- Overview browser-session auto refresh:
  - `.aiworkspace/note/finance/tasks/active/overview-browser-auto-refresh/`에서 OS scheduler 대신 Overview를 열어둔 동안만 작동하는 1차 자동 refresh를 시작했다.
  - `browser_safe` profile은 S&P 500 daily snapshot만 선택하고, Market Movers `데이터 갱신`의 자동 모드는 Streamlit fragment로 5분마다 해당 profile을 호출한다.
  - 브라우저 smoke에서 토글 ON 시 장 시간 밖 `skipped` 상태가 표시되고 console error 0개를 확인했다.
  - 자동 check 중에는 전체 화면 blocking 대신 Market Movers `데이터 갱신` 안에서 초 단위 countdown / cadence progress / completion 상태를 표시한다.
  - UI redesign pass 1에서 Market Movers `데이터 갱신`을 반복 badge/card layout 대신 현재 상태, 수동/자동 모드, 주요 액션이 한 번에 읽히는 명령 영역으로 정리했다.
  - UI redesign pass 2에서 `데이터 갱신` 외곽 카드 컨테이너를 제거하고, 현재 상태 pill / 메타 chip / 갱신 방식 / 수동 액션이 이어지는 status + action bar로 정리했다.
  - UI redesign pass 3에서 Market Movers의 단순 wrapper container를 줄이고, snapshot status cards를 얇은 metadata strip으로 바꿔 ranking/table과의 시각적 거리를 줄였다.
  - UI redesign pass 4에서 Market Movers 전용 HTML/CSS 렌더러를 `app/web/overview_ui_components.py`로 분리해 `overview_dashboard.py`의 화면 흐름과 시각 컴포넌트 책임을 나눴다.
  - UI redesign pass 5에서 Overview 전용 색상 / 표면 / 차트 팔레트 / spacing / typography 토큰을 `overview_ui_components.py`로 모아 반복 하드코딩을 줄였다.
  - UI redesign pass 6에서 새 UI 라이브러리 도입 전 단계로 Coverage / Period / Group / Events control 구성을 내부 model / helper로 정리했다.
- Overview Events UX redesign:
  - `.aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/`에서 Events 탭을 Agenda / Calendar / Quality / Raw 구조로 개편했다.
  - Source lane, event summary strip, agenda list 렌더러를 추가해 다음 일정 / source 상태 / review 필요 row가 먼저 읽히도록 했다.
  - DB schema / collector 변경 없이 기존 `market_event_calendar` read model만 사용했다.
- Overview Market Session Banner:
  - `.aiworkspace/note/finance/tasks/active/overview-market-session-banner/`에서 Overview 상단 미국장 세션 배너를 추가했다.
  - NYSE 거래일이면 Open / Close ET와 KST 시간을 표시하고, 휴장이면 주말 / 주요 휴장일 사유와 다음 세션 시간을 표시한다.
  - 외부 API 없이 rules-based NYSE calendar로 처리하며, one-off exchange closure는 범위 밖으로 명시했다.
- Practical Validation Module Gate V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-module-gate-v1/`에서 Practical Validation 개편을 구현했다.
  - source traits 기반 validation module planner와 Final Review gate를 추가해 필수 module `BLOCKED` / `NEEDS_INPUT` / `NOT_RUN`이면 save-and-move를 막는다.
  - UI는 Final Review Gate / 필수 / 조건부 / 후속 참고 module board를 먼저 보여주고, 기존 상세 diagnostics는 그대로 유지한다.
- Practical Validation Required Module Polish V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-required-module-polish-v1/`에서 필수검증 8개 표시를 보강했다.
  - `Benchmark Parity` 사용자-facing label을 `Benchmark / Comparator Parity`로 확장하고, module row에 `Gate Effect` / `Gate Reason`을 추가했다.
  - Source Integrity, Data Coverage, Latest Runtime Replay, Stress / Robustness, Backtest Realism 설명을 실제 gate 의미에 맞게 다듬었다.
- Practical Validation Board Map V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-board-map-v1/`에서 화면 board와 validation module을 분리했다.
  - `Applied Validation Map`은 적용 보드 / 비적용 보드 / 모듈 연결을 보여주고, 각 board title 아래에 `Board Type`, `Applies`, `Feeds`, `Gate` badge를 표시한다.
  - 단일 component GTAA 후보에서는 weighted-mix 전용 Risk Contribution / Component Role / Weight board가 collapsed `Not applicable`로 내려간다.
  - blocker / review module table에 `Fix Location`과 `Fix Action`을 추가해 `Latest Runtime Replay`가 `3. 최신 데이터 기준 전략 재검증`에서 해결된다는 점을 바로 표시한다.
  - Practical Validation 화면을 `4. Final Review Gate / 검증 모듈`, `5. 검증 근거 보드`, `6. 보강 액션`, `7. 저장 & Final Review 이동`으로 나눠 module / evidence / action 혼동을 줄였다.
- Practical Validation Commercial UX V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-commercial-ux-v1/`에서 Practical Validation의 표시 계층을 summary-first로 개편했다.
  - Control Center / Fix Queue / Evidence Workspace / Provider Action Center를 추가하고, raw module / evidence / provider table은 상세 영역으로 낮췄다.
  - service contract 193 tests와 Browser QA를 통과했으며, 검증 module / Final Review gate 정책은 변경하지 않았다.
  - 저장-only는 audit trail로 유지하되 Gate 미통과 validation row는 Final Review 후보 목록에서 숨기도록 정리했다.
  - Practical Validation 신규 진입 / source 변경 시 이전 replay 표시 state를 비우고, Step 1~7 본문 경계 surface를 복원했다.
  - 사용자 확인에 따라 Portfolio Validation closeout으로 정리하고 durable docs / roadmap / project map / glossary / storage governance를 최신 상태로 맞췄다.
- Overview Market Movers second pass:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/`에서 Volume Rank를 수익률 Top N의 재정렬이 아니라 별도 `volume_rows` read model로 분리했다.
  - Daily는 당일 snapshot / EOD 거래량과 거래대금을, weekly / monthly / yearly는 평균 일거래량 / 평균 일거래대금과 기간 합계를 함께 표시한다.
  - Top1000 / Top2000 비일별 조회는 결측 진단 최신일자 조회를 missing row로 제한하고 price / volume point read에 symbol-timeframe-date index를 사용하도록 줄였다.
- Overview Sector / Industry polish:
  - `.aiworkspace/note/finance/tasks/active/overview-sector-industry-polish/`에서 Trend Groups 유지, Heatmap / Line / Latest Delta trend view, insight cards, Positive Group Detail marker 개선을 완료했다.
  - Service read model은 breadth, cap-vs-equal gap, concentration, ticker previous return, momentum delta를 제공한다.
  - `tests.test_service_contracts` 80개, chart JSON smoke, `git diff --check`, Browser QA screenshot을 통과했다.
  - 후속 QA에서 Daily heatmap이 과밀하다는 문제를 확인해 Trend horizon을 Daily 1M / Weekly 3M / Monthly 12M으로 조정했다.
  - 후속 QA에서 전체 섹터 선택 시 Heatmap 높이가 압축되는 문제를 확인해 선택 그룹 수만큼 아래로 늘어나는 chart height 계약을 추가했다.
- Selected Portfolio Candidate Search:
  - `.aiworkspace/note/finance/tasks/active/selected-portfolio-candidate-search-20260531/`에서 기존 V2 selection source, Practical Validation 결과, saved portfolios, legacy Final Review 후보를 재검토했다.
  - Practical Validation 통과 또는 Final Review evidence-ready 후보는 있었지만, Final Review selected-route investability gate `select_allowed=True`를 만족한 후보는 없었다.
  - `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`에는 아무 row도 append하지 않았고, Selected Portfolio Dashboard read model은 `dashboard_rows=0`, `HANDOFF_NO_FINAL_DECISION`으로 확인됐다.
  - 다음 보강 1순위는 `EW Growth/Commodity 30 + GTAA Clean-6 70`의 backtest realism, component role / weight rationale propagation, provider/look-through, risk contribution, stress/validation efficacy evidence다.
- Practical Validation Source Context V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-source-context-v1/`에서 Step 1 source snapshot에 strategy / construction brief와 component strategy table을 추가했다.
  - 신규 candidate / weighted mix / saved mix handoff는 compact monthly selection / holdings history를 함께 넘기고, legacy source는 Step 3 runtime replay selection history를 fallback으로 읽는다.
  - Result Table은 기존 performance row를 유지하면서 selection / holdings row를 별도 표로 표시한다. Full holdings 원장이나 provider raw data는 workflow JSONL에 새로 복사하지 않는다.
- Practical Validation Selected-route Preflight V1:
  - `.aiworkspace/note/finance/tasks/active/practical-validation-selected-route-preflight-v1/`에서 Practical Validation gate와 Final Review selected-route gate의 의미를 맞췄다.
  - Final Review selection policy를 Practical Validation에서 preflight로 먼저 실행하고, selected-route 저장을 막을 evidence gap은 `Selected-route Preflight` 필수 module의 `NEEDS_INPUT`으로 승격해 Final Review 이동을 차단한다.
  - 기존 saved Practical Validation row는 재작성하지 않고 Final Review source picker에서 동적으로 preflight를 확인해, 과거 `READY_WITH_REVIEW` row라도 selected-route 미통과이면 후보 목록에서 숨긴다.
- Final Review pass candidate dashboard exposure:
  - `.aiworkspace/note/finance/tasks/active/final-review-pass-candidate-search-20260601/`에서 통과 후보를 fresh 재검증한 뒤 Final Decision V2에 4개 GRS 후보를 append했다.
  - `Final Review 통과 후보 2026-06-01` dashboard saved portfolio를 만들어 4개 selected decision id를 배정했고, Selected Dashboard Browser QA에서 `My Portfolios=1`, `Selected Pool=4`, `Assigned=4`를 확인했다.
  - `GTAA Default Top3`는 fresh run에서 Practical Validation / investability packet이 block되어 저장하지 않았다. live approval / order / auto rebalance는 모두 disabled 상태다.
- JSONL registry audit dry run:
  - `.aiworkspace/note/finance/tasks/active/jsonl-registry-audit-20260601/`에서 `.aiworkspace/note/finance/**/*.jsonl` read-only inventory와 cleanup plan을 작성했다.
  - JSONL 13개 / 109 row parse, GRS Final Decision V2 4개 selected row, Dashboard row 4개, assigned reference 4개를 확인했다.
  - 승인 전 archive/delete/rewrite는 하지 않았다. 권장안은 GRS 4개를 Final Decision V2 self-contained selected record로 유지하고 synthetic source/result row는 만들지 않는 것이다.
- JSONL registry cleanup:
  - 사용자 승인 후 전체 JSONL 13개를 `.aiworkspace/note/finance/archive/jsonl-registry-audit-20260601/20260601T152645KST/`에 SHA-256 manifest와 함께 백업했다.
  - active JSONL은 Final Decision V2, Selected Dashboard portfolios, Saved Portfolios 3개만 남겼고 legacy/prototype/generated JSONL 10개는 active에서 제거했다.
  - 검증 결과 selected rows 4 / dashboard rows 4 / assigned 4 / missing 0, 6개 focused service contract, `git diff --check`가 통과했다.
- Ingestion Console UX / Data Quality follow-up:
  - `.aiworkspace/note/finance/tasks/active/ingestion-console-ux-data-quality-v1/`에서 리뷰 후속 개선을 완료했다.
  - Ingestion 상단에 workflow overview를 추가하고, 주요 가격 수집 card에 실행 전 source / 대상 수 / 기간 / interval 계약과 bounded DB coverage quick check를 붙였다.
  - 결과 summary는 job domain별 metric label / interpretation callout을 사용해 가격 row, lifecycle evidence row, provider snapshot의 의미를 분리한다.
  - py_compile, `git diff --check`, service contract 207 tests, Browser DOM QA를 통과했다. Browser screenshot capture는 timeout으로 생성하지 못했다.
- Futures Market Monitoring research:
  - `.aiworkspace/note/finance/researches/active/2026-06-futures-market-monitoring/`에 선물장 OHLCV / 개장 전 급변 모니터링 리서치 번들을 만들었다.
  - 로컬 `yfinance` 1분봉 smoke에서 `ES=F`, `NQ=F`, `YM=F`, `RTY=F`, `CL=F`, `GC=F`, `ZN=F`, `6E=F` 등은 rows를 반환했고 `DX=F`, `VX=F`는 제외 대상으로 확인했다.
  - 권장 방향은 `Overview > Futures Monitor` 탭, DB-backed `yfinance` polling, 60초 기본 cadence, Altair candlestick, provider freshness / stale / failed 상태 표시다.
- Futures Market Monitoring MVP V1:
  - `.aiworkspace/note/finance/tasks/active/futures-market-monitoring-mvp-v1/`에서 futures schema, `yfinance` 1m OHLCV collector, ingestion job, Overview read model, Data Health 연결을 구현했다.
  - `Overview > Futures Monitor`는 Watch Group / Symbols / Candle Symbol / Window / Chart control, Shock Board, Candles, Provider Run을 제공하며 provider age / stale / missing 상태를 표시한다.
  - `Workspace > Ingestion`에는 수동 선물 1분봉 수집 expander를 추가했다. 기본 자동 갱신은 browser-open 60초 cadence이고 fast mode는 작은 symbol set에만 허용된다.
  - 검증: focused / full service contracts, py_compile, UI-engine boundary, `git diff --check`, yfinance collector smoke, Browser QA screenshot 통과.
  - 후속 UI 개선으로 Candles 탭에 선택 symbol을 포함한 최대 4개 2x2 미니 캔들 차트와 선택 symbol 상세 차트를 함께 표시하도록 바꿨다.
  - 후속 데이터 검증에서 지수 / 금리 / 원자재 / FX core 16개가 모두 1분봉 row를 저장했고, 기본 `Pre-open Core` 2x2를 `NQ=F`, `ZN=F`, `CL=F`, `6E=F`로 확정했다.
- Futures Macro Thermometer V1:
  - `.aiworkspace/note/finance/tasks/active/futures-macro-thermometer-v1/`에서 1년 일봉 기반 글로벌 매크로 해석 기능을 구현했다.
  - `Overview > Futures Monitor > Macro Thermometer`는 Risk-On / Growth / Rate Pressure / Dollar Pressure / Safe Haven / Inflation Pressure 점수, 오늘의 해석, 근거 티커, 표준화 움직임, 주의 문구를 표시한다.
  - 기존 1m 차트 / Shock Board는 유지하고, macro tab은 저장된 `interval_code=1d` row를 별도로 읽는다.
  - 16개 core futures `1y / 1d` backfill smoke가 성공했고, focused service contracts는 통과했다. 최종 Browser QA / full verification은 task RUNS를 확인한다.
- Futures Macro Thermometer Validation follow-up:
  - `.aiworkspace/note/finance/tasks/active/futures-macro-thermometer-validation-v1/`에서 리뷰 후속 수정까지 반영했다.
  - 5y point-in-time validation은 target return 선계산과 Overview TTL cache를 사용하며, same-process 반복 렌더는 캐시로 즉시 반환된다.
  - Mixed scenario는 directional hit-rate를 N/A로 표시하고 occurrence count를 분리한다. `Max Adverse`는 forward window path adverse move 기준이며 false-positive rate가 UI summary에 노출된다.
- Futures Monitor UI V2:
  - `.aiworkspace/note/finance/tasks/active/futures-monitor-ui-v2/`에서 prototype-like tab UI를 workspace layout으로 개편했다.
  - 상단 Futures Workspace / Market Pulse / Data Feed command center를 추가하고 Macro Context와 Live Futures Charts를 같은 화면에 배치했다.
  - Shock Board / Provider Run / raw candle rows는 하단 diagnostics expander로 낮췄고, manual refresh의 즉시 `st.rerun()`을 제거했다.
  - py_compile, UI-engine boundary, service contract 234 tests, Browser QA screenshot을 통과했다.
  - V2.1 후속으로 상단 controls를 압축하고, mini chart metric을 chip strip으로 바꾸며, Macro Context를 signal strip / score chip 중심으로 다듬었다.
  - V2.2 후속으로 Macro Context를 상단 full-width로 올리고, Live Futures Charts를 하단 3x2 grid로 바꾸며, 중복 `Selected Detail` 차트를 제거했다.
  - V2.3 후속으로 `Focus` control을 제거하고, `Symbols`가 3x2 grid 순서를 직접 결정하도록 정리했다. `Chart` hourly option은 `1h` 대신 `60m`로 표시한다.
  - V2.4 후속으로 Macro Context daily refresh와 Live Futures Charts auto refresh를 별도 Streamlit fragment로 분리했다. Live provider run summary는 `1m` run만 읽도록 필터링했다.
- Futures Monitor yfinance intraday fallback:
  - `.aiworkspace/note/finance/tasks/active/futures-market-monitoring-mvp-v1/`에서 yfinance `1d / 1m` futures 응답이 빈 frame이거나 지나치게 희소할 때 해당 symbol만 `2d / 1m`으로 한 번 보강 수집하도록 수정했다.
  - `ZN=F`, `CL=F`, `GC=F`처럼 몇 개 candle만 그려지는 문제는 provider가 sparse 1d intraday rows를 반환한 것이 원인이었고, fallback 성공 시 초기 sparse rows를 대체한다.
  - 8501 Browser QA에서 `Live Futures Charts` 6/6 symbol, Provider Run `success`, dense 3x2 chart grid를 확인했다.
- Operations Overview IA V1:
  - `.aiworkspace/note/finance/tasks/active/operations-overview-ia-v1/`에서 Operations landing page와 navigation label 정리를 구현했다.
  - `Operations > Operations Overview`는 Portfolio Monitoring / System Data Health / Archive Recovery / Reference Reports lane을 표시한다.
  - 기존 Selected Dashboard route는 `Portfolio Monitoring`으로 유지하고, Backtest Run History / Candidate Library는 Archive recovery 도구로 낮췄다.
  - live approval / order / account sync / auto rebalance / registry rewrite는 추가하지 않았다.
- Operations Console Restructure V2-V5:
  - `.aiworkspace/note/finance/tasks/active/operations-console-restructure-v2-v5/`에서 2차~5차 scope를 하나의 완료 흐름으로 묶었다.
  - `Operations > Operations Overview`는 `Operations Console`로서 today action queue, 1차~5차 roadmap, surface audit, primary/secondary lane을 표시한다.
  - Portfolio Monitoring의 리밸런싱 표는 `Target Snapshot Date`, `Next Review Date`, `Current Target Snapshot`으로 바꿔 주문/자동 리밸런싱이 아님을 명시했다.
  - Backtest Run History와 Candidate Library는 삭제하지 않고 Archive / Recovery 도구로 보존했다.
- Operations Archive Tabs Removal:
  - `.aiworkspace/note/finance/tasks/active/operations-archive-tabs-removal-20260607/`에서 Operations 상단 archive 탭 제거를 완료했다.
  - 현재 Operations top navigation은 `Operations Overview`, `Portfolio Monitoring`, `System / Data Health`만 남긴다.
  - Backtest Run History / Candidate Library 데이터와 helper code는 삭제하지 않고, 실제 삭제는 별도 audit 후 판단한다.
  - focused unittest 4개, py_compile, `git diff --check`를 검증 기준으로 삼았다.
- Risk-On Momentum 5D V1:
  - `.aiworkspace/note/finance/tasks/active/risk-on-momentum-5d-v1/`에서 Top1000 기본 short-term stock swing strategy를 구현했다.
  - Core는 `finance/swing.py`, daily swing features는 `finance/transform.py`, futures daily loader는 `finance/loaders/futures.py`, DB wrapper / artifact writer는 `app/runtime/backtest.py`가 맡는다.
  - `Backtest Analysis > Single Strategy` form, result `Swing Detail` tab, History replay fields, Compare default runner를 연결했다. V1은 `close_based + fixed_pct + Equal Slot`만 지원한다.
  - Browser QA, focused tests, manual DB smoke, full service contract 237 tests, `git diff --check`가 통과했다. QA screenshot은 generated artifact `risk-on-momentum-5d-qa.png`로 남겼고 커밋 대상은 아니다.
- Risk-On Momentum 5D V2:
  - `.aiworkspace/note/finance/tasks/active/risk-on-momentum-5d-v2/`에서 Daily Swing Backtest Analysis 고도화를 구현했다.
  - ATR / macro ranking penalty / comparison-sensitivity-stability-quality analysis는 Backtest Analysis 연구 surface로 남기고, Practical Validation / Final Review / Selected Dashboard daily signal governance는 구현하지 않았다.
- Risk-On Momentum 5D S&P 500 universe follow-up:
  - Single Strategy form에 `S&P 500` universe mode를 추가했고 runtime resolver는 `sp500` / `snp500` 입력을 `SP500` managed universe로 해석한다.
  - S&P 500 멤버십 row가 없으면 Top500으로 조용히 대체하지 않고 universe refresh 필요 오류를 반환한다.
  - focused compile / Risk-On service contract tests / DB membership smoke / hygiene check를 통과했다.
- Overview Market Movers Why It Moved V1.7:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/`에서 SEC filing preview를 추가했다.
  - 기존 SEC metadata table은 유지하고, 선택한 filing 1건만 버튼으로 session-only bounded preview한다.
  - 8-K Item / 10-Q·10-K section locator parser와 nested iXBRL sanitizer regression을 service contracts에 추가했다.
  - Browser QA screenshot은 `why-it-moved-v17-sec-preview-qa-20260604.png`로 생성했고 generated artifact라 커밋 대상이 아니다.
- Overview Market Movers Why It Moved V1.8:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/`에서 SEC filing preview를 `공시 Digest`로 확장했다.
  - Digest는 선택 filing 1건의 8-K Item / Exhibit 단서와 10-Q·10-K section / bounded table 단서를 session-only로 보여준다.
  - 기존 SEC metadata table, official SEC link, button-triggered fetch, no DB / no JSONL / no body / no AI summary / no classifier boundary는 유지했다.
  - QA screenshot은 `why-it-moved-v18-sec-digest-qa-20260605.png`로 생성했고 generated artifact라 커밋 대상이 아니다.
- Overview Market Movers SEC preview rollback:
  - 사용자 검토 후 V1.7 selected-filing preview와 V1.8 `공시 Digest`를 table 아래 추가물로 보고 rollback했다.
  - 현재 `Why It Moved > SEC 공시`는 compact metadata table(`양식 / 공시일 / 제목 / 열기`)과 official SEC clickable link만 유지한다.
  - 후속 재무제표 표 preview는 8-K digest가 아니라 별도 10-Q / 10-K 또는 SEC XBRL/companyfacts feature로 설계해야 한다.
- Overview Market Sentiment V1 2차:
  - `.aiworkspace/note/finance/tasks/active/overview-market-sentiment-v1/`에서 Practical Validation sentiment context overlay를 완료했다.
  - `Backtest > Practical Validation`은 CNN Fear & Greed / AAII sentiment를 risk-on / neutral / risk-off 참고 맥락으로 보여주며, `context_only`, `gate_effect=none`, `registry_write=false` 경계를 표시한다.
  - 기존 Practical Validation Gate / selected-route preflight / registry / saved setup / live approval / order / auto rebalance 경계는 변경하지 않았다.
  - 검증: service contracts 255 tests, py_compile, `git diff --check`, Browser QA screenshot 완료.
- Futures Monitor stale refresh fix:
  - `.aiworkspace/note/finance/tasks/active/futures-monitor-stale-refresh-fix-20260607/`에서 Overview Futures Monitor의 간헐적 미갱신 원인을 추적하고 수정했다.
  - 원인은 service candle query가 현재 UTC 기준 lookback만 읽어, yfinance 지연 / 휴장 / 주말 상태의 latest stored candle을 `Missing`처럼 숨긴 것이었다.
  - 이제 차트 window는 각 symbol의 latest stored candle 기준으로 읽고, freshness는 실제 현재 시각 대비 `Stale`로 표시한다.
  - 검증: failing regression -> fix -> focused futures tests 15개, full service contracts 288개, py_compile, `git diff --check`, UI-engine boundary, Browser QA 통과.
- Reference Guides Center V1:
  - `.aiworkspace/note/finance/tasks/active/reference-guides-center-v1-20260607/`에서 `Reference > Guides`를 task-first Reference Center로 개편했다.
  - Streamlit-free `app/services/reference_guides_catalog.py`에 task cards, journeys, status concepts, records map, troubleshooting playbooks를 분리했고, 기존 portfolio-selection guide는 `Portfolio Selection Journey`로 보존했다.
  - Reference는 read-only 안내 surface이며 provider fetch / registry write / broker order / auto rebalance를 추가하지 않았다.
- Reference Guides Journey / Playbooks V2:
  - `.aiworkspace/note/finance/tasks/active/reference-guides-journey-playbooks-v2-20260607/`에서 Reference Center의 journey detail과 troubleshooting playbook을 확장했다.
  - 제품 흐름 tab은 journey별 확인 순서 / failure state / downstream owner를 보여주고, 문제 해결 tab은 playbook별 check steps와 evidence locations를 보여준다.
  - 3차는 Glossary / searchable concept dictionary 통합, 4차는 주요 화면 contextual links 연결로 남긴다.
- Reference Glossary / Concept Dictionary V3:
  - `.aiworkspace/note/finance/tasks/active/reference-glossary-concept-dictionary-v3-20260607/`에서 Guides status lookup과 Glossary page를 shared concept dictionary로 통합했다.
  - `app/services/reference_glossary_catalog.py`가 curated operational concepts, markdown glossary parser, search helper를 소유하고, `Guides`와 `Glossary`가 이를 함께 사용한다.
  - 검증: RED/GREEN catalog tests, 296 focused/service tests, py_compile, UI-engine boundary, `git diff --check`, Browser QA render screenshot 통과.
  - 남은 흐름은 4차 contextual links, 5차 Reference drift guard / QA polish다.
- Reference Contextual Links V4:
  - `.aiworkspace/note/finance/tasks/active/reference-contextual-links-v4-20260608/`에서 주요 workflow 화면의 `Reference help` expander를 추가했다.
  - `app/services/reference_contextual_help.py`가 Backtest Analysis, Practical Validation, Final Review, Operations Console, Portfolio Monitoring별 guide focus / glossary terms / next checks / boundary를 소유한다.
  - 화면 helper는 read-only entry point이며 Guides / Glossary 링크만 제공하고 validation gate, selected decision, saved setup, provider fetch, broker order, auto rebalance를 바꾸지 않는다.
  - 5차는 Reference drift guard / QA polish다.
- Reference Drift Guard / QA Polish V5:
  - `.aiworkspace/note/finance/tasks/active/reference-drift-guard-qa-polish-v5-20260608/`에서 contextual help drift report와 표시 polish를 추가했다.
  - guard는 Glossary term, Reference link target, duplicate surface key, raw guide focus marker를 Streamlit-free로 점검한다.
  - Reference 검색 deep-linking, Ingestion / Overview 전체 surface 확장, DB / registry / saved JSONL rewrite는 하지 않았다.
- Sub-dev Overview / Macro Base Research:
  - `.aiworkspace/note/finance/researches/active/2026-06-sub-dev-overview-macro-base/`에서 sub-dev worktree의 Overview / Ingestion / Operations 분석·시각화 개발 베이스를 정리했다.
  - 결론은 `Overview Macro Context Cockpit V1`을 1차 후보로 두고, `Data Health -> Ingestion Action Queue`, macro source catalog, breadth / heatmap, Events quality view를 후속 후보로 둔다.
  - 이번 작업은 research guide이며 AGENTS.md / ROADMAP / code 변경이나 실제 구현은 하지 않았다.
- Overview Macro Context Cockpit V1:
  - `.aiworkspace/note/finance/tasks/active/overview-macro-context-cockpit-v1-20260608/`에서 1차 구현을 완료했다.
  - `Workspace > Overview` 상단에 기존 DB-backed movers / breadth / futures / sentiment / events / data-health snapshot을 합성한 summary-first cockpit을 추가했다.
  - 새 provider / DB schema / registry 또는 saved JSONL write / provider fetch / validation gate / monitoring signal / trading action은 추가하지 않았다.
  - 다음 흐름은 2차 `Data Health -> Ingestion Handoff`, 3차 breadth / heatmap and macro week view다.
- Overview Data Health Ingestion Handoff V1:
  - `.aiworkspace/note/finance/tasks/active/overview-data-health-ingestion-handoff-v1-20260608/`에서 2차 구현을 완료했다.
  - `Workspace > Overview > Data Health` 상단에 stale / missing / failed / partial / due target을 우선순위화한 read-only handoff lane을 추가했다.
  - Handoff는 owning collection surface와 alternate Overview bounded refresh surface를 안내하지만 job 실행 / action queue persistence / provider fetch / registry or saved JSONL write는 하지 않는다.
  - 다음 흐름은 3차 breadth / heatmap and macro week view, 4차 source/provider hardening 후보, 5차 Overview IA closeout 후보다.
- Overview Breadth / Macro Week V1:
  - `.aiworkspace/note/finance/tasks/active/overview-breadth-macro-week-v1-20260608/`에서 3차 구현을 완료했다.
  - `Sector / Industry` 탭 상단에 breadth / concentration summary와 latest heatmap을 추가했고, `Events` 탭 상단에 14일 macro week lane을 추가했다.
  - 새 provider / schema / registry write / saved JSONL write / UI provider fetch 없이 기존 DB-backed group leadership / event snapshot만 재사용했다.
  - 다음 흐름은 4차 source/provider hardening 후보, 5차 Overview IA closeout 후보다.
- Overview Source Confidence Catalog V1:
  - `.aiworkspace/note/finance/tasks/active/overview-source-confidence-catalog-v1-20260608/`에서 4차 구현을 완료했다.
  - `Workspace > Overview` cockpit 하단에 prices / breadth / futures / sentiment / events / data-health source confidence lane을 추가했다.
  - 같은 cockpit snapshots만 재사용하며 source owner, freshness, caveat, next check를 보여주고 provider fetch / schema / persistence / validation / monitoring / trading semantics는 추가하지 않았다.
  - 다음 흐름은 5차 Overview IA closeout 후보다.
- Overview IA Closeout V1:
  - `.aiworkspace/note/finance/tasks/active/overview-ia-closeout-v1-20260608/`에서 5차 구현을 완료했다.
  - `Workspace > Overview` cockpit 아래에 `Overview Map / Deep Tab Reading Order`를 추가해 Market Context / Data Repair / transitional Candidate Ops 경계를 표시했다.
  - Candidate Ops는 삭제 / 이동하지 않았고, 새 provider / schema / persistence / validation / monitoring / trading semantics도 추가하지 않았다.
  - Overview Macro Context Cockpit 1차~5차 라운드는 구현 closeout됐으며 후속은 Candidate Ops relocation, Reference companion, provider hardening 같은 별도 승인 후보로 남긴다.
- Futures Monitor chart scope follow-up:
  - `.aiworkspace/note/finance/tasks/active/overview-macro-context-cockpit-v1-20260608/`에 follow-up 기록을 추가했다.
  - `Workspace > Overview > Futures Monitor`에 `Charts` control을 추가해 기본 `Compact 6`과 `All with data` 렌더 범위를 명시적으로 선택하게 했다.
  - `All · 23 selected` / `16 / 23 symbols` 상태에서 `All with data`는 DB에 stored candle이 있는 16개 chart를 렌더한다.
- Overview context refresh / Korean copy V1:
  - `.aiworkspace/note/finance/tasks/active/overview-context-refresh-ko-v1-20260610/`에서 1차 구현을 진행했다.
  - `Workspace > Overview` 상단에 `Market Context 일괄 갱신` 버튼을 추가하고, cockpit / Overview Map 주요 설명을 한국어 중심으로 정리했다.
  - 일괄 갱신은 기존 `app/jobs/overview_actions.py` boundary 안에서 SP500 movers, futures, sentiment, FOMC / earnings / macro calendar refresh를 순차 실행한다.
- Overview Market Context Tab V1:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-tab-v1-20260610/`에서 `Market Context`를 Overview 첫 deep tab으로 추가했다.
  - refresh / cockpit / Deep Tab guide / Overview Map을 같은 tab 안으로 이동해 Overview 진입 직후 종합 context를 먼저 보게 했다.
  - 새 provider / schema / registry / saved write / validation or trading semantics는 추가하지 않았다.
- Overview Market Context Readability V2:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-readability-v2-20260610/`에서 Market Context 첫 화면을 summary-first layout으로 정리했다.
  - REVIEW headline을 source/data 상태 중심 copy로 바꾸고, 상태 / 다음 확인 / 자료 기준 rail을 카드 위에 추가했다.
  - 기존 DB-backed read model과 UI renderer만 변경했으며 provider / schema / persistence / validation / trading semantics는 추가하지 않았다.
- Overview Context Supporting Sections V2:
  - `.aiworkspace/note/finance/tasks/active/overview-context-supporting-sections-v2-20260610/`에서 `Source Confidence`와 `Overview Map`을 기본 접힘 disclosure로 낮췄다.
  - Market Context 첫 화면은 summary rail / 핵심 cards / 다음 확인을 먼저 보여주고, source/map 세부는 펼쳐서 확인한다.
  - UI renderer만 변경했으며 provider / schema / persistence / validation / trading semantics는 추가하지 않았다.
- Overview Market Context Brief Flow V1:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-flow-v1-20260612/`에서 Market Context 후속 개선 1차를 완료했다.
  - 기존 `현재 맥락:` headline은 유지하고, standalone `다음 확인 순서` / Deep Tab guide / `해석 전 확인` 카드 흐름을 `시장 브리프` rows와 `해석할 때 같이 볼 변수` rows로 재배치했다.
  - Data Health는 작은 자료 주의점과 접힌 출처 상태로 낮췄고, `보조 갱신`은 하단 secondary maintenance action으로 유지했다.
  - 다음 작업은 갱신 후 상단 context 반영, CPI/Event coverage, Data Health 노출 범위, 과거 유사국면 기능 검토다.
- Overview Market Context Refresh Reflect V1:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-refresh-reflect-v1-20260612/`에서 Market Context 후속 개선 2차를 완료했다.
  - 하단 `보조 갱신` 완료 후 refresh result를 session state에 남기고, 관련 cache를 clear한 뒤 `st.rerun()`으로 상단 cockpit이 새 snapshot을 다시 읽게 했다.
  - 상단에는 success / partial / failure를 구분하는 작은 반영 안내만 추가하고, job result table은 기존 collapsed expander 보조 정보로 유지했다.
  - 후속은 CPI/Event coverage, Macro Calendar 수집/ICS fallback 검증, Data Health 노출 범위 재검토다.
- Overview Market Context Events Data Trust V1:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-events-data-trust-v1-20260612/`에서 Market Context 후속 개선 3차를 완료했다.
  - Events read model은 recent 7D + upcoming horizon을 함께 읽고 FOMC / CPI / PPI / Employment / GDP를 earnings보다 우선하는 context ordering을 적용했다.
  - Macro Week Lane은 recent major / upcoming event section으로 나뉘며, Market Context는 compact event cue와 Data Health 자료 주의점만 보여준다.
  - Local DB에는 `2026-06-10`, `2026-07-14` CPI row가 아직 없어 Macro Calendar collection 또는 BLS `.ics` import가 다음 data coverage follow-up이다.
- Overview Market Context Cardless Brief Layout V1:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-cardless-brief-layout-v1-20260615/`에서 사용자 지적에 따라 Market Context의 카드/그리드 중첩 느낌을 걷어냈다.
  - Summary rail, 시장 브리프, 해석 변수, 과거 유사 맥락, 출처 상태는 row/list/disclosure 중심으로 렌더링하고 data/model semantics는 바꾸지 않았다.
  - 검증은 focused unittest 41개, py_compile, diff check, Browser QA screenshot으로 완료했다.
  - 남은 UX 후보는 mobile density polish와 Market Context 전체 정보량 재조정이다.
- Overview Market Context Copy Density V2:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-copy-density-v2-20260615/`에서 2차 polish를 완료했다.
  - `오늘의 시장 맥락`은 `현재 맥락:` 한 줄 대신 top mover / breadth / futures / next reading order를 2~3문장으로 표시한다.
  - Reading-flow 단락은 typography / color density를 조정해 `시장 브리프`, `해석 변수`, `과거 유사 맥락`, `자료 기준`이 흐름대로 읽히게 했다.
  - 검증은 focused unittest 87개, py_compile, diff check, Browser desktop/mobile DOM QA와 screenshot으로 완료했다.
- Overview Market Context Supporting Flow V3:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-supporting-flow-v3-20260615/`에서 3차 하단 보조 흐름 개선을 완료했다.
  - `해석할 때 같이 볼 변수`는 `다음 맥락 체크`로 바꾸고, cue rows는 이벤트 / 심리 / 매크로 관찰 지점만 남겼다.
  - `과거 유사 맥락`은 참고, `자료 기준 / 출처 상태`는 근거 footer로 낮췄으며 Data Health는 main cue row에서 제거했다.
  - 검증은 focused/regression unittest, py_compile, diff check, Browser QA screenshot으로 완료했다.
- Portfolio Discovery / Final Review / Monitoring 2026-06-08:
  - `.aiworkspace/note/finance/tasks/active/portfolio-discovery-final-review-monitoring-20260608/`에서 현재 Compare catalog 전략을 탐색하고 workflow-complete 후보를 선별했다.
  - 최종 등록 후보는 GTAA U5 20% / GTAA U3 75% / GRS Compact 5%, Final Review decision `final_gtaa_u3_u5_grs_monitoring_20260608`.
  - Portfolio Monitoring setup `selected_dashboard_portfolio_gtaa_u3_u5_grs_20260608` 저장과 performance recheck `SELECTION_THESIS_HOLDS`를 확인했다.
- Distinct Strategy Portfolio Discovery 2026-06-09:
  - `.aiworkspace/note/finance/tasks/active/distinct-strategy-portfolio-discovery-20260609/`에서 중복 strategy family 없이 SPY 대비 우위 후보를 재탐색했다.
  - 최종 등록 후보는 GTAA U3 85% / GRS Compact 10% / Risk Parity Trend 5%, Final Review decision `final_distinct_strategy_gtaa_u3_grs_risk_parity_20260609`.
  - Portfolio Monitoring setup `selected_dashboard_portfolio_distinct_strategy_gtaa_grs_rp_20260609` 저장과 selected dashboard performance recheck `ok`를 확인했다.
- Overview Market Movers Coverage Refresh V1:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-coverage-refresh-v1-20260617/`에서 1차 Nasdaq coverage, 2차 refresh / automation, 3차 diagnostics evidence 보강을 완료했다.
  - Market Movers는 `Nasdaq-listed current snapshot` coverage를 제공하며, latest `nasdaq_symdir_nasdaqlisted` lifecycle row를 직접 읽고 empty state에서는 Symbol Directory refresh를 안내한다.
  - `overview_automation`은 `nasdaq_symbol_directory`와 `nasdaq_intraday` dry-run plan을 노출하고, Coverage Diagnostics는 Likely Cause / Evidence Summary / Next Check / Listing Evidence / Profile Freshness / Market Data Issue를 보여준다.
  - 새 schema / provider / registry or saved JSONL write / OS scheduler 등록 / trading or validation semantics는 추가하지 않았다.
- Overview Market Context Source Action Flow V1:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-source-action-flow-v1-20260618/`에서 1차 Market Context 읽기 흐름 / 자료상태 명확화를 완료했다.
  - `다음 맥락 체크`는 `next_checks` source/action checklist를 렌더링하고, source confidence footer와 보조 갱신 expander도 같은 action 흐름을 따른다.
  - Historical analog는 current as-of / data window / 계산식 기준을 표시하며 context-only boundary를 유지한다.
  - 2차 / 3차 후속 설계 메모는 task `DESIGN.md`에 남겼고, 새 provider / schema / replay storage / macro-conditioned analog 구현은 하지 않았다.
- Overview Market Context Futures-Conditioned Analog V3B:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-futures-conditioned-analog-v3b-20260618/`에서 3차-B를 완료했다.
  - 3차-A의 GLD `Macro 조건 포함 pilot`에 stored futures daily OHLCV Rate Pressure proxy (`ZN=F` / `ZB=F`) 조건 1개를 추가했다.
  - Browser QA 20D path는 broad 69회 -> Macro 조건 sample 1회, GLD / futures condition row 분리 표시, forbidden Korean copy 없음으로 확인했다.
  - FRED rates, events, sentiment, 새 provider / schema / loader, Backtest / Validation / Final Review / Operations logic은 열지 않았다.
- Overview Market Context Brief Flow Redesign V1:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-flow-redesign-v1-20260620/`에서 사용자가 직접 테스트하며 지적한 card-first UX를 brief-first reading flow로 정리했다.
  - Historical analog controls는 analog 섹션 흐름에 붙이고, 기준/패턴/표본/한계 basis ledger와 broad-vs-macro sample comparison, source ledger, `필요 자료 보강` refresh assist를 추가했다.
  - Browser QA 중 selected date/pattern 반영이 한 렌더 늦는 문제를 발견해 supporting model을 controls 후 즉시 reload하도록 수정했다.
  - 검증은 `git diff --check`, py_compile, `tests/test_service_contracts.py` 365개, Streamlit Browser QA screenshot으로 완료했다.
- Overview Market Context Brief Flow Redesign V2:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-flow-redesign-v2-20260620/`에서 V1이 여전히 카드 재배치처럼 보인다는 사용자 피드백을 후속 보정했다.
  - `시장 브리프` rows를 cockpit 안의 `오늘의 시장 브리프` wide lane으로 흡수하고, `다음 맥락 체크`는 priority / observation / reason / action rail로 바꿨다.
  - Historical analog / macro comparison / source evidence는 반복 card background와 left-rule을 줄이고, `Macro 조건 포함 비교`로 broad vs conditioned sample 차이를 먼저 읽게 했다.
  - 검증은 `git diff --check`, py_compile, `tests/test_service_contracts.py` 367개, selected as-of / 20D / monthly Browser QA와 screenshot으로 완료했다.
- Overview Market Context Analog Basis Clarity V10:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-basis-clarity-v10-20260620/`에서 historical analog 기준일 UX 보정을 완료했다.
  - 선택 기준일과 실제 계산 기준일이 다를 때 requested / effective as-of, limiting symbols, basis warning을 표시하고 latest도 DB 공통 가격 기준임을 설명한다.
  - Macro 조건 포함 비교는 broad sample -> GLD 배경 -> 금리선물 압력 funnel과 사용자 언어 condition group으로 정리했다.
  - 검증은 RED/GREEN focused tests, py_compile, `tests/test_service_contracts.py` 377개, latest / selected 2026-06-18 / 20D / monthly Browser QA와 screenshot으로 완료했다.
- Overview Market Context Analog Usability V12:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-usability-v12-20260621/`에서 historical analog V12 보정을 완료했다.
  - selected as-of 공통 daily price basis mismatch를 limiting symbols 대상 `overview_historical_analog_ohlcv` 최신화 action으로 연결했다.
  - broad analog UI는 compact basis summary / 접힌 계산 경계 상세 / core outcome matrix / support summary / 접힌 상세 통계로 정리했다.
  - 검증은 RED/GREEN focused tests, `git diff --check`, py_compile, `tests/test_service_contracts.py` 378개, Streamlit Browser QA와 screenshot으로 완료했다.
- Overview Market Context Flow Alignment V13:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-flow-alignment-v13-20260621/`에서 Market Context 상단 섹터 흐름과 historical analog 기준 섹터를 정렬했다.
  - latest historical analog는 visible daily sector leadership snapshot을 재사용하고, sector pressure map은 canonical 11개 섹터를 균일 tile로 표시한다.
  - Historical analog는 guide block / 별도 시장 배경 요약을 낮추고 sector ETF / SPY / QQQ / TLT / GLD 핵심 matrix와 compact Macro 조건 비교 흐름으로 정리했다.
  - 검증은 RED/GREEN focused tests, `git diff --check`, py_compile, `tests/test_service_contracts.py` 380개, Streamlit Browser QA와 screenshot으로 완료했다.
- Overview Market Context Macro Clarity V14:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-clarity-v14-20260621/`에서 Macro 조건 비교 읽기 구조를 다시 정리했다.
  - `Sector ETF vs SPY relative strength`는 broad sample 기준으로 분리하고, GLD / Rate Pressure futures는 Macro 추가 조건으로 표본 축소 흐름에 표시한다.
  - Macro 섹션은 broad-vs-conditioned 결과 변화, 현재 Macro 배경(T10Y3M / VIXCLS / BAA10Y), 접힌 상세 / 원본 통계 순서로 읽게 했고, matrix 색상 농도와 sector pressure 2자리 표시를 추가했다.
  - 검증은 RED/GREEN focused tests, `git diff --check`, py_compile, `tests/test_service_contracts.py` 382개, Streamlit Browser QA와 screenshot으로 완료했다.
- Overview Market Context Macro Labels V15:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-labels-v15-20260621/`에서 V14 Macro 조건 비교 문구를 사용자 언어로 보정했다.
  - `Macro 추가 조건` 반복 라벨을 `GLD 조건 적용` / `금리선물 조건 적용`으로 바꾸고, `81회 -> 37회 -> 6회`가 broad anchor pool에서 조건별로 좁혀진 표본임을 문장으로 표시한다.
  - `현재 Macro 배경 참고`에는 T10Y3M / VIXCLS / BAA10Y 한글 설명과 broad sample 중 같은 상태 횟수를 함께 보여준다.
  - 검증은 RED/GREEN focused tests, `git diff --check`, py_compile, `tests/test_service_contracts.py` 382개, Streamlit Browser QA와 screenshot으로 완료했다.
- Overview Market Context Macro Matrix V16:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-matrix-v16-20260621/`에서 V15 Macro 섹션이 여전히 wide table / verbose text처럼 보인다는 사용자 피드백을 보정했다.
  - Macro 표본 흐름은 historical analog와 같은 basis bar로 바꾸고, 결과 변화는 자산 x `기본 / 조건 후 / 변화` matrix로 렌더링한다.
  - 긴 조건 source 원문과 raw 통계는 `Macro 조건 상세`로 낮추고, 현재 Macro 배경은 한글 우선 라벨로 정리했다.
  - 검증은 RED/GREEN focused tests, `git diff --check`, py_compile, `tests/test_service_contracts.py` 382개, Streamlit Browser QA와 screenshot으로 완료했다.
- Overview Market Context Macro Meaning Gradient V19:
  - `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-meaning-gradient-v19-20260622/`에서 matrix 색상 가시성과 Macro reference 값 해석을 보정했다.
  - 핵심 자산 비교와 Macro 조건 결과 비교 matrix는 median / delta 방향과 크기를 green/red gradient로 더 분명히 보여준다.
  - 조건에는 쓰지 않은 Macro 배경은 T10Y3M / VIXCLS / BAA10Y 현재 값이 어떤 상태인지 한 줄 의미 문장으로 설명한다.
  - 검증은 RED/GREEN focused tests, `git diff --check`, py_compile, `tests/test_service_contracts.py` 382개, Streamlit Browser QA와 screenshot으로 완료했다.
- Overview Lazy Tab Render V20:
  - `.aiworkspace/note/finance/tasks/active/overview-lazy-tab-render-v20-20260622/`에서 Overview 첫 진입 로딩을 줄이기 위해 top-level deep tab을 selected-tab lazy render로 바꿨다.
  - 기본 선택은 `Market Context`이며 Market Movers / Futures Monitor / Sentiment / Sector / Industry / Events / Data Health / Candidate Ops는 선택 시점에만 렌더된다.
  - Candidate Ops dashboard snapshot load도 Candidate Ops branch 안으로 지연했고, 각 탭 내부 read model / data boundary / trade semantics는 바꾸지 않았다.
  - 검증은 RED/GREEN focused tests, OverviewAutomationContractTests 68개, `tests/test_service_contracts.py` 384개, py_compile, `git diff --check`, Streamlit Browser QA와 screenshot으로 완료했다.
- Overview Market Context Direct Refresh Scope 2026-06-24:
  - Market Context `필요 자료 보강`은 현재 화면 direct 자료만 실행하도록 좁혔다.
  - Top1000 / Top2000 / Futures refresh는 Market Context 보강에서 제외하고 Market Movers / Futures Macro / Ingestion 전용 흐름에 남겼다.
  - 현재 DB 기준 `현재 이슈만 보강`은 S&P 500 Daily Snapshot 1개만 남는 것을 확인했다.
  - 관련 경계는 `PROJECT_MAP.md`, `SCRIPT_STRUCTURE_MAP.md`, `OVERVIEW_MARKET_INTELLIGENCE.md`에 반영했다.
- Overview Tab Module Split V1 2026-06-25:
  - `app/web/overview_dashboard.py`를 compatibility wrapper로 줄이고 active page shell을 `app/web/overview/page.py`로 분리했다.
  - Market Context / Market Movers / Futures Macro / Sentiment / Events primary tab entry modules를 `app/web/overview/` 아래에 추가했다.
  - 기존 monolithic helper 구현은 `app/web/overview/legacy_dashboard.py`에 보존했다. V2는 탭별 helper / controls 이동이다.
  - 작업 기록은 `.aiworkspace/note/finance/tasks/active/overview-tab-module-split-v1-20260625/`를 보면 된다.
- Overview Legacy Cleanup V6-V10 2026-06-25:
  - `.aiworkspace/note/finance/tasks/active/overview-legacy-cleanup-v6-v10-20260625/`에서 legacy audit, navigation surface extraction, IA read model service extraction, confirmed unused wrapper / Candidate Ops snapshot helper removal, guard tests, final QA를 순서대로 완료했다.
  - Active Overview ownership은 `app/web/overview/page.py`, `app/web/overview/navigation.py`, `app/web/overview/{market_context,market_movers,futures_macro,sentiment,events}.py`로 정리했고, `legacy_dashboard.py`는 helper compatibility surface로 남겼다.
  - 검증은 V6-V10 각 차수별 Browser QA, py_compile, OverviewAutomationContractTests, `git diff --check`로 기록했다.
- Backtest Analysis Commercial UX Research 2026-06-29:
  - `.aiworkspace/note/finance/researches/active/2026-06-backtest-analysis-commercial-ux/`에 Backtest Analysis 과도한 guide / Reference / readiness 흐름을 줄이기 위한 audit, benchmark, 단계별 개발 가이드를 작성했다.
  - 결론은 `Backtest 사용 안내`와 `Reference help`를 기본 Backtest Analysis에서 제거하고, Latest Run을 summary-first / validation handoff eligibility 중심으로 재설계하는 것이다.
  - 다음 구현 세션은 `DEVELOPMENT_GUIDELINES.md`의 1차 `Backtest Analysis Default Surface Cleanup`만 승인 범위로 여는 것을 권장한다.
- GTAA SPY Low-MDD Top-2 ADV20 2026-06-29:
  - `.aiworkspace/note/finance/tasks/active/gtaa-spy-cagr-mdd-preset-search-20260629/`에서 SPY 대비 CAGR/MDD 개선, CAGR 11% 이상, MDD 절대값 15% 이하, current 1차 promotion gate 통과 후보를 확인했다.
  - 새 anchor는 `GTAA SPY Low-MDD Style Top-2 ADV20`: `QQQ, SOXX, MTUM, QUAL, USMV, IAU, IEF, TLT`, `top=2`, `interval=4`, `1M/6M`, `MA200`, `ADV20D=20M`; 결과는 `24.08% / -9.99% / real_money_candidate`.
  - GTAA runtime에 ADV20 liquidity evidence를 연결했고, preset 선택 시 핵심 파라미터가 자동 적용되도록 했다. 상세 결과는 `.aiworkspace/note/finance/reports/backtests/runs/2026/strategy_search/GTAA_SPY_LOW_MDD_TOP2_ADV20_20260629.md`를 보면 된다.
- Overview Market Movers Workbench V1 2026-06-29:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-workbench-v1-20260629/`에서 1차 Market Movers UX 골격 재설계를 완료했다.
  - 상단 command strip으로 coverage / period / effective timestamp / freshness / universe / returnable / missing / mode를 먼저 보여주고, 본문은 `상위 변동종목 목록` + `핵심 차트 / 섹터 요약` + 보조 diagnostics + `선택 종목 조사` 흐름으로 정리했다.
  - 검증은 py_compile, `git diff --check`, focused unittest fallback, Streamlit Browser QA(SP500 daily/weekly, NASDAQ daily/weekly, narrow viewport)로 완료했다. 2차는 explicit exploration mode / ranking read model 정리다.
- Overview Market Movers Modes V2 2026-06-29:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-modes-v2-20260629/`에서 2차 탐색 모드와 ranking read model 정리를 완료했다.
  - `mover_views`로 Top Gainers / Top Losers / Volume Leaders / Unusual Volume / Sector Leaders를 추가하고, UI는 선택 모드 표/차트를 첫 화면에 렌더링한다.
  - 검증은 RED/GREEN focused tests, `git diff --check`, py_compile, unittest fallback, Streamlit Browser QA(SP500 daily/weekly, NASDAQ coverage, narrow viewport)로 완료했다. 3차는 선택 종목 detail pane과 Why It Moved 통합이다.
- Overview Market Movers Detail V3 2026-06-29:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-detail-v3-20260629/`에서 3차 선택 종목 detail pane과 Why It Moved 조사 흐름 통합을 완료했다.
  - 선택된 탐색 모드의 종목을 기준으로 rank / price / volume / relative volume / 같은 섹터 위치 / metadata 상태 / 뉴스·한국어 뉴스·SEC·외부 검색 시작점을 한 패널에 묶었다.
  - metadata 조회는 기존 why_it_moved service boundary를 통한 사용자 버튼 동작으로만 유지하고, 자동 원인 판정 / score / 추천 / 저장은 추가하지 않았다.
  - 검증은 RED/GREEN focused tests, `git diff --check`, py_compile, unittest fallback, Streamlit Browser QA(SP500 daily/weekly, NASDAQ coverage, narrow viewport)로 완료했다. 4차는 sector/heatmap/breadth 맥락 개선이다.
- Overview Market Movers Sector V4 2026-06-29:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-sector-v4-20260629/`에서 4차 sector / heatmap / breadth 맥락 개선을 완료했다.
  - 기존 mover return rows로 full `sector_breadth` read model을 만들고, advancers / decliners, 평균·중앙·시총가중 수익률, market-cap share proxy, sector별 top gainer / loser를 heatmap과 fallback table로 렌더링한다.
  - 4차도 context-only 경계를 유지했다. 새 provider / schema / 외부 fetch / sector rotation prediction / 추천 / Backtest·Validation·Final Review·Operations 연결은 추가하지 않았다.
  - 검증은 RED/GREEN focused tests, `git diff --check`, py_compile, unittest fallback, Streamlit Browser QA(SP500 daily/weekly, NASDAQ coverage, narrow viewport)로 완료했다. 5차는 Coverage/Data Quality trust UX 정리다.
- Overview Market Movers Quality V5 2026-06-29:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-quality-v5-20260629/`에서 5차 Coverage/Data Quality UX 정리를 완료했다.
  - `coverage trust` read model과 `자료 신뢰 상태` strip을 추가하고, grouped missing diagnostics를 먼저 보여주며 raw diagnostics / quote-gap diagnosis는 collapsed expander에 남겼다.
  - Nasdaq no-universe는 기존 Overview action facade의 Symbol Directory refresh로만 이어지며, 새 provider / schema / signal / monitoring UX는 추가하지 않았다.
  - 검증은 RED/GREEN focused tests, `git diff --check`, py_compile, unittest fallback, Streamlit Browser QA(SP500 daily/weekly, NASDAQ coverage, narrow viewport)로 완료했다.
- Fundamental Source Migration Research 2026-06-30:
  - `.aiworkspace/note/finance/researches/active/2026-06-fundamental-source-migration/`에서 yfinance broad fundamentals와 EDGAR statement ledger / shadow 의존성을 audit했다.
  - 결론은 yfinance financial statements를 즉시 삭제하지 말고 legacy/fallback으로 freeze하고, EDGAR annual statement shadow를 primary로 승격하되 quarterly 10-K/FY 혼입 문제를 먼저 수정하는 것이다.
  - 다음 개발은 Market Movers detail annual source 전환, quarterly correctness, broad quality_snapshot deprecation 순서로 잡는 것이 안전하다.
- Fundamental Source Migration Phase 7 2026-06-30:
  - `.aiworkspace/note/finance/tasks/active/fundamental-source-migration-p7-legacy-yfinance-decommission/`에서 legacy broad yfinance active UI 제거를 완료했다.
  - Ingestion의 broad fundamentals / factor 실행 카드는 내려가고, old run history / saved replay용 action handler와 table은 유지했다.
  - 검증은 focused RED/GREEN, `git diff --check`, py_compile, service contract filtered pytest, Ingestion Browser QA로 기록했다.
- Fundamental Source Migration Phase 8 2026-06-30:
  - `.aiworkspace/note/finance/tasks/active/fundamental-source-migration-p8-final-docs-runbook-alignment/`에서 source migration closeout docs를 완료했다.
  - Durable docs는 EDGAR statement shadow를 canonical financial statement path로, broad yfinance fundamentals / factors를 legacy compatibility로 정렬했다.
  - 다음 세션은 `.aiworkspace/note/finance/docs/data/README.md`, `DB_SCHEMA_MAP.md`, `DATA_FLOW_MAP.md`, `TABLE_SEMANTICS.md`, `EDGAR_FINANCIAL_STATEMENT_REFRESH.md`를 보면 source contract를 확인할 수 있다.
- Ingestion Console Action Unification V2 2026-07-01:
  - `.aiworkspace/note/finance/tasks/active/ingestion-console-action-unification-v2-20260701/`에서 Ingestion action registry, scheduled diagnostics, shared progress, active / compatibility action boundary를 1~6차로 정리했다.
  - Ingestion workbench는 `일상 운영 / 검증 데이터`, `수동 복구 / 진단`, `실행 기록 / 결과` 3개 section을 유지하고, read-only 진단도 공용 scheduled job / run history / progress 흐름을 탄다.
  - Broad yfinance fundamentals / factors는 active UI가 아니라 old replay / explicit comparison compatibility로만 남긴다.
- Overview Market Movers Statement Collection Status 2026-07-01:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-statement-collection-status-20260701/`에서 기본 지표 하단에 재무제표 수집 / 반영 상태 lane을 추가했다.
  - EDGAR filing ledger 최신 10-Q / 10-K report date와 statement shadow period를 비교해 미반영 공시는 `받아야 할 재무제표 있음`, 반영 완료는 OK로 표시한다.
  - Browser QA 중 GIS fiscal quarter false positive를 발견해 prediction-only quarter-end 비교에 14일 tolerance를 추가했다.
- Ingestion Console Module Split V1 2026-07-01:
  - `.aiworkspace/note/finance/tasks/active/ingestion-console-module-split-v1-20260701/`에서 Ingestion script structure refactor를 1~6차로 진행했다.
  - `app/web/ingestion_console.py`는 compatibility facade가 되었고 active UI는 `app/web/ingestion/{page,registry,guides,styles,results,dispatcher,sections}.py`로 나뉘었다.
  - `app/jobs/ingestion/common.py`가 symbol parsing, normalized result, progress/status helper를 소유하고 `app/jobs/ingestion_jobs.py`는 기존 import path를 유지한다.
- Overview Market Movers React Pilot 2026-07-03:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-react-pilot-20260703/`에서 0~8차를 순차 개발 / QA / commit으로 완료했다.
  - React custom component가 Market Movers filters, summary, coverage trust detail, action strip을 렌더링하고, action / state normalization은 기존 Overview Python facade와 session result key로 dispatch된다.
  - Streamlit fallback은 유지한다. 다른 Overview 탭 확장은 이 pilot QA 결과를 확인한 뒤 별도 phase로 잡는다.
- Overview Market Movers Liquidity Universe V1 2026-07-05:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-liquidity-universe-v1-20260705/`에서 1~6차 개발 / QA / commit을 진행했다.
  - Top1000 / Top2000 기준은 `nyse_asset_profile.market_cap`에서 `market_liquidity_universe_member`의 최근 20거래일 평균 거래대금 materialized membership으로 전환됐다.
  - `유니버스 기준 갱신`은 SP500 구성, Nasdaq Symbol Directory, Top liquidity universe materialize로 분기하며, Market Movers 기본 UI에서는 `가격 이력 갱신` primary action을 숨겼다.
  - Local DB smoke 기준 TOP1000은 1,000개, TOP2000은 1,920개가 저장됐고, Browser QA에서 남은 `by market cap` 문구를 제거했다.
- Overview Market Movers Sector React Follow-up 2026-07-05:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-sector-react-20260705/`에서 React 섹터 breadth 상세표 펼침 시 iframe 높이가 갱신되지 않아 표가 잘리는 문제를 수정했다.
  - `<details>` toggle 시 custom component frame height를 재동기화하고, Browser QA에서 섹터 iframe 높이가 `765 -> 1617`로 늘어나는 것을 확인했다.
- Overview Futures Macro React UX Phase 3 2026-07-05:
  - `.aiworkspace/note/finance/tasks/active/overview-futures-macro-react-ux-20260705/`에서 3차 1W / 1M reading-flow 확장을 완료했다.
  - `flow_context`는 저장된 1D 선물의 `5D %` / `20D %`로 1주 / 1개월 흐름을 만들고, React workbench는 기간 탭으로 렌더링한다.
  - 다음 차수는 4차 mixed subtype / confidence interpretation refinement다.
- Overview Futures Macro Session Basis / Score Sign UX 2026-07-06:
  - `.aiworkspace/note/finance/tasks/active/overview-futures-macro-evidence-original-data-ux-20260706/` 후속으로 React 기준일 표기를 `CME/yfinance 일봉 세션 기준`으로 바꿨다.
  - Score chips는 `+ 위험선호 강화 · - 위험회피`, `+ 금리 부담 확대 · - 금리 부담 완화` 같은 polarity hint를 보여줘 양수 / 음수가 보편적 good/bad가 아니라 score-family 방향임을 드러낸다.
  - QA는 focused contracts, FuturesMacroThermometer contracts, `py_compile`, React build, Browser QA로 완료했다.
- Overview Futures Macro 1D Flow Tab 2026-07-06:
  - `Futures Macro` React flow tabs now use `1D / 1W / 1M`, defaulting to 1D so the current standardized score can be compared with raw one-day moves before weekly / monthly context.
  - Existing 1W `weekly_context` compatibility remains pinned to 1W; DB collection, schema, and provider refresh boundaries are unchanged.
  - QA covered RED/GREEN contracts, the focused 26-test Futures Macro suite, `py_compile`, `git diff --check`, and Browser QA.
- Overview Futures Macro Historical Validation UX 2026-07-06:
  - `과거 점검` is now framed as `오늘과 비슷한 과거 흐름 확인`: the current 16-futures daily score state is compared against historical dates computed with the same classification method.
  - The React panel owns the historical-validation action, inline loading state, and metric-backed result tiles for `판정`, `5거래일 표본`, `20거래일 표본`, and `자산군 해석`.
  - The panel now shows first-read conclusion tiles for `비슷한 상태`, `상태 빈도`, `방향성 판정`, and `판정 이유` before detailed 5D / 20D tiles. Lower `원본 데이터 / 계산 추적` stays focused on raw score / contribution / daily futures / historical sample tables; validation prose uses only computed sample / mean-return / hit-rate metrics and does not create recommendation copy.
- Overview Sentiment React UX 2026-07-07:
  - `.aiworkspace/note/finance/tasks/active/overview-sentiment-react-ux-20260707/`에서 1~5차 개발 / QA / 커밋 흐름을 완료했다.
  - Sentiment는 React workbench로 phase/headline/summary, freshness/action, CNN / AAII cross-read, driver lanes, component explanations, hover-readable history line chart, component bars, stored evidence tables를 렌더링한다.
  - 후속 피드백으로 기본 화면의 next-check cards는 제거했고, history graph hover tooltip은 날짜 / 시리즈 / 값 / source를 보여준다.
  - Python service/helper가 DB read, refresh action, interpretation text를 계속 소유하고 React는 표시/dispatch만 맡는다. Browser QA screenshot은 generated artifact로 남기고 커밋하지 않는다.
- Overview Sentiment context-depth follow-up 2026-07-07:
  - 같은 task에서 CNN / AAII 최근 range percentile, CNN headline / component / AAII divergence, CNN component latest-vs-previous change context를 service read model에 추가했다.
  - React workbench는 range cards, divergence panel, component-history section으로 표시하고, Browser QA에서 range 3개 / divergence axis 3개 / component history 7개 렌더링을 확인했다.
  - 새 screenshot은 generated artifact로 남기고 커밋하지 않는다. 다음에 이어 볼 위치는 `.aiworkspace/note/finance/tasks/active/overview-sentiment-react-ux-20260707/`이다.
- Overview Sentiment divergence copy follow-up 2026-07-07:
  - `지표 합의 상태` framing을 제거하고 React heading을 `엇갈리는 지점`으로 바꿨다.
  - CNN headline / CNN components / AAII survey axis cards는 metric 정의가 아니라 service-owned current interpretation copy를 보여준다.
  - QA와 상세 기록은 `.aiworkspace/note/finance/tasks/active/overview-sentiment-react-ux-20260707/`의 `STATUS.md` / `RUNS.md`를 본다.
- Overview Events Calendar 4차 Earnings Universe 2026-07-07:
  - `.aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/`에서 Earnings 수집 row에 taxonomy 필드와 universe/source-authority contract를 채웠다.
  - S&P 500 / large-cap batch는 canonical source로 저장되고, portfolio / watchlist / Nasdaq-100은 explicit symbol loader boundary로 열었다.
  - 다음 차수는 market-structure 일정 수집이며 generated screenshots / run history는 계속 커밋 제외한다.
- Overview Events Calendar 5차 Market Structure 2026-07-07:
  - Nasdaq Trader holiday / early close, Cboe options expiration, FTSE Russell reconstitution calendar를 market-structure background event로 수집하는 경계를 추가했다.
  - Ingestion의 시장 이벤트 캘린더 수집에 `시장 구조 일정` 탭과 `collect_market_structure_calendar` job을 연결했다.
  - 다음 차수는 Python service가 React workbench용 hero / rail / trust / chart payload를 구조화하는 작업이다.
- Overview Events Calendar 6차 Workbench Payload 2026-07-07:
  - `app/services/overview/events.py`에 `build_events_workbench_payload()`를 추가해 hero brief, rails, trust review, calendar / density, evidence rows를 Python-owned contract로 만들었다.
  - React는 다음 차수부터 이 payload만 렌더링하고, 거래 신호 / validation gate / monitoring action 문구를 만들지 않는다.
  - 다음 차수는 `app/web/streamlit_components/events_workbench`와 `app/web/overview/events_react_component.py` scaffold다.
- Overview Events Calendar 7차 React Scaffold 2026-07-07:
  - `events_workbench` Vite component, static build, Python wrapper, Events tab integration을 추가했다.
  - React는 현재 additive scaffold로 기존 Streamlit lanes / detail tabs 위에 렌더링되며 fallback을 제거하지 않았다.
  - 다음 차수는 hero brief / freshness / refresh UX를 React 쪽에서 제품 흐름으로 다듬는 작업이다.
- Overview Events legacy cleanup follow-up 2026-07-07:
  - React workbench build가 있으면 Events 탭은 중복 Streamlit summary / source / macro-week lanes와 상단 Refresh popover를 숨기고, React command band를 refresh entry로 사용한다.
  - Streamlit Agenda / Calendar / Quality / Raw는 삭제하지 않고 하단 `상세 표 / 전체 근거` collapsed fallback/evidence section으로 낮췄다.
  - React component는 incoming payload를 직접 mutate하지 않도록 기본값을 파생 상수로 정리했다. 상세 QA 기록은 `.aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/RUNS.md`를 본다.
- Overview Events feedback follow-up 1~6차 2026-07-07:
  - 상단 Streamlit `일정 타입` / separate `Refresh Results`를 React-first path에서 제거하고, refresh 결과는 React command band의 last results로 통합했다.
  - React는 `전체 일정 갱신`, 실적 예상 일정 기준, 탭형 event rails, `일정 확정성 / 추정 일정 점검`, 오늘/current-week highlight가 있는 월간 calendar grid를 렌더한다.
  - QA와 commit handoff는 `.aiworkspace/note/finance/tasks/active/overview-events-ux-redesign/STATUS.md` / `RUNS.md`를 본다. Browser screenshots는 generated artifact로 커밋 제외한다.
- Overview Market Movers smart EOD refresh 1~3차 2026-07-07:
  - Weekly / Monthly / Yearly 가격 이력 갱신은 freshness preflight로 최신 종목을 스킵하고 stale 종목은 delta, missing / insufficient coverage 종목은 full fallback window로 보강한다.
  - latest close / volume 이상값은 quality repair 대상으로 포함하며, UI result caption은 갱신 대상 / 최신 스킵 / Delta / Full window / 품질 보강 수를 요약한다.
  - 상세 QA와 한계는 `.aiworkspace/note/finance/tasks/active/overview-market-movers-smart-eod-refresh-20260707/`를 본다. Browser screenshots / run history는 커밋 제외한다.
- Overview Market Movers EOD refresh scope 1~4차 2026-07-08:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-eod-refresh-scope-20260708/`에서 Top1000 weekly refresh가 반복해서 길어지는 원인을 action as-of / universe / batch 범위 불일치로 정리하고 수정했다.
  - Top1000 / Top2000 가격 이력 갱신은 화면과 같은 materialized liquidity universe를 쓰고, 화면 effective EOD date를 `as_of_date`로 넘겨 KST 하루 차이로 current symbols가 stale 처리되지 않게 했다.
  - Preflight와 React action detail은 수집 대상 수, 범위, 시작일 이유를 클릭 전 보여주며, 상태는 `계산 가능 · 이력 보강 필요`로 화면 계산 정상과 refresh debt를 분리한다.
- Overview Market Movers Fundamental Chart polish 2026-07-08:
  - `.aiworkspace/note/finance/tasks/active/overview-market-movers-fundamental-charts-20260708/` 후속으로 기본지표 그래프의 연간 / 분기 nested tabs를 제거했다.
  - 각 PER / EPS / 당기순이익 / 유동비율 / FCF 탭은 연간 그래프와 분기 그래프를 좌우 한 row로 보여주며, 각 그래프는 tall bar, tighter spacing, 내부 horizontal scroll, SVG line overlay를 사용한다.
  - 추가 후속으로 막대 위 숫자를 제거하고 기간 / 값을 하단 2줄 caption으로 분리했다. Browser QA는 in-app browser localhost URL policy로 차단됐고, 검증은 focused tests / `py_compile` / static preview로 기록했다.
  - 분기 그래프가 2023년 이후 8개만 보인 원인은 service trend limit이 연간/분기 모두 8개였기 때문이라, 분기는 최대 32개까지 유지하도록 수정했다. 콤마 문자열 금액도 억/만/천 달러 formatter를 타도록 보강했다.
- Backtest Entry Cleanup Tabs V1 2026-06-30:
  - `.aiworkspace/note/finance/tasks/active/backtest-entry-cleanup-tabs-v1-20260630/`에서 Backtest 첫 화면 안내 / strategy capability helper / 하단 연구 참고 보드를 기본 render path에서 제거했다.
  - 3단계 workflow selector는 Overview와 같은 `st.pills` 기반 Korean-first text tab + red underline으로 맞췄다.
  - 검증은 focused RED/GREEN, Boundary / Backtest 관련 43개 unittest, py_compile, `git diff --check`, Browser QA screenshot으로 완료했다.
- Backtest Boundary Refactor V1 2026-07-01:
  - `.aiworkspace/note/finance/tasks/active/backtest-boundary-refactor-v1/`에서 1차~7차 staged refactor를 진행했다.
  - UI state / formatter, Single Strategy payload, Portfolio Mix readiness, validation status policy, Final Review policy, runtime runner catalog 경계를 추가했다.
  - 전략 계산식, validation threshold, registry / saved JSONL / provider DB 의미는 바꾸지 않았다.
- Backtest Final Boundary Refactor V2-V8 2026-07-01:
  - `docs/superpowers/plans/2026-07-01-backtest-final-boundary-refactor.md` 기준으로 runtime package, runners, stores/read_models, Single Strategy forms, Portfolio Mix Builder, Practical Validation, Final Review package split을 순차 완료했다.
  - 각 차수는 development -> QA -> commit으로 닫았고, V8에서 durable docs / root logs / task logs / full QA / Browser QA를 마무리했다.
  - 상세 완료 구조와 QA 기록은 `.aiworkspace/note/finance/tasks/active/backtest-boundary-refactor-v1/STATUS.md`와 `RUNS.md`를 보면 된다.
- Backtest Handoff UI Integrated V1 2026-07-02:
  - `.aiworkspace/note/finance/tasks/active/backtest-handoff-ui-integrated-v1-20260702/`에서 Latest Backtest Run의 `2차 실전성 검증 Handoff` 중복 UI를 단일 custom panel로 통합했다.
  - gate 판정, Practical Validation source 저장 경로, registry / saved JSONL, strategy runtime은 변경하지 않았다.
  - 후속 V2 후보는 handoff readiness policy의 service extraction과 `Policy Signal Meta` 역할 정리다.
- Backtest Handoff Readiness V2-V6 2026-07-02:
  - `.aiworkspace/note/finance/tasks/active/backtest-handoff-readiness-v2-v6-20260702/`에서 readiness policy service extraction, grouped gate display, `검증 신호 · Policy Signals` cleanup, Practical Validation source snapshot persistence, final QA/docs closeout을 완료했다.
  - 버튼 활성화 기준은 보수적으로 유지했다: promotion hold, execution blocker, validation blocker가 있으면 source registration은 막힌다.
  - Browser QA는 current worktree server `localhost:8502`에서 Equal Weight / Dividend ETFs 실행 후 확인했고, screenshot은 generated artifact로 커밋하지 않았다.
- Backtest 2차 확인 큐 이동 2026-07-03:
  - Backtest Analysis의 `2차 확인` review focus 상세를 1차 처리 항목처럼 펼치지 않고, compact count / handoff notice로 낮췄다.
  - Practical Validation `1. 선택 후보 확인` 상단에서 `entry_gate.review_focus_rows`를 `Backtest에서 넘어온 2차 확인 항목`으로 이어 보게 했다.
  - hard blocker / source 등록 기준은 유지했고, review focus의 책임 위치만 2차 화면으로 옮겼다.
- Backtest Handoff / Policy Signals action cleanup V1-V4 2026-07-04:
  - Handoff를 유일한 Practical Validation 진입 판단 / source 등록 action surface로 두고, Policy Signals는 evidence detail surface로 낮췄다.
  - Streamlit-only production path에서 Handoff action shell을 통합했고, React custom component POC는 `app/web/components/backtest_handoff_action/`에 격리해 두었다.
  - React POC는 현재 source registration에 연결하지 않고, 반복되는 고급 action-card 수요가 확인될 때만 production wiring 후보로 본다.
- Backtest Handoff React action card correction 2026-07-05:
  - 사용자 피드백에 따라 Handoff action을 Streamlit shell에서 React Handoff action card production path로 전환했다.
  - 보이는 `2차 실전성 검증 Handoff` card와 버튼은 React component가 함께 렌더링하고, Python은 submit event를 받아 current selection source 등록 / rerun만 수행한다.
  - Policy Signals는 계속 evidence detail만 소유하며, registry / saved / strategy runtime 계약은 변경하지 않았다.
- Backtest Policy Signal Stage Split V1 2026-07-05:
  - `.aiworkspace/note/finance/tasks/active/backtest-policy-signal-stage-split-v1-20260705/`에서 `검증 기준 상세`을 1차 source 기준 React board로 정리했다.
  - 2차 review focus는 Backtest Analysis에서 count / group handoff만 보이고, 상세 row는 Practical Validation `Backtest에서 넘어온 2차 확인 항목`에서 확인한다.
  - gate math, source registration write, registry / saved / strategy runtime 계약은 변경하지 않았다.
- Backtest Handoff Entry Gate Queue V1 2026-07-05:
  - `.aiworkspace/note/finance/tasks/active/backtest-handoff-entry-gate-queue-v1-20260705/`에서 Handoff card의 visible `진입 준비도` score를 제거하고 `1차 진입 기준 / 먼저 해결 / 2차 확인 큐`로 바꿨다.
  - `promotion_decision=hold`는 1차 source 등록 blocker가 아니라 Practical Validation으로 전달되는 2차 review queue로 표시한다.
  - React card / button integration은 유지하고, registry / saved / strategy runtime / gate threshold는 변경하지 않았다.
- Backtest Second Stage Visibility V1 2026-07-05:
  - `.aiworkspace/note/finance/tasks/active/backtest-second-stage-visibility-v1-20260705/`에서 Data Trust와 Handoff의 1차 / 2차 표시 경계를 추가 정리했다.
  - Data Trust는 excluded ticker / malformed price row 같은 1차 데이터 이슈만 상세 표시하고, `meta["warnings"]` review focus는 2차 전달 count로만 남긴다.
  - Practical Validation `Backtest에서 넘어온 2차 확인 항목`의 상세 queue 전달은 유지했고, gate threshold / source registration / registry / strategy runtime은 변경하지 않았다.
- Backtest Entry Gate Ownership Correction 2026-07-05:
  - Backtest Analysis visible surface에서 `2차 확인 큐` count / `2차 전달` Data Trust 표시 / readiness score를 제거하고, 1차 source 등록 기준과 버튼 활성화만 남겼다.
  - `promotion_decision=hold` 등 review focus는 버튼을 막지 않고 source contract `entry_gate.review_focus_rows`로만 Practical Validation에 전달한다.
  - Practical Validation `Backtest에서 넘어온 2차 확인 항목` 상세 표시와 registry / saved / strategy runtime 계약은 유지했다.

## 2026-07-05 - Backtest Data Trust Price Refresh V1

- Added Backtest Data Trust price refresh planning / execution path so stale OHLCV can be repaired for the current backtest ticker set.
- The UI action appears only when DB common latest price date is older than the latest completed NYSE trading day after excluding weekends / holidays.
- Boundary retained: refresh uses existing `run_collect_ohlcv`; no automatic rerun, source registration, validation handoff, approval, or order behavior.
- Follow-up UI integration moved the visible price-refresh card and button into `app/web/components/backtest_price_refresh_action/` React custom component, matching the Handoff action pattern while Python keeps the ingestion side effect.

## 2026-07-06 - Practical Validation Flow 3/4 Handoff Style V2

- `.aiworkspace/note/finance/tasks/active/practical-validation-flow3-flow4-handoff-style-v2-20260706/`에서 Flow 3/4를 Practical Validation에 맞게 다시 정리했다.
- Flow 3 React Fix Queue는 Final Review 이동 판단 / 다음 단계 / 먼저 해결할 일 / 기준 요약을 보여주는 read-only first-read board가 됐다.
- Flow 4는 `Final Review 이동 기준 상세` board를 먼저 보여주고 Source Readiness / Validation Readiness / Final Review Readiness Preview의 판정 근거와 보강 위치를 정리한다.
- Gate threshold, replay 실행, provider 수집, registry / saved JSONL, Final Review persistence, live approval / broker order / auto rebalance 경계는 바꾸지 않았다.

## 2026-07-06 - Practical Validation Readable Fix Queue V1

- `.aiworkspace/note/finance/tasks/active/practical-validation-readable-fix-queue-v1-20260706/`에서 Flow 3 / Flow 4 blocker copy를 사용자 언어로 바꿨다.
- Flow 3 `먼저 해결할 일`은 `무엇을 검증했나 / 부족한 점 / 해야 할 일 / 왜 중요한가`를 먼저 보여주고, `NEEDS_INPUT` / `NOT_RUN`은 `기술 기준` tag로 낮춘다.
- Flow 4는 `Final Review로 넘기기 전 확인 기준`으로 renamed / clarified됐고, 새 검증 단계가 아니라 Flow 3 결론의 기준 상세로 읽힌다.
- Gate threshold, replay 실행, provider 수집, registry / saved JSONL, Final Review persistence, live approval / broker order / auto rebalance 경계는 바꾸지 않았다.

## 2026-07-06 - Practical Validation Flow 1/2 Profile Placement

- Practical Validation Flow 1을 `후보 Source 확인`으로 좁히고, 검증 프로필은 Flow 2 `검증 기준 설정 / 실전 재검증 실행` 상단으로 이동했다.
- Flow 2는 `검증 기준 선택 -> 실전 재검증 실행` 순서로 읽히며, 세부 프로필 질문과 기준 카드는 접힌 상세로 낮췄다.
- Replay, provider 수집, gate threshold, registry / saved JSONL, Final Review persistence 경계는 변경하지 않았다.

## 2026-07-07 - Backtest Strategy Detail React V1

- `.aiworkspace/note/finance/tasks/active/backtest-strategy-detail-react-v1-20260707/`에서 Quality / Value strict Price Freshness Preflight blank iframe을 수정했다.
- Single Strategy 선택 직후 `app/services/backtest_strategy_detail.py` read model과 `app/web/components/backtest_strategy_detail_panel/` React panel로 strategy / variant 상세를 먼저 보여주는 시도는 후속 form cleanup에서 제거됐다.
- 실제 form input, backtest execution, registry / saved JSONL, Practical Validation gate policy는 변경하지 않았다.

## 2026-07-08 - Backtest Quarterly Productionization V1

- `.aiworkspace/note/finance/tasks/active/backtest-quarterly-productionization-v1-20260708/`에서 strict quarterly Quality / Value / Quality+Value의 1차~5차 정식화 작업을 완료했다.
- User-facing catalog / runner catalog / forms / compare / history / evidence inventory는 `Strict Quarterly`로 표시하며, legacy `_prototype` strategy key는 saved payload / old run replay 호환용으로 유지한다.
- Strict quarterly runtime wrappers는 annual-like investability, benchmark, promotion, underperformance/drawdown guardrail inputs를 받고, result bundle은 post-run `statement_shadow_coverage` metadata를 남긴다.
- Post-run Factor Readiness는 실제 실행 결과 기준으로 가격 / statement shadow 문제 ticker와 보강 action을 보여주며, 보강 성공 후에는 기존 결과를 stale로 보고 재실행을 요구한다.
- QA: py_compile, quarterly productionization tests, evidence/bridge tests, `tests.test_service_contracts` 529개 통과.

## 2026-07-07 - Backtest Strategy Form Cleanup V1

- `.aiworkspace/note/finance/tasks/active/backtest-strategy-form-cleanup-v1-20260707/`에서 1차~5차로 과한 Strategy Detail panel 제거, strict preset copy, strict factor form, ETF-like form, Portfolio Mix Builder 영향 확인을 완료했다.
- Backtest Analysis의 Strategy dropdown / Single Strategy form switching과 Portfolio Mix Builder strategy multiselect / variant controls는 Streamlit-owned 흐름으로 유지한다.
- React는 Price Freshness Preflight 같은 좁은 form-level component에만 남겼고, runtime / result bundle / registry / saved JSONL / Practical Validation gate policy는 변경하지 않았다.

## 2026-07-07 - Backtest Strict Coverage Refresh V1

- `.aiworkspace/note/finance/tasks/active/backtest-strict-coverage-refresh-v1-20260707/`에서 strict Quality / Value coverage 1차~5차를 완료했다.
- `US Statement Coverage N`은 표시상 `US Base Universe N`으로 정리했고, 실행 가능 coverage 보장값이 아니라 asset_profile 기반 후보군으로 문서화했다.
- Data Trust 가격 최신화는 stale/missing ticker 중심의 `Coverage 최신화`로 바뀌었고, Dynamic PIT는 더 넓은 backfill pool에서 target membership을 채우면 candidate-pool stale/missing을 non-blocking context로 보존한다.
- 20D 거래대금 기준은 Base Universe 선별이 아니라 Base Universe / Dynamic PIT membership 이후 적용되는 optional `liquidity_layer_v1`로 정리했다.

## 2026-07-07 - Practical Validation Flow4 Action Guide V2

- `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-action-guide-v2-20260707/`에서 Flow 4 criteria card를 해결 중심 구조로 바꿨다.
- `부족한 것 / 해야 할 일 / 보강 위치` 분리 대신 `해결해야 할 항목 / 해결 방법 / 통과 기준 / 위치`로 표시한다.
- Gate policy, replay execution, provider ingestion orchestration, registry / saved JSONL, live approval / order semantics는 변경하지 않았다.

## 2026-07-07 - Backtest PIT Universe Visible Contract Follow-up

- `.aiworkspace/note/finance/tasks/active/backtest-pit-universe-v1-20260707/` 후속으로 strict Quality / Value form의 사용자-facing `Universe Contract`를 `PIT Monthly Snapshot Universe` 하나로 정리했다.
- `Static Managed Research Universe`와 `Historical Dynamic PIT Universe`는 old saved payload / run replay 호환용 legacy internal path로만 유지한다.
- Single Strategy와 Portfolio Mix Builder의 strict form 입력값은 과거 Static 세션값을 PIT Monthly로 보정한다.
- 후속 오류 수정: PIT-only 실행 시 기존 로컬 DB에 `equity_universe_member`가 없어 MySQL 1146이 노출되던 문제를 loader readiness 처리로 낮췄다.
- 로컬 테스트 DB에는 100 / 300 / 500 / 1000 기본 coverage의 monthly PIT snapshot을 생성했다.

## 2026-07-07 - Backtest Factor Readiness Panel V1

- `.aiworkspace/note/finance/tasks/active/backtest-factor-readiness-panel-v1-20260707/`에서 1차~5차 개발을 완료했다.
- strict annual Quality / Value / Quality + Value setup은 Base Universe, Price Freshness, Statement Shadow를 하나의 React `Factor Readiness` panel로 읽는다.
- Single Strategy는 기본 시작일과 submit guard를 최대 5년으로 제한했고, Portfolio Mix Builder는 선택된 annual strict factor component에 대해서만 같은 window guard를 적용한다.
- Browser QA는 `http://localhost:8515/backtest`의 Single Strategy Quality Strict Annual 화면에서 빈 iframe 없이 panel 렌더링과 `2021/07/07` start default를 확인했다.

## 2026-07-07 - Backtest Post-Run Factor Readiness V1

- `.aiworkspace/note/finance/tasks/active/backtest-post-run-factor-readiness-v1-20260707/`에서 pre-run 후보군 검증을 post-run 실제 결과 기준 readiness로 전환했다.
- Single Strategy / Portfolio Mix Builder strict annual factor form은 `Preset -> Universe 기준 -> Run 이후 readiness preview -> form inputs` 순서로 읽힌다.
- 결과 화면은 strict factor bundle의 `price_freshness`, `History Excluded Ticker`, `Liquidity Excluded Ticker`로 문제 / 티커 / 해결 방법을 구성하고, 가격 refresh는 실제 refresh 가능한 티커만 대상으로 제한한다.
- QA: py_compile, `tests.test_service_contracts` 529개, Browser QA(`http://localhost:8524/backtest`) 완료. Screenshot artifact는 `backtest-post-run-factor-readiness-v1-qa.png`로 남겼고 커밋 대상은 아니다.

## 2026-07-08 - Strict Quarterly Productionization V1

- `.aiworkspace/note/finance/tasks/active/backtest-quarterly-productionization-v1-20260708/`에서 strict quarterly Quality / Value / Quality+Value의 1차~5차 정식화 작업을 완료했다.
- Quarterly result bundle은 post-run Factor Readiness가 가격 / statement shadow gap을 실제 실행 결과 기준으로 보여주고, 필요한 경우 targeted refresh action을 제공한다.
- User-facing label은 `Strict Quarterly`로 승격했고 legacy `_prototype` key는 saved replay 호환용으로 유지한다.
- Browser QA 후 `Research-only defaults` residual copy 제거와 quarterly 5-year window guard 보정을 추가했다.

## 2026-07-08 - Backtest Symbol Resolver V1

- `.aiworkspace/note/finance/tasks/active/backtest-symbol-resolver-v1-20260708/`에서 Backtest Quality / Value Factor Readiness용 ticker-change repair 1차~5차를 완료했다.
- `nyse_symbol_lifecycle(event_type=ticker_change)` 기반 후보 / active repair 저장 path를 추가했고, source evidence factor / confidence / LOW 수동 확인 계약을 붙였다.
- Price refresh는 source ticker를 유지하되 active repair가 있으면 collection ticker만 resolved symbol로 바꾸며, plan/details에 metadata-only `source_range` / `resolved_range` / `split_status`를 남긴다.
- Factor Readiness는 후보쌍 / 신뢰도 / 기간 경계 / 다음 행동을 보여주고, repair 후 readiness 재확인과 백테스트 재실행을 안내한다.
- 후속 범위: official corporate-action feed 신규 수집과 실제 old/new ticker price series stitching.

## 2026-07-09 - Institutional Portfolios Live SEC 13F V1

- `.aiworkspace/note/finance/tasks/active/institutional-portfolios-live-sec13f-v1-20260709/`에서 1차~6차 개발 / QA / docs closeout을 완료했다.
- SEC 13F ingestion은 refresh status row와 conservative CUSIP-symbol enrichment를 기록하고, Institutional Portfolios는 watchlist rail / freshness payload / secondary refresh panel을 갖게 됐다.
- QA: focused tests 12개, py_compile, npm build, git diff --check, UI/engine boundary check, Browser QA screenshot 완료. Full official SEC ZIP load는 사용자가 명시 실행할 수 있는 후속 운영 action으로 남겼다.

## 2026-07-10 KST - Institutional Portfolios Selection Loading V1

- `.aiworkspace/note/finance/tasks/active/institutional-portfolios-selection-loading-v1-20260709/`에서 manager rail 클릭 후 반복 로딩처럼 보이던 선택 전환 문제를 진단하고 수정했다.
- 원인은 watchlist 선택 CIK가 search result에 없을 때 첫 DB row로 fallback되고, custom component의 이전 event가 재처리될 수 있던 흐름이었다.
- Watchlist-aware selected manager resolver, event nonce 소비, reverse lookup lazy cache, 한글 loading banner, Runtime / Build 제거를 적용했다.
- QA: focused tests 18개, py_compile, npm build, git diff --check, Browser 반복 클릭 QA 완료. 후속 범위는 SEC full ZIP 운영 refresh와 CUSIP-symbol map 품질 개선이다.

## 2026-07-11 KST - Institutional Portfolios UX Detail / Performance V1

- `.aiworkspace/note/finance/tasks/active/institutional-portfolios-ux-detail-performance-v1-20260711/`에서 selected-security detail, report-period performance, institution-count ranking, scroll/pending fallback을 구현했다.
- 13F raw holdings는 service read model에서 CUSIP / put-call 기준으로 합산해 도넛 / holdings / change board / performance 중복 표시를 줄였다.
- Ranking loader는 `ix_report_period_cusip_cik` 접근을 사용하고, React는 pending timeout fallback으로 클릭 후 무한 로딩처럼 보이지 않게 했다.
- QA: focused tests 24개, py_compile, npm build, git diff --check, UI/engine boundary scan, Browser QA screenshot 완료.

## 2026-07-12 KST - Institutional Portfolios Holding Chart Refresh V1

- `.aiworkspace/note/finance/tasks/active/institutional-portfolios-holding-chart-refresh-v1-20260712/`에서 보유기관조회 차트 empty 원인을 실제 DB 기준으로 진단했다.
- Berkshire 상위 13F holdings는 ticker가 비어 있었지만 가격 DB에는 KO/BAC/CVX/OXY/GOOGL 등 row가 이미 있어, service-level safe CUSIP resolver로 차트를 연결했다.
- `KO` 같은 curated symbol reverse lookup은 오염된 generic map보다 curated CUSIP를 먼저 사용하며, 차트가 비면 React 버튼이 Python `run_collect_ohlcv` 수집 job을 실행한다.

## 2026-07-12 KST - Institutional Portfolios Watchlist / Mapping V1

- `.aiworkspace/note/finance/tasks/active/institutional-portfolios-watchlist-mapping-v1-20260712/`에서 대가 watchlist / alias 검색과 가격 차트 empty 사유 분리를 구현했다.
- Duquesne / Stanley Druckenmiller 등 확장 seed와 DB-backed `institutional_13f_manager_watchlist` loader 경계를 추가했고, alias 검색 CIK를 우선 정렬한다.
- Ambiguous CUSIP-symbol mapping은 차트용 symbol로 쓰지 않으며, selected-security price action은 symbol missing / ambiguous mapping / price missing / ready 상태로 나뉜다.

## 2026-07-09 - Market Movers Analyst Interest Multi-Source V1

- `.aiworkspace/note/finance/tasks/active/overview-market-interest-analyst-multisource-20260709/`에서 Market Movers 선택 종목의 `애널리스트 관심`을 link-only에서 yfinance 구조화 세션 단서로 보강했다.
- `시장 관심 근거 확인`은 선택 종목 1개에 대해 news / Korean news / SEC metadata / yfinance analyst metadata를 세션 전용으로 조회한다.
- 화면은 최근 애널리스트 액션, 목표가 요약, 의견 분포, Nasdaq / WSJ / MarketWatch / Yahoo 원문 교차확인 링크를 보여준다.
- Nasdaq / WSJ / MarketWatch HTML scraping, DB 저장, 추천/점수화/매매 신호, paid API, broker 연결은 추가하지 않았다.

## 2026-07-11 - Overview Market Movers Visual Grouping V1

- `.aiworkspace/note/finance/tasks/active/overview-market-movers-visual-grouping-v1-20260711/`에서 Sector Breadth 색상 범위와 선택 종목 조사 그룹 통합을 완료했다.
- Sector Breadth는 3% outer surface와 lane별 direction tint를 사용하며, 조사 selector/panel/tabs/Snapshot/chart는 keyed 부모 container 하나로 읽힌다.
- 후속으로 Ranking Board의 모드별 전체 표 expander를 Ranking Board keyed 부모 안으로 이동해 Sector Breadth와 선택 종목 조사 사이의 독립 박스를 제거했다.
- Market Movers 81 tests, React build, desktop/mobile Browser QA를 통과했고 데이터/payload/provider/DB 경계는 변경하지 않았다.

## 2026-07-12 - Overview Market Context S&P 500 Valuation V1

- 기존 Market Context visible cockpit/brief/sector/event/refresh composition을 제거하고 5년 후행 PER 구간과 FOMC 예상 EPS/SPX 시나리오 React 화면으로 교체했다.
- Shiller 월별 valuation, S&P index earnings release vintage, Federal Reserve SEP vintage 3-table pipeline과 loader/service/read-model 경계를 추가했다.
- SEP 최신 링크를 매일 확인하는 automation과 optional EPS table bootstrap을 추가했고, 실제 수집·TypeScript/Vite·18 valuation tests·31 Market Context contracts·Browser QA를 완료했다.
- V1 당시에는 S&P actual earnings workbook이 없으면 예상 지수 시나리오를 차단했다. 이 제약은 아래 V1.1 fallback 구현으로 대체됐으며 generated QA screenshot은 커밋하지 않는다.

## 2026-07-12 - Overview Market Context S&P 500 Valuation V1.1

- 그래프 1을 official EPS/SPX readiness에서 분리하고 최신 Shiller 월별 PER를 current marker로 사용했다.
- 그래프 2는 official actual 4분기를 우선하고 없으면 최신 Robert Shiller TTM EPS를 source/quality/basis/fallback evidence와 함께 사용한다.
- SEP median GDP+PCE 예상 EPS와 동일 EPS × 5년 PER band, 현재 SPX 괴리율을 React에 연결했다.
- 상세 실행과 QA는 `.aiworkspace/note/finance/tasks/active/overview-market-context-sp500-valuation-v1-20260712/`를 본다.

## 2026-07-12 - Overview Market Context S&P 500 Valuation V1.2

- 2025-06 이후 missing SEP official vintage를 backfill하고 Shiller EPS 미발표 최신 월의 price-only row를 보존했다.
- Graph 1은 대칭 `-2σ/-1σ/center/+1σ/+2σ`와 hover inspector로 개선했다.
- Graph 2는 다음 달 SEP activation과 observation-year target을 적용한 12개월 actual-vs-reconstructed SPX band를 추가했다.
- 테스트, 실제 DB smoke, desktop/420px Browser QA 근거는 active task `RUNS.md`를 본다.

## 2026-07-12 - Overview Market Context S&P 500 Valuation V1.3

- Graph 1의 60개월 분포는 2026-03 완결 PER까지만 유지하고, EPS 미발표 2026-04~07은 March EPS를 유지한 잠정 PER 점선으로 연장했다.
- current SPX EOD와 price/EPS basis date, latest complete PER를 service contract에 추가하고 React hover inspector를 선택 점 옆으로 이동·경계 반전·상단 clamp했다.
- 33 valuation tests, 34 Market Context contracts, DB smoke, desktop/420px Browser QA를 완료했으며 generated V1.3 screenshot은 커밋하지 않는다.
- Graph 2의 1/3/5년 선택은 older SEP vintage backfill과 Shiller EPS PIT 경계를 함께 다루는 후속 차수로 남긴다.

## 2026-07-12 - Overview Market Context S&P 500 Valuation V1.4

- Federal Reserve calendar에서 공식 SEP 21개 vintage(2021-03~2026-06)를 발견해 missing 16개 release 326 rows를 idempotent backfill했다.
- Graph 2 service는 120개월 Shiller warmup으로 12/36/60-point history options를 만들고 React는 `1년 / 3년 / 5년` selector로 전환한다.
- 37 valuation tests, 35 Market Context contracts, DB smoke, desktop/420px Browser QA를 완료했고 V1.4 screenshot은 커밋하지 않는다.
- Shiller EPS release-vintage 한계와 `과거 시점 재구성` 경계는 모든 기간에 유지한다.

## 2026-07-08 - Practical Validation Flow Gating / Evidence IA V1

- `.aiworkspace/note/finance/tasks/active/practical-validation-flow-gating-evidence-ia-v1-20260708/`에서 1차~4차 Practical Validation flow 정리를 완료했다.
- Flow 2에서 현재 세션 `전략 재검증 실행` 전에는 Flow 3 / Flow 4 / Flow 5와 결과 JSON을 렌더링하지 않는다.
- Flow 4는 `카테고리별 검증 결과 -> 단계별 검증 소유권 -> Provider / Data 보강 액션 -> 접힌 근거 부록` 순서로 읽고, 수집 가능한 provider / holdings / exposure / macro gap에만 `수집하기` CTA를 노출한다.
- Provider 부족근거 copy는 `수집 대상 근거`로 낮췄고, 상세 evidence tabs는 기본 접힌 `근거 부록`으로 이동했다.
- 2026-07-09 Flow5 CTA Integration V1에서 이 visible Flow5 / evidence IA는 Flow3 CTA와 Flow4 `상세 근거 / 원자료` 구조로 대체됐다.

## 2026-07-09 - Practical Validation Flow5 CTA Integration V1

- `.aiworkspace/note/finance/tasks/active/practical-validation-flow5-cta-integration-v1-20260709/`에서 Flow5 visible container를 Flow3 `검증 결론 / 다음 행동` CTA로 통합했다.
- Flow3 React는 `검증 결과 저장(기록용)`과 `저장하고 Final Review로 이동` intent만 보내고, Python page/service가 audit append, Final Review handoff, session state, rerun을 처리한다.
- Selection Source JSON / Practical Validation Result JSON은 Flow4 `상세 근거 / 원자료` Raw Evidence로 낮췄다.
- Gate threshold, provider/FRED/API/DB fetch path, Final Review selected-route policy, registry / saved rewrite, live approval / broker order 의미는 변경하지 않았다.
- Follow-up review: Flow3 노란불 통과 상태를 `주의 포함 이동 가능`으로 표시하고, stale Flow5 copy / unused gate module board helpers / `Required for Final Review` display group 잔여물을 정리했다.

## 2026-07-09 - Final Review Detailed Scorecard V1-V6

- `.aiworkspace/note/finance/tasks/active/final-review-detailed-scorecard-v1-v6-20260709/`에서 1차~6차 개발 / QA / commit 흐름을 완료했다.
- Final Review scorecard는 5개 dimension, Level2 REVIEW role별 score impact, hard blocker / selected-route not-ready / gate review-required / excessive open review score cap을 만든다.
- React investment report는 Python read model의 `세부 점수`, `Level2 REVIEW 점수 영향`, `최종 선택 사유`, `판단 저장 전 메모`를 표시만 하며 provider fetch / DB write / registry write / gate 계산을 소유하지 않는다.
- QA: focused service / React contract 47개, npm build, py_compile, Browser QA iframe label 확인 완료. Browser screenshot artifacts는 generated 파일로 남기고 stage하지 않았다.

## 2026-07-10 - Final Review Investment Report IA V1

- `.aiworkspace/note/finance/tasks/active/final-review-investment-report-ia-v1-20260710/`에서 1차~4차 투자 검토서 IA 개선을 완료했다.
- Python read model은 `decision_summary`, high-score dimension 강점, compact `watch_items`, 실제 해석 카드 payload를 만들고 React는 이를 `선택 판단 요약`, `강점`, `확인 지점`, `해석`으로 렌더링한다.
- old first-read `다음 행동` / `판단 저장 전 메모` 반복 block은 제거했고, score / gate / save / Monitoring handoff / provider / registry 경계는 변경하지 않았다.
- QA: focused service / React contract 51개, py_compile, npm build, diff check, Browser QA 완료. Screenshot과 run history는 generated artifact로 stage하지 않는다.

## 2026-07-10 - Final Review Investment Report Flat UI V1

- `.aiworkspace/note/finance/tasks/active/final-review-investment-report-flat-ui-v1-20260710/`에서 1차~4차 투자 검토서 평면화 작업을 완료했다.
- React first-read는 meta strip, `왜 후보인가` / `무엇을 확인해야 하나`, 강점 / 확인 지점 rows, 해석 rows로 정리했고, 상세 scorecard / Level2 / handoff / 개선안 / Monitoring 조건은 disclosure로 낮췄다.
- Python score / gate / route / save / Monitoring handoff / provider / registry 경계는 변경하지 않았다.
- QA: RED/GREEN source contract, focused service / React contract 51개, py_compile, npm build, diff check, Browser QA 완료. Screenshot과 run history는 generated artifact로 stage하지 않는다.

## 2026-07-11 - Final Review Investment Report Detail Tabs V1

- `.aiworkspace/note/finance/tasks/active/final-review-investment-report-detail-tabs-v1-20260711/`에서 1차~4차 하단 상세 탭 전환 작업을 완료했다.
- React lower detail 영역은 expander 5개 대신 `근거 상세`, `저장 경계`, `개선 후보`, `Review 처리`, `Monitoring` 탭과 단일 panel로 렌더링한다.
- Python score / gate / route / save / Monitoring handoff / provider / registry 경계는 변경하지 않았다.
- QA: RED/GREEN source contract, focused service / React contract 51개, py_compile, npm build, diff check, Browser QA tab click 완료. Screenshot과 run history는 generated artifact로 stage하지 않는다.

## 2026-07-11 - Final Review Decision Surface Consolidation V1

- `.aiworkspace/note/finance/tasks/active/final-review-decision-surface-consolidation-v1-20260711/`에서 하단 근거 탭, REVIEW trace, 다음 실험, 최종 판단 흐름 1차~4차를 완료했다.
- 연결된 세 탭 shell, 한국어 세부 점수, stored audit trace와 정성 판단 구분, 상위 3개 counterfactual 가설을 적용했다.
- standalone Decision Cockpit / 반복 Save Readiness / disabled order action을 제거하고 Python-owned 통합 `판단 기록`으로 정리했다.
- service 53개 / page 8개 test, React build, py_compile, diff check, Browser QA를 통과했으며 generated screenshot과 run history는 stage하지 않는다.

## 2026-07-12 - Final Review Evidence Closure Contract V1

- `.aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/`의 계획과 1차~4차 구현 / QA를 완료했다.
- root issue dedup, Level2 actionability Gate, GRS signal/valuation 분리, static/dynamic survivorship policy, Final Review terminal snapshot, measured-only score를 적용했다.
- 구현 커밋: `697a119b`, `65eacc92`, `cb2af299`, `4a05ae2f`; closeout 상세는 active task `STATUS.md`와 `RUNS.md`를 본다.
- 후속은 dynamic historical universe용 PIT membership / delisting provider 승인 여부다.

## 2026-07-12 - Practical Validation Closure Summary UX Correction

- Flow 4의 중복 `근거 종결 경로`와 `미정` closure card를 제거했다.
- Flow 3 기존 검증 결론에 Python root-dedup accepted-limit count와 즉시 해결·개발 blocker 유무를 compact하게 통합했다.
- 내부 closure / Gate / save / Final Review 계약은 유지했으며 구현 커밋은 `b5e1cd68`이다.
- focused 45 tests, Vite build, py_compile, 760px current GRS Browser QA를 통과했다.

## 2026-07-12 - Nasdaq-100 무계정 공개 데이터 경로 조사

- SEC에서 QQQ 분기 N-PORT 22건(2020-12-31~2026-03-31)을 인증 없이 backfill할 수 있음을 확인했다.
- no-account V1 권고를 `QQQ N-PORT + SEC actual + QQQ EOD` 공개 공시 기반 재구성으로 변경했다.
- 공식 Nasdaq P/E가 아니라 `Nasdaq-100 (QQQ proxy)`로 표시하며, ADR/복수 클래스/foreign issuer mapping과 공개 P/E calibration을 구현 전 quality gate로 둔다.
- 상세 근거와 구현 후보는 `.aiworkspace/note/finance/researches/active/2026-07-nasdaq100-index-eps-source/`를 본다.
## 2026-07-13 - Nasdaq-100 QQQ Public-Filing Valuation V1

- `.aiworkspace/note/finance/tasks/active/overview-market-context-nasdaq100-valuation-v1-20260712/`의 1차~5차 pipeline/service/React/automation/QA를 완료했다.
- 실제 job은 SEC holdings 3,060행을 정규화해 3,049 unique key를 저장했고, QQQ EOD 20행과 monthly proxy 119행을 처리했다. Monthly quality는 READY 5 / BLOCKED 114다.
- Market Context는 S&P 500 / Nasdaq-100 selector를 제공하며 Nasdaq은 최신 coverage 94.47%가 95% 기준 미달이라 값을 숨기고 blocker evidence를 표시한다.
- 구현 커밋은 `50fe4059`, `10a973f4`, `287d359f`, `6ed08d0e`; 5차 closeout은 task `STATUS.md`와 `RUNS.md`를 본다.

## 2026-07-14 - Nasdaq-100 무료 direct aggregate 원천 재검증

- GuruFocus 가격표의 동적 contract를 확인해 Economic Data가 무료 core가 아니라 `+$90/month` add-on 또는 PAYG임을 확정했다.
- 무료 대체 원천을 다시 비교했지만 60개월 direct Nasdaq-100 P/E/EPS와 자동 수집·내부 저장 권리를 함께 충족한 외부 source는 찾지 못했다.
- 무료 production 경로는 기존 `QQQ N-PORT + SEC actual` 자체 재구성뿐이며, 상세 근거는 `researches/active/2026-07-nasdaq100-index-eps-source/`를 본다.

## 2026-07-14 - MacroMicro Nasdaq-100 Forward P/E 수집 조건 검증

- 월별 series `23955`는 공개되지만 forward P/E이며 현재 QQQ actual trailing P/E graph의 결측 대체 원천이 아니다.
- 로그아웃 화면과 공식 Help를 확인해 Free/Prime/Max raw CSV 및 무계정 API 경로가 없고, CSV/API는 Business/API Essential/Custom 범위임을 확인했다.
- exact-series entitlement와 DB retention/파생 차트 권한은 공개 정보만으로 확정되지 않아 유료 검토 시 서면 확인이 필요하다.
- 현재 무료 V1에는 MacroMicro collector를 추가하지 않으며, 도입 시 별도 forward-valuation track으로만 검토한다.

## 2026-07-14 - Nasdaq-100 대안 원천 구현 가능성 재검증

- 현재 DB는 119개월 중 READY 66 / BLOCKED 53이며, 계산기 FY-to-Q4 오류 수정으로 최소 69개월까지 우선 복구 가능함을 확인했다.
- Tiingo 무료 EOD catalog가 historical price gap 23개 중 22개 exact symbol과 `SYMC -> GEN` successor 후보를 제공하며, SEC/N-PORT가 EPS와 price anchor를 제공한다.
- 미국 상장 누락분만 복구한 upper-bound에서도 119/119개월이 95%를 넘고 최저 96.319%여서 기능은 구현 가능 판정이다.
- 권장 순서는 계산 정확도 -> SEC identity/actual -> optional Tiingo EOD -> 119개월 calibration -> QA이며 상세는 research bundle을 본다.

## 2026-07-14 - 미국 개별주식 가치평가 V1 설계

- Nasdaq-100 user-facing selector를 searchable 미국 개별주식 상대가치 화면으로 교체하는 방향을 승인했다.
- 월말 가격 + filing-aware quarterly TTM EPS carry-forward로 monthly P/E를 만들고, Graph 2는 FOMC macro + 기업 초과 EPS 성장률을 사용한다.
- 상세 설계와 1차~5차 roadmap은 `.aiworkspace/note/finance/tasks/active/overview-market-context-us-stock-valuation-v1-20260714/`에 고정했다.
- 현재는 written spec review 단계이며 구현 코드는 변경하지 않았다.

## 2026-07-14 - 미국 개별주식 가치평가 V1 구현 완료

- Market Context selector를 `S&P 500 | 미국 개별주식`으로 교체하고 DB-only 검색, filing-aware monthly TTM EPS/PER, 60m/36m multiple, FOMC+기업 초과성장 상대가치 시나리오를 연결했다.
- comparative FY false-Q4와 split-unit drift를 real-like TDD fixture로 먼저 수정했고, raw gap만 explicit synchronous collection을 허용한다.
- AAPL/NVDA/META/TSLA actual READY와 loss/short-listing/SEC-gap/split/foreign issuer 경계를 검증했으며 S&P와 retained Nasdaq backend는 보존했다.
- 상세 구현·QA·남은 full-suite unrelated failures는 `tasks/active/overview-market-context-us-stock-valuation-v1-20260714/STATUS.md`와 `RUNS.md`를 본다.

## 2026-07-15 - 미국 개별주식 가치평가 정확성 후속 완료

- comparative Q/FY fact를 primary filing period로 제한하고, split-year Q/FY를 동일한 월말 share basis로 정규화한 뒤 Q4를 파생하도록 real-like TDD로 수정했다.
- Graph 1의 positive-P/E readiness와 Graph 2의 최소 8개 growth 관측 readiness를 분리해, 성장 이력 부족이 계산 가능한 P/E 화면을 숨기지 않게 했다.
- AMD actual은 TTM EPS `3.05`, P/E `169.22x`, growth `10/8`로 READY이며 AAPL/MSFT/NVDA/META/TSLA, LCID, RDDT/RIVN, S&P 화면을 함께 회귀 검증했다.
- focused 125개 통과, isolated full 1,030/1,034 통과(기존 unrelated 4건), desktop/420px Browser QA와 no-overflow/zero-console-error 확인을 완료했다. 상세는 active task `RUNS.md`를 본다.

## 2026-07-15 - 미국 개별주식 PER 부분 이력 표시 완료

- 1/3/5년 이력에 full-month `timeline`과 `PARTIAL` 상태를 추가해 계산 가능한 월을 원래 위치에 표시하고 결측 월의 선·band를 끊었다.
- Actual AAPL은 3년 `36/36`, 5년 `42/60`; AMD는 3년 `33/36`, 5년 `39/60`이며 누락 원인을 화면에서 구분한다.
- focused 129개 통과, isolated full 1,033/1,037 통과(기존 unrelated 4건), S&P 회귀와 desktop/420px Browser QA를 완료했다.
- 현재 PER 화면 후속은 완료했다. 다음 선택 범위는 historical SEP/PIT backfill 또는 적자기업 전용 비-P/E 분석 화면이다.

## 2026-07-15 - 미국 개별주식 전환 분석 V1 설계

- 미국 개별주식 내부의 `PER 상대가치 | 전환 분석` selector와 selected-company V1 범위를 승인 방향으로 고정했다.
- cumulative SEC duration fact의 filing-aware discrete-quarter resolver, operating milestone/risk overlay 분리, EV freshness gate를 authoritative design에 기록했다.
- actual DB에서 RIVN/PLTR 16~19분기, LCID core flow 15~18분기 evidence를 read-only 확인했고 GrossProfit tag gap을 same-quarter revenue-cost fallback 대상으로 분리했다.
- 상세는 `tasks/active/overview-market-context-us-stock-turnaround-analysis-v1-20260715/DESIGN.md`를 본다. 현재 0/5차이며 written spec review 후 TDD plan으로 이어진다.

## 2026-07-15 - 미국 개별주식 전환 분석 V1 구현 완료

- `PER 상대가치 | 전환 분석` 내부 selector와 filing-aware discrete-quarter 영업·현금 chart, independent milestone/risk, fresh-input valuation readiness를 1차~5차로 구현했다.
- Actual DB에서 RIVN/LCID/PLTR는 전환 분석, AMD/AAPL은 기존 PER를 추천했고 기존 S&P/PER payload를 보존했다.
- focused 96개 통과, isolated full 1,073/1,077 통과(기존 unrelated 4건), desktop/420px Browser QA와 overflow 0 / console error 0을 확인했다.
- 상세 구현·actual matrix·남은 CIK/latency 경계는 `tasks/active/overview-market-context-us-stock-turnaround-analysis-v1-20260715/STATUS.md`, `RUNS.md`, `RISKS.md`를 본다.

## 2026-07-15 - 미국 개별주식 최신 데이터 재계산 V1 설계

- PER와 전환 분석 공통 상단에 `최신 데이터로 다시 계산` action 하나를 두는 방향을 승인 범위로 고정했다.
- 가격은 마지막 완료 NYSE session, 시장가치는 profile/가격 7일 정렬, 재무는 실제 raw coverage gap만 최신성 판단에 사용한다.
- Cloudflare처럼 CIK가 없어도 profile/price는 갱신하고 SEC statement만 별도 잔여 gap으로 남기는 partial-success 경계를 설계했다.
- 상세는 `tasks/active/overview-market-context-us-stock-freshness-refresh-v1-20260715/DESIGN.md`, `PLAN.md`를 본다. Cached UI 우선 + 자동 freshness 판정 + 명시적 CTA를 승인했고 현재 0/3차 detailed TDD plan complete다.

## 2026-07-15 - 미국 개별주식 최신 데이터 재계산 V1 완료

- 공용 NYSE 완료-session freshness, CIK-independent profile/price와 SEC-only identity gate, unified `refresh_us_stock_data` event를 1차~2차로 구현했다.
- Header와 PER/전환 selector 사이에 stale일 때만 CTA 하나를 표시하고 가격·재무·공개 기준일을 분리했다. 자동 provider 수집과 run/job/row 진단 panel은 추가하지 않았다.
- Actual NET는 explicit action 뒤 price `2026-07-14`, profile `2026-07-15`, statement `2026-03-31`/available `2026-05-08`로 READY가 됐고 AAPL stale desktop/420px Browser QA에서 CTA 중복·overflow·console error가 모두 0이었다.
- Focused 114개와 React build가 통과했다. 전체 discovery의 기존 unrelated assertion 4건과 Streamlit reimport isolation error 154건은 task `RUNS.md`에 구분해 기록했다.

## 2026-07-16 - 전환단계 AAPL 의미 보정 설계

- AAPL PER는 READY/TTM EPS `7.90`인데 turnaround EPS가 null인 원인을 `USD per share` unit allowlist 누락으로 확정했다.
- 영업손실 축소/EPS 양전 미확인이 적자 의미로 보이는 문제를 transition과 already-positive 상태 혼동으로 분리했다.
- 6요소 rail과 threshold는 유지하고 EPS unit, 사용자 문구, UI-local established state를 1차~3차로 보정하는 written spec을 active task에 기록했다.

## 2026-07-16 - 전환분석 공시 기반 분기 산출·표시 완료

- MRNA의 revenue concept rename으로 비어 있던 2023-Q4를 explicit family의 확정 FY/Q1/Q2/Q3로 안전하게 산출해 TTM 선을 복구했다.
- Per-metric/TTM provenance와 `공시 기반 산출` marker·badge·산식을 React inspector에 추가했고 보간·forecast는 만들지 않았다.
- Focused 112/112, isolated repository 1,103/1,107(기존 unrelated 4건), actual DB 및 desktop/420px Browser QA를 완료했다.
- 상세 evidence와 후속 경계는 `tasks/active/overview-market-context-turnaround-derived-quarter-provenance-v1-20260716/`를 본다.

## 2026-07-16 - sub-dev master 통합 충돌 해결

- Finance 문서 충돌 9개를 문서 역할과 시간순으로 통합해 Overview / Market Context와 Institutional Portfolios 양쪽 완료 이력을 보존했다.
- current active task는 `none`, latest completed task는 `overview-market-context-turnaround-derived-quarter-provenance-v1-20260716`으로 Index / Roadmap / task manifest / root pointer를 정렬했다.
- SEC 13F collector와 selected-stock freshness / turnaround data flow 설명을 함께 유지하고 중복된 짧은 경로 설명은 제거했다.
- 기관 포트폴리오 39 tests, py_compile, React production build, Browser QA는 통과했다. Backtest/service contract 823개 중 822개가 통과했고 남은 Sentiment 1건은 병합 전 HEAD에도 존재하는 unrelated source-contract drift다.
- 미추적 `2026-07-market-interest-free-source-benchmark/` 리서치와 QA screenshot은 병합 범위 밖 generated/local artifact로 두고 stage하지 않았다.

## 2026-07-16 - Market Context 미국 경제 사이클 V1 완료

- 사용자의 회복·확장·둔화·침체 프레임을 17-series FRED/ALFRED vintage, strict as-of, h0/h1/h2 rolling-origin publication gate, compact DB snapshot으로 확장했다.
- `경제 사이클 | S&P 500 | 미국 개별주식` same-level selector와 별도 React workbench를 연결하고 desktop/420px Browser QA를 완료했다.
- 후속 actual bootstrap으로 17-series `1,232,856`행과 121개월 replay를 적재했다. h0/h1/h2는 각각 coverage/calibration/origin/baseline gate 미통과로 `LIMITED`이며 숫자를 표시하지 않는다.
- 전체 roadmap `5/5` 완료. 향후 숫자 publication은 더 많은 forecast-safe 증거를 확보해 horizon별 gate를 통과할 때만 가능하다.

## 2026-07-17 - 경제사이클 금·달러 다중 경로 파일럿 완료

- 전체 5차 중 1차 공통 시계열 판정기와 2차 금·달러 파일럿을 완료하고, 단정적 우호/부담·일치/불일치 계약을 `economic_cycle_v2` 다중 경로로 교체했다.
- FRED 5개 경로 시계열 6,698행을 저장했다. Actual은 금 `SUFFICIENT`, 달러 `PARTIAL`이며 가격 원인·확률·매매 결론은 만들지 않는다.
- Focused 48 tests, compile, React build, actual smoke, desktop/420px Browser QA를 통과했다. 상세는 `tasks/active/overview-economic-cycle-multichannel-asset-interpretation-v1-20260717/`를 본다.
- 3차 채권·금리, 4차 주식, 5차 원자재는 자체 데이터 경로를 별도 승인한 뒤 이어간다.

## 2026-07-17 - 경제사이클 자산 경로 3·4·5차 완료

- 채권·금리는 2년·10년·10년-2년 구조와 실질금리·기대인플레이션, 주식은 `^GSPC`와 실질금리·신용·VIX·actual EPS, 원자재는 WTI·EIA 수급·구리·달러·미국 활동·금을 연결했다.
- T10YIE·EIA 3계열 `8,049` rows, S&P 가격 `5,026` rows, futures 4종 `10,055` rows를 actual DB에 적재했다. 실제 S&P EPS 완료 분기는 없어 해당 경로만 자료 부족으로 유지했다.
- 공통 관측 UI, desktop 2열/mobile 1열, hover/focus 상세와 채권 내부 1열 지표 목록을 확인했다. Focused `104 passed`, TypeScript와 React production build를 통과했다.
- 전체 자산경로 roadmap은 `5/5` 완료다. 해외 상대금리와 승인된 글로벌 구리 활동지표는 후속 범위다.

## 2026-07-18 - S&P 500 실제 EPS 등록 경로 구현

- Workspace Ingestion에 공식 Index Earnings XLSX와 발표일을 등록하는 사용자 흐름을 추가했다.
- 공식 `QUARTERLY DATA` 다단 머리글과 normalized 호환 형식을 검증하고, actual As-Reported release vintage를 transaction으로 저장한다.
- S&P 가치평가는 actual 4분기 current TTM, Economic Cycle은 actual 8분기 current/prior TTM YoY를 사용하며 모든 as-of read에 발표 vintage 기준을 적용했다.
- 현재 공식 최신 파일을 직접 받지 못해 DB 실제 적재는 남아 있다. 상세는 `tasks/active/overview-economic-cycle-sp500-actual-eps-registration-v1-20260718/`를 본다.
