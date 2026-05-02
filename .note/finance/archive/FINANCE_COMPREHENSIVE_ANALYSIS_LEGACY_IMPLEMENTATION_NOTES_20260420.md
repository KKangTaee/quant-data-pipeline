# Finance Comprehensive Analysis Legacy Implementation Notes

## 목적

이 문서는 예전에 `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`의 `3-3. 상세 구현 메모`에 들어 있던 긴 legacy 구현 메모를 보관한다.

`FINANCE_COMPREHENSIVE_ANALYSIS.md`는 이제 finance 시스템의 high-level current-state map으로 관리한다.
따라서 긴 phase별 구현 기록, QA 흔적, 과거 판단 메모는 본문에 계속 두지 않고 이 archive 문서로 분리했다.

## 읽는 방법

- 현재 시스템 구조를 파악할 때는 먼저 `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`를 본다.
- phase별 현재 상태는 `.note/finance/MASTER_PHASE_ROADMAP.md`와 각 `phase*/` 문서를 본다.
- 코드 흐름은 `.note/finance/code_analysis/`를 본다.
- DB / data 의미는 `.note/finance/data_architecture/`를 본다.
- 이 문서는 과거 구현 배경, 당시 판단, 오래된 상세 메모를 확인할 때만 참고한다.

## 주의

- 아래 내용은 원문 보존용 legacy archive다.
- 현재 구현 상태와 다를 수 있다.
- 현재 상태를 판단할 때는 최신 roadmap, phase 문서, code, code_analysis, data_architecture를 우선한다.

---

### 3-3. 상세 구현 메모

이 섹션은 예전 종합 분석에서 누적된 상세 구현 기록을 보존하는 곳이다.
다만 앞으로는 여기에 긴 변경 이력을 계속 덧붙이지 않는다.
현재 시스템을 빠르게 이해하려면 `3-1. 현재 시스템 구조`와 `3-2. Phase별 구현 히스토리`를 먼저 읽고,
세부 배경이나 과거 판단이 필요할 때만 아래 legacy 메모를 참고한다.

#### 3-3-1. 이 메모의 역할

`3-3`은 현재 사양 문서가 아니라 과거 구현 맥락을 보존하는 archive다.
여기에는 phase 진행 중 쌓인 UI 변경, runtime 연결, strategy 확장, DB/ingestion 판단,
QA 피드백, backtest 검증 메모가 섞여 있다.

따라서 이 섹션을 읽을 때는 다음처럼 구분한다.

- `현재 상태`: 지금 코드와 문서가 실제로 따르는 구조다. 보통 `3-1`, `4~12`, phase 문서, roadmap에서 확인한다.
- `당시 기록`: 특정 phase 당시의 판단이나 구현 배경이다. 현재와 다를 수 있다.
- `참고 가치`: 왜 어떤 기능이 생겼는지, 왜 어떤 UI 문구가 바뀌었는지, 어떤 위험을 고려했는지 확인할 때 유용하다.
- `주의점`: 이 섹션만 보고 현재 기능이 그대로 동작한다고 판단하지 않는다.

#### 3-3-2. 현재 3-3에 섞여 있는 내용

기존 상세 메모에는 다음 내용이 한 곳에 누적되어 있었다.

- 전체 architecture 그림과 data / runtime / strategy / UI 연결 설명
- phase별 구현 기록과 practical closeout 판단
- Backtest UI, Compare, History, Saved Portfolio, Guides, Glossary UX 변경 이력
- GTAA, Equal Weight, Risk Parity, Dual Momentum, Global Relative Strength 구현 메모
- Strict Annual / Quarterly Quality, Value, Quality + Value 관련 구현 메모
- EDGAR, statement shadow table, coverage, freshness, run artifact 관련 data/DB 메모
- PIT, survivorship, dynamic universe, promotion, pre-live, deployment readiness 관련 정책 메모
- smoke run, backtest 결과, 후보 판단, QA 피드백, warning 문구 변경 기록

이 내용들은 모두 보존 가치가 있지만, 한 문단에 계속 쌓이면 나중에 현재 상태와 과거 기록을 구분하기 어렵다.
그래서 앞으로는 아래 관리 원칙을 따른다.

#### 3-3-3. 상세 메모 관리 원칙

- `3-3`에는 새 긴 구현 이력을 직접 append하지 않는다.
- 현재 동작이 바뀌면 이 문서의 해당 주제 섹션을 짧게 수정한다.
- phase 진행 기록은 해당 `.note/finance/phases/phase*/` 문서와 `WORK_PROGRESS.md`에 남긴다.
- 설계 판단이나 사용자 질문에서 나온 durable conclusion은 `QUESTION_AND_ANALYSIS_LOG.md`에 남긴다.
- backtest 결과, 후보 비교, 실험 성과는 `.note/finance/backtest_reports/` 또는 strategy별 backtest log에 남긴다.
- 현재 후보나 near-miss 후보처럼 기계적으로 다시 읽어야 하는 정보는 `CURRENT_CANDIDATE_REGISTRY.jsonl`을 우선한다.
- 기존 기록을 옮기거나 요약할 때는 원문을 먼저 보존하고, 그 다음 current-state 요약을 별도로 만든다.
- `현재`, `최근`, `나중에` 같은 표현은 가능하면 `2026-04-20 기준`, `Phase 25 기준`처럼 기준점을 붙인다.

