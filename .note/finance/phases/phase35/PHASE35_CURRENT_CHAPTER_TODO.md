# Phase 35 Current Chapter TODO

## 진행 상태

- `active`

## 검증 상태

- `not_ready_for_qa`

## 현재 목표

Phase 35의 목표는 Phase 34에서 최종 선정된 final review record를 바로 주문으로 연결하는 것이 아니다.
선정된 후보를 실제 운영 전 어떤 리밸런싱 / 중단 / 축소 / 재검토 기준으로 관리할지
`Post-Selection Operating Guide`로 정리하는 것이다.

## 작업 단위 진행 순서

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase 35 전체 목표 | 최종 선정 후보의 운영 가이드를 만든다 | `active` |
| 첫 번째 작업 | Operating policy 계약 정의 | `pending` |
| 두 번째 작업 | Phase35 input selector / readiness 기준 | `pending` |
| 세 번째 작업 | Operating guide preview / record surface | `pending` |
| 네 번째 작업 | Saved guide review와 다음 handoff 정리 | `pending` |

## 1. Phase kickoff

- `completed` Phase 34 closeout 확인
  - Phase 34는 `complete / manual_qa_completed` 상태다.
- `completed` Phase 34 next phase preparation 확인
  - Phase 35 방향은 `Post-Selection Operating Guide`다.
- `completed` Phase 35 문서 bundle 생성
  - 문서 위치는 `.note/finance/phases/phase35/`이다.

## 2. 첫 번째 작업 준비 항목

- `pending` selected final review record 입력 기준 정의
  - `decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO`
  - `phase35_handoff.handoff_route = READY_FOR_POST_SELECTION_OPERATING_GUIDE`
- `pending` operating policy 필드 초안 정의
  - rebalancing cadence
  - rebalance trigger
  - reduce / stop trigger
  - re-review trigger
  - capital / live approval boundary
- `pending` 저장소 경계 판단
  - 새 append-only operating guide registry가 필요한지
  - final decision record의 snapshot만으로 충분한지
  - 어느 쪽이든 current candidate / proposal / final decision 원본을 덮어쓰지 않는지

## 3. Validation

- `pending` phase35 helper / UI 구현 후 `py_compile`
- `pending` selected final decision input smoke
- `pending` user manual QA

## 4. Documentation Sync

- `completed` phase kickoff plan 문서 생성
- `completed` current chapter TODO 문서 생성
- `pending` first work-unit 문서 생성
- `pending` roadmap / doc index / work log / question log sync
- `pending` Phase35 구현 후 operations guide / code analysis 문서 검토

## 현재 판단

Phase 35는 active / not_ready_for_qa 상태다.
아직 구현은 시작하지 않았고, 다음 작업은 `Operating policy 계약 정의`다.

중요한 경계:

- Phase35도 live approval이나 broker order가 아니다.
- Phase35는 Portfolio Proposal 탭을 다시 키우는 작업이 아니다.
- Phase35는 Phase34 final review record를 읽어 운영 기준을 만드는 작업이다.
