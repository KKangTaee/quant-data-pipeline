# Finance Roadmap

Status: Active
Last Verified: 2026-07-08

## Current State After Master Merge

현재 active phase는 없다.

현재 active task는 없다.

Latest completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-final-review-handoff-v1-20260708/`다.

- 목적: Practical Validation Flow 4가 Final Review에서 해석할 REVIEW 항목을 카테고리별 상세 문제처럼 보여 사용자가 현재 보강해야 할 항목과 최종 판단 항목을 혼동하는 문제를 줄였다.
- 주요 변경: Flow 4 main board는 `통과`, `보강 후 재검증 필요`, `실전 사용 어려움`을 먼저 보여주며, REVIEW 항목은 `Final Review 참고` handoff count로만 남긴다. REVIEW만 남은 상태는 Practical Validation 관점에서 보강 필요가 아니라 Final Review 판단으로 넘긴다.
- 이번 차수에서 하지 않은 일: Final Review evidence 화면 재구성, gate threshold 변경, registry / saved JSONL rewrite, provider ingestion, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-outcome-taxonomy-v1-20260708/`다.

- 목적: Practical Validation Flow 4가 raw status 중심으로 보여 `REVIEW`, `NEEDS_INPUT`, `BLOCKED`의 실제 행동 의미를 구분하기 어려운 문제를 줄였다.
- 주요 변경: Flow 4 criteria summary는 `통과`, `보강 후 재검증 필요`, `Final Review 판단 필요`, `실전 사용 어려움` outcome layer를 먼저 보여준다. `READY`는 통과로 읽고, `Current=REVIEW`인 input check는 `NEEDS_INPUT`으로 강등하지 않아 최신 replay / coverage review가 Final Review 판단 항목으로 남는다.
- 이번 차수에서 하지 않은 일: registry / saved JSONL rewrite, provider ingestion, 새 DB schema, Final Review selected-route threshold 전면 변경, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-required-taxonomy-refactor-v1-20260708/`다.

- 목적: Practical Validation의 1차 필수 검증에서 같은 검증이 여러 module 안에 반복되는 문제를 줄이고, `validation_efficacy`를 방법론 검증 전용으로 축소했다.
- 주요 변경: `app/services/backtest_validation_efficacy.py`는 walk-forward / OOS / regime split row만 생성한다. module planner / board registry / workspace는 `Validation Method Strength`와 `Stress / Robustness`를 분리해 보여주며, Flow 4 copy는 `검증 방법론`, `강건성`, `실전성 진단`처럼 사용자-facing 업무명으로 정리했다. Final Review gate와 evidence read model도 `Validation Method Strength` label과 method-only blocker 문구를 사용한다.
- 이번 차수에서 하지 않은 일: gate threshold 강화, registry / saved JSONL rewrite, provider ingestion, 새 DB schema, 새 live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-required-taxonomy-audit-v1-20260708/`다.

- 목적: Practical Validation의 1차 필수 검증이 여러 module 안에서 같은 검증을 반복 소유하는 문제를 막기 위해 현재 audit row inventory와 `check_id -> owner_module` taxonomy를 정리했다.
- 주요 결론: `validation_efficacy`는 source / replay / benchmark / provider / PIT / survivorship / robustness를 다시 보는 umbrella audit이 아니라 walk-forward / OOS / regime split 중심의 `validation_method_strength`로 축소해야 한다. replay, benchmark, PIT, survivorship, provider freshness, stress/robustness는 각각 owner module이 단독 소유해야 한다.
- 이번 차수에서 하지 않은 일: Python service refactor, gate threshold 변경, Flow 4 UI 변경, registry / saved JSONL rewrite, provider ingestion, Final Review selected-route policy 변경, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/backtest-symbol-resolver-v1-20260708/`다.

- 목적: Backtest Quality / Value Factor Readiness에서 stale/missing price ticker가 단순 가격 지연인지 ticker-change symbol identity 문제인지 구분하고, 사용자가 검토 후 repair를 실행할 수 있게 한다.
- 주요 변경: `nyse_symbol_lifecycle(event_type=ticker_change)` 기반 resolver / active repair 저장 path를 추가했다. 후보는 same CIK, lifecycle coverage, source reference, resolved ticker price freshness를 `evidence_factors`로 설명하고 LOW confidence는 자동 반영하지 않는다. Active repair는 source ticker를 rewrite하지 않고 collection ticker만 resolved symbol로 바꾸며, price refresh plan/details에 `source_range` / `resolved_range` / `split_status` metadata-only PIT split contract를 남긴다. Factor Readiness는 후보쌍 / 신뢰도 / 기간 경계 / 다음 행동을 보여주고 repair 후 readiness 재확인과 백테스트 재실행을 안내한다.
- 이번 차수에서 하지 않은 일: official corporate-action feed 신규 수집, 실제 old/new ticker price series stitching, universe 선정 정책 변경, registry / saved JSONL rewrite, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/backtest-factor-readiness-action-ui-v1-20260707/`다.

- 목적: Quality / Value strict form의 Factor Readiness가 내부 진단값 중심으로 보여 사용자가 `무엇이 문제인지 / 어떤 티커인지 / 어떻게 해결할지`를 바로 알기 어려운 문제를 줄인다.
- 주요 변경: strict preset 안내는 후보군 선택 정보만 짧게 남기고, Factor Readiness React panel은 문제 / 영향받는 티커 / 해결 방법 / action button 중심 contract로 바꿨다. 가격 문제는 Backtest OHLCV refresh service, statement gap은 targeted Extended Statement Refresh로 연결하고, provider/source gap은 반복 업데이트가 아니라 수동 확인 문제로 표시한다.
- 이번 차수에서 하지 않은 일: OHLCV provider 교체, DB schema 변경, universe 선정 정책 변경, factor/runtime 계산 변경, registry / saved JSONL rewrite, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/backtest-coverage-provider-gap-refresh-v1-20260707/`다.

- 목적: Backtest Data Trust의 Coverage 최신화가 provider no-data / persistent source gap 심볼을 계속 해결 가능한 버튼으로 보여주는 문제를 막는다.
- 주요 변경: price refresh plan이 명백한 provider/source gap 심볼을 refresh 대상에서 제외하고, 실행 후 rows_written=0 + unresolved 심볼이 남으면 같은 화면에서 retry action card를 다시 렌더링하지 않는다.
- 이번 차수에서 하지 않은 일: OHLCV provider 교체, DB schema 변경, universe 선정 정책 변경, factor/runtime 결과 계산 변경, registry / saved JSONL rewrite, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-action-steps-v3-20260707/`다.

- 목적: Practical Validation Flow 4의 `해결 방법`이 여러 Next Action을 한 줄에 이어 붙인 설명처럼 보이지 않게 하고, 사용자가 처리 순서를 바로 읽을 수 있게 했다.
- 주요 변경: `resolution_guide`에 UI용 `action_steps` list를 추가하고, Flow 4 criteria card가 이를 번호형 목록으로 렌더링한다. non-PASS audit row의 `Next Action`은 구체 단계로 우선 노출하고, 기준별 기본 action guide는 보강 / 재검증 같은 후속 단계로 붙인다.
- 이번 차수에서 하지 않은 일: validation threshold 변경, module severity 변경, replay 실행 로직 변경, provider ingestion orchestration 변경, registry / saved JSONL rewrite, Final Review selected-route 정책 변경, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-action-guide-v2-20260707/`다.

- 목적: Practical Validation Flow 4의 상세 카드가 위치 안내에 머물지 않고, 사용자가 실제로 무엇을 보강하면 통과되는지 판단할 수 있게 했다.
- 주요 변경: `resolution_guide`에 `통과 기준`을 추가하고, criteria card를 `검증한 것 / 해결해야 할 항목 / 해결 방법 / 통과 기준 / 위치` 구조로 재구성했다. Audit row의 non-PASS `Criteria`와 `Next Action`은 계속 우선 사용하며, 위치는 실행 위치 보조 정보로 낮췄다.
- 이번 차수에서 하지 않은 일: validation threshold 변경, replay 실행 로직 변경, provider ingestion orchestration 변경, registry / saved JSONL rewrite, Final Review selected-route 정책 변경, live approval / broker order / auto rebalance 의미 추가.

Latest completed task는 `.aiworkspace/note/finance/tasks/active/backtest-quarterly-productionization-v1-20260708/`다.

- 목적: Strict quarterly Quality / Value / Quality+Value를 prototype 표시가 아닌 formal `Strict Quarterly` 후보로 정식화하되, quarterly filing lag와 statement shadow coverage 민감성은 post-run Factor Readiness에서 확인하게 한다.
- 주요 변경: strict quarterly runtime wrappers가 annual-like investability / benchmark / promotion / guardrail inputs를 받도록 확장했고, result bundle에 statement shadow coverage metadata를 남긴다. post-run Factor Readiness는 실제 실행 결과 기준으로 가격 / statement 문제 티커와 해결 버튼을 보여준다. Strategy catalog / runner catalog / evidence inventory / forms / compare / history helper는 user-facing `Strict Quarterly` label을 사용하고 legacy `_prototype` key는 replay 호환용으로 유지한다.
- 이번 차수에서 하지 않은 일: official historical index membership ingestion, provider no-data 대체 소스 구축, live approval / broker order / auto rebalance, 기존 saved/run history JSONL 재작성.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-resolution-guide-v1-20260707/`다.

