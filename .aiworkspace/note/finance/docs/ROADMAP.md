# Finance Roadmap

Status: Active
Last Verified: 2026-06-18

## Current State After Master Merge

현재 active phase는 없다.

2026-06-07 master 병합 후 제품은 다음 네 흐름이 함께 연결된 상태다.

```text
Workspace > Ingestion
  -> Workspace > Overview market context
  -> Backtest > Backtest Analysis
  -> Backtest > Practical Validation
  -> Backtest > Final Review
  -> Operations > Operations Console
  -> Operations > Portfolio Monitoring
```

현재 5차~10차 code structure / refactor baseline round는 closeout됐다.

- 5차: UI / service / runtime / jobs / finance layer boundary and refactor baseline audit.
- 6차: Overview / Ingestion collection-read action boundary cleanup.
- 7차 / 7B: Ingestion Console physical split and read-only diagnostic facade extraction.
- 8차: Backtest runtime Risk-On Momentum, real-money / readiness, strict quality / value family split.
- 9차: Backtest Compare Portfolio Mix Builder visual component extraction.
- 10차: final structure audit, residual split decision, and handoff closeout.

- Latest completed task: `.aiworkspace/note/finance/tasks/active/finance-integration-doc-merge-skill-20260617/`
- 목적: 반복될 multi-worktree merge에서 `.aiworkspace/note/finance` 문서 충돌을 손실 없이, 문서 역할과 읽기 흐름 기준으로 정리하도록 `finance-integration-review` skill에 전용 checklist를 추가했다.
- 이번 차수에서 하지 않은 일: 새 별도 skill 생성, 자동 충돌 해결기 구현, task folder archive migration, registry / saved JSONL rewrite, generated artifact 정리.
- Latest completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-source-action-flow-v1-20260618/`
- 목적: `Workspace > Overview > Market Context`의 1차 source-action flow 개선으로 `다음 맥락 체크`를 실제 `next_checks` checklist로 렌더링하고, Data Health / Events source action, source confidence footer, historical analog 기준 시점 / 계산식 표시를 명확히 했다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema, UI render 중 external fetch, macro-conditioned analog 계산, historical analog replay 저장소, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- 2차 / 3차 후속: `.aiworkspace/note/finance/tasks/active/overview-market-context-source-action-flow-v1-20260618/DESIGN.md`에 historical analog 기준 시점 / 기간 확장 설계와 macro-conditioned analog pilot 설계 메모를 남겼다.
- Recent previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-movers-coverage-refresh-v1-20260617/`
- 목적: `Workspace > Overview > Market Movers`에 Nasdaq-listed current snapshot coverage를 추가하고, Nasdaq Symbol Directory / intraday 반복 갱신 경로와 Coverage Diagnostics evidence를 보강했다.
- 이번 차수에서 하지 않은 일: Nasdaq Composite / Nasdaq-100 표현, trade signal / 추천, 새 provider / DB schema, registry / saved JSONL write, OS scheduler 등록, 대량 provider collection 실행.
- Recent previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-movers-period-refresh-v1-20260616/`
- 목적: `Workspace > Overview > Market Movers`에서 Weekly / Monthly / Yearly period도 EOD 가격 이력 기준과 `가격 이력 갱신` 수동 action을 같은 화면에서 확인하게 했다.
- 이번 차수에서 하지 않은 일: Daily 자동 갱신 복제, Market Context / Futures / Events / Backtest / Operations / historical analog 변경, 새 provider, DB schema, registry / saved JSONL write, 대량 provider collection 실행.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-readability-v5-20260616/`
- 목적: `Workspace > Overview > Market Context`에서 `참고: 과거 유사 맥락`이 표부터 보이는 구조를 정의 문장, 핵심 요약 strip, `먼저 읽을 결론`, 핵심 / 보조 자산 table 흐름으로 재구성해 사용자가 과거 유사맥락의 기준과 해석을 먼저 읽게 했다.
- 이번 차수에서 하지 않은 일: historical analog 계산식 변경, macro / futures / event / sentiment conditioned analog expansion, anchor date drill-down, 새 provider, DB schema, loader, CSV upload, registry / saved JSONL write, Overview render 중 external fetch, 예측 / 추천 / trading signal, validation / monitoring gate.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-repair-v4-20260615/`
- 목적: `Workspace > Overview > Market Context`에서 `참고: 과거 유사 맥락`의 `자료 부족` 상태를 부족 ticker / row 기준 / `보조 갱신` repair action으로 연결하고, `근거: 자료 기준 / 출처 상태`는 접힌 summary에서도 정상 / 확인 / 부족 count와 핵심 source를 읽게 했다.
- 이번 차수에서 하지 않은 일: 새 provider, DB schema, loader, CSV upload, registry / saved JSONL write, Overview render 중 external fetch, 예측 / 추천 / trading signal, validation / monitoring gate, macro / futures / event conditioned analog expansion.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-supporting-flow-v3-20260615/`
- 목적: `Workspace > Overview > Market Context`에서 하단 보조 흐름을 `다음 맥락 체크`, `참고: 과거 유사 맥락`, `근거: 자료 기준 / 출처 상태`로 재정의하고 Data Health를 main cue row에서 evidence context로 낮췄다.
- 이번 차수에서 하지 않은 일: 새 provider, DB schema, registry / saved JSONL write, Overview render 중 external fetch, dashboard editor, deep drill-in interaction, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-copy-density-v2-20260615/`
- 목적: `Workspace > Overview > Market Context`에서 `오늘의 시장 맥락`을 `현재 맥락:` 한 줄 요약 대신 2~3문장형 brief로 풀고, reading-flow 단락의 typography / color density를 조정했다.
- 이번 차수에서 하지 않은 일: 새 provider, DB schema, registry / saved JSONL write, Overview render 중 external fetch, dashboard editor, deep drill-in interaction, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-section-flow-v1-20260615/`
- 목적: `Workspace > Overview > Market Context`에서 상단 cockpit은 headline / tape / 섹터 압력 지도 / 이벤트 타임라인만 담고, `시장 브리프`, `해석할 때 같이 볼 변수`, `과거 유사 맥락 참고`, `자료 기준 / 출처 상태`를 별도 reading-flow section으로 분리했다.
- 이번 차수에서 하지 않은 일: 새 provider, DB schema, registry / saved JSONL write, Overview render 중 external fetch, dashboard editor, deep drill-in interaction, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-hybrid-visual-v1-20260615/`
- 목적: `Workspace > Overview > Market Context`에서 card-first 구조를 줄이고, 5칸 시장 테이프 / 섹터 압력 지도 / 이벤트 타임라인 / 근거 row 흐름으로 현재 맥락을 더 시각적으로 읽게 한다.
- 이번 차수에서 하지 않은 일: 새 provider, DB schema, registry / saved JSONL write, Overview render 중 external fetch, full dashboard editor, deep drill-in interaction, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-historical-analog-v1-20260615/`
- 목적: `Workspace > Overview > Market Context`에서 current sector leadership을 sector ETF proxy로 연결하고, coverage가 충분한 경우에만 과거 유사 맥락 이후 5D / 20D / 60D 주요 자산 흐름을 context-only로 보여준다.
- 이번 차수에서 하지 않은 일: 예측 모델, 투자 추천 / 매수·매도 신호, Backtest strategy 연결, Practical Validation / Final Review / Operations gate 연결, DB schema, 새 provider, registry / saved JSONL write, full historical PIT sector universe reconstruction.
- Current local coverage note: live leadership sector changes with the latest stored market snapshot. If its sector ETF proxy has insufficient local daily price rows, Market Context now shows the missing ticker and an explicit `보조 갱신` OHLCV repair action instead of a generic `자료 부족` dead end.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-events-data-trust-v1-20260612/`
- 목적: `Workspace > Overview > Market Context / Events`에서 FOMC / CPI / PPI / Employment / GDP 같은 주요 macro event를 recent + upcoming 관점으로 읽고, Market Context에서는 compact event cue와 자료 주의점만 보여준다.
- 이번 차수에서 하지 않은 일: 과거 유사국면 / 향후 예측 기능, 새 provider, DB schema, registry / saved JSONL write, Backtest / Practical Validation / Final Review / Operations 변경, Data Health 진단 패널 전면화.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-ia-closeout-v1-20260608/`
- 목적: `Workspace > Overview` cockpit 아래에 `Overview Map / Deep Tab Reading Order`를 추가해 market context, data repair, transitional Candidate Ops 경계를 명확히 닫았다.
- 이번 차수에서 하지 않은 일: Candidate Ops 제거 / 이동, Backtest workflow 변경, 새 provider, DB schema, registry / saved JSONL write, Overview render 중 external fetch, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-source-confidence-catalog-v1-20260608/`
- 목적: `Workspace > Overview` cockpit 하단에 기존 DB-backed snapshots의 source, owner, freshness, caveat, next check를 보여주는 read-only Source Confidence lane을 추가했다.
- 이번 차수에서 하지 않은 일: 새 provider, provider 교체, DB schema, registry / saved JSONL write, Overview render 중 external fetch, Reference companion 본격 연결, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-breadth-macro-week-v1-20260608/`
- 목적: `Workspace > Overview > Sector / Industry`와 `Events` 상단에 breadth / concentration, latest heatmap, 14일 macro week lane을 추가했다.
- 이번 차수에서 하지 않은 일: full breadth heatmap, Events Quality workflow 본격 구현, 새 provider, schema, persistence, validation / monitoring / trading signal.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-data-health-ingestion-handoff-v1-20260608/`
- 목적: `Workspace > Overview > Data Health` 상단에 stale / missing / failed / partial / due targets를 우선순위화하고 owning collection surface로 넘기는 read-only handoff lane을 추가했다.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/overview-macro-context-cockpit-v1-20260608/`
- 목적: `Workspace > Overview` 상단에 기존 DB-backed movers / breadth / futures / sentiment / events / data-health snapshot을 합성한 summary-first market context cockpit을 추가했다.
- 이번 차수에서 하지 않은 일: 새 provider, DB schema, registry / saved JSONL write, Overview render 중 external fetch, Data Health -> Ingestion Action Queue, heatmap / macro week view, Candidate Ops IA 변경, live approval / broker order / auto rebalance.
- Recent completed Reference merge-review task: `.aiworkspace/note/finance/tasks/active/merge-review-fixes-20260608/`
- 목적: sub-dev / main-dev master merge review에서 확인된 Reference contextual help internal link, Reference V4 task status, Reference Guides catalog test assertion 문제를 바로잡았다.
- 이번 차수에서 하지 않은 일: Reference 전체 UX 재설계, URL query deep-linking, Ingestion / Overview 전체 surface 연결, DB / registry / saved JSONL rewrite, provider fetch, live approval / broker order / auto rebalance.
- Recent previous completed task: `.aiworkspace/note/finance/tasks/active/reference-drift-guard-qa-polish-v5-20260608/`
- 목적: Reference contextual help가 shared Glossary concept dictionary와 Reference route boundary에서 drift되지 않도록 Streamlit-free guard를 추가하고, guide path copy 표시를 정리한다.
- Recent previous sub-dev task: `.aiworkspace/note/finance/tasks/active/operations-v2-closeout-20260608/`
- 목적: Operations Overview V2 5차로 1차~4차 개편을 최종 QA / runbook / durable docs 기준으로 닫고, 정상 top-navigation QA path와 direct `/operations` local routing diagnostic을 분리한다.

