# Notes

## 2026-06-08

- 공식 chain: `PORTFOLIO_SELECTION_SOURCES.jsonl -> PRACTICAL_VALIDATION_RESULTS.jsonl -> FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl -> SELECTED_DASHBOARD_PORTFOLIOS.jsonl`.
- Portfolio Monitoring은 read-only monitoring / saved setup 경계이며 live approval, broker order, account sync, auto rebalance를 만들지 않는다.
- Risk-On Momentum 5D는 Compare catalog에 포함되어 탐색 대상이지만, 문서상 Practical Validation / Final Review / Portfolio Monitoring daily signal governance 연결은 deferred 상태다.
- Strict annual / quarterly factor 계열은 숫자상 좋은 조합이 있었지만, 현재 Practical Validation replay route가 ETF dynamic strategies 중심이라 `NOT_RUN` 없이 Final Review / Monitoring까지 닫는 최종 후보에는 쓰지 않았다.
- 최종 후보는 all-ETF workflow-complete 조합이다: GTAA U5 20%, GTAA U3 75%, GRS Compact 5%.
- 비용 / turnover / net-curve proof는 각 component runtime meta에서 가져와 weighted source contract에 연결했다. Weighted mix 자체의 추가 sleeve-level rebalance cost는 별도 모델링하지 않았고, component net curve를 합성한 결과로 해석한다.
- Monitoring helper의 기본 기간 표시 일부는 component별 coverage를 넓게 읽을 수 있다. 성능 판단은 intersection replay / performance recheck의 실제 period를 기준으로 해석한다.
