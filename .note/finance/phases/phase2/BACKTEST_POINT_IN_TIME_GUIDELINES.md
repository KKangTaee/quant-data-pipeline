# Backtest Point-In-Time Guidelines

## 목적
이 문서는 PHASE2의 loader 설계와 이후 백테스트 구현에서
반드시 지켜야 할 point-in-time 기준을 정리한다.

핵심 목표:
- 과거 시점의 의사결정에 미래 정보를 섞지 않는다
- `fundamentals`, `factors`, `detailed financial statements`를
  price 시계열과 결합할 때 룩어헤드 편향을 막는다

---

## 1. Point-In-Time이란 무엇인가

point-in-time은
특정 날짜의 투자 판단에 대해
그 날짜에 실제로 알 수 있었던 정보만 사용하는 원칙이다.

즉:
- `period_end`가 과거라고 해서
- 그 데이터가 그 시점에 이미 시장에 알려졌다고 가정하면 안 된다

재무 데이터는 보통 두 시점이 분리된다.

1. 경제적 의미가 발생한 시점
   - 예: `period_end = 2022-12-31`
2. 시장이 실제로 그 정보를 알 수 있게 된 시점
   - 예: 공시/반영 가능 시점 = `2023-02-15`

백테스트는 2번 기준으로 데이터를 사용해야 한다.

---

## 2. 왜 중요한가

이 원칙을 지키지 않으면
백테스트가 실제보다 훨씬 좋아 보일 수 있다.

대표적인 문제:
- look-ahead bias
- 과거 시점에 미래 재무 수치를 사용
- factor ranking이 비현실적으로 좋아짐
- 리밸런싱 성과가 과대평가됨

특히 이 프로젝트에서는 아래 테이블들이 핵심 위험 구간이다.

- `finance_fundamental.nyse_fundamentals`
- `finance_fundamental.nyse_factors`
- `finance_fundamental.nyse_financial_statement_labels`
- `finance_fundamental.nyse_financial_statement_values`

반면 price 데이터는 일반적으로 거래일 시계열이라
재무 데이터보다 point-in-time 문제가 상대적으로 단순하다.

---

## 3. 이 프로젝트에서의 핵심 위험

## 3-1. `period_end`를 곧바로 사용 가능 시점으로 오해하는 위험

잘못된 예:
- `2022-12-31` 연간 재무 데이터를
- `2023-01-03` 포트폴리오 구성에 사용

문제:
- 실제 공시가 아직 안 되었을 수 있다

## 3-2. factor 테이블도 동일한 위험을 가진다

`nyse_factors`는 이미 계산된 결과지만,
그 기반이 되는 fundamentals와 price 결합 시점이 중요하다.

즉 factor row도
단순히 `period_end`만 보고 사용하면 안 된다.

## 3-3. detailed statement raw ledger는 더 조심해야 한다

`nyse_financial_statement_values`는
더 긴 과거와 더 세부적인 계정 정보를 주지만,
그만큼 시점 정렬을 잘못하면
커스텀 팩터 전체가 오염될 수 있다.

---

## 4. loader 설계 규칙

## 4-1. 시계열 loader와 snapshot loader를 구분한다

시계열 loader:
- `start/end` 기준으로 row를 반환

snapshot loader:
- `as_of_date` 기준으로
- 그 날짜에 사용 가능했어야 하는 최신 row만 반환

즉:
- `load_fundamentals(...)`는 시계열용
- `load_fundamental_snapshot(..., as_of_date=...)`는 snapshot용

같은 원칙을 factor / statement loader에도 적용한다.

## 4-2. `period_end <= as_of_date`만으로 충분하다고 가정하지 않는다

1차 구현에서는 임시 기준으로 쓸 수 있지만,
최종 백테스트 기준으로는 부족하다.

이유:
- `period_end`는 보고 기간 종료일일 뿐
- 실제 시장 반영 가능 시점이 아니다

따라서 loader는 장기적으로 아래 둘을 분리해야 한다.

- `period_end`
- `available_at` 또는 이에 준하는 공시 가능 시점

## 4-3. 공시 가능 시점 컬럼이 없으면 보수적 fallback 규칙을 둔다

