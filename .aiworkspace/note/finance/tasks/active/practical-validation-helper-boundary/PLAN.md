# Practical Validation Helper Boundary Plan

Status: Complete
Created: 2026-05-27

## 이걸 하는 이유?

`app/services`는 UI와 engine 사이의 Streamlit-free boundary여야 한다.
그런데 현재 Practical Validation diagnostics / replay service가 `app/web` 아래의 curve / provider context helper를 import하고 있다.

이 helper들은 화면 render나 session state를 다루지 않는다.
따라서 `app/web`에 남아 있으면 실제 책임과 파일 위치가 어긋나고, 이후 UI agent와 engine/service agent가 같은 web helper를 서로 다른 이유로 건드릴 수 있다.

이 task는 계산 결과를 바꾸지 않고 helper 위치만 service boundary로 옮겨, `app/services`와 `app/runtime`이 `app/web`을 거꾸로 import하지 않는 상태를 만든다.

## Scope

포함한다.

- `6-01`: Practical Validation curve helper를 `app/services`로 이동
- `6-02`: provider context helper를 `app/services`로 이동하고 이름을 책임에 맞게 정리
- `6-03`: docs / service contract / boundary lint 정렬

포함하지 않는다.

- Practical Validation 계산식 변경
- provider loader / ingestion 변경
- Streamlit 화면 UX 변경
- registry / saved JSONL 변경
- Task 7 diagnostics service split

## Done Criteria

- `rg -n "from app\\.web\\.|import app\\.web\\." app/services app/runtime -g '*.py'` 결과가 없다.
- boundary lint의 advisory가 0건이다.
- service contract tests가 통과한다.
- 관련 durable docs가 새 helper 위치를 가리킨다.
- UI-visible behavior 변경이 없으면 browser QA는 생략 사유를 기록한다.