## Product Tracks

| Track | Current State | Main Surfaces | Boundary |
|---|---|---|---|
| Data Collection / Data Trust | DB-backed ingestion baseline complete | `Workspace > Ingestion`, MySQL, loaders | UI에서 provider / FRED / external source를 직접 fetch하지 않는다. Overview bounded refresh는 `app/jobs/overview_actions.py` facade만 통과한다 |
| Overview / Market Context | Production baseline plus recent sentiment / Why It Moved work complete | `Workspace > Overview` | Market context and investigation only; bounded refresh action allowed through facade; no trade signal, approval, order, registry rewrite |
| Backtest Analysis | Candidate creation plus Risk-On Momentum 5D research lane complete | `Backtest > Backtest Analysis` | 후보 source 생성 단계; final decision / monitoring governance는 후속 단계 |
| Practical Validation / Final Review | Investability evidence workflow complete through P2 / P3 and first hardening cycle | `Backtest > Practical Validation`, `Backtest > Final Review` | PASS / BLOCKER / selected-route gate는 validation evidence가 소유; sentiment overlay is context-only |
| Operations / Portfolio Monitoring | Operations Console now opens with portfolio-first status summary, evidence health strip, and priority/evidence ordered review queue, while Portfolio Monitoring remains daily-monitoring-first | `Operations > Operations Console`, `Operations > Portfolio Monitoring`, `System / Data Health` | Read-only monitoring and explicit scenario update; no live approval, broker order, account sync, auto rebalance |
| UI / Engine Boundary | Service/runtime boundary and lint baseline complete | `app/services`, `app/runtime`, `app/web` | UI handles render/session state; runtime / service owns engine dispatch, JSONL helpers, read models |

