# Phase 35 Completion Summary

## 현재 상태

- 진행 상태: `implementation_complete`
- 검증 상태: `manual_qa_pending`

Phase 35 구현은 완료됐고, 사용자 manual QA handoff 단계다.

## 목적

Phase 35 `Post-Selection Operating Guide`는
Phase 34에서 최종 선정된 후보를 실제 운영 전 리밸런싱 / 중단 / 축소 / 재검토 기준으로 정리하는 phase다.

## 이번 phase에서 완료된 것

### 1. Phase kickoff

- Phase 34 checklist 완료 신호를 반영해 Phase 34를 closeout했다.
- Phase 35 문서 bundle을 `.note/finance/phases/phase35/` 아래에 생성했다.
- Phase 35 목표를 `Post-Selection Operating Guide`로 정리했다.

쉽게 말하면:

- 이제 "최종 후보를 골랐다"에서 끝내지 않고, "고른 후보를 어떻게 운영할 것인가"를 만들 준비가 되었다.

### 2. Operating policy 계약 정의

- Phase35 입력은 `SELECT_FOR_PRACTICAL_PORTFOLIO`와 `READY_FOR_POST_SELECTION_OPERATING_GUIDE`를 만족하는 final review record로 제한했다.
- 운영 가이드 필드를 Guide ID, Capital Mode, 자본 / 승인 경계, rebalancing cadence, rebalance trigger, reduce trigger, stop trigger, re-review trigger로 정했다.
- 새 append-only 저장소를 `.note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl`로 분리했다.

쉽게 말하면:

- 최종 선정 record를 덮어쓰지 않고, 선정 이후 운영 기준만 별도 기록으로 남긴다.

### 3. Phase35 input selector / readiness 기준

- `Backtest > Post-Selection Guide`에서 Final Review record 전체를 먼저 보여주고, 운영 guide 대상 여부를 `Guide Eligible`로 표시한다.
- selected final decision만 운영 가이드 대상으로 선택할 수 있다.
- readiness route는 `OPERATING_GUIDE_RECORD_READY`, `OPERATING_GUIDE_NEEDS_INPUT`, `OPERATING_GUIDE_BLOCKED`로 구분한다.

쉽게 말하면:

- 보류 / 거절 / 재검토 record는 운영 가이드 대상이 아니며, 사용자가 왜 제외되는지 볼 수 있다.

### 4. Operating guide preview / record surface

- `Backtest > Post-Selection Guide` workflow panel을 추가했다.
- 사용자는 target components, target weight, source evidence를 보고 운영 기준을 작성할 수 있다.
- `운영 가이드 기록` 버튼은 readiness가 통과했을 때만 활성화된다.
- 기록은 append-only이며 current candidate, proposal, final decision 원본을 덮어쓰지 않는다.

쉽게 말하면:

- 최종 후보 선정 기록이 "운영 가능한 기준표"로 바뀐다.

### 5. Saved guide review / handoff

- 기록된 operating guide를 table로 다시 읽는다.
- 선택한 guide의 source decision, component, operating policy, JSON을 확인할 수 있다.
- 저장된 guide의 handoff는 `POST_SELECTION_OPERATING_GUIDE_READY`로 읽힌다.
- Final Review에서 `Post-Selection Guide 열기`로 이동할 수 있다.

쉽게 말하면:

- 사용자는 최종 선정 후보와 운영 기준이 연결됐는지 다시 확인할 수 있다.

## 아직 남아 있는 것

- 사용자 manual QA checklist 확인
- Phase35 이후 optional extension 방향 결정

## closeout 판단

현재 Phase 35는 `implementation_complete / manual_qa_pending` 상태다.
사용자가 `PHASE35_TEST_CHECKLIST.md`를 확인한 뒤 완료를 알려주면 closeout할 수 있다.
