# Phase 10 Walk-forward / OOS / Regime Validation Design

Status: Complete
Created: 2026-05-29

## Design Principle

Phase 10은 "더 많이 저장"하는 방식이 아니라 "이미 존재하는 성과 / 가격 / macro / validation evidence를 더 엄격하게 해석"하는 방식으로 시작한다.
필요한 신규 데이터는 무료 API 또는 공개 source를 우선 검토하고, 검증 효력을 높이는 경우에만 DB-backed ingestion으로 연결한다.

## Evidence Layers

| Layer | Purpose | Initial Source |
| --- | --- | --- |
| Source map | 현재 백테스트 결과, curve, benchmark, macro, robustness evidence가 어디에서 오는지 확인 | `app/services/backtest_practical_validation*.py`, `app/services/backtest_evidence_read_model.py`, DB loaders |
| Split contract | walk-forward / OOS window를 같은 의미로 읽기 위한 compact schema 정의 | result bundle curve, benchmark curve, DB price proxy |
| Regime contract | market condition bucket별 성과 / drawdown / benchmark spread 확인 | macro loader, market context, stress / monthly return helpers |
| Audit rows | `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 표시 | Practical Validation / Final Review read model |
| Gate policy | selected-route 가능 여부에 overfit / OOS / regime gap 반영 | investability packet / selected-route gate |

## Route Semantics

| State | Meaning |
| --- | --- |
| `PASS` | 충분한 기간과 source를 바탕으로 split / OOS / regime evidence가 기준을 만족 |
| `REVIEW` | 일부 evidence는 있으나 기간, coverage, source strength, sensitivity가 부족 |
| `NEEDS_INPUT` | 실행에 필요한 curve / benchmark / macro / split source가 없음 |
| `BLOCKED` | evidence가 명확히 deployable-fit 판단을 막는 수준으로 약함 |

`NOT_RUN`은 pass가 아니다. 실행하지 못한 검증은 `NEEDS_INPUT` 또는 `REVIEW`로 남긴다.

## Candidate Implementation Boundaries

초기 구현 후보는 아래 경계 안에서 다룬다.

- `app/services/backtest_practical_validation_stress_sensitivity.py`: rolling / stress / monthly return helper 재사용 여부 확인
- `app/services/backtest_validation_efficacy.py`: validation efficacy audit 확장 후보
- `app/services/backtest_evidence_read_model.py`: Final Review gate policy 연결 후보
- `app/web/backtest_practical_validation.py`: read-only evidence display 후보
- `app/web/backtest_final_review.py`: investability packet / selected-route evidence display 후보
- `finance/loaders/macro.py`, `finance/loaders/market.py` equivalent source: regime source 확인 후보

실제 파일 변경은 10-1 source map / gap audit 후 결정한다.

## Data Boundary

- full split curve, raw optimization grid, raw provider response는 workflow JSONL에 저장하지 않는다.
- 필요한 raw / series data는 DB에 두고 loader가 compact summary를 제공한다.
- Practical Validation JSONL에는 기존 흐름이 허용하는 compact evidence만 둔다.
- user memo, preset, approval, order, auto rebalance 성격의 저장은 추가하지 않는다.

## 10-1 Source Map Result

`walkforward-oos-source-map-v1` confirmed the following:

- Practical Validation already has normalized portfolio / benchmark curve sources and curve provenance.
- Runtime backtest already emits rolling / out-of-sample review metadata, but this is not yet a first-class Practical Validation / Validation Efficacy audit row.
- Existing Robustness Lab rolling evidence is useful, but it currently emphasizes portfolio rolling CAGR / MDD and does not produce benchmark-aligned rolling excess rows.
- Regime / macro suitability is a current market-context diagnostic, not a historical regime split performance test.

Therefore 10-2 should build a compact walk-forward / rolling temporal validation contract before OOS holdout and regime split implementation.

## 10-2 Implemented Contract

`walkforward-split-contract-v1` added `app/services/backtest_temporal_validation.py`.

The contract:

- aligns portfolio and benchmark curves by month
- computes rolling portfolio return, benchmark return, excess return, strategy MDD, benchmark MDD, and drawdown gap
- returns compact rows and metrics under `temporal_validation`
- downgrades missing / short / proxy-only evidence instead of passing it
- writes no DB rows, no new JSONL registry, no memo, and no preset state

## 10-3 Implemented Contract

`oos-holdout-validation-contract-v1` extended `app/services/backtest_temporal_validation.py`.

The contract:

- reuses benchmark-aligned monthly portfolio / benchmark curves
- splits common history into in-sample and out-sample periods
- computes in-sample excess return, out-sample excess return, excess deterioration, and out-sample drawdown gap
- returns compact rows and metrics under `oos_holdout_validation`
- downgrades missing / short / proxy-only evidence instead of passing it
- writes no DB rows, no new JSONL registry, no memo, and no preset state

## 10-4 Implemented Contract

`regime-split-validation-v1` extended `app/services/backtest_temporal_validation.py`.

The contract:

- reads DB-backed FRED macro observation history through `finance.loaders.macro.load_macro_series_observations()`
- classifies monthly macro history into `neutral`, `caution`, and `risk_off` buckets using VIX / yield curve / credit spread thresholds
- aggregates portfolio and benchmark monthly returns by regime bucket
- computes bucket excess return and drawdown gap
- returns compact rows and metrics under `regime_split_validation`
- downgrades missing / short / proxy-only macro evidence instead of passing it
- writes no DB rows, no new JSONL registry, no memo, and no preset state

## 10-5 Implemented Contract

`validation-efficacy-gate-policy-refinement-v2` extended `app/services/backtest_evidence_read_model.py`.

The contract:

- merges non-PASS Validation Efficacy Audit rows into the `validation_efficacy` gate policy group
- surfaces `Walk-forward temporal validation`, `OOS holdout validation`, and `Regime split validation` criteria in Final Review selected-route evidence
- maps `NEEDS_INPUT` / `BLOCKED` to selected-route blockers and `REVIEW` to hold / re-review requirements
- reuses the existing investability packet / selected-route gate contract
- writes no DB rows, no new JSONL registry, no memo, and no preset state

## 10-6 Closeout Result

`phase10-integrated-qa-closeout` completed integrated verification and added the done summary.

The closeout:

- passed targeted compile for Phase 10 service / loader touch points
- passed full `tests.test_service_contracts`
- passed UI / engine boundary and finance refinement hygiene checks
- recorded residual risks and Phase 11 handoff
- added no DB rows, no new JSONL registry, no memo, and no preset state

## User Flow Target

사용자는 기존 흐름을 유지한다.

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Selected Portfolio Dashboard
```

Phase 10이 끝나면 Practical Validation과 Final Review에서 "이 전략은 전체기간 수익률은 좋아도 OOS / regime evidence 때문에 보류해야 한다"는 결론을 더 명확히 볼 수 있어야 한다.