#### 3-3-4. 앞으로 새 내용을 기록하는 규칙

새로운 상세 메모가 정말 필요하다면 아래 형식을 사용한다.
단, 10~15줄을 넘는다면 이 섹션이 아니라 phase work-unit 문서, backtest report, 또는 별도 guide 문서로 분리한다.

```md
##### YYYY-MM-DD / Phase N / 짧은 제목
- 구분: current_state | historical_note | decision | caveat | deprecated
- 관련 영역: data | db | runtime | strategy | web_ui | history | real_money | pre_live
- 현재 상태에 미치는 영향:
- 근거 문서 / 코드:
- 나중에 다시 확인할 조건:
```

기록 위치를 고르는 기준은 다음과 같다.

- 제품의 현재 구조 설명이면 `FINANCE_COMPREHENSIVE_ANALYSIS.md`의 해당 주제 섹션에 반영한다.
- phase 진행 상황이면 해당 phase TODO, completion, next-phase 문서에 반영한다.
- 반복 가능한 테스트 결과이면 `backtest_reports/`에 남긴다.
- 용어가 반복되면 `FINANCE_TERM_GLOSSARY.md`에 남긴다.
- 다음 agent가 따라야 할 작업 방식이면 `AGENTS.md` 또는 active skill 문서를 검토한다.

#### 3-3-5. Legacy 상세 메모 색인

아래 legacy 본문을 찾을 때는 대략 다음 주제로 읽으면 된다.

- `architecture / layer model`: finance package의 data, loader, strategy, UI 흐름
- `web product surface`: Streamlit Backtest, Compare, History, Guides, Glossary, Ingestion 화면
- `history / load into form / saved replay`: run history, saved compare, saved portfolio 재실행 흐름
- `real-money / promotion / pre-live`: promotion, shortlist, paper, watchlist, hold, deployment readiness 구분
- `GTAA / ETF strategies`: GTAA 후보, expanded universe, ETF 전략 QA
- `strict annual`: Quality, Value, Quality + Value annual factor strategy 구조
- `quarterly / dynamic PIT`: quarterly prototype, dynamic statement shadow, PIT timing
- `data / DB / ingestion`: EDGAR, statement shadow, coverage, freshness, refresh payload
- `runtime / smoke validation`: compile, import, DB-backed smoke, run artifact, warning metadata
- `candidate / compare / weighted`: current candidate re-entry, compare form, weighted portfolio, saved portfolio
- `new strategy expansion`: Phase 24 Global Relative Strength와 신규 strategy family 연결

#### 3-3-6. Legacy 상세 구현 메모

아래 내용은 기존 상세 메모 원문이다.
현재 상태를 판단할 때는 먼저 `3-1`, `3-2`, roadmap, phase 문서, 최신 code를 확인하고,
이 부분은 과거 구현 배경을 추적하는 용도로 사용한다.

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
- 초기 Phase 4에서는 메인 Streamlit 앱 하나를 유지하되,
  수집 탭과 백테스트 탭을 분리하는 방향으로 시작했다.
