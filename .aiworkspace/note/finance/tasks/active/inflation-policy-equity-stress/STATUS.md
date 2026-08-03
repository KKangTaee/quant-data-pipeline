# Inflation Policy Equity Stress Status

State: complete
Roadmap: 5/5 implementation checkpoints complete
Last Updated: 2026-08-03

## Current

- 전체 phase의 4/5차 조건부 S&P 500 스트레스 구현과 actual Browser QA를 완료했다.
- 승인된 equity-stress 구현 계획을 실제 평면 module 구조와 독립 `equity_json` 저장
  계약에 맞게 반영했다.
- actual `sp500_index_earnings`는 0건이므로 실제 확률은 official workbook vintage가
  등록될 때까지 공개하지 않는다.
- DB-only equity bundle과 PIT year-end EPS×multiple panel을 구현했다.
- EPS·multiple response와 paired residual을 label 공개시각 기준 rolling-origin으로
  검증한다. constant EPS·constant multiple·unconditional index change 세 baseline과
  80% interval coverage gate를 넘지 못하면 `LIMITED`, 표본 부족은 `NOT_AVAILABLE`로 닫았다.
- 사용자 AI EPS uplift와 임의 지수 수준 역산을 bounded scenario로 추가했다.
- `EquityStressResult`를 독립 snapshot field, 서비스 read model, command와 React panel에
  연결했고 equity 실패가 물가·정책·금리 상태를 바꾸지 않는 회귀 테스트를 고정했다.
- production materialization은 official EPS bundle→PIT panel→versioned artifact→독립
  `READY` 공동경로→equity simulation을 실제로 호출하며, 어느 gate든 불충족이면
  equity section만 fail-closed한다.
- 공동경로는 core artifact와 충돌하지 않는 `joint_macro_paths` component를 사용한다.
  model artifact에는 불변 계수·잔차·검증만, 현재 지수·EPS·금리 시작점은 snapshot별
  `equity_json`에 저장해 같은 training cutoff의 과거 replay도 재현 가능하게 했다.
- measured EPS revision, 시작금리 4종, months-to-year-end와 공동경로 endpoint 4종 중
  하나라도 없으면 0으로 보정하지 않고 `scenario_context_incomplete`로 닫는다.
- actual DB snapshot `2026-08-03T00:00:00`은 macro `LIMITED`, equity
  `NOT_AVAILABLE`이다. 공식 EPS 빈티지와 검증된 공동 거시경로가 없으므로 실제 확률은
  표시하지 않는다.
- desktop과 390px Browser QA에서 hard gate, 인과효과 아님 disclosure, 5차 침체
  미연결 경계와 responsive 단일 열을 확인했다. desktop `994=994`, mobile
  `313=313` client/scroll width로 가로 overflow가 없다.

## Handoff

- 전체 phase는 4/5차 완료 상태로 유지한다.
- 다음은 기존 경제 사이클 확률을 재사용하지 않는 5차 독립 침체 위험 모델이다.
