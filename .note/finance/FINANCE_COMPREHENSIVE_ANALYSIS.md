# Finance Comprehensive Analysis

## 문서 목적
이 문서는 아래 기존 문서들을 종합한 `finance` 패키지의 상세 분석 문서다.

- `finance/docs/FINANCE_PACKAGE_ANALYSIS.md`
- `finance/docs/FINANCE_DB_DATA_AUDIT.md`
- 현재 워크스페이스의 실제 코드

이 문서는 이후 대화에서 `finance` 패키지의 현재 상태를 이해하는 기준 문서로 사용하기 위한 것이다.

- 범위 포함: `finance` 패키지 전체
- 범위 제외: `financial_advisor`
- 기준 시점: 2026-03-11

---

## 1. 전체 요약

현재 `finance` 패키지는 하나의 단일 라이브러리라기보다 아래 두 축이 함께 들어 있는 초기 단계 퀀트 리서치 시스템에 가깝다.

1. 데이터 인프라 축
   - NYSE 유니버스 수집
   - 자산 메타데이터 수집
   - 가격/재무/팩터 DB 적재
   - 상세 재무제표 라벨/값 수집
2. 전략 리서치 축
   - 시계열 전처리
   - 전략 시뮬레이션
   - 성과 분석 및 시각화

즉, 이 패키지는 "데이터 수집기"와 "백테스트 프레임워크"가 같은 패키지 안에 공존하는 구조다.

---

## 2. 기존 문서와 이번 종합 문서의 관계

### `FINANCE_PACKAGE_ANALYSIS.md`가 다루는 것
- 패키지 레이어 구조
- 각 스크립트의 역할
- 전략/엔진/변환 흐름

### `FINANCE_DB_DATA_AUDIT.md`가 다루는 것
- 어떤 DB와 테이블이 생성되는지
- 어떤 데이터가 실제로 수집/적재되는지
- 퀀트 관점에서 어떤 데이터가 추가로 필요한지

### 이번 문서가 추가로 다루는 것
- 코드 기준으로 재검증한 실제 구조
- 패키지의 중심 인터페이스와 실행 순서
- 데이터 흐름과 DB 흐름의 연결 구조
- 현재 설계의 강점, 리스크, 구조적 갭
- 향후 리팩터링과 확장 우선순위

---

## 3. 패키지의 실질적 아키텍처

현재 구조를 가장 자연스럽게 표현하면 아래와 같다.

```text
외부 데이터 소스
  - yfinance
  - NYSE 웹페이지
  - EDGAR

      |
      v

Data Collection / Persistence
  - finance/data/*
  - MySQL

      |
      v

Loader / Runtime Read Path
  - finance/loaders/*

      |
      v

Research / Backtest Processing
  - finance/transform.py
  - finance/engine.py
  - finance/strategy.py

      |
      v

Analysis / Presentation
  - finance/performance.py
  - finance/display.py
  - finance/visualize.py
```

이 구조는 레이어 분리가 완전히 나쁘지 않다. 다만 중요한 점은 현재 **데이터 적재 파이프라인과 전략 파이프라인이 부분적으로만 연결돼 있다**는 것이다.

예를 들어:

- 가격/재무/팩터는 DB 적재 경로가 존재한다.
- 그리고 이제 `finance/loaders/*`와 `*_from_db` 샘플 entrypoint를 통해 DB 기반 실행 경로도 생겼다.
- 최근에는 DB 기반 sample 경로가 direct path와 같은 indicator warmup 순서를 따르도록 보강되었다.
- direct-fetch sample path는 reference / comparison 용도로 유지되고,
  DB-backed path는 loader/runtime 및 향후 UI handoff 기준 경로로 정리되고 있다.
- 최근에는 runtime cleanup backlog를 Phase 3 문서로 분리했고,
  Phase 4 UI가 직접 호출할 최소 runtime function 방향도 strategy-specific DB wrapper 기준으로 정리되기 시작했다.
- 이어서 user-facing 입력도 최소화하는 방향으로 정리되었고,
  첫 전략 실행 UI는 우선 `전략 + 유니버스 + 기간` 중심 입력 세트로 시작하는 것이 권장된다.
- 또한 결과 반환은 `result_df` 단일 반환 대신
  `summary_df`, `chart_df`, `meta`를 포함한 단순 result bundle 형태로 handoff하는 방향이 권장된다.
- Phase 4의 첫 UI 구조는 메인 Streamlit 앱 하나를 유지하되,
  수집 탭과 백테스트 탭을 분리하고 내부 코드를 탭별/속성별 모듈로 나누는 방향으로 정리되었다.
- 현재 구현 기준으로 메인 앱에는 이미 `Ingestion` / `Backtest` 탭 골격이 들어갔고,
  백테스트 탭은 placeholder 상태에서 이후 runtime wrapper와 첫 실행 화면을 기다리는 단계다.
- 첫 public runtime boundary는 `app/web/runtime/backtest.py`의
  `run_equal_weight_backtest_from_db(...)`와 `build_backtest_result_bundle(...)` 조합으로 열렸다.
- 즉 UI는 `sample.py`나 `BacktestEngine` 체인을 직접 호출하지 않고,
  strategy-specific wrapper가 반환하는 result bundle을 소비하는 방향으로 정리되었다.
- 이어서 Backtest 탭에는 `Equal Weight` 전용 first-pass form이 추가되었고,
  현재는 universe / period / advanced input을 입력해 실제 DB-backed wrapper를 실행할 수 있는 상태다.
- 또한 first-pass 수준의 결과 표시로
  `summary_df`, `Total Balance` line chart, result preview table, execution meta가 연결되어 있다.
- 최근에는 이 결과 영역이
  - KPI metric row
  - `Summary / Equity Curve / Result Table / Meta`
  탭 구조로 정리되어, single-strategy 결과를 더 읽기 쉽게 보여주는 상태까지 올라왔다.
- 추가로 first-pass UI는
  - 입력 오류
  - 데이터 부재 오류
  - 일반 실행 오류
  를 구분해 표시하도록 정리되어, 사용자가 실패 원인을 더 직접적으로 이해할 수 있게 됐다.
- 이후 같은 runtime/public-boundary 패턴으로 `GTAA`, `Risk Parity Trend`, `Dual Momentum`까지 공개 전략으로 연결되었고,
  현재 `Backtest` 탭은 `Equal Weight`, `GTAA`, `Risk Parity Trend`, `Dual Momentum`을 selector 형태로 전환 실행할 수 있다.
- 또한 GTAA는 더 이상 고정 `2개월` cadence에 묶여 있지 않고,
  advanced input을 통해 signal interval을 조정할 수 있다.
- Phase 4에서는 여기서 한 단계 더 나아가,
  `Backtest` 탭 안에 `Single Strategy` / `Compare & Portfolio Builder` / `History` 구조가 추가되었고,
  최대 4개 전략 비교와 월별 weighted portfolio 결합까지 first-pass 수준으로 열렸다.
- 또한 compare mode에서도 전략별 advanced input override가 가능하도록 확장되어,
  GTAA interval, Equal Weight rebalance interval, Risk Parity volatility window, Dual Momentum top/rebalance interval을 조절할 수 있다.
- 최근에는 Backtest 탭 실행도 별도 JSONL history로 남기기 시작했으며,
  single strategy / strategy compare / weighted portfolio 실행을 구분해서 다시 조회할 수 있다.
- 그 history surface도 이후 한 단계 더 강화되어,
  run kind filter, text search, selected record drilldown까지 지원하게 되었다.
- 그리고 추가로
  recorded date range filter, metric sort, single-strategy `Run Again`
  까지 지원하게 되었다.
- 현재는 이 persistent history와 drilldown이 compare 하단에 붙어 있지 않고,
  `History` top-level tab에서 single / compare 공용 surface로 노출된다.
- 이어서 persistent history는 third-pass 수준으로 더 강화되어,
  metric threshold filter,
  single-strategy `Load Into Form`,
  stored input의 current form prefill
  까지 지원하게 되었다.
- Phase 12부터는 ETF 전략군(`GTAA`, `Risk Parity Trend`, `Dual Momentum`)에
  first-pass real-money hardening이 추가되어,
  `Minimum Price`, `Transaction Cost (bps)`, `Benchmark Ticker`를 입력할 수 있고,
  결과도 gross/net/cost/benchmark 기준으로 같이 읽을 수 있게 되었다.
- 같은 Phase 12에서 `Strict Annual Family`
  (`Quality Snapshot (Strict Annual)`, `Value Snapshot (Strict Annual)`, `Quality + Value Snapshot (Strict Annual)`)
  도 first-pass real-money hardening이 추가되어,
  annual strict single/compare/history 경로에서도
  `Minimum Price`, `Transaction Cost (bps)`, `Benchmark Ticker`와
  gross/net/cost/benchmark surface를 같은 계약으로 읽을 수 있게 되었다.
- 이어서 same shared real-money helper에 second-pass validation surface가 추가되어,
  annual strict와 ETF 전략군 모두 benchmark-relative
  - drawdown
  - rolling underperformance
  - `validation_status = normal / watch / caution`
  - `promotion_decision = real_money_candidate / production_candidate / hold`
  를 결과 화면에서 같이 읽을 수 있게 되었다.
- 그리고 strict annual family에는 optional
  `underperformance guardrail` first pass도 추가되어,
  trailing benchmark-relative excess return이 지정한 window / threshold 아래로 내려가면
  해당 rebalance는 cash로 유지하도록 실제 전략 규칙으로 연결할 수 있게 되었다.
- 이와 함께 `GTAA`의 현재 기본 preset/sample universe는
  commodity sleeve에서 `DBC` 대신 `PDBC`를 사용하도록 조정되었다.
- GTAA preset surface는 현재 기본 preset과,
  Phase 12 search에서 살아남은 주요 후보 preset들을 함께 제공한다:
  - `GTAA Universe`
  - `GTAA Universe (No Commodity + QUAL + USMV)`
  - `GTAA Universe (QQQ + XLE + IAU + TIP)`
  - `GTAA Universe (QQQ + QUAL + USMV + XLE + IAU)`
  - `GTAA Universe (U3 Commodity Candidate Base)`
  - `GTAA Universe (U1 Offensive Candidate Base)`
  - `GTAA Universe (U5 Smallcap Value Candidate Base)`
- 새 `U3 / U1 / U5` preset은 universe preset이며,
  각 preset의 caption에 현재까지 검증된 추천 contract(`top`, `interval`, `Score Horizons`)를 같이 보여준다.
- GTAA single-strategy form에서는 universe selector가 submit form 밖으로 분리되어,
  preset을 바꿀 때 `Selected tickers` preview가 즉시 다시 그려지도록 조정되었다.
- 같은 GTAA universe selector가 `Compare & Portfolio Builder`에도 확장되어,
  compare에서도 `Preset` / `Manual`을 고를 수 있고,
  현재는 `Advanced Inputs > Strategy-Specific Advanced Inputs` 안에서
  해당 전략 블록과 같이 관리되며,
  `History` / saved portfolio prefill도 같은 universe contract를 복원한다.
