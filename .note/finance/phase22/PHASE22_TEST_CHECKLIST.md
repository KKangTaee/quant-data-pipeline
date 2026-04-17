# Phase 22 Test Checklist

## 목적

- 이 checklist는 `Phase 22`가 practical closeout에 가까워졌을 때 사용자가 직접 QA하기 위한 초안이다.
- 현재 Phase 22는 막 시작된 상태이므로,
  아래 항목은 최종 체크리스트가 아니라 앞으로 채워질 검수 기준이다.

## 사용 방법

- 실제 portfolio-level validation report가 만들어진 뒤 이 checklist를 다시 정리한다.
- 사용자는 최종 handoff 때 아래 항목을 `[ ]`에서 `[x]`로 바꾸며 확인한다.
- 모든 주요 항목이 완료되기 전에는 다음 major phase로 넘어가지 않는 것을 기본으로 한다.

## 1. Portfolio-Level Candidate 기준 확인

### 확인 위치

| 문서 | 확인할 내용 |
|---|---|
| [PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md) | Phase 22 목적과 범위 |
| [PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md) | portfolio 후보의 정의와 최소 기록 항목 |
| [FINANCE_TERM_GLOSSARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_TERM_GLOSSARY.md) | 반복 용어 설명 |

### 체크 항목

- [ ] `Portfolio-Level Candidate`가 단순 weighted result가 아니라 재현 가능한 후보 기록이라는 점이 이해되는지
- [ ] component strategy, weight, date alignment, saved replay가 왜 필요한지 설명되어 있는지
- [ ] 유지 / 교체 / 보류 판단 기준이 숫자만이 아니라 해석까지 포함하는지

## 2. Representative Portfolio Candidate Pack 확인

### 확인 위치

- 추후 생성될 Phase 22 portfolio-level validation report
- `Backtest > Compare & Portfolio Builder`
- `Weighted Portfolio Builder`
- `Saved Portfolios > Replay Saved Portfolio`

### 체크 항목

- [ ] 어떤 component strategy가 portfolio candidate에 들어갔는지 보이는지
- [ ] weight와 date alignment가 명확히 기록되어 있는지
- [ ] baseline portfolio와 대안 portfolio를 같은 frame에서 비교했는지

## 3. Saved Replay와 Report 확인

### 확인 위치

- 추후 생성될 Phase 22 portfolio-level validation report
- `.note/finance/backtest_reports/` index
- `.note/finance/phase22/PHASE22_CURRENT_CHAPTER_TODO.md`

### 체크 항목

- [ ] saved portfolio replay가 주요 결과를 재현하는지
- [ ] report에서 "최종 후보", "baseline", "watchlist", "comparison-only" 같은 해석이 분명한지
- [ ] 아직 확인하지 않은 한계가 report에 따로 적혀 있는지

## 4. Closeout / Handoff 확인

### 확인 문서

- [PHASE22_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_CURRENT_CHAPTER_TODO.md)
- [PHASE22_COMPLETION_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_COMPLETION_SUMMARY.md)
- [PHASE22_NEXT_PHASE_PREPARATION.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_NEXT_PHASE_PREPARATION.md)
- [MASTER_PHASE_ROADMAP.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/MASTER_PHASE_ROADMAP.md)
- [FINANCE_DOC_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_DOC_INDEX.md)

### 체크 항목

- [ ] Phase 22 상태가 실제 진행 상태와 맞는지
- [ ] 새 Phase 22 문서들이 index에서 바로 찾히는지
- [ ] 다음 phase로 갈지, Phase 22에서 portfolio construction을 더 볼지 판단 근거가 남아 있는지

## 한 줄 판단 기준

- 이 checklist는 **"weighted portfolio를 재현 가능한 portfolio-level candidate로 읽을 기준과 결과가 충분히 정리됐는가"**를 확인하는 문서다.