- 이후 UI가 커지면서 현재 구현 기준의 메인 앱은 explicit top navigation을 사용한다.
  `Overview`의 상단 상태 metric은 active phase의 준비/closeout 상태를 짧게 보여주는 용도로 쓰였으며,
  이 상세 메모가 작성되던 당시 기준 값은 `Phase 14 Practical Closeout`였다.
  상단 페이지는 현재:
  - `Overview`
  - `Ingestion`
  - `Backtest`
  - `Ops Review`
  - `Guides`
  - `Glossary`
  로 나뉘고,
  helper 모듈은 더 이상 Streamlit `pages/` auto-discovery에 섞이지 않도록
  실제 페이지 경로 밖으로 분리했다.
  최근 `Guides` 페이지는 단순 문서 링크 모음뿐 아니라,
  `Promotion / Shortlist` 승격 흐름과 단계별 해석을 한국어 요약으로 먼저 보여주는
  operator-facing quick reference 역할도 함께 갖는다.
  이후에는 `어떻게 다음 단계로 가나` 안에
  - 상태가 실제로 어디에 보이는지
  - `Watch / Caution / Unavailable / Error`가 각각 무엇을 뜻하는지
  까지 같이 설명해, 실제 결과 탭과 가이드 문서 사이의 연결을 더 직접적으로 만들었다.
  최근 보강으로는
  - `Hold 해결 가이드`가 정확히 어디에 나타나는지
  - `Probation / Monitoring`, `최근 구간 / Out-of-Sample Review`, `Deployment Readiness`, `Strategy Highlights`가 각각 어떤 화면 surface인지
  까지 `Guides`에서 바로 확인할 수 있게 정리됐다.
  이어서 `Guides`에는 `Real-Money Contract 값 해설` 섹션도 추가되어,
  `Advanced Inputs > Real-Money Contract`에 나오는
  `Minimum Price`, `Transaction Cost`, `Benchmark Ticker`,
  strict annual의 benchmark / liquidity / validation / guardrail threshold,
  ETF의 `Min ETF AUM`, `Max Bid-Ask Spread`
  가 각각 무엇을 뜻하고 왜 필요한지, 결과의 어느 surface에 영향을 주는지까지
  operator가 UI 안에서 바로 다시 읽을 수 있게 됐다.
  이후 strict annual 유동성 입력 tooltip도 보강되어,
  `Min Avg Dollar Volume 20D ($M)`는 OHLCV `close × volume` 기반 trailing 20-day average dollar volume 계산을,
  `Min Liquidity Clean Coverage (%)`는 그 후보 필터가 전략-level `Liquidity Policy` 해석으로 이어지는 구조를
  field help에서 직접 설명한다.
  같은 strict annual `Real-Money Contract` 안의 robustness threshold tooltip도 한 번 더 보강되어,
  `Max Underperformance Share`, `Min Worst Rolling Excess`,
  `Max Strategy Drawdown`, `Max Drawdown Gap vs Benchmark`
  가 각각 무엇을 막기 위한 기준인지와
  `rolling 구간`이 moving comparison window라는 뜻을 field 주변에서 바로 읽을 수 있게 됐다.
  Phase 14 controlled factor expansion first pass에서는 strict annual UI factor surface도 small-set으로 넓어져,
  Quality family는 `interest_coverage`, `ocf_margin`, `fcf_margin`, `net_debt_to_equity`,
  Value family는 `liquidation_value`를 추가로 고를 수 있게 됐다.
  이 first pass는 default factor를 바꾸지 않고, sign 해석이 비교적 명확한 후보만 옵션으로 여는 보수적 widening이다.
  이어서 representative near-miss case study first pass도 정리되어,
  strict annual은 `validation / validation_policy`,
  ETF family는 `operability + validation watch/caution boundary`
  를 family별 calibration의 다음 active 질문으로 좁혀 읽는 기준점이 생겼다.
	  이어서 `Guides`에는
	  - 데이터 최신화
	  - single strategy 확인
	  - Real-Money 검증 신호 확인
	  - hold blocker 해결
	  - compare
	  - history / backtest report 정리
	  - Pre-Live 운영 점검
	  - 실전 후보 판단
	  까지를 `1단계 ~ 8단계` 형태로 읽는 operator runbook도 추가됐다.
	  최근에는 여기서 Real-Money를 "개별 백테스트 실행의 검증 신호"로,
	  Phase 25 Pre-Live 운영 점검을 "paper tracking / watchlist / 보류 / 재검토를 기록하는 운영 절차"로
	  명확히 분리해 사용자가 두 흐름을 같은 기능으로 혼동하지 않게 했다.
	  Phase 25 kickoff 기준으로 이 경계는 phase plan과 first work-unit 문서에도 반영되어,
	  다음 구현은 pre-live 후보 기록 포맷과 저장 위치를 정하는 방향으로 진행된다.
  같은 `Reference` 그룹 안의 `Glossary` 페이지는
  `.note/finance/FINANCE_TERM_GLOSSARY.md`를 그대로 source로 사용하면서,
  제목/본문 검색이 가능한 operator-facing 용어 사전 UI를 제공한다.
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
- Phase 24 first implementation에서는 같은 price-only infrastructure 위에
  `Global Relative Strength` core strategy와 DB-backed runtime wrapper가 추가되었다.
  이후 `Backtest > Single Strategy`, `Compare & Portfolio Builder`, history payload,
  `Load Into Form`, `Run Again`, saved portfolio replay override까지 연결되어
  신규 전략이 제품 화면에서 반복 실행 가능한 surface로 노출된다.
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
- Phase 14 first pass에서는 여기서 한 단계 더 나아가,
  새로운 history record(schema v2)가
  `promotion / shortlist / probation / monitoring / deployment` 상태와
  `validation / benchmark policy / liquidity policy / validation policy / guardrail policy / ETF operability / rolling / out-of-sample / price freshness`
  를 `gate_snapshot`으로 함께 저장하도록 보강되었다.
  즉 이후 blocker audit는 report 문서만이 아니라
  persistent history record 기준으로도 다시 집계할 수 있게 됐다.
- Phase 12부터는 ETF 전략군(`GTAA`, `Risk Parity Trend`, `Dual Momentum`)에
  first-pass real-money hardening이 추가되어,
  `Minimum Price`, `Transaction Cost (bps)`, `Benchmark Ticker`를 입력할 수 있고,
  결과도 gross/net/cost/benchmark 기준으로 같이 읽을 수 있게 되었다.
- 그리고 next ETF operability pass에서는
  current `nyse_asset_profile` snapshot을 이용한
  `Min ETF AUM ($B)` / `Max Bid-Ask Spread (%)` policy도 추가되어,
  ETF 전략군은 이제 "현재 시점 기준으로 규모가 너무 작거나 스프레드가 너무 넓은 ETF가 섞여 있는지"를
  `etf_operability_status = normal / watch / caution / unavailable`
  로 같이 읽고,
  이 상태를 `promotion_decision`에도 반영한다.
  다만 이는 current-snapshot operability overlay이며,
  point-in-time ETF operability history를 복원한 것은 아니다.
- Phase 13 ETF second pass부터는
  `GTAA`, `Risk Parity Trend`, `Dual Momentum`도 optional
  - `underperformance guardrail`
  - `drawdown guardrail`
  actual rule을 받을 수 있게 되었고,
  trailing benchmark-relative 약세나 낙폭 악화가 심하면
  다음 ETF rebalance는 cash로 물러나게 할 수 있다.
  이 값들은 single / compare / history / saved-portfolio compare context까지 같이 왕복된다.
