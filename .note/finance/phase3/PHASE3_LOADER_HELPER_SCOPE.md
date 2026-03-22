# Phase 3 Loader Helper Scope

## 목적
이 문서는 Phase 3 loader 구현 전에
`finance/loaders/_common.py`에 둘 helper 범위를 고정하기 위한 문서다.

관련 문서:
- `.note/finance/phase3/PHASE3_LOADER_MODULE_PATH.md`
- `.note/finance/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md`

---

## 1. 기본 결론

`finance/loaders/_common.py`는
모든 loader가 공통으로 쓰는
입력 정규화 / symbol resolution / validation helper만 둔다.

즉 여기에는:
- 도메인별 SQL
- 도메인별 DataFrame 가공
- price/fundamental/statement 전용 조회 로직

을 넣지 않는다.

---

## 2. `_common.py`에 포함할 helper

Phase 3 1차 기준 포함 대상:

1. `parse_symbol_list(...)`
2. `resolve_loader_symbols(...)`
3. `normalize_timestamp(...)`
4. `normalize_date_range(...)`
5. `normalize_loader_freq(...)`
6. `normalize_timeframe(...)`
7. `validate_snapshot_inputs(...)`

---

## 3. helper별 책임

### 3-1. `parse_symbol_list(...)`
- 문자열 또는 iterable을 `list[str]`로 정규화
- 공백 제거
- 대문자화
- 중복 제거

### 3-2. `resolve_loader_symbols(...)`
- `symbols` 우선
- 없으면 `universe_source` 해석
- loader 계약에 맞는 source enum을 처리

### 3-3. `normalize_timestamp(...)`
- `str | datetime | pd.Timestamp`를 `pd.Timestamp`로 정규화

### 3-4. `normalize_date_range(...)`
- `start`, `end`를 정규화
- `start > end` 방지

### 3-5. `normalize_loader_freq(...)`
- `annual`, `quarterly`만 허용

### 3-6. `normalize_timeframe(...)`
- `1d`, `1wk`, `1mo`만 허용

### 3-7. `validate_snapshot_inputs(...)`
- `as_of_date`와 `start/end`의 충돌 방지
- snapshot 계열 loader 입력 검증

---

## 4. `_common.py`에서 제외할 것

아래 항목은 `_common.py`에 두지 않는다.

1. price SQL query builder
2. factor pivot helper
3. statement-specific latest snapshot SQL
4. universe-specific business filter
5. runtime adapter helper

이유:
- `_common.py`가 비대해지면
  도메인 경계가 다시 흐려진다

---

## 5. symbol source 해석 기준

`resolve_loader_symbols(...)`가 지원할 초기 source:

- `nyse_stocks`
- `nyse_etfs`
- `nyse_stocks_etfs`
- `profile_filtered_stocks`
- `profile_filtered_etfs`
- `profile_filtered_stocks_etfs`

비고:
- `manual`은 loader 내부 기본 source가 아니라
  UI 계층에서 `symbols` 직접 입력으로 처리하는 것으로 본다

---

## 6. 구현 기준 요약

`_common.py`는
"모든 loader가 공통으로 쓰는 입력 해석 계층"
으로만 유지한다.

즉:
- 공통 helper는 넣고
- 도메인 로직은 넣지 않는다

---

## 결론

Phase 3의 helper 분리 기준은
`_common.py`를 작은 공통 입력 계층으로 유지하는 것이다.

이렇게 해야 이후 `universe.py`, `price.py`, `fundamentals.py`,
`factors.py`, `financial_statements.py`가
서로 겹치지 않고 자연스럽게 구현된다.
