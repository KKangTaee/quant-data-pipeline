# Main-dev Master Merge Resolution Risks

State: complete
Last Updated: 2026-08-17

## Residual Risks

- broad `tests/test_service_contracts.py`에는 병합 전부터 존재한 Final Review / Practical
  Validation source drift, Sentiment fixture, Futures thermometer fixture 관련 18 failures가 남아 있다.
  이번 통합의 신규 failure는 0건으로 복구했지만 별도 owning task에서 정리해야 한다.
- local registry / run history / QA artifact는 unstaged로 보존한다.
- Browser QA는 저장된 actual data를 읽는 화면 확인만 수행했고 refresh button은 실행하지 않았다.
