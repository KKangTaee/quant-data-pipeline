# Phase 30 Portfolio Proposal And Pre-Live Monitoring Surface Plan

## 이 문서는 무엇인가

이 문서는 Phase 30에서 후보 검토 결과를 포트폴리오 제안과
paper / pre-live monitoring surface로 연결하기 위한 계획 문서다.

다만 Phase 30은 곧바로 새 기능을 더 얹는 것으로 시작하지 않는다.
첫 작업은 Phase 29 이후 기준으로 사용 흐름을 다시 정렬하고,
너무 커진 `app/web/pages/backtest.py`를 어떤 제품 경계로 나눌지 검토하는 것이다.

## 목적

1. `테스트에서 상용화 후보 검토까지 사용하는 흐름`을 Phase 29 이후 기준으로 다시 정리한다.
2. Candidate Draft / Candidate Review Note / Current Candidate Registry / Pre-Live Review가 언제 필요한지 설명한다.
3. Phase 30 portfolio proposal 구현 전에 `backtest.py` 리팩토링 경계를 정한다.

## 쉽게 말하면

Phase 29까지 오면서 좋은 백테스트 결과를 후보로 읽고,
검토 메모를 남기고, 후보 registry에 명시적으로 남기는 길이 생겼다.

이제 바로 포트폴리오 제안 화면을 만들면 기능은 늘어나지만,
사용자가 "그래서 언제 무엇을 눌러야 하지?"를 놓칠 수 있다.

그래서 Phase 30의 첫 작업은 제품 사용 지도를 다시 그리고,
그 지도에 맞춰 큰 `backtest.py` 파일을 어떤 단위로 나눌지 정하는 것이다.

## 왜 필요한가

- `Backtest > Single Strategy`, `Compare`, `Candidate Review`, `History`, `Pre-Live Review`가 모두 연결되면서 사용 흐름이 길어졌다.
- 기존 Guide의 `테스트에서 상용화 후보 검토까지 사용하는 흐름`은 Phase 29의 Candidate Draft / Review Note / Registry Draft를 충분히 반영하지 못한다.
- `app/web/pages/backtest.py`는 16k lines 이상으로 커져 UI, state, persistence helper, chart, candidate workflow가 한 파일에 몰려 있다.
- 최종 목표는 실전 포트폴리오와 가이드를 제시하는 것이므로, 포트폴리오 제안 전에 후보의 의미와 저장 단계가 흔들리지 않아야 한다.

## 이 phase가 끝나면 좋은 점

- 사용자는 좋은 백테스트 결과를 보고 다음에 무엇을 해야 하는지 단계별로 이해할 수 있다.
- Candidate Review와 Pre-Live Review가 투자 승인처럼 보이지 않고, 포트폴리오 제안 전 검토 절차로 읽힌다.
- Phase 30 후속 구현은 큰 파일에 기능을 계속 붙이는 방식이 아니라, 제품 경계에 맞춰 점진적으로 분리할 수 있다.

## 이 phase에서 다루는 대상

- `Reference > Guides > 테스트에서 상용화 후보 검토까지 사용하는 흐름`
- `Backtest > Candidate Review`
- `Backtest > Compare & Portfolio Builder`
- `Backtest > Pre-Live Review`
- `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`
- `.note/finance/CANDIDATE_REVIEW_NOTES.jsonl`
- `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`
- `app/web/pages/backtest.py` 모듈 분리 경계
- `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md`

이번 phase에서 바로 다루지 않는 것:

- live trading 승인
- 브로커 연결
- 실제 주문 실행
- 최종 투자 판단 자동화
- 대규모 stop-the-world 리팩토링

## 현재 구현 우선순위

1. 사용 흐름 재정렬
   - 쉽게 말하면: 백테스트 실행부터 후보 검토, registry, compare, Pre-Live, portfolio proposal까지 한 흐름으로 다시 쓴다.
   - 왜 먼저 하는가: 사용자가 이해하지 못한 상태에서 기능을 더 만들면 다음 phase가 더 복잡해진다.
   - 기대 효과: Candidate Draft / Review Note / Registry Draft의 사용 시점이 분명해진다.
2. `backtest.py` 리팩토링 경계 검토
   - 쉽게 말하면: 큰 파일을 바로 쪼개기보다 어떤 제품 단위로 나눌지 먼저 정한다.
   - 왜 필요한가: Candidate Review, Pre-Live, History, Compare, Saved Portfolio가 모두 한 파일에 있어 변경 위험이 커졌다.
   - 기대 효과: Phase 30 구현 중에도 점진적으로 모듈을 분리할 수 있는 기준이 생긴다.
