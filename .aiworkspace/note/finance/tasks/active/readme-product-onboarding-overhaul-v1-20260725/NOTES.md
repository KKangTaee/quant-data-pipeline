# README Product / Onboarding Overhaul V1 Notes

## Current-State Findings

- root README의 마지막 실질 개편은 2026-05-13이다.
- README navigation은 `Workspace / Operations / Reference`를 사용하지만 실제 앱은 `Research / Portfolio / Data / Help`다.
- 기존 README는 Backtest -> Practical Validation -> Final Review -> Selected Portfolio Dashboard에 집중한다.
- 현재 제품은 Today, Market Research, Institutional Holdings와 current Portfolio Monitoring까지 범위가 넓어졌다.
- 기존 “현재 개발 초점”은 5월 상태를 복제해 drift했다.
- Python project metadata의 description placeholder는 이번 README task 범위 밖이다.

## Decisions

- README는 한국어를 기본으로 하고 code / product contract 명칭은 현재 코드의 영어 이름을 유지한다.
- product-first, developer-second의 균형형 문서로 만든다.
- 대표 화면은 Today 1장만 사용한다.
- Node.js는 runtime prerequisite로 표시하지 않는다.
- DB setup 전체를 root README에 복제하지 않는다.
- app이 빈 DB에서도 unavailable / missing evidence를 숨기지 않는다는 점을 정상 경계로 설명한다.
- current MySQL local-default contract를 env-configured architecture처럼 과장하지 않는다.
- active task snapshot을 README에 복제하지 않는다.
- 일반 quick start는 Streamlit default `8501`, backtest-dev actual screenshot / Browser QA는 `8510`을 사용한다.
- Browser screenshot API의 실제 output은 JPEG였으므로 README asset은 `.jpg`로 관리한다.
- route 이름은 `st.Page(title=...)`의 navigation contract를 기준으로 유지하고, 화면별 질문형 H1 또는 `Ingestion` 같은 본문 제목과 구분한다.
- README는 7개 top-level surface를 설명하되 Practical Validation과 Final Review는 Portfolio Lab 내부 stage로 유지한다.
- 제품 code와 canonical architecture / data / flow 문서는 바뀌지 않았으므로 durable docs 본문을 중복 수정하지 않고 README와 root handoff만 동기화한다.
- README 검증 명령은 시스템 `python`이 아니라 project runtime인 `uv run python`을 사용한다.

## Protected Existing Work

다음은 작업 시작 전부터 존재한 사용자 / runtime 변경으로 이번 task에서 건드리지 않는다.

- `.aiworkspace/note/finance/registries/*.jsonl` 변경
- `.aiworkspace/note/finance/run_history/*.jsonl`
- `.aiworkspace/note/finance/saved/*.jsonl`
- root의 기존 Backtest / Today / Market / Final Review QA image와 snapshot
- `.superpowers/`

## Final Maintenance Contract

- README는 제품 정의, 빠른 실행, 구현 언어와 계층 경계, 신뢰 원칙, durable docs 진입점을 소유한다.
- active task, 최근 완료 작업, 실행 로그와 일시적인 product 상태는 README에 복제하지 않는다.
- navigation이나 저장 경계가 바뀌면 `app/web/streamlit_app.py`와 canonical finance docs를 먼저 갱신한 뒤 README를 다시 대조한다.
