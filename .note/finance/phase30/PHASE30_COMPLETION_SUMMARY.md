# Phase 30 Completion Summary

## 목적

이 문서는 Phase 30 `Portfolio Proposal And Pre-Live Monitoring Surface`의 진행 상황을 정리한다.

현재는 closeout summary가 아니라 active phase 진행 요약 초안이다.
Phase 30이 practical closeout에 도달하면 이 문서를 closeout 기준으로 다시 갱신한다.

## 진행 상태

- `active`

## 검증 상태

- `not_ready_for_qa`

## 이번 phase에서 현재까지 완료된 첫 작업

### 1. Product-flow reorientation

- Phase 29 이후 기준으로 `테스트에서 상용화 후보 검토까지 사용하는 흐름`을 다시 정렬했다.
- Candidate Draft / Candidate Review Note / Current Candidate Registry / Pre-Live Review / Portfolio Proposal의 역할을 한 흐름으로 설명했다.

쉽게 말하면:

- 사용자가 좋은 백테스트 결과를 보고 다음에 무엇을 해야 하는지 다시 손에 잡히게 만드는 작업이다.

### 2. Backtest refactor boundary

- `app/web/pages/backtest.py`의 책임 묶음을 확인했다.
- Candidate Review, Pre-Live, registry helper, History, Saved Portfolio 같은 분리 후보를 기록했다.

쉽게 말하면:

- 큰 파일을 바로 쪼개기보다, 어떤 제품 경계로 나누면 안전한지 먼저 정하는 작업이다.

## 이번 phase에서 현재까지 완료된 두 번째 작업

### 3. Portfolio Proposal contract

- Portfolio Proposal UI / persistence 구현 전에 proposal row의 최소 계약을 정의했다.
- 후보 묶음의 목적, 후보별 역할, 비중 근거, risk constraints, evidence snapshot, open blockers, operator decision을 필수 정보로 잡았다.
- 당시에는 저장소 후보를 `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`로 제안하되 파일 생성이나 append helper 구현은 하지 않았다.
- 네 번째 작업에서 이 저장소와 append helper가 실제 구현되었다.

쉽게 말하면:

- 포트폴리오 제안 화면을 만들기 전에, 무엇을 포트폴리오 제안이라고 부를지 먼저 정한 작업이다.

## 이번 phase에서 현재까지 완료된 세 번째 작업

### 4. Registry IO helper refactor

- `app/web/pages/backtest.py` 안에 있던 registry JSONL read / append helper를 `app/web/runtime/candidate_registry.py`로 분리했다.
- Current Candidate Registry, Candidate Review Notes, Pre-Live Candidate Registry의 파일 path constant와 I/O helper를 runtime boundary로 옮겼다.
- UI rendering, session state key, compare prefill, row schema, append-only semantics는 바꾸지 않았다.

쉽게 말하면:

- 화면은 그대로 두고, 후보 / review note / pre-live 저장소를 읽고 쓰는 작은 helper만 먼저 밖으로 뺀 작업이다.

## 이번 phase에서 현재까지 완료된 네 번째 작업

### 5. Portfolio Proposal Draft UI / persistence

- `Backtest > Portfolio Proposal` panel을 추가했다.
- current candidate 여러 개를 선택해 proposal objective, proposal type, 후보별 역할, target weight, weight reason, operator decision을 작성할 수 있게 했다.
- proposal row는 `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`에 append-only로 저장한다.
- `Proposal Registry` tab에서 저장된 proposal draft를 다시 확인할 수 있다.
- 저장 버튼은 live trading approval이나 주문 지시가 아니라 proposal draft 저장으로만 동작한다.

쉽게 말하면:

- 후보 여러 개를 "포트폴리오 제안 초안"으로 묶고, 왜 그렇게 묶는지 저장할 수 있는 첫 화면이 생겼다.

## 이번 phase에서 현재까지 완료된 다섯 번째 작업

### 6. Portfolio Proposal Monitoring Review

- `Backtest > Portfolio Proposal`에 `Monitoring Review` tab을 추가했다.
- 저장된 proposal draft를 monitoring state, component table, blocker, review gap, operator decision 관점으로 다시 읽을 수 있게 했다.
- monitoring state는 `blocked`, `needs_review`, `review_ready`로 요약하지만, live approval이나 주문 지시는 아니다.

쉽게 말하면:

- 저장된 포트폴리오 제안 초안을 다시 열어 "무엇이 막혀 있고, 무엇을 더 확인해야 하는지" 보는 화면이 생겼다.

## 아직 남아 있는 것

- Paper / Pre-Live tracking feedback 연결
- Candidate Review / Pre-Live / History / Saved Portfolio의 추가 `backtest.py` 모듈 분리
- Phase 30 manual QA

## 현재 판단

Phase 30은 active 상태다.
첫 작업은 portfolio proposal 기능 구현이 아니라,
사용 흐름 재정렬과 리팩토링 경계 검토다.
이 첫 작업 단위는 문서와 Guide 기준으로 정리되었고,
두 번째 작업으로 Portfolio Proposal row 계약도 정리되었다.
세 번째 작업으로 registry JSONL I/O helper를 실제 코드에서 분리했다.
네 번째 작업으로 Portfolio Proposal Draft UI와 append-only persistence를 구현했다.
다섯 번째 작업으로 Portfolio Proposal Monitoring Review surface를 구현했다.
다음 작업에서는 paper / pre-live tracking feedback 연결 또는 Candidate Review / Pre-Live 추가 모듈 분리를 선택한다.
