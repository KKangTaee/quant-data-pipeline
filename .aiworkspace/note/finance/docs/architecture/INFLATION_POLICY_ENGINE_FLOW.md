# Inflation / Policy / Yield Engine Flow

Status: Active
Last Verified: 2026-08-02

## 목적

사용자의 `Core PCE -> FOMC 정책 -> 10년물 저항대` 질문을 기존 경제 사이클
확률과 분리된 Point-in-Time 분석으로 계산한다. 4.7%, 3.5%, 월 0.4~0.5% 같은
숫자는 전역 인과 규칙이 아니라 시점별 자동 기준 또는 사용자 시나리오다.

## Runtime Flow

```text
released_at PIT macro vintages + anonymous SEP + actual FOMC vote
  -> finance/loaders/inflation_policy.py
  -> finance/inflation_policy_model.py
       bridge + ridge + momentum one-month Core PCE nowcast
  -> finance/inflation_path.py
       index recursion + Q4/Q4 distribution + five states
  -> finance/policy_path.py
       SEP marginal + economic reaction prior + committee vote marginal
  -> finance/yield_resistance.py
       confirmed pivots + 63/252/504-day zones + driver lenses
  -> finance/inflation_policy_simulation.py
       joint forward paths + target-conditional reverse summaries
  -> finance/inflation_policy_validation.py
       chronological metrics + baseline + calibration publication gate
  -> finance/inflation_policy_pipeline.py
       compact model artifact / snapshot
  -> finance/data/inflation_policy_results.py
```

정상 UI는 다음 3차 workbench에서 저장 snapshot을 읽는다. provider/FRED 조회와
canonical 확률 계산을 화면 렌더링 중 수행하지 않는다.

## Module Ownership

| Owner | Responsibility |
|---|---|
| `finance/loaders/inflation_policy.py` | 한 cutoff의 strict bundle과 과거 origin 재구성용 전체 eligible vintage read |
| `finance/inflation_policy_model.py` | Core PCE 모멘텀, CPI·PPI·임금·trimmed-mean bridge, 정규화 ridge와 rolling-origin component weight |
| `finance/inflation_path.py` | 월별 index 복리 경로, Q4 평균 기반 Q4/Q4, SEP-versioned 5상태와 사용자 threshold probability |
| `finance/policy_path.py` | 익명 SEP 금리점의 순이동 marginal, 실제 의결·dissent 방향, versioned state-to-policy 반응행렬 |
| `finance/yield_resistance.py` | 오른쪽 확인 이후에만 알려지는 pivot, adaptive tolerance, 동적 zone과 2개 driver lens |
| `finance/inflation_policy_simulation.py` | 정책 25bp와 10년물 25bp를 기계적으로 연결하지 않는 순방향·조건부 역산 계약 |
| `finance/inflation_policy_validation.py` | CRPS/MAE/coverage, Brier/log loss/ECE, baseline 비교와 fail-closed publication gate |
| `finance/inflation_policy_pipeline.py` | exact cutoff 학습·재현, compact evidence, 명시적 저장 CLI |

## Point-in-Time Contract

- 현재 bundle은 `released_at <= as_of_at`인 최신 eligible version만 사용한다.
- 모델 학습은 한 cutoff의 최신 수정값을 과거에 알았던 값처럼 쓰지 않는다. 전체
  vintage 행에서 각 target 공개 직전의 version을 다시 선택한다.
- Core PCE target은 해당 월 최초 공개값과 그 공개시각에 알려진 직전월 index로
  계산한다.
- 같은 개정일에 함께 공개된 여러 과거 관측치는 별도 rolling origin으로 세지 않는다.
- artifact는 관측월 `trained_through_date`와 실제 학습 시각 `trained_cutoff_at`을 따로
  저장하며, 학습 cutoff가 replay cutoff와 정확히 같지 않으면 core-dependent 출력을
  차단한다. artifact 관측월과 bundle의 최신 Core PCE 월도 일치해야 한다.
- artifact 없이 최신 수정값 bundle만 받은 직접 호출은 momentum을 재학습하지 않고
  `NOT_AVAILABLE`로 닫는다. `FAILED` artifact도 snapshot으로 승격하거나 저장하지 않는다.
- Core PCE가 막혀도 유효한 Treasury 저항/driver read payload는 독립 `LIMITED`로
  계산하지만, 실패한 core 학습 run 자체는 신규 snapshot을 저장하지 않는다.
- SEP 금리점과 Core PCE histogram은 익명 marginal이며 개인별 joint mapping을 만들지
  않는다.

## Dynamic Yield Criterion

- 각 instrument는 63/252/504거래일의 confirmed pivot high를 사용한다.
- 해당 수만큼 관측 이력이 실제로 쌓인 lookback만 timeframe 근거로 인정한다.
- tolerance는 `max(5bp, 최근 63행 절대 일간변화 중앙값)`이다.
- `active_test_zone`은 현재 금리가 buffer 안에 있는 후보 중 strength가 가장 높은
  구간이고, `next_overhead_zone`은 현재보다 위에 있는 가장 가까운 confirmed 구간이다.
- 10년물 돌파만으로 인플레이션을 확정하지 않는다. 2년물 정책 proxy, 실질 10년물,
  10년 breakeven, 가능한 경우 ACM term premium과 Core PCE posterior 변화가 필요하다.

## Publication Boundary

| Status | Meaning |
|---|---|
| `READY` | 해당 component의 PIT origin, baseline 개선, coverage와 calibration gate 통과 |
| `LIMITED` | 계산은 가능하지만 그 horizon 또는 event probability의 독립 검증 부족 |
| `NOT_AVAILABLE` | critical input 또는 충분한 target-support path 부재 |
| `FAILED` | schema, simplex, non-finite 또는 실행 계약 위반 |

현재 `core_pce_hybrid`는 97개 독립 release origin에서 carry-forward·3개월·6개월
baseline 중 최선보다 낮은 CRPS를 보였지만, SEP/공식 nowcast benchmark 묶음이
완성되지 않아 `LIMITED`다. 연말 Q4/Q4 path, FOMC 정책 경로, 저항 돌파·안착 확률도
각각 별도 검증 전이므로 통합 snapshot은 `LIMITED`다. joint rate path가 검증되기 전 역산은
`NOT_AVAILABLE`이고, 신규 침체 모델도 5차 전까지 같은 상태다.

## Related Docs

- [Data DB Pipeline Flow](./DATA_DB_PIPELINE_FLOW.md)
- [Inflation / Policy Data Refresh](../runbooks/INFLATION_POLICY_DATA_REFRESH.md)
- [Inflation Policy Yield Path phase](../../phases/active/inflation-policy-yield-path/PLAN.md)
