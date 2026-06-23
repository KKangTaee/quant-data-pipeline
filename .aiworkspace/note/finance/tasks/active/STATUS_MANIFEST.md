# Active Task State Manifest

Status: Active
Last Verified: 2026-06-23

## Current State

Current active task:

- none

Latest completed task:

- `overview-nav-internal-lazy-load-v1-20260623`

Latest completed docs cleanup task:

- `post-merge-verification-handoff-20260607`

Recent post-merge cleanup records:

- `post-merge-docs-alignment-20260607`: 1차 product / roadmap / current state alignment
- `post-merge-boundary-docs-alignment-20260607`: 2차 architecture / data / flow boundary alignment
- `post-merge-active-state-cleanup-20260607`: 3차 active task / phase state manifest alignment
- `post-merge-verification-handoff-20260607`: 4차 verification / handoff alignment

Recent structure audit records:

- `refactor-round-closeout-20260607`: 10차 structure / refactor baseline closeout, residual split decision, and handoff audit
- `backtest-compare-components-split-20260607`: 9차 Backtest Compare Streamlit split first pass / Portfolio Mix Builder visual component extraction
- `ingestion-diagnostic-facade-20260607`: 7차 large Streamlit file split 7B / Ingestion read-only diagnostic facade extraction
- `runtime-backtest-strict-family-split-20260607`: 8차 runtime large file split 8C / strict quality-value runtime wrapper extraction
- `runtime-backtest-real-money-split-20260607`: 8차 runtime large file split 8B / real-money readiness helper extraction
- `runtime-backtest-risk-on-momentum-split-20260607`: 8차 runtime large file split 8A / Risk-On Momentum runtime slice extraction
- `streamlit-ingestion-console-split-20260607`: 7차 large Streamlit file split 7A / Ingestion Console render-state-job UI extraction
- `overview-ingestion-action-boundary-20260607`: 6차 collection / read action boundary cleanup
- `code-boundary-refactor-audit-20260607`: 5차 code boundary / refactor baseline audit

Recent Reference records:

- `merge-review-fixes-20260608`: post-merge review fix / Reference page-link, V4 status, and catalog test assertion cleanup
- `reference-drift-guard-qa-polish-v5-20260608`: Reference contextual help 5차 / drift guard and QA polish
- `reference-contextual-links-v4-20260608`: Reference contextual help 4차 / workflow screen expander links
- `reference-glossary-concept-dictionary-v3-20260607`: Reference Glossary 3차 / shared concept dictionary
- `reference-guides-journey-playbooks-v2-20260607`: Reference Guides 2차 / journey playbooks and failure states
- `reference-guides-center-v1-20260607`: Reference Guides 1차 / task-first Reference Center

Recent portfolio selection records:

- `distinct-strategy-portfolio-discovery-20260609`: unique strategy family constraint / SPY superior GTAA U3 85% + GRS Compact 10% + Risk Parity Trend 5% portfolio / Final Review and Monitoring registration
- `portfolio-discovery-final-review-monitoring-20260608`: current strategy catalog exploration / all-ETF Final Review selected decision / Portfolio Monitoring registration

Recent Operations records:

- `operations-v2-closeout-20260608`: Operations Overview V2 5차 / final QA and docs closeout
- `operations-review-queue-refinement-20260608`: Operations Overview V2 4차 / priority and evidence ordered review queue
- `operations-evidence-health-strip-20260607`: Operations Overview V2 3차 / Evidence Health mini strip
- `operations-portfolio-first-summary-20260607`: Operations Overview V2 2차 / Portfolio Monitoring Status summary first-pass
- `operations-cockpit-cleanup-20260607`: Operations Overview V2 1차 cleanup / archive and development-history user-facing artifact removal

Recent Overview / Market Context records:

