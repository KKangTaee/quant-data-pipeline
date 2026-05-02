# Phase 30 Portfolio Proposal And Pre-Live Monitoring Surface Plan

## 이 문서는 무엇인가

이 문서는 Phase 30에서 후보 검토 결과를 포트폴리오 제안과
paper / pre-live monitoring surface로 연결하기 위한 계획 문서다.

다만 Phase 30은 곧바로 새 기능을 더 얹는 것으로 시작하지 않는다.
첫 작업은 Phase 29 이후 기준으로 사용 흐름을 다시 정렬하고,
너무 커진 `app/web/pages/backtest.py`를 어떤 제품 경계로 나눌지 검토하는 것이다.

주의:

- `사용 흐름 재정렬 + backtest.py 리팩토링 경계 검토`는 Phase 30 전체가 아니라 첫 번째 작업 단위다.
- Phase 30 전체 목표는 후보 묶음을 Portfolio Proposal / Pre-Live Monitoring으로 연결하는 것이다.
- 두 번째 작업인 Portfolio Proposal 계약 정의는 첫 번째 작업 이후, UI 구현 전에 진행하는 설계 단계다.
- 네 번째 작업에서 `Backtest > Portfolio Proposal` draft 작성 / 저장 / registry inspect 흐름을 추가했다.
- 다섯 번째 작업에서 저장된 proposal draft를 다시 읽는 `Monitoring Review` surface를 추가했다.
- 여섯 번째 작업에서 저장된 proposal snapshot과 현재 Pre-Live registry 상태를 비교하는 `Pre-Live Feedback` surface를 추가했다.
- 일곱 번째 작업에서 proposal evidence snapshot과 현재 Pre-Live result snapshot을 비교하는 `Paper Tracking Feedback` surface를 추가했다.

## 목적

1. `테스트에서 상용화 후보 검토까지 사용하는 흐름`을 Phase 29 이후 기준으로 다시 정리한다.
2. Candidate Draft / Candidate Review Note / Current Candidate Registry / Pre-Live Review가 언제 필요한지 설명한다.
3. Phase 30 portfolio proposal 구현 전에 `backtest.py` 리팩토링 경계를 정한다.
4. Portfolio Proposal row가 담아야 할 목적, 후보 역할, 비중 근거, 위험 경계, evidence snapshot, blocker, operator decision을 먼저 정의한다.
5. Portfolio Proposal 계약을 실제 Backtest UI와 append-only registry persistence로 연결한다.
6. 저장된 Portfolio Proposal draft를 blocker / review gap / 후보 구성 관점으로 다시 읽는다.
7. Portfolio Proposal draft와 최신 Pre-Live 운영 상태를 비교한다.
8. Portfolio Proposal draft와 최신 Pre-Live result snapshot의 paper tracking 성과 피드백을 비교한다.

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
- `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`
- `app/web/pages/backtest.py` 모듈 분리 경계
- `app/web/runtime/candidate_registry.py` registry JSONL I/O helper
- `app/web/runtime/portfolio_proposal.py` proposal JSONL I/O helper
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
   - 현재 상태: 두 번째 작업 단위에서 proposal row의 최소 필드, 후보 역할, 비중 원칙, 저장 전 차단 조건, lifecycle을 정의했다.
4. Portfolio Proposal Draft UI / persistence
   - 쉽게 말하면: current candidate 여러 개를 선택해 proposal objective, 후보별 역할, target weight, 다음 행동을 저장하는 첫 화면을 만든다.
   - 왜 필요한가: 계약만 있으면 사용자가 실제 workflow에서 proposal을 만들 수 없으므로, 저장 전 초안과 registry inspect surface가 필요하다.
   - 기대 효과: 후보 검토 흐름이 단일 후보 registry에서 포트폴리오 제안 초안까지 이어진다.
   - 현재 상태: 네 번째 작업 단위에서 `Backtest > Portfolio Proposal` panel, append-only proposal helper, proposal registry inspect tab을 추가했다.
5. Portfolio Proposal Monitoring Review
   - 쉽게 말하면: 저장한 proposal draft를 다시 열어 어떤 blocker와 review gap이 남았는지 확인한다.
   - 왜 필요한가: proposal은 저장에서 끝나는 것이 아니라, paper / pre-live monitoring과 live readiness 전 검토로 이어져야 한다.
   - 기대 효과: 사용자는 proposal draft가 단순 저장물인지, 추가 확인이 필요한 검토 대상인지 한눈에 볼 수 있다.
   - 현재 상태: 다섯 번째 작업 단위에서 `Monitoring Review` tab, monitoring summary, component table, blocker / review gap readout을 추가했다.