- `Equal Weight`도 compare에서 같은 `Preset` / `Manual` universe selector를 지원하게 되어,
  `Dividend ETFs` preset 또는 직접 입력한 ticker set을 compare 실행 / prefill / saved portfolio 경로에서 일관되게 유지한다.
- GTAA의 현재 기본 `Signal Interval`은 `1`로 rebased 되었고,
  `Single Strategy`, `Compare`, `History/Load Into Form`, sample/runtime fallback도 같은 기본값으로 정렬되었다.
- GTAA는 더 이상 고정 `1/3/6/12` 단순 평균 점수에만 묶여 있지 않고,
  사용자가 `1M / 3M / 6M / 12M` 중 실제로 쓸 horizon만 고를 수 있다.
  현재 선택된 horizon은 모두 동일 비중으로 score에 반영된다.
- 또한 GTAA risk-off contract도 first pass 수준으로 확장되어,
  `Trend Filter Window`, `Fallback Mode`, `Defensive Tickers`, `Market Regime Overlay`, `Crash Guardrail`을
  single / compare / history 경로에서 조절할 수 있게 되었다.
- Phase 12의 추가 DB-backed group search에서는
  historical comparison contract(`top=3`, `interval=2`, `month_end`, `10 bps`) 기준으로
  `QQQ + IAU + XLE` 축이 가장 강한 additive direction으로 관찰되었고,
  `QUAL` / `USMV`는 이를 보조하는 broadener 성격으로 해석되었다.
- 이후 default를 `interval=1`로 rebased 한 뒤에도,
  normalized rerun에서는 같은 방향(`QQQ + IAU + XLE`)이 여전히 가장 강한 개선 축으로 유지되었다.
- 더 넓은 GTAA manual universe 탐색에서는
  `CAGR >= 9%`와 `MDD >= -16%`를 동시에 만족하는 실전형 candidate가 여러 개 확인되었고,
  특히 `interval=3`과 `top=2/3` 조합이 강하게 작동했다.
  대표 후보는:
  - `SPY|QQQ|XLE|COMT|IAU|GLD|QUAL|USMV|TIP|TLT|IEF|LQD|VNQ|EFA|MTUM`
    - `top=2`
    - `interval=3`
    - `Score Horizons = 1/3/6`
  - `SPY|QQQ|MTUM|QUAL|USMV|VUG|VTV|RSP|IAU|XLE|TIP|TLT|IEF|LQD|VNQ|EFA`
    - `top=2`
    - `interval=3`
    - `Score Horizons = 1/3/6/12`
  - `SPY|QQQ|IWM|IWN|IWD|MTUM|QUAL|USMV|EFA|VNQ|TLT|IEF|LQD|IAU|XLE|TIP`
    - `top=3`
    - `interval=3`
    - `Score Horizons = 1/3/6/12`
- 이 hardening은 현재
  - 전략 레벨 `min_price` investability filter
  - runtime post-process turnover/cost 추정
  - benchmark overlay
  - history / prefill / compare override 왕복
  까지 구현된 상태다.
- `Load Into Form`의 현재 의미는
  single-strategy history record의 저장 입력값을
  즉시 재실행하지 않고
  현재 `Single Strategy` form으로 다시 채워 넣어
  사용자가 수정한 뒤 다시 실행할 수 있게 하는 prefill action이다.
- compare / weighted replay는 현재 저장된 context로는 fidelity를 보장하기 어려워
  아직 intentionally deferred 상태로 유지된다.
- 다만 compare history drilldown은 이후 보강되어,
  primary summary row 대신
  per-strategy summary row와
  strategy별 override / trend / market regime 설정을
  context 표로 확인할 수 있게 되었다.
- 또한 single-strategy 결과는 최고점/최저점/end marker와 `Best / Worst Period` marker,
  top/bottom period 표까지 볼 수 있고,
  compare view에서는 total return overlay, overlay end marker, strategy highlight table, focused strategy drilldown까지,
  weighted portfolio 결과에서도 같은 marker / balance-extremes / period-extremes 읽기 흐름과
  strategy contribution amount/share view까지 확인할 수 있게 되었다.
- 이후 Phase 11 first pass에서는
  `Compare & Portfolio Builder` 아래에 `Saved Portfolios` surface가 추가되어,
  현재 compare 결과와 weighted portfolio 구성을
  - 저장하고
  - 다시 compare 화면으로 불러오고
  - end-to-end로 다시 실행하는
  workflow가 열렸다.
- 이 saved portfolio는 별도 store
  `.note/finance/SAVED_PORTFOLIOS.jsonl`
  에 저장되며,
  내부적으로는
  - `compare_context`
  - `portfolio_context`
  - `source_context`
  구조를 사용한다.
- 또한 weighted portfolio 결과에도 `Meta` 탭이 추가되어
  `portfolio_name`, `portfolio_id`, `portfolio_source_kind`, `date_policy`,
  `selected_strategies`, `input_weights_percent`
  를 같이 확인할 수 있게 되었다.
- history context에도 `saved_portfolio_id` / `saved_portfolio_name`가 남도록 보강되어,
  later batch review 시 saved portfolio definition과 rerun history를 연결할 수 있다.
- 이 시점 기준으로 Phase 4의 첫 UI 실행 챕터는 실질적으로 완료 상태로 보고,
  다음 활성 챕터는 factor / fundamental 전략 진입 준비로 넘어간 상태다.
- 현재 다음 챕터의 핵심은
  snapshot-first runtime wrapper 경계를 product-facing UI 기준으로 다시 정리하고,
  첫 factor / fundamental 전략 후보를 `Value` 또는 `Quality` 쪽에서 좁히는 것이다.
- 현재 선택된 첫 전략 방향은 `Quality Snapshot Strategy`이며,
  first-pass 범위는
  - annual factor snapshot
  - monthly rebalance
  - top N selection
  - equal-weight holding
  기준으로 정리되고 있다.
- 그리고 현재 first public mode는 `broad_research`로 결정되었으며,
  broad-research quality snapshot 전략의 DB-backed sample entrypoint와
  UI-facing runtime wrapper까지 first-pass 수준으로 구현된 상태다.
- 이어서 quality strategy 전용 입력도
  `basic / advanced / hidden`
  기준으로 정리되었고,
  Backtest UI의 다섯 번째 공개 전략으로 실제 연결되었다.
- 현재 public `Quality Snapshot` 경로는
  - DB-backed price history (`nyse_price_history`)
  - broad-research factor snapshot (`nyse_factors`)
  를 함께 사용한다.
- 따라서 이 전략을 실제로 돌리기 위한 first-pass 운영 경로는
  - `Daily Market Update` 또는 OHLCV 수집
  - `Weekly Fundamental Refresh`
  조합으로 이해하는 것이 맞고,
  `Extended Statement Refresh`는 현재 public quality strategy의 필수 전제는 아니다.
- 또한 현재 public quality path는 factor coverage가 시작되는 시점보다 이른 backtest start를 주면
  초기 구간이 현금 상태로 남을 수 있으며,
  UI는 이제 첫 usable factor snapshot이 늦게 시작될 때 이를 warning으로 직접 알려준다.
- history / form prefill / compare first-pass 경로에도 quality 전략 메타가 반영되었다.
- 이어서 strict annual statement path도 sample-universe annual coverage 확장과 함께
  `Quality Snapshot (Strict Annual)` 이름의 public candidate 전략으로
  single-strategy / compare / history 흐름에 연결되었다.
- 현재 다음 설계 결정은
  strictness를 더 강화할지,
  아니면 다음 factor / fundamental 전략군으로 확장할지에 관한 것이다.
- 이후 sample-universe 기준으로
  `nyse_financial_statement_values` strict snapshot을 직접 사용하는
  statement-driven quality prototype도 first-pass 수준으로 구현되었다.
- 이 prototype은
  - `finance/data/fundamentals.py`의 statement-to-fundamentals 변환
  - `finance/data/factors.py`의 fundamentals-to-quality-factor-snapshot 변환
  - `finance/sample.py`의 `get_statement_quality_snapshot_from_db(...)`
  - `app/web/runtime/backtest.py`의 `run_statement_quality_prototype_backtest_from_db(...)`
  경로를 통해 검증된다.
- 즉 현재는 broad-research public quality path와 별도로,
  `strict statement snapshot -> normalized fundamentals -> quality factor snapshot`
  의 reusable data-layer 경로가 생긴 상태다.
- 그리고 이 strict statement quality path도 이제
  `finance/loaders/factors.py`의
  `load_statement_quality_snapshot_strict(...)`
  를 통해 loader 계층 read boundary를 가지게 되었다.
- backfill 준비 관점에서도
  `finance/loaders/financial_statements.py`의
  `load_statement_coverage_summary(...)`
  가 추가되어, symbol/freq별 strict statement usable history를 먼저 audit할 수 있게 되었다.
- 또한 현재는 broad public path를 덮어쓰지 않기 위해
  `finance_fundamental.nyse_fundamentals_statement`,
  `finance_fundamental.nyse_factors_statement`
  shadow table first-pass도 열려 있다.
- 이 shadow path는
  `nyse_financial_statement_values`
  에서 strict usable history를 읽고,
  `latest_available_for_period_end` 기준으로 normalized fundamentals / derived factors를 별도 저장한다.
- sample-universe 기준 write/read validation까지 완료되었고,
  accounting quality 계열 필드는 유의미하게 채워진다.
- 추가로 이 shadow path는 현재 broad `nyse_fundamentals`의 nearest-period `shares_outstanding`
  를 fallback으로 붙이는 first-pass 보강도 갖는다.
- 따라서 sample-universe 기준으로는 valuation 계열 `market_cap`, `per`, `pbr`도 상당 부분 채워지지만,
  이 값들은 strict statement-only가 아니라
  `statement + broad shares fallback` hybrid 의미를 가진다.
- 현재 이 경로는 public UI 전략이 아니라
  sample-universe feasibility / architecture validation 용도이며,
  초기에는 `AAPL/MSFT/GOOG` targeted backfill 기준으로 대략 `2023` 이후 구간에서만 실질적인 strict statement quality ranking이 가능했다.
- 다만 이후 annual statement collector의 period-limit semantics를
  raw `period_end` bucket이 아니라 `report_date` 우선 기준으로 고치고,
  sample-universe annual canonical refresh를 다시 수행하면서
  annual strict coverage가 `2011~2025` 수준까지 확장되었다.
- 그 결과 sample-universe annual strict statement quality prototype은
  이제 `2016-02-29`부터 실제로 투자 구간이 열리며,
  `2016-01-01 ~ 2026-03-20` 백테스트도 가능해졌다.
- 따라서 현재 bottleneck은 sample-universe annual strict path 자체가 아니라,
  이 annual strict path를 public 후보로 키울지,
  아니면 wider universe coverage를 먼저 넓힐지의 제품 판단 쪽으로 이동했다.
- 현재 구현 상태에서는 broad path와 strict annual path가 함께 존재한다:
  - `Quality Snapshot`
  - `Quality Snapshot (Strict Annual)`
