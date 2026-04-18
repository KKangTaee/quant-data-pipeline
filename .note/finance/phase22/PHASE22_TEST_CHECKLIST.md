# Phase 22 Test Checklist

## 목적

- 이 checklist는 `Phase 22`의 portfolio-level candidate construction 결과를 사용자가 직접 QA하기 위한 문서다.
- 현재 Phase 22는 baseline candidate pack, benchmark / guardrail policy, weight alternative rerun까지 작성된 상태다.
- 사용자는 아래 항목을 보며 문서와 UI 흐름이 이해되는지 확인하면 된다.

## 먼저 확인할 전제

- `Phase 22`는 실전 투자 포트폴리오를 확정하는 단계가 아니다.
- `Value / Quality / Quality + Value` 3개는 최종 투자 조합이라서 쓴 것이 아니라,
  포트폴리오 구성 / 저장 / replay / 비교 기능을 검증하기 좋은 대표 fixture로 쓴 것이다.
- 여기서 말하는 `equal-third baseline`은 투자 benchmark가 아니라
  같은 fixture 조합의 weight alternative를 비교하기 위한 개발 검증용 기준이다.
- 따라서 QA의 핵심은 "이 포트폴리오로 투자해도 되는가"가 아니라
  "프로그램이 포트폴리오 구성 workflow를 재현 가능하게 다루는가"다.

## 사용 방법

- 새 portfolio-level validation report가 추가될 때마다 이 checklist를 같이 정리한다.
- 사용자는 최종 handoff 때 아래 항목을 `[ ]`에서 `[x]`로 바꾸며 확인한다.
- 모든 주요 항목이 완료되기 전에는 다음 major phase로 넘어가지 않는 것을 기본으로 한다.

## 1. Portfolio-Level Candidate 기준 확인

### 이 항목에서 확인하려는 것

여기서는 "포트폴리오 후보"라는 말이 그냥 weighted portfolio 결과표를 뜻하는지,
아니면 source / weight / replay / 해석이 남은 재현 가능한 후보 기록을 뜻하는지 확인한다.

또한 이 후보가 실전 투자 승인 후보가 아니라,
현재 개발 중인 포트폴리오 구성 기능을 검증하기 위한 기록이라는 점도 함께 확인한다.

### 확인 위치

| 문서 | 확인할 내용 |
|---|---|
| [PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md) | `목적: 쉽게 말하면`, `왜 필요한가`, `Portfolio-Level Candidate로 인정하는 최소 조건` |
| [PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md) | `기본 정의`, `Portfolio-Level Candidate 최소 기록 항목`, `후보 판단 규칙 초안` |
| [FINANCE_TERM_GLOSSARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_TERM_GLOSSARY.md) | `Portfolio-Level Candidate`, `Portfolio Bridge`, `Saved Portfolio Replay`, `Date Alignment` 용어 |

### 체크 방법

1. plan 문서에서 Phase 22가 "전략 3개를 섞은 결과를 바로 최종 후보로 정하는 phase가 아니다"라고 설명하는지 본다.
2. first work unit 문서에서 portfolio 후보가 되려면 `component`, `source`, `period`, `universe`, `weight`, `date alignment`, `replay`, `interpretation`이 필요하다고 설명하는지 본다.
3. 유지 / 교체 / 보류 판단이 단순히 CAGR이 높은 순서가 아니라, 재현성과 위험 해석까지 같이 보는 구조인지 확인한다.

### 체크 항목

- [x] `Portfolio-Level Candidate`가 단순 weighted result가 아니라 재현 가능한 후보 기록이라는 점이 plan 문서에서 이해되는지
- [x] first work unit의 최소 기록 항목을 보면 component strategy, weight, date alignment, saved replay가 왜 필요한지 확인할 수 있는지
- [x] 유지 / 교체 / 보류 판단 기준이 숫자만이 아니라 재현성, component status, 위험 해석까지 포함하는지
- [ ] Phase 22가 실전 투자 포트폴리오 확정이 아니라 개발 검증용 portfolio workflow 정리라는 점이 명확히 보이는지

## 2. Representative Portfolio Candidate Pack 확인

### 확인 위치

- [PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md)
- [phase22/README.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase22/README.md)
- `Backtest > Compare & Portfolio Builder`
- `Weighted Portfolio Builder`
- `Saved Portfolios > Replay Saved Portfolio`

### 체크 항목

- [x] 어떤 component strategy가 portfolio candidate에 들어갔는지 보이는지
- [x] `33 / 33 / 34` 표현과 저장된 `[33.33, 33.33, 33.33]` weight의 차이가 헷갈리지 않게 설명되어 있는지
- [x] baseline weight policy가 `equal-third baseline`으로 명확히 기록되어 있는지
- [ ] `equal-third baseline`이 투자 기준이 아니라 개발 검증용 비교 기준이라는 점이 명확히 보이는지
- [x] Phase 21의 `33 / 33 / 34` 결과와 Phase 22의 `[33.33, 33.33, 33.33]` 공식 baseline 수치가 구분되어 있는지
- [x] date alignment가 `intersection`으로 명확히 기록되어 있는지
- [x] baseline portfolio는 유지됐지만, 최종 deployment 후보가 아니라 `portfolio_watchlist`라는 점이 보이는지

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
- [ ] 다음 기본 방향이 portfolio optimization 확대가 아니라 Phase 23 core implementation이라는 점이 보이는지
- [ ] 사용자가 별도로 분석을 요청할 경우에는 백테스트 / 분석을 수행할 수 있지만,
      기본 phase 방향은 개발 검증이라는 점이 구분되어 있는지

## 한 줄 판단 기준

- 이 checklist는 **"weighted portfolio를 재현 가능한 portfolio-level candidate로 읽을 기준과 결과가 충분히 정리됐는가"**를 확인하는 문서다.
