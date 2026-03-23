# Phase 4 Third Strategy Risk Parity Addition

## 목적
이 문서는 Phase 4 first-pass UI에
세 번째 공개 전략으로 `Risk Parity Trend`를 추가한 결과를 정리한다.

현재 범위:
- single-strategy execution
- DB-backed
- first public price-only strategies

---

## 현재 결정

세 번째 공개 전략은 `Risk Parity Trend`로 추가했다.

추가 이유:
- price-only 범위 안에서 분산/리스크 기반 전략을 확인할 수 있다
- `Equal Weight`, `GTAA`와 다른 성격의 의사결정 규칙을 가진다
- Phase 4 first pass가 단순 모멘텀/랭킹 전략만 다루는 상태를 넘어선다

---

## 구현 결과

### 1. Public runtime wrapper
- `run_risk_parity_trend_backtest_from_db(...)`

위치:
- `app/web/runtime/backtest.py`

### 2. Backtest tab strategy selector 확장
- `Equal Weight`
- `GTAA`
- `Risk Parity Trend`

위치:
- `app/web/pages/backtest.py`

### 3. Risk Parity Trend 전용 form

현재 입력:
- preset/manual universe
- start date
- end date
- advanced:
  - timeframe
  - option

기본 preset:
- `SPY`
- `TLT`
- `GLD`
- `IEF`
- `LQD`

---

## 검증 결과

`.venv` 기준 wrapper smoke check:

- `run_risk_parity_trend_backtest_from_db(...)`
- `start=2016-01-01`
- `end=2026-03-20`
- risk parity 기본 유니버스

확인 결과:
- `strategy_name = Risk Parity Trend`
- `End Balance = 15880.0`
- DB-backed sample parity 기준 결과와 일치

---

## 현재 UI 의미

이제 `Backtest` 탭은:

- `Equal Weight`
- `GTAA`
- `Risk Parity Trend`

세 개의 공개 DB-backed price-only 전략을 전환 실행할 수 있다.

하지만 여전히 현재 단계는:
- multi-strategy comparison 화면은 아님
- factor/fundamental 전략 화면도 아님
- single-run 실행과 결과 확인이 중심이다

---

## 다음 자연스러운 확장

현재 이후 후보:

1. `Dual Momentum` 추가
2. 백테스트 실행 이력 저장
3. 시각화 강화
4. multi-strategy comparison 설계

---

## 결론

Phase 4 first-pass UI는 이제:
- `Equal Weight`
- `GTAA`
- `Risk Parity Trend`

세 개의 공개 DB-backed price-only 전략을 실행할 수 있는 상태다.
