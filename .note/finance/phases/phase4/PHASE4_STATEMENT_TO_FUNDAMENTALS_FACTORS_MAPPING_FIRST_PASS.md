# Phase 4 Statement To Fundamentals / Factors Mapping First Pass

## 목적
이 문서는 statement-driven quality prototype을
임시 전략 코드가 아니라 `finance/data/*`의 재사용 가능한 매핑 경로로 정리한 first-pass 작업을 기록한다.

핵심 목표:
- `nyse_financial_statement_values` strict snapshot에서
- normalized fundamentals를 만들고
- 그 위에서 quality factor snapshot을 만들 수 있게 한다

즉 현재 broad-research public path와 별도로,
다음 경로를 코드 레벨에서 고정하는 것이 목적이다.

```text
strict statement snapshot
  -> normalized fundamentals
  -> quality factor snapshot
  -> quality strategy
```

---

## 추가된 reusable 함수

### `finance/data/fundamentals.py`
- `build_fundamentals_from_statement_snapshot(...)`

역할:
- strict statement snapshot rows를 symbol별 normalized fundamentals 단면으로 변환
- 현재 first-pass에서 만드는 핵심 필드:
  - `total_revenue`
  - `gross_profit`
  - `operating_income`
  - `net_income`
  - `total_assets`
  - `current_assets`
  - `total_liabilities`
  - `current_liabilities`
  - `total_debt`
  - `net_assets`
  - `operating_cash_flow`
  - `free_cash_flow`
  - `capital_expenditure`
  - `cash_and_equivalents`
  - `interest_expense`

특징:
- concept 후보군을 명시적으로 사용
- source column도 같이 남김
- `gross_profit` direct row가 없으면 `revenue - cost_of_revenue`
- `free_cash_flow`는 `operating_cash_flow - capex` first-pass derivation 허용

### `finance/data/factors.py`
- `calculate_quality_factors_from_fundamentals(...)`
- `build_quality_factor_snapshot_from_statement_snapshot(...)`

역할:
- normalized fundamentals에서
  - `roe`
  - `gross_margin`
  - `operating_margin`
  - `debt_ratio`
  를 계산
- quality strategy가 바로 읽을 수 있는 snapshot DataFrame 반환

---

## 왜 이 구조가 필요한가

이전 prototype은
- `finance/transform.py`
안에서 바로 strict statement rows를 quality snapshot으로 바꾸는 방식이었다.

그 방식도 동작은 했지만, 아래 문제가 있었다.
- data-layer 역할과 strategy-layer 역할이 섞임
- 나중에 statement-driven fundamentals/factors rebuild로 이어가기 어려움
- prototype logic를 다른 경로에서 재사용하기 어려움

이번 정리로:
- statement mapping은 `finance/data/fundamentals.py`
- factor derivation은 `finance/data/factors.py`
- strategy execution은 기존 `quality_snapshot_equal_weight(...)`

구조로 다시 나눴다.

---

## 현재 사용처

현재 first-pass 사용처:
- `finance/sample.py`
  - `get_statement_quality_snapshot_from_db(...)`

여기서 now:
1. `load_statement_snapshot_strict(...)`
2. `build_quality_factor_snapshot_from_statement_snapshot(...)`
3. `quality_snapshot_equal_weight(...)`

순서로 연결된다.

즉 prototype이 여전히 sample/runtime 검증 경로이긴 하지만,
핵심 계산 로직은 이제 data-layer로 옮겨진 상태다.

---

## 현재 해석

이 작업은 아직 아래를 의미하지는 않는다.
- `nyse_fundamentals`를 바로 statement-driven으로 교체했다
- `nyse_factors`를 바로 statement-driven으로 교체했다
- public UI quality strategy가 strict statement path로 바뀌었다

현재 의미는 정확히 이것이다.
- statement ledger를 source of truth로 쓰는
  `future rebuild path`가 코드로 생겼다
- broad-research public quality path와는 별도 경로로 유지된다

---

## 다음 의미 있는 선택

이제 다음 단계는 둘 중 하나다.

1. 이 mapping 경로를 바탕으로
   `statement-driven fundamentals/factors backfill`을 더 본격적으로 준비

2. sample-universe prototype을 조금 더 다듬어
   `strict statement quality` public 후보로 키울지 판단

현재 기준에서는 1번이 더 구조적으로 자연스럽다.
