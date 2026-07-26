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
