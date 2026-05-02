# Phase 20 Test Checklist

## 목적

- `Phase 20`에서 정리한 candidate consolidation / operator workflow hardening이
  실제 UI에서 자연스럽게 이어지는지 확인한다.
- 이번 checklist는
  "새 후보가 더 추가됐는가"보다
  **현재 후보를 다시 꺼내고, compare하고, 저장하고, 다시 이어 쓰는 흐름이 편해졌는가**
  를 보는 데 초점을 둔다.

## 사용 방법

- 아래 항목은 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 주요 체크 항목이 모두 완료된 뒤 다음 major phase로 넘어간다.
- 일부 항목을 보류하면 그 이유를 이 문서나 handoff에 짧게 남긴다.

## 현재 UI 이름 기준

- 이 checklist는 **현재 화면에 실제로 보이는 이름** 기준으로 읽는다.
- 예전 대화에서 쓰던 이름과 현재 UI 이름이 다를 수 있으니, 아래 대응표를 먼저 보고 테스트하면 덜 헷갈린다.

| 예전 표현 | 현재 UI에서 볼 이름 |
| --- | --- |
| `Current Candidate Re-entry` | `Quick Re-entry From Current Candidates` |
| `Load Current Anchors` | `Load Recommended Candidates` |
| `Load Lower-MDD Near Misses` | `Load Lower-MDD Alternatives` |
| `Inspect Current Candidate Bundle Options` | `Pick Manually` 탭 안의 후보 목록 |
| `Load Selected Candidates Into Compare` | `Load Selected Candidates Into Compare` |
| `What Changed In Compare` | `Compare Form Updated` |
| `Current Compare Bundle` | `What You Are Combining` |

## 테스트할 때 보는 순서

1. 먼저 **현재 화면에 보이는 제목 이름**을 기준으로 찾는다.
2. 예전 이름이 기억나면 바로 위 대응표에서 현재 이름으로 바꿔 읽는다.
3. 버튼을 눌렀을 때
   - 화면 상단 안내 카드 이름
   - section 제목
   - 표 제목
   이 현재 checklist와 같은지 확인한다.

## 추천 실행 순서

1. current candidate를 compare로 다시 불러오는 흐름 확인
2. compare -> weighted portfolio 흐름 확인
3. saved portfolio 재진입 흐름 확인
4. phase closeout 문서와 index 확인

## 1. current candidate re-entry 확인

- 확인 위치:
  - `Backtest > Compare & Portfolio Builder`
  - `Strategies` 바로 아래 `Quick Re-entry From Current Candidates`
- 체크 항목:
  - [x] `Quick Re-entry From Current Candidates` 섹션이 보이는지
  - [x] `Quick Bundles` 탭과 `Pick Manually` 탭이 보이는지
  - [x] `Load Recommended Candidates`와 `Load Lower-MDD Alternatives` quick action이 보이는지
  - [x] `Pick Manually` 탭 안에서 후보 제목, family, 역할, contract 요약이 읽기 쉽게 보이는지
  - [x] 여러 후보를 직접 선택해서 `Load Selected Candidates Into Compare`를 누를 수 있는지
  - [x] 불가능한 조합일 때 왜 막히는지 안내 문구가 이해되게 보이는지
  - [x] current candidate를 불러온 뒤 `Compare Form Updated`가 보이고, compare form에 strategy/period/override가 자연스럽게 채워지는지
  - [x] `Compare Form Updated` 카드에서 무엇이 바뀌었는지와 어디를 확인하면 되는지가 이해되는지

## 2. compare -> weighted portfolio 흐름 확인

- 확인 위치:
  - `Backtest > Compare & Portfolio Builder`
  - compare 실행 후 `Strategy Comparison` 아래
  - divider 아래 `Weighted Portfolio Builder`
