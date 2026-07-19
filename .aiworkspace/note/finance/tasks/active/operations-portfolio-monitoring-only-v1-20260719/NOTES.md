# Operations Portfolio Monitoring Only V1 Notes

## Findings

- `Operations Overview`는 최신 Portfolio Monitoring workspace와 run history를 읽어 summary와 링크를 만드는 중복 landing이다.
- `System / Data Health`는 persistent run history, raw logs, failure CSV, artifact/runtime inspection을 위한 internal ops console이다.
- `Workspace > Ingestion > 실행 기록 / 결과`는 session result, persistent history, recent logs, failure CSV를 이미 제공한다.
- 사용자는 앱에서 failure CSV, log, artifact path를 직접 검사하지 않는다고 확인했다.
- Portfolio Monitoring React Command Center는 현재 post-selection monitoring의 user-facing product value를 충분히 소유한다.

## Decision

중복 화면을 숨겨 두지 않고 전용 코드까지 제거한다. 저장 데이터와 generated artifacts는 삭제하지 않으며, 과거 task 문서는 역사 기록으로 보존한다.

## Closeout

- Operations의 사용자 질문은 `선정한 포트폴리오를 지금 어떻게 추적할 것인가?` 하나로 좁혔다.
- 진단 기능을 Portfolio Monitoring으로 옮기지 않았다. 운영 근거가 필요할 때는 기존 Ingestion 기록 화면을 사용한다.
- 과거 문서의 역사적 언급은 보존하고 current-state 문서와 앱 안내만 정렬했다.
- 실제 Browser QA screenshot은 repository 밖 generated artifact가 아니라 worktree root의 untracked 파일로 남겼다.
