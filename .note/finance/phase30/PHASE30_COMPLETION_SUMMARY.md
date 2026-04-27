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

## 아직 남아 있는 것

- Portfolio Proposal row 계약 정의
- Portfolio Proposal UI / persistence 구현
- Pre-Live monitoring surface 연결
- 실제 `backtest.py` 모듈 분리
- Phase 30 manual QA

## 현재 판단

Phase 30은 active 상태다.
첫 작업은 portfolio proposal 기능 구현이 아니라,
사용 흐름 재정렬과 리팩토링 경계 검토다.
이 첫 작업 단위는 문서와 Guide 기준으로 정리되었고,
다음 작업에서는 실제 모듈 분리 또는 Portfolio Proposal row 계약 정의 중 하나를 선택한다.
