# Portfolio Monitoring Initial Setting Correction V1 Risks

- 시작일만 바꾸고 entry close/history load 범위를 그대로 두면 최초 투자금과 가치곡선이 잘못된다.
- group timeline이 원본 item date를 계속 읽으면 개별 lane과 그룹 KPI가 불일치한다.
- 새 시작일보다 이른 기존 buy/sell을 허용하면 음의 시간 순서가 생긴다.
- 기존 initial correction row의 optional date가 비어 있는 경우 원본 item fallback이 필요하다.
- actual schema migration은 두 nullable date column을 첫 실행에만 추가하고 두 번째 실행이 no-op임을 확인했다. 기존 row count와 JSONL checksum도 보존됐다.
- Browser QA의 실제 저장 interaction은 in-app Browser와 Streamlit component iframe 사이 selection event가 server session으로 되돌아오지 않아 미실행이다. production command/UI 계약은 자동화 테스트가 검증했지만, 배포 전 일반 브라우저에서 날짜 변경 → preview → 저장 → 같은 종목 recovery를 한 번 확인하는 것이 좋다.
- repo-wide UI/Engine boundary check에는 기존 `app/services/backtest_workflow_shell.py`의 `app.web.backtest_workflow_routes` import hard violation 1건이 남아 있다. 이번 Portfolio Monitoring 변경 파일에는 해당 경계 위반이 없다.
