# Phase 34 Current Chapter TODO

## 진행 상태

- `active`

## 검증 상태

- `not_ready_for_qa`

## 현재 목표

Phase 34의 목표는 Phase 33의 paper tracking ledger를 바로 주문으로 연결하는 것이 아니다.
저장된 paper ledger record를 읽어 최종 실전 후보로 선정할지, 더 볼지, 거절할지, 재검토할지 판단하는
`Final Portfolio Selection Decision Pack`을 만드는 것이다.

## 작업 단위 진행 순서

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase 34 전체 목표 | Final Portfolio Selection Decision Pack을 만든다 | `active` |
| 첫 번째 작업 | Final decision 계약과 저장소 경계 정의 | `completed` |
| 두 번째 작업 | Decision evidence pack 계산 기준 추가 | `pending` |
| 세 번째 작업 | Final decision UI 추가 | `pending` |
| 네 번째 작업 | Saved final decision review와 Phase 35 handoff 정리 | `pending` |

## 1. Phase kickoff

- `completed` Phase 33 closeout 확인
  - Phase 33은 `complete / manual_qa_completed` 상태다.
- `completed` Phase 33 next phase preparation 확인
  - Phase 34 방향은 `Final Portfolio Selection Decision Pack`이다.
- `completed` Phase 34 문서 bundle 생성
  - 문서 위치는 `.note/finance/phases/phase34/`이다.

## 2. 첫 번째 작업 준비 항목

- `completed` final decision row schema 정의
  - decision id, source paper ledger id, source type / id, decision route, evidence snapshot, operator reason을 정한다.
- `completed` append-only 저장소 경계 정의
  - 예상 저장소는 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이다.
- `completed` live approval / order instruction 경계 정의
  - `selected` decision은 최종 실전 후보 선정이지 주문 실행이 아니다.

## 3. Validation

- `completed` 문서 schema / terminology review
- `pending` 향후 구현 대상 모듈 확인
- `pending` user manual QA

## 4. Documentation Sync

- `completed` phase kickoff plan 문서 생성
- `completed` current chapter TODO 문서 생성
- `completed` first work-unit 문서 생성
- `completed` test checklist 초안 생성
- `completed` roadmap / doc index / work log / question log sync

## 현재 판단

Phase 34는 active / not_ready_for_qa 상태다.
첫 번째 작업인 final decision 계약과 저장소 경계 정의는 완료했고,
다음 작업은 저장된 paper ledger record를 final decision evidence pack으로 계산하는 기준을 구현하는 것이다.
아직 UI 구현, final decision 저장, Phase35 handoff 구현은 시작하지 않았다.
