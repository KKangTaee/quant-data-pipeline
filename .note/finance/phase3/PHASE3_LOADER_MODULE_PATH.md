# Phase 3 Loader Module Path

## 목적
이 문서는 Phase 3에서 구현할 loader 계층의
파일 경로와 모듈 경계를 확정하기 위한 문서다.

관련 문서:
- `.note/finance/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`
- `.note/finance/phase3/PHASE3_INITIAL_LOADER_IMPLEMENTATION_SET.md`

---

## 1. 기본 결론

Phase 3 loader 계층은
`finance/loaders/` 패키지 아래에 둔다.

즉, 새 loader 코드는
기존 `finance/data/*`와 분리된
"조회/런타임용 계층"으로 구현한다.

이유:
1. `finance/data/*`는 수집과 적재 중심이다
2. Phase 3 loader는 조회와 runtime 연결 중심이다
3. ingestion 코드와 loader 코드를 물리적으로 분리하는 것이 유지보수에 유리하다

---

## 2. 권장 디렉터리 구조

Phase 3 기준 권장 구조:

```text
finance/
  loaders/
    __init__.py
    _common.py
    universe.py
    price.py
    fundamentals.py
    factors.py
    financial_statements.py
```

---

## 3. 모듈별 책임

### `finance/loaders/__init__.py`
- 공개 loader 함수 재노출
- 외부 호출 진입점 정리

### `finance/loaders/_common.py`
- symbol resolution helper
- date normalization helper
- freq / timeframe normalization helper
- shared validation helper

### `finance/loaders/universe.py`
- `load_universe(...)`
- universe source 해석

### `finance/loaders/price.py`
- `load_price_history(...)`
- `load_price_matrix(...)`

### `finance/loaders/fundamentals.py`
- `load_fundamentals(...)`
- `load_fundamental_snapshot(...)`

### `finance/loaders/factors.py`
- `load_factors(...)`
- factor snapshot / matrix 계열

### `finance/loaders/financial_statements.py`
- `load_statement_values(...)`
- `load_statement_snapshot_strict(...)`

---

## 4. 경계 원칙

loader 계층은:
- 조회 전용
- runtime 입력용
- SQL/DB 세부사항 은닉

ingestion 계층은:
- 원천 데이터 수집
- 정규화
- DB 적재

즉:
- `finance/data/*`는 write path
- `finance/loaders/*`는 read path

로 분리한다.

---

## 5. 현재 1차 구현과의 연결

이번 챕터에서 바로 연결되는 모듈:

1. `finance/loaders/__init__.py`
2. `finance/loaders/_common.py`
3. `finance/loaders/universe.py`
4. `finance/loaders/price.py`

후속 모듈:

5. `finance/loaders/fundamentals.py`
6. `finance/loaders/factors.py`
7. `finance/loaders/financial_statements.py`

---

## 6. 보류한 대안

검토했지만 채택하지 않은 대안:

### 대안 A. `finance/data/loaders/*`
- 문제:
  - 수집/적재 계층과 조회 계층이 섞인다
  - write path와 read path의 책임이 흐려진다

### 대안 B. `finance/runtime/loaders/*`
- 문제:
  - loader가 runtime 전용으로만 보인다
  - 향후 웹 UI / 리서치 코드 재사용 관점에서 범용성이 떨어진다

따라서 현재 구조에서는
`finance/loaders/*`가 가장 명확하다.

---

## 7. 구현 기준 요약

Phase 3 loader 경로 기준:

1. 새 loader 패키지는 `finance/loaders/`
2. 공통 helper는 `_common.py`
3. 도메인별 모듈 분리는 `universe / price / fundamentals / factors / financial_statements`
4. 공개 함수는 `__init__.py`에서 재노출

---

## 결론

Phase 3의 loader 구현은
`finance/loaders/*` 구조로 고정한다.

이렇게 하면
기존 수집/적재 계층과 조회/실행 계층이 분리되고,
다음 단계에서 바로 실제 loader 코드 구현으로 넘어가기 쉽다.