- broad path는 `nyse_factors` 기반 first public research path이고,
  strict annual path는 statement ledger / shadow path 기반 public candidate이다.
- 이후 strict annual public path는 추가 최적화를 거쳐,
  백테스트 중 매 리밸런싱마다
  `nyse_financial_statement_values`를 다시 재구성하지 않고
  `nyse_factors_statement` shadow factor history를 읽는 fast runtime으로 전환되었다.
- sample-universe(`AAPL/MSFT/GOOG`) 기준으로는
  optimized strict annual runtime이
  기존 prototype rebuild 경로와 동일한
  `End Balance = 93934.6`
  결과를 내면서도,
  실행 시간은 대략
  `0.33초 vs 17.09초`
  수준으로 줄어드는 것이 확인되었다.
- 이후 UI 기본값도 분리되었다.
  - broad quality single default:
    - `Big Tech Quality Trial`
  - strict annual quality single default:
    - `US Statement Coverage 300`
- strict annual quality compare default:
  - `US Statement Coverage 100`
- 즉 strict annual path는 이제 sample-universe smoke path라기보다,
  verified US / EDGAR-friendly wider stock universe를 전제로 한 public candidate로 해석하는 편이 맞다.
- 또한 strict annual family도 한 단계 더 확장되어,
  `Value Snapshot (Strict Annual)`이
  single-strategy / compare / history / form prefill 경로에 함께 연결되었다.
- snapshot 계열 전략 결과 화면도 강화되어,
  `Selection History` 탭에서
  - first active date
  - active rebalances
  - distinct selected names
  - rebalance-level selected tickers
  를 바로 읽을 수 있다.
- 또한 wider-universe annual coverage 확장을 준비하기 위해,
  `Extended Statement Refresh`와 manual `Financial Statement Ingestion`은
  large run일 때 batch-progress 기반 live progress를 표시하도록 보강되었다.
- 이후 동작 보강으로 `Extended Statement Refresh`는
  raw statement ledger만 갱신하는 카드가 아니라,
  선택한 `freq` 기준으로 아래를 연속 실행하는 operational pipeline이 되었다.
  - raw statement collection
  - `nyse_fundamentals_statement` rebuild
  - `nyse_factors_statement` rebuild
- 그리고 first staged annual coverage run으로
  `Profile Filtered Stocks` 중 시가총액 상위 `100`개를 대상으로
  annual statement refresh + annual shadow rebuild를 수행했고,
  `100`개 입력 중 `80`개에서 strict annual coverage가 실제로 확인되었다.
- 이 결과는 annual strict path가 sample universe 밖으로도 확장 가능하다는 점을 보여주지만,
  동시에 missing symbols 대부분이 foreign issuer였기 때문에
  다음 wider-universe run은 단순 top-market-cap보다 EDGAR 친화적인 scope refinement가 필요함도 보여준다.
- 이후 stage 2에서는
  `United States` issuer + `market_cap DESC` top `300`
  범위로 annual coverage를 다시 확장했고,
  `300`개 입력 중 `297`개에서 strict annual coverage가 확인되었다.
- 즉 annual strict statement path는
  단순 sample universe를 넘어, US/EDGAR-friendly stock universe에서는
  실제 전략 후보로 볼 수 있을 정도의 coverage 기반을 갖추기 시작했다.
- 이 wider annual coverage 운용을 위해 ingestion/operator 경로에도
  `US Statement Coverage 100`,
  `US Statement Coverage 300`
  preset이 추가되어,
  annual refresh와 shadow rebuild를 반복 가능한 운영 run으로 가져가기 쉬워졌다.
- 이후 large-universe actual runtime 검증 과정에서,
  strict annual snapshot 전략은 statement coverage보다
  price input shaping이 더 큰 문제라는 점도 확인되었다.
- 기존 경로는 snapshot 전략임에도 모든 심볼의 가격 날짜를 full intersection으로 맞췄고,
  그 결과 `US Statement Coverage 300`은 실제 strategy input이
  `2025-12-31 ~ 2026-02-27`의 `3` row만 남는 상태가 되었다.
- 이를 해결하기 위해 strict annual family는
  full intersection 대신
  `union calendar + per-symbol availability`
  방식으로 price input을 재정렬하도록 보강되었다.
- 그 결과 `Quality Snapshot (Strict Annual)`의
  `US Statement Coverage 300` 경로는
  `2016-01-29 ~ 2026-03-20` 구간의 `124` monthly row를 가진 실제 전략 경로로 회복되었고,
  `first_active_date`도 `2016-01-29`로 당겨졌다.
- 이후 strict annual single-strategy UI에는
  `Price Freshness Preflight`가 추가되었다.
  이 preflight는 per-symbol latest price date 집계를 바탕으로
  common latest date / newest latest date / spread days / stale symbol count를 보여주며,
  large-universe strict annual 결과에서 final-month duplicate row가
  selection bug가 아니라 stale daily price coverage 때문인지 빠르게 구분할 수 있게 한다.
- 그리고 second pass에서는 이 preflight가 operator 대응 UX까지 확장되어,
  stale / missing symbol이 있을 때
  `Daily Market Update`에 넣을 수 있는 refresh payload를 같이 보여준다.
- 이후 `Ingestion > Manual Jobs / Inspection`에는
  `Price Stale Diagnosis` 카드도 추가되었다.
  이 카드는
  - DB latest date
  - provider read-only 재조회 (`5d`, `1mo`, `3mo`)
  - asset profile status
  를 합쳐서
  stale symbol을 아래처럼 좁혀본다.
  - `local_ingestion_gap`
  - `provider_source_gap`
  - `likely_delisted_or_symbol_changed`
  - `asset_profile_error`
  - `rate_limited_during_probe`
  - `inconclusive`
- 이 diagnosis card는 새 데이터를 쓰지 않는 read-only helper이며,
  `Price Freshness Preflight`의 yellow 상태를
  “다시 수집할 것인지 / source 문제로 볼 것인지 / symbol-status 문제로 볼 것인지”
  더 명확히 해석하기 위한 operator 도구다.
- diagnosis 결과가 `local_ingestion_gap`으로 좁혀지는 경우에만
  targeted `Daily Market Update` payload를 제안한다.
- 이어서 UI에는 `Broad vs Strict Guide`도 추가되어,
  `Quality Snapshot`,
  `Quality Snapshot (Strict Annual)`,
  `Value Snapshot (Strict Annual)`
  세 전략의 data source / timing / history / speed / best-for 차이를 직접 설명한다.
- 이후 `Quality Snapshot (Strict Annual)`의 기본 factor set도
  coverage-first 방향으로 다시 정리되었다.
  - `roe`
  - `roa`
  - `net_margin`
  - `asset_turnover`
  - `current_ratio`
- 이 변경은 strict annual wider-universe에서
  `gross_margin`, `debt_ratio` coverage가 약했던 점을 반영한 것이다.
- strict family 비교 평가 기준으로 보면,
  `Quality Snapshot (Strict Annual)`은 현재 primary strict annual public candidate이고,
  `Value Snapshot (Strict Annual)`은 secondary candidate에 가깝다.
- 이후 strict annual managed universe도 더 넓혀서
  `US Statement Coverage 500`,
  `US Statement Coverage 1000`
  preset이 추가되었다.
- 이후 DB-connected runtime / shadow coverage 재검증 결과,
  strict annual managed preset은 실제 top-N universe로 동작한다.
  - top `500` covered symbols:
    - `496 / 500`
  - top `1000` covered symbols:
    - `987 / 1000`
- 다만 wide preset이 완전히 운영 안정 상태인 것은 아니고,
  `US Statement Coverage 1000` 기준으로도
  price freshness spread가 `49d`까지 벌어질 수 있어
  preflight warning과 targeted `Daily Market Update` 대응이 여전히 중요하다.
- 이후 Phase 5에서는 strict managed preset에
  `freshness-aware backfill-to-target` 실험을 잠시 붙여 보았지만,
  historical backtest 타당성 관점에서 selected end date 기준 stale 여부로
  run 전체 universe를 미리 교체하는 것은 과하다는 결론이 났다.
- 그래서 현재 코드는 다시
  **run-level static preset + rebalance-date availability filtering**
  으로 정리되어 있다.
- 즉 `Coverage 1000`을 선택해도
  preset ticker list 자체를 실행 전에 replacement로 갈아끼우지는 않는다.
- 대신 각 월말 리밸런싱 날짜마다
  - 가격이 있는 종목
  - factor snapshot이 usable한 종목
  만 실제 후보가 된다.
- `Price Freshness Preflight`는 계속 유지되며,
  stale / missing symbol이 selected end date 근처에 있는지 보여주는
  운영/해석용 진단 레이어 역할을 한다.
- 이 설계는
  - 과거 구간에서 아직 살아 있던 종목을
    end-date stale라는 이유로 run 전체에서 제거하지 않고
  - 해당 종목이 실제로 가격을 잃는 시점부터
    자연스럽게 후보에서 빠지게 한다는 점에서
  historical backtest에 더 타당한 방향이다.
- 따라서 strict annual public default는 현재도 그대로
  - single strategy:
    - `US Statement Coverage 300`
  - compare:
    - `US Statement Coverage 100`
  으로 유지하는 것이 맞다.
- 즉 `500/1000`은 노출은 되었지만,
  현재는 staged operator preset으로 해석하는 편이 가장 정확하다.
- strict annual selection-history 해석도 한 단계 더 보강되어,
  이제 `Selection Frequency` view에서
  어떤 이름이 여러 rebalance에서 반복 선택되는지 바로 확인할 수 있다.
- strict annual family는 여기서 한 단계 더 확장되어,
  `Quality + Value Snapshot (Strict Annual)`
  first public multi-factor candidate까지 추가되었다.
- 그리고 `Value Snapshot (Strict Annual)` 자체도 later closeout에서 추가로 보강되었다.
  초기에는 valuation factor usable history가 `2021` 이후로 밀려
  `2016~2021` 구간이 사실상 현금 대기에 가까웠지만,
  statement shadow fundamentals의 `shares_outstanding` fallback을
  historical weighted-average share-count concept까지 넓히면서
  valuation factor usable history가 `2011` 수준까지 회복되었다.
- 그 결과 strict annual value 기본 factor set도
  보다 stable한 coverage-first 방향으로 정리되었다.
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
- 추가로 UI advanced input에서는
  아래 strict value factor도 선택 가능하다.
  - `fcf_yield`
  - `per`
  - `pbr`
  - `psr`
  - `pcr`
  - `pfcr`
  - `ev_ebit`
  - `por`
- 이 보강 이후 `Value Snapshot (Strict Annual)`은
  `US Statement Coverage 300` / `1000` 검증에서
  모두 `2016-01-29`부터 active하게 동작하는 것이 확인되었다.
- first-pass 검증 기준으로 이 multi-factor candidate는
  `US Statement Coverage 100`에서
  - `3.569s`
  - `End Balance = 24778.9`
  - `CAGR = 9.36%`
  - `Sharpe Ratio = 0.7048`
  수준을 보였다.
