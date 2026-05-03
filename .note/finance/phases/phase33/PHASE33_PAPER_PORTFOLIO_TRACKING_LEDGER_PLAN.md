# Phase 33 Paper Portfolio Tracking Ledger Plan

## 이 문서는 무엇인가

Phase 33에서 만들 `Paper Portfolio Tracking Ledger`의 목적, 범위, 작업 단위를 정리하는 계획 문서다.

## 목적

- Phase 32에서 `READY_FOR_PAPER_LEDGER_PREP` 또는 보강 후 추적 가능하다고 판단한 후보 / Portfolio Proposal을 paper tracking record로 남긴다.
- 시작일, target weight, tracking benchmark, review cadence, 재검토 기준을 가진 append-only ledger를 만든다.
- Phase 34 final selection decision pack이 읽을 수 있는 paper evidence를 쌓기 시작한다.

## 쉽게 말하면

Phase 32가 "이 후보를 다시 흔들어볼 준비가 되었나"를 봤다면,
Phase 33은 "실제 돈을 넣기 전에 이 후보를 어떤 조건으로 관찰할 것인가"를 장부로 남기는 단계다.

이 단계도 live approval이나 주문 지시가 아니다.
실전 투자 전 관찰 기록을 만들고, 나중에 최종 선정 판단에 쓸 근거를 쌓는 단계다.

## 왜 필요한가

- 백테스트 snapshot만으로 최종 실전 포트폴리오를 고르면 최근 시장 변화나 운용 중 악화 신호를 놓칠 수 있다.
- Phase 30의 `Paper Tracking Feedback`은 proposal snapshot과 최신 Pre-Live snapshot 비교에 가깝고, 시작일 / 비중 / review cadence를 가진 paper portfolio ledger는 아직 없다.
- Phase 34에서 최종 선정 / 보류 / 거절을 하려면 "얼마 동안 어떤 조건으로 paper tracking했는가"가 남아 있어야 한다.

## 이 phase가 끝나면 좋은 점

- 사용자는 후보나 proposal을 실제 돈 없이 추적할 paper record로 저장할 수 있다.
- paper tracking record는 source id, 시작일, target weights, benchmark, review cadence, stop / re-review trigger를 함께 남긴다.
- Phase 34는 백테스트 결과만이 아니라 paper tracking 기록까지 읽어 최종 후보 판단을 할 수 있다.

## 이 phase에서 다루는 대상

- `Backtest > Portfolio Proposal`의 단일 후보 / 작성 중 proposal / 저장 proposal Validation Pack
- Phase 32 `phase33_handoff` 결과
- current candidate registry row
- Portfolio Proposal registry row
- 새 append-only paper ledger 저장소
  - 예상 위치: `.note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`

## 현재 구현 우선순위

1. Paper tracking ledger row 계약 정의
   - 쉽게 말하면: paper tracking 장부 한 줄에 무엇을 저장할지 먼저 정한다.
   - 왜 먼저 하는가: 저장 계약이 흔들리면 UI와 Phase 34 handoff가 모두 흔들린다.
   - 기대 효과: 후보 / proposal을 같은 언어로 paper tracking record로 남길 수 있다.
2. Ledger 저장 helper와 UI draft / save surface
   - 쉽게 말하면: Phase 32 handoff를 읽어 paper ledger draft를 만들고, 사용자가 명시적으로 저장한다.
   - 왜 필요한가: Validation Pack을 여는 것만으로 자동 저장되면 안 되고, 사용자가 기록 의사를 확인해야 한다.
   - 기대 효과: 저장 버튼과 저장 결과가 분명한 paper tracking workflow가 생긴다.
3. Ledger review / status surface
   - 쉽게 말하면: 저장된 paper tracking record를 다시 열어 현재 상태와 다음 행동을 본다.
   - 왜 필요한가: paper tracking은 저장으로 끝나는 것이 아니라 관찰 / 보류 / 재검토 상태를 계속 읽어야 한다.
   - 기대 효과: Phase 34 final selection으로 넘길 수 있는 record를 분리해서 볼 수 있다.
4. Phase 34 handoff 정리
   - 쉽게 말하면: paper tracking record가 최종 선정 판단으로 넘어갈 만큼 충분한지 요약한다.
   - 왜 필요한가: Phase 34는 최종 선정 / 보류 / 거절 decision pack이므로, 입력 기준이 필요하다.
   - 기대 효과: 최종 실전 후보 포트폴리오 선정 전 단계가 더 선명해진다.

## 이 문서에서 자주 쓰는 용어

- `Paper Portfolio Tracking Ledger`: 실제 돈을 넣기 전에 후보나 proposal을 일정 조건으로 관찰하는 append-only 장부다.
- `Tracking Start Date`: paper tracking을 시작한 기준일이다.
- `Review Cadence`: 매주 / 매월 / 리밸런싱 주기처럼 얼마마다 다시 볼지 정한 규칙이다.
- `Stop / Re-Review Trigger`: CAGR 악화, MDD 확대, benchmark 이탈처럼 재검토를 걸 조건이다.
- `Phase 34 Handoff`: 최종 선정 decision pack으로 넘길 준비 상태 요약이다.

## 이번 phase의 운영 원칙

- live approval, 주문 지시, 최종 투자 추천은 만들지 않는다.
- paper ledger 저장은 사용자의 명시적 저장 버튼으로만 수행한다.
- current candidate registry, Pre-Live registry, Portfolio Proposal registry를 덮어쓰지 않는다.
- 새 paper ledger는 append-only로 관리한다.
- Phase 32의 handoff를 입력으로 쓰되, Phase 32 결과를 자동 승인으로 해석하지 않는다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업. Paper ledger row 계약과 저장소 경계 정의

- paper ledger row에 필요한 필드를 정한다.
- source가 단일 후보인지, 저장 proposal인지, 작성 중 proposal인지 구분한다.
- Phase 32 handoff snapshot과 tracking rules를 row에 포함한다.

### 두 번째 작업. Paper ledger draft / save UI 추가

- `Backtest > Portfolio Proposal` Validation Pack에서 paper ledger draft를 확인한다.
- 사용자가 명시적으로 `Save Paper Tracking Ledger`를 눌러야 저장한다.
- 저장 후 성공 메시지와 중복 id 방지 UX를 제공한다.

### 세 번째 작업. 저장된 paper ledger review surface 추가

- 저장된 paper tracking record 목록을 보고 상세를 확인한다.
- active / watch / paused / re-review 같은 상태를 읽는다.
- 아직 실제 paper PnL 시계열이 없어도 시작 조건과 tracking rule이 명확히 보이게 한다.

### 네 번째 작업. Phase 34 final selection handoff 정리

- paper ledger record가 최종 선정 후보로 충분한지, 더 관찰해야 하는지, 차단해야 하는지 route로 정리한다.
- Phase 34가 읽을 최소 입력을 next phase preparation에 남긴다.

## 다음에 확인할 것

- `PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` 저장소 이름과 row schema가 적절한지 확인한다.
- 단일 후보와 proposal의 ledger row가 같은 UI에서 자연스럽게 읽히는지 확인한다.
- 저장된 paper ledger가 proposal registry나 Pre-Live registry와 섞이지 않는지 확인한다.

## 한 줄 정리

Phase 33은 최종 실전 포트폴리오 선정 전, 후보나 proposal을 실제 돈 없이 관찰할 paper tracking 장부를 만드는 단계다.