- 목적: Practical Validation Flow 4의 `보강 위치`가 단순 위치 문자열이라 사용자가 실제 부족 항목과 해야 할 일을 파악하기 어려운 문제를 해결했다.
- 주요 변경: workspace read model에 `resolution_guide`를 추가하고, Flow 4 criteria card를 `검증한 것 / 부족한 것 또는 확인할 것 / 해야 할 일 / 확인 위치` 구조로 렌더링한다. Data Coverage / Validation Method Strength 등 audit row가 있는 기준은 non-PASS `Criteria`와 `Next Action`을 우선 사용한다. 위치명은 `Flow4 > 데이터 > 데이터 품질 / 편향 통제 상세`, `Flow4 > Provider / Data 보강 액션`처럼 실제 화면 경로로 세분화했다.
- 이번 차수에서 하지 않은 일: validation threshold 변경, replay 실행 로직 변경, provider ingestion orchestration 변경, registry / saved JSONL rewrite, Final Review selected-route 정책 변경, live approval / broker order / auto rebalance 의미 추가.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/backtest-pit-universe-v1-20260707/`다.

- 목적: Quality / Value strict coverage가 현재 market-cap Top-N을 과거 전체 기간에 고정해 쓰는 look-ahead / survivorship 위험을 줄이고, 사용자가 2016년부터 실행할 때 당시 월말 기준 근사 universe를 선택할 수 있게 한다.
- 주요 변경: `finance_meta.equity_universe_snapshot` / `equity_universe_member` schema와 builder / upsert / loader를 추가했다. Strict Quality / Value / Quality+Value annual and quarterly strict runners는 `PIT Monthly Snapshot Universe`를 선택하면 사전 저장 monthly membership을 읽고, 각 리밸런싱일에는 가장 가까운 이전 snapshot을 적용한다. Backtest Single Strategy와 Portfolio Mix Builder strict form은 `PIT Monthly Snapshot Universe`만 visible option으로 노출한다. Static Managed Research와 Historical Dynamic PIT는 기존 saved payload / old run 호환용 legacy internal path로만 유지한다.
- 이번 차수에서 하지 않은 일: paid official historical Russell / S&P membership ingestion, float-adjusted market cap feed, broker execution, live approval / order / auto rebalance, 기존 Strategy selector의 React 이관.
- 중요한 한계: V1 PIT monthly universe는 DB 가격과 latest-known statement shares 기반 근사 large-cap membership이다. 공식 지수 편입 이력이나 완전한 historical float-adjusted market cap이 필요하면 별도 provider / collector phase가 필요하다.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/backtest-strategy-form-cleanup-v1-20260707/`다.

- 목적: 사용자가 요청한 맥락대로 기존 Strategy dropdown과 strategy-specific Streamlit form switching은 유지하고, 과하게 추가된 Strategy Detail panel을 제거한 뒤 각 전략 form 내부의 preset / preflight / advanced input 설명만 정리했다.
- 주요 변경: active Strategy Detail service / React component / render path를 제거했다. strict preset 설명은 `현재 기준 / 주의 / 업데이트 방법` compact model로 바꿨고, Quality / Value strict form은 `데이터 준비 기준`, compact preset basis, Price Freshness Preflight 순서로 읽히게 했다. Equal Weight / ETF-like form은 기존 layout을 유지하고 혼란스러운 `runtime wrapper` copy만 줄였으며, Portfolio Mix Builder는 Streamlit-owned strict settings와 같은 preset helper를 계속 사용한다.
- 이번 차수에서 하지 않은 일: Strategy selector / actual form controls의 React 이관, strategy runtime / result bundle / registry / saved JSONL / Practical Validation gate policy 변경, provider 수집 로직 변경, live approval / broker order / auto rebalance 의미 추가.

Earlier completed task record는 `.aiworkspace/note/finance/tasks/active/backtest-strategy-detail-react-v1-20260707/`다. 이 작업의 Price Freshness Preflight asset fix는 유지하지만, Strategy Detail panel은 latest cleanup task에서 제거되어 active product flow가 아니다.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow4-labels-v1-20260706/`다.

- 목적: Practical Validation Flow 4가 내부 `Workbench` / audit taxonomy가 아니라 사용자가 찾을 수 있는 `검증 기준 상세` 화면으로 읽히게 했다.
- 주요 변경: Flow 4 title을 `검증 기준 상세`으로 바꾸고, category title emphasis를 강화했으며, `보강 위치`를 `검증 기준 상세 · 데이터 품질 / Provider 보강`, `검증 기준 상세 · 검증 강도 / 강건성`, `Flow 2 · 실전 재검증 실행` 같은 화면 기준 위치명으로 통일했다.
- 이번 차수에서 하지 않은 일: validation threshold 변경, replay 실행 로직 변경, provider 수집 로직 변경, registry / saved JSONL rewrite, Final Review selected-route 정책 변경, live approval / broker order / auto rebalance 의미 추가.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-flow3-conclusion-summary-v1-20260706/`다.

- 목적: Practical Validation Flow 3을 Fix Queue / 보강 가이드가 아니라 `검증 결론` compact summary로 읽히게 했다.
- 주요 변경: Flow 3은 Final Review 이동 가능 / 보류와 카테고리별 통과 / 실패 / 확인 필요만 요약한다. `현재 문제 / 완료 기준 / 보강 위치` 같은 상세 설명과 검증 모듈 기술 상세는 Flow 4로 이동했다. 반복 안전 문구도 Flow 3 React surface에서 제거했다.
- 이번 차수에서 하지 않은 일: validation threshold 변경, selected-route policy 변경, provider 수집 실행, registry / saved JSONL rewrite, live approval / broker order / auto rebalance 의미 추가.

Earlier completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-category-results-v1-20260706/`다.

- 목적: Practical Validation Flow 4가 Final Review 이동 기준판이 아니라 카테고리별 검증 결과로 읽히게 하고, 후보 특성과 무관한 검증이 universal blocker처럼 보이는 문제를 줄였다.
- 주요 변경: workspace read model이 `Source & Replay`, `Data Quality / Bias Control`, `Comparison Validity`, `Realism / Tradability`, `Validation Method Strength`, `Stress / Robustness`, `Portfolio Construction`, `Conditional Evidence` category를 만든다. `selected_route_preflight`는 `Final Review 이동 요약`으로 분리했다. stress / robustness missing evidence는 기본 REVIEW, construction risk는 ETF-like 또는 weighted mix에만 적용, sentiment risk-on/off overlay는 macro gate status에서 제외했다.
- 이번 차수에서 하지 않은 일: provider 수집 실행, registry / saved JSONL rewrite, Final Review selected-route 저장 정책 변경, live approval / broker order / auto rebalance 의미 추가.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-issue-summary-v1-20260706/`다.

