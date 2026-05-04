# Phase 35 Completion Summary

## 현재 상태

- 진행 상태: `implementation_complete`
- 검증 상태: `manual_qa_pending`

Phase 35 구현은 완료됐고, 사용자 manual QA handoff 단계다.

## 목적

Phase 35 `Post-Selection Guide`는
Phase 34에서 기록한 최종 판단을 다시 읽어
사용자가 마지막에 투자 가능성 및 운영 전 지침을 확인하는 phase다.

## 쉽게 말하면

Phase 34가 "이 후보를 최종 후보로 선정 / 보류 / 거절 / 재검토할지 기록"하는 단계라면,
Phase 35는 "그 기록을 보고 실제 투자 후보로 볼 수 있는지 마지막으로 읽는 화면"이다.

이 phase는 새 저장소를 만들지 않는다.
최종 판단의 원본은 Final Review에서 저장한 final selection decision이다.

## 이번 phase에서 완료된 것

### 1. Phase kickoff

- Phase 34 checklist 완료 신호를 반영해 Phase 34를 closeout했다.
- Phase 35 문서 bundle을 `.note/finance/phases/phase35/` 아래에 생성했다.
- Phase 35 목표를 Final Review 이후 마지막 확인 surface로 정리했다.

### 2. Final investment guide 계약 정의

- Phase35 입력은 `SELECT_FOR_PRACTICAL_PORTFOLIO` final review record로 제한했다.
- 신규 final decision row는 `READY_FOR_FINAL_INVESTMENT_GUIDE` handoff로 읽는다.
- 기존 QA row의 `READY_FOR_POST_SELECTION_OPERATING_GUIDE` handoff도 backward compatibility로 읽는다.
- 최종 판단 문구를 사용자 기준으로 바꿨다.
  - 투자 가능 후보
  - 내용 부족 / 관찰 필요
  - 투자하면 안 됨
  - 재검토 필요

### 3. No-extra-save 경계 보정

- Phase35에서 별도 `POST_SELECTION_OPERATING_GUIDES.jsonl` 저장소를 쓰지 않게 했다.
- `app/web/runtime/post_selection_guides.py` helper를 제거했다.
- `Backtest > Post-Selection Guide`에서 `운영 가이드 기록` / saved guide review UX를 제거했다.
- Final Review의 final decision registry를 최종 판단 원본으로 유지했다.

### 4. Final guide preview UI

- `Backtest > Post-Selection Guide` workflow panel을 유지했다.
- Final Review record table에서 `투자 가능성`을 표시한다.
- selected final decision의 component, evidence, Phase35 handoff를 확인할 수 있다.
- Capital Mode, Rebalancing Cadence, 리밸런싱 / 축소 / 중단 / 재검토 기준은 preview로 확인한다.
- readiness route는 `FINAL_INVESTMENT_GUIDE_READY`, `FINAL_INVESTMENT_GUIDE_NEEDS_INPUT`, `FINAL_INVESTMENT_GUIDE_BLOCKED`로 읽힌다.

### 5. Handoff와 QA 문서

- checklist를 저장 확인이 아니라 최종 투자 가능성 / no-extra-save / 실행 경계 확인 중심으로 바꿨다.
- operations guide를 `POST_SELECTION_FINAL_INVESTMENT_GUIDE.md`로 보정했다.
- code analysis, roadmap, doc index, comprehensive analysis, glossary, work log, question log를 현재 구현과 맞췄다.

## 아직 남아 있는 것

- 사용자 manual QA checklist 확인
- Phase35 이후 optional extension 방향 결정

## closeout 판단

현재 Phase 35는 `implementation_complete / manual_qa_pending` 상태다.
사용자가 `PHASE35_TEST_CHECKLIST.md`를 확인한 뒤 완료를 알려주면 closeout할 수 있다.
