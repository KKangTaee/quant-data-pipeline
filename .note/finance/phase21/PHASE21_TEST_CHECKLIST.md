# Phase 21 Test Checklist

## 이 checklist의 목적

이 문서는 `Phase 21`에서 수행한 integrated deep validation을 사용자가 직접 확인하기 위한 QA 문서다.

이번 phase에서 확인할 핵심은 UI 디자인이 아니라 다음 4가지다.

1. 같은 기준표에서 후보를 다시 검증했는가
2. `Value`, `Quality`, `Quality + Value` family의 current anchor 판단이 문서에 일관되게 남았는가
3. weighted / saved portfolio workflow가 재현 가능하게 작동했는가
4. `Phase 22`로 넘어갈 근거가 문서에 충분히 정리되었는가

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 주요 체크 항목이 모두 완료된 뒤 다음 major phase로 넘어간다.
- 일부 항목을 나중으로 미루면 그 이유를 문서나 handoff에 짧게 남긴다.

## 추천 확인 순서

| 순서 | 확인 영역 | 핵심 질문 |
|---:|---|---|
| 1 | Validation Frame | 모두 같은 기준에서 비교했는가 |
| 2 | Family별 rerun 결과 | current anchor 유지 / 교체 / 보류 판단이 가능한가 |
| 3 | Portfolio Bridge | weighted / saved portfolio workflow가 재현되는가 |
| 4 | Closeout / Handoff | Phase 22로 넘어갈 근거가 정리됐는가 |

---

## 1. Validation Frame 확인

### 무엇을 확인하나

`Phase 21`에서 여러 후보를 비교하기 전에 기간, universe, 후보 묶음, 결과 기록 위치를 먼저 고정했는지 확인한다.

여기서 `Validation Frame`은 "여러 후보를 같은 조건에서 비교하기 위해 미리 고정해 두는 검증 기준표"라는 뜻이다.

### 어디서 확인하나

| 문서 | 확인할 내용 |
|---|---|
| [FINANCE_TERM_GLOSSARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_TERM_GLOSSARY.md) | `Validation Frame` 뜻 |
| [PHASE21_INTEGRATED_DEEP_BACKTEST_VALIDATION_PLAN.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_INTEGRATED_DEEP_BACKTEST_VALIDATION_PLAN.md) | Phase 21 목적과 전체 방향 |
| [PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md) | 기간, universe, candidate pack, report naming |
| [PHASE21_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_CURRENT_CHAPTER_TODO.md) | 작업 상태와 완료 여부 |

### 체크 항목

- [x] `Validation Frame`이 "여러 후보를 같은 조건에서 비교하기 위해 미리 고정해 두는 검증 기준표"라는 뜻으로 이해되는지
- [x] 이번 phase에서 다시 볼 family와 candidate 범위가 문서에 분명히 적혀 있는지
- [x] 공통 기간(`2016-01-01 ~ 2026-04-01`)과 공통 universe frame(`US Statement Coverage 100`, `Historical Dynamic PIT Universe`)이 분명히 적혀 있는지
- [x] current anchor / lower-MDD alternative / portfolio bridge가 무엇인지 용어 설명이 충분한지
- [x] family별 rerun report 이름과 strategy log entry naming rule이 먼저 정리되어 있는지
- [x] rerun 결과를 어디에 남길지 기준이 보이는지

---

## 2. Family별 Integrated Rerun 결과 확인

### 무엇을 확인하나

`Value`, `Quality`, `Quality + Value` family에서 current anchor를 유지할지, 대안으로 교체할지, 아니면 보류할지 판단할 수 있을 만큼 결과와 해석이 정리되어 있는지 확인한다.

### 어디서 확인하나

먼저 Phase 21 archive 목차를 열고, family별 report 3개를 순서대로 확인한다.

| family | 이번 phase report | 장기 기록 확인 문서 |
|---|---|---|
| `Value` | [Value rerun report](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md) | [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md), [VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md) |
| `Quality` | [Quality rerun report](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md) | [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md), [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md) |
| `Quality + Value` | [Quality + Value rerun report](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md) | [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md), [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md) |

전체 archive 안내는 [phase21/README.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/README.md)에서 확인한다.

### 판단 기준

| 판단 | 무엇을 보면 되는가 |
|---|---|
| 유지 | current anchor가 여전히 가장 안정적인 기준점이고, 대안이 gate나 해석 면에서 더 강하지 않을 때 |
| 교체 | 대안이 `CAGR / MDD`를 개선하면서 `Promotion / Shortlist / Deployment`도 current anchor와 같거나 더 강할 때 |
| 보류 | 대안이 일부 지표는 좋지만 `hold`, `blocked`, `paper_only`, `weaker-gate`, `near-miss`, `comparison-only` 해석이 남을 때 |

확인할 때는 `CAGR / MDD`만 보지 말고 `Promotion`, `Shortlist`, `Deployment`, `Validation / Rolling Review / Out-of-Sample Review`, report의 `해석`, backtest log의 `다음 액션`을 함께 본다.

### 체크 항목

