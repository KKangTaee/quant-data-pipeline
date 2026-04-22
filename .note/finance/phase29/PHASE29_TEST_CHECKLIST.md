# Phase 29 Test Checklist

## 목적

이 checklist는 Phase 29에서 추가한 `Candidate Review` 화면이
current candidate를 검토 보드로 읽고 compare / Pre-Live Review로 자연스럽게 넘기는지 확인하기 위한 문서다.

현재는 Phase 29 first work unit QA checklist다.
이 문서의 항목을 확인한 뒤 다음 작업 단위로 넘어갈지 판단한다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 주요 체크 항목이 완료된 뒤 다음 작업 단위로 넘어간다.
- checklist에는 별도 `용어 기준` 섹션을 만들지 않는다.
- 용어 설명이 필요하면 각 체크 항목 안에 `어디서 무엇을 어떻게 확인하는지`를 직접 적는다.

## 1. Candidate Review panel 확인

- 확인 위치:
  - `Backtest > Candidate Review`
- 체크 항목:
  - [ ] `Candidate Review` panel이 `Backtest` 상단 panel 선택지에 보이는지
  - [ ] 화면 상단 설명이 이 화면을 live trading 승인이나 최종 투자 판단으로 오해하지 않게 설명하는지
  - [ ] `Active Candidates`, `Current Anchors`, `Near Miss / Scenario`, `Pre-Live Records` metric이 보이는지
  - [ ] `How To Use Candidate Review` 안내를 열었을 때 compare / Pre-Live Review로 넘어가는 역할이 이해되는지

## 2. Candidate Board 확인

- 확인 위치:
  - `Backtest > Candidate Review > Candidate Board`
- 체크 항목:
  - [ ] current candidate registry의 active 후보들이 표로 보이는지
  - [ ] `Review Stage`가 current anchor, near miss, scenario 후보를 구분하는 데 도움이 되는지
  - [ ] `Why It Exists`가 후보가 왜 남아 있는지 쉽게 설명하는지
  - [ ] `Suggested Next Step`이 투자 추천이 아니라 다음 검토 행동 제안으로 읽히는지
  - [ ] CAGR / MDD / Promotion / Shortlist / Deployment가 한 행에서 같이 보여 후보 상태를 읽기 쉬운지

## 3. Inspect Candidate 확인

- 확인 위치:
  - `Backtest > Candidate Review > Inspect Candidate`
- 체크 항목:
  - [ ] 후보를 선택하면 detail card에 title, review stage, CAGR, MDD, promotion, shortlist가 보이는지
  - [ ] `Suggested Next Step`과 `Contract Summary`가 후보를 compare할지 Pre-Live로 넘길지 판단하는 데 도움이 되는지
  - [ ] `Raw Candidate Registry Row`를 열면 원본 registry row를 확인할 수 있는지
  - [ ] `Open Candidate In Pre-Live Review` 버튼 이름이 저장/승인 버튼으로 오해되지 않는지

## 4. Candidate Review -> Pre-Live Review 흐름 확인

- 확인 위치:
  - `Backtest > Candidate Review > Inspect Candidate`
  - `Open Candidate In Pre-Live Review`
  - 이동 후 `Backtest > Pre-Live Review`
- 체크 항목:
  - [ ] 버튼을 누르면 `Pre-Live Review` panel로 이동하는지
  - [ ] 이동 후 선택한 후보가 `Candidate To Review`에 유지되는지
  - [ ] 상단 안내문이 아직 저장된 것이 아니라 운영 상태와 next action을 확인해야 한다고 설명하는지
  - [ ] `Save Pre-Live Record`를 누르기 전까지 registry에 저장된 것으로 오해되지 않는지

## 5. Candidate Review -> Compare 흐름 확인

- 확인 위치:
  - `Backtest > Candidate Review > Send To Compare`
- 체크 항목:
  - [ ] `Load Recommended Candidates`가 대표 후보 묶음을 compare form에 채우는 기능으로 이해되는지
  - [ ] `Load Lower-MDD Alternatives`가 near-miss 대안을 compare form에 채우는 기능으로 이해되는지
  - [ ] `Pick Manually`에서 후보를 직접 고르고 `Load Selected Candidates Into Compare`를 누를 수 있는지
  - [ ] compare panel로 이동한 뒤 `Compare Form Updated`에서 어떤 후보가 채워졌는지 확인할 수 있는지

## 6. 문서와 상태 확인

- 확인 문서:
  - `.note/finance/phase29/PHASE29_CANDIDATE_REVIEW_AND_RECOMMENDATION_WORKFLOW_PLAN.md`
  - `.note/finance/phase29/PHASE29_CANDIDATE_REVIEW_BOARD_FIRST_WORK_UNIT.md`
  - `.note/finance/phase29/PHASE29_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 29가 최종 투자 승인 phase가 아니라 후보 검토 workflow phase로 설명되는지
  - [ ] Phase 29 상태가 `active / manual_qa_pending`으로 읽히는지
  - [ ] 다음 작업 후보가 Latest / History result to candidate handoff 쪽으로 이어지는지

## 한 줄 판단 기준

이번 checklist는
**좋은 후보를 추천으로 확정했는가**가 아니라,
**후보를 먼저 이해하고 compare 또는 Pre-Live Review로 넘기는 길이 자연스러운가**
를 확인하는 문서다.
