# Finance Run History

이 폴더는 로컬 실행 이력을 담는 JSONL 파일을 둔다.

## 포함 파일

- `BACKTEST_RUN_HISTORY.jsonl`: Backtest UI에서 저장한 전략 실행 / replay 이력
- `WEB_APP_RUN_HISTORY.jsonl`: Operations / data job 실행 이력

## 사용 기준

run history는 재현과 디버깅에는 유용하지만 로컬 생성물 성격이 강하다. 중요한 전략 결과는 `backtest_reports/`의 strategy log에 따로 요약한다.
