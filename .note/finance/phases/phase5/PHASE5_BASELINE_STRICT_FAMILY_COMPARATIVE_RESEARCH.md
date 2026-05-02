# Phase 5 Baseline Strict Family Comparative Research

## 목적

- Phase 5의 overlay 실험 전에
  `Quality`, `Value`, `Quality + Value` strict annual family를
  같은 기준으로 읽을 수 있는 baseline을 고정한다.
- compare / single / history / 해석 화면이
  같은 기본 실험 프로토콜을 공유하도록 만든다.

## baseline 전략군

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

세 전략 모두 현재 baseline 정의는 다음과 같다.

1. annual statement shadow factor snapshot 사용
2. `timeframe=1d`
3. `option=month_end`
4. equal-weight holding
5. `rebalance_interval=1` 기본

## canonical research preset

### compare baseline

- preset:
  - `US Statement Coverage 100`
- 이유:
  - multi-strategy compare 실행 시간을 감당하기 쉽다
  - strict family 간 상대 비교를 먼저 보기 좋다

### single baseline

- preset:
  - `US Statement Coverage 300`
- 이유:
  - 현재 strict annual public default
  - coverage / runtime / 운영 안정성 균형이 가장 좋다

## 전략별 baseline 기본값

### Quality Snapshot (Strict Annual)

- `top_n=2`
- 기본 factor:
  - `roe`
  - `roa`
  - `net_margin`
  - `asset_turnover`
  - `current_ratio`

### Value Snapshot (Strict Annual)

- `top_n=10`
- 기본 factor:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`

### Quality + Value Snapshot (Strict Annual)

- `top_n=10`
- quality 기본 factor:
  - `roe`
  - `roa`
  - `net_margin`
  - `asset_turnover`
  - `current_ratio`
- value 기본 factor:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`

## baseline 비교 질문

Phase 5 첫 챕터에서 baseline compare가 답해야 하는 질문은 아래와 같다.

1. long-history strict annual family에서 누가 가장 일관되게 active한가
2. single default `300`에서 누가 public candidate로 가장 안정적인가
3. compare default `100`에서 quality/value/multi-factor의 상대적 성격 차이가 읽히는가
4. overlay를 얹기 전에도 selection history가 충분히 해석 가능한가

## 현재 baseline 해석 상태

- single 화면:
  - strict family 모두 selection history를 볼 수 있다
- compare 화면:
  - focused strategy drilldown은 가능하다
  - 이번 챕터에서 selection interpretation도 compare focus 안으로 확장했다
- history:
  - strict family single run은 prefill / rerun 가능하다

## 이번 챕터에서 baseline 위에 추가된 것

- compare strict factor advanced-input parity
  - preset
  - factor set
  - `top_n`
  - `rebalance_interval`
  - first overlay input
- selection interpretation 확장
  - raw selected names
  - overlay rejected names
  - selection frequency

## 결론

- Phase 5 baseline strict family는 이제
  `100` compare baseline과 `300` single baseline으로 고정한다.
- 이 baseline 위에서 first overlay 실험을 시작하는 것이 가장 자연스럽다.
