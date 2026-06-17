# Portfolio Discovery / Final Review / Monitoring 2026-06-08

Status: Completed
Last Verified: 2026-06-08

## Purpose

현재 Finance 프로그램의 기존 전략과 Backtest -> Practical Validation -> Final Review -> Portfolio Monitoring 흐름을 사용해, SPY보다 CAGR이 높고 MDD가 낮으며 MDD 15% 미만인 모니터링 후보 포트폴리오를 찾는다.

## 이걸 하는 이유?

사용자는 단순 백테스트 숫자가 아니라 Final Review를 지나 Portfolio Monitoring에 등록 가능한 검증 완료 후보를 원한다. 따라서 성과 필터, validation gate, final selected decision, dashboard monitoring setup을 같은 source chain으로 남겨야 이후 Operations 화면에서 계속 확인할 수 있다.

## Tentative Roadmap

| 차수 | 목적 | 범위 | 완료 조건 |
|---|---|---|---|
| 1차 | 실행 경계 확인 | docs / strategy catalog / registry / saved setup 확인 | 모든 현행 전략 목록과 공식 source chain 확인 |
| 2차 | 후보 탐색 | 현재 compare catalog 전략 전체 실행, SPY 대비 CAGR / MDD 필터, weighted 조합 탐색 | MDD < 15%, SPY 대비 CAGR 우위 / MDD 우위 후보 압축 |
| 3차 | 검증 chain 통과 | source 저장, latest replay 포함 Practical Validation 생성, Final Review selected decision 저장 | Final Review selected-route gate 통과 row 생성 |
| 4차 | Monitoring 등록 확인 | Selected Dashboard portfolio setup 저장, dashboard state / handoff / recheck 가능성 확인 | Portfolio Monitoring state에서 complete strategy slot 확인 |

## Result

- 1차~4차 완료.
- Final selected decision: `final_gtaa_u3_u5_grs_monitoring_20260608`.
- Monitoring setup: `selected_dashboard_portfolio_gtaa_u3_u5_grs_20260608`.
- Final candidate: GTAA U5 20% / GTAA U3 75% / GRS Compact 5%.
- Practical Validation replay: PASS.
- Final Review gate: `READY_WITH_REVIEW`, selected-route preflight: `SELECTED_ROUTE_PREFLIGHT_READY`.
- Portfolio Monitoring performance recheck: `SELECTION_THESIS_HOLDS`.

## Scope

- Backtest Compare catalog의 현행 전략을 모두 탐색한다.
- SPY 대비 CAGR / MDD를 비교한다.
- 최종 후보는 Practical Validation과 Final Review selected-route 기준을 통과해야 한다.
- Operations > Portfolio Monitoring saved setup에 등록한다.
- 실행 기록, 통과/탈락 이유, 검증 공백은 task 문서에 남긴다.

## Not In Scope

- 새 전략 개발 또는 전략 로직 수정.
- Streamlit UX / workflow 구조 변경.
- provider / FRED / external source를 UI에서 직접 fetch하는 변경.
- live approval, broker order, account sync, auto rebalance.
- 기존 registry / saved JSONL 재작성 또는 정리.