- 목적: Practical Validation Flow 3 / Flow 4의 blocker 설명이 가이드 문단처럼 보이지 않게 하고, 사용자가 실제로 무엇을 보강해야 하는지 바로 읽게 했다.
- 주요 변경: workspace read model이 module별 `현재 문제 / 완료 기준 / 보강 위치 / 영향` field와 criteria group별 `통과한 기준 / 남은 문제 / 판정` summary를 만들었다. 이때 Flow 3 React surface는 이슈 큐로 표시했으나, 최신 `practical-validation-flow3-conclusion-summary-v1-20260706`에서 visible UI는 `검증 결론` 요약으로 축소했고 상세 보강 field는 Flow 4로 내렸다. `NEEDS_INPUT`, `NOT_RUN`, `REVIEW` 같은 raw status는 first-read label이 아니라 기술 tag로 낮춘다.
- 변경하지 않은 경계: validation threshold / gate policy 의미, registry / saved JSONL rewrite, provider 수집, replay 실행 로직, Final Review handoff persistence, live approval / broker order / auto rebalance.

Previous completed task는 `.aiworkspace/note/finance/tasks/active/practical-validation-readable-fix-queue-v1-20260706/`다.

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

- Latest completed task: `.aiworkspace/note/finance/tasks/active/backtest-second-stage-visibility-v1-20260705/`
- 목적: Backtest Analysis의 Data Trust / Handoff가 2차 Practical Validation review focus를 1차 상세 검토처럼 보여주는 혼선을 줄인다.
- 주요 변경: Data Trust는 excluded ticker / malformed price row 같은 직접 데이터 이슈만 상세 표시하고, `meta["warnings"]` 기반 review focus는 2차 전달 count / 위치 안내로 낮췄다. Handoff / Policy Signals도 2차 상세 판단 문구를 반복하지 않는다.
- 이번 차수에서 하지 않은 일: source registration write, Practical Validation review queue 저장, registry / saved JSONL / strategy runtime / gate threshold 변경.
- Recent Overview cleanup task: `.aiworkspace/note/finance/tasks/active/overview-legacy-dashboard-removal-v17-v24-20260625/`
- Previous completed structure task: `.aiworkspace/note/finance/tasks/active/overview-tab-helper-extraction-v11-v16-20260625/`
- 목적: Overview primary tab entrypoint가 직접 legacy helper를 호출하지 않도록, Market Context / Events / Futures Macro / Market Movers / Sentiment 각각의 tab-local helper bridge를 만든다.
- 주요 변경: `app/web/overview/{market_context,events,futures_macro,market_movers,sentiment}_helpers.py`를 추가하고 active tab entry modules가 semantic helper functions를 호출하게 했다.
- 이번 차수에서 하지 않은 일: low-level helper body 전체 물리 이동, `legacy_dashboard.py` 삭제, provider / schema / registry / saved JSONL 변경, validation / monitoring / trading semantics 추가.
- Recent completed task: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-refresh-state-v1-20260624/`
- 목적: `Workspace > Overview > Futures Macro` 탭이 저장된 선물 일봉 최신일을 stale하게 보여주지 않도록 DB 최신 marker와 화면 snapshot cache 경계를 정리한다.
- 주요 변경: `load_overview_futures_macro_snapshot` cache key에 latest stored 1D futures candle marker를 포함했다. `Futures Macro` 탭 상단에는 `일봉 매크로 갱신`과 `최신 데이터 다시 읽기` controls를 추가해 daily collection과 cache reload를 탭 안에서 직접 실행할 수 있게 했다.
- 이번 차수에서 하지 않은 일: futures daily collector provider 교체, OS scheduler / automation cadence 변경, DB schema / registry / saved JSONL 변경, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed task: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-mixed-substates-v1-20260624/`
- 목적: `Workspace > Overview > Futures Macro`에서 자주 보이는 `혼재된 매크로 흐름`을 억지 directional signal로 바꾸지 않고, 현재 선물 일봉 점수만으로 어떤 혼재인지 더 읽히게 한다.
- 주요 변경: `generate_market_interpretation`은 기존 directional scenario rule이 모두 빗나간 fallback에서만 mixed subtype을 계산한다. 상위 scenario는 `혼재된 매크로 흐름`으로 유지해 historical validation compatibility를 보존하고, summary에는 `sub_scenario`, `regime_hint`, `mixed_reason`을 추가한다. Overview brief hero는 하위 맥락을 보조 라벨로 보여준다.
- 이번 차수에서 하지 않은 일: FRED `T10Y3M` / `VIXCLS` / `BAA10Y`, real yield, breakeven inflation 같은 macro source score 추가, provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed task: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-tab-split-v1-20260624/`
- 목적: `Workspace > Overview`의 기본 진입 화면인 `Market Context`에서 무거운 futures macro historical validation을 분리하고, 별도 `Futures Macro` primary tab에서 선물 매크로 진단을 관리한다.
- 주요 변경: Overview primary tabs는 `Market Context`, `Market Movers`, `Futures Macro`, `Sentiment`, `Events` 순서다. `Market Context` helper는 기본 `include_futures_macro=False`, `include_historical_analog=False`로 cockpit을 만들며 movement / breadth / sentiment / events / data 중심의 light brief만 즉시 로드한다. `Market Context` renderer에서는 historical analog controls / reading flow / repair action을 제외했다. `Futures Macro` tab은 저장된 선물 일봉 snapshot과 historical validation이 필요한 상세 진단을 소유한다. `nyse_price_history` 최신 raw date 조회는 `MAX(date)` 대신 `ORDER BY date DESC LIMIT 1` read path로 바꿨다.
- 이번 차수에서 하지 않은 일: futures validation 결과 DB 저장 테이블 추가, provider / schema / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed task: `.aiworkspace/note/finance/tasks/active/overview-market-context-load-gate-removal-v1-20260624/`
- 목적: `Workspace > Overview > Market Context`의 `시장 맥락 불러오기` gate를 제거하고, 전처럼 기본 시장 맥락 본문이 즉시 렌더링되게 되돌린다.
- 주요 변경: explicit load button / loaded-tab session state / lazy body gate를 제거했다. Internal `st.pills` text-tab underline selector와 no-anchor switching은 유지한다. Cold timing 기준 느린 구간은 `load_overview_macro_context_cockpit`의 snapshot fan-out, 특히 futures macro validation으로 확인했다.
- 이번 차수에서 하지 않은 일: futures macro validation 최적화, loader 구조 분리, provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed task: `.aiworkspace/note/finance/tasks/active/overview-nav-internal-lazy-load-v1-20260623/`
- 목적: `Workspace > Overview` primary tab 전환을 anchor/link navigation이 아니라 같은 브라우저 안의 내부 탭 전환으로 고치고, 첫 진입 때 무거운 `Market Context` 본문 로드를 늦춘다.
- 주요 변경: primary selector는 `st.pills` 내부 widget을 사용하되, user-provided reference처럼 plain text tabs + active red underline으로 보이게 scoped CSS를 적용한다. Query-param slug는 직접 진입 호환 입력으로만 읽고 `<a href>` navigation은 렌더링하지 않는다. 이 작업의 explicit load gate는 `overview-market-context-load-gate-removal-v1-20260624`에서 제거됐다.
- 이번 차수에서 하지 않은 일: Market Context 내부 old source label 흡수, futures / sector service 또는 renderer helper 물리 삭제, provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed task: `.aiworkspace/note/finance/tasks/active/overview-primary-nav-pill-v1-20260623/`
- 목적: `Workspace > Overview`의 네 개 primary tab을 기본 Streamlit segmented/radio 위젯 느낌이 아니라 제품형 compact navigation으로 보이게 했다.
- 주요 변경: primary selector를 Korean-first compact pill nav로 바꾸고, English secondary label과 `?overview_tab=market-movers` 같은 query-param slug selection을 추가했다. 이 anchor 기반 visual polish는 이후 `overview-nav-internal-lazy-load-v1-20260623`에서 내부 widget selector로 대체됐다.
- 이번 차수에서 하지 않은 일: Market Context 내부 old source label 흡수, futures / sector service 또는 renderer helper 물리 삭제, provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Earlier completed task: `.aiworkspace/note/finance/tasks/active/overview-primary-tab-soft-remove-v1-20260623/`
- 목적: `Workspace > Overview`에서 사용 가치가 선명하지 않은 `Futures Monitor`와 `Sector / Industry` standalone tab을 primary navigation에서 제거하고, Overview를 더 작고 확실한 market context entry로 좁혔다.
- 주요 변경: primary selector / lazy dispatch는 `Market Context`, `Market Movers`, `Sentiment`, `Events`만 노출한다. 기존 session 또는 deep-link 값이 `Futures Monitor` / `Sector / Industry`를 가리키면 `Market Context`로 fallback한다. IA guide와 durable docs도 현재 primary tab 목록에 맞췄다.
- 이번 차수에서 하지 않은 일: futures / sector service 또는 renderer helper 물리 삭제, provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Earlier completed task: `.aiworkspace/note/finance/tasks/active/futures-monitor-workbench-v1_1-20260623/`
- 목적: `Workspace > Overview > Futures Monitor`의 Workbench V1 후속으로, prototype-like lower evidence / validation / refresh 영역을 제품형 read-only market context 흐름으로 정리했다.
- 주요 변경: context bar는 상태만 요약하고, `자료 갱신` module이 1분봉 / 일봉 매크로 / 화면 reload / 확인 방식을 소유한다. `근거 해석 / 원본 데이터`는 `현재 근거 상태 -> 과거 점검 요약 -> 자료 관리 -> 원본 표` 순서로 읽히며, raw scenario / relationship / sensitivity tables는 접힌 원본 상세로 낮췄다.
- 이번 차수에서 하지 않은 일: provider / schema / DB / registry / saved JSONL 변경, UI render 중 external provider fetch, trading signal / 추천 / validation gate / monitoring signal / broker order / auto rebalance semantics 추가.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/futures-monitor-workbench-v1_1-20260623/`
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/futures-monitor-workbench-layout-v1-20260623/`
- 목적: `Workspace > Overview > Futures Monitor`를 form/card 느낌에서 compact workbench 기본 화면으로 재구성했다.
- 주요 변경: Workbench context bar, compact watch strip, market brief hero, weekly flow lane, chart workspace question을 도입하고 symbol edit / refresh setting / raw evidence / provider diagnostics를 낮췄다.
- 이번 차수에서 하지 않은 일: provider/schema/registry/saved write, live trading/order/recommendation/monitoring signal semantics.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-source-refresh-ux-v21-20260622/`
- 목적: `Workspace > Overview > Market Context`의 V19 Macro meaning / gradient 보정으로, 핵심 자산 비교와 Macro 조건 결과 비교 matrix의 양수 / 음수 색상 구분을 더 분명히 하고, 조건에는 쓰지 않은 Macro 배경 값이 어떤 상태를 뜻하는지 바로 읽히게 했다.
- 주요 변경: Historical analog / Macro conditioned comparison matrix cells는 median return 또는 delta 방향과 크기를 green / red gradient로 표시한다. Reference-only Macro backdrop cards는 T10Y3M / VIXCLS / BAA10Y 현재 값 옆에 `양의 금리곡선`, `변동성 주의`, `신용위험 안정권` 같은 상태와 해당 값의 의미 문장을 보여준다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-intersection-v18-20260622/`
- 목적: `Workspace > Overview > Market Context`의 V18 Macro intersection 보정으로, Macro 조건 표본이 GLD 조건을 먼저 적용한 뒤 금리선물을 적용하는 순서 의존 결과처럼 보이는 문제를 정리했다.
- 주요 변경: Macro conditioned analog 모델은 broad count, GLD 같은 상태 count, 금리선물 같은 상태 count, futures 계산 가능 count, 두 조건 교집합 count를 별도로 제공한다. Macro basis bar는 `기본 유사 맥락 기준` / `GLD 같은 상태` / `금리선물 같은 상태` / `두 조건 모두`로 표시하고, 최종 조건 후 결과는 두 조건 모두 현재와 같았던 교집합 표본으로 계산한다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-polish-v17-20260621/`
- 목적: `Workspace > Overview > Market Context`의 V17 Macro polish 보정으로, Macro 조건 축소 bar의 `37회`, `6회`가 정확히 어떤 GLD / 금리선물 상태를 뜻하는지 바로 읽히지 않고 `현재 Macro 배경 참고`가 긴 텍스트 덩어리처럼 보이는 문제를 정리했다.
- 주요 변경: Macro basis bar는 `XLY가 SPY 대비 5D 기준 비슷하게 강했던 구간` -> `GLD가 현재처럼 중립권이었던 과거 구간` -> `ZN=F/ZB=F가 현재처럼 금리 압력이 엇갈렸던 구간`처럼 각 단계의 조건 뜻을 먼저 보여준다. `조건에는 쓰지 않은 Macro 배경`은 T10Y3M / VIXCLS / BAA10Y를 한글 상태 badge, 현재 값, broad 표본 내 같은 상태 비율 bar, compact source 설명 순서로 보여준다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-matrix-v16-20260621/`
- 목적: `Workspace > Overview > Market Context`의 V16 Macro matrix 보정으로, V15 Macro 조건 비교가 여전히 wide table / verbose source text 중심의 prototype-like UI로 보이는 문제를 정리했다.
- 주요 변경: Macro sample flow는 historical analog와 같은 basis bar로 표시하고, 결과 변화는 자산 x `기본 / 조건 후 / 변화` matrix로 렌더링한다. 긴 조건 source 원문은 접힌 상세로 낮추고, 현재 Macro 배경은 `금리곡선` / `변동성` / `신용스프레드` 한글 라벨을 우선 표시한다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-labels-v15-20260621/`
- 목적: `Workspace > Overview > Market Context`의 V15 Macro labels 보정으로, `Macro 조건 후 결과 변화`에서 `37회`, `6회`, `같은 상태`가 무엇을 뜻하는지 기본 사용자가 바로 이해하기 어려운 문제를 정리했다.
- 주요 변경: Macro sample flow를 `기본 유사 맥락` -> `GLD 조건 적용` -> `금리선물 조건 적용` 단계로 명명하고, 각 단계가 broad anchor pool에서 어떤 표본을 남겼는지 문장으로 설명한다. `현재 Macro 배경 참고`는 T10Y3M / VIXCLS / BAA10Y의 한글 지표 설명과 broad sample 중 같은 상태 횟수를 함께 표시한다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-clarity-v14-20260621/`
- 목적: `Workspace > Overview > Market Context`의 V14 Macro clarity 보정으로, `Macro 조건 비교`가 기본 유사 맥락 조건과 Macro 추가 조건을 섞어 보여주고, `Macro 조건 포함 핵심 자산` 표가 더 나은 예측표처럼 오해될 수 있던 문제를 정리했다.
- 주요 변경: `Sector ETF vs SPY relative strength`는 broad sample을 만드는 기본 유사 맥락 기준으로 분리하고, GLD / Rate Pressure futures는 Macro 추가 조건으로 표시한다. Macro 섹션은 sample narrowing, broad vs conditioned 결과 변화, 현재 Macro 배경(T10Y3M / VIXCLS / BAA10Y), 접힌 상세 / 원본 통계 순서로 읽는다. Historical analog matrix는 median return 방향과 크기에 따라 색상 농도를 조절하고, sector pressure map 수익률은 소수점 둘째 자리까지 표시한다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-flow-alignment-v13-20260621/`
- 목적: `Workspace > Overview > Market Context`의 V13 흐름 보정으로, 상단 섹터 압력 지도와 `참고: 과거 유사 맥락`이 서로 다른 섹터를 기준으로 보이고 섹터 지도 / analog / macro 비교가 여전히 prototype-like guide UI처럼 읽히는 문제를 정리했다.
- 주요 변경: latest historical analog는 상단 Market Context의 visible daily sector leadership snapshot을 재사용한다. Selected as-of는 선택일 daily sector snapshot을 쓰고, pattern window는 sector source가 아니라 similarity window만 바꾼다. Sector pressure map은 provider sector alias를 canonical 11개 섹터로 normalize하고 전체를 균일 tile로 표시한다. Historical analog는 `먼저 볼 점` / `주의할 점` / `시장 배경 요약` guide block을 기본 화면에서 제거하고, sector ETF / SPY / QQQ / TLT / GLD를 하나의 핵심 비교 matrix로 보여준다. Broad analog rows가 없으면 Macro 조건 비교는 숨겨 dashed prototype UI를 만들지 않는다. V14에서 Macro 조건 비교는 broad-vs-conditioned 결과 변화와 현재 Macro 배경 중심으로 다시 정리됐다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-usability-v12-20260621/`
- 목적: `Workspace > Overview > Market Context`의 historical analog V12 보정으로, 실제 계산 기준일이 선택일보다 오래된 경우에도 보강 경로가 없고 기준 / 조건 / 표본 / 자산 통계가 반복 table-first로 보이는 문제를 정리했다.
- 주요 변경: selected as-of common daily price basis mismatch를 limiting symbols 대상 bounded OHLCV refresh action으로 연결했다. 기준 영역은 compact basis summary와 접힌 계산 경계 상세로 줄였고, 핵심 자산은 5D / 20D / 60D matrix로 먼저 읽으며 보조 자산은 시장 배경 요약, 원본 표는 `상세 통계` disclosure로 낮췄다. V13에서 latest historical analog 기준 섹터는 상단 visible sector leadership snapshot과 정렬되고, 시장 배경 요약은 sector ETF / SPY / QQQ / TLT / GLD 핵심 matrix로 흡수됐다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-macro-ux-v11-20260621/`
- 목적: `Workspace > Overview > Market Context`의 historical analog / Macro 조건 비교 UX 보정으로, 과거 유사 맥락과 Macro 조건 포함 비교가 카드 안 카드 / prototype-like payload dump처럼 보이는 문제를 정리했다.
- 주요 변경: historical analog 기준 영역을 wide basis bar로 바꾸고, 설명을 `현재 기준` / `유사 사례 조건` / `표본 품질`로 나눴다. 결과 해석은 `먼저 볼 점` / `주의할 점`으로 분리했고, Macro 조건 포함 비교는 broad analog의 sibling section으로 분리해 funnel, broad-vs-conditioned lanes, 조건 역할 그룹, dimension audit을 보여준다. V12에서 historical analog broad 영역은 다시 compact basis summary와 matrix-first outcome으로 보정됐다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-basis-clarity-v10-20260620/`
- 목적: `Workspace > Overview > Market Context`의 historical analog 기준일 UX 보정으로, 선택 기준일과 실제 계산 기준일이 다를 때 날짜가 무시된 것처럼 보이는 문제를 정리했다.
- 주요 변경: historical analog service model에 requested / effective as-of alignment, limiting symbols, basis warning을 추가했다. UI는 `요청 기준일`과 `실제 계산 기준일`을 나눠 보여주고, Macro 조건 포함 비교는 broad sample -> GLD 배경 -> 금리선물 압력 funnel로 읽게 했다. V11에서 이 표시 구조는 card stack에서 basis bar / separate Macro comparison section으로 재정리됐다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-session-basis-v9-20260620/`
- 목적: `Workspace > Overview > Market Context`의 V8 후속으로, 미국장 휴장 / 주말 / 장외 시간에도 `오늘의 시장 브리프`처럼 보이고 장중 snapshot age 때문에 보강 이슈가 과하게 보이는 문제를 정리했다.
- 주요 변경: 기존 NYSE session helper를 Market Context cockpit에 전달해 `market_session` basis payload를 만들었다. 장중에는 `오늘의 시장 브리프`, 휴장에는 `마지막 거래일 시장 브리프`, 장 시작 전 / 장 종료 후에는 현재 세션 기준 브리프로 표시한다. 휴장 중에는 마지막 trading session date를 기준일로 고정하고, stale / due intraday elapsed age만으로 `현재 이슈만 보강` action을 만들지 않는다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-source-actionability-v8-20260620/`
- 목적: `Workspace > Overview > Market Context`의 V7 후속으로, `현재 이슈만 보강`에서 제외되는 Events와 관리 메타인 Data Health가 계속 `자료 확인 필요`처럼 남아 사용자를 헷갈리게 하는 문제를 정리했다.
- 주요 변경: source confidence에 `source_role` / `actionability` / `counts_for_status`를 추가해 direct brief source, reference context, management meta를 분리했다. Top `자료 상태`, source confidence summary, source ledger는 보강 가능한 자료만 unresolved로 세며, Events estimate caveat는 `참고 제한`, Data Health는 `관리 메타`로 표시한다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-smart-refresh-v7-20260620/`
- 목적: `Workspace > Overview > Market Context`의 V6 후속으로, Events caveat가 상단 시장 브리프 결론처럼 보이고 `필요 자료 일괄 보강`이 현재 이슈와 무관한 전체 job 실행처럼 보인다는 사용자 피드백을 정리했다.
- 주요 변경: `brief_rows`는 움직임, 확산, Futures/Macro 배경 3행으로 고정하고 Events는 event timeline / source evidence / `refresh_plan.excluded_items`로 낮췄다. 새 `refresh_plan`은 보강 가능 / 일부 보강 / 보강 제외를 분리하며, 기본 버튼은 `현재 이슈만 보강`으로 현재 action ids만 실행한다. 기존 전체 7개 job 실행은 `전체 Market Context 자료 보강` fallback으로 유지하고, refresh 결과는 raw job rows 전에 브리프 반영 요약을 먼저 보여준다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-context-absorption-v6-20260620/`
- 목적: `Workspace > Overview > Market Context`의 V5 `브리프 신뢰도`가 여전히 가이드/주의사항처럼 보이고 시장맥락 자체의 필요 정보로 읽히지 않는다는 사용자 피드백에 따라, 별도 신뢰도 섹션을 제거하고 의미 있는 부분만 시장 브리프 결론으로 흡수했다. V7에서 Events caveat는 상단 brief conclusion에서 다시 내려갔다.
- 주요 변경: `brief_caveats` / `브리프 신뢰도`를 제거했다. V6의 optional `이벤트 배경`은 V7부터 default brief row가 아니며, Futures / OHLCV data-health 항목이 있을 때만 `Futures/Macro 배경`을 `장중 macro 해석 보류`로 낮춘다. 상세 source / freshness는 하단 `근거: 자료 기준 / 출처 상태`가 소유한다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-confidence-v5-20260620/`
- 목적: `Workspace > Overview > Market Context`의 V4 보정 후 Events / 자료 신뢰도 caveat가 `오늘의 시장 브리프` 결론처럼 보인다는 사용자 피드백에 따라, 시장 브리프와 브리프 읽기 강도 근거를 분리했다. V6에서 이 별도 섹션은 제거되고 필요한 정보만 브리프 결론에 흡수됐다.
- 주요 변경: V5에서는 `brief_rows`를 움직임, 확산, Futures/Macro 배경의 3행 market story로 유지하고, Events / 자료 기준을 별도 `brief_caveats` / `브리프 신뢰도` 영역에서 보여줬다. V6부터 `brief_caveats`는 제거됐다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-findings-integration-v4-20260620/`
- 목적: `Workspace > Overview > Market Context`의 V3 `맥락 검토 결과`가 가격 움직임 / Futures-Macro를 상단 브리프와 중복해서 보여준다는 사용자 피드백에 따라, 중복 findings rail을 없애고 Events / 자료 신뢰도 caveat만 `오늘의 시장 브리프` 안으로 통합했다. V5에서 이 caveat는 `브리프 신뢰도`로 다시 분리됐다.
- 주요 변경: V4에서는 `brief_rows`가 움직임, 확산, Futures/Macro 배경, 이벤트 caveat, 자료 신뢰도 caveat의 5행 흐름이 됐다. V5부터 `brief_rows`는 3행 market story, `brief_caveats`는 별도 confidence row로 읽는다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-context-findings-v3-20260620/`
- 목적: `Workspace > Overview > Market Context`의 `다음 맥락 체크`가 여전히 사용자가 직접 다른 탭을 확인하라는 checklist처럼 보인다는 사용자 피드백에 따라, Market Context가 이미 읽은 보조 맥락의 결론을 보여주도록 바꿨다.
- 주요 변경: user-facing `다음 맥락 체크`를 `맥락 검토 결과`로 전환하고, 가격 움직임 / Futures-Macro / Events / 자료 신뢰도 caveat를 `결론`, `해석 영향`, `자료 기준` 행으로 표시한다. V4에서 이 rail은 기본 화면에서 제거되고 Events / 자료 신뢰도 caveat만 브리프에 흡수됐다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-brief-flow-redesign-v2-20260620/`
- 목적: `Workspace > Overview > Market Context` V1 UX 보정이 여전히 카드 재배치처럼 보인다는 사용자 피드백에 따라, Market Context를 wide brief lane / next-check rail / transparent reading sections로 다시 정리했다.
- 주요 변경: `시장 브리프` rows를 cockpit 안의 `오늘의 시장 브리프`로 흡수하고, `다음 맥락 체크`를 card grid 대신 priority / observation / reason / action rail로 표시하며, `Macro 조건 포함 pilot`은 UI상 `Macro 조건 포함 비교`로 broad vs conditioned sample 차이를 먼저 읽게 했다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, FRED / events / sentiment hard conditioning, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- Previous completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-futures-conditioned-analog-v3b-20260618/`
- 목적: `Workspace > Overview > Market Context`의 3차-B historical analog 개선으로 3차-A `Macro 조건 포함 pilot`에 stored futures daily OHLCV 기반 Rate Pressure proxy 조건 1개를 추가했다.
- 실제 사용 조건: 필수 sector ETF vs SPY relative strength, GLD price proxy safe-haven / gold context, `ZN=F` / `ZB=F` Rate Pressure futures proxy.
- 이번 차수에서 하지 않은 일: FRED 2Y/10Y 수집 또는 조건화, events / sentiment historical conditioning, 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, full PIT sector universe storage, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- sample quality: 20D Browser QA 기준 broad sample 69회 중 GLD + futures 조건 포함 sample 1회로 줄어 `REVIEW` 상태였다. UI는 broad sample, Macro 조건 sample, sample quality, sample reduction reason, used / insufficient / excluded conditions를 함께 표시한다.
- Recent completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-macro-conditioned-analog-pilot-v1-20260618/`
- 목적: `Workspace > Overview > Market Context`의 3차-A historical analog 개선으로 기존 broad analog와 별도인 `Macro 조건 포함 pilot` 영역과 GLD price proxy condition을 추가했다.
- Recent completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-analog-asof-window-v2-20260618/`
- 목적: `Workspace > Overview > Market Context`의 2차 historical analog 개선으로 `참고: 과거 유사 맥락`에 latest / 과거 기준 시점 replay와 5D / 20D / monthly pattern window controls를 추가했다.
- 이번 차수에서 하지 않은 일: 새 provider / DB schema / loader / persistence path, registry / saved JSONL write, UI render 중 external fetch, macro-conditioned analog, full PIT sector universe storage, Backtest / Practical Validation / Final Review / Operations core logic, trade signal / 추천 / validation or monitoring signal.
- as-of replay 판정: 기존 DB만으로는 current universe / sector metadata와 selected-as-of DB prices 기반 bounded replay가 가능하다. 과거 당시 universe / sector classification / market-cap snapshot을 보장하는 full PIT replay는 후속 storage/read path 승인이 필요하다.
- Recent completed product task: `.aiworkspace/note/finance/tasks/active/overview-market-context-source-action-flow-v1-20260618/`
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