- 이후 Backtest strategy surface도 first-pass 수준으로 재정리되어,
  `Single Strategy`와 `Compare & Portfolio Builder`의 top-level 목록은
  - `Quality`
  - `Value`
  - `Quality + Value`
  family 중심으로 단순화되었고,
  각 family 안에서 strict variant를 고르는 구조로 바뀌었다.
  현재 active family surface는
  - `Quality`: `Strict Annual`, `Strict Quarterly Prototype`
  - `Value`: `Strict Annual`, `Strict Quarterly Prototype`
  - `Quality + Value`: `Strict Annual`, `Strict Quarterly Prototype`
  이다.
  broad `Quality Snapshot` research path는 코드에 남아 있지만,
  현재 active family variant에서는 노출하지 않는다.
- 이 변경은 UI/orchestration surface 정리이지,
  quality/value 계산 로직을 `backtest.py`로 이동시킨 것은 아니다.
  현재 역할은 그대로:
  - `finance/strategy.py` = simulation / decision layer
  - `finance/sample.py` = DB-backed factor / snapshot assembly layer
  - `app/web/runtime/backtest.py` = runtime wrapper / bundle assembly layer
  - `app/web/pages/backtest.py` = Streamlit form / compare / history orchestration
  이다.
- 또한 family / variant / concrete strategy key 매핑은
  새 `app/web/backtest_strategy_catalog.py`로 분리되어,
  history / `Load Into Form` / compare prefill도 기존 concrete strategy key를 유지한 채
  family UI로 복원된다.
- 같은 Phase 12에서 `Strict Annual Family`
  (`Quality Snapshot (Strict Annual)`, `Value Snapshot (Strict Annual)`, `Quality + Value Snapshot (Strict Annual)`)
  도 first-pass real-money hardening이 추가되어,
  annual strict single/compare/history 경로에서도
  `Minimum Price`, `Minimum History (Months)`, `Transaction Cost (bps)`, `Benchmark Ticker`,
  그리고 guardrail용 reference ticker를 포함한
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
- 이후 same strict annual contract에는
  `Minimum History (Months)` investability proxy와
  `Benchmark CAGR`, `Net CAGR Spread`, `Benchmark Coverage`
  도 first pass로 추가되어,
  strategy-vs-benchmark 판단을 더 직접적으로 읽을 수 있게 되었다.
- 그리고 strict annual promotion contract는 later pass에서 더 강화되어,
  `Max Strategy Drawdown (%)`와
  `Max Drawdown Gap vs Benchmark (%)`를 입력할 수 있고,
  `guardrail_policy_status = normal / watch / caution / unavailable`가
  `promotion_decision`에 함께 반영된다.
  이 변경은 actual strategy-side drawdown rule을 더한 것은 아니고,
  drawdown-based promotion review를 더 엄격하게 만든 쪽에 가깝다.
- Phase 13 first pass부터는 이 `promotion_decision` 위에
  candidate shortlist contract가 추가되어,
  결과 surface가
  - `watchlist`
  - `paper_probation`
  - `small_capital_trial`
  - `hold`
  상태로도 다시 읽히게 되었다.
  현재 first pass는
  - `hold -> hold`
  - `production_candidate -> watchlist`
  - `real_money_candidate -> paper_probation`
  을 기본으로 두고,
  strict annual 계열 중 actual guardrail과 candidate-equal-weight benchmark contract가 함께 맞는 경우에만
  보수적으로 `small_capital_trial`을 추천한다.
  이 상태는 single `Real-Money`, `Execution Context`, compare `Strategy Highlights`와 meta 표에도 같이 남는다.
- 그리고 그 shortlist 위에 probation / monitoring workflow first pass가 더해져,
  각 run이 지금
  - `not_ready`
  - `watchlist_review`
  - `paper_tracking`
  - `small_capital_live_trial`
  중 어느 probation 상태인지,
  그리고 monitoring은
  - `blocked`
  - `routine_review`
  - `heightened_review`
  - `breach_watch`
  중 어디로 읽어야 하는지까지 같이 보여주게 되었다.
  이 layer는 새 전략 규칙을 더 추가한 것이 아니라,
  기존 `validation / benchmark / liquidity / guardrail / freshness` 정책 상태와
  actual guardrail trigger count를 운영 언어로 다시 해석한 것이다.
- 그리고 Phase 13 다음 pass에서는 rolling / out-of-sample validation workflow도 추가되어,
  이제 결과 surface가 최근 `12M` 또는 `252D` validation window와
  전체 aligned 기간의 앞/뒤 절반 split-period를 따로 읽을 수 있게 되었다.
  이 layer는
  - `rolling_review_status = normal / watch / caution / unavailable`
  - `out_of_sample_review_status = normal / watch / caution / unavailable`
  를 만들고,
  최근 window excess return, recent drawdown gap, split-period excess deterioration를 같이 남긴다.
  현재 first pass는 이를 promotion을 직접 바꾸는 rule이 아니라,
  probation / monitoring을 더 보수적으로 읽게 하는 deployment-readiness review layer로 사용한다.
