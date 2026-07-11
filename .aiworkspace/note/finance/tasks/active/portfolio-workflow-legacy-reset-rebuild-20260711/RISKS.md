# Risks

- 구형 단일 GRS 4개의 replay contract 복원과 6개 후보 runtime 재실행은 완료됐다.
- stored-period replay를 사용했으므로 최신 시장일까지 확장한 재평가는 이번 reset 범위가 아니다.
- append-only registry reset의 rollback snapshot은 `/tmp/quant-data-pipeline-backtest-dev-portfolio-reset-20260711T094422/`에만 있다. `/tmp` 정리 전까지만 복구용으로 사용할 수 있다.
- Browser QA는 localhost URL 보안 정책 때문에 미실행이다. 사용자가 앱에서 Final Review를 새로 열어 6개 후보와 역할별 REVIEW 표시를 최종 육안 확인할 수 있다.
