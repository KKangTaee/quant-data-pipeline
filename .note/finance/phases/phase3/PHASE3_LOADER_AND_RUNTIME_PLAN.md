# Phase 3 Loader And Runtime Plan

## 목적
이 문서는 `finance` 프로젝트의 Phase 3 계획 문서다.

Phase 3의 정식 이름:
- `Backtest Loader Implementation And Strategy Runtime`

이 단계의 목적은
Phase 2에서 정리한 문서와 설계를
실제 코드로 옮겨,
DB 기반 백테스트 실행 경로를 만드는 것이다.

---

## Phase 3의 핵심 목표

Phase 3 종료 시점에 확보하고 싶은 상태:

1. DB loader 계층이 실제 코드로 존재한다
2. broad research loader와 strict PIT loader가 구분된다
3. 최소 1개 전략이 DB loader를 통해 실행 가능하다
4. strategy runtime이 loader 계약을 기준으로 동작한다
5. Phase 4의 UI 실행기로 연결할 수 있는 실행 경로가 준비된다

---

## Phase 3의 큰 작업 축

1. loader 구현 범위 확정
2. strict vs broad loader 정책 확정
3. universe / price / fundamentals / factors / statements loader 구현
4. strategy runtime 연결
5. 최소 전략 실행 검증

---

## Phase 3-1. Loader Scope Finalization

### 목표
- 어떤 loader를 1차로 구현할지 확정한다

### 우선 구현 후보
- `load_universe(...)`
- `load_price_history(...)`
- `load_price_matrix(...)`
- `load_fundamentals(...)`
- `load_factors(...)`
- `load_statement_values(...)`
- `load_statement_snapshot_strict(...)`

### 산출물
- loader 구현 범위 문서
- naming 규칙

---

## Phase 3-2. Broad vs Strict Loader Policy

### 목표
- 연구용 broad loader와 strict PIT loader의 차이를 고정한다

### 핵심 질문
- strict loader 이름을 어떻게 할지
- mixed-state row를 broad loader에서 어디까지 허용할지
- strict loader는 accession-bearing row만 읽을지

### 산출물
- loader naming 규칙
- strict/broad 정책 문서

---

## Phase 3-3. Loader Implementation

### 목표
- 설계 문서를 실제 코드 모듈로 옮긴다

### 구현 후보 모듈
- `finance/loaders/universe.py`
- `finance/loaders/price.py`
- `finance/loaders/fundamentals.py`
- `finance/loaders/factors.py`
- `finance/loaders/financial_statements.py`

### 산출물
- 실제 loader 코드
- 최소 테스트 또는 샘플 실행 코드

---

## Phase 3-4. Strategy Runtime Connection

### 목표
- 전략이 직접 DB를 만지지 않고 loader를 통해 실행되게 만든다

### 방향
- 기존 전략 코드를 읽고 필요한 입력 형태 파악
- transform / engine / strategy 경계 유지
- DB 기반 입력을 사용하는 최소 실행 흐름 확보

### 산출물
- loader를 사용하는 최소 strategy runtime path

---

## Phase 3-5. First DB-Backed Strategy Execution

### 목표
- 최소 1개 전략이 DB loader를 통해 실제 실행되게 한다

### 후보 전략
- 기존 구조에 가장 잘 맞는 단순 전략 1개
- 입력 요건이 복잡하지 않은 전략을 우선 선택

### 검증 기준
- DB loader -> strategy runtime -> 결과 DataFrame 흐름이 실제 동작
- 향후 UI에서 이 경로를 호출할 수 있어야 함

---

## Phase 3 진입 전 확인 사항

Phase 3 시작 시 먼저 확정해야 할 것:

1. research-universe backfill 범위
2. strict vs broad loader naming 규칙
3. 1차 loader 구현 우선순위
4. first DB-backed strategy 후보

---

## 결론

Phase 3는
Phase 2에서 준비한 문서/원칙을
실제 백테스트 실행 코드로 바꾸는 단계다.

즉 이 단계부터는
“문서화 중심 준비 단계”에서
“실행 가능한 quant runtime 구현 단계”로 넘어간다.

