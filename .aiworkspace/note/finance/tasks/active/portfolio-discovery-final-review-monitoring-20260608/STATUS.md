# Status

Status: Completed
Last Updated: 2026-06-08 11:35 KST

## Progress

- 1차 완료: docs read order, Backtest workflow boundary, strategy compare catalog, Final Review / Portfolio Monitoring runtime boundary 확인.
- 2차 완료: Compare catalog의 현행 전략을 탐색했고, 숫자상 strict/factor 후보와 workflow-complete all-ETF 후보를 분리했다.
- 3차 완료: all-ETF 후보를 Practical Validation replay와 Final Review selected-route gate로 검증했다.
- 4차 완료: Final Review decision과 Portfolio Monitoring saved setup을 저장하고 monitoring performance recheck를 실행했다.

## Current Position

전체 roadmap 중 4차까지 완료했다. 이번 task는 코드 / UX 변경 없이 현재 제품 workflow를 운용했다.

## Final Candidate

- Portfolio: GTAA U5 20% / GTAA U3 75% / GRS Compact 5%.
- Selection source: `selection_weighted_portfolio_mix_monitoring_candidate_gtaa_u3_u5_grs_20260608_28206caf`.
- Practical Validation: `validation_selection_weighted_portfolio_mix_monitoring_candidate_gtaa_u3_u5_grs_20260608_28206caf_3bf891d6`.
- Final Review decision: `final_gtaa_u3_u5_grs_monitoring_20260608`.
- Portfolio Monitoring setup: `selected_dashboard_portfolio_gtaa_u3_u5_grs_20260608`.

## Key Metrics

- Candidate intersection period: 2016-08-31 to 2026-02-28.
- Candidate CAGR: 13.90%; MDD: -13.44%; Sharpe: 1.16.
- Same-period SPY reference used in search: CAGR 12.90%; MDD -24.90%.
- Stored-period replay: PASS, CAGR 13.88%, MDD -13.37%.
- Monitoring performance recheck: `SELECTION_THESIS_HOLDS`.
