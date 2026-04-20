# Phase 24 Next Phase Preparation

## 목적

이 문서는 `Phase 24` 이후 어떤 질문으로 다음 phase를 여는 것이 자연스러운지 정리하기 위한 handoff 문서다.

현재는 Phase 24 practical closeout 단계의 handoff로 읽는다.

## 현재 handoff 상태

- 아직 Phase 24는 manual validation completed 상태가 아니다.
- 첫 신규 전략 `Global Relative Strength`는 core/runtime smoke와
  UI catalog, single strategy, compare, history, saved replay 연결까지 완료했다.
- 따라서 지금은 Phase 25로 넘어가기 전에 `PHASE24_TEST_CHECKLIST.md`로 사용자 QA를 먼저 진행하는 것이 맞다.

## 다음 phase에서 더 중요한 질문

1. 새 전략 확장 경로가 충분히 안정되었는가
2. 추가 전략을 더 붙일 것인가, 아니면 pre-live readiness로 넘어갈 것인가
3. quarterly real-money / guardrail parity를 Phase 25 전후에 열어야 하는가

## 추천 다음 방향

현재 roadmap 기준으로 Phase 24 이후 기본 방향은 `Phase 25 Pre-Live Operating System And Deployment Readiness`다.

다만 Phase 24에서 신규 전략 구현 경로가 충분히 검증되지 않으면,
Phase 25로 바로 넘어가기보다 Phase 24 안에서 한 번 더 implementation hardening을 진행한다.

현재 판단:

- `Global Relative Strength`는 제품 UI와 재진입 흐름까지 연결된 상태다.
- 다음 작업은 사용자가 single / compare / history / saved replay 체크리스트를 실제 화면에서 확인하는 것이다.
- 그 manual QA가 끝난 뒤에 Phase 25 진입 여부를 판단한다.

## Phase 25에서 헷갈리면 안 되는 경계

### Real-Money 검증 신호

- 위치:
  - `Backtest 결과 > Real-Money`
- 역할:
  - 개별 백테스트 실행에 대해 거래비용, benchmark, drawdown, 유동성, ETF 운용 가능성, promotion 상태를 보여준다.
- 한 줄로 말하면:
  - "이 백테스트 결과를 실전 후보로 보기 전에 어떤 위험 신호가 있는가"를 보여주는 진단표다.

### Pre-Live 운영 점검

- 위치:
  - Phase 25에서 만들 운영 checklist / paper-run 기록 / monitoring note
- 역할:
  - Real-Money 검증 신호를 보고 paper tracking, watchlist, 보류, 재검토, 데이터 재수집 같은 실제 운영 행동을 정리한다.
- 한 줄로 말하면:
  - "이 후보를 실제 돈 넣기 전에 어떻게 관찰하고 기록할 것인가"를 정하는 운영 절차다.

### 둘의 관계

- Real-Money는 `검증 신호`다.
- Pre-Live 운영 점검은 그 신호를 받아서 움직이는 `운영 절차`다.
- 둘은 연결되어 있지만 같은 기능으로 보지 않는다.
- Phase 25에서는 이 둘이 UI / 문서 / checklist에서 섞여 보이지 않게 분리해서 설명해야 한다.

## handoff 메모

- Phase 25는 live trading이 아니라 paper / review / pre-live readiness 운영 체계다.
- Phase 24 결과가 투자 추천으로 자동 변환되지 않게 유지한다.
- `Reference > Guides > 테스트에서 상용화 후보 검토까지 사용하는 흐름`도
  Real-Money 검증 신호와 Pre-Live 운영 점검을 별도 단계로 읽도록 업데이트했다.