3. Portfolio Proposal 첫 계약 정의
   - 쉽게 말하면: 후보 여러 개를 어떤 목적과 비중, 위험 역할로 묶을지 저장 전 초안을 정한다.
   - 왜 필요한가: 단일 후보 검토만으로는 최종 목표인 포트폴리오 구성 제안까지 가지 못한다.
   - 기대 효과: 사용자가 포트폴리오 제안을 투자 승인과 구분해 읽을 수 있다.

## 이 문서에서 자주 쓰는 용어

- Candidate Draft
  - Latest Backtest Run 또는 History 결과를 후보처럼 읽어보는 저장 전 초안이다.
- Candidate Review Note
  - 후보 초안을 본 뒤 사람이 남기는 판단 기록이다.
- Current Candidate Registry
  - 후보로 남기기로 한 current anchor / near miss / scenario row의 저장소다.
- Pre-Live Review
  - 후보를 실제 돈 없이 관찰 / 보류 / 재검토 상태로 운영 기록하는 단계다.
- Portfolio Proposal
  - 후보 여러 개를 목적과 비중, 위험 역할로 묶은 제안 초안이다. 투자 승인이나 주문 지시가 아니다.

## 이번 phase의 운영 원칙

- 사용자가 이해할 수 있는 흐름을 먼저 고정한다.
- 포트폴리오 제안은 live approval이 아니다.
- 리팩토링은 제품 경계가 명확한 단위부터 점진적으로 진행한다.
- 큰 파일을 줄이는 것이 목표가 아니라, 변경 이유와 소유 경계를 분명하게 만드는 것이 목표다.
- Candidate Review / Pre-Live / Portfolio Proposal의 저장소 역할을 섞지 않는다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업: 사용 흐름 재정렬과 리팩토링 경계 검토

- 무엇을 바꾸는가:
  - Guide의 `테스트에서 상용화 후보 검토까지 사용하는 흐름`을 Phase 29 이후 기준으로 갱신한다.
  - `WEB_BACKTEST_UI_FLOW.md`에 `backtest.py` 분리 후보와 순서를 남긴다.
  - Phase 30 첫 작업 단위 문서를 만든다.

- 왜 필요한가:
  - Phase 29 기능은 안전장치가 많지만, 사용자가 언제 써야 하는지 흐려질 수 있다.
  - Phase 30 기능을 더 붙이기 전에 제품 흐름과 코드 경계를 맞춰야 한다.

- 작업이 끝나면 좋은 점:
  - 다음 구현자는 어떤 흐름을 보존해야 하는지 알고 작업할 수 있다.
  - 사용자는 Candidate Review 기능을 별도 기능 묶음이 아니라 상용화 후보 검토 흐름 안에서 이해할 수 있다.

### 두 번째 작업: Portfolio Proposal 초안 계약

- 무엇을 바꾸는가:
  - 포트폴리오 제안 row가 어떤 후보들을 포함하고, 어떤 목적 / 비중 / 위험 역할 / 데이터 신뢰성 요약을 가져야 하는지 정한다.

- 왜 필요한가:
  - 후보 여러 개를 묶는 순간 단일 전략 후보보다 해석 책임이 커진다.

- 작업이 끝나면 좋은 점:
  - 포트폴리오 제안 UI와 저장소를 만들기 전, 무엇을 저장해야 하는지 흔들리지 않는다.

### 세 번째 작업: Proposal review / monitoring surface

- 무엇을 바꾸는가:
  - 후보 묶음의 Real-Money / Data Trust / Pre-Live 상태를 한 화면에서 읽게 한다.

- 왜 필요한가:
  - 포트폴리오 제안은 성과 숫자만으로 판단할 수 없다.

- 작업이 끝나면 좋은 점:
  - 사용자는 포트폴리오 제안을 paper tracking 또는 재검토 대상으로 볼 수 있다.

## 다음에 확인할 것

- Guide를 읽었을 때 Candidate Draft / Review Note / Registry Draft의 필요성이 이해되는지
- `backtest.py` 리팩토링 경계가 너무 세밀하거나 너무 넓지 않은지
- Portfolio Proposal을 투자 승인처럼 보이게 하는 용어나 버튼이 없는지
- Phase 30 이후 Live Readiness / Final Approval을 별도 phase로 남겨둘지

## 한 줄 정리

Phase 30은 후보 검토 결과를 포트폴리오 제안과 pre-live monitoring으로 연결하는 phase이며,
첫 작업은 기능 추가 전에 사용 흐름과 코드 경계를 다시 정렬하는 것이다.