6. Portfolio Proposal Pre-Live Feedback
   - 쉽게 말하면: proposal 저장 당시 Pre-Live 상태와 현재 Pre-Live registry 상태가 달라졌는지 확인한다.
   - 왜 필요한가: proposal을 저장한 뒤에도 paper / pre-live 운영 상태는 바뀔 수 있다.
   - 기대 효과: proposal이 현재 관찰 상태와 어긋난 채로 다음 단계로 넘어가는 위험을 줄인다.
   - 현재 상태: 여섯 번째 작업 단위에서 `Pre-Live Feedback` tab, status drift, review overdue, feedback gap readout을 추가했다.
7. Portfolio Proposal Paper Tracking Feedback
   - 쉽게 말하면: proposal 저장 당시 CAGR / MDD와 현재 Pre-Live result snapshot의 CAGR / MDD를 비교한다.
   - 왜 필요한가: paper tracking 상태의 후보가 저장 당시보다 성과가 악화됐는지 proposal 관점에서 다시 읽어야 한다.
   - 기대 효과: live readiness 전 단계에서 missing result, paper tracking 미진입, CAGR / MDD 악화를 놓칠 가능성을 줄인다.
   - 현재 상태: 일곱 번째 작업 단위에서 `Paper Tracking Feedback` tab, performance signal, tracking plan, feedback gap readout을 추가했다.

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

- 현재 결과:
  - `.note/finance/phases/phase30/PHASE30_PORTFOLIO_PROPOSAL_CONTRACT_SECOND_WORK_UNIT.md`에서 계약을 정의했다.
  - 두 번째 작업 당시에는 파일 생성이나 append helper 구현은 하지 않았다.
  - 후속 네 번째 작업에서 `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` append-only 저장소와 UI가 구현되었다.

### 세 번째 작업: Registry I/O helper 분리

- 무엇을 바꾸는가:
  - `backtest.py` 안의 current candidate / review note / pre-live registry read / append helper를 runtime module로 분리한다.

- 왜 필요한가:
  - Portfolio Proposal 구현 때 같은 registry helper pattern을 재사용하기 쉽다.
  - UI rendering과 persistence helper의 책임을 조금이라도 분리해 `backtest.py` 증가를 늦춘다.

- 작업이 끝나면 좋은 점:
  - Candidate Review / Pre-Live UI는 그대로 두면서, 저장소 I/O 경계가 먼저 생긴다.

- 현재 결과:
  - `app/web/runtime/candidate_registry.py`가 추가되었다.
  - 이번 작업은 전체 `backtest.py` 리팩토링이 아니라 registry JSONL I/O 첫 분리다.

### 네 번째 작업: Portfolio Proposal Draft UI / persistence

- 무엇을 바꾸는가:
  - `Backtest > Portfolio Proposal`에서 current candidate 여러 개를 선택하고,
    proposal 목적, 후보별 역할, target weight, weight reason, operator decision을 작성한다.
  - 저장된 proposal draft는 `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`에 append-only로 남긴다.
  - `Proposal Registry` tab에서 저장된 proposal row를 다시 확인한다.

- 왜 필요한가:
  - Phase 29의 후보 검토 흐름을 포트폴리오 제안 초안으로 실제 연결해야 한다.
  - 단일 candidate 저장소만으로는 최종 목표인 portfolio construction guide까지 이어지기 어렵다.

- 작업이 끝나면 좋은 점:
  - 사용자는 current candidate 여러 개를 목적 / 역할 / 비중 근거와 함께 하나의 proposal draft로 저장할 수 있다.
  - proposal draft가 live approval과 분리된 기록이라는 점이 화면과 저장소에서 명확해진다.

- 현재 결과:
  - `app/web/runtime/portfolio_proposal.py`가 추가되었다.
  - `Backtest > Portfolio Proposal` panel에 `Create Proposal Draft`와 `Proposal Registry` tab이 추가되었다.

### 다섯 번째 작업: Portfolio Proposal Monitoring Review

- 무엇을 바꾸는가:
  - 저장된 proposal draft의 Real-Money / Data Trust / Pre-Live 상태, blocker, review gap, operator decision을 한 화면에서 읽게 한다.

- 왜 필요한가:
  - 포트폴리오 제안은 성과 숫자만으로 판단할 수 없다.

- 작업이 끝나면 좋은 점:
  - 사용자는 포트폴리오 제안을 paper tracking 또는 재검토 대상으로 볼 수 있다.