## Recently Merged Work

| Workstream | Status | Durable Notes |
|---|---|---|
| Overview Market Sentiment V1 | 1차~3차 complete | CNN Fear & Greed / AAII collect into `finance_meta.macro_series_observation`. Overview Sentiment, Practical Validation, Final Review, and Portfolio Monitoring read it as context-only market backdrop. |
| Operations Overview IA / Operations Console V2-V5 | V2 closeout complete | Operations now has a console entry, Portfolio Monitoring and System / Data Health as the only top-level Operations tabs, and disabled live trading boundary copy. Operations Overview no longer exposes archive / development-history decision tables in the operator path and now starts with Portfolio Monitoring Status plus Evidence Health before a priority/evidence ordered review queue. Closeout QA and routing diagnostic are documented in `docs/runbooks/OPERATIONS_OVERVIEW_QA.md`; Backtest Runs / Candidate Library data deletion is deferred. |
| Risk-On Momentum 5D V1/V2 | Implementation / QA complete | Daily Swing research lane added under Backtest Analysis. V2 adds ATR exit, macro ranking penalty, comparison / sensitivity / stability / trade-cause / quality-warning analysis, S&P 500 universe option. Governance connection to Practical Validation / Final Review / Portfolio Monitoring is deferred. |
| Selected Dashboard Monitoring First UX V1 | Complete | Portfolio Monitoring opens with Active Portfolio Monitoring Scenario first, while portfolio setup and strategy board sit below. Scenario results stay explicit/session-based and do not auto-write monitoring logs. |
| Overview Market Movers Second Pass / Why It Moved | Current V1 complete; period refresh V1 complete; V2 decision pending | Return / Volume rank, previous-period context, manual investigation board, keyless Google News KR RSS metadata/snippet, compact SEC metadata table. Weekly / Monthly / Yearly now expose a manual EOD price-history refresh action through the existing Overview action facade / OHLCV job boundary. No article body, filing body, AI summary, catalyst classifier, DB schema, registry, saved setup write. |
| Overview Macro Context Cockpit V1 | Complete | Overview opens with a summary-first cockpit that synthesizes existing DB-backed movers, sector breadth, futures macro thermometer, CNN / AAII sentiment, event calendar, and data-health evidence. It remains context-only and adds no provider, schema, registry, saved setup, validation gate, monitoring signal, or trading action. |
| Overview Data Health Ingestion Handoff V1 | Complete | Data Health now opens with priority-ranked stale / missing / failed / partial / due targets, exact owning collection surface guidance, alternate Overview bounded refresh surface where applicable, and read-only boundary copy. It does not execute jobs, persist an action queue, fetch providers, or write registry / saved JSONL. |
| Overview Breadth / Macro Week V1 | Complete | Sector / Industry now opens with breadth / concentration summary plus the existing latest heatmap, and Events opens with a 14-day macro week lane for FOMC / macro / earnings context. It reuses existing DB-backed snapshots only and remains context-only, with no provider, schema, registry, saved setup, validation gate, monitoring signal, or trading action. |
| Overview Source Confidence Catalog V1 | Complete | The Overview cockpit now includes a compact Source Confidence lane for prices, breadth, futures, sentiment, events, and data health source state. It reuses the same snapshots already loaded by the cockpit, exposes owner / freshness / caveat / next check, and does not add provider fetch, schema, persistence, validation, monitoring, or trading semantics. |
| Overview IA Closeout V1 | Complete | Overview now places a compact `Overview Map / Deep Tab Reading Order` between the cockpit and deep tabs. It keeps Market Context, Data Repair, and transitional Candidate Ops boundaries visible without moving Candidate Ops, adding providers, changing storage, or creating validation / monitoring / trading semantics. |
| Overview Market Context UX V3 | Complete | Market Context now opens as a summary-first cockpit: current context headline, separate data-state rail, core/supporting card hierarchy, action-oriented next check order, and secondary refresh placement. It keeps existing DB-backed read models and Overview action facade boundaries, with no provider fetch, schema, registry / saved write, validation, monitoring, or trading semantics. Direct `/overview` local first-load still has a Streamlit Page not found modal and remains a routing follow-up. |
| Overview Market Context Events Data Trust V1 | Complete | Events now reads recent 7D plus upcoming horizon rows, prioritizes FOMC / CPI / PPI / Employment / GDP over earnings in context surfaces, splits Macro Week Lane into recent major and upcoming events, and keeps Market Context event/Data Health cues compact. Local DB still lacks CPI rows for 2026-06-10 and 2026-07-14, so Macro Calendar collection or BLS `.ics` import remains a data coverage follow-up. |
| Overview Market Context Historical Analog V1 | Complete | Market Context now has a compact `과거 유사 맥락 참고` section that maps current sector leadership to a sector ETF proxy and, when price coverage is sufficient, summarizes 5D / 20D / 60D forward returns for major assets from simple SPY-relative historical anchors. It is context-only and does not create prediction, recommendation, trade signal, validation gate, Final Review, Operations monitoring, schema, provider, registry, or saved JSONL behavior. Coverage can be uneven by sector ETF; V4 turns those gaps into an explicit repair action. |
| Overview Market Context Hybrid Visual V1 | Complete | Market Context now renders as a card-light hybrid cockpit: 5-cell tape, sector pressure map, event timeline, existing evidence rows, historical analog disclosure, and source confidence disclosure. It reuses stored Overview snapshots only and does not add provider fetch, schema, persistence, registry / saved write, validation gate, monitoring signal, or trading action. |
| Overview Market Context Section Flow V1 | Complete | Market Context now keeps the top cockpit focused on headline, tape, sector pressure map, and event timeline, then renders market brief, interpretation variables, historical analog, source confidence, and boundary copy as sibling reading-flow sections. It remains DB-backed and context-only. |
| Overview Market Context Copy Density V2 | Complete | Market Context now renders `오늘의 시장 맥락` as a short 2-3 sentence narrative and tightens reading-flow typography / color density so the brief, variables, historical analog, and source confidence sections read as a sequence instead of one dense surface. It remains DB-backed and context-only. |
| Overview Market Context Analog Readability V5 | Complete | Market Context historical analog now explains the similarity rule before the table, surfaces sample / proxy median / positive-rate / worst-path summary metrics, and splits detailed rows into core assets and supporting assets. The calculation remains the existing sector ETF relative-strength analog and stays context-only. |
| Overview Market Context Analog Repair V4 | Complete | Market Context now turns historical analog `자료 부족` into an actionable gap panel with missing ETF ticker / row evidence and a `보조 갱신` OHLCV repair action through the existing Overview action facade. Source confidence also shows normal / review / missing counts and key source pills before expansion. It remains DB-backed and context-only; no new provider, schema, registry / saved write, validation, monitoring, or trading action was added. |
| Overview Market Context Supporting Flow V3 | Complete | Market Context now reframes the lower supporting flow as `다음 맥락 체크`, `참고: 과거 유사 맥락`, and `근거: 자료 기준 / 출처 상태`. Data Health is no longer a primary market-variable row; it stays available as evidence/source context. It remains DB-backed and context-only. |
| Overview Market Context Source Action Flow V1 | Complete | Market Context now renders `다음 맥락 체크` from `next_checks` instead of legacy `interpretation_cues`, with target tab, source area, reason, action, freshness, and priority visible. Source Confidence exposes review source/action hints while collapsed, historical analog shows current as-of / data window / calculation basis, and refresh assist remains a secondary collapsed action. |
| Futures Market Monitoring / Macro Thermometer | Complete | yfinance futures 1m / daily OHLCV feeds Futures Monitor and Macro Thermometer. Historical validation is point-in-time read-only context, not a prediction guarantee. |

