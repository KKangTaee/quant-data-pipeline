# Phase 3 Loader Implementation TODO

## 목적
이 문서는 Phase 3의 실제 loader 코드 구현 챕터를
큰 TODO와 세부 체크 항목으로 관리하기 위한 작업 보드다.

상위 계획 문서:
- `.note/finance/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`

선행 문서:
- `.note/finance/phase3/PHASE3_INITIAL_LOADER_IMPLEMENTATION_SET.md`
- `.note/finance/phase3/PHASE3_FIRST_LOADER_IMPLEMENTATION_ORDER.md`
- `.note/finance/phase3/PHASE3_MINIMAL_VALIDATION_PATH.md`

---

## 현재 챕터 범위

현재 챕터의 목표:

1. 첫 loader 세트를 실제 코드로 만든다
2. public import 경로를 정리한다
3. 최소 smoke validation을 통과시킨다

---

## 큰 TODO 보드

### A. Universe Loader
상태:
- `completed`

세부 작업:
- `[completed]` `finance/loaders/universe.py` 구현
  - source/symbol 기반 universe resolution 공개 함수 추가
- `[completed]` universe loader smoke validation
  - manual symbol 및 source path 기본 동작 확인

완료 기준:
- `load_universe(...)`가 공개 함수로 사용 가능해야 함

---

### B. Price Loader
상태:
- `completed`

세부 작업:
- `[completed]` `finance/loaders/price.py` 구현
  - long-form price loader 추가
- `[completed]` price matrix loader 구현
  - pivot matrix 반환 함수 추가
- `[completed]` price loader smoke validation
  - 최소 import / py_compile / shape 확인

완료 기준:
- `load_price_history(...)`, `load_price_matrix(...)`가 공개 함수로 사용 가능해야 함

---

### C. Loader Package Export
상태:
- `completed`

세부 작업:
- `[completed]` `finance/loaders/__init__.py` 공개 import 정리
  - 첫 구현 함수들을 패키지 루트에서 import 가능하게 정리

완료 기준:
- `from finance.loaders import ...` 형태가 동작해야 함

---

### D. Runtime Adapter
상태:
- `completed`

세부 작업:
- `[completed]` runtime adapter helper 구현
  - loader long-form price history를 기존 전략 입력 dict로 변환
- `[completed]` first DB-backed strategy smoke validation
  - `EqualWeightStrategy` 경로 최소 실행 확인
- `[completed]` first DB-backed runtime result 기록
  - 실제 검증 입력과 결과 요약 문서화

완료 기준:
- loader 출력이 기존 전략에 연결되는 최소 브리지 경로가 있어야 함

---

### E. DB Sample Entrypoints
상태:
- `completed`

세부 작업:
- `[completed]` `BacktestEngine.load_ohlcv_from_db(...)` 추가
  - 기존 엔진 체이닝을 유지하면서 DB 가격 로드를 붙임
- `[completed]` `sample.py`에 `*_from_db` 함수 추가
  - 기존 전략 샘플과 분리된 DB 기반 전략 테스트 진입점 제공

완료 기준:
- 기존 전략 샘플을 유지한 채 DB 기반 테스트 함수가 별도로 존재해야 함

---

## 현재 작업 중 항목

현재 `in_progress`:
- `없음`

바로 다음 체크 대상:
- `fundamentals / factors loader 확장 또는 runtime 정리`

---

## 현재 진척도

- Phase 3 loader implementation chapter:
  - 약 `95%`