- 현재 결과:
  - `Backtest > Portfolio Proposal > Monitoring Review` tab이 추가되었다.
  - monitoring state는 `blocked`, `needs_review`, `review_ready`로 요약하지만 live approval은 아니다.

### 여섯 번째 작업: Portfolio Proposal Pre-Live Feedback

- 무엇을 바꾸는가:
  - 저장된 proposal draft의 component 후보를 현재 Pre-Live registry active record와 비교한다.
  - saved pre-live snapshot, current pre-live status, status drift, review overdue, tracking cadence, next action을 보여준다.

- 왜 필요한가:
  - proposal draft는 저장 당시의 snapshot이므로, 이후 Pre-Live 상태 변화가 반영되지 않을 수 있다.
  - paper / pre-live 운영 상태가 바뀌면 proposal 해석도 다시 확인해야 한다.

- 작업이 끝나면 좋은 점:
  - 사용자는 proposal을 live readiness 후보로 착각하기 전에 현재 Pre-Live feedback gap을 확인할 수 있다.

- 현재 결과:
  - `Backtest > Portfolio Proposal > Pre-Live Feedback` tab이 추가되었다.
  - 이 tab은 읽기 전용이며 proposal row나 Pre-Live registry를 자동 수정하지 않는다.

### 일곱 번째 작업: Portfolio Proposal Paper Tracking Feedback

- 무엇을 바꾸는가:
  - 저장된 proposal draft의 `evidence_snapshot`과 현재 Pre-Live record의 `result_snapshot`을 비교한다.
  - component별 saved/current CAGR, saved/current MDD, delta, performance signal, tracking cadence, stop/success condition을 보여준다.

- 왜 필요한가:
  - proposal과 Pre-Live 상태가 연결되어도, paper tracking 성과가 악화됐는지 보이지 않으면 live readiness 전 검토가 부족하다.
  - 현재는 별도 paper PnL 시계열 저장소가 없으므로, Pre-Live record에 저장된 최신 result snapshot을 읽는 보수적 surface가 필요하다.

- 작업이 끝나면 좋은 점:
  - 사용자는 proposal component가 paper tracking 상태인지, 최신 result snapshot 기준으로 CAGR / MDD가 악화됐는지 확인할 수 있다.
  - Phase 30의 Portfolio Proposal / Pre-Live Monitoring 제품 기능 단위가 manual QA로 넘어갈 수 있다.

- 현재 결과:
  - `Backtest > Portfolio Proposal > Paper Tracking Feedback` tab이 추가되었다.
  - 이 tab은 실제 paper PnL 자동 계산, proposal 자동 수정, live approval을 만들지 않는다.

## 다음에 확인할 것

- Guide를 읽었을 때 Candidate Draft / Review Note / Registry Draft의 필요성이 이해되는지
- `backtest.py` 리팩토링 경계가 너무 세밀하거나 너무 넓지 않은지
- Portfolio Proposal을 투자 승인처럼 보이게 하는 용어나 버튼이 없는지
- Phase 30 이후 Live Readiness / Final Approval을 별도 phase로 남겨둘지
- `Backtest > Portfolio Proposal`에서 proposal draft 저장과 registry inspect 흐름이 자연스러운지
- `Monitoring Review`에서 저장된 proposal의 blocker / review gap / 후보 구성이 한눈에 읽히는지
- `Pre-Live Feedback`에서 proposal 저장 당시 snapshot과 현재 Pre-Live 상태 차이가 읽히는지
- `Paper Tracking Feedback`에서 proposal 저장 당시 성과와 최신 Pre-Live result snapshot의 CAGR / MDD 차이가 읽히는지
- proposal draft가 saved portfolio 또는 live approval로 오해되지 않는지

## 한 줄 정리

Phase 30은 후보 검토 결과를 포트폴리오 제안과 pre-live monitoring으로 연결하는 phase이며,
첫 작업은 기능 추가 전에 사용 흐름과 코드 경계를 다시 정렬하는 것이었고,
두 번째 작업은 Portfolio Proposal 계약 정의,
세 번째 작업은 registry helper 분리,
네 번째 작업은 Portfolio Proposal Draft UI / persistence 구현,
다섯 번째 작업은 Portfolio Proposal Monitoring Review 구현,
여섯 번째 작업은 Portfolio Proposal Pre-Live Feedback 구현,
일곱 번째 작업은 Portfolio Proposal Paper Tracking Feedback 구현이다.
