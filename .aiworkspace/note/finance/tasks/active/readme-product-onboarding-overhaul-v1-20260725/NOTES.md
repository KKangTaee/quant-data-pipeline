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

## Protected Existing Work

다음은 작업 시작 전부터 존재한 사용자 / runtime 변경으로 이번 task에서 건드리지 않는다.

- `.aiworkspace/note/finance/registries/*.jsonl` 변경
- `.aiworkspace/note/finance/run_history/*.jsonl`
- `.aiworkspace/note/finance/saved/*.jsonl`
- root의 기존 Backtest / Today / Market / Final Review QA image와 snapshot
- `.superpowers/`
