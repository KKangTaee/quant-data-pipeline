# Phase 18 Test Checklist

## 목적

- 이번 checklist는 `Phase 18` larger structural redesign first slice가
  UI / history / 문서 / rerun report 기준으로 다시 읽히는지 확인하는 문서다.
- 이번 checklist는
  **next-ranked fill contract가 실제로 연결되었는지와,
  왜 current anchor replacement가 아니었는지 이해되는지**
  를 보는 데 초점을 둔다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 주요 체크 항목이 모두 완료된 뒤 다음 major phase로 넘어간다.
- 일부 항목을 나중으로 미루면 그 이유를 문서나 handoff에 짧게 남긴다.

## 추천 실행 순서

1. strict annual UI에서 next-ranked fill contract 확인
2. representative rerun / follow-up report 확인
3. strategy hub / candidate summary / roadmap closeout 확인

## 1. strict annual UI에서 next-ranked fill contract 확인

- 확인 위치:
  - `Backtest > Single Strategy > Value / Quality + Value > Strict Annual`
  - `Backtest > Compare > strict annual family override`
- 체크 항목:
  - [ ] `Fill Rejected Slots With Next Ranked Names` 또는 그에 대응하는 handling contract가 UI에서 다시 보이는지
  - [ ] trend rejection 이후 빈 슬롯을 다음 ranked name으로 채우는 구조라는 설명이 문서나 tooltip에서 읽히는지
  - [ ] history / load-into-form / compare prefill에서도 같은 contract가 다시 복원되는지

## 2. representative rerun / follow-up report 확인

- 확인 문서:
  - [PHASE18_NEXT_RANKED_FILL_REPRESENTATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase18/PHASE18_NEXT_RANKED_FILL_REPRESENTATIVE_RERUN_FIRST_PASS.md)
  - [PHASE18_VALUE_FILL_ANCHOR_NEAR_FOLLOWUP_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase18/PHASE18_VALUE_FILL_ANCHOR_NEAR_FOLLOWUP_SECOND_PASS.md)
- 체크 항목:
  - [ ] `Value`에서 redesign evidence는 있었지만 current anchor replacement는 아니었다는 해석이 보이는지
  - [ ] `Quality + Value`에서 개선은 있었지만 still `hold / blocked`였다는 해석이 보이는지
  - [ ] 보고서가 "실패한 실험"이 아니라 "meaningful redesign evidence"라는 맥락으로 읽히는지

## 3. strategy hub / candidate summary / phase closeout 확인

- 확인 문서:
  - [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
  - [PHASE18_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase18/PHASE18_CURRENT_CHAPTER_TODO.md)
  - [PHASE18_COMPLETION_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase18/PHASE18_COMPLETION_SUMMARY.md)
  - [PHASE18_NEXT_PHASE_PREPARATION.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase18/PHASE18_NEXT_PHASE_PREPARATION.md)
  - [MASTER_PHASE_ROADMAP.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/MASTER_PHASE_ROADMAP.md)
  - [FINANCE_DOC_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_DOC_INDEX.md)
- 체크 항목:
  - [ ] `Phase 18`이 practical closeout / manual validation pending 상태로 읽히는지
  - [ ] second-slice backlog가 immediate blocker가 아니라 future backlog로 정리되어 있는지
  - [ ] 다음 자연스러운 main phase가 `Phase 21` deep validation이라는 점이 문서에서 읽히는지
  - [ ] 새 closeout / next-phase / checklist 문서가 index에서 바로 찾히는지

## 한 줄 판단 기준

- 이번 checklist는
  **"next-ranked fill first slice가 실제로 연결되었고, 왜 여기서 current anchor를 바로 교체하지 않고 Phase 21 deep validation으로 넘어가는지 이해되는가"**
  를 확인하는 문서다.
