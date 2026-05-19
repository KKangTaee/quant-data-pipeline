# Practical Validation Service Boundary Design

Status: Complete
Created: 2026-05-20

## Current Coupling

현재 Practical Validation 흐름은 아래 책임이 섞여 있다.

| 책임 | 현재 위치 | 문제 |
|---|---|---|
| 화면 입력 / 렌더 | `app/web/backtest_practical_validation.py` | UI 책임이므로 유지 가능 |
| result 생성 | `app/web/backtest_practical_validation_helpers.py` | 계산 로직이 `app/web`에 남아 있고 service boundary가 없음 |
| result 저장 | `app/web/backtest_practical_validation_helpers.py` | 저장 use-case가 화면 helper에 있음 |
| Final Review handoff | `app/web/backtest_practical_validation_helpers.py` | helper가 `st.session_state`를 직접 수정함 |
| provider gap job 실행 | `app/web/backtest_practical_validation.py` | interactive job orchestration과 UI state가 결합됨 |

## Target Boundary

1차 경계:

```text
Streamlit UI
  -> app.services.backtest_practical_validation
    -> app.web.backtest_practical_validation_helpers
    -> app.web.runtime.portfolio_selection_v2 append/load helper
```

역할:

- Service: result 생성, 저장, Final Review handoff payload / notice contract 생성
- Service: Practical Validation source 저장과 source handoff payload / notice contract 생성
- UI: profile form, recheck button, provider gap button, screen render, `st.session_state` 반영
- Helper: diagnostic 계산 / dataframe 변환 같은 기존 pure-ish 계산 helper

## Migration Rule

- 첫 slice는 behavior-preserving wrapper다.
- UI session state key는 변경하지 않는다.
- registry append 함수는 기존 runtime helper를 그대로 사용한다.
- `BLOCKED` source는 계속 Final Review button에서 disable한다.
- `NOT_RUN`은 pass가 아니라 disclosure / review 대상이라는 의미를 유지한다.

## Implemented Slice

- `app/services/backtest_practical_validation.py` added.
- `prepare_practical_validation_source_handoff()` returns a UI-neutral contract for source handoff.
- `prepare_final_review_handoff_from_validation()` returns a UI-neutral contract for Final Review handoff.
- `save_practical_validation_result()` and source append calls live in the service layer.
- `app/web/backtest_practical_validation_helpers.py` no longer imports Streamlit.

## Later Slices

- provider gap collection plan / run orchestration service 분리
- replay plan / actual replay result wrapper service 분리
- large diagnostic builder를 `app/services` 또는 `finance` domain layer로 이동할지 재평가