- 체크 항목:
  - [x] compare를 실행한 뒤 `Weighted Portfolio Builder` 위에 `What You Are Combining` 요약이 보이는지
  - [x] `What You Are Combining`에서 `들어온 경로`, `묶음 이름`, `비교 기간`, `조합할 전략 수`가 현재 compare 맥락과 맞게 보이는지
  - [x] 그 아래 전략 표에서 `Strategy`, `Period`, `CAGR`, `MDD`, `Promotion`이 보여서 지금 무엇을 섞는지 한 번에 이해되는지
  - [x] registry 기반 current candidate를 compare로 불러왔을 때 registry ids 또는 source 정보가 요약에 보이는지
  - [x] `Strategy Comparison`과 `Weighted Portfolio Builder` 사이에 divider가 보여 두 단계가 시각적으로 나뉘는지
  - [x] weighted portfolio를 만들 때 compare source 맥락을 잃지 않고 바로 이어서 저장할 수 있는지
  - [x] weighted portfolio 결과가 생성된 뒤 다음 행동이 자연스럽게 이해되는지

## 3. saved portfolio 재진입 흐름 확인

- 확인 위치:
  - `Backtest > Compare & Portfolio Builder`
  - `Weighted Portfolio Builder` 아래 divider 다음 `Saved Portfolios`
- 체크 항목:
  - [x] `Weighted Portfolio Builder`와 `Saved Portfolios` 사이에 divider가 보여 두 단계가 시각적으로 나뉘는지
  - [x] `Save This Weighted Portfolio`를 열었을 때 `Portfolio Name`이 추천 이름과 함께 자연스럽게 보이고, 그 이름이 source label 또는 strategy 조합 기준으로 이해되는지
  - [x] 저장된 포트폴리오 목록에 `Source` 컬럼이 보이는지
  - [x] 저장된 포트폴리오 상세에서 `Source & Next Step` 탭이 보이는지
  - [x] `Source & Next Step` 탭에서 이 포트폴리오가 어디서 왔는지와 다음 행동이 쉽게 읽히는지
  - [x] `Load Saved Setup Into Compare`를 누르면 compare 화면 상단으로 이동하고, `Compare Form Updated`와 `Weighted Portfolio Builder`에서 전략 조합/기간/세부 설정/weights/date alignment가 다시 채워진 것을 확인할 수 있는지
  - [x] `Replay Saved Portfolio`를 누르면 저장된 compare context와 weighted portfolio 구성을 그대로 다시 실행하는지
  - [x] saved portfolio를 다시 열었을 때 "수정할지 / 그대로 재실행할지" 판단이 더 쉬워졌는지

## 4. phase closeout 문서와 index 확인

- 확인 문서:
  - [PHASE20_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase20/PHASE20_CURRENT_CHAPTER_TODO.md)
  - [PHASE20_COMPLETION_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase20/PHASE20_COMPLETION_SUMMARY.md)
  - [PHASE20_NEXT_PHASE_PREPARATION.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase20/PHASE20_NEXT_PHASE_PREPARATION.md)
  - [PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase20/PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md)
  - [PHASE20_CURRENT_CANDIDATE_COMPARE_REENTRY_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase20/PHASE20_CURRENT_CANDIDATE_COMPARE_REENTRY_FIRST_WORK_UNIT.md)
  - [PHASE20_COMPARE_WEIGHTED_AND_SAVED_REENTRY_HARDENING_SECOND_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase20/PHASE20_COMPARE_WEIGHTED_AND_SAVED_REENTRY_HARDENING_SECOND_WORK_UNIT.md)
  - [FINANCE_DOC_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_DOC_INDEX.md)
  - [MASTER_PHASE_ROADMAP.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/MASTER_PHASE_ROADMAP.md)
- 체크 항목:
  - [x] Phase 20 상태가 `phase complete / manual_validation_completed`로 보이는지
  - [x] Phase 20 first/second work-unit, completion summary, next preparation, checklist 문서를 index에서 바로 찾을 수 있는지
  - [x] roadmap에 Phase 20가 operator workflow hardening closeout 기준으로 반영됐는지
  - [x] completion summary가 "무엇이 쉬워졌는지"를 쉽게 설명하는지
  - [x] next phase preparation 문서가 다음 질문을 이해하기 쉽게 정리하는지

## 한 줄 판단 기준

- 이번 checklist는
  "기능이 더 많아졌는가"보다,
  **현재 후보를 다시 보고 비교하고 저장하고 다시 이어 쓰는 흐름이 실제로 더 자연스러워졌는가**
  를 확인하는 checklist다.