## Completed Foundations

| Foundation | Status | Closeout |
|---|---|---|
| UI Engine Boundary Foundation / Cleanup | Complete | Service/runtime boundary and `app.services/app.runtime -> app.web` import hard-fail lint baseline are in place. |
| Investability Decision Foundation | Complete | Validation gate, storage governance, data provenance, look-through, robustness, selected monitoring, decision dossier baseline complete. |
| Phase 8 Data Evidence Expansion | Complete | Provider / macro / provenance / lifecycle evidence added for investability workflow. |
| Phase 9 Cost / Slippage / Liquidity Realism | Complete | Cost model, turnover, net-cost curve, liquidity / capacity, cost / slippage sensitivity evidence added. |
| Phase 10 Walk-forward / OOS / Regime Validation | Complete | Temporal validation, holdout, macro regime evidence added and connected to selection evidence. |
| Phase 11 Portfolio Construction Risk Controls | Complete | Concentration / overlap / exposure, risk contribution, component role / weight evidence added. |
| Phase 12 Selected Monitoring / Recheck Operations | Complete | Recheck readiness, provider evidence staleness, review signals, allocation boundary, decision dossier continuity complete. |
| Phase 13 First-Cycle Hardening Closeout | Complete | Integrated QA, gate matrix, storage audit, docs/runbook alignment, residual risk carry-forward complete. |
| Practical Validation V2 P2 / P3 | Closeout complete | Provider / macro / look-through / robustness normalization and selected monitoring handoff QA complete. |
| Documentation / AI Workspace Rebuild | Practical closeout | `.aiworkspace/note/finance` and repo-local skill/plugin source are canonical. |

