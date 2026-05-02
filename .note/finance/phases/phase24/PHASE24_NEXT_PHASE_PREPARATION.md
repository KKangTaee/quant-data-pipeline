# Phase 24 Next Phase Preparation

## 목적

이 문서는 `Phase 24` 이후 어떤 질문으로 다음 phase를 여는 것이 자연스러운지 정리하기 위한 handoff 문서다.

현재는 Phase 24 closeout 이후 Phase 25 kickoff handoff로 읽는다.

## 현재 handoff 상태

- Phase 24는 `phase complete / manual_validation_completed` 상태로 닫혔다.
- 첫 신규 전략 `Global Relative Strength`는 core/runtime smoke와
  UI catalog, single strategy, compare, history, saved replay 연결까지 완료했다.
- 사용자 QA 중 확인된 데이터 품질 이슈는 결과를 억지로 늘리지 않고
  `excluded_tickers`, `malformed_price_rows`, 한국어 주의사항으로 드러내는 방향으로 정리했다.
- 따라서 다음 기본 방향은 Phase 25 `Pre-Live Operating System And Deployment Readiness`다.

## 다음 phase에서 더 중요한 질문

1. Real-Money 검증 신호를 보고 operator가 어떤 다음 행동을 선택해야 하는가
2. paper tracking / watchlist / hold / re-review 기록을 어디에 어떻게 남길 것인가
3. live trading이 아니라 pre-live readiness라는 경계를 UI와 문서에서 어떻게 유지할 것인가

## 추천 다음 방향

Phase 25는 `Real-Money` 탭을 하나 더 만드는 phase가 아니다.
이미 백테스트 결과에 붙는 Real-Money 신호를 보고,
그 다음 운영 행동을 정리하는 paper / watchlist / review 체계를 만든다.

현재 판단:

- Phase 24 신규 전략 구현 경로는 manual QA까지 통과했다.
- Phase 25는 live trading이 아니라 pre-live 운영 점검을 문서와 UI 흐름으로 분리해 잡는다.
- 이후 실제 투자 분석이나 후보 평가가 필요하면 사용자가 명시적으로 요청했을 때 별도 분석으로 수행한다.

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
- Phase 25 plan / checklist에서도 같은 경계를 계속 유지한다.