- `overview-nav-internal-lazy-load-v1-20260623`: Completed record. `Workspace > Overview` primary navigation now uses internal `st.pills` state styled as plain text tabs with an active red underline. It does not render tab anchors, so switching stays inside the current browser session. Query-param slugs remain read-only compatibility input, and fresh Overview entry defers the heavy default Market Context body until `시장 맥락 불러오기`. Boundaries stayed visual/navigation/loading-only: no provider / schema / registry / saved / validation / monitoring / trade semantics changed.
- `overview-primary-nav-pill-v1-20260623`: Superseded completed record. This first visual polish used a compact custom anchor nav with Korean primary labels and English secondary labels. It was replaced by `overview-nav-internal-lazy-load-v1-20260623` because tab switching must not behave as link navigation.
- `overview-primary-tab-soft-remove-v1-20260623`: Completed record. `Workspace > Overview` primary selector now exposes only `Market Context`, `Market Movers`, `Sentiment`, and `Events`. `Futures Monitor` and `Sector / Industry` standalone tabs are soft-removed from primary navigation and old selected values fall back to `Market Context`. Futures / sector services and helper renderers were not physically deleted; no provider / schema / registry / saved / validation / monitoring / trade semantics changed.
- `overview-ia-cleanup-v22-20260622`: Completed record superseded by `overview-primary-tab-soft-remove-v1-20260623` for current primary tab membership. V22 removed `Data Health` and `Candidate Ops` from the primary selector while still retaining `Futures Monitor` and `Sector / Industry`; V1 soft-remove later removed those two standalone tabs as well. registry / saved JSONL, run history, provider / DB schema, Backtest / validation / monitoring / trade semantics는 변경하지 않았다.
- `overview-market-context-source-refresh-ux-v21-20260622`: Completed record. `Overview > Market Context` V21 보정으로 `근거: 자료 기준 / 출처 상태`를 긴 진단 표에서 `자료 상태 요약` / `시장 브리프 직접 자료` / `참고 / 관리 자료` / `보강 판단` 흐름으로 바꿨다. `필요 자료 보강`은 실행 대상이 없을 때 disabled smart-refresh button 대신 compact no-action panel과 보조 전체 보강 action만 남긴다. Refresh action id / provider / DB / registry / saved / validation / monitoring / trade semantics는 변경하지 않았다.
- `overview-lazy-tab-render-v20-20260622`: Completed record. `Workspace > Overview` V20 보정으로 top-level deep tab 렌더링을 native eager `st.tabs`에서 selected-tab lazy renderer로 바꿨다. 기본 선택은 `Market Context`이며, 당시 탭 membership은 이후 `overview-primary-tab-soft-remove-v1-20260623`이 supersede했다. Candidate Ops의 dashboard snapshot load도 Candidate Ops branch 안으로 지연했다. 각 탭 내부 read model / UI 의미 / provider / DB / registry / validation / monitoring / trade semantics는 변경하지 않았다.
- `overview-market-context-macro-meaning-gradient-v19-20260622`: Completed record. `Overview > Market Context` V19 보정으로 핵심 자산 비교와 Macro 조건 결과 비교 matrix의 양수 / 음수 return gradient를 더 선명하게 표시하고, 조건에는 쓰지 않은 Macro 배경(T10Y3M / VIXCLS / BAA10Y)에 현재 값이 뜻하는 상태 판단 문장을 추가했다. 기존 DB-backed bucket / broad vs conditioned sample 계산은 바꾸지 않았고, 새 provider / schema / hard condition / validation / monitoring / trade semantics는 추가하지 않았다.
- `overview-market-context-macro-intersection-v18-20260622`: Completed record. `Overview > Market Context` V18 보정으로 Macro 조건 표본이 `GLD 조건 적용` 후 `금리선물 조건 적용`처럼 순서 의존적으로 보이던 문제를 정리했다. 서비스 모델은 broad 표본, GLD 같은 상태 count, 금리선물 같은 상태 count, futures 계산 가능 count, 두 조건 교집합 count를 `macro_condition_counts`로 제공한다. UI는 `기본 유사 맥락 기준` / `GLD 같은 상태` / `금리선물 같은 상태` / `두 조건 모두` 4칸으로 표시하며, 최종 조건 후 결과는 두 조건 교집합 표본으로 계산한다. 계산 bucket 기준 / provider / schema / persistence / validation / monitoring / trade semantics는 추가하지 않았다.
- `overview-market-context-macro-polish-v17-20260621`: Completed record. `Overview > Market Context` V17 보정으로 Macro 조건 축소 bar의 `GLD 조건 적용` / `금리선물 조건 적용`이 무엇을 의미하는지 바로 읽히게 했다. 각 단계는 broad relative-strength 표본에서 현재와 비슷한 GLD 상태, ZN=F / ZB=F 금리선물 배경을 차례로 남기는 흐름으로 표시한다. `조건에는 쓰지 않은 Macro 배경`은 T10Y3M / VIXCLS / BAA10Y를 한글 상태 badge, 현재 값, broad 표본 내 같은 상태 비율 bar, source 설명 순서로 보여준다. 계산 로직 / hard condition / provider / schema / persistence / validation / monitoring / trade semantics는 추가하지 않았다.
- `overview-market-context-macro-matrix-v16-20260621`: Completed record. `Overview > Market Context` V16 보정으로 V15 Macro 조건 비교가 여전히 prototype-like wide table / verbose text처럼 보이던 문제를 정리했다. Macro 표본 흐름은 historical analog와 같은 basis bar로 바꾸고, 결과 변화는 자산 x `기본 / 조건 후 / 변화` matrix로 렌더링한다. 긴 조건 source 원문은 접힌 상세로 낮추고, 현재 Macro 배경은 `금리곡선` / `변동성` / `신용스프레드` 한글 라벨을 우선 표시한다. 계산 로직 / hard condition / provider / schema / persistence / validation / monitoring / trade semantics는 추가하지 않았다.
- `overview-market-context-macro-labels-v15-20260621`: Completed record. `Overview > Market Context` V15 보정으로 `Macro 조건 후 결과 변화`의 표본 축소 흐름을 `기본 유사 맥락` -> `GLD 조건 적용` -> `금리선물 조건 적용`으로 명명했다. GLD / Rate Pressure 단계는 기존 broad anchor pool에서 몇 회가 남았는지 문장으로 설명하고, T10Y3M / VIXCLS / BAA10Y `현재 Macro 배경 참고`는 한글 지표 설명과 broad sample 중 같은 상태 횟수를 함께 표시한다. 계산 로직 / hard condition / provider / schema / persistence / validation / monitoring / trade semantics는 추가하지 않았다.
- `overview-market-context-macro-clarity-v14-20260621`: Completed record. `Overview > Market Context` V14 보정으로 Macro 조건 비교를 기본 유사 맥락 기준과 Macro 추가 조건으로 분리했다. `Sector ETF vs SPY relative strength`는 broad sample 기준으로 낮추고, GLD / Rate Pressure futures 조건은 표본 축소 흐름으로 표시한다. Broad vs conditioned 결과 변화, 현재 Macro 배경(T10Y3M / VIXCLS / BAA10Y), 접힌 상세 / 원본 통계 순서로 읽게 했으며, matrix 색상은 median return 방향과 크기 기준으로 농도를 조절하고 sector pressure map 수익률은 소수점 둘째 자리까지 표시한다.
- `overview-market-context-flow-alignment-v13-20260621`: Completed record. `Overview > Market Context` V13 보정으로 최신 historical analog가 상단 Market Context의 visible sector leadership snapshot과 같은 섹터를 쓰게 정렬했다. Sector pressure map은 provider sector alias를 canonical 11개 섹터로 normalize하고 전체를 균일 tile로 표시한다. Historical analog는 `먼저 볼 점` / `주의할 점` / `시장 배경 요약` guide block을 기본 흐름에서 제거하고, sector ETF / SPY / QQQ / TLT / GLD를 하나의 핵심 비교 matrix로 보여준다. Broad sample이 없을 때 Macro 조건 비교는 숨겨 dashed prototype UI를 만들지 않는다.
- `overview-market-context-analog-usability-v12-20260621`: Completed record. `Overview > Market Context` V12 보정으로 historical analog의 selected as-of 공통 daily price basis mismatch를 bounded 가격 기준 최신화 action으로 연결하고, 기준/조건/표본 중복을 compact basis summary + 접힌 계산 경계 상세로 낮췄다. 핵심 자산은 5D / 20D / 60D matrix로 먼저 읽고, 보조 자산은 배경 요약으로 낮추며, 원본 통계 표는 `상세 통계` disclosure에 남긴다.
- `overview-market-context-analog-macro-ux-v11-20260621`: Completed record. `Overview > Market Context` V11 보정으로 historical analog / Macro 조건 포함 비교를 prototype-like card stack에서 분석형 flow로 재구성했다. 기준 선택은 analog flow 바로 앞에 두고, 결과는 basis bar, `현재 기준` / `유사 사례 조건` / `표본 품질`, `먼저 볼 점` / `주의할 점`, 별도 Macro comparison section, condition-role groups로 읽게 했다.
- `overview-market-context-analog-basis-clarity-v10-20260620`: Completed record. `Overview > Market Context` V10 보정으로 historical analog의 요청 기준일과 실제 계산 기준일을 분리해 표시하고, 공통 daily 가격 coverage가 오래되어 선택일보다 이른 날짜로 계산될 때 limiting symbols와 basis warning을 보여준다. Macro 조건 포함 비교는 broad sample -> GLD 배경 -> 금리선물 압력 funnel과 사용자 언어 condition group으로 정리했다.
- `overview-market-context-session-basis-v9-20260620`: Completed record. `Overview > Market Context` V9 보정으로 미국장 휴장 / 장외 시간에는 `오늘의 시장 브리프`를 마지막 거래일 또는 현재 세션 기준 브리프로 표시하고, 장중 snapshot elapsed age만으로 `현재 이슈만 보강`을 띄우지 않도록 했다.
- `overview-market-context-source-actionability-v8-20260620`: Completed record. `Overview > Market Context` V8 보정으로 Events estimate caveat와 Data Health 관리 메타를 unresolved source issue에서 분리했다. Top `자료 상태`, source confidence summary, source ledger는 보강 가능한 자료만 `자료 확인 필요`로 세고, Events는 `참고 제한`, Data Health는 `관리 메타`로 표시한다.
- `overview-market-context-smart-refresh-v7-20260620`: Completed record. `Overview > Market Context` V7 보정으로 Events를 상단 브리프에서 낮추고, 필요 자료 보강을 현재 이슈 기반 smart refresh로 전환했다. 전체 Market Context 자료 보강은 fallback으로 남긴다.
- `overview-market-context-brief-context-absorption-v6-20260620`: Overview Market Context V5 follow-up / `브리프 신뢰도` 독립 섹션을 제거하고, 이벤트 / Futures 자료 제한을 별도 가이드가 아니라 `오늘의 시장 브리프`의 `이벤트 배경` 또는 `Futures/Macro 배경` 결론으로 흡수했다. 상세 source / freshness는 하단 근거 disclosure에 남긴다.
- `overview-market-context-brief-confidence-v5-20260620`: Overview Market Context V4 follow-up / `오늘의 시장 브리프`를 움직임, 확산, Futures/Macro 배경의 3행 market story로 되돌리고, Events / 자료 기준은 별도 `브리프 신뢰도` 영역에서 브리프 읽기 강도 조절 근거로 표시한다. `context_findings` / `next_checks`는 compatibility payload로 유지하되 default user-facing rail로 렌더링하지 않는다.
- `overview-market-context-brief-findings-integration-v4-20260620`: Overview Market Context V3 follow-up / 중복되는 가격 움직임과 Futures-Macro findings rail은 기본 화면에서 제거하고, Events / 자료 신뢰도 caveat를 `오늘의 시장 브리프` 안으로 통합했다. `context_findings` / `next_checks`는 compatibility payload로 유지하되 default user-facing rail로 렌더링하지 않는다.
- `overview-market-context-context-findings-v3-20260620`: Overview Market Context `다음 맥락 체크` follow-up / user-facing action checklist를 `맥락 검토 결과`로 바꿔 Market Context가 이미 읽은 가격 움직임, Futures/Macro, Events, 자료 신뢰도 caveat의 결론 / 해석 영향 / 자료 기준을 보여주게 했다. `next_checks`는 compatibility payload로 남기되 user-facing action checklist로 쓰지 않는다.
- `overview-market-context-brief-flow-redesign-v2-20260620`: Overview Market Context V1 UX 보정 follow-up / top brief rows를 cockpit 안의 `오늘의 시장 브리프` wide lane으로 흡수, `다음 맥락 체크`를 card grid에서 priority / observation / reason / action rail로 변경, historical / macro / source sections의 반복 card visual language 축소
- `overview-market-context-brief-flow-redesign-v1-20260620`: Overview Market Context UX redesign / current brief flow split, historical analog controls inside analog flow, basis ledger, broad-vs-macro sample comparison, source ledger, and `필요 자료 보강` refresh assist
- `overview-market-context-futures-conditioned-analog-v3b-20260618`: Overview Market Context Historical Analog 3차-B / 3차-A GLD `Macro 조건 포함 pilot`에 stored futures daily OHLCV Rate Pressure proxy (`ZN=F` / `ZB=F`) 1개 추가, selected as-of / anchor-date bounded condition, sample quality 유지
- `overview-market-context-macro-conditioned-analog-pilot-v1-20260618`: Overview Market Context Historical Analog 3차-A / 기존 broad analog와 별도인 Macro 조건 포함 pilot, GLD price proxy 조건, sample quality, deferred/disabled condition 표시
- `overview-market-context-analog-asof-window-v2-20260618`: Overview Market Context Historical Analog 2차 / 기준 시점 replay, 5D / 20D / monthly pattern window, current universe metadata 기반 bounded replay 한계 문서화
- `overview-market-context-source-action-flow-v1-20260618`: Overview Market Context Source Action Flow V1 / `next_checks` source-action checklist, source confidence action footer, historical analog basis metadata, refresh assist secondary flow
- `overview-market-movers-period-refresh-v1-20260616`: Overview Market Movers Period Refresh V1 / non-daily Weekly, Monthly, and Yearly EOD price-history manual refresh action through the existing Overview action facade
- `overview-market-context-analog-readability-v5-20260616`: Overview Market Context Analog Readability V5 / Historical analog explanation, summary strip, first-read conclusion, and core/supporting asset table split
- `overview-market-context-analog-repair-v4-20260615`: Overview Market Context Analog Repair V4 / Historical analog coverage gap panel, bounded OHLCV repair action, source confidence summary strip
- `overview-market-context-historical-analog-v1-20260615`: Overview Market Context Historical Analog V1 / Sector Leadership -> Sector ETF Proxy -> context-only historical analog MVP
- `overview-market-context-events-data-trust-v1-20260612`: Overview Market Context Events Data Trust V1 / recent + upcoming major macro event trust
- `overview-data-health-ingestion-handoff-v1-20260608`: Overview Data Health Ingestion Handoff V1 / priority-ranked read-only Data Health -> collection surface handoff
- `overview-macro-context-cockpit-v1-20260608`: Overview Macro Context Cockpit V1 / summary-first DB-backed market context band