- [x] `Value` current anchor와 lower-MDD alternative rerun 결과를 같은 frame에서 비교할 수 있는지
- [x] `Quality` current anchor와 alternative rerun 결과를 같은 frame에서 비교할 수 있는지
- [x] `Quality + Value` strongest point와 alternative rerun 결과를 같은 frame에서 비교할 수 있는지
- [x] 결과를 보고 유지 / 교체 / 보류 판단이 가능한 정도로 해석이 적혀 있는지

---

## 3. Portfolio Bridge Validation 확인

### 무엇을 확인하나

weighted / saved portfolio 기능이 실제 current candidate workflow와 연결되어 재현 가능한지 확인한다.

중요한 점은, 이 검증이 최종 portfolio winner를 고르는 검증이 아니라는 것이다. 이번 검증은 `Load Recommended Candidates -> Weighted Portfolio Builder -> Save Portfolio -> Replay Saved Portfolio` 흐름이 실제로 쓸 수 있는지 확인한 첫 검증이다.

### 어디서 확인하나

| 구분 | 확인 위치 | 무엇을 본다 |
|---|---|---|
| 공식 report | [PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md) | 결론, 검증 이유, 결과, 한계, Phase 22 질문 |
| UI 재현 경로 | `Backtest > Compare & Portfolio Builder` | 같은 workflow를 화면에서 다시 확인 |
| portfolio 구성 | `Weighted Portfolio Builder` | weight와 date alignment 입력 |
| portfolio 결과 | `Weighted Portfolio Result` | weighted portfolio 결과 표시 |
| 저장 / 재실행 | `Saved Portfolios > Replay Saved Portfolio` | 저장된 compare + weighted portfolio 재실행 |

UI에서 같은 흐름을 확인하려면 아래 순서로 본다.

1. `Backtest > Compare & Portfolio Builder`
2. `Quick Re-entry From Current Candidates`
3. `Load Recommended Candidates`
4. `Strategy Comparison`
5. `Weighted Portfolio Builder`
6. `Weighted Portfolio Result`
7. `Saved Portfolios`
8. `Replay Saved Portfolio`

### report를 읽는 순서

1. `결론 먼저`
2. `왜 이 3개 전략을 묶었나`
3. `검증 흐름`
4. `weighted portfolio 결과`
5. `saved portfolio replay 검증`
6. `이 결과가 의미하는 것`
7. `Phase 22로 넘길 질문`

### 체크 항목

- [ ] report가 "최종 portfolio winner 선정"이 아니라 "portfolio workflow 첫 검증"이라는 목적을 분명히 설명하는지
- [ ] 왜 `Value / Quality / Quality + Value` 3개를 묶었는지와 이 조합의 한계가 함께 설명되어 있는지
- [ ] `Load Recommended Candidates -> Weighted Portfolio Builder -> Save Portfolio -> Replay Saved Portfolio` 검증 흐름이 이해되는지
- [ ] representative weighted portfolio 결과가 single-strategy rerun과 같은 phase frame에서 읽히는지
- [ ] saved portfolio replay 결과가 `CAGR / MDD / End Balance` exact match 기준으로 재현되는지
- [ ] 이번 결과가 아직 확인하지 않은 것과 `Phase 22`로 넘길 질문이 분리되어 있는지
- [ ] portfolio bridge가 다음 phase의 메인 대상이 될지 판단할 재료가 충분한지

---

## 4. Closeout / Handoff 확인

### 무엇을 확인하나

`Phase 21`이 practical closeout 상태로 정리됐고, 다음 단계가 왜 `Phase 22 portfolio-level candidate construction`인지 문서에서 이해되는지 확인한다.

### 어디서 확인하나

| 문서 | 확인할 내용 |
|---|---|
| [PHASE21_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_CURRENT_CHAPTER_TODO.md) | Phase 21 작업 완료 상태 |
| [PHASE21_COMPLETION_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_COMPLETION_SUMMARY.md) | Phase 21 결과 요약 |
| [PHASE21_NEXT_PHASE_PREPARATION.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_NEXT_PHASE_PREPARATION.md) | Phase 22로 넘길 질문 |
| [MASTER_PHASE_ROADMAP.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/MASTER_PHASE_ROADMAP.md) | 전체 phase 진행 상태 |
| [FINANCE_DOC_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_DOC_INDEX.md) | 관련 문서 인덱스 |

### 체크 항목

- [ ] phase 상태가 현재 실제 진행 상태와 맞는지
- [ ] Phase 21 plan / TODO / closeout / next-phase 문서를 index에서 바로 찾을 수 있는지
- [ ] next-phase preparation이 Phase 22 방향을 이해하기 쉽게 정리하는지
- [ ] Phase 21에서 확인한 annual strict anchors와 portfolio bridge 결과가 다음 phase의 출발점으로 충분히 설명되어 있는지

## 한 줄 판단 기준

이 checklist는 **"current annual strict 후보와 portfolio bridge를 같은 검증 기준에서 다시 보고, Phase 22로 넘어갈 만큼 판단이 정리됐는가"**를 확인하는 문서다.
