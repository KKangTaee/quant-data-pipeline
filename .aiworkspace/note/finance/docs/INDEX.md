# Finance Documentation Index

Status: Active
Last Verified: 2026-07-19

## Purpose

이 폴더는 `finance` 프로젝트의 장기 지식만 보관한다.

작업 중 임시 분석, 실행 로그, 진행 상태는 `docs/`에 바로 넣지 않는다.
진행 중 기록은 `.aiworkspace/note/finance/tasks/active/<task>/`, `.aiworkspace/note/finance/phases/active/<phase>/`, 또는 제품 방향 리서치의 경우 `.aiworkspace/note/finance/researches/active/<research-id>/`에 두고,
반복적으로 필요한 내용만 이 폴더로 승격한다.

## Read First

1. [Product Direction](./PRODUCT_DIRECTION.md)
2. [Roadmap](./ROADMAP.md)
3. [Project Map](./PROJECT_MAP.md)
4. [Glossary](./GLOSSARY.md)

## Current Phase State

- Latest completed phase: [Phase 13 First-Cycle Hardening Closeout](../phases/done/phase13-hardening-cycle-closeout.md)
- Previous completed phase: [Phase 12 Selected Monitoring / Recheck Operations](../phases/done/phase12-selected-monitoring-recheck-operations.md)
- Current active phase: none. New phase work should be opened only after a user-approved scope is selected from current research / carry-forward material.
- Current active task: [Backtest Analysis Level1 Decision Workspace V1 2026-07-17](../tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717/STATUS.md). 1~15차 Level1 one-shell 개선을 완료했다. Portfolio Mix는 four-step React shell과 Python-owned 실행·저장·Level2 인계 계약으로 전환됐고, 후속 범위는 task `RISKS.md`의 compatibility/accessibility 항목만 남는다.
- Latest completed task: [Futures Macro Pattern Outlook V1 2026-07-18](../tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/STATUS.md) — 전체 roadmap과 materialized snapshot / React disclosure closeout을 완료했다. 일봉 갱신이 5년 compact snapshot을 저장하고 Overview 첫 진입은 DB-only로 읽는다.
- Recent completed Institutional Portfolios task: [Institutional 13F OpenFIGI Mapping V1 2026-07-18](../tasks/active/institutional-13f-openfigi-mapping-v1-20260718/STATUS.md) — 전체 roadmap `4/4`. 무료 OpenFIGI v3 current resolution, error-preserving UPSERT, safe loader precedence, curated 12-manager backfill과 actual Browser QA를 완료했다.
- Recent completed Overview / Market Context task: [S&P 500 Actual EPS Registration V1 2026-07-18](../tasks/active/overview-economic-cycle-sp500-actual-eps-registration-v1-20260718/STATUS.md) — 공식 workbook 등록 제품 경로와 PIT loader 검증은 완료했고, 현재 공식 workbook과 발표일 입력은 외부 입력으로 남아 있다.
- Previous completed task: [Economic Cycle Asset Pathways Stages 3-5 V1 2026-07-17](../tasks/active/overview-economic-cycle-asset-pathways-stages3-5-v1-20260717/STATUS.md) — 전체 자산경로 roadmap `5/5`를 완료했다. 채권·금리 구조, S&P 500 단일 대표지수, WTI·구리·금의 daily/weekly/quarterly 측정 경로를 DB-only로 연결하고 공통 관측 UI와 actual desktop/mobile QA를 닫았다.
- Previous completed task: [Economic Cycle Multichannel Asset Interpretation V1 2026-07-17](../tasks/active/overview-economic-cycle-multichannel-asset-interpretation-v1-20260717/STATUS.md) — 1차 공통 판정기와 2차 금·달러 파일럿에서 인과·가격예측·매매 결론을 만들지 않는 `economic_cycle_v2` 계약을 확립했다.
- Previous completed task: [Economic Cycle Asset Signal Copy V1 2026-07-17](../tasks/active/overview-economic-cycle-asset-signal-copy-v1-20260717/STATUS.md) — 자산마다 반복되던 경제 전체 국면을 제거하고 금·달러를 `미국 경기 신호 / 실제 가격 / 두 신호 관계`로 분리했다. 이 계약은 최신 다중 경로 task에서 대체됐다.
- Earlier completed task: [Economic Cycle Gold / Dollar Price Confirmation V1 2026-07-17](../tasks/active/overview-economic-cycle-gold-dollar-price-confirmation-v1-20260717/STATUS.md) — 금과 달러를 별도 카드로 분리하고 저장 일봉 가격 확인을 최초 연결했다. 배경 일치·불일치 계약은 최신 다중 경로 task에서 대체됐다.
- Previous completed task: [Economic Cycle Asset Context V1 2026-07-16](../tasks/active/overview-economic-cycle-asset-context-v1-20260716/STATUS.md) — 정적 `시장의 다음 질문`을 네 canonical factor 기반 `자산별 확인 포인트`로 교체했다. 채권·금리/주식/금·달러/원자재를 `우호·부담·혼재·자료 부족`으로 구분하고 상위 근거 두 개와 바뀌는 조건을 2×2 카드로 표시한다. 자산 수익률 예측이나 매매 신호는 만들지 않는다.
- Previous completed task: [Economic Cycle Provisional Hybrid V2 2026-07-16](../tasks/active/overview-market-context-economic-cycle-provisional-hybrid-v2-20260716/STATUS.md) — validation threshold를 유지한 채 계산 가능한 LIMITED 결과를 `잠정 모델 추정`으로 공개하고 READY는 `검증된 모델 추정`, 계산 불가는 `판단 불가`로 분리했다. 원형 clock을 최근 12개월 2×2 국면 경로로 교체하고 hover/focus 지점 정보를 추가했으며, 최근 60개월+2개월 ribbon은 실제 history 개수로 전체 너비를 채운다. Actual 122 snapshot은 그대로 보존한다.
- Previous completed task: [U.S. Economic Cycle V1 2026-07-16](../tasks/active/overview-market-context-us-economic-cycle-v1-20260716/STATUS.md) — 1차~5차 + actual bootstrap complete. 17-series FRED/ALFRED vintage ledger `1,232,856`행, strict as-of loader, leakage-safe h0/h1/h2 probability engine, 121개월 replay, rolling-origin publication gate, compact artifact/snapshot, `경제 사이클 | S&P 500 | 미국 개별주식` selector와 responsive React workbench를 연결했다.
- Previous completed task: [Turnaround Derived Quarter Provenance V1 2026-07-16](../tasks/active/overview-market-context-turnaround-derived-quarter-provenance-v1-20260716/STATUS.md) — 1차~4차 complete. Explicit concept family 안의 FY/Q1/Q2/Q3 확정 공시로 missing Q4를 안전하게 산출하고, per-metric/TTM provenance와 `공시 기반 산출` marker·badge·산식을 전환분석에 표시한다. MRNA 2023-Q4와 desktop/420px QA를 완료했다.
- Previous completed task: [Turnaround Stage Semantics Fix V1 2026-07-16](../tasks/active/overview-market-context-turnaround-stage-semantics-fix-v1-20260716/STATUS.md) — 1차~3차 complete. Canonical `USD per share` diluted EPS를 turnaround reader에 포함하고, backend threshold를 유지한 채 6개 rail에서 전환 신호·이미 양수·PER 적용 가능·흑자지만 개선폭 미달을 구분한다. `ESTABLISHED`는 UI-local 상태이며 저장 milestone이 아니다.
- Previous completed task: [US Stock Freshness Refresh V1 2026-07-15](../tasks/active/overview-market-context-us-stock-freshness-refresh-v1-20260715/STATUS.md) — 1차~3차 complete. 선택 종목 cached UI는 DB-only로 즉시 열고, 마지막 완료 NYSE 거래일·profile/가격 정렬·실제 재무 raw gap이 어긋날 때만 상단의 단일 `최신 데이터로 다시 계산` action을 표시한다. 명시 클릭에서 profile/price는 CIK 없이 먼저 수집하고 SEC statement만 identity를 요구한다.
- Previous completed task: [US Stock Turnaround Analysis V1 2026-07-15](../tasks/active/overview-market-context-us-stock-turnaround-analysis-v1-20260715/STATUS.md) — 1차~5차 complete. 미국 개별주식 내부에 `PER 상대가치 | 전환 분석` selector를 추가하고, filing-aware discrete-quarter 매출·margin·OCF·FCF·EPS, cash runway·debt·dilution risk, stage-appropriate valuation readiness를 표시한다. PER가 READY인 AMD/AAPL은 기존 분석을 기본으로 유지하고 RIVN/LCID/PLTR는 전환 분석을 기본으로 연다. V1은 selected-company analysis이며 universe-wide screener/peer ranking은 후속이다.
- Previous completed task: [US Stock Valuation V1 2026-07-14](../tasks/active/overview-market-context-us-stock-valuation-v1-20260714/STATUS.md) — original 1차~5차, 2026-07-15 정확성 후속 1차~3차, 부분 이력 후속 1차~3차 complete. Nasdaq-100 user-facing selector를 searchable 미국 개별주식 상대가치 화면으로 교체했고, primary-period filing-aware TTM EPS/PER, split-year share-basis 정규화, 60m/36m Graph 1과 독립 Graph 2 readiness, DB-only 검색과 explicit selected-symbol 수집을 연결했다. 1/3/5년은 계산 가능한 월을 원래 달력 위치에 표시하고 결측 구간을 연결·보간하지 않는다. 기존 Nasdaq backend는 보존한다.
- Previous completed task: [Nasdaq-100 Scenario History Warmup V1 2026-07-13](../tasks/active/overview-market-context-nasdaq100-scenario-history-warmup-v1-20260713/STATUS.md) — 1차~5차 implementation/QA complete; 60개월 rolling 계약을 유지한 최대 119개월 보강 action과 선택 기간별 정확한 부족 안내를 추가했다. Local actual QA는 66/119 READY이며 무료 원천 gap은 합성하지 않는다.
- Previous completed task: [Nasdaq-100 60m Coverage Repair Action V1 2026-07-13](../tasks/active/overview-market-context-nasdaq100-coverage-repair-action-v1-20260713/STATUS.md) — valuation coverage blocker용 60개월 보강과 strict rematerialization을 완료했다.
- Previous completed Institutional Portfolios task: [Institutional Portfolios Context-First Redesign V1 2026-07-18](../tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/STATUS.md).
- Previous completed Institutional Portfolios task: [Institutional Portfolios Security Detail Chart Layout V1 2026-07-12](../tasks/active/institutional-portfolios-security-detail-chart-layout-v1-20260712/STATUS.md).
- Previous completed task: [Institutional Portfolios Watchlist / Mapping V1 2026-07-12](../tasks/active/institutional-portfolios-watchlist-mapping-v1-20260712/STATUS.md).
- Previous completed task: [Institutional Portfolios Two-Tier Tabs V1 2026-07-12](../tasks/active/institutional-portfolios-two-tier-tabs-v1-20260712/STATUS.md).
- Previous completed task: [Institutional Portfolios Portfolio / Security IA V1 2026-07-12](../tasks/active/institutional-portfolios-portfolio-security-ia-v1-20260712/STATUS.md).
- Previous completed task: [Institutional Portfolios Interactive Security Chart V1 2026-07-12](../tasks/active/institutional-portfolios-interactive-security-chart-v1-20260712/STATUS.md).
- Previous completed task: [Institutional Portfolios Holding Chart Refresh V1 2026-07-12](../tasks/active/institutional-portfolios-holding-chart-refresh-v1-20260712/STATUS.md).
- Previous completed task: [Institutional Portfolios UX Detail / Performance V1 2026-07-11](../tasks/active/institutional-portfolios-ux-detail-performance-v1-20260711/STATUS.md).
- Previous completed task: [Institutional Portfolios Live SEC 13F V1 2026-07-09](../tasks/active/institutional-portfolios-live-sec13f-v1-20260709/STATUS.md).
- Previous completed task: [Institutional Portfolios React Workbench V1 2026-07-09](../tasks/active/institutional-portfolios-react-workbench-v1-20260709/STATUS.md).
- Previous completed task: [Institutional Portfolios Workspace V1 2026-07-08](../tasks/active/institutional-portfolios-workspace-v1-20260708/STATUS.md).
- Recent completed Final Review task: [Final Review Evidence Closure Contract V1 2026-07-12](../tasks/active/final-review-evidence-closure-contract-v1-20260712/STATUS.md).
- Previous completed task: [S&P 500 Valuation V1 2026-07-12](../tasks/active/overview-market-context-sp500-valuation-v1-20260712/STATUS.md).
- Previous completed task: [Practical Validation Recheck Handoff Loop Fix V1 2026-07-12](../tasks/active/practical-validation-recheck-handoff-loop-fix-v1-20260712/STATUS.md).
- Previous completed task: [Practical Validation Pre-Final Enrichment Gate V1 2026-07-12](../tasks/active/practical-validation-pre-final-enrichment-gate-v1-20260712/STATUS.md).
- Previous completed task: [Overview Market Movers Top Actions / Monthly History V1 2026-07-11](../tasks/active/overview-market-movers-top-actions-monthly-history-v1-20260711/STATUS.md).
- Previous completed task: [Overview Market Movers Visual Grouping V1 2026-07-11](../tasks/active/overview-market-movers-visual-grouping-v1-20260711/STATUS.md).
- Earlier completed task: [Overview Market Movers Section Title Unification V1 2026-07-11](../tasks/active/overview-market-movers-section-title-unification-v1-20260711/STATUS.md).
- Previous completed task: [Final Review Readable Review Evidence V1 2026-07-11](../tasks/active/final-review-readable-review-evidence-v1-20260711/STATUS.md).
- Previous completed task: [Final Review Decision Flow Simplification V1 2026-07-11](../tasks/active/final-review-decision-flow-simplification-v1-20260711/STATUS.md).
- Previous completed task: [Final Review Responsive Evidence V1 2026-07-11](../tasks/active/final-review-responsive-evidence-v1-20260711/STATUS.md).
- Previous completed task: [Final Review Decision Surface Consolidation V1 2026-07-11](../tasks/active/final-review-decision-surface-consolidation-v1-20260711/STATUS.md).
- Previous completed task: [Portfolio Workflow Legacy Reset / Rebuild 2026-07-11](../tasks/active/portfolio-workflow-legacy-reset-rebuild-20260711/STATUS.md).
- Previous completed task: [Final Review Confirmed Review Flow V1 2026-07-11](../tasks/active/final-review-confirmed-review-flow-v1-20260711/STATUS.md).
- Previous completed task: [Final Review Investment Report Detail Tabs V1 2026-07-11](../tasks/active/final-review-investment-report-detail-tabs-v1-20260711/STATUS.md).
- Previous completed task: [Final Review Investment Report Flat UI V1 2026-07-10](../tasks/active/final-review-investment-report-flat-ui-v1-20260710/STATUS.md).
- Previous completed task: [Final Review Investment Report IA V1 2026-07-10](../tasks/active/final-review-investment-report-ia-v1-20260710/STATUS.md).
- Previous completed task: [Final Review Candidate Selection Integration V1 2026-07-10](../tasks/active/final-review-candidate-selection-integration-v1-20260710/STATUS.md).
- Previous completed task: [Final Review Sentiment Scope Cleanup V1 2026-07-10](../tasks/active/final-review-sentiment-scope-cleanup-v1-20260710/STATUS.md).
- Previous completed task: [Final Review Detailed Scorecard V1-V6 2026-07-09](../tasks/active/final-review-detailed-scorecard-v1-v6-20260709/STATUS.md).
- Previous completed task: [Final Review Level3 React V2-V6 2026-07-09](../tasks/active/final-review-level3-react-v2-v6-20260709/STATUS.md).
- Previous completed task: [Practical Validation Flow5 CTA Integration V1 2026-07-09](../tasks/active/practical-validation-flow5-cta-integration-v1-20260709/STATUS.md).
- Previous completed task: [Practical Validation Stage Ownership V1 2026-07-09](../tasks/active/practical-validation-stage-ownership-v1/STATUS.md).
- Previous completed task: [Practical Validation Flow4 Action Center V1 2026-07-09](../tasks/active/practical-validation-flow4-action-center-v1-20260709/STATUS.md).
- Previous completed task: [Practical Validation Flow4 Data Action Board V1 2026-07-09](../tasks/active/practical-validation-flow4-data-action-board-v1-20260709/STATUS.md).
- Previous completed task: [Practical Validation Flow Gating / Evidence IA V1 2026-07-08](../tasks/active/practical-validation-flow-gating-evidence-ia-v1-20260708/STATUS.md).
- Previous completed task: [Practical Validation Category Empty State V1 2026-07-08](../tasks/active/practical-validation-category-empty-state-v1-20260708/STATUS.md).
- Previous completed task: [Post-Merge Docs / Code Flow Refresh 2026-07-08](../tasks/active/post-merge-docs-flow-refresh-20260708/STATUS.md).
- Previous completed task: [Practical Validation Boundary Cleanup V1 2026-07-08](../tasks/active/practical-validation-boundary-cleanup-v1-20260708/STATUS.md).
- Previous completed task: [Practical Validation Flow4 Final Review Handoff V1 2026-07-08](../tasks/active/practical-validation-flow4-final-review-handoff-v1-20260708/STATUS.md).
- Previous completed task: [Practical Validation Flow4 Outcome Taxonomy V1 2026-07-08](../tasks/active/practical-validation-flow4-outcome-taxonomy-v1-20260708/STATUS.md).
- Previous completed task: [Practical Validation Required Taxonomy Refactor V1 2026-07-08](../tasks/active/practical-validation-required-taxonomy-refactor-v1-20260708/STATUS.md).
- Previous completed task: [Practical Validation Required Taxonomy Audit V1 2026-07-08](../tasks/active/practical-validation-required-taxonomy-audit-v1-20260708/STATUS.md).
- Previous completed task: [Backtest Symbol Resolver V1 2026-07-08](../tasks/active/backtest-symbol-resolver-v1-20260708/STATUS.md).
- Previous completed task: [Backtest Factor Readiness Action UI V1 2026-07-07](../tasks/active/backtest-factor-readiness-action-ui-v1-20260707/STATUS.md).
- Previous completed task: [Backtest Coverage Provider Gap Refresh V1 2026-07-07](../tasks/active/backtest-coverage-provider-gap-refresh-v1-20260707/STATUS.md).
- Previous completed task: [Practical Validation Flow4 Action Steps V3 2026-07-07](../tasks/active/practical-validation-flow4-action-steps-v3-20260707/STATUS.md).
- Earlier completed task: [Practical Validation Flow4 Action Guide V2 2026-07-07](../tasks/active/practical-validation-flow4-action-guide-v2-20260707/STATUS.md).
- Earlier completed task: [Practical Validation Flow 4 Resolution Guide V1 2026-07-07](../tasks/active/practical-validation-flow4-resolution-guide-v1-20260707/STATUS.md).
- Earlier completed task: [Backtest PIT Universe V1 2026-07-07](../tasks/active/backtest-pit-universe-v1-20260707/STATUS.md).
- Earlier completed task: [Backtest Strategy Form Cleanup V1 2026-07-07](../tasks/active/backtest-strategy-form-cleanup-v1-20260707/STATUS.md).
- Earlier completed task: [Backtest Strategy Detail React V1 2026-07-07](../tasks/active/backtest-strategy-detail-react-v1-20260707/STATUS.md) was superseded by the form cleanup task; the overbuilt Strategy Detail panel is no longer an active flow.
- Earlier completed task: [Practical Validation Flow 4 Labels V1 2026-07-06](../tasks/active/practical-validation-flow4-labels-v1-20260706/STATUS.md).
- Latest completed product task: [Practical Validation Taxonomy Roadmap V1 2026-07-05](../tasks/active/practical-validation-taxonomy-roadmap-v1-20260705/STATUS.md).
- Recent Backtest handoff task: [Backtest Second Stage Visibility V1 2026-07-05](../tasks/active/backtest-second-stage-visibility-v1-20260705/STATUS.md).
- Recent Overview / Market Movers task: [Overview Market Movers Fundamental Charts 2026-07-08](../tasks/active/overview-market-movers-fundamental-charts-20260708/STATUS.md).
- Recent Overview / Market Context task: [S&P 500 Valuation V1 2026-07-12](../tasks/active/overview-market-context-sp500-valuation-v1-20260712/STATUS.md).
- Recent Overview Futures Macro task: [Overview Futures Macro Evidence / Original Data UX 2026-07-06](../tasks/active/overview-futures-macro-evidence-original-data-ux-20260706/STATUS.md).
- Recent data-source migration: [Fundamental Source Migration P0-P8 research / implementation records](../researches/active/2026-06-fundamental-source-migration/DEVELOPMENT_GUIDE.md). Canonical financial statement source is EDGAR detailed statements plus statement shadow tables; broad yfinance fundamentals / factors are legacy compatibility only.
- Recent Overview final cleanup task: [Overview Final Cleanup V33-V36 2026-06-29](../tasks/active/overview-final-cleanup-v33-v36-20260629/STATUS.md).
- Recent Overview service split task: [Overview Service Split V25-V32 2026-06-29](../tasks/active/overview-service-split-v25-v32-20260629/STATUS.md).
- Recent Overview legacy removal task: [Overview Legacy Dashboard Removal V17-V24 2026-06-25](../tasks/active/overview-legacy-dashboard-removal-v17-v24-20260625/STATUS.md).
- Recent Overview helper extraction task: [Overview Tab Helper Extraction V11-V16 2026-06-25](../tasks/active/overview-tab-helper-extraction-v11-v16-20260625/STATUS.md).
- Recent Backtest strategy contract task: [Risk Parity / Dual Momentum 5B 2026-06-10](../tasks/active/risk-parity-dual-momentum-5b-20260610/STATUS.md).
- Recent Reference merge-review fix: [Merge Review Fixes 2026-06-08](../tasks/active/merge-review-fixes-20260608/STATUS.md).
- Current product state: recent merged work is grouped as Overview / Market Context, Backtest Analysis, Practical Validation / Final Review, Operations / Portfolio Monitoring, and UI / Engine Boundary. Overview primary tabs are `Market Context`, `Market Movers`, `Futures Macro`, `Sentiment`, and `Events`; each tab keeps its thin entrypoint, helper bridge, visual components, and service read model boundary. `Market Context` valuation has an S&P 500 / 미국 개별주식 selector. S&P retains the Shiller/SEP 60m/36m and 1/3/5-year flow. 개별주는 DB-only 기업 검색 뒤 내부 `PER 상대가치 | 전환 분석`을 제공한다. PER는 primary filing-period 기반 TTM EPS, split-neutral 60m/36m multiple, FOMC+기업 초과성장 relative scenario와 독립 Graph 1/2 readiness를 유지한다. 전환 분석은 filing-aware discrete quarter, 8/12/20-quarter 영업·현금 chart, independent milestone, runway/debt/dilution risk, fresh-input valuation readiness를 제공하고 negative P/E를 만들지 않는다. 6개 rail은 backend threshold를 자동 통과시키지 않으며, 이미 흑자인 영업/EPS는 UI-local `ESTABLISHED`로 전환 신호와 구분한다. 화면 진입·분석 전환은 read-only이며, 공용 NYSE 완료-session 기준보다 자료가 뒤처질 때만 상단의 selected-symbol action을 표시한다. 명시 클릭 시 profile/price는 CIK 없이 먼저 실행하고 SEC statement만 identity를 요구한다. 기존 Nasdaq QQQ public-filing backend/materialization/collector는 보존하지만 current selector에는 연결되지 않는다. `Futures Monitor` / `Sector / Industry` are not primary navigation surfaces. See [Roadmap](./ROADMAP.md).
- Current Final Review evidence state: [Final Review Evidence Closure Contract V1](../tasks/active/final-review-evidence-closure-contract-v1-20260712/STATUS.md) is completed. Practical Validation closes actionable root issues before handoff, while Final Review records accepted limits / Monitoring transfers as terminal states instead of treating REVIEW count as unfinished work.

