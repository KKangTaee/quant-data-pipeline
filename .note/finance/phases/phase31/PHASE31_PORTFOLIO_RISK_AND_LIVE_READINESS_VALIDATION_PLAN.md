# Phase 31 Portfolio Risk And Live Readiness Validation Plan

## 이 문서는 무엇인가

이 문서는 Phase 31에서 무엇을 만들지 정리하는 kickoff plan이다.
Phase 31은 새로운 투자 승인 기록을 하나 더 만드는 단계가 아니라,
Phase 30까지 만들어진 Candidate Review / Pre-Live / Portfolio Proposal 결과를 읽어서
실전 검토 후보로 구조적으로 충분한지 검증하는 단계다.

## 목적

- 단일 current candidate 또는 Portfolio Proposal draft를 같은 검증 화면에서 읽을 수 있게 한다.
- 후보 묶음의 비중, 역할, 중복, blocker, Pre-Live 상태를 포트폴리오 위험 관점으로 요약한다.
- `Live Readiness 후보 가능 / 보강 필요 / 차단`을 투자 승인과 분리된 검증 신호로 보여준다.

## 쉽게 말하면

지금까지는 좋은 백테스트 결과를 후보로 저장하고,
후보 여러 개를 Portfolio Proposal 초안으로 묶을 수 있게 만들었다.

Phase 31은 그 다음 질문을 다룬다.

- 이 후보를 실제 투자 검토 후보로 더 밀어도 되는가?
- 후보 여러 개를 묶었을 때 한쪽에 너무 쏠리지 않는가?
- Pre-Live / Real-Money / Data Trust / blocker 상태가 함께 봐도 괜찮은가?

즉, 저장 버튼을 하나 더 만드는 것이 아니라
`이 포트폴리오 구조가 실전 검토 후보로 버틸 수 있는지`를 보는 검증 pack을 만든다.

## 왜 필요한가

Phase 30까지는 아래가 가능해졌다.

- 좋은 run을 Candidate Packaging으로 보낸다.
- Candidate Review Note를 저장한다.
- Current Candidate Registry에 명시적으로 append한다.
- Pre-Live 운영 기록을 남긴다.
- 단일 후보는 Live Readiness 직행 가능 여부를 본다.
- 여러 후보는 Portfolio Proposal draft로 저장한다.
- 저장 proposal을 Monitoring / Pre-Live / Paper Tracking snapshot으로 다시 읽는다.

하지만 아직 부족한 부분이 있다.

- 후보 여러 개가 같은 전략 family, universe, factor, benchmark에 쏠려 있는지 한눈에 보기 어렵다.
- target weight가 100%여도 실제 포트폴리오 관점에서 집중 위험이 큰지 판단하는 표면이 약하다.
- 단일 후보와 다중 proposal을 같은 기준으로 `다음 검증 단계에 넘길 수 있는지` 읽는 화면이 없다.
- Phase 32 이후 robustness / stress validation이 읽을 입력 형태가 아직 고정되어 있지 않다.

## 이 phase가 끝나면 좋은 점

- 사용자는 Portfolio Proposal을 저장한 뒤 바로 투자 결정을 고민하지 않고, 먼저 risk validation pack을 볼 수 있다.
- 단일 후보도 다중 proposal도 같은 언어로 `ready / review required / blocked`를 읽을 수 있다.
- 다음 Phase 32의 robustness 검증은 어떤 후보 또는 proposal을 입력으로 삼을지 더 명확해진다.
- Final Selection으로 가기 전에 `포트폴리오 구조상 말이 되는가`라는 질문을 별도 검증 단계로 고정할 수 있다.

## 현재 구현 상태

- 진행 상태: `implementation_complete`
- 검증 상태: `manual_qa_pending`

구현 결과는 이 kickoff plan의 경계를 따른다.
새 approval registry를 만들지 않고,
`Backtest > Portfolio Proposal` 안에서 단일 후보, 작성 중 proposal, 저장 proposal을 같은 Validation Pack으로 읽는다.
수동 QA는 `PHASE31_TEST_CHECKLIST.md`에서 진행한다.

## 이 phase에서 다루는 대상

직접 다루는 범위:

- `Backtest > Portfolio Proposal`
- `app/web/backtest_portfolio_proposal.py`
- `app/web/backtest_portfolio_proposal_helpers.py`
- `app/web/runtime/candidate_registry.py`
- `app/web/runtime/portfolio_proposal.py`
- `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`
- `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`
- `.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`

직접 다루지 않는 범위:

- broker 주문 / 자동매매
- 최종 투자 승인 registry
- 실제 paper PnL ledger
- optimizer 기반 자동 비중 산출
- Phase 32의 본격 stress / robustness sweep

## 구현 우선순위와 완료 상태

1. Portfolio Risk input contract 정의 - `completed`
   - 쉽게 말하면: 단일 후보와 proposal draft를 검증 pack이 읽을 수 있는 같은 입력 모양으로 맞춘다.
   - 왜 먼저 하는가: 입력이 흐릿하면 Live Readiness 판단 기록을 중복해서 만들 위험이 커진다.
   - 기대 효과: Phase 31은 기존 기록을 재사용하고, 새 approval registry를 만들지 않는다는 경계가 분명해진다.