Recent Backtest strategy contract work retained from `backtest-dev`:

- `risk-parity-dual-momentum-5b-20260610`: Backtest 5B로 Risk Parity Trend와 Dual Momentum의 strategy runtime / result bundle 계약을 고도화했다. Risk Parity는 volatility window / eligible universe / inverse-vol weight / cash-only state / guardrail effect / low-vol overweight를, Dual Momentum은 top-N concentration / trend rejected ticker / selected count / cash proxy retention / turnover-whipsaw 해석을 result row/meta와 기존 Selection History에서 확인할 수 있게 됐다. 새 Backtest Analysis evidence / log / workbench panel, registry / saved JSONL / run history / generated artifact write, provider / FRED direct fetch, Practical Validation / Final Review / Monitoring behavior, live trading / broker order / auto rebalance는 열지 않았다.
- `global-relative-strength-5a-20260609`: Backtest 5A로 Global Relative Strength의 strategy runtime / result bundle 계약을 고도화했다. GRS는 strategy가 rebalance interval을 직접 소유하고, cash proxy / benchmark contract / excluded ticker / stale price / top-N concentration / momentum score window 정보를 result bundle meta와 기존 Selection History에서 해석할 수 있게 됐다. 새 evidence/log/workbench panel과 durable writes는 열지 않았다.
- `backtest-analysis-direction-reset-20260609`: Backtest 4차 4C로 3A~4B evidence / governance / workbench 패널을 기본 화면에서 내리고, Backtest Analysis를 전략 실행 / 비교 / 후보 생성 중심으로 되돌렸다. 2026-06-30 cleanup 이후 해당 보조 패널은 기본 Backtest Analysis render path에서 제외된 historical / auxiliary surface로 남는다.
- `etf-rerun-matrix-workbench-20260608`, `etf-current-anchor-workbench-20260608`, `etf-evidence-expansion-20260608`, `risk-on-momentum-governance-20260608`, `strict-annual-etf-bridge-20260608`, `strategy-evidence-inventory-direction-panel-20260608`: Backtest 3A~4B read-only strategy evidence / bridge / governance / ETF readiness / rerun matrix workbench records. 이 흐름은 current candidate promotion, Practical Validation result creation, provider snapshot collection, live trading / broker order / auto rebalance를 열지 않는 retained work record다.

