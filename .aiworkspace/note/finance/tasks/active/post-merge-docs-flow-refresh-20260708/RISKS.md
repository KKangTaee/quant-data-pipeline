# Risks

## Open Risks

- 공용 문서가 매우 길어 최신 작업 로그와 durable product state가 섞이기 쉽다. 이번 refresh는 current pointer / code flow / surface boundary 정렬에 집중하고, 대규모 문서 재구성은 별도 task로 분리해야 한다.
- `Futures Monitor` 표현은 일부 legacy runbook / 과거 task 설명에는 남을 수 있다. current user-facing tab 또는 primary surface처럼 읽히는 문장만 고친다.
- untracked QA screenshots는 이번 문서 작업 산출물이 아니므로 stage / commit하지 않는다.
- `Data Health`는 current primary Overview tab이 아니지만, Operations / System의 관리 메타 이름으로는 남는다. 이번 보정은 Overview cockpit / handoff의 클릭 경로와 user-facing target label 정렬에 한정한다.
- 후속 후보: post-merge docs refresh마다 current tab list, latest completed task pointer, data-health handoff target을 점검하는 consistency checker를 만들면 문서와 service contract drift를 줄일 수 있다.
