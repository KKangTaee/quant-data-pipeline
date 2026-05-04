# Phase 34 Current Chapter TODO

## 진행 상태

- `complete`

## 검증 상태

- `manual_qa_completed`

## 현재 목표

Phase 34의 목표는 Portfolio Proposal 초안 저장 뒤에 저장 버튼을 계속 늘리는 것이 아니다.
`Backtest > Final Review`를 별도 탭으로 분리해 단일 후보 또는 저장된 proposal을 읽고,
validation / robustness / paper observation 기준 / operator judgment를 하나의 최종 검토 기록으로 남기는 것이다.

## 작업 단위 진행 순서

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase 34 전체 목표 | Final Portfolio Selection Decision Pack을 만든다 | `completed` |
| 첫 번째 작업 | Final decision 계약과 저장소 경계 정의 | `completed` |
| 두 번째 작업 | Decision evidence pack 계산 기준 추가 | `completed` |
| 세 번째 작업 | Final decision UI 추가 | `completed` |
| 네 번째 작업 | Saved final decision review와 Phase 35 handoff 정리 | `completed` |
| 보정 작업 | Portfolio Proposal 반복 저장 UX를 Final Review 탭으로 분리 | `completed` |

## 1. Phase kickoff

- `completed` Phase 33 closeout 확인
  - Phase 33은 `complete / manual_qa_completed` 상태다.
- `completed` Phase 33 next phase preparation 확인
  - Phase 34 방향은 `Final Portfolio Selection Decision Pack`이다.
- `completed` Phase 34 문서 bundle 생성
  - 문서 위치는 `.note/finance/phases/phase34/`이다.

## 2. 첫 번째 작업 준비 항목

- `completed` final decision row schema 정의
  - decision id, source candidate / proposal id, source observation id, decision route, evidence snapshot, operator reason을 정한다.
- `completed` append-only 저장소 경계 정의
  - 예상 저장소는 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이다.
- `completed` live approval / order instruction 경계 정의
  - `selected` decision은 최종 실전 후보 선정이지 주문 실행이 아니다.

## 3. Validation

- `completed` 문서 schema / terminology review
- `completed` 향후 구현 대상 모듈 확인
- `completed` helper smoke validation
- `completed` Final Review tab reboundary smoke validation
- `completed` user manual QA

## 4. Documentation Sync

- `completed` phase kickoff plan 문서 생성
- `completed` current chapter TODO 문서 생성
- `completed` first work-unit 문서 생성
- `completed` test checklist QA handoff 갱신
- `completed` roadmap / doc index / work log / question log sync
- `completed` code analysis / operations guide sync
- `completed` Final Review tab 분리와 checklist 재개편

## 현재 판단

Phase 34는 complete / manual_qa_completed 상태다.
첫 번째부터 네 번째 작업까지 구현한 뒤, 사용자가 제기한 반복 저장 UX 문제를 반영해
최종 검토 surface를 `Backtest > Final Review` 탭으로 분리했다.
2026-05-04 사용자가 `PHASE34_TEST_CHECKLIST.md` 기준 manual QA 완료를 확인했다.

구현된 내용:

- `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` append-only 저장소 helper
- 단일 current candidate 또는 저장된 proposal을 읽는 Final Review source 선택
- validation / robustness / paper observation 기준을 하나로 묶는 Final Review Evidence Pack
- 별도 Paper Ledger save 없이 final review record 안에 들어가는 inline paper observation snapshot
- `최종 검토 결과 기록` 명시 기록 버튼
- 저장된 최종 검토 결과 review surface
- Phase35 `Post-Selection Operating Guide` handoff
- live approval / order instruction 비활성 경계
