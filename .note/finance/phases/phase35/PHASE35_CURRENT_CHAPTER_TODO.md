# Phase 35 Current Chapter TODO

## 진행 상태

- `implementation_complete`

## 검증 상태

- `manual_qa_pending`

## 현재 목표

Phase 35의 목표는 Phase 34에서 최종 선정된 final review record를 바로 주문으로 연결하는 것이 아니다.
선정된 후보를 실제 운영 전 어떤 리밸런싱 / 중단 / 축소 / 재검토 기준으로 관리할지
`Post-Selection Operating Guide`로 정리하는 것이다.

## 작업 단위 진행 순서

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase 35 전체 목표 | 최종 선정 후보의 운영 가이드를 만든다 | `implementation_complete` |
| 첫 번째 작업 | Operating policy 계약 정의 | `completed` |
| 두 번째 작업 | Phase35 input selector / readiness 기준 | `completed` |
| 세 번째 작업 | Operating guide preview / record surface | `completed` |
| 네 번째 작업 | Saved guide review와 다음 handoff 정리 | `completed` |

## 1. Phase kickoff

- `completed` Phase 34 closeout 확인
  - Phase 34는 `complete / manual_qa_completed` 상태다.
- `completed` Phase 34 next phase preparation 확인
  - Phase 35 방향은 `Post-Selection Operating Guide`다.
- `completed` Phase 35 문서 bundle 생성
  - 문서 위치는 `.note/finance/phases/phase35/`이다.

## 2. 첫 번째 작업 준비 항목

- `completed` selected final review record 입력 기준 정의
  - `decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO`
  - `phase35_handoff.handoff_route = READY_FOR_POST_SELECTION_OPERATING_GUIDE`
- `completed` operating policy 필드 초안 정의
  - rebalancing cadence
  - rebalance trigger
  - reduce / stop trigger
  - re-review trigger
  - capital / live approval boundary
- `completed` 저장소 경계 판단
  - `.note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl`을 새 append-only registry로 둔다.
  - final decision record는 원본 선정 판단으로 보존한다.
  - current candidate / proposal / final decision 원본을 덮어쓰지 않는다.

## 3. 두 번째 작업 완료 항목

- `completed` Phase35 input selector 구현
  - selected final review record만 `Guide Eligible = Yes`로 읽는다.
- `completed` readiness route 구현
  - `OPERATING_GUIDE_RECORD_READY`
  - `OPERATING_GUIDE_NEEDS_INPUT`
  - `OPERATING_GUIDE_BLOCKED`
- `completed` selected가 아닌 final decision row 제외 안내

## 4. 세 번째 작업 완료 항목

- `completed` `Backtest > Post-Selection Guide` workflow panel 추가
- `completed` operating guide 입력 UI 구현
  - Guide ID
  - Capital Mode
  - Rebalancing Cadence
  - 자본 / 승인 경계
  - 리밸런싱 / 축소 / 중단 / 재검토 기준
- `completed` `운영 가이드 기록` append-only save 구현
- `completed` Final Review에서 Post-Selection Guide로 이동하는 버튼 연결

## 5. 네 번째 작업 완료 항목

- `completed` 저장된 operating guide review table 구현
- `completed` saved guide 상세 JSON / component / operating policy 확인 구현
- `completed` base workflow complete handoff route 구현
  - `POST_SELECTION_OPERATING_GUIDE_READY`

## 6. Validation

- `completed` phase35 helper / UI 구현 후 `py_compile`
- `completed` selected final decision input smoke
- `pending` user manual QA

## 7. Documentation Sync

- `completed` phase kickoff plan 문서 생성
- `completed` current chapter TODO 문서 생성
- `completed` first / second / third / fourth work-unit 문서 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` Phase35 구현 후 operations guide / code analysis 문서 검토

## 현재 판단

Phase 35는 implementation_complete / manual_qa_pending 상태다.
첫 번째부터 네 번째 작업까지 구현했으며,
이제 사용자가 `PHASE35_TEST_CHECKLIST.md`를 기준으로 manual QA를 진행하면 된다.

구현된 내용:

- `Backtest > Post-Selection Guide` workflow panel
- selected final review record input selector
- `.note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl` append-only 저장소 helper
- operating guide readiness / blocker / score
- 리밸런싱 / 축소 / 중단 / 재검토 운영 기준 입력
- `운영 가이드 기록` 명시 액션
- 저장된 운영 가이드 review surface
- live approval / broker order / 자동매매 비활성 경계

중요한 경계:

- Phase35도 live approval이나 broker order가 아니다.
- Phase35는 Portfolio Proposal 탭을 다시 키우는 작업이 아니다.
- Phase35는 Phase34 final review record를 읽어 운영 기준을 만드는 작업이다.
