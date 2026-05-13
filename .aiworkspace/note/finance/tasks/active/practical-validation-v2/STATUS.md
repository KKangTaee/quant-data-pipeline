# STATUS - Practical Validation V2

Status: Active
Last Updated: 2026-05-13

## Current Status

P2 implementation은 대부분 완료된 상태다.

최근 완료된 내용:

- ETF operability / holdings / exposure provider snapshot 수집 경로 추가
- FRED macro market-context 수집 경로 추가
- Ingestion 화면에서 Practical Validation Provider Snapshot 수집 가능
- Practical Validation Provider Data Gaps 표시와 수집 가능한 gap 보강 버튼 추가
- provider 기준일을 저장된 backtest 종료일이 아니라 Practical Validation 실행일 기준으로 보정
- official + DB bridge evidence 병합 로직 보강
- stress / sensitivity interpretation board 보강
- 12개 진단 세부 근거에 사용자-facing 설명 추가
- Practical Validation V2 상세 설계 / connector 계획 문서를 `code_analysis`에서 active task 문서로 이동

## Next

- P2-7 QA 여부 결정
- proxy / `NOT_RUN` / `REVIEW` 항목이 사용자에게 충분히 설명되는지 확인
- P2 closeout 또는 P3 진입 결정

## Current Development Boundary

- 데이터 수집은 `Workspace > Ingestion`에서 수행한다.
- Practical Validation은 DB loader를 통해 provider context를 읽는다.
- UI는 원격 provider를 직접 fetch하지 않는다.
- JSONL에는 full raw provider data를 저장하지 않는다.
