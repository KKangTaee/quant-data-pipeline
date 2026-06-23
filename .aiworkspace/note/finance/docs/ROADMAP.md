# Finance Roadmap

Status: Active
Last Verified: 2026-06-23

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

- Latest completed task: `.aiworkspace/note/finance/tasks/active/overview-nav-internal-lazy-load-v1-20260623/`
- 목적: `Workspace > Overview` primary tab 전환을 anchor/link navigation이 아니라 같은 브라우저 안의 내부 탭 전환으로 고치고, 첫 진입 때 무거운 `Market Context` 본문 로드를 늦춘다.
- 주요 변경: primary selector는 `st.pills` 내부 widget을 사용하되, user-provided reference처럼 plain text tabs + active red underline으로 보이게 scoped CSS를 적용한다. Query-param slug는 직접 진입 호환 입력으로만 읽고 `<a href>` navigation은 렌더링하지 않는다. Fresh Overview entry는 shell / nav / session banner만 먼저 보여주고 `시장 맥락 불러오기`를 눌렀을 때 `load_overview_macro_context_cockpit` fan-out을 실행한다.
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
| Overview Nav Internal Lazy Load V1 | Complete | Current Overview primary navigation uses an internal `st.pills` selector styled as plain text tabs with a red active underline, not rendered anchors. Query-param tab slugs remain read-only compatibility input. Fresh Overview entry defers the heavy default Market Context body until the user clicks `시장 맥락 불러오기`. |
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
| Backtest Compare follow-up splits | 9차 first pass moved the visual shell, but saved replay, weighted result, and strategy-specific form body still remain in `app/web/backtest_compare.py` | Moving saved replay / weighted result / strategy form sections into focused modules while preserving service/runtime boundaries |
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
