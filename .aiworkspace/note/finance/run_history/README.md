# Finance Run History

Status: Active
Last Verified: 2026-05-28

이 폴더는 로컬 실행 이력을 담는 JSONL 파일을 둔다.

## 포함 파일

- `BACKTEST_RUN_HISTORY.jsonl`: Backtest UI에서 저장한 전략 실행 / replay 이력
- `WEB_APP_RUN_HISTORY.jsonl`: Operations / data job 실행 이력

## 사용 기준

run history는 재현과 디버깅에는 유용하지만 로컬 생성물 성격이 강하다.
투자 판단 source-of-truth가 아니며, 중요한 전략 결과는 `.aiworkspace/note/finance/reports/backtests/`에 사람이 읽는 report로 따로 요약한다.
