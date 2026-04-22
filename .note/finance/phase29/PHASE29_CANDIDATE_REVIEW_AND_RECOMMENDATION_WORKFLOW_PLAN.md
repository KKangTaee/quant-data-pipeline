# Phase 29 Candidate Review And Recommendation Workflow Plan

## 이 문서는 무엇인가

이 문서는 Phase 29에서 백테스트 결과와 current candidate registry를
어떻게 "후보 검토 workflow"로 연결할지 정리하는 계획 문서다.

Phase 29는 최종 투자 승인이나 live trading을 여는 phase가 아니다.
좋아 보이는 결과를 바로 추천으로 확정하지 않고,
후보로 읽고, 비교하고, Pre-Live 검토로 넘기는 절차를 정리하는 phase다.

## 목적

1. current candidate / near miss / scenario 후보를 사용자가 한 화면에서 읽게 만든다.
2. 후보를 compare 또는 Pre-Live Review로 넘기기 전에 그 후보가 왜 존재하는지 설명한다.
3. 향후 "새 백테스트 결과 -> 후보 검토 기록" 흐름을 표준화할 기반을 만든다.

## 쉽게 말하면

Phase 29는 "좋은 백테스트 결과를 봤다. 그래서 이걸 후보로 남길지, 비교할지,
Pre-Live 관찰로 넘길지"를 정리하는 단계다.

지금까지는 후보 문서, registry, compare, Pre-Live가 각각 따로 존재했다.
이번 phase에서는 그 사이를 이어서 사용자가 다음 행동을 덜 헷갈리게 만든다.

## 왜 필요한가

- Phase 20에서 current candidate를 compare로 다시 불러오는 길을 만들었다.
- Phase 25에서 current candidate를 Pre-Live 운영 기록으로 넘기는 길을 만들었다.
- Phase 27~28에서 데이터 신뢰성과 전략 family별 기능 범위를 화면에 보이게 했다.
- 이제 필요한 것은 후보를 "성과표"가 아니라 "검토 대상"으로 읽는 중간 화면이다.

## 이 phase가 끝나면 좋은 점

- 후보가 왜 current anchor인지, 왜 near miss인지, 왜 scenario인지 먼저 볼 수 있다.
- 후보를 compare로 보낼지 Pre-Live Review로 보낼지 다음 행동이 분명해진다.
- 새 후보를 등록하거나 기존 후보를 재검토할 때 문서와 UI 흐름이 덜 끊긴다.

## 이 phase에서 다루는 대상

- `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`
- `Backtest > Candidate Review`
- `Backtest > Compare & Portfolio Builder`의 current candidate re-entry
- `Backtest > Pre-Live Review`의 current candidate 운영 기록
- candidate review 관련 phase 문서와 guide

이번 phase에서 직접 다루지 않는 것:

- live trading 승인
- 실제 주문 / 브로커 연결
- 최종 투자 판단
- 새 전략 성과 탐색 자체

## 현재 구현 우선순위

1. Candidate Review Board 첫 구현
   - 쉽게 말하면: current candidate registry를 후보 검토 보드로 보여준다.
   - 왜 먼저 하는가: 후보를 compare나 Pre-Live로 넘기기 전에 "이 후보가 무엇인지"를 먼저 읽어야 한다.
   - 기대 효과: 후보 역할과 다음 행동 제안이 한 화면에서 보인다.
2. Latest / History result to candidate handoff
   - 쉽게 말하면: 새 백테스트 결과를 후보 검토 초안으로 넘기는 길을 만든다.
   - 왜 필요한가: 앞으로 사용자가 특정 백테스트 결과를 후보로 남기고 싶을 때 수동 문서 작성에만 의존하면 흐름이 끊긴다.
   - 기대 효과: 후보 등록 / 보류 / near-miss 기록이 반복 가능해진다.
