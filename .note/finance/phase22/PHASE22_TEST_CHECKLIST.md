# Phase 22 Test Checklist

## 목적

- 이 checklist는 `Phase 22`의 portfolio-level candidate construction 결과를 사용자가 직접 QA하기 위한 문서다.
- 현재 Phase 22는 baseline candidate pack, benchmark / guardrail policy, weight alternative rerun까지 작성된 상태다.
- 사용자는 아래 항목을 보며 문서와 UI 흐름이 이해되는지 확인하면 된다.

## 사용 방법

- 새 portfolio-level validation report가 추가될 때마다 이 checklist를 같이 정리한다.
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

- [PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md)
- [phase22/README.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase22/README.md)
- `Backtest > Compare & Portfolio Builder`
- `Weighted Portfolio Builder`
- `Saved Portfolios > Replay Saved Portfolio`

### 체크 항목

- [ ] 어떤 component strategy가 portfolio candidate에 들어갔는지 보이는지
- [ ] `33 / 33 / 34` 표현과 저장된 `[33.33, 33.33, 33.33]` weight의 차이가 헷갈리지 않게 설명되어 있는지
- [ ] baseline weight policy가 `equal-third baseline`으로 명확히 기록되어 있는지
- [ ] Phase 21의 `33 / 33 / 34` 결과와 Phase 22의 `[33.33, 33.33, 33.33]` 공식 baseline 수치가 구분되어 있는지
- [ ] date alignment가 `intersection`으로 명확히 기록되어 있는지
- [ ] baseline portfolio는 유지됐지만, 최종 deployment 후보가 아니라 `portfolio_watchlist`라는 점이 보이는지

## 3. Saved Replay와 Report 확인

### 확인 위치

- [PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md)
- `.note/finance/backtest_reports/` index
- `.note/finance/phase22/PHASE22_CURRENT_CHAPTER_TODO.md`

### 체크 항목

- [ ] saved portfolio replay가 주요 결과를 재현하는지
- [ ] report에서 "최종 후보"가 아니라 `baseline_candidate / portfolio_watchlist / not_deployment_ready`라는 해석이 분명한지
- [ ] 아직 확인하지 않은 한계가 report에 따로 적혀 있는지

## 4. Portfolio Benchmark / Guardrail / Weight Scope 확인

### 확인 위치

- [PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md)
- [FINANCE_TERM_GLOSSARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_TERM_GLOSSARY.md)

### 체크 항목

- [ ] portfolio 후보의 1차 benchmark가 `SPY`가 아니라 equal-third baseline이라는 설명이 이해되는지
- [ ] `SPY`는 market context이고, component benchmark는 component 품질 해석으로만 남는다는 점이 보이는지
- [ ] portfolio-level guardrail이 아직 actual trading rule이 아니라 report-level warning이라는 점이 이해되는지
- [ ] 다음 weight alternative가 `25 / 25 / 50`과 `40 / 40 / 20` 두 개로 좁혀진 이유가 보이는지

## 5. Weight Alternative Rerun 확인

### 확인 위치

- [PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase22/PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md)
- [PHASE22_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_CURRENT_CHAPTER_TODO.md)

### 체크 항목

- [ ] `equal-third baseline`, `25 / 25 / 50`, `40 / 40 / 20` 세 후보가 같은 frame에서 비교되는지
- [ ] `25 / 25 / 50`은 CAGR은 높지만 `Quality + Value` 편중이 커서 baseline 교체가 아니라 watch alternative로 남긴 이유가 이해되는지
- [ ] `40 / 40 / 20`은 MDD가 조금 낮아지지만 CAGR을 포기해서 baseline 교체가 아닌 comparison-only 후보로 남긴 이유가 이해되는지
- [ ] 현재 결론이 `baseline 유지 / alternative 보류 / immediate replacement 없음`으로 분명한지
- [ ] 두 weight alternative는 아직 별도 saved portfolio UI replay까지 한 것이 아니라, saved compare context를 code runner로 재실행한 scripted rerun이라는 점이 보이는지

## 6. Closeout / Handoff 확인

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