- 그 위에 deployment-readiness checklist first pass도 추가되어,
  이제 `Universe Contract`, `Benchmark Availability`, 각 policy status,
  `Shortlist`, `Probation`, `Monitoring`, `Rolling Review`, `Out-Of-Sample Review`
  를 한 장의 checklist row로 같이 읽을 수 있다.
  이 checklist는
  - `blocked`
  - `review_required`
  - `watchlist_only`
  - `paper_only`
  - `small_capital_ready`
  - `small_capital_ready_with_review`
  같은 deployment status를 만들고,
  single `Real-Money`, `Execution Context`, compare `Strategy Highlights`, compare meta table까지 같이 연결된다.
  현재는 deployment를 자동 승인하는 rule이 아니라,
  실제 운용 전 점검표를 product surface에서 읽는 summary layer다.
- 이후 `Real-Money` 탭 UX도 한 번 더 정리되어,
  결과 surface는 이제
  - `현재 판단`
  - `검토 근거`
  - `실행 부담`
  - `상세 데이터`
  네 묶음으로 읽히게 되었다.
  이 변경은 runtime/meta 계산을 바꾼 것이 아니라,
  `Promotion / Shortlist / Probation / Deployment`를 먼저 보게 하고,
  benchmark / rolling / policy는 이유 확인용으로,
  cost / liquidity / ETF operability는 실행 부담 확인용으로 다시 배치한 UI-layer 정리다.
  낮은 신호의 raw detail은 expander나 마지막 상세 탭으로 내려가서,
  사용자가 "지금 상태가 뭔지"를 먼저 판단하기 쉬운 구조가 되었다.
  이후 시각적 그룹화도 한 번 더 보강되어,
  각 섹션은 border container 안에서
  - 제목
  - 짧은 설명
  - 관련 metric / status / rationale
  순서로 보이게 되었다.
  그래서 같은 탭 안에서도 `승격`, `숏리스트`, `probation`, `deployment`,
  `benchmark`, `validation`, `ETF operability`, `guardrail`
  같은 묶음을 서로 더 쉽게 구분할 수 있다.
  그리고 `Promotion Decision = hold`일 때는
  `Real-Money > 현재 판단` 안에 별도의 `Hold 해결 가이드`가 같이 나타난다.
  이 가이드는 raw rationale code를 그대로 노출하는 대신,
  - 항목
  - 현재 상태
  - 상태를 보는 위치
  - 이 상태의 뜻
  - 바로 해볼 일
  형태로 다시 정리해서,
  사용자가 `resolve_validation_gaps_before_promotion`을 실제 수정 액션으로 바로 읽을 수 있게 한다.
  이후 `실행 부담` 탭도 한 번 더 보강되어,
  특히 `Liquidity Policy`는 이제 별도 섹션에서
  - Policy Status
  - Min Avg Dollar Volume 20D
  - Min Clean Coverage
  - Actual Clean Coverage
  - Liquidity Excluded Rows
  를 같이 보여준다.
  전략 입력 UX도 같은 원칙으로 한 번 더 정리되어,
  `Advanced Inputs`는 이제 "핵심 실행 계약"과 "추가 정책"을 분리해서 읽게 되었다.
  ETF 전략과 strict annual family에서는
  - 핵심 계약: timeframe / option / rebalance / universe / factors / top N
  - 추가 정책: overlay / real-money contract / guardrails
  구조를 기본 패턴으로 사용한다.
  이 변경은 strategy logic을 바꾼 것이 아니라,
  앞으로 옵션이 더 늘어나도 각 전략 form이 한 줄씩 길어지지 않도록 정리한 UI-layer 개선이다.
  그리고 `unavailable / watch / caution` 상태일 때는
  왜 그 상태가 떴는지와
  무엇을 바꾸면 되는지를 한국어 안내문으로 바로 붙여서,
  `Hold 해결 가이드 -> 실행 부담` 이동이 실제 수정 액션으로 이어지게 했다.
- 그리고 single run 결과 헤더인 `Latest Backtest Run` 아래도 다시 정리되어,
  이제는
  - 결과 읽는 순서
  - 이번 실행에 포함된 보기
  - 이번 실행의 주의 사항
  이 세 가지를 먼저 한국어로 묶어서 보여준다.
  기존처럼 caption과 warning이 흩어져 있는 방식보다,
  사용자가 어떤 탭부터 보면 되는지와 어떤 주의문을 함께 봐야 하는지를 더 빨리 파악할 수 있게 되었다.
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
  현재는 `Strategy-Specific Advanced Inputs`의 해당 전략 블록에서 관리되며,
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
- 또한 history detail drilldown도 Phase 14 first pass에서 보강되어,
  schema v2 record가 있을 경우
  `Promotion / Shortlist / Probation / Monitoring / Deployment`와
  policy 상태를 `Gate Snapshot` 표로 바로 다시 읽을 수 있다.
- 또한 single-strategy 결과는 최고점/최저점/end marker와 `Best / Worst Period` marker,
  top/bottom period 표까지 볼 수 있고,
  compare view에서는 total return overlay, overlay end marker, strategy highlight table, focused strategy drilldown까지,
  weighted portfolio 결과에서도 같은 marker / balance-extremes / period-extremes 읽기 흐름과
  strategy contribution amount/share view까지 확인할 수 있게 되었다.