3. Candidate review report / registry guide 정리
   - 쉽게 말하면: 후보 기록을 어떤 기준으로 남기는지 문서화한다.
   - 왜 필요한가: current candidate, near miss, scenario, Pre-Live record가 섞이면 사용자가 투자 추천처럼 오해할 수 있다.
   - 기대 효과: 후보 검토와 운영 기록의 경계가 유지된다.

## 이 문서에서 자주 쓰는 용어

- Candidate Review
  - 후보를 투자 승인으로 확정하기 전, 왜 후보인지와 다음 행동을 검토하는 단계다.
- Current Candidate
  - 지금 family의 기준 후보로 쓰는 registry row다.
- Near Miss
  - 일부 기준은 약하지만 방어성이나 다른 장점 때문에 다시 볼 가치가 있는 후보이다.
- Scenario
  - 주 후보를 바로 대체하기보다 설정 차이를 비교하기 위한 대안 후보이다.
- Suggested Next Step
  - 투자 추천이 아니라 다음 검토 행동 제안이다.

## 이번 phase의 운영 원칙

- 후보 검토는 투자 추천이 아니다.
- Pre-Live Review는 live trading 승인이 아니다.
- 좋은 CAGR만으로 후보를 승격하지 않는다.
- 후보를 볼 때는 data trust, Real-Money signal, strategy family capability를 함께 읽는다.
- 새 기능은 먼저 "사용자가 이해할 수 있는 흐름"을 만든 뒤 자동화한다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업: Candidate Review Board

- 무엇을 바꾸는가:
  - `Backtest`에 `Candidate Review` 패널을 추가한다.
  - current candidate registry의 active 후보를 검토 보드로 보여준다.
  - 후보별 review stage, 존재 이유, 다음 행동 제안을 보여준다.
  - 선택한 후보를 Pre-Live Review로 넘기는 버튼을 추가한다.
  - 기존 compare re-entry를 Candidate Review에서도 사용할 수 있게 한다.

- 왜 필요한가:
  - 기존에는 후보가 registry와 compare 보조 도구, Pre-Live 화면에 흩어져 있었다.
  - 사용자는 먼저 "이 후보가 왜 있는지"를 보고 다음 행동을 정해야 한다.

- 작업이 끝나면 좋은 점:
  - 후보 검토가 compare / Pre-Live 사이의 중간 workflow로 보인다.

### 두 번째 작업: 후보 등록 / 재검토 handoff

- 무엇을 바꾸는가:
  - Latest Backtest Run 또는 History 결과를 candidate review 초안으로 넘기는 흐름을 검토한다.

- 왜 필요한가:
  - 사용자가 좋은 결과를 발견했을 때 후보 기록으로 남기는 방식이 필요하다.

- 작업이 끝나면 좋은 점:
  - 새 후보와 near-miss 후보를 반복 가능한 방식으로 관리할 수 있다.

### 세 번째 작업: 후보 검토 문서 / guide 정리

- 무엇을 바꾸는가:
  - current candidate registry guide와 glossary를 Phase 29 기준으로 보강한다.

- 왜 필요한가:
  - 후보 검토, Pre-Live 운영 기록, 최종 투자 승인 경계를 계속 분리해야 한다.

- 작업이 끝나면 좋은 점:
  - 다음 phase에서 포트폴리오 제안 workflow로 넘어갈 때 후보 의미가 흔들리지 않는다.

## 다음에 확인할 것

- Candidate Review Board가 사용자가 읽기에 과하게 분석 화면처럼 보이지 않는지
- `Suggested Next Step`이 투자 추천이 아니라 다음 검토 행동으로 읽히는지
- Candidate Review에서 Pre-Live Review로 넘어갈 때 "저장 전 초안"이라는 점이 분명한지
- Compare로 보내는 흐름이 기존 current candidate re-entry와 충돌하지 않는지

## 한 줄 정리

Phase 29는 백테스트 후보를 바로 투자 추천으로 확정하지 않고,
검토 보드에서 읽고 compare / Pre-Live로 넘기는 workflow를 만드는 phase다.
