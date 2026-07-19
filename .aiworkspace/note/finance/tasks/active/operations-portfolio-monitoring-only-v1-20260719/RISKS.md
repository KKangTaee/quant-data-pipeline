# Operations Portfolio Monitoring Only V1 Risks

- `/operations`, `/ops-review` 직접 bookmark는 제거 후 동작하지 않는다. 사용하지 않는 화면이므로 alias를 남기지 않는다.
- current durable docs와 service copy의 System / Data Health destination은 Ingestion 기록 경로로 정렬했다.
- 과거 active/done task 문서는 역사 기록이므로 명칭을 일괄 치환하지 않는다.
- Operations 전용 테스트를 단순 삭제하면 회귀 공백이 생길 수 있다. Portfolio Monitoring-only navigation과 Ingestion 기록 보존 계약으로 교체한다.
- 사용자 소유 untracked QA screenshots와 `.superpowers/`는 이 task에서 stage하거나 수정하지 않는다.
- static UI/engine boundary 전체 검사는 이번 변경 이전부터 존재한 `app/services/backtest_workflow_shell.py:6`의 web import 1건 때문에 통과하지 않는다. 이번 task의 변경 파일에는 새 boundary 위반이 없다.
