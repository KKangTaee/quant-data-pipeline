# Finance Canonical Docs Alignment V1 Runs

## 2026-07-26 — Discovery

- `INDEX.md`, `PRODUCT_DIRECTION.md`, `PROJECT_MAP.md`, `ROADMAP.md` 전체 구조 확인
- `app/web/streamlit_app.py`의 `Research / Portfolio / Data / Help`와 7개 route 확인
- active task state manifest와 named active / paused / QA-only task `STATUS.md` 대조
- 최근 commit과 README 개편 결과 확인
- 네 문서의 line count, task link, completed marker, old navigation 표현 계량
- INDEX local Markdown link 143개 존재 검사: missing 0
- Project Map 주요 path 후보 검사: current path는 대체로 유효

## Result

- link breakage보다 역할 혼합과 rolling history 누적이 주요 문제다.
- 사용자 승인에 따라 INDEX를 포함한 역할 분리형 전면 정리를 설계했다.
- canonical docs implementation은 written spec 검토 후 시작한다.

## 2026-07-26 — Task 1 INDEX

- 기존 INDEX task-path 124개와 `Current Phase State` rolling history 존재 확인
- INDEX를 Purpose / Start Here / Reading Paths / Canonical Docs / Current Work /
  Workspace Boundaries / Maintenance Rules 구조로 재작성
- 108 lines, literal task-path reference 3개, required section 6개 확인
- local Markdown link existence 검사 통과
- 개별 완료 task 목록을 제거하고 Roadmap / task index / manifests로 discovery를 단일화

## 2026-07-26 — Task 2 Product Direction

- old `Workspace / Operations / Backtest / Reference` navigation 표현 존재 확인
- Product Promise / Who It Is For / User Journey / Current Product Surfaces /
  Principles / Safety / Maturity 구조로 121 lines 재작성
- current navigation group, 7개 surface, Practical Validation / Final Review 내부
  stage와 product boundary keyword assertion 통과
- local link와 `git diff --check` 통과

## 2026-07-26 — Task 3 Project Map

- `streamlit_app.py`에서 7개 `st.Page` title과 app / finance inventory 재확인
- System / Layer / Surface Entry / Workflow / Storage / Change-Type /
  Detailed Documentation 구조로 199 lines 재작성
- current surface와 core layer assertion, old navigation 부재 확인
- backtick code / storage path existence 검사에서 optional 미생성 artifact path 1개를
  발견해 policy 표현으로 교정한 뒤 전체 path 검사 통과
- line cap과 `git diff --check` 통과