## Product Tracks

| Track | Current State | Main Surfaces | Boundary |
|---|---|---|---|
| Data Collection / Data Trust | DB-backed ingestion baseline complete | `Workspace > Ingestion`, MySQL, loaders | UI에서 provider / FRED / external source를 직접 fetch하지 않는다. Overview bounded refresh는 `app/jobs/overview_actions.py` facade만 통과한다 |
| Overview / Market Context | Production baseline plus recent sentiment / Why It Moved work complete | `Workspace > Overview` | Market context and investigation only; bounded refresh action allowed through facade; no trade signal, approval, order, registry rewrite |
| Backtest Analysis | Candidate creation plus compact Korean-first stage navigation cleanup complete | `Backtest > Backtest Analysis` | 후보 source 생성 단계; final decision / monitoring governance는 후속 단계 |
| Practical Validation / Final Review | Investability evidence workflow complete through P2 / P3 and first hardening cycle | `Backtest > Practical Validation`, `Backtest > Final Review` | PASS / BLOCKER / selected-route gate는 validation evidence가 소유; sentiment overlay is context-only |
| Operations / Portfolio Monitoring | Operations Console now opens with portfolio-first status summary, evidence health strip, and priority/evidence ordered review queue, while Portfolio Monitoring remains daily-monitoring-first | `Operations > Operations Console`, `Operations > Portfolio Monitoring`, `System / Data Health` | Read-only monitoring and explicit scenario update; no live approval, broker order, account sync, auto rebalance |
| UI / Engine Boundary | Service/runtime boundary and lint baseline complete | `app/services`, `app/runtime`, `app/web` | UI handles render/session state; runtime / service owns engine dispatch, JSONL helpers, read models |

