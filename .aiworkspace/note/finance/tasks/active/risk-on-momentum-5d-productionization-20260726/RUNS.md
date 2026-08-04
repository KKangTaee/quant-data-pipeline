# Risk-On Momentum 5D Productionization Runs

## 2026-07-26 Baseline

### Actual Top1000 Two-Year Timing

Range: `2024-07-26` through `2026-07-24`

| Stage | Result |
|---|---|
| universe | 0.034s, 1,000 symbols |
| prices | 3.006s, 610,253 rows, 1,002 symbols |
| statements | 0.250s, 9,930 rows, 953 symbols |
| macro | 0.055s, 7,583 source rows, 632 score rows |
| features | 3.008s, 609,005 rows, 31 columns |
| primary | 18.616s, 500 days, 340 trades, 6,130 scanner rows |
| three random variants | 55.631s |
| total diagnostic | 80.621s |

The diagnostic called domain/loaders directly and did not write a backtest artifact.

### Profile

- approximately 318.9 million profiled calls in the measured process
- approximately 15.7 million `Series.__getitem__` calls
- approximately 496,000 `DataFrame.iterrows` rows
- `_rank_candidates` itself was not the dominant single-run Python cost

### Baseline Tests

Command:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.RiskOnMomentumSwingContractTests \
  tests.test_backtest_risk_on_governance
```

Result: PASS, 13 tests.

Broader evidence-inventory command: 21 tests run, one pre-existing literal-source drift failure.

## 2026-07-26 Implementation Verification

### TDD / Focused Contracts

- Prepared simulation parity, indexed lookup, analysis intensity와 variant cache RED/GREEN 완료
- Risk-On core focused suite: 15 tests PASS
- Daily Swing governance focused suite: 12 tests PASS
- History compact evidence / analysis intensity persistence와 replay option contract: PASS

### Actual Top1000 Two-Year Standard Timing

Range: `2024-07-26` through `2026-07-24`

| Result | Value |
|---|---:|
| elapsed | 21.247s |
| trading rows | 500 |
| simulation requests | 20 |
| distinct executions | 16 |
| cache hits | 4 |
| evidence status | REVIEW |

Acceptance target `<= 60s`를 충족했다. `REVIEW`는 성능 실패가 아니라 current membership
universe의 historical PIT / delisting coverage가 검증되지 않았다는 downstream evidence 판정이다.

### Browser QA

- Risk-On이 `모멘텀·전술 자산배분` 그룹과 `운영 전략` label로 표시됨
- `분석 강도`가 `표준 · 무작위 10회 + 비교`를 기본 선택함
- 실제 DB 실행이 완료되고 result workspace / Swing 결과 표가 생성됨
- 실행 데이터 최신성 warning은 기존 DB 공통 기준일 부족을 사용자 행동으로 표시함
- in-app Browser screenshot은 응답 capture로 확인했지만 이 환경에서 local screenshot artifact export는 지원되지 않아 파일로 저장하지 못함

### Static / Regression

- relevant modules `py_compile`: PASS
- `git diff --check`: PASS
- `RiskOnMomentumSwingContractTests + PracticalValidationServiceContractTests + BacktestRefactorBoundaryTests`: 94 tests, 92 PASS
- 나머지 2건은 이번 변경 파일 밖의 current-date market sentiment overlay expectation drift

## 2026-08-04 Master Merge Integration Verification

- master 병합의 유일한 text conflict인 `docs/ROADMAP.md`를 phase/task `STATUS.md`와
  manifest 우선순위로 수동 병합했다. 완료된 Inflation Policy phase와 Risk-On
  production baseline을 함께 보존하고 current active phase/task는 `none`으로 정렬했다.
- 병합 대상 Python 파일 전체 `py_compile`: PASS
- `RiskOnMomentumSwingContractTests + BacktestRiskOnGovernanceContractTests`:
  27 tests PASS
- `RiskOnMomentumSwingContractTests + PracticalValidationServiceContractTests +
  BacktestRefactorBoundaryTests`: 94 tests, 92 PASS
- 실패 2건은 재현 결과 sentiment fixture가 현재 5개 core series 중 일부를 제공하지 않아
  `REVIEW/neutral`이 되는 기존 expectation drift다. 관련 sentiment 구현과 실패 테스트
  본문은 병합 양쪽에서 변경되지 않았으므로 이번 integration 범위에서 수정하지 않았다.
- fresh temporary Streamlit server Browser QA: Risk-On이 `모멘텀·전술 자산배분`에
  속하고 `운영 전략`으로 표시되며 분석 강도 기본값이 `표준 · 무작위 10회 + 비교`임을
  확인했다. Browser console error는 0건이다.
- QA screenshot: `risk-on-master-merge-qa-20260804.jpg` (generated, unstaged)
- local registry row, run history, research bundle, QA image와 기타 untracked artifact는
  병합 stage에 포함하지 않았다.
