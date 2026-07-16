# Overview Market Context U.S. Economic Cycle V1 Design Record

Status: Approved
Last Updated: 2026-07-16

## Approved Product Contract

- 공개 국면은 `회복 / 확장 / 둔화 / 침체`다.
- 현재·1개월 후·2개월 후마다 네 국면 확률 전체를 보여준다.
- UI는 확률 header, cycle clock, evidence, 10년 regime ribbon으로 구성한다.
- 위치는 `Workspace > Overview > 시장 맥락`이며 selector는 `경제 사이클 | S&P 500 | 미국 개별주식`다.
- 현재 국면은 실물·고용이 결정한다. 금리·신용·인플레이션·정책은 예측과 보조 근거 역할이다.
- rolling-origin 검증을 통과하지 못한 horizon에는 숫자 확률을 공개하지 않는다.

## Architecture Decisions

1. 기존 `macro_series_observation`은 revised-latest 소비자를 위해 유지한다.
2. `macro_series_vintage_observation`은 모든 real-time revision interval을 보존한다.
3. `economic_cycle_model_artifact`는 model version, training cutoff, calibration, validation, publication status를 보존한다.
4. `economic_cycle_snapshot`은 current/historical replay의 compact probability/evidence payload를 저장한다.
5. label은 activity/labor와 `USREC`만 사용한다.
6. h0 model은 real-economy features만 사용하며 h1/h2는 financial-leading/inflation-policy context를 추가할 수 있다.
7. UI는 snapshot/history DB read만 수행하며 provider fetch, training, materialization, registry write를 하지 않는다.
8. 경제 사이클 React component는 기존 valuation React component와 분리한다.

## Authoritative Detail

전체 rationale, data roles, statistical semantics, visualization, limitations는 [`docs/superpowers/specs/2026-07-16-us-economic-cycle-regime-forecast-design.md`](../../../../../../docs/superpowers/specs/2026-07-16-us-economic-cycle-regime-forecast-design.md)를 따른다. 구현 중 설계 변경이 필요하면 코드보다 명세와 사용자 재승인이 먼저다.
