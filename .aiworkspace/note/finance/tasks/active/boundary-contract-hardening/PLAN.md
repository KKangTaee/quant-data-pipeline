# Boundary Contract Hardening Plan

Status: Complete
Created: 2026-05-27

## 이걸 하는 이유?

Task 6~8에서 `app/services`와 `app/runtime`의 Streamlit/UI 의존을 줄이고, Practical Validation helper와 runtime result bundle helper를 분리했다.
이제 필요한 것은 새 구조가 다시 흐트러지지 않게 자동 검증을 강하게 만드는 것이다.

이 task가 끝나면 `app/services`와 `app/runtime`은 Streamlit뿐 아니라 `app.web` helper에도 의존하지 않는 layer로 보호된다.
그래야 이후 UI agent와 engine/runtime agent가 서로의 파일을 덜 건드리고 병렬 작업하기 쉬워진다.

## Scope

포함한다.

- UI / engine boundary lint에서 `app.services/app.runtime -> app.web` import를 hard failure로 승격
- boundary lint behavior contract test 추가
- service/runtime import contract test 보강
- runbook / phase / roadmap 문서 정렬
- phase closeout QA

포함하지 않는다.

- Streamlit 화면 UX 변경
- DB / strategy algorithm 변경
- provider ingestion 추가
- registry / saved JSONL 변경

## Steps

| Step | Goal | Status |
| --- | --- | --- |
| `9-01` | boundary lint hardening | Complete |
| `9-02` | service / boundary contract test 보강 | Complete |
| `9-03` | docs / runbook 정렬 | Complete |
| `9-04` | phase closeout QA | Complete |

## Done Criteria

- `check_ui_engine_boundary.py`가 `app.services/app.runtime -> app.web` import를 hard violation으로 보고한다.
- 관련 behavior가 test로 고정된다.
- `py_compile`, boundary lint, service contract test, diff check가 통과한다.
- docs/runbook에서 더 이상 `app.web import advisory`라고 설명하지 않는다.
- UI 변경이 없으므로 browser QA 생략 사유가 기록된다.