- 마지막으로 operator 반복 경로도 더 정리되어,
  `run_strict_annual_shadow_refresh(...)`
  helper를 통해
  annual statement refresh ->
  statement fundamentals shadow rebuild ->
  statement factors shadow rebuild
  순서를 하나의 maintenance flow로 재사용할 수 있게 되었다.
- large-universe snapshot 전략의 date-shaping도 이후 한 번 더 보강되었다.
  기존 union-calendar path는 symbol별 마지막 available date를 그대로 보존해서,
  `month_end` 전략에서도 `2026-02-03`, `2026-03-17` 같은 symbol-specific row가
  결과 테이블에 남을 수 있었다.
- 이를 해결하기 위해 `finance/transform.py`에는
  `align_dfs_to_canonical_period_dates(...)`가 추가되었고,
  snapshot 전략용 price builder는
  union calendar 생성 후 period당 1개의 canonical date로 다시 정렬한다.
- 그 결과 `Quality Snapshot (Strict Annual)`의
  `US Statement Coverage 1000` 검증에서도
  tail row가
  `2026-02-27`, `2026-03-20`
  처럼 canonical month-end row로 정리되는 것이 확인되었다.
- 따라서 현재 `finance`의 factor/fundamental public family는
  - broad research representative:
    - `Quality Snapshot`
  - strict annual representative:
    - `Quality Snapshot (Strict Annual)`
  - strict annual secondary family:
    - `Value Snapshot (Strict Annual)`
  - strict annual multi-factor candidate:
    - `Quality + Value Snapshot (Strict Annual)`
  구조로 보는 편이 가장 정확하다.
- Phase 5 first chapter에서는 이 strict annual family 위에
  strategy-library baseline과 first risk overlay가 추가로 올라갔다.
  현재 구현 상태는 다음과 같다.
  - `Backtest` 화면 상단은
    - `Single Strategy`
    - `Compare & Portfolio Builder`
    - `History`
    구조로 정리되었고,
    history는 single / compare 공용 surface로 분리되었다
  - compare 화면에서도 strict family별 advanced input parity가 열려 있다
    - preset
    - factor set
    - `top_n`
    - `rebalance_interval`
    - trend filter on/off
    - trend filter window
  - first overlay는
    `month-end MA200 trend filter + survivor reweight / full-cash fallback`
    으로 고정되었다
  - overlay가 켜진 strict family result는
    - `Raw Selected Ticker`
    - `Raw Selected Count`
    - `Raw Selected Score`
    - `Overlay Rejected Ticker`
    - `Overlay Rejected Count`
    - `Trend Filter Enabled`
    - `Trend Filter Column`
    을 함께 남긴다
  - strict family의 `Selection History`는
    `History / Interpretation / Selection Frequency`
    구조로 확장되었고,
    `Interpretation` 탭에서
    - raw candidate 수
    - final selected 수
    - overlay rejection 수
    - cash-only rebalance 수
    - 평균 cash share
    - overlay rejection frequency
    를 함께 읽을 수 있다
  - 현재 구현 기준으로는
    partial trend rejection이 발생해도
    생존 종목들에 다시 균등배분한다
    - 즉 부분 탈락분은 자동으로 현금으로 남지 않는다
    - `cash share`가 커지는 경우는
      raw 후보 전부 탈락하거나
      market regime overlay가 전체를 막는 경우에 더 가깝다
  - 다만 일부 runtime / interpretation copy에는
    여전히 부분 탈락분이 cash로 간다고 읽힐 수 있는 문구가 남아 있다
    - 이는 현재 코드 의미와 완전히 일치하지 않는다
  - single strategy뿐 아니라 compare focused strategy에서도
    selection interpretation과 selection frequency를 함께 읽을 수 있다
  - strict preset은 현재 historical backtest semantics를 유지한다
    - run-level preset universe는 고정
    - selected end date freshness로 run 전체 universe를 교체하지 않음
    - 각 rebalance date마다 usable한 price / factor가 있는 종목만 자연스럽게 후보로 남음
  - `Price Freshness Preflight`는
    경고 / 진단 레이어로 유지되며,
    stale / missing symbol에 대해
    heuristic reason을 추가로 보여준다
    - `likely_delisted_or_symbol_changed`
    - `asset_profile_error`
    - `missing_price_rows`
    - `minor_source_lag`
    - `source_gap_or_symbol_issue`
    - `persistent_source_gap_or_symbol_issue`
- first overlay on/off 검증 결과는 strategy별로 달랐다
  - `Quality` strict에서는 overlay가 더 보수적으로 작동해
    canonical compare 기준 성과가 약화되었다
  - `Value`, `Quality + Value` strict에서는
    canonical compare 기준으로
      End Balance / CAGR / Sharpe가 개선되고 MDD가 완화되었다
- Phase 6에서는 여기서 second overlay first pass가 추가되었다.
  - second overlay는
    `Market Regime Overlay`
    로 고정되었다
  - first-pass rule은
    benchmark `Close < MA(window)`이면
    그 rebalance에서 strict factor 후보 전체를 현금으로 이동시키는 방식이다
  - 기본 benchmark는 `SPY`, 기본 window는 `200`이며,
    여기서 `200`은 benchmark의 `200거래일 이동평균`을 뜻한다.
    즉 장기 추세선 아래인지 위인지로
    risk-on / risk-off를 판정한다.
  - UI에서는 overlay가 꺼져 있어도
    window / benchmark를 미리 조정할 수 있고,
    overlay를 켜면 그 값이 바로 사용된다.
  - quarterly prototype은 현재 research-only 경로라
    quarterly shadow coverage가 늦게 시작되는 구간에서는
    요청 start date보다 실제 active period가 뒤에서 시작될 수 있다.
  - 선택 가능한 benchmark는
    `SPY`, `QQQ`, `VTI`, `IWM`
    로 열려 있다
  - 이 overlay는 현재
    `Quality Snapshot (Strict Annual)`,
    `Value Snapshot (Strict Annual)`,
    `Quality + Value Snapshot (Strict Annual)`
    의 single / compare / history path에 연결되었다
  - result row는 이제 아래 regime 메타를 함께 남긴다
    - `Market Regime Enabled`
    - `Market Regime Benchmark`
    - `Market Regime Column`
    - `Market Regime State`
    - `Market Regime Close`
    - `Market Regime Trend`
    - `Regime Blocked Ticker`
    - `Regime Blocked Count`
  - `Selection History -> Interpretation`도 여기에 맞춰 보강되어,
    `Regime Blocked Events`,
    `Regime Cash Rebalances`,
    `Market Regime Events`
    를 함께 읽을 수 있다
  - current semantics는 여전히 rebalance-date only다
    - intramonth daily regime trigger는 아직 없다
    - 즉 month-end 시점에만 benchmark regime을 판정하고,
      risk-off면 그 달 포트폴리오 전체를 현금으로 둔다
- Phase 6~8에서는 quarterly strict family가 research-only strategy family 수준까지 확장되었다.
  - 현재 quarterly family:
    - `Quality Snapshot (Strict Quarterly Prototype)`
    - `Value Snapshot (Strict Quarterly Prototype)`
    - `Quality + Value Snapshot (Strict Quarterly Prototype)`
  - 세 경로 모두 quarterly statement shadow factor history를 사용하며,
    현재는 public default가 아니라
    research-only prototype으로 해석하는 것이 맞다
  - current first pass에서 quarterly family도
    trend filter overlay,
    market regime overlay,
    selection history,
    interpretation
    을 annual strict family와 같은 형태로 지원한다
  - quarterly family는 이제
    - single strategy
    - compare
    - history rerun / prefill
    까지 연결되어 있다
  - compare 기본 preset은
    `US Statement Coverage 100`
    으로 고정되어 quarterly validation 비용을 낮춘다
  - manual small universe 기준으로는
    `AAPL/MSFT/GOOG`에서
    quarterly value / quality+value가 `2017-05-31`부터 active하게 열렸고,
    managed preset `US Statement Coverage 100` 기준으로는
    quarterly quality / value / quality+value 모두 `2016-01-29`부터 active하다
  - 이 차이 때문에 current semantics는 여전히 research-only가 맞다.
    - 즉 실행 가능성과 promotion readiness는 구분해서 본다
  - Phase 7 first pass 이후에는
    quarterly raw ledger / shadow coverage가 다시 복구되어
    `US Statement Coverage 100` 기준으로 quarterly family의 first active date가
    `2016-01-29` 부근까지 내려갔다
  - same Phase 7 supplementary polish에서는
    `Price Freshness Preflight`가 selected end 그대로가 아니라
    실제 DB `effective trading end`를 기준으로 stale 여부를 판단하도록 보강되었다
    - 예:
      - selected end `2026-03-28`
      - effective trading end `2026-03-27`
    - 따라서 weekend / holiday end-date 때문에 whole-universe stale처럼 보이는 false warning이 줄었다
  - quarterly prototype single forms에는
    `Statement Shadow Coverage Preview`가 추가되어
    현재 rebuilt quarterly shadow 기준
    - earliest period
    - latest period
    - median rows per symbol
    을 실행 전 바로 읽을 수 있다
  - same preview는 이후 보강으로
    `Covered < Requested`일 때
    - missing symbol 목록
    - raw statement coverage 존재 여부
    - targeted `Extended Statement Refresh` payload
    까지 보여주도록 확장되었다
    - `no_raw_statement_coverage`
      - strict raw statement ledger 자체가 없음
      - 추가 statement 수집 우선
    - `raw_statement_present_but_shadow_missing`
      - raw는 존재하지만 shadow가 비어 있음
      - source 추가 수집보다 shadow rebuild / coverage hardening 점검 우선
  - 또한 `Extended Statement Refresh`가 quarterly raw statement만 갱신하고
    quarterly shadow coverage는 그대로 두던 경로도 수정되었다.
    - 이제 post-fix run에서는
      `Quality Snapshot (Strict Quarterly Prototype)` 같은 quarterly preview가
      같은 실행 안에서 raw + shadow 기준으로 함께 갱신된다
    - 다만 pre-fix 시점에 이미 raw-only refresh가 누적된 심볼은
      `raw_statement_present_but_shadow_missing`로 대량 남아 있을 수 있고,
      이 경우에는 post-fix `Extended Statement Refresh`를 한 번 더 태워야
      quarterly shadow coverage가 실제로 올라간다
  - same preview는 이후 성능 보강으로
    `nyse_fundamentals_statement` / `nyse_financial_statement_values`를
    aggregate query로 요약해서 읽고,
    statement-related job 완료 시 preview cache도 함께 비우도록 수정되었다
    - 목적:
      - large-universe preview 응답 개선
      - refresh 직후 stale cached summary 노출 방지
