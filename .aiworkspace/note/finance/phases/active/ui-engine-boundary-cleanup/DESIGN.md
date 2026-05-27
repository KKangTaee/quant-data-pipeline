# UI Engine Boundary Cleanup Design

Status: Complete
Created: 2026-05-27

## Boundary Rule

이 phase의 핵심 규칙은 단순하다.

```text
app/web -> app/services -> app/runtime -> finance/*
```

허용 방향:

- `app/web`은 `app/services`와 `app/runtime`을 호출할 수 있다.
- `app/services`는 `app/runtime`, `finance/*`, loader, job wrapper를 호출할 수 있다.
- `app/runtime`은 `finance/*`, registry / saved helper, loader를 호출할 수 있다.

금지 방향:

- `app/services`와 `app/runtime`은 `streamlit`을 import하지 않는다.
- `app/services`와 `app/runtime`은 `app/web`을 import하지 않는다.
- service / runtime은 `st.session_state`, `st.toast`, `st.rerun`, chart render, button state를 알지 않는다.

## Cleanup Strategy

작업은 "전체 얕은 audit + task별 깊은 분석"으로 진행한다.
처음부터 모든 파일을 상세 재설계하지 않고, phase 시작 시 전체 위험 지도를 잡은 뒤 각 task에 들어갈 때 해당 파일을 다시 깊게 읽고 하위 단계로 쪼갠다.

## Task Detail Policy

각 task는 아래처럼 하위 단계 번호를 둔다.

- `6-01`, `6-02`처럼 task 내부 sub-step을 명시한다.
- 각 sub-step은 수정 파일, 책임 이동, 검증 기준을 가진다.
- 한 sub-step이 끝나면 status / runs를 갱신하고 다음 sub-step으로 넘어간다.

## Browser Testing Policy

Task 0은 문서 / audit 작업이라 브라우저로 확인할 화면이 없다.

향후 task에서 Streamlit 화면의 import, 화면 흐름, 버튼 결과, session state 반영이 바뀌면 브라우저를 열어 사용자가 확인할 수 있는 local URL을 제공한다.
특히 Practical Validation 화면의 provider coverage, replay result, diagnostics board가 바뀌는 task는 browser/manual QA 대상으로 본다.

## Safety Rules

- registry / saved JSONL은 수정하지 않는다.
- 계산식 변경과 구조 이동을 같은 sub-step에 섞지 않는다.
- import 이동 후 public function name과 return shape를 유지한다.
- function 이동이 어려운 큰 file은 먼저 characterization test 또는 import contract를 추가한다.
- boundary lint는 service/runtime의 Streamlit import, `st.*` 접근, `app.web` import를 hard violation으로 본다.
