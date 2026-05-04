# Phase 35 Test Checklist

## 목적

이 checklist는 Phase 35 `Post-Selection Guide` 보정 구현이 끝난 뒤
사용자가 직접 확인할 manual QA 문서다.

현재 Phase 35는 `implementation_complete / manual_qa_pending` 상태다.

## 사용 방법

- `Backtest > Post-Selection Guide`는 Phase34에서 기록한 Final Review 결과를 다시 읽는 마지막 확인 화면이다.
- 이 화면은 새 저장소를 만들지 않는다.
- 최종 판단의 원본 기록은 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이다.
- Phase35는 투자 가능 후보 / 투자하면 안 됨 / 내용 부족 / 재검토 필요를 사용자가 쉽게 확인하게 돕는다.
- 이 화면도 live approval, broker order, 자동매매, 수익 보장이 아니다.

## 1. Workflow Panel 확인

- 확인 위치:
  - `Backtest`
- 체크 항목:
  - [ ] workflow navigation에 `Post-Selection Guide`가 보이는지
  - [ ] `Final Review`에서 `Post-Selection Guide 열기` 버튼을 누르면 해당 panel로 이동하는지
  - [ ] 상단 card에서 `Extra Save = Not Required`가 보이는지
  - [ ] 상단 card에서 `Live Approval = Disabled`, `Order = Disabled`가 보이는지
  - [ ] 이 화면이 Portfolio Proposal 탭 안에 섞이지 않고 별도 마지막 확인 공간으로 읽히는지

## 2. 최종 판단 결과 확인

- 확인 위치:
  - `Backtest > Post-Selection Guide`
  - `1. 최종 판단 결과 확인`
- 체크 항목:
  - [ ] Final Review record table에서 `투자 가능성`이 보이는지
  - [ ] `SELECT_FOR_PRACTICAL_PORTFOLIO` record는 `투자 가능 후보`로 읽히는지
  - [ ] `HOLD_FOR_MORE_PAPER_TRACKING` record는 `내용 부족 / 관찰 필요`로 읽히는지
  - [ ] `REJECT_FOR_PRACTICAL_USE` record는 `투자하면 안 됨`으로 읽히는지
  - [ ] `RE_REVIEW_REQUIRED` record는 `재검토 필요`로 읽히는지
  - [ ] eligible record가 없을 때 Final Review에서 먼저 최종 판단을 기록하라는 안내가 보이는지

## 3. 선정 기록과 Component 확인

- 확인 위치:
  - `Backtest > Post-Selection Guide`
  - `2. 선정 기록과 component 확인`
- 체크 항목:
  - [ ] 선택한 final decision의 Decision ID, Source, Evidence, Phase35 handoff가 보이는지
  - [ ] `투자 가능성 = 투자 가능 후보` badge가 보이는지
  - [ ] target component table에서 Registry ID, Title, Role, Target Weight, Benchmark, Data Trust가 보이는지
  - [ ] target weight 합계가 최종 지침 readiness에서 확인되는지

## 4. 운영 전 기준 확인

- 확인 위치:
  - `Backtest > Post-Selection Guide`
  - `3. 운영 전 기준 확인`
  - `4. 최종 투자 가능성 확인`
- 체크 항목:
  - [ ] 이 구간이 확인용 preview이며 별도 저장하지 않는다는 안내가 보이는지
  - [ ] Capital Mode, Rebalancing Cadence를 선택할 수 있는지
  - [ ] 자본 / 승인 경계, 리밸런싱 기준, 축소 기준, 중단 기준, 재검토 기준을 확인 / 수정해 볼 수 있는지
  - [ ] 기준이 부족하면 `FINAL_INVESTMENT_GUIDE_NEEDS_INPUT` 또는 block 상태로 읽히는지
  - [ ] 정상 조건이면 `FINAL_INVESTMENT_GUIDE_READY`가 보이는지
  - [ ] `운영 가이드 기록`, `Save Post-Selection Guide`, saved guide table 같은 추가 저장 UX가 보이지 않는지

## 5. 저장 경계 확인

- 확인 위치:
  - `Backtest > Post-Selection Guide`
  - `4. 최종 투자 가능성 확인`
- 체크 항목:
  - [ ] `추가 저장 없음` 버튼이 disabled 상태로 보이는지
  - [ ] `Live Approval / Order` 버튼이 disabled 상태로 보이는지
  - [ ] `최종 지침 Preview` JSON에서 `preview_only = true`인지
  - [ ] `최종 지침 Preview` JSON에서 `live_approval = false`, `order_instruction = false`인지
  - [ ] QA 중 `.note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl` 같은 새 파일이 생성되지 않는지
  - [ ] source final decision registry가 덮어써지지 않는지

## 6. 문서 / 경계 확인

- 확인 문서:
  - `.note/finance/phases/phase35/PHASE35_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phases/phase35/PHASE35_COMPLETION_SUMMARY.md`
  - `.note/finance/phases/phase35/PHASE35_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/operations/POST_SELECTION_FINAL_INVESTMENT_GUIDE.md`
  - `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md`
- 체크 항목:
  - [ ] Phase35가 `implementation_complete / manual_qa_pending` 상태로 설명되는지
  - [ ] Phase35가 최종 선정 후보를 다시 저장하는 단계가 아니라고 설명되는지
  - [ ] Phase35가 최종 투자 가능성 확인과 운영 전 지침 확인 단계라고 설명되는지
  - [ ] Phase35도 live approval / broker order / 자동매매가 아니라고 설명되는지
  - [ ] Phase35 완료 후 기본 흐름은 "실전 후보 포트폴리오 선정 + 운영 전 지침 확인"까지 갖춘 상태로 읽히는지

## 완료 판단

위 항목이 통과하면,
**사용자는 백테스트 후보를 최종 실전 후보로 선정하고, 그 후보의 기본 운영 전 지침까지 확인할 수 있는 상태**로 본다.

다만 이것은 broker order, 자동매매, live approval, 수익 보장이 아니다.