- `Ingestion` 탭에는
  `Statement PIT Inspection` helper card가 추가되어
    아래를 UI에서 직접 확인할 수 있다
    - DB coverage summary
    - DB timing audit
    - EDGAR source payload inspection
  - 또한 같은 카드 안에
    결과 해석용 한국어 가이드가 추가되어
    - `Coverage Summary`는 DB coverage 확인
    - `Timing Audit`는 PIT timing 확인
    - `Source Payload Inspection`은 live source field 구조 확인
    으로 읽도록 정리되어 있다
  - same operator polish pass에서
    `Ingestion` 화면의 상단 `Write Targets` 표는 제거되었고,
    각 실행 카드는 expander 기반으로 바뀌었다
    - 이유:
      - write target 정보는 각 카드 안의 `Writes to:` 설명과 중복
      - 운영/수동 작업이 한 화면에 너무 길게 펼쳐지는 문제 완화
  - `Recent Logs`는 현재도 실사용 가치가 높고,
    최근 `logs/*.log`를 tail preview하는 방식으로 유지된다
  - `Failure CSV Preview`는 기술적으로는 동작하지만,
    최근 주요 job들이 failure CSV를 일관되게 남기지 않아서
    현재 운영 가치는 상대적으로 낮다
  - same operator-tooling pass에서
    `Ingestion` 상단에 `Runtime / Build` block이 추가되어
    - current runtime marker
    - process loaded timestamp
    - git short SHA
    를 확인할 수 있게 되었다
  - 또한 manual helper로
    `Statement Shadow Rebuild Only`가 추가되어
    raw statement ledger를 다시 수집하지 않고
    - `nyse_fundamentals_statement`
    - `nyse_factors_statement`
    shadow만 재생성할 수 있게 되었다
  - quarterly prototype의 `Statement Shadow Coverage Preview` drilldown은
    이제 단순 payload 제안에 그치지 않고
    - raw-gap symbols -> `Extended Statement Refresh`
    - raw-present / shadow-missing symbols -> `Statement Shadow Rebuild Only`
    로 넘기는 action bridge까지 가진다
  - 같은 operator tooling pass에서
    `Statement Coverage Diagnosis` card도 추가되었다
    - 목적:
      - coverage-missing symbol이 단순 재수집 대상인지
      - shadow rebuild 대상인지
      - foreign/non-standard form 구조 때문에 현재 strict path와 잘 맞지 않는지
      - symbol/source issue 쪽인지
      를 한 번 더 좁히기 위함
    - 예를 들어:
      - `MRSH` 같은 source-empty case는 `source_empty_or_symbol_issue`
      - `AU` 같이 `20-F` / `6-K` form 위주인 case는 `foreign_or_nonstandard_form_structure`
      로 분리되도록 구현되었다
  - persisted ingestion runs에는
    standardized run artifacts가 붙는다
    - every run:
      - `.note/finance/run_artifacts/<run-key>/result.json`
      - `.note/finance/run_artifacts/<run-key>/manifest.json`
    - symbol-level issue가 있을 때:
      - `csv/<run-key>_failures.csv`
  - `Persistent Run History` 아래에는 `Run Inspector`가 추가되어
    selected run의
    - runtime marker
    - pipeline steps
    - artifact paths
    - related logs
    를 다시 읽을 수 있게 되었다
- Phase 6 smoke validation 기준으로는
  `AAPL/MSFT/GOOG`, `2024-01-01 -> 2026-03-28`, `SPY < MA200 => cash`
  small universe에서
  - annual strict family 3종 모두 regime row/blocked count를 정상 기록했고
  - quarterly prototype도 실제 result bundle을 반환했다
  - quarterly prototype small-smoke 결과는
    - `End Balance = 14066.3`
    - `CAGR = 0.1718`
    - `Sharpe = 1.0931`
    - `MDD = -0.1232`
    수준으로 확인되었다
- 따라서 현재 strict factor strategy library의 Phase 8 상태는
  - annual strict family:
    - first overlay + second overlay까지 실험 가능한 상태
  - quarterly strict family:
    - research-only family 3종이 single / compare / history까지 열린 상태
    - 다음 major question은 promotion readiness와 wider-universe stability다
  - current strict coverage preset semantics:
    - `Coverage 100/300/500/1000`은 historical monthly top-N universe가 아니라
      current managed universe 기준 membership를 쓰는 `managed static research universe`
    - run 안에서는 각 rebalance date마다 usable price/factor availability filtering이 적용된다
    - 따라서 현재 preset 결과는 실전 투자용 final validation contract가 아니라
      research/operator validation contract로 읽는 편이 맞다
    - real-money 수준의 final validation은 future `historical dynamic PIT universe` mode에서 다시 봐야 한다
  - Phase 10 first pass 이후 annual strict single-strategy surface에는
    별도 `Universe Contract`가 추가되었다:
    - `static_managed_research`
    - `historical_dynamic_pit`
  - current 구현 범위에서 dynamic PIT는
    annual strict + quarterly strict prototype
    single-strategy + compare first pass를 포함한다
  - dynamic PIT membership first/second pass는
    - managed candidate pool
    - rebalance-date close
    - `latest_available_at <= rebalance_date`인 최신 statement `shares_outstanding`
    를 사용해 `approx_market_cap`을 계산하고 top-N membership를 다시 구성한다
  - dynamic first pass는 candidate pool 전체의 full-range price history를 강제하지 않는다
    - selected end까지 DB price history가 확인된 candidate만 natural inclusion된다
    - 따라서 `dynamic_candidate_count`와 실제 `candidate_pool_count`는 다를 수 있다
  - second pass에서는 continuity / profile diagnostics도 함께 남긴다
    - `continuity_ready_count`
    - `pre_listing_excluded_count`
    - `post_last_price_excluded_count`
    - `asset_profile_delisted_count`
    - `asset_profile_issue_count`
  - candidate-level continuity 진단도 별도 row로 남긴다
    - `first_price_date`
    - `last_price_date`
    - `price_row_count`
    - `profile_status`
    - `profile_delisted_at`
    - `profile_error`
  - result / meta surface에도 dynamic 계약 정보가 함께 남는다:
    - result row:
      - `Universe Membership Count`
      - `Universe Contract`
    - bundle meta:
      - `universe_contract`
      - `dynamic_candidate_count`
      - `dynamic_target_size`
      - `universe_debug`
    - bundle top-level:
      - `dynamic_universe_snapshot_rows`
      - `dynamic_candidate_status_rows`
    - result UI:
      - `Dynamic Universe` 탭
      - history drilldown의 `dynamic_universe_preview_rows`
      - history drilldown의 `dynamic_universe_artifact`
  - dynamic run history에는 universe artifact도 같이 남는다
    - `dynamic_universe_artifact`
    - `dynamic_universe_preview_rows`
    - `.note/finance/backtest_artifacts/.../dynamic_universe_snapshot.json`
  - compare / repeated strict run에서는 small in-process cache를 사용해
    price panel / statement shadow / asset profile summary의 중복 로드를 일부 줄인다
  - compare mode에서도 annual strict family는 dynamic first pass를 사용할 수 있으며,
    `Strategy Highlights`에
    - `Universe Contract`
    - `Dynamic Candidate Pool`
    - `Membership Avg`
    - `Membership Range`
    를 같이 노출해 static vs dynamic 차이를 읽을 수 있게 했다
  - quarterly strict prototype family도 same contract first pass를 지원하지만,
    이 결과는 여전히 research-only quarterly family로 읽는 것이 맞다
  - current dynamic PIT는 여전히 perfect constituent-history engine이 아니며,
    current-source 기반 `approximate PIT + diagnostics` contract다
로 보는 것이 가장 정확하다

즉, 예전보다 통합은 많이 진행됐지만 아직 모든 전략과 모든 입력이 loader 계층으로 완전히 이행된 상태는 아니다.

---

## 4. 상위 디렉터리 기준 파일 역할

## 4-1. 핵심 실행 계층

### `finance/loaders/*`
Phase 3에서 추가된 조회 계층이다.

역할:
- DB 적재 데이터 조회
- loader 계약 기준 입력 정규화
- broad research loader와 strict PIT loader 분리의 기반 제공
- 기존 전략 계층과 DB 사이의 read path 담당

현재 구현된 것:
- `load_universe`
- `load_price_history`
- `load_price_matrix`
- `load_fundamentals`
- `load_fundamental_snapshot`
- `load_factors`
- `load_factor_snapshot`
- `load_factor_matrix`
- `load_statement_values`
- `load_statement_labels`
- `load_statement_snapshot_strict`
- runtime adapter 계열

### `finance/engine.py`
`BacktestEngine`이 패키지의 전략 실행 중심 인터페이스다.

역할:
- 티커 집합과 기간 옵션을 받는다.
- OHLCV 로드
- 전처리 함수 체이닝
- 전략 실행
- 표시용 반올림

현재 사용 패턴은 아래와 같다.

```python
engine = (
    BacktestEngine(tickers, period=..., option=...)
    .load_ohlcv()
    .add_ma(...)
    .filter_by_period()
    .align_dates()
    .slice(...)
    .run(strategy)
    .round_columns()
)
```

의미:
- 기존 외부 직접조회 기반 실행과
  DB 기반 loader 실행을 같은 체이닝 인터페이스 안에서 관리한다.
- `load_ohlcv_from_db(...)`는 `history_start`를 받아
  지표 warmup용 과거 이력을 먼저 읽고 마지막에 실제 start/end를 자르는 흐름도 지원한다.
- `engine.py`는 계산 엔진 자체라기보다 orchestration wrapper다.
- 실질 계산은 대부분 `data.py`, `transform.py`, `strategy.py`에 있다.

### `finance/strategy.py`
전략 로직이 모여 있는 핵심 파일이다.

현재 구현 전략:
- `equal_weight`
- `gtaa3`
- `risk_parity_trend`
- `dual_momentum`

특징:
- 모든 전략이 event-driven 주문 엔진보다는 "시점별 포트폴리오 상태 계산" 방식이다.
- 결과는 체결 로그가 아니라 시점별 상태 테이블이다.
- 각 전략 결과 스키마가 완전히 통일되지는 않았다.

### `finance/transform.py`
순수 전처리 함수 집합이다.

가장 중요한 점:
- 입력 형태를 `{ticker: DataFrame}`로 통일하고 있다.
- 전략 이전 단계에서 데이터 길이를 줄이는 함수가 여러 개 있다.

예:
- `add_ma`: 가장 긴 이동평균이 없는 초반 구간 제거
- `add_interval_returns`: 가장 긴 구간 수익률이 없는 초반 구간 제거
- `align_dfs_by_date_intersection`: 모든 티커 공통 날짜만 유지

이 때문에 실제 전략 입력 데이터는 원본보다 훨씬 짧아질 수 있다.

### `finance/performance.py`
성과 요약 계층이다.

핵심 함수:
- `portfolio_performance_summary`
- `make_monthly_weighted_portfolio`

중요한 가정:
- 입력 DataFrame에 최소한 `Date`, `Total Balance`, `Total Return`이 있어야 한다.

### `finance/display.py`
결과를 보기 좋게 만드는 후처리 계층이다.

특징:
- list 컬럼과 ndarray 컬럼까지 반올림 가능
- 현재 전략 결과 포맷과 잘 맞게 설계돼 있다

### `finance/visualize.py`
Matplotlib 시각화 계층이다.

