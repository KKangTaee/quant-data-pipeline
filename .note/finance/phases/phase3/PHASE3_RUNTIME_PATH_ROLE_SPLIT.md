# Phase 3 Runtime Path Role Split

## 목적
이 문서는 Phase 3에서 공존하는 두 실행 경로:

- legacy direct-fetch path
- DB-backed runtime path

의 역할을 명확히 구분하기 위한 정리 문서다.

상위 보드:
- `.note/finance/phases/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`

---

## 왜 이 문서가 필요한가

현재 `finance/sample.py`에는 같은 전략에 대해 두 종류의 함수가 함께 존재한다.

예:
- `get_equal_weight(...)`
- `get_equal_weight_from_db(...)`

이 둘은 이름은 비슷하지만, 역할은 다르다.

초기에는 이 차이가 충분히 문서화되지 않아:
- 어떤 경로가 기준 경로인지
- 어떤 경로가 loader/runtime 검증용인지
- 언제 어떤 함수를 써야 하는지

가 혼동될 수 있었다.

---

## 1. Legacy Direct-Fetch Path

대표 함수:
- `get_equal_weight(...)`
- `get_gtaa3(...)`
- `get_risk_parity_trend(...)`
- `get_dual_momentum(...)`
- `portfolio_sample(...)`

특징:
- 외부 소스(yfinance)에서 직접 OHLCV를 읽는다
- 기존 프로젝트에서 먼저 존재하던 전략 예시/연구 경로다
- 예제, 빠른 전략 스모크 테스트, 기존 기준 결과 확인에 적합하다

현재 역할:
- legacy reference path
- direct provider behavior 확인
- DB와 무관한 전략 예제 경로

현재 판단:
- 당장 제거 대상은 아님
- 하지만 장기적으로는 “사용자 실행 경로”가 아니라
  reference / comparison path로 보는 것이 맞다

---

## 2. DB-Backed Runtime Path

대표 함수:
- `get_equal_weight_from_db(...)`
- `get_gtaa3_from_db(...)`
- `get_risk_parity_trend_from_db(...)`
- `get_dual_momentum_from_db(...)`
- `portfolio_sample_from_db(...)`

연결 계층:
- `finance/loaders/*`
- `BacktestEngine.load_ohlcv_from_db(...)`

특징:
- MySQL에 적재된 데이터를 loader를 통해 읽는다
- Phase 3에서 구축한 read path와 runtime path를 검증하는 경로다
- Phase 4 UI와 실제 제품 경로로 이어질 후보 경로다

현재 역할:
- canonical DB runtime path
- loader integration path
- UI handoff 준비 경로

현재 판단:
- 앞으로 확장될 기본 실행 경로는 이쪽이다

---

## 3. 두 경로의 관계

현재는 두 경로가 모두 필요하다.

### direct path가 필요한 이유
- provider와 DB 결과를 비교할 때 기준점이 된다
- sample 전략의 가장 단순한 예제 역할을 유지한다
- DB 이슈가 있을 때 원인 분리에 도움이 된다

### DB-backed path가 필요한 이유
- 실제 제품 구조는 DB 기반으로 가야 한다
- loader / engine / strategy 경계를 검증할 수 있다
- 향후 UI 백테스트 실행기와 자연스럽게 연결된다

즉 지금 단계에서는:
- direct path = reference / comparison / legacy sample
- DB-backed path = product-facing runtime candidate

로 이해하는 것이 가장 정확하다.

---

## 4. 권장 사용 기준

### direct path를 쓰는 경우
- 전략 자체가 도는지만 빠르게 보고 싶을 때
- DB 상태와 무관하게 provider 기준 결과를 보고 싶을 때
- 기존 예제 코드를 그대로 참고하고 싶을 때

### DB-backed path를 쓰는 경우
- 실제 DB 적재 데이터로 전략을 검증하고 싶을 때
- loader/runtime 변경이 전략 결과에 어떤 영향을 주는지 볼 때
- 앞으로 UI에서 호출될 경로를 미리 확인하고 싶을 때

---

## 5. 현재 코드 운영 원칙

현재 원칙은 다음과 같다.

1. 기존 direct-fetch sample 함수는 유지한다
2. DB 기반 경로는 `*_from_db`로 명시적으로 분리한다
3. direct path와 DB path를 같은 것으로 혼동하지 않도록 문서와 함수명을 유지한다
4. 새로운 runtime 일반화 작업은 DB-backed path를 중심으로 진행한다

---

## 6. 앞으로의 방향

Phase 3 이후에는 점점 다음 방향으로 가는 것이 맞다.

1. 전략 runtime의 중심은 DB-backed path로 이동
2. direct path는 reference / regression comparison 용도로 축소
3. Phase 4 UI는 DB-backed runtime function을 호출

즉 장기적으로는:
- direct path가 기준 예시로 남고
- DB-backed path가 실제 서비스 경로가 된다

---

## 결론

현재 `finance` 프로젝트에서:

- `portfolio_sample(...)`은 legacy reference sample
- `portfolio_sample_from_db(...)`는 DB-backed runtime sample

로 보는 것이 맞다.

두 경로는 당분간 같이 유지하되,
앞으로 확장과 제품 연결의 중심은
DB-backed runtime path에 둔다.
