# README Product / Onboarding Overhaul V1 Risks

## Open Risks

### README가 다시 current-state log가 될 위험

- 대응: active task와 최근 완료 목록을 복제하지 않고 canonical roadmap / task index로 연결한다.

### Quick start가 실제 DB 준비보다 쉬워 보일 위험

- 대응: app process 시작과 DB-backed feature readiness를 분리하고, MySQL / initial collection은 상세 runbook으로 넘긴다.

### MySQL 설정을 실제보다 통합된 구조로 설명할 위험

- 대응: 현재 local-default connection contract를 그대로 밝히고 env-based unified configuration을 주장하지 않는다.

### 대표 화면에 개인 / runtime-specific 상태가 포함될 위험

- 대응: 캡처 전 Today 화면의 값과 노출 범위를 확인하고 README용 stable viewport / 상태를 사용한다.

### React 기술 설명이 runtime prerequisite를 혼동시킬 위험

- 대응: committed production bundle과 frontend development dependency를 분리한다.

### README가 지나치게 길어질 위험

- 대응: 화면 설명은 2~3문장, component별 명령과 schema detail은 canonical docs link로 제한한다.

## Current Blockers

없음.

## Non-Blocking Verification Gap

전체 pytest one-shot은 Streamlit module / singleton isolation이 보장되지 않아 test order에 따라 대량 실패한다.
이번 README task는 실패했던 대표 63개 isolated test의 통과와 문서 전용 검증을 기준으로 진행한다.
pytest dev dependency 선언과 full-suite isolation은 별도 test-harness task 대상이며 README 완료를 차단하지 않는다.

## Closeout

- README local link, diagram structure, navigation contract, 8510 actual Browser QA에는 남은 blocker가 없다.
- 대표 이미지는 특정 날짜의 sample evidence 값을 포함하므로 향후 Today shell이 크게 바뀔 때만 교체한다. 단순 데이터 값 변화만으로 매번 갱신하지 않는다.
- canonical product / architecture / data / flow behavior는 이번 문서 작업에서 변경하지 않았다.
