# Phase 4 Second Strategy GTAA Addition

## 목적
이 문서는 Phase 4 first-pass UI에
두 번째 공개 전략으로 `GTAA`를 추가한 결과를 정리한다.

현재 범위:
- single-strategy execution
- DB-backed
- first public price-only strategies

---

## 현재 결정

두 번째 공개 전략은 `GTAA`로 추가했다.

추가 이유:
- `Equal Weight`보다 한 단계 더 복잡한 price-only 전략이다
- momentum / MA / score 기반 runtime이 실제 UI에서도 잘 이어지는지 확인하기 좋다
- 아직 factor/fundamental snapshot 전략으로 넘어가기 전의 적절한 중간 단계다

---

## 구현 결과

현재 추가된 것:

### 1. Public runtime wrapper
- `run_gtaa_backtest_from_db(...)`

위치:
- `app/web/runtime/backtest.py`

책임:
- ticker/date/timeframe 입력 정규화
- DB-backed GTAA sample 실행
- 공통 result bundle 반환

### 2. Backtest tab strategy selector
- `Equal Weight`
- `GTAA`

위치:
- `app/web/pages/backtest.py`

의미:
- Phase 4 first pass는 여전히 single-screen
- 하지만 전략 선택기를 통해 현재 공개 전략 두 개를 전환 가능

### 3. GTAA 전용 form

현재 입력:
- preset/manual universe
- start date
- end date
- advanced:
  - timeframe
  - option
  - top assets
  - signal interval (months)

---

## 검증 결과

`.venv` 기준 wrapper smoke check:

- `run_gtaa_backtest_from_db(...)`
- `start=2016-01-01`
- `end=2026-03-20`
- GTAA 기본 유니버스

확인 결과:
- `strategy_name = GTAA`
- `End Balance = 22589.1`
- DB-backed sample parity 기준 결과와 일치

---

## 현재 UI 의미

이제 `Backtest` 탭은:

- `Equal Weight`
- `GTAA`

두 전략을 DB-backed runtime path로 실행할 수 있다.

하지만 여전히 first-pass 성격은 유지한다.

즉:
- multi-strategy comparison UI는 아직 아님
- factor/fundamental 전략 UI도 아직 아님
- single-run + result inspection 단계다

---

## 다음 자연스러운 확장

현재 이후 후보:

1. 세 번째 전략 추가
2. 백테스트 실행 이력 저장
3. 시각화 확장
4. factor/fundamental 전략 준비 문서화

---

## 결론

Phase 4 first-pass UI는 이제:
- `Equal Weight`
- `GTAA`

두 개의 공개 DB-backed price-only 전략을 실행할 수 있는 상태다.

후속 보강:
- GTAA의 기존 고정 `2개월` cadence는 더 이상 하드코딩 상태가 아니며,
  `Advanced Inputs`의 `Signal Interval (months)`에서 조정 가능하다.