Recent Workspace / tooling records:

- `finance-integration-doc-merge-skill-20260617`: Finance integration review skill hardening / document merge conflict checklist for `.aiworkspace/note/finance`

## What `tasks/active/` Means Right Now

This folder currently contains retained work records from prior active worktrees.
Do not infer that every child folder is still open work.

The current active task source of truth is:

1. this manifest
2. [README.md](./README.md)
3. [Finance Roadmap](../../docs/ROADMAP.md)
4. root handoff logs

## Review Count

Reviewed on 2026-06-08:

- `tasks/active`: 194 task folders
- `tasks/done`: README only

Because `tasks/done` has not been used as a full task folder archive, this cleanup does not move all retained task folders.

## Retained Task Groups

| Group | Meaning | Representative Folders |
|---|---|---|
| Post-merge docs cleanup | Current 1차~4차 cleanup records | `post-merge-docs-alignment-20260607`, `post-merge-boundary-docs-alignment-20260607`, `post-merge-active-state-cleanup-20260607`, `post-merge-verification-handoff-20260607` |
| Collection / read boundary cleanup | 6차 Overview / Ingestion action boundary record | `overview-ingestion-action-boundary-20260607` |
| Large Streamlit file split | 7차 Ingestion Console and 9차 Backtest Compare split records | `backtest-compare-components-split-20260607`, `ingestion-diagnostic-facade-20260607`, `streamlit-ingestion-console-split-20260607` |
| Runtime large file split | 8차 Backtest runtime split records | `runtime-backtest-strict-family-split-20260607`, `runtime-backtest-real-money-split-20260607`, `runtime-backtest-risk-on-momentum-split-20260607` |
| Code structure audit | 5차 refactor baseline and 10차 closeout records | `refactor-round-closeout-20260607`, `code-boundary-refactor-audit-20260607` |
| Overview / market context | Overview Market Intelligence, Sentiment, Futures, Why It Moved, Events, automation | `overview-market-sentiment-v1`, `overview-market-movers-second-pass`, `futures-market-monitoring-mvp-v1`, `futures-monitor-stale-refresh-fix-20260607`, `futures-macro-thermometer-validation-v1`, `overview-scheduled-refresh-automation` |
| Backtest Analysis / strategy research | Candidate source generation, portfolio mix builder, Risk-On Momentum research lane | `backtest-portfolio-mix-builder-flow-v1`, `backtest-portfolio-mix-builder-ux-v1`, `risk-on-momentum-5d-v1`, `risk-on-momentum-5d-v2` |
| Practical Validation / Final Review | Validation modules, selected-route gate, evidence read model, Final Review UX | `practical-validation-module-gate-v1`, `practical-validation-selected-route-preflight-v1`, `final-review-selection-readiness-gate-v1`, `final-review-commercial-ux-v1` |
| Operations / Portfolio Monitoring | Operations Console and selected portfolio monitoring work | `operations-v2-closeout-20260608`, `operations-review-queue-refinement-20260608`, `operations-evidence-health-strip-20260607`, `operations-portfolio-first-summary-20260607`, `operations-cockpit-cleanup-20260607`, `operations-console-restructure-v2-v5`, `selected-dashboard-monitoring-first-ux-v1`, `selected-dashboard-manual-scenario-run-v1`, `allocation-drift-evidence-boundary-v1` |
| Reference / product guidance | Reference Center, Glossary, contextual workflow help | `merge-review-fixes-20260608`, `reference-drift-guard-qa-polish-v5-20260608`, `reference-contextual-links-v4-20260608`, `reference-glossary-concept-dictionary-v3-20260607`, `reference-guides-journey-playbooks-v2-20260607`, `reference-guides-center-v1-20260607` |
| Data / provider / lifecycle evidence | Provider snapshots, macro, data coverage, lifecycle, survivorship | `data-provenance-coverage-v1`, `historical-universe-survivorship-v1`, `sec-form25-delisting-backfill-v1`, `symbol-directory-snapshot-ingestion-v1` |
| Phase closeout tasks | Phase 8~13 board open / integrated QA / closeout records | `phase10-board-open`, `phase13-integrated-qa-final-closeout`, `phase13-docs-runbook-alignment-v1` |
| Workspace / tooling | AI workspace migration, plugin / skill system, service boundary, docs rebuild | `ai-workspace-migration`, `doc-system-rebuild`, `product-research-plugin-split`, `service-contract-tests` |

## Physical Migration Rule

Physical movement from `tasks/active/` to `tasks/done/` should be a separate migration task.
That task must:

- create or update a redirect / lookup index
- check references from roadmap, root logs, phase boards, reports, and docs
- avoid moving registry / saved / generated artifacts
- keep a rollback plan or at least a path map

Until then, retained task folders stay in place and are interpreted through this manifest.
