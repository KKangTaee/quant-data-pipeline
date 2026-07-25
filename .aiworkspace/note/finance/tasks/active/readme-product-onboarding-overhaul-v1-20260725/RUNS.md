# README Product / Onboarding Overhaul V1 Runs

## 2026-07-25 — Design Discovery

- `README.md`, `docs/INDEX.md`, `docs/ROADMAP.md`, `docs/PROJECT_MAP.md`, `docs/PRODUCT_DIRECTION.md` 확인
- `git log --follow -- README.md`와 `git blame README.md`로 마지막 실질 개편 시점 확인
- `app/web/streamlit_app.py`에서 current top navigation과 route 확인
- `pyproject.toml`, `.python-version`, React component `package.json` 확인
- committed `component_static` bundle 존재와 Node runtime 비필수 경계 확인
- `docs/architecture/`, `docs/runbooks/`, `tests/`로 구현 / 검증 경계 확인

## Result

- 설계 문서 작성 완료
- README implementation / screenshot capture / verification은 아직 실행하지 않음

## 2026-07-25 — Implementation Plan

- `writing-plans` 기준으로 `PLAN.md`를 4개 independently verifiable task로 확장
- exact files, interface, command, expected result, commit boundary 기록
- spec coverage, placeholder, task structure, `git diff --check` self-review 통과

## 2026-07-26 — Baseline Test Harness Investigation

- full-suite one-shot은 `PYTHONPATH=.`와 ephemeral pytest를 사용해 `2035 passed / 319 failed`
- 다수 테스트가 Streamlit-free contract를 위해 `sys.modules`에서 `streamlit`을 제거해 한 process 전체 실행에서 singleton / module state가 교차 오염됨
- full run에서 실패한 Today 61개, Final Review 1개, Overview service contract 1개를 격리·결합 재실행해 `63 passed`
- 사용자 승인에 따라 README와 무관한 full-suite harness gap은 별도 범위로 남기고 task-specific verification을 사용

## 2026-07-26 — 1차 Product Journey

- 옛 `Workspace / Operations / Selected Portfolio Dashboard`와 stale current-focus 표현 존재 확인
- README를 Evidence-first product positioning, current surface map, Portfolio Lab 3단계, product workflow와 non-goal 중심으로 재작성
- current 7개 surface assertion, old label 부재, `git diff --check` 통과

## 2026-07-26 — 2차 Quick Start / Technical Architecture

- Python 3.12, `pyproject.toml`, Today committed `component_static`과 frontend manifest 존재 확인
- default `8501` quick start와 multiple-worktree `8510` example, provider `.env`와 current local MySQL limitation 기록
- Python / Streamlit / React / TypeScript / Vite / MySQL / JSONL ownership, architecture Mermaid, repository / storage / trust / verification map 작성
- backtest-dev `8510` listener가 current worktree cwd를 사용하고 HTTP 200을 반환함을 확인
- README 321 lines, 기술·PIT·bias keyword assertion과 `git diff --check` 통과