- 다만 의미를 분리해서 보면,
  compare 결과는 각 전략의 own backtest에 붙는 `promotion / shortlist / deployment` 해석을 그대로 보여주는 반면,
  weighted portfolio 결과는 여러 compare 결과를 monthly composite로 합친 연구용 포트폴리오 표면이다.
  즉 weighted bundle 자체에는 별도의 real-money semantics가 새로 생기지 않고,
  실제 승격 판단은 여전히 구성 전략 단위에서 읽는 것이 맞다.
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
- 따라서 saved portfolio는 실전 운용 객체라기보다,
  compare -> weighted builder -> rerun을 다시 열 수 있는 재현용 연구 아티팩트에 가깝다.
  Phase 17에서 다루어야 할 것은 이 객체에 새로운 승격 의미를 부여하는 것이 아니라,
  후보 개선 작업을 반복 재현할 수 있는 operator bridge로서의 역할을 명확히 적는 것이다.
- Phase 20 first work unit에서는 이 흐름 앞단도 보강되어,
  `Compare & Portfolio Builder`에서
  현재 문서화된 candidate를 compare form으로 다시 불러오는
  `Current Candidate Re-entry` surface가 추가되었다.
- 이 surface는
  current candidate registry를 읽어
  - current anchor
  - lower-MDD near miss
  - cleaner alternative
  를 한 표로 다시 보여주고,
  `Load Current Anchors` 또는 custom bundle selection으로
  current candidate를 compare form에 바로 다시 채울 수 있게 한다.
- 그리고 이 candidate list는
  매번 백테스트 결과가 자동으로 쌓이는 공간이 아니라,
  `CURRENT_CANDIDATE_REGISTRY.jsonl`에 curate된 active candidate만 보여주는 ingress로 해석하는 것이 맞다.
- QA feedback 이후에는
  이 surface가 compare를 즉시 실행하는 기능이 아니라
  compare form의 전략/기간/override를 다시 채우는 기능이라는 점도
  화면에서 먼저 읽히게 보강되었다.
- 이어서 compare의 기본 동선을 먼저 보이도록,
  `Strategies` 선택은 상단에 그대로 두고
  current candidate 재진입은 그 아래의 secondary expander인
  `Quick Re-entry From Current Candidates` 안으로 이동했다.
- 설명도 늘 펼쳐진 줄글 대신
  `What This Does` expander 안으로 정리되어,
  compare의 기본 사용 흐름을 가리지 않게 되었다.
- 이후 QA에서는
  `Load Current Anchors`, `Load Lower-MDD Near Misses` 같은 용어가
  operator 외 사용자에게 다소 내부자 언어처럼 보인다는 피드백이 나와,
  버튼 이름을
  `Load Recommended Candidates`,
  `Load Lower-MDD Alternatives`
  처럼 더 직접적인 표현으로 바꿨다.
- 각 버튼 아래에는
  - 대표 후보를 한 번에 불러오는 버튼인지
  - 더 방어적인 대안 후보를 불러오는 버튼인지
  - 아니면 아래 표에서 직접 고르는 흐름인지
  한 줄 설명을 붙여,
  왜 버튼이 두 개 있는지 화면에서 바로 이해할 수 있게 했다.
- 이후 한 번 더 UX를 다듬으면서,
  current candidate 재진입은
  - `Quick Bundles`
  - `Pick Manually`
  두 탭으로 나눠 읽히게 정리했다.
- 이때 `Pick Manually` 탭에는
  현재 목록이 새 백테스트 실행이나 Markdown 문서 생성만으로 자동 누적되는 것이 아니라,
  `CURRENT_CANDIDATE_REGISTRY.jsonl`의 active row를 읽는 구조라는 점도
  화면 안에서 바로 설명하도록 보강했다.
- compare form에 candidate bundle을 불러온 직후 뜨는 카드도
  `What Changed In Compare` 중심의 짧은 내부자 표현 대신,
  `Compare Form Updated` 아래에서
  - 어떤 방식으로 불러왔는지
  - 어떤 묶음을 불러왔는지
  - 기간이 어떻게 채워졌는지
  - 어디에서 값을 다시 확인하면 되는지
  - 다음에 무엇을 눌러야 하는지
  를 더 직접적으로 읽히게 정리했다.
- 이후 QA에서는
  이 카드 표가 `Trend Filter`, `Market Regime`만 보여서
  실제 prefill된 핵심 계약과 비교하기에 부족하다는 피드백이 나와,
  표에 `Weighting Contract`, `Risk-Off Contract`도 같이 보이게 보강했다.
- 이후 QA에서는 compare의
  `Strategy-Specific Advanced Inputs`에서
  family selector와 실제 snapshot 설정이 떨어져 보여
  GTAA처럼 한 섹션으로 읽히지 않는다는 피드백이 나왔다.
- 이후 Phase 23에서 Annual / Quarterly variant 즉시 갱신 문제가 확인되어,
  현재 compare 화면은 아래 구조로 정리되어 있다.
  - `Strategies`: compare에 넣을 전략 family 선택
  - `Compare Period & Shared Inputs`: `Start Date`, `End Date`, `Timeframe`, `Option`
  - `Strategy-Specific Advanced Inputs`: 선택된 전략별 border box
  - 각 `Quality / Value / Quality + Value` box 안의 Annual / Quarterly variant selector
- 이 변경으로 compare 화면에서
  - Annual / Quarterly를 바꾸면 별도 Apply 버튼 없이 하단 입력 UI가 즉시 바뀌고
  - variant 선택과 해당 전략 세부 입력을 같은 box 안에서 읽을 수 있게 되었다.
