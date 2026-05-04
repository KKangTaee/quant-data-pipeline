# Phase 35 Test Checklist

## 목적

이 checklist는 Phase 35 `Post-Selection Operating Guide` 구현이 끝난 뒤
사용자가 직접 확인할 manual QA 문서다.

현재 Phase 35는 `implementation_complete / manual_qa_pending` 상태다.

## 사용 방법

- `Backtest > Post-Selection Guide`는 Phase34에서 최종 선정한 record를 운영 기준으로 바꾸는 마지막 작업 공간이다.
- `SELECT_FOR_PRACTICAL_PORTFOLIO`로 기록된 final review record만 운영 가이드 대상이다.
- `운영 가이드 기록`은 live approval이나 주문 지시가 아니다.
- QA 중 저장되는 operating guide는 `.note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl`에 append-only로 남는다.

## 1. Workflow Panel 확인

- 확인 위치:
  - `Backtest`
- 체크 항목:
  - [ ] workflow navigation에 `Post-Selection Guide`가 보이는지
  - [ ] `Final Review`에서 `Post-Selection Guide 열기` 버튼을 누르면 해당 panel로 이동하는지
  - [ ] 상단 card에서 `Live Approval = Disabled`, `Order = Disabled`가 보이는지
  - [ ] 이 화면이 Portfolio Proposal 탭 안에 섞이지 않고 별도 마지막 작업 공간으로 읽히는지

## 2. Phase35 입력 대상 확인

- 확인 위치:
  - `Backtest > Post-Selection Guide`
  - `1. Phase35 입력 대상 확인`
- 체크 항목:
  - [ ] Final Review record table에서 `Guide Eligible`이 보이는지
  - [ ] `SELECT_FOR_PRACTICAL_PORTFOLIO` / `READY_FOR_POST_SELECTION_OPERATING_GUIDE` record만 `Guide Eligible = Yes`로 보이는지
  - [ ] 보류 / 거절 / 재검토 record는 운영 guide 대상에서 제외되는지
  - [ ] eligible record가 없을 때 Final Review에서 먼저 선정 판단을 기록하라는 안내가 보이는지

## 3. 선정 기록과 Component 확인

- 확인 위치:
  - `Backtest > Post-Selection Guide`
  - `2. 선정 기록과 component 확인`
- 체크 항목:
  - [ ] 선택한 final decision의 Decision ID, Source, Evidence, Phase35 handoff가 보이는지
  - [ ] target component table에서 Registry ID, Title, Role, Target Weight, Benchmark, Data Trust가 보이는지
  - [ ] target weight 합계가 운영 가이드 readiness에서 확인되는지

## 4. 운영 기준 작성 / 기록 확인

- 확인 위치:
  - `Backtest > Post-Selection Guide`
  - `3. 운영 기준 작성`
  - `4. 운영 가이드 기록 준비`
- 체크 항목:
  - [ ] Guide ID, Capital Mode, Rebalancing Cadence를 입력 / 선택할 수 있는지
  - [ ] 자본 / 승인 경계, 리밸런싱 기준, 축소 기준, 중단 기준, 재검토 기준을 입력할 수 있는지
  - [ ] 필수 기준이 비어 있거나 guide id가 중복이면 readiness가 block / needs input으로 읽히는지
  - [ ] 정상 입력이면 `OPERATING_GUIDE_RECORD_READY`가 보이는지
  - [ ] `운영 가이드 기록` 버튼이 readiness 통과 시 활성화되는지
  - [ ] 저장 후 성공 메시지가 보이고, live approval이나 주문이 아니라는 문구가 보이는지

## 5. 기록된 운영 가이드 확인

- 확인 위치:
  - `Backtest > Post-Selection Guide`
  - `5. 기록된 운영 가이드 확인`
- 체크 항목:
  - [ ] 방금 저장한 guide가 saved guide table에 보이는지
  - [ ] saved guide에서 Source Decision, Source, Components, Weight Total, Guide Route, Handoff가 보이는지
  - [ ] 상세 확인에서 component table과 운영 기준이 다시 보이는지
  - [ ] saved guide JSON에서 `live_approval = false`, `order_instruction = false`인지
  - [ ] source final decision registry가 덮어써지지 않고 operating guide registry에만 append되는지

## 6. 문서 / 경계 확인

- 확인 문서:
  - `.note/finance/phases/phase35/PHASE35_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phases/phase35/PHASE35_COMPLETION_SUMMARY.md`
  - `.note/finance/phases/phase35/PHASE35_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/operations/POST_SELECTION_OPERATING_GUIDES_GUIDE.md`
  - `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md`
- 체크 항목:
  - [ ] Phase35가 `implementation_complete / manual_qa_pending` 상태로 설명되는지
  - [ ] Phase35가 최종 선정 후보를 운영 기준으로 바꾸는 단계라고 설명되는지
  - [ ] Phase35도 live approval / broker order / 자동매매가 아니라고 설명되는지
  - [ ] Phase35 완료 후 기본 흐름은 "실전 후보 포트폴리오 선정 + 운영 가이드"까지 갖춘 상태로 읽히는지

## 완료 판단

위 항목이 통과하면,
**사용자는 백테스트 후보를 최종 실전 후보로 선정하고, 그 후보의 기본 운영 기준까지 확인할 수 있는 상태**로 본다.

다만 이것은 broker order, 자동매매, live approval, 수익 보장이 아니다.