## By Purpose

| 목적 | 먼저 볼 문서 |
|---|---|
| 프로젝트가 무엇을 만드는지 확인 | [Product Direction](./PRODUCT_DIRECTION.md) |
| 현재 개발 순서와 active task 확인 | [Roadmap](./ROADMAP.md) |
| 코드 위치와 책임 확인 | [Project Map](./PROJECT_MAP.md) |
| 용어 의미 확인 | [Glossary](./GLOSSARY.md) |
| 시스템 구조와 layer 경계 확인 | [Architecture](./architecture/README.md) / [System Boundaries](./architecture/SYSTEM_BOUNDARIES.md) |
| 사용자 / 런타임 흐름 확인 | [Flows](./flows/README.md) |
| DB / JSONL / 저장 경계 확인 | [Data](./data/README.md) |
| 실행 / 검증 / 운영 절차 확인 | [Runbooks](./runbooks/README.md) |
| 제품 방향 / 벤치마킹 리서치 확인 | [Research](../researches/README.md) |
| backtest 결과 report 확인 | [Backtest Reports](../reports/backtests/INDEX.md) |

## Work Records

| 위치 | 역할 |
|---|---|
| `.aiworkspace/note/finance/phases/active/` | `main-dev` worktree가 관리한 phase 단위 계획과 통합 기록. 현재 완료 board도 handoff 용도로 남아 있으므로 `STATUS_MANIFEST.md`, README, roadmap의 active 표시를 함께 확인 |
| `.aiworkspace/note/finance/phases/done/` | 완료된 phase의 closeout summary. full board archive가 아니라 summary 중심 |
| `.aiworkspace/note/finance/tasks/active/` | 개별 실행 task의 계획, 진행 상태, 실행 결과. 과거 완료 task도 retained work record로 남아 있으므로 `STATUS_MANIFEST.md`, README, roadmap에서 current active 상태를 확인 |
| `.aiworkspace/note/finance/researches/active/` | 제품 방향, 벤치마킹, 기능 후보 리서치 산출물 |
| `.aiworkspace/note/finance/agent/` | Codex 반복 실수, 교훈, 운영 팁 |
| `.aiworkspace/note/finance/reports/backtests/` | 전략 탐색, 후보 근거, validation report |
| `.aiworkspace/note/finance/registries/` | 제품 workflow가 읽고 쓰는 append-only JSONL registry |
| `.aiworkspace/note/finance/saved/` | 사용자가 저장한 reusable portfolio setup |

## Documentation Rules

- `docs/`에는 오래 유지될 프로젝트 지식만 둔다.
- 작업 중 추측, 조사 메모, 실패 로그는 task 문서에 먼저 둔다.
- 제품 방향 리서치의 추측, 비교표, source note, 기능 후보는 research 문서에 먼저 둔다.
- phase는 여러 task를 묶는 상위 관리 단위다.
- task는 실제 코드나 문서를 수정하는 실행 단위다.
- `registries/`와 `saved/`의 JSONL은 제품 데이터이므로 문서 정리 과정에서 삭제하거나 재작성하지 않는다.
- backtest report는 `.aiworkspace/note/finance/reports/backtests/`에 두고, registry / saved source-of-truth와 섞지 않는다.
- run history, runtime artifact, Playwright output, temp CSV는 장기 문서가 아니다.
