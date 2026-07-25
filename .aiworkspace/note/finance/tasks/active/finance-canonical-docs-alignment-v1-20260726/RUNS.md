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
