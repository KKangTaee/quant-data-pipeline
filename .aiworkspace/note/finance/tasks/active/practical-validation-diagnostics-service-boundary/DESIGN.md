# Practical Validation Diagnostics Service Boundary Design

Status: Complete
Created: 2026-05-20

## Before

```text
app/web/backtest_practical_validation.py
  -> app/services/backtest_practical_validation.py
    -> app/web/backtest_practical_validation_helpers.py
```

`backtest_practical_validation_helpers.py`는 Streamlit-free였지만 위치가 `app/web`이라, service layer가 web helper를 호출하는 구조가 남아 있었다.

## Target

```text
app/web/backtest_practical_validation.py
  -> app/services/backtest_practical_validation.py
    -> app/services/backtest_practical_validation_diagnostics.py
```

관련 화면은 source handoff나 compact curve snapshot 생성이 필요할 때 service module을 import한다.

## Transitional Notes

- moved diagnostics module은 아직 `app.web.runtime`, provider connector, curve helper를 일부 참조한다.
- 이는 기존 runtime / connector 위치를 유지한 점진적 이동이다.
- 다음 후보는 curve/helper connector를 service 또는 loader-facing adapter로 추가 분리하는 것이다.