현재 DB에 명시적 `available_at`이 없다면,
초기 단계에서는 보수적 lag 규칙을 둘 수 있다.

예시:
- annual fundamentals: `period_end + conservative lag`
- quarterly fundamentals: `period_end + shorter but still conservative lag`

이 fallback은 추후 실제 공시일 기반으로 대체하는 것이 목표다.

## 4-4. snapshot loader는 항상 “latest available” 의미를 명시한다

`as_of_date = 2024-03-31`일 때
snapshot loader는
그날까지 사용 가능했던 데이터 중 가장 최신 재무 row를 반환해야 한다.

즉 “latest period”가 아니라
“latest available record as of that date”여야 한다.

---

## 5. 테이블별 적용 가이드

## 5-1. Price Loader

기본 원칙:
- 거래일 기준 시계열 로드
- 리밸런싱 날짜와 가격 필드 선택을 명확히 분리

주의:
- 종가 기반 전략이면
  같은 날 종가로 신호를 계산하고 같은 날 종가로 체결하는 식의 가정은 보수적으로 검토해야 한다
- 최소한 다음 거래일 체결인지, 당일 종가 체결인지 규칙을 전략 레벨에서 명확히 해야 한다

## 5-2. Fundamentals Loader

기본 원칙:
- `period_end`는 보고 기준일
- 실제 snapshot은 `available_at <= as_of_date` 기준으로 선택

1차 fallback:
- 명시적 공시일이 없으면 보수적 lag를 적용한 pseudo-available date를 사용

## 5-3. Factor Loader

기본 원칙:
- factor 자체도 point-in-time 제약을 받는다
- factor row 생성 시점이 아니라
  factor 산출에 사용된 재무 데이터의 가용 시점을 따라야 한다

권장:
- factor snapshot도 내부적으로 fundamentals snapshot 규칙을 재사용

## 5-4. Detailed Financial Statement Loader

기본 원칙:
- raw ledger 조회는 `period_end` row를 읽더라도
  실제 전략 입력용 snapshot은 available-date 기준으로 잘라야 한다

권장:
- raw load와 strategy-ready snapshot load를 분리
- 예:
  - `load_statement_values(...)`
  - `load_statement_snapshot(..., as_of_date=...)`

---

## 6. 구현 단계 권장 규칙

## 6-1. 1차 구현

목표:
- loader 인터페이스를 먼저 통일
- point-in-time을 위한 확장 포인트를 남김

허용:
- `period_end <= as_of_date` 기반 latest snapshot

조건:
- 문서에 “strict point-in-time 아님”을 명시
- 백테스트 결과 해석 시 보수적으로 본다

## 6-2. 2차 구현

목표:
- `available_at` 또는 fallback lag 규칙 도입

권장 작업:
- loader 내부 snapshot selection helper 분리
- annual / quarterly 별 기본 lag 규칙 분리
- factor snapshot이 fundamentals snapshot 로직을 공유하도록 정리

## 6-3. 3차 구현

목표:
- 실제 공시일 또는 제출일 기반 strict point-in-time 강화

가능한 방향:
- SEC filing date
- 실제 ingestion 시점 기록
- vendor-specific release date

---

## 7. 백테스트 해석 규칙

- point-in-time이 완전히 구현되기 전의 백테스트는
  연구용 참고치로만 본다
- 장기 팩터 전략 성과가 지나치게 좋다면
  먼저 point-in-time 오염 가능성을 의심한다
- raw statement 기반 커스텀 팩터는
  summary factor보다 더 엄격하게 시점 검증을 거친다

---

## 8. 앞으로 loader 구현 시 확인할 체크리스트

- `snapshot` loader가 `as_of_date`를 받는가
- `start/end`와 `as_of_date` 충돌을 막는가
- `period_end`와 실제 가용 시점을 개념적으로 분리했는가
- strict point-in-time이 아닌 경우 문서와 함수명에 이를 숨기지 않는가
- factor loader가 fundamentals availability 규칙을 재사용하는가
- detailed statement snapshot이 raw row 전체를 미래 정보와 함께 노출하지 않는가

