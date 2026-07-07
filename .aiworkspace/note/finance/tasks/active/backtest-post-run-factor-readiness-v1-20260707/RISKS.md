# Risks

- Runtime meta에 월별 PIT membership 전체가 충분히 남아 있지 않으면 V1은 result-level excluded / missing evidence 중심으로 시작해야 한다.
- 전체 월별 universe audit은 DB membership snapshot과 rebalance calendar를 직접 읽는 후속 작업이 필요할 수 있다.
- statement raw/shadow 데이터가 부족해 runtime이 bundle 생성 전 실패하는 케이스는 별도 error-context 모델이 필요하다. 이번 V1은 successful bundle의 post-run readiness에 초점을 둔다.
- Browser QA는 form placement 확인까지 수행했다. 실제 post-run panel은 DB 상태 / 실행 비용 때문에 자동으로 full backtest를 재실행하지 않았다.