## Recently Merged Work

| Workstream | Status | Durable Notes |
|---|---|---|
| Overview Legacy Dashboard Removal V17-V24 | Complete | `app/web/overview/legacy_dashboard.py` was physically removed after remaining helper ownership moved into tab-local helper modules. `app/web/overview_dashboard.py` now keeps explicit compatibility exports only, while active page / tab / helper ownership lives under `app/web/overview/`. |
| Overview Tab Helper Extraction V11-V16 | Complete | Market Context, Events, Futures Macro, Market Movers, and Sentiment primary tab entry modules now call tab-local helper bridges instead of importing `legacy_dashboard.py` directly. |
| Overview Legacy Cleanup V6-V10 | Complete | Overview navigation moved to `app/web/overview/navigation.py`, IA read-model ownership moved to `app/services/overview/ia.py`, confirmed unused standalone wrappers / Candidate Ops helpers were removed, and guard tests prevent reintroduction. |
| Overview Structure Split V2-V5 | Complete | Overview primary tab modules own tab-level orchestration, `app/web/overview/components/` component surfaces and `app/services/overview/` service surfaces were introduced, and boundary guard contracts protect active page / tab / component / service ownership. |
| Overview Tab Module Split V1 | Complete | `app/web/overview_dashboard.py` became a compatibility wrapper, active Overview shell moved to `app/web/overview/page.py`, and primary tab entry modules were added for Market Context, Market Movers, Futures Macro, Sentiment, and Events. |
| Overview Market Context Load Gate Removal V1 | Complete | Current Overview keeps the internal text-tab underline selector but removes the explicit `시장 맥락 불러오기` gate. Market Context renders immediately when selected. Cold timing shows the slow path is the cockpit snapshot fan-out, especially futures macro validation. |
| Overview Nav Internal Lazy Load V1 | Superseded | This replaced anchor navigation with internal `st.pills` text tabs and added a first-load Market Context gate. The internal no-anchor navigation remains, but the explicit load gate was removed by Overview Market Context Load Gate Removal V1. |
| Overview Primary Nav Pill V1 | Superseded | This first visual polish rendered a compact custom anchor nav with Korean primary labels, English secondary labels, and query-param tab slugs. It was replaced by Overview Nav Internal Lazy Load V1 because tab switching must stay inside the current browser session rather than behave as link navigation. |
| Overview Primary Tab Soft Remove V1 | Complete | Current Overview primary tabs are Market Context, Market Movers, Sentiment, and Events. Futures Monitor and Sector / Industry standalone tabs are soft-removed from primary navigation, with stale selected values falling back to Market Context. Futures / sector services and helper renderers are retained for later cleanup or repurpose decision. |
| Overview IA Cleanup V22 | Complete | Superseded by Overview Primary Tab Soft Remove V1 for current primary tab membership. V22 demoted Data Health to Market Context source / refresh evidence plus Operations / Ingestion ownership and removed Candidate Ops from the Overview render path, while still retaining Futures Monitor and Sector / Industry at that time. Registry / saved data and Backtest / Operations core workflows are unchanged. |
| Overview Market Context Source Refresh UX V21 | Complete | Market Context source evidence now reads as `자료 상태 요약 -> 시장 브리프 직접 자료 -> 참고 / 관리 자료 -> 보강 판단`, and no-action refresh states use a compact no-action panel plus secondary full refresh instead of a prototype-like disabled action. Refresh action ids and data boundaries are unchanged. |
| Overview Market Context Macro Meaning Gradient V19 | Complete | Historical analog and Macro conditioned comparison matrix cells now use clearer green/red gradients based on median return or delta direction and magnitude. Reference-only T10Y3M / VIXCLS / BAA10Y backdrop cards now pair the current numeric value with Korean state meaning such as positive yield curve, volatility watch, and contained credit spread, without changing hard conditioning or data boundaries. |
| Overview Market Context Macro Intersection V18 | Complete | Macro conditioned comparison now reports broad sample, GLD same-state sample, Rate Pressure futures same-state sample, futures-computable sample, and the final GLD ∩ futures intersection separately. The visible basis bar reads as `기본 / GLD 같은 상태 / 금리선물 같은 상태 / 두 조건 모두`, avoiding an order-dependent funnel interpretation. |
| Overview Market Context Macro Polish V17 | Complete | Macro conditioned comparison now shows the meaning of each narrowing step inside the basis bar: broad sector ETF vs SPY analog pool, current-like GLD bucket, then current-like ZN=F / ZB=F rate-pressure bucket. Reference-only T10Y3M / VIXCLS / BAA10Y backdrop now renders as Korean state badges, current value, same-state ratio bars, and compact source labels. |
| Overview Market Context Macro Matrix V16 | Complete | Macro conditioned comparison now uses the same visual language as historical analog: a basis bar for broad -> GLD -> futures narrowing, a compact asset x `기본 / 조건 후 / 변화` matrix, collapsed verbose condition source details, and Korean-first labels for current Macro backdrop. |
| Overview Market Context Macro Labels V15 | Complete | Macro conditioned comparison now names the visible narrowing stages as broad basis, GLD condition, and rate-pressure futures condition. It explains `81회 -> 37회 -> 6회` as broad anchors narrowed by current-like GLD and futures states, and current Macro backdrop cards include Korean descriptions plus broad-sample same-state counts. |
| Overview Market Sentiment V1 | 1차~3차 complete | CNN Fear & Greed / AAII collect into `finance_meta.macro_series_observation`. Overview Sentiment, Practical Validation, Final Review, and Portfolio Monitoring read it as context-only market backdrop. |
| Operations Overview IA / Operations Console V2-V5 | V2 closeout complete | Operations now has a console entry, Portfolio Monitoring and System / Data Health as the only top-level Operations tabs, and disabled live trading boundary copy. Operations Overview no longer exposes archive / development-history decision tables in the operator path and now starts with Portfolio Monitoring Status plus Evidence Health before a priority/evidence ordered review queue. Closeout QA and routing diagnostic are documented in `docs/runbooks/OPERATIONS_OVERVIEW_QA.md`; Backtest Runs / Candidate Library data deletion is deferred. |
| Risk Parity / Dual Momentum 5B | Complete | Risk Parity Trend now exposes volatility window, eligible universe, inverse-vol weights, cash-only reasons, guardrail cash-only state, and low-vol overweight diagnostics. Dual Momentum now retains trend-rejected top-N slots as cash proxy and exposes selected / rejected / unfilled counts, cash proxy return, concentration, and selection-change / whipsaw diagnostics. Both reuse existing Selection History and result bundle meta without adding a new panel. |
| Global Relative Strength 5A | Complete | GRS strategy cadence now lives in strategy runtime, not duplicated period-row slicing. Cash proxy, benchmark, excluded ticker, stale price, top-N concentration, rebalance interval, and momentum window metadata flow to the result bundle and Selection History without new evidence/log/workbench panels or durable writes. |
| Backtest Entry Cleanup Tabs V1 | Complete | Backtest entry removes the top guide expander, strategy capability helper expander, and bottom research reference board from the default render path. The 3-stage workflow selector now uses Korean-first `st.pills` text tabs with red active underline. |
| Backtest Analysis Direction Reset 4C | Complete | Backtest Analysis returned to execution-first strategy run / comparison / candidate creation. Reference help and 3A-4B evidence / governance / ETF workbench panels are now historical / auxiliary surfaces outside the default Backtest Analysis render path. |
| Risk-On Momentum 5D V1/V2 | Implementation / QA complete | Daily Swing research lane added under Backtest Analysis. V2 adds ATR exit, macro ranking penalty, comparison / sensitivity / stability / trade-cause / quality-warning analysis, S&P 500 universe option. Governance connection to Practical Validation / Final Review / Portfolio Monitoring is deferred. |
| Selected Dashboard Monitoring First UX V1 | Complete | Portfolio Monitoring opens with Active Portfolio Monitoring Scenario first, while portfolio setup and strategy board sit below. Scenario results stay explicit/session-based and do not auto-write monitoring logs. |
| Overview Market Movers Second Pass / Why It Moved | Current V1 complete; period refresh V1 complete; V2 decision pending | Return / Volume rank, previous-period context, manual investigation board, keyless Google News KR RSS metadata/snippet, compact SEC metadata table. Weekly / Monthly / Yearly now expose a manual EOD price-history refresh action through the existing Overview action facade / OHLCV job boundary. No article body, filing body, AI summary, catalyst classifier, DB schema, registry, saved setup write. |
| Overview Macro Context Cockpit V1 | Complete | Overview opens with a summary-first cockpit that synthesizes existing DB-backed movers, sector breadth, futures macro thermometer, CNN / AAII sentiment, event calendar, and data-health evidence. It remains context-only and adds no provider, schema, registry, saved setup, validation gate, monitoring signal, or trading action. |
| Overview Data Health Ingestion Handoff V1 | Superseded as primary Overview tab | The read model remains a historical / helper artifact, but V22 removes `Data Health` from Overview top-level navigation. Market Context source / refresh evidence and Operations / Ingestion now own the user-facing data-health path. |
| Overview Breadth / Macro Week V1 | Complete | Sector / Industry now opens with breadth / concentration summary plus the existing latest heatmap, and Events opens with a 14-day macro week lane for FOMC / macro / earnings context. It reuses existing DB-backed snapshots only and remains context-only, with no provider, schema, registry, saved setup, validation gate, monitoring signal, or trading action. |
| Overview Source Confidence Catalog V1 | Complete | The Overview cockpit now includes a compact Source Confidence lane for prices, breadth, futures, sentiment, events, and data health source state. It reuses the same snapshots already loaded by the cockpit, exposes owner / freshness / caveat / next check, and does not add provider fetch, schema, persistence, validation, monitoring, or trading semantics. |
| Overview IA Closeout V1 | Superseded by V22 | V1 made Market Context / Data Repair / transitional Candidate Ops boundaries visible. V22 completes the approved IA cleanup by removing Candidate Ops from Overview and demoting Data Health out of primary Overview tabs. |
| Overview Market Context Brief Flow Redesign V2 | Complete | Market Context now absorbs `시장 브리프` rows into the top `오늘의 시장 브리프` lane, renders `다음 맥락 체크` as a priority / observation / reason / action rail instead of a card grid, and shows `Macro 조건 포함 비교` as broad vs conditioned sample context. It remains DB-backed and context-only with no provider fetch, schema, registry / saved write, validation, monitoring, or trading semantics. |
| Overview Market Context Macro Clarity V14 | Complete | Macro conditioned comparison now separates the broad basis from additional Macro conditions, shows broad-vs-conditioned result deltas before raw tables, surfaces T10Y3M / VIXCLS / BAA10Y as current Macro backdrop rather than hidden preview labels, and keeps Events / sentiment deferred. Matrix cells use median-return strength coloring and sector pressure returns display two decimal places. |
| Overview Market Context Flow Alignment V13 | Complete | Latest historical analog now follows the same visible daily sector leadership snapshot as the top Market Context view, while selected as-of uses the selected daily sector basis. Sector pressure renders the canonical 11-sector map with equal tiles, and historical analog removes default guide blocks in favor of one sector ETF / SPY / QQQ / TLT / GLD core comparison matrix. Macro comparison stays compact and is hidden when broad analog rows are unavailable. |
| Overview Market Context Analog Usability V12 | Complete | Historical analog now connects stale selected-as-of common daily price basis to a bounded OHLCV refresh action for limiting ETF symbols. The broad analog section reads as compact basis summary, collapsed calculation details, method line, summary strip, core 5D / 20D / 60D outcome matrix, support asset summary, and collapsed detailed tables. It remains DB-backed and context-only. |
| Overview Market Context Analog / Macro UX V11 | Complete | Historical analog now renders as an analysis flow: controls directly precede the analog section, requested/effective basis values sit in a wide basis bar, the similarity method is split into `현재 기준` / `유사 사례 조건` / `표본 품질`, and Macro conditioned comparison is a separate sibling section with funnel, broad-vs-conditioned lanes, condition-role groups, and dimension audit. It remains DB-backed and context-only. |
| Overview Market Context Analog Basis Clarity V10 | Complete | Historical analog now separates requested basis date from actual calculation date when common DB daily price coverage is older. Selected dates such as 2026-06-18 show the effective 2026-05-29 calculation date, limiting symbols, and no-post-basis-price boundary; Macro comparison reads as broad sample -> GLD backdrop -> rate-pressure futures backdrop. |
| Overview Market Context Session Basis V9 | Complete | Market Context now reads the existing US market session state before naming the brief. During open trading it can show `오늘의 시장 브리프`; during weekends / holidays it shows `마지막 거래일 시장 브리프` with the previous trading date as basis and does not create current refresh actions only because intraday snapshot age elapsed while the market was closed. |
| Overview Market Context Source Actionability V8 | Complete | Market Context now separates source confidence into actionable brief sources, reference limitations, and management meta. `현재 이슈만 보강` exclusions such as Events estimate caveats no longer remain as unresolved `자료 확인 필요`, and Data Health is shown as `관리 메타` rather than a market-context source issue. |
| Overview Market Context Smart Refresh V7 | Complete | Market Context keeps the default brief to movement, breadth, and Futures/Macro only. Events caveats are excluded from the brief and shown as non-actionable refresh exclusions unless future cause-analysis logic is approved. `refresh_plan` now separates resolvable, partial, and non-actionable items; `현재 이슈만 보강` runs only current action ids and `전체 Market Context 자료 보강` remains a fallback. |
| Overview Market Context Brief Context Absorption V6 | Complete | Market Context removed the separate `브리프 신뢰도` guide section and no longer returns `brief_caveats`. Events / data-source limits are absorbed only when they change the market brief: optional `이벤트 배경` shows whether events are weak direct-cause evidence, and Futures / OHLCV freshness can lower `Futures/Macro 배경` to `장중 macro 해석 보류`. Source details remain in the evidence disclosure. |
| Overview Market Context Brief Confidence V5 | Complete | Market Context keeps `오늘의 시장 브리프` to movement, breadth, and Futures/Macro background, while Events / data caveats now render as a separate `브리프 신뢰도` section that adjusts reading strength rather than acting as market conclusions. `context_findings` / `next_checks` remain compatibility payloads only. |
| Overview Market Context Brief Findings Integration V4 | Complete | Market Context removed the default V3 `맥락 검토 결과` rail and temporarily absorbed Events / 자료 신뢰도 caveat into `오늘의 시장 브리프`; V5 later split those caveats into `브리프 신뢰도`. Price movement and Futures / Macro remain in the main brief/headline, avoiding duplicate P1/P2 reading. `context_findings` / `next_checks` remain compatibility payloads only. |
| Overview Market Context Context Findings V3 | Complete | Market Context converted `다음 맥락 체크` from an action checklist into `context_findings` conclusions for price movement, Futures / Macro, Events, and data-health caveat. V4 removed the default findings rail; V5 briefly rendered Events / data-source notes as brief confidence; V6 removed that guide section and absorbs only interpretation-changing limits into the market brief. |
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
| Overview Market Context Analog As-Of Window V2 | Complete | Market Context historical analog now has 기준 시점 and 패턴 기간 controls. It can replay latest or a selected as-of date using existing DB prices plus current universe / sector metadata, and supports 5D / 20D / monthly pattern windows while keeping the existing distribution table. Full PIT sector membership / metadata replay remains a storage/read-path approval item. |
| Overview Market Context Macro Dimension Audit V3C | Complete | Market Context `Macro 조건 포함 pilot` now includes `맥락 차원 상태`, showing actual hard conditions, stored FRED `T10Y3M` / `VIXCLS` / `BAA10Y` availability and bucket preview counts, plus event / sentiment annotation or deferred reasons. It remains context-only and does not add FRED / event / sentiment hard filtering. |
| Overview Market Context Futures-Conditioned Analog V3B | Complete | Market Context `Macro 조건 포함 pilot` now keeps GLD context and adds one stored futures daily OHLCV Rate Pressure proxy condition using `ZN=F` / `ZB=F`. The condition is bounded by selected as-of / anchor date, shows used or insufficient state, and remains context-only. |
| Overview Market Context Macro-Conditioned Analog Pilot V1 | Complete | Market Context historical analog separates the original broad analog from a `Macro 조건 포함 pilot`. 3차-A introduced GLD price proxy context and sample quality display; 3차-B extended it with the stored futures Rate Pressure proxy; 3차-C adds dimension availability / preview audit without applying FRED / events / sentiment as hard filters. |
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
| Backtest package refactor follow-up | V2-V8 moved Backtest runtime, stores/read models, Single Strategy forms, Portfolio Mix Builder, Practical Validation, and Final Review into packages. Remaining follow-up is smaller cleanup of transitional shared helpers such as `backtest_common.py`, not another broad same-name module split | Moving remaining shared helper ownership or public call paths |
| Large-surface second refactor round | 10차 closeout confirmed large files remain in Backtest Compare, Overview, Operations / Portfolio Monitoring runtime, and Overview services | Opening a new focused refactor round that changes module ownership or public call paths |
| Physical task / phase archive migration | `tasks/active` and `phases/active` still contain retained completed folders even though current active state is now manifest-clean | Moving folders, deleting retained boards, changing archive layout, or repairing historical links |
| Overview Why It Moved V2 | Current V1 is manual/session-only; durable metadata retention or SEC financial-statement preview needs a storage/source policy | DB schema, article/filing body handling, AI summary, catalyst classification |
| Risk-On Momentum 5D governance | Strategy is implemented as research lane but not connected to validation / monitoring daily signal policy | Practical Validation module, Final Review gate, Portfolio Monitoring signal integration |
| Overview scheduler hardening | Browser-session refresh exists; OS scheduler / launchd production operation is a separate decision | Enabling unattended scheduled collection |
| Overview historical analog expansion | 2차 supports latest / selected as-of bounded replay and 5D / 20D / monthly pattern windows using current universe metadata plus DB prices. 3차-A adds GLD context; 3차-B adds one stored futures daily OHLCV Rate Pressure proxy condition; 3차-C shows macro dimension availability / preview status for FRED, events, and sentiment without hard filtering | Adding upload/import flow, full PIT sector universe / metadata storage, expanding sector ETF coverage, CPI/FOMC event-window analogs, events/sentiment conditioning, FRED rates collection, safe-haven futures variants beyond the current Rate Pressure proxy, or strengthening PIT/survivorship/sample-quality treatment |
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
