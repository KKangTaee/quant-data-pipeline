# Practical Validation Replay Service Boundary Design

## Current Coupling

`app/web/backtest_practical_validation_replay.py`는 Streamlit을 import하지 않는 pure-ish runtime helper지만,
파일 위치가 `app/web` 아래라 UI module처럼 보인다.
현재 Practical Validation UI는 이 파일에서 recheck mode constant, plan builder, actual replay runner를 직접 가져온다.

## Target Boundary

```text
Streamlit UI
  -> app.services.backtest_practical_validation_replay
       build_practical_validation_recheck_plan()
       run_practical_validation_actual_replay()
  -> app.web.runtime.backtest / finance runtime
```

역할:

- Service replay module: DB 최신 시장일 조회, recheck period plan, existing strategy runtime replay, component / portfolio curve evidence 생성
- UI: mode selector, run button, session state, result display

## Behavior Preservation

- recheck mode key와 label은 변경하지 않는다.
- session state key 생성 방식은 UI에 그대로 둔다.
- 저장 기간 재현 / 최신 DB 확장 검증 semantics를 변경하지 않는다.
- 실제 replay execution은 기존 함수 내용을 이동만 한다.

## Transitional Debt

이동한 service replay module은 아직 `app.web.runtime.backtest`와 `app.web.backtest_practical_validation_curve`를 사용한다.
현재 boundary lint에서는 `app.services -> app.web` import를 advisory로만 보고 있으므로,
이번 slice는 책임 위치를 먼저 바로잡고 runtime / curve module 재배치는 별도 task로 남긴다.