특징:
- 리서치/노트북 사용을 염두에 둔 단순한 플로팅 함수
- macOS 한글 폰트 설정이 코드에 포함됨

### `finance/sample.py`
예제 파일이지만 실질적으로는 수동 통합 테스트 역할도 한다.

함수군:
- 전략 실행 샘플
- DB 기반 전략 실행 샘플 (`*_from_db`)
- 자산 프로필 적재 샘플
- fundamentals/factors 적재 샘플

즉, 사용 예제이면서 현재 프로젝트의 "실행 가이드" 역할도 같이 한다.

추가 메모:
- DB 기반 sample 함수들은 indicator warmup이 필요한 전략에 대해
  실제 `start`보다 더 앞선 이력을 먼저 읽고,
  마지막에 `slice(start=...)`를 적용하는 구조로 정리되었다.
- direct-fetch sample 함수들은 legacy reference path로 남아 있으며,
  `*_from_db` 함수들이 제품 경로에 더 가까운 DB-backed runtime sample 역할을 맡는다.
- 최근에는 price-only 전략 sample들이 `_build_price_only_engine(...)` helper를 공유하도록 정리되어,
  direct path와 DB-backed path의 runtime 시작 규칙이 한 곳에서 관리된다.
- factor / fundamental 전략은 price-only 경로와 달리
  `loader -> snapshot connection layer -> strategy` 구조로 연결하는 것이 권장되며,
  향후 rebalance-date 기준 snapshot payload가 runtime의 핵심 계약이 될 가능성이 높다.
- 현재 기준 strategy input contract는
  - price-only 전략: `{ticker: price_df}` dict
  - factor / fundamental 전략: `price_dfs + snapshot_by_date + rebalance_dates`
  로 구분해서 다루는 방향으로 정리되고 있다.
- 또한 DB-backed runtime regression을 위해
  repeatable smoke scenario 세트가 별도 문서로 정리되어 있으며,
  price runtime / parity / fundamentals/factors sample validation을 기준 경로로 사용한다.
- 같은 맥락에서 loader/runtime 검증용 실행 예시 모음도 별도 문서로 정리되어 있어,
  이후 UI 연결 전에도 최소 경로를 바로 재실행할 수 있다.

---

## 4-2. 데이터 수집 계층

### `finance/data/data.py`
가격 데이터 경계 모듈이다.

핵심 기능:
- `get_ohlcv`
  - yfinance OHLCV를 `{ticker: DataFrame}`로 변환
- `get_fx_rate`
  - 환율 조회
- `store_ohlcv_to_mysql`
  - 가격 데이터 DB 적재
- `load_ohlcv_many_mysql`
  - DB에서 가격 이력 조회

이 파일의 의미:
- 시장 데이터와 시스템 내부 표현 사이의 첫 번째 boundary
- 최근에는 canonical refresh 관점에서:
  - blank OHLCV row를 적재하지 않도록 보강되었고
  - 요청 구간의 기존 row를 지우고 다시 적재하는 경로를 지원하며
  - `end`를 inclusive semantics로 보정해 direct provider path와 DB path의 일관성을 맞추고 있다
- 또한 `Daily Market Update` rate-limit 대응 first-pass로:
  - yfinance provider output을 batch 단위로 캡처해
    `rate_limited_symbols` / `provider_no_data_symbols`를 구분한다
  - execution profile(`managed_safe`, `managed_fast`, `managed_refresh_short`, `raw_heavy`)에 따라
    batch size / retry / cooldown 동작을 다르게 적용한다
  - broad source에서 rate-limit이 감지되면 cooldown event를 남기고,
    더 보수적인 다음 batch window로 진행한다
- 이어서 속도 최적화 second-pass로:
  - `managed_fast` profile이 추가되었고
  - `Profile Filtered Stocks + ETFs`는 이제 기본적으로 이 faster managed profile을 탄다
  - writer 결과에는 timing breakdown이 남아,
    fetch / delete / upsert / retry sleep / cooldown sleep / inter-batch sleep을 분해해서 볼 수 있다
- 이후 short-window acceleration pass로:
  - `managed_refresh_short` profile이 추가되었고
  - `1d` 또는 아주 짧은 explicit daily refresh는
    managed broad source뿐 아니라 narrower managed source에서도 이 profile을 우선 탄다
  - 이 경로는 `2-worker + chunk_size 70` first pass로 동작하되,
    rate-limit이 보이면 다시 더 보수적인 다음 batch window로 후퇴한다
- 가격 데이터만 놓고 보면 현재 가장 기본적인 source adapter 역할

### `finance/data/nyse.py`
NYSE 상장 종목 목록 수집기다.

기술 방식:
- Selenium
- BeautifulSoup

산출물:
- `csv/nyse_stock.csv`
- `csv/nyse_etf.csv`

의미:
- 전체 유니버스 구축의 출발점
- 현재는 API 기반이 아니라 웹 크롤링 기반

### `finance/data/nyse_db.py`
NYSE CSV를 DB로 올리는 로더다.

역할:
- CSV 읽기
- 테이블 생성
- UPSERT

즉, `nyse.py`와 짝을 이루는 ETL의 load 단계다.

### `finance/data/asset_profile.py`
심볼별 메타데이터 수집기다.

수집 데이터:
- 이름
- quote type
- exchange
- sector
- industry
- country
- market_cap
- dividend_yield
- payout_ratio
- status
- is_spac

이 파일이 중요한 이유:
- 이후 유니버스 필터링의 기준이 된다.
- `load_symbols_from_asset_profile()`를 통해 종목군을 선별한다.

현재 기본 필터:
- SPAC 제외
- 중국 종목 제외
- delisted 추정 제외

즉, 단순 메타 저장이 아니라 "전략용 유니버스 정제"의 시작점이다.

### `finance/data/fundamentals.py`
재무 스냅샷 정규화 모듈이다.

핵심 목적:
- yfinance 원시 재무제표에서 백테스트용 최소 필수 항목만 안정적으로 추출

특징:
- 계정명이 직접 존재하지 않을 때 fallback 계산 로직이 들어 있다.
- 예:
  - gross profit 보정
  - operating income 보정
  - EBIT 보정
  - shares outstanding 근사치 계산
- 최근에는 factor 계산에 필요한 base field를 더 넓게 담도록 보강되었다.
  - 예:
    - pretax income
    - interest expense
    - inventory
    - short-term / long-term debt
    - shareholders equity
- 또한 각 핵심 필드가 direct / derived / inferred 중 어떤 경로로 만들어졌는지
  source 메타를 함께 저장하도록 확장되었다.

즉, 단순 수집이 아니라 **정규화와 보정**을 수행한다.

### `finance/data/factors.py`
재무 팩터 계산 모듈이다.

입력:
- `nyse_fundamentals`
- 가격 DB의 종가

핵심 처리:
- `period_end` 기준 직전 거래일 가격 매칭
- market cap 계산
- enterprise value 계산
- valuation/profitability/growth 팩터 계산
- price attachment metadata 저장
  - `price_date`
  - `price_match_gap_days`
  - `timing_basis`
  - `pit_mode`

이 파일의 의미:
- 이 프로젝트가 단순 가격 백테스트를 넘어 팩터 전략으로 확장될 수 있게 하는 핵심 중간 계층

### `finance/data/financial_statements.py`
상세 재무제표 저장용 모듈이다.

특징:
- EDGAR 사용
- 라벨 메타와 값 테이블을 분리 저장
- 한글 라벨 매핑 지원

의미:
- `fundamentals.py`가 "요약 스냅샷"이라면,
- `financial_statements.py`는 "세부 계정 원장"에 가깝다.

이 모듈이 있으면 장기적으로 커스텀 팩터를 훨씬 풍부하게 만들 수 있다.

### `finance/data/data_format.py`
실행 모듈이 아니라 참조성 문서 모듈이다.

역할:
- yfinance `ticker.info` 구조 예시 정리

실질 의미:
- 스키마 설계나 필드 탐색에 도움을 주는 reference file

---

## 4-3. DB 계층

### `finance/data/db/mysql.py`
아주 얇은 MySQL 래퍼다.

제공 기능:
- `execute`
- `executemany`
- `query`
- `use_db`
- `close`

의미:
- ORM이 아니라 직접 SQL 중심 운영
- 구조가 단순해 현재 단계에서는 이해하기 쉽다

### `finance/data/db/schema.py`
스키마 정의와 자동 동기화의 중심이다.

중요 기능:
- `NYSE_SCHEMAS`
- `PRICE_SCHEMAS`
- `FUNDAMENTAL_SCHEMAS`
- `sync_table_schema`

`sync_table_schema`의 의미:
- 코드에 새 컬럼이 추가되면 기존 테이블에 자동으로 컬럼을 더한다
- 초기 단계 프로젝트에서 스키마 진화를 쉽게 만들어 준다

한계:
- 컬럼 추가 중심이지, 컬럼 변경/삭제/인덱스 재설계까지 안전하게 다루는 정식 migration 시스템은 아니다

---

## 5. 현재 데이터 흐름

## 5-1. 유니버스 구축 흐름

```text
NYSE 웹페이지
  -> load_nyse_listings()
  -> csv/nyse_stock.csv, csv/nyse_etf.csv
  -> load_nyse_csv_to_mysql()
  -> finance_meta.nyse_stock / finance_meta.nyse_etf
  -> collect_and_store_asset_profiles()
  -> finance_meta.nyse_asset_profile
```

의미:
- 유니버스 데이터는 "크롤링 -> CSV -> DB -> 프로파일 보강" 순서다.

## 5-2. 가격 데이터 흐름

```text
yfinance
  -> get_ohlcv()
  -> 백테스트 직접 사용

또는

yfinance
  -> store_ohlcv_to_mysql()
  -> finance_price.nyse_price_history
  -> load_ohlcv_many_mysql()
```

의미:
- 가격은 "직접 사용 경로"와 "DB 적재 경로"가 둘 다 존재한다.
- 이 이중 경로는 유연하지만, 장기적으로는 소스 일관성 문제를 만들 수 있다.

## 5-3. 재무/팩터 흐름

```text
yfinance statements
  -> upsert_fundamentals()
  -> finance_fundamental.nyse_fundamentals
  -> upsert_factors()
  -> finance_fundamental.nyse_factors
```

중요 포인트:
- 팩터 계산은 fundamentals가 먼저 채워져 있어야 한다.
- 가격 DB도 준비돼 있어야 한다.

즉, `nyse_factors`는 독립 수집 테이블이 아니라 파생 테이블이다.

추가된 shadow path:

```text
nyse_financial_statement_values
  -> upsert_statement_fundamentals_shadow()
  -> finance_fundamental.nyse_fundamentals_statement
  -> upsert_statement_factors_shadow()
  -> finance_fundamental.nyse_factors_statement
```

의미:
- broad public path와 statement-driven rebuild path를 분리
- first-pass는 `latest_available_for_period_end` 기준 shadow history
- strict PIT raw truth 자체는 여전히 `nyse_financial_statement_values`

## 5-4. 상세 재무제표 흐름

