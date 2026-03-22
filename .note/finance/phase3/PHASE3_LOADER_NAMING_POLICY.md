# Phase 3 Loader Naming Policy

## 목적
이 문서는 Phase 3에서 구현할 DB loader 계층의 naming 규칙을 고정한다.

핵심 목표:
- broad research loader와 strict point-in-time loader를 이름만 보고 구분 가능하게 만든다
- loader 함수명만 봐도 데이터 가정과 사용 목적이 드러나게 만든다

---

## 기본 원칙

1. 기본 함수명은 broad loader에 사용한다
2. strict point-in-time 가정이 붙는 경우 이름에 `strict`를 명시한다
3. snapshot 성격은 `snapshot`으로 표현한다
4. matrix / pivot / history 같은 반환 형태는 suffix로 표현한다

즉:
- 기본 이름 = 일반 연구용 / broad read
- `*_strict` 또는 `*_snapshot_strict` = strict PIT read

---

## 권장 패턴

## 1. Universe

- `load_universe(...)`

비고:
- universe loader는 strict/broad 구분이 상대적으로 덜 중요
- strict point-in-time universe가 필요해지면 별도 naming을 추가 검토

---

## 2. Price

- `load_price_history(...)`
- `load_price_matrix(...)`

비고:
- price는 기본적으로 거래일 시계열이라
  재무 loader만큼 strict/broad 분리가 크지 않다
- 다만 execution timing 가정은 strategy/runtime 레벨에서 별도 관리

---

## 3. Fundamentals

- `load_fundamentals(...)`
  - broad research loader
- `load_fundamental_snapshot(...)`
  - broad snapshot
- `load_fundamental_snapshot_strict(...)`
  - strict PIT snapshot

권장:
- strict가 붙지 않으면 research-friendly read로 해석

---

## 4. Factors

- `load_factors(...)`
  - broad research loader
- `load_factor_matrix(...)`
  - broad factor matrix
- `load_factor_snapshot(...)`
  - broad snapshot
- `load_factor_snapshot_strict(...)`
  - strict PIT snapshot

비고:
- factor는 재무 데이터 availability 영향을 받으므로
  strict snapshot 구분이 중요하다

---

## 5. Detailed Financial Statements

- `load_statement_values(...)`
  - broad/raw research loader
- `load_statement_pivot(...)`
  - broad pivot
- `load_statement_snapshot(...)`
  - broad snapshot
- `load_statement_snapshot_strict(...)`
  - strict PIT snapshot

비고:
- detailed statements는 mixed-state / strict PIT 차이가 크므로
  strict loader naming을 반드시 분리한다

---

## naming에서 피할 것

- `load_clean_*`
  - 무엇이 clean한지 모호함
- `load_safe_*`
  - 안전 기준이 불명확함
- `load_true_*`
  - 해석 여지가 큼
- `pit_*`
  - 약어만으로는 의미가 약할 수 있음

현재 프로젝트에서는
`strict`라는 단어가 가장 직관적이다.

---

## 최종 권장 규칙

1. broad research loader:
   - `load_*`
2. broad snapshot:
   - `load_*_snapshot`
3. strict point-in-time snapshot:
   - `load_*_snapshot_strict`

이 규칙을 Phase 3 loader 구현 기본 규칙으로 사용한다.

