# Phase 35 Current Chapter TODO

## 진행 상태

- `implementation_complete`

## 검증 상태

- `manual_qa_pending`

## 현재 목표

Phase 35의 목표는 Phase 34에서 기록한 final review decision을 다시 저장하는 것이 아니다.
최종 판단 기록을 읽어 사용자가 마지막에 다음을 확인하게 만드는 것이다.

- 투자 가능 후보인지
- 투자하면 안 되는 후보인지
- 내용 / 관찰 근거가 부족한지
- 재검토가 필요한지
- 실제 투자 전 리밸런싱 / 축소 / 중단 / 재검토 기준이 충분한지

## 작업 단위 진행 순서

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase 35 전체 목표 | 최종 판단 결과를 최종 투자 지침 확인 화면으로 읽는다 | `implementation_complete` |
| 첫 번째 작업 | Final investment guide 계약 정의 | `completed` |
| 두 번째 작업 | Phase35 input selector / readiness 기준 | `completed` |
| 세 번째 작업 | Final guide preview UI 구현 | `completed` |
| 네 번째 작업 | No-extra-save handoff와 문서 보정 | `completed` |

## 1. Phase kickoff

- `completed` Phase 34 closeout 확인
  - Phase 34는 `complete / manual_qa_completed` 상태다.
- `completed` Phase 34 next phase preparation 확인
  - Phase 35 입력은 Final Review의 최종 판단 기록이다.
- `completed` Phase 35 문서 bundle 생성
  - 문서 위치는 `.note/finance/phases/phase35/`이다.

## 2. 첫 번째 작업 완료 항목

- `completed` selected final review record 입력 기준 정의
  - `decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO`
  - 신규 저장 row는 `phase35_handoff.handoff_route = READY_FOR_FINAL_INVESTMENT_GUIDE`로 읽는다.
  - 기존 QA row의 `READY_FOR_POST_SELECTION_OPERATING_GUIDE`도 backward compatibility로 읽는다.
- `completed` 최종 판단 문구 정의
  - `SELECT_FOR_PRACTICAL_PORTFOLIO`: 투자 가능 후보
  - `HOLD_FOR_MORE_PAPER_TRACKING`: 내용 부족 / 관찰 필요
  - `REJECT_FOR_PRACTICAL_USE`: 투자하면 안 됨
  - `RE_REVIEW_REQUIRED`: 재검토 필요
- `completed` 저장소 경계 보정
  - Phase35는 새 append-only registry를 만들지 않는다.
  - Final Review의 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이 최종 판단 원본이다.
  - Post-Selection Guide는 read / preview surface다.

## 3. 두 번째 작업 완료 항목

- `completed` Phase35 input selector 구현
  - selected final review record만 최종 지침 확인 대상으로 선택할 수 있다.
- `completed` final investment readiness route 구현
  - `FINAL_INVESTMENT_GUIDE_READY`
  - `FINAL_INVESTMENT_GUIDE_NEEDS_INPUT`
  - `FINAL_INVESTMENT_GUIDE_BLOCKED`
- `completed` selected가 아닌 final decision row 제외 안내

## 4. 세 번째 작업 완료 항목

- `completed` `Backtest > Post-Selection Guide` workflow panel 보정
- `completed` final guide preview UI 구현
  - Capital Mode
  - Rebalancing Cadence
  - 자본 / 승인 경계
  - 리밸런싱 / 축소 / 중단 / 재검토 기준
- `completed` `운영 가이드 기록` append-only save 제거
- `completed` Final Review에서 Post-Selection Guide로 이동하는 버튼 유지

## 5. 네 번째 작업 완료 항목

- `completed` saved guide review table 제거
- `completed` `추가 저장 없음` disabled action 추가
- `completed` live approval / broker order / 자동매매 비활성 경계 유지
- `completed` Phase35 checklist를 no-extra-save QA 기준으로 개편
- `completed` operations / code analysis / roadmap / index 문서 보정

## 6. Validation

- `completed` phase35 helper / UI 구현 후 `py_compile`
- `completed` selected final decision input smoke
- `pending` user manual QA

## 현재 판단

Phase 35는 implementation_complete / manual_qa_pending 상태다.
첫 번째부터 네 번째 작업까지 구현했으며,
이제 사용자가 `PHASE35_TEST_CHECKLIST.md`를 기준으로 manual QA를 진행하면 된다.

구현된 내용:

- `Backtest > Post-Selection Guide` workflow panel
- selected final review record input selector
- 투자 가능 후보 / 투자하면 안 됨 / 내용 부족 / 재검토 필요 표시
- final investment readiness / blocker / score
- 리밸런싱 / 축소 / 중단 / 재검토 운영 전 기준 preview
- 추가 저장 없음 경계
- live approval / broker order / 자동매매 비활성 경계

중요한 경계:

- Phase35는 Final Review 기록을 다시 저장하지 않는다.
- Phase35도 live approval이나 broker order가 아니다.
- Phase35는 Portfolio Proposal 탭을 다시 키우는 작업이 아니다.
- Phase35는 Phase34 final review record를 읽어 최종 투자 가능성과 운영 전 지침을 확인하는 작업이다.