- 이후 QA에서는 strict annual `Real-Money Contract`의
  `Benchmark Contract` 설명이 아직 축약되어 있어서
  `Candidate Universe Equal-Weight`가 무엇인지 바로 이해하기 어렵다는 피드백이 나왔다.
- 그래서 현재 UI에서는 `Benchmark Contract` tooltip을
  - `Ticker Benchmark`
  - `Candidate Universe Equal-Weight`
  두 방식이 각각 무엇을 비교하는지 plain language로 설명하도록 보강했다.
- 또한 `Candidate Universe Equal-Weight`를 선택했을 때는
  이것이 "같은 후보군 안에서 복잡한 ranking 없이 그냥 동일 비중으로 담은 기준선"이라는 점을
  캡션으로 한 번 더 보여주도록 정리했다.
- 이어서 QA에서는
  compare 요약 카드와 current candidate registry 표에서
  `Candidate Universe Equal-Weight / SPY`가 하나의 benchmark처럼 읽혀 혼동된다는 피드백이 나왔다.
- 그래서 현재는
  - `Benchmark Contract`
  - `Benchmark Ticker`
  - `Guardrail / Reference Ticker`
  를 분리해 보여주고,
  `Candidate Universe Equal-Weight`일 때는 `Benchmark Ticker`가 equal-weight benchmark를 만드는 재료가 아니라는 점,
  `Guardrail / Reference Ticker`가 underperformance / drawdown guardrail이 따로 참고하는 기준 ticker라는 점을
  카드 아래 설명으로 다시 보여주도록 정리했다.
- 이후 한 번 더 UX를 다듬으면서, strict annual `Real-Money Contract` 입력 자체도
  하나의 중립 필드에 역할을 겹쳐 놓는 방식 대신
  - `Comparison Baseline`
  - `Guardrail / Reference`
  두 역할로 나누어 읽히게 바꿨다.
  즉 현재는 입력 단계부터
  - `Benchmark Ticker`: 전략이 무엇과 직접 비교되는지
  - `Guardrail / Reference Ticker`: guardrail이 무엇을 기준으로 쉬는지
  를 별도 필드로 구분해 본다.
- 같은 QA 흐름에서 한 번 더 정리된 최종 UX는,
  `Ticker Benchmark`일 때는
  - `Benchmark Ticker`를 직접 비교 기준으로 먼저 보여주고
  - `Guardrail / Reference Ticker`는 `Guardrails` 탭에서 비워두면 benchmark와 동일하게 쓰는 선택 입력으로 읽히게 하는 방식이다.
  반대로 `Candidate Universe Equal-Weight`일 때는
  - benchmark curve가 후보군 equal-weight로 자동 생성된다는 설명을 함께 보여주고
  - `Benchmark Ticker`는 "직접 비교 baseline에는 쓰이지 않는다"는 안내와 같이 계속 보이며
  - `Guardrail / Reference Ticker`는 `Guardrails` 탭 안에서만 guardrail 기준 입력으로 읽히게 한다.
  즉 현재 UI는
  - `Real-Money Contract`: 무엇과 직접 비교하나
  - `Guardrails`: guardrail이 무엇을 기준으로 멈추나
  를 화면 구조 자체로 분리해서 읽게 만드는 쪽으로 정리됐다.
  그리고 compare prefill 요약 카드에서는
  - `Candidate Universe Equal-Weight`일 때 `Benchmark Ticker`를 빈칸으로 두고
  - guardrail이 실제로 꺼져 있으면 `Guardrail / Reference Ticker`도 빈칸으로 두어
  "실제로 활성화된 설정만 보여주는 표"에 더 가깝게 읽히게 만들었다.
  이후 QA 중 compare strict annual 렌더 경로에서
  예전 `guardrail_reference_ticker` 대입문이 한 줄 남아 있던 회귀도 발견되었고,
  현재는 compare strict annual도 single strict annual과 동일하게
  `Guardrails` expander 안에서만 guardrail reference를 생성/보관하는 구조로 다시 맞춰져 있다.
- 이후 QA에서는 compare / weighted / saved portfolio 사이의 divider가 과하다는 피드백이 나와,
  top-level divider는 제거하고 각 섹션의 `###` 제목만으로 구분하도록 정리했다.
- `Saved Portfolios`는 별도 top-level 탭으로 빼지 않고
  `Compare & Portfolio Builder` 안에 유지했다.
  현재 판단은 이 기능이 독립 모듈이라기보다
  `compare -> weighted portfolio -> save / replay / edit-in-compare`
  흐름의 마지막 operator 단계에 가깝기 때문이다.
- 즉 현재 compare surface는
  - manual strategy selection
  - saved portfolio compare re-entry
  - current candidate compare re-entry
  세 가지 operator ingress를 함께 가지게 되었다.