2. Portfolio Risk Summary / Readiness panel 구현 - `completed`
   - 쉽게 말하면: 후보 구성, 비중, core anchor, blocker, Pre-Live 상태를 한 화면에서 요약한다.
   - 왜 필요한가: 현재 proposal draft는 저장할 수 있지만, 실전 검토 후보로 구조적으로 괜찮은지는 별도 요약이 없다.
   - 기대 효과: 사용자는 `ready`, `review required`, `blocked`를 투자 승인과 분리해서 읽을 수 있다.

3. Component overlap / concentration check 추가 - `completed`
   - 쉽게 말하면: 후보들이 서로 다른 역할을 하는지, 사실상 같은 위험에 몰려 있는지 본다.
   - 왜 필요한가: 좋은 후보 여러 개를 묶어도 같은 factor나 universe에 몰리면 포트폴리오 위험은 줄지 않을 수 있다.
   - 기대 효과: Phase 32에서 더 깊게 robustness를 보기 전에 기본 구조 위험을 걸러낼 수 있다.

4. 다음 단계 안내 field 고정 - `completed`
   - 쉽게 말하면: robustness 검증이 읽을 최소 summary와 blocker를 정한다.
   - 왜 필요한가: Phase 31 결과가 다음 phase 입력이 되어야 개발 흐름이 끊기지 않는다.
   - 기대 효과: Phase 32를 새로 설계할 때 같은 입력 계약을 다시 만들지 않아도 된다.

## 이 문서에서 자주 쓰는 용어

- `Live Readiness Validation`: 실제 투자 승인 전, 후보 또는 proposal이 다음 검증 단계로 넘어갈 수 있는지 보는 검증이다.
- `Validation Pack`: 후보 구성, 비중, risk signal, blocker, next action을 한 번에 묶어 읽는 검증 결과다.
- `Component`: proposal 안에 들어간 개별 current candidate를 뜻한다.
- `Core Anchor`: 포트폴리오의 중심 역할을 맡는 후보다. 모든 proposal에 꼭 하나 이상 있어야 한다.
- `Concentration`: 비중이나 risk source가 한 후보 / 한 전략군 / 한 universe에 지나치게 몰린 상태다.
- `Overlap`: 서로 다른 후보처럼 보이지만 실제로는 같은 전략 family, factor, universe, benchmark에 크게 의존하는 상태다.
- `Hard Blocker`: 다음 검증 단계로 넘기기 전에 반드시 해결해야 하는 차단 항목이다.

## 이번 phase의 운영 원칙

- Phase 31은 live approval이 아니다.
- Phase 31은 Candidate Review나 Portfolio Proposal의 판단 기록을 반복 저장하지 않는다.
- 우선은 read-only validation pack으로 시작한다.
- 새 append-only registry는 필요성이 분명해질 때만 후속 phase에서 검토한다.
- optimizer는 만들지 않는다. 비중 자동 추천보다 기존 비중이 검증 가능한지 먼저 본다.
- Phase 30 manual QA가 끝나기 전에는 Phase 31 구현 중에도 Phase 30 status를 `manual_qa_pending`으로 유지한다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업. Portfolio Risk 입력 계약과 검증 모델 정의

- 단일 후보와 proposal draft를 같은 validation input으로 정규화한다.
- current candidate, Pre-Live record, proposal component, evidence snapshot 중 어느 값을 우선 읽을지 정한다.
- validation result의 route label, blocker, next action, score 필드를 정의한다.

### 두 번째 작업. Portfolio Proposal 안에 Validation Pack surface 추가

- `Backtest > Portfolio Proposal`의 보조 영역 또는 새 tab에서 validation summary를 보여준다.
- 단일 후보와 proposal draft를 선택하면 같은 형태의 risk/readiness panel을 렌더링한다.
- `Open Live Readiness`를 실제 승인 버튼처럼 보이게 하지 않고, 검증 결과 확인 표면으로 유지한다.

### 세 번째 작업. Component risk / overlap table 구현

- 후보별 role, target weight, strategy family, benchmark, Pre-Live status, promotion, deployment, data trust를 같이 보여준다.
- core anchor 부재, weight concentration, active candidate hold/rejected, missing snapshot 같은 blocker를 분리한다.
- factor / universe / benchmark overlap은 처음에는 저장된 contract에서 읽을 수 있는 값 중심의 first pass로 구현한다.

### 네 번째 작업. 다음 단계 안내 요약 추가

- Phase 32가 robustness / stress validation에 쓸 최소 입력을 정한다.
- validation pack이 `ready_for_robustness`, `paper_tracking_required`, `blocked` 같은 다음 행동을 명확히 말하게 한다.
- Phase 31 completion과 Phase 32 preparation 문서를 갱신한다.

## 다음에 확인할 것

- Phase 31 manual QA에서 direct single-candidate path, 작성 중 proposal path, saved proposal Validation Pack을 확인한다.
- Phase 30 manual QA pending 상태와 Phase 31 manual QA pending 상태가 혼동되지 않는지 확인한다.
- Phase 32를 열 때는 Phase 31 `handoff_summary`를 robustness / stress validation 입력 기준으로 사용한다.

## 한 줄 정리

Phase 31은 후보 또는 proposal을 다시 저장하는 단계가 아니라,
실전 포트폴리오 후보로 더 검증할 만한 구조인지 읽는 Portfolio Risk / Live Readiness 검증 단계다.