```text
EDGAR
  -> get_fundamental()
  -> _iter_label_rows()
  -> _iter_value_rows()
  -> upsert_financial_statements()
  -> labels / values 테이블
```

의미:
- detailed statement 계층은 향후 커스텀 팩터 엔진의 원재료가 될 수 있다.

---

## 6. DB 구조 요약

## 6-1. DB 목록

- `finance_meta`
- `finance_price`
- `finance_fundamental`

## 6-2. 테이블 목록

### `finance_meta`
- `nyse_stock`
- `nyse_etf`
- `nyse_asset_profile`

### `finance_price`
- `nyse_price_history`

### `finance_fundamental`
- `nyse_fundamentals`
- `nyse_factors`
- `nyse_financial_statement_filings`
- `nyse_financial_statement_values`
- `nyse_financial_statement_labels`

---

## 7. 테이블별 역할과 데이터 성격

### `nyse_stock`, `nyse_etf`
역할:
- 전체 유니버스의 출발점

성격:
- 마스터 심볼 목록
- 상대적으로 정적 데이터

### `nyse_asset_profile`
역할:
- 유니버스 필터링
- 섹터/산업/국가 기반 분류
- 운영 상태 추적

성격:
- 반정적 메타데이터
- 정제된 심볼 집합 생성에 직접 사용됨

### `nyse_price_history`
역할:
- 가격 기반 백테스트의 핵심 원장

성격:
- 시계열 원천 데이터
- OHLCV + 배당 + 분할 포함
- stock과 ETF를 함께 저장하는 공용 price fact table
- 자산 종류 구분은 별도 meta 테이블(`nyse_stock`, `nyse_etf`, `nyse_asset_profile`)에서 해석

### `nyse_fundamentals`
역할:
- 핵심 재무 스냅샷 저장

성격:
- broad coverage summary layer
- period-end 기준 provider-normalized 재무 요약
- strict raw ledger가 아니라 factor 계산용 중간 계층
- 핵심 필드에 대해 derivation/source 메타를 함께 저장

### `nyse_fundamentals_statement`
역할:
- statement ledger 기반 fundamentals shadow 저장

성격:
- statement-driven shadow layer
- `nyse_financial_statement_values`에서 strict usable row를 읽어 재구성
- `first_available_for_period_end` 의미의 summary history
- public broad table을 대체하지 않고 비교/검증용으로 유지
- schema의 메타 컬럼 이름은 여전히
  `latest_available_at`, `latest_accession_no`, `latest_form_type`
  이지만,
  현재 의미는 각 `period_end`에 대한 **가장 이른 usable filing snapshot**을 가리킨다
- Phase 7에서는 quarterly builder가 더 이상 `report_date`를
  `period_end` anchor처럼 강제하지 않도록 수정되었다.
  즉 quarterly comparative facts도 valid `period_end` 기준으로 shadow에 남을 수 있다.
- `shares_outstanding`은 현재 가능하면 statement-derived를 우선하고,
  없을 때는 broad `nyse_fundamentals` nearest-period fallback을 사용할 수 있음

### `nyse_factors`
역할:
- 파생 팩터 저장

성격:
- broad research derived layer
- `nyse_fundamentals + as-of price` 기반 파생 팩터 테이블
- strict PIT factor store가 아니라 research / prototype 전략 입력 후보 테이블
- price attachment metadata와 timing 의미를 함께 저장

### `nyse_factors_statement`
역할:
- statement-driven shadow factor 저장

성격:
- `nyse_fundamentals_statement + as-of price` 기반 파생 테이블
- 현재는 quality / accounting 계열 검증에 더 적합하지만,
  shares fallback이 붙은 row에서는 valuation 계열도 일부 계산 가능
- `fundamental_available_at`, `fundamental_accession_no` 메타 포함
- 여전히 shares 부재 시 valuation 계열은 일부 `NULL`일 수 있음
- 현재는 `Quality Snapshot (Strict Annual)`과
  `Value Snapshot (Strict Annual)`의 public fast runtime source로도 사용된다

### `nyse_financial_statement_filings`
역할:
- filing 단위 공시 메타 저장

성격:
- human-inspectable filing ledger
- `accession_no`, `filing_date`, `accepted_at`, `available_at`, `report_date` 중심

### `nyse_financial_statement_values`
역할:
- filing / concept / period 단위 상세 재무 계정 저장

성격:
- long-format raw fact ledger
- 실제 `period_end`와 공시 가능 시점을 함께 보존
- strict raw ledger 방향으로 정리 중
- `accession_no`, `unit`, `available_at`를 갖는 row를 PIT-friendly raw row로 우선 취급
- 확장형 팩터 생성에 적합
- Phase 7 이후 quarterly path는
  - `10-Q`
  - `10-Q/A`
  - `10-K`
  - `10-K/A`
  를 함께 받아 year-end `FY` rows를 quarterly longer-history에 포함한다
- statement ingestion은 이제 `periods=0`을 `all available periods`로 공식 지원한다
- web operator UI에서 manual `Financial Statement Ingestion`은
  `Statement Mode` 단일 입력을 노출하고,
  내부적으로 `freq`와 `period`를 같은 값으로 맞춰 실행한다

### `nyse_financial_statement_labels`
역할:
- 재무 계정 concept 요약 메타 저장

성격:
- operator-facing summary 계층
- `symbol + statement_type + concept + as_of` 기준의 concept summary
- strict loader의 source of truth가 아니라 UI/해석 보조 계층

---

## 8. 현재 전략 레이어의 성격

현재 전략들은 전반적으로 ETF/자산배분형 전략에 더 가깝다.

샘플 기준:
- 배당 ETF 묶음
- 글로벌 자산배분
- 듀얼 모멘텀
- 리스크 패리티

즉, 개별 종목 selection 엔진보다는 "소수 자산군 로테이션/배분" 성격이 강하다.

이건 데이터 인프라가 향하는 방향과 약간 차이가 있다.

왜냐하면 데이터 인프라는:
- NYSE 전체 유니버스
- 주식 프로파일
- 재무/팩터
- 상세 재무제표

까지 수집하고 있어서, 장기적으로는 **주식 단면(cross-sectional) 팩터 전략** 쪽으로 확장할 준비가 되어 있기 때문이다.

즉, 현재 상태는 다음과 같이 볼 수 있다.

- 전략: ETF 중심 리서치
- 데이터: 주식 팩터 연구까지 고려한 인프라

이 구조는 나쁘지 않지만, 두 축의 연결은 아직 초기 단계다.

---

## 9. 강점 분석

## 9-1. 역할 분리가 비교적 명확하다
- 수집
- 변환
- 전략
- 성과/표현

의 층이 분명하다.

특히 `transform.py`와 `strategy.py`가 분리되어 있어 전략 실험이 쉬운 편이다.

## 9-2. DB 적재 계층이 이미 꽤 실용적이다
- UPSERT 기반
- 스키마 자동 동기화
- 배치 처리
- 재시도
- 로그 파일 저장

초기 프로젝트치고는 운영 감각이 들어가 있다.

## 9-3. 재무 데이터 계층이 단순하지 않다
- fundamentals 요약 계층
- detailed financial statements 계층
- factors 파생 계층

의 3단 구조가 있다.

이건 향후 팩터 연구에 유리하다.

## 9-4. 전략 API가 간단하다
`BacktestEngine(...).<transform>().run(strategy)` 패턴은 이해하기 쉽다.

즉, 새로운 전략을 붙이기도 나쁘지 않다.

---

## 10. 현재 구조의 핵심 한계

## 10-1. DB 기반 데이터 파이프라인과 전략 파이프라인이 분리돼 있다
현재 전략 샘플은 대부분 DB가 아닌 `yfinance` 직로딩을 사용한다.

영향:
- 재현성 저하
- 데이터 버전 관리 어려움
- 동일 전략이라도 실행 시점에 따라 데이터 차이 가능

장기적으로는 아래 중 하나로 정리해야 한다.

1. 백테스트 입력을 DB 기준으로 통일
2. 또는 실험용/운영용 경로를 명시적으로 분리

## 10-2. 포인트인타임 공시 시점 통제가 아직 약하다
`nyse_fundamentals`는 기본적으로 `period_end` 중심이다.

문제:
- 백테스트에서 실제 공시 이전 시점에 해당 재무값을 사용하면 룩어헤드 바이어스가 생긴다.

상세 재무제표 쪽은 2026-03-18 기준으로
- `nyse_financial_statement_filings`
- `nyse_financial_statement_values`
- `nyse_financial_statement_labels`

에 `filing_date`, `accepted_at`, `available_at`, `accession_no`, `report_date`를 저장한다.

즉 raw ledger 차원에서는 point-in-time 기반 snapshot을 만들 수 있는 기반이 생겼다.
다만 현재 한계는 여전히 남아 있다.

- 전략/팩터 계층이 이 availability 규칙을 아직 직접 재사용하지 않는다
- `nyse_fundamentals`, `nyse_factors`는 여전히 별도 강화가 필요하다
- quarterly raw ledger는 provider truth를 보존하는 방향이라 Q4를 DB에서 합성하지 않는다
- `nyse_financial_statement_values`는 strict raw ledger 방향으로 재정의되었고,
  old mixed-state row를 PIT source로 곧바로 신뢰하지 않는 방향으로 정리됐다

즉, 실전형 팩터 백테스트로 가려면 이 부분이 매우 중요하다.

## 10-3. 생존편향 제어가 충분하지 않다
현재는 `status`와 일부 휴리스틱 필터가 있지만:
- listing_date
- delisting_date
- symbol change history
- corporate action identity history

가 별도 시계열 테이블로 정리돼 있지 않다.

즉, 현재 유니버스 필터는 유용하지만 완전한 point-in-time universe는 아니다.

## 10-4. 거래비용 모델이 없다
전략 계산은 사실상 frictionless market을 가정한다.

없는 것:
- 수수료
- 슬리피지
- bid/ask spread proxy
- 거래량 제약

ETF 전략에서는 영향이 덜할 수 있지만, 개별 종목 팩터 전략으로 가면 필수다.

## 10-5. 설정값이 코드에 하드코딩돼 있다
여러 모듈에서 아래 기본값이 반복된다.

- host=`localhost`
- user=`root`
- password=`1234`

영향:
- 보안 취약
- 환경 분리 어려움
- 테스트/운영 전환 불편

## 10-6. 패키지 인터페이스가 아직 정리 중이다
- `finance/__init__.py`는 일부만 re-export한다.
- `finance/data`에는 `__init__.py`가 없다.
- public API가 아직 안정적으로 정해진 느낌은 아니다.

즉, 내부 구조는 보이지만 외부 사용 계약은 아직 약하다.

## 10-7. 전략 결과 스키마가 완전히 표준화돼 있지 않다
예:
- 어떤 전략은 `Ticker`
- 어떤 전략은 `End Ticker`, `Next Ticker`
- 어떤 전략은 `Cash`, `Next Weight`

이 차이는 사람이 보기엔 문제없지만, 공통 리포팅/저장/비교 시스템을 만들 때 비용이 생긴다.

---

## 11. 데이터 품질 관점 분석