- Phase 20 second work unit에서는 이 흐름이 weighted portfolio와 saved portfolio까지 더 직접적으로 이어지도록 보강되었다.
  - `Weighted Portfolio Builder` 위에는
    현재 compare 결과를 내부 bundle 이름보다
    "지금 무엇을 섞는가" 중심으로 읽히게 하는 summary가 추가되었다.
    이 summary는
    - 들어온 경로
    - 묶음 이름
    - 비교 기간
    - 조합할 전략 수
    를 먼저 보여주고,
    그 아래에
    `Strategy / Period / CAGR / MDD / Promotion`
    표를 붙여 실제 조합 대상 전략을 바로 읽게 만든다.
  - divider도 같은 QA 흐름에서 다시 정리되어,
    `Quick Re-entry From Current Candidates` 아래 line은 제거하고
    `Strategy Comparison -> Weighted Portfolio Builder -> Saved Portfolios`
    세 단계 사이에만 보이도록 바뀌었다.
  - current candidate 또는 saved portfolio에서 compare를 다시 불러온 직후에는
    `Compare Form Updated` summary가 함께 보여서,
    어떤 전략/기간/override가 방금 compare form에 채워졌는지와
    어디를 확인하면 되는지 바로 알 수 있게 되었다.
  - weighted portfolio meta와 history context에도 compare source context가 남도록 보강되어,
    later rerun 시 compare bundle 출처를 다시 읽기 쉬워졌다.
  - saved portfolio는 source context를 같이 저장하고,
    상세 surface에 `Source & Next Step` 탭을 추가해
    "이 포트폴리오가 어디서 왔는지"와
    "지금 다음에 무엇을 하면 되는지"
    를 더 직접적으로 보여주게 되었다.
  - `Save This Weighted Portfolio`에서는
    `Portfolio Name`이 현재 source label 또는 strategy 조합 기준의 추천 이름으로 먼저 채워지고,
    `Description`은 이 저장 포트폴리오를 왜 남기는지 메모하는 칸으로 설명되어
    save 시점의 의미가 더 직접적으로 읽히게 되었다.
  - action label도
    - `Load Into Compare` -> `Load Saved Setup Into Compare`
    - `Run Saved Portfolio` -> `Replay Saved Portfolio`
    로 정리되어,
    operator가 저장된 포트폴리오를 수정하려는지 그대로 재실행하려는지 더 빠르게 이해할 수 있다.
  - `Load Saved Setup Into Compare`는
    저장된 전략 조합/기간만 다시 넣는 버튼이 아니라,
    compare 세부 설정과 weighted portfolio의 weight/date alignment까지 다시 채우는 흐름으로 정리되었다.
  - `Replay Saved Portfolio`는
    저장 당시 compare context를 그대로 다시 실행하는데,
    이 경로에서는 저장 record 안의 legacy compare override가
    현재 runtime signature에 없는 키를 포함해도
    compare runner가 지원하지 않는 kwargs를 걸러 주도록 보강되었다.
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
    portfolio handling contract first pass,
    selection history,
    interpretation
    을 annual strict family와 같은 형태로 지원한다
  - Phase 23 first implementation에서는 quarterly 3개 family도
    `Portfolio Handling & Defensive Rules`를 UI / payload / compare / history prefill에 연결했다.
    - `Weighting Contract`
    - `Rejected Slot Handling Contract`
    - `Risk-Off Contract`
    - `Defensive Sleeve Tickers`
  - 단, quarterly는 여전히 productionization 중인 path다.
    - real-money promotion
    - benchmark contract / liquidity promotion policy
    - underperformance / drawdown guardrail UI
    는 아직 annual strict 중심으로 유지한다
  - quarterly family는 이제
    - single strategy
    - compare
    - history rerun / prefill
    까지 연결되어 있다
  - 2026-04-19 representative DB-backed smoke run에서
    `Quality / Value / Quality + Value` quarterly prototype 3개 family가
    non-default portfolio handling contract 조합으로 실제 실행되는 것을 확인했다.
    - smoke 중 공통 result bundle meta에 `weighting_mode`, `rejected_slot_handling_mode`,
      `rejected_slot_fill_enabled`, `partial_cash_retention_enabled`가 빠지는 문제를 발견해 수정했다.
    - 따라서 history / load-into-form 복원에 필요한 portfolio handling contract meta가 result bundle에 남는다.
  - 추가 code-level roundtrip check에서
    result bundle meta -> history record -> history payload -> saved portfolio strategy override까지
    quarterly portfolio handling contract 값이 보존되는 것을 확인했다.
  - Compare 화면에서는 `Quality / Value / Quality + Value` family의 Annual / Quarterly variant 선택을 각 strategy box 안에 배치했다.
    - 별도 Apply 버튼 없이 variant 변경 즉시 같은 box 안의 strategy-specific inputs가 해당 annual/quarterly 경로로 갱신된다.
    - `Start Date`, `End Date`, `Timeframe`, `Option`은 `Compare Period & Shared Inputs`로 모으고,
      전략별 세부 옵션은 `Strategy-Specific Advanced Inputs` 아래 border box로 분리했다.
    - quarterly prototype compare 경로도 annual strict처럼 `Overlay`와 `Portfolio Handling & Defensive Rules`를 하위 접기 그룹으로 보여준다.
    - `Load Into Form` 후 `Back To History` shortcut은 `History` panel로 직접 돌아가도록 보강되었다.
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
    - selected preset/manual candidate pool
    - rebalance-date close
    - `latest_available_at <= rebalance_date`인 최신 statement `shares_outstanding`
    를 사용해 `approx_market_cap`을 계산하고 top-N membership를 다시 구성한다
  - strict annual UI에서는 `Historical Dynamic PIT Universe`를 선택해도
    selected preset 자체가 candidate pool로 유지된다
    - 예: `US Statement Coverage 100` + dynamic PIT면
      candidate pool도 `100`, target membership도 `100`
    - 이전처럼 hidden `1000 -> 100` 확장은 더 이상 기본 동작이 아니다
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