## Current Documentation State

`tasks/active/` and `phases/active/` still contain retained completed boards from prior worktrees.
For now, read them as detailed work records unless the current roadmap or root handoff explicitly names them as active.

Current active phase:

- none

Current active task:

- none

Recent completed docs cleanup tasks:

- `post-merge-verification-handoff-20260607`
- `post-merge-active-state-cleanup-20260607`
- `post-merge-boundary-docs-alignment-20260607`
- `post-merge-docs-alignment-20260607`

Recent completed structure audit tasks:

- `refactor-round-closeout-20260607`
- `backtest-compare-components-split-20260607`
- `ingestion-diagnostic-facade-20260607`
- `runtime-backtest-strict-family-split-20260607`
- `runtime-backtest-real-money-split-20260607`
- `runtime-backtest-risk-on-momentum-split-20260607`
- `streamlit-ingestion-console-split-20260607`
- `overview-ingestion-action-boundary-20260607`
- `code-boundary-refactor-audit-20260607`

Retained completed boards in `phases/active/` should not be treated as newly open phase work.
Their closeout summaries live under `.aiworkspace/note/finance/phases/done/` when available.

State manifest pointers:

- task state manifest: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`
- phase state manifest: `.aiworkspace/note/finance/phases/active/STATUS_MANIFEST.md`
- post-merge handoff: `.aiworkspace/note/finance/tasks/active/post-merge-verification-handoff-20260607/HANDOFF.md`
- Refactor Round Closeout: `.aiworkspace/note/finance/tasks/active/refactor-round-closeout-20260607/AUDIT.md`
- Backtest Compare Components Split: `.aiworkspace/note/finance/tasks/active/backtest-compare-components-split-20260607/DESIGN.md`
- Ingestion Diagnostic Facade: `.aiworkspace/note/finance/tasks/active/ingestion-diagnostic-facade-20260607/DESIGN.md`
- Runtime Backtest Strict Family split: `.aiworkspace/note/finance/tasks/active/runtime-backtest-strict-family-split-20260607/DESIGN.md`
- Runtime Backtest Real-Money split: `.aiworkspace/note/finance/tasks/active/runtime-backtest-real-money-split-20260607/DESIGN.md`
- Runtime Backtest Risk-On Momentum split: `.aiworkspace/note/finance/tasks/active/runtime-backtest-risk-on-momentum-split-20260607/DESIGN.md`
- Streamlit Ingestion Console split: `.aiworkspace/note/finance/tasks/active/streamlit-ingestion-console-split-20260607/DESIGN.md`
- Overview / Ingestion action boundary: `.aiworkspace/note/finance/tasks/active/overview-ingestion-action-boundary-20260607/DESIGN.md`
- code refactor audit: `.aiworkspace/note/finance/tasks/active/code-boundary-refactor-audit-20260607/AUDIT.md`

Legacy `.note/` was removed after user approval and is no longer part of the current local state.

## Next Decisions

| Candidate | Why It Matters | Requires Approval Before |
|---|---|---|
| Backtest Compare follow-up splits | 9차 first pass moved the visual shell, but saved replay, weighted result, and strategy-specific form body still remain in `app/web/backtest_compare.py` | Moving saved replay / weighted result / strategy form sections into focused modules while preserving service/runtime boundaries |
| Large-surface second refactor round | 10차 closeout confirmed large files remain in Backtest Compare, Overview, Operations / Portfolio Monitoring runtime, and Overview services | Opening a new focused refactor round that changes module ownership or public call paths |
| Physical task / phase archive migration | `tasks/active` and `phases/active` still contain retained completed folders even though current active state is now manifest-clean | Moving folders, deleting retained boards, changing archive layout, or repairing historical links |
| Overview Why It Moved V2 | Current V1 is manual/session-only; durable metadata retention or SEC financial-statement preview needs a storage/source policy | DB schema, article/filing body handling, AI summary, catalyst classification |
| Risk-On Momentum 5D governance | Strategy is implemented as research lane but not connected to validation / monitoring daily signal policy | Practical Validation module, Final Review gate, Portfolio Monitoring signal integration |
| Overview scheduler hardening | Browser-session refresh exists; OS scheduler / launchd production operation is a separate decision | Enabling unattended scheduled collection |
| Overview historical analog expansion | V1 source-action follow-up leaves 2차 / 3차 design notes for current pattern window, as-of replay, and macro-conditioned analog pilot while keeping current calculation context-only | Adding upload/import flow, expanding sector ETF coverage, adding macro/futures/event regime conditions, CPI/FOMC event-window analogs, or strengthening PIT/survivorship/sample-quality treatment |
| UI platform split | Streamlit is workable but complex UX may eventually benefit from API + React/Next.js | Any large frontend migration or service API expansion |
| Second-cycle investability hardening | Phase 13 carry-forward material can seed another phase | Opening a new phase from carry-forward matrix |

## Work Model

| Layer | Location | Meaning |
|---|---|---|
| Phase | `.aiworkspace/note/finance/phases/active/<phase>/` | User-approved multi-task direction, design, integration owner |
| Task | `.aiworkspace/note/finance/tasks/active/<task>/` | Actual implementation, docs, QA, investigation unit |
| Research | `.aiworkspace/note/finance/researches/active/<research-id>/` | Product direction / benchmark / feature opportunity body |
| Durable Docs | `.aiworkspace/note/finance/docs/` | Stable project knowledge after implementation or approved direction |
| Root Handoff Logs | `.aiworkspace/note/finance/WORK_PROGRESS.md`, `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md` | 3~5 line milestone / decision pointers only |

## Update Rules

- Add detailed implementation history to task docs, not this roadmap.
- Keep this roadmap focused on active state, completed foundations, and next decisions.
- Update `PRODUCT_DIRECTION.md` when the product purpose or user-facing workflow changes.
- Update `PROJECT_MAP.md` when ownership boundaries or entry points change.
- Update architecture / flow / data docs when runtime, storage, or user workflow boundaries change.
- Use `docs/architecture/SYSTEM_BOUNDARIES.md` as the first checkpoint for layer / storage / product surface boundary changes.