## 11-1. 가격 데이터
좋은 점:
- OHLCV 외에 배당과 주식분할도 저장함
- stock과 ETF를 동일 price ledger에 넣어 mixed-asset backtest에 바로 연결 가능
- 최근 hardening으로 Daily Market Update가 stock + ETF 공통 수집을 전제로 동작하도록 정리됨
- Daily Market Update 기본 source가 이제 raw exchange 전체보다
  `Profile Filtered Stocks + ETFs` 같은 managed universe 중심으로 기울어 있다
- yfinance batch fetch 경로가 이제
  - safer default batching
  - provider no-data vs rate-limit diagnostics
  - cooldown event tracking
  - timing breakdown metrics
  까지 포함하는 운영형 경로로 보강되었다
- broad managed source와 raw exchange source는 이제 다른 execution profile로 동작한다
  - managed broad source: `managed_fast`
  - managed short-window daily refresh: `managed_refresh_short`
  - raw broad source: `raw_heavy`
- 특히 `Profile Filtered Stocks + ETFs`의 `1d` 또는 최근 며칠 refresh는
  이제 long historical fetch와 다른 execution profile을 타므로,
  short-window 운영 refresh가 별도 계약으로 분리되어 있다

주의점:
- 거래소 세션 정보 없음
- 조정 가격 활용 규칙이 백테스트 전반에서 통일되어 있진 않음
- 현재 전략은 주로 `Close`를 사용함
- 대규모 전 유니버스 refresh는 여전히 외부 provider 속도에 영향을 크게 받음
- provider failure 분류는 아직 heuristic이며,
  `yfinance`가 structured batch error를 주지 않기 때문에 완전한 ground truth는 아니다
- speed optimization도 현재는
  single-worker + larger chunk 중심이라,
  완전한 high-throughput 병렬 fetch와는 다르다

즉, total return 정확도와 corporate action 처리 정책을 더 명확히 할 필요가 있다.

## 11-2. 프로파일 데이터
좋은 점:
- 유니버스 필터링에 실용적

주의점:
- `status`는 추정치다
- `is_spac`도 휴리스틱이다
- sector/industry/country도 provider 품질에 의존한다

즉, 유용하지만 절대적 ground truth로 보기엔 위험하다.

## 11-3. fundamentals 데이터
좋은 점:
- 백테스트용 최소 항목이 잘 정리돼 있다
- 결측 보정 로직이 있다
- factor 계산에 필요한 base field 범위가 이전보다 넓어졌다
- direct / derived / inferred source를 같이 추적할 수 있다

주의점:
- 보정값은 근사치다
- shares outstanding도 일부 경우 추정
- source가 yfinance라 계정명/coverage 일관성이 완벽하지 않을 수 있다
- broad coverage summary layer이지 strict PIT table은 아니다
- 전체 universe가 새 canonical 규칙으로 완전히 backfill된 상태는 아닐 수 있다

즉, 실용성은 높지만 accounting-grade precision은 아니다.

## 11-4. detailed financial statements 데이터
좋은 점:
- filing / concept 단위 세부 정보가 저장된다
- actual `period_end`를 raw fact 기준으로 저장한다
- `filing_date`, `accepted_at`, `available_at`, `accession_no`, `form_type`를 함께 저장한다
- filing 메타를 사람이 직접 확인할 수 있도록 `nyse_financial_statement_filings`가 별도로 존재한다

주의점:
- 라벨 표준화 문제
- 기업별/기간별 라벨 변형
- 같은 개념이 다른 라벨로 나타날 가능성
- provider의 `fiscal_year` / `fiscal_period`는 비교열 fact에서 filing 컨텍스트일 수 있어서,
  row 정체성은 `period_end`와 `accession_no`를 우선 기준으로 봐야 한다
- quarterly 저장은 raw truth 우선이라 10-Q의 비교 balance-sheet row와 10-K 기반 FY row가 함께 보일 수 있고,
  DB 저장 단계에서 synthetic Q4를 만들지 않는다
- `nyse_financial_statement_labels`는 convenience summary로 보는 것이 맞고,
  실제 strict loader는 `values`를 중심으로 읽어야 한다
- Phase 7에서는 사람이 raw timing을 바로 확인할 수 있도록
  `inspect_financial_statement_source()` 출력과
  `load_statement_timing_audit(...)` inspection path를 추가했다
- 또한 `upsert_financial_statements(..., periods=N)`는 현재
  raw fact `period_end`가 아니라 reported period(`report_date` 우선, 없으면 `period_end`) 기준으로
  latest N period를 제한한다
- 다만 `N=0`이면 source가 가진 전체 usable history를 그대로 적재한다
- 그리고 같은 symbol/freq scope는 canonical refresh 방식으로 다시 쓰기 때문에,
  old slicing semantics row를 유지하지 않는다

즉, powerful하지만 정교한 semantic normalization이 뒤따라야 한다.

## 11-5. factors 데이터
좋은 점:
- valuation/profitability/growth를 폭넓게 포함한다
- price attachment metadata가 있어 해석 가능성이 좋아졌다
- yield / margin / leverage / growth 계열이 이전보다 풍부해졌다

주의점:
- `period_end` 기준 asof 가격 매칭은 유용하지만,
  실제 공시 시점 기반으로는 아닐 수 있다
- point-in-time strictness는 아직 부족하다
- 따라서 현재 `nyse_factors`는 broad research layer로 이해하는 것이 맞다

---

## 12. 현재 기준으로 가장 중요한 함수들

## 12-1. 데이터 적재
- `finance.data.nyse.load_nyse_listings`
- `finance.data.nyse_db.load_nyse_csv_to_mysql`
- `finance.data.asset_profile.collect_and_store_asset_profiles`
- `finance.data.fundamentals.upsert_fundamentals`
- `finance.data.factors.upsert_factors`
- `finance.data.financial_statements.upsert_financial_statements`

## 12-2. 전략 실행
- `finance.data.data.get_ohlcv`
- `finance.engine.BacktestEngine`
- `finance.strategy.EqualWeightStrategy`
- `finance.strategy.GTAA3Strategy`
- `finance.strategy.RiskParityTrendStrategy`
- `finance.strategy.DualMomentumStrategy`
- ETF 전략 3종은 Phase 12 first pass부터
  `min_price` investability filter를 전략 함수 자체에서 받고,
  UI/runtime에서는 turnover 기반 cost와 benchmark overlay까지 함께 붙는다.
- strict annual family 3종도 Phase 12 first pass부터
  같은 real-money contract를 사용하며,
  `quality_snapshot_equal_weight` 경로에 `min_price` investability filter가 추가되어
  annual strict ranking candidate에도 실제로 적용된다.
- 그리고 same runtime helper가 현재는 benchmark가 있을 때
  validation surface까지 함께 만든다.
  즉 real-money 결과는 이제
  - gross / net / cost
  - benchmark overlay
  - benchmark-relative drawdown / rolling underperformance diagnostics
  를 한 번에 갖는 구조다.
- strict annual family는 여기에 더해 optional
  `underperformance guardrail`까지 전략 규칙으로 받을 수 있고,
  이때 trailing excess return guardrail trigger / state / blocked-count가
  result row와 real-money surface에 같이 남는다.

## 12-3. 성과 요약
- `finance.performance.portfolio_performance_summary`
- `finance.performance.make_monthly_weighted_portfolio`
- `finance.visualize.plot_equity_curves`

---

## 13. 지금 당장 이해해야 하는 핵심 사실

### 사실 1
이 프로젝트는 아직 "전략 백테스트 엔진"보다 "연구용 퀀트 워크벤치"에 더 가깝다.

### 사실 2
데이터 계층은 장기적으로 주식 팩터 전략을 할 준비가 꽤 되어 있다.

### 사실 3
하지만 현재 샘플 전략은 대부분 ETF 자산배분형이다.

### 사실 4
DB 적재 계층은 실제 운영용 파이프라인처럼 보이지만, 전략 계층과 완전 통합되진 않았다.

### 사실 5
향후 고도화에서 가장 중요한 축은 아래 셋이다.

1. point-in-time 데이터 정합성
2. DB 기반 전략 입력 통일
3. 전략 결과 스키마 표준화

---

## 14. 향후 리팩터링 우선순위 제안

## 14-1. 1순위
백테스트 입력 데이터 소스를 통일한다.

권장 방향:
- 실험용: yfinance 직로딩
- 운영용: DB 로딩

둘을 명시적으로 분리하거나, 가능하면 DB 기준으로 수렴시키는 것이 좋다.

## 14-2. 2순위
공시 시점 기반 팩터 파이프라인을 만든다.

필요한 연결:
- `financial_statements.py`의 `filing_date`, `accepted_at`, `available_at`
- `factors.py`의 계산 기준 시점
- 백테스트 리밸런싱 시점

## 14-3. 3순위
전략 결과 공통 스키마를 정의한다.

예:
- `Date`
- `Holdings`
- `Weights`
- `Cash`
- `Total Balance`
- `Total Return`
- `Rebalancing`

## 14-4. 4순위
설정 관리 계층을 만든다.

대상:
- DB 연결
- batch size
- sleep
- retry
- 로그 경로

## 14-5. 5순위
리서치용 샘플과 운영 파이프라인을 분리한다.

예:
- `sample.py`는 examples로 이동
- ingestion jobs는 별도 jobs/module화

---

## 15. 퀀트 관점에서 추가되면 좋은 데이터

이미 기존 감사 문서에서 제안된 항목을 현재 코드 맥락으로 다시 정리하면 아래가 핵심이다.

## 15-1. 매우 중요
- filing/accepted 시점 기반 point-in-time 재무 데이터
- listing/delisting/symbol change history
- benchmark 및 risk-free rate 시계열
- 거래비용 근사용 유동성 데이터

## 15-2. 중요
- 섹터/산업 분류 이력
- index membership history
- 배당 이벤트 상세 이력
- ETF 전용 메타 확장

## 15-3. 고급 확장
- analyst estimates / surprise
- short interest / borrow fee
- options implied volatility

---

## 16. 현재 패키지를 한 문장으로 정의하면

현재 `finance` 패키지는:

"NYSE 유니버스, 가격, 재무, 팩터 데이터를 수집·저장하면서 동시에 ETF/자산배분형 전략을 빠르게 연구할 수 있게 만든 초기 단계 퀀트 리서치 패키지"

라고 정의하는 것이 가장 정확하다.

---

## 17. 이후 대화에서 이 문서를 어떻게 사용할지

이후 `finance` 관련 질문에서는 이 문서를 기준으로 아래 순서로 이해하면 된다.

1. 지금 묻는 내용이 데이터 적재 문제인지 전략 문제인지 먼저 구분
2. 데이터 적재면 어느 DB/테이블에 해당하는지 확인
3. 전략 문제면 `engine -> transform -> strategy -> performance` 순서로 본다
4. 팩터 문제면 `fundamentals -> factors -> point-in-time 이슈`를 같이 본다

즉, 이 문서는 단순 설명 문서가 아니라 이후 분석과 설계 대화의 기준 좌표다.
