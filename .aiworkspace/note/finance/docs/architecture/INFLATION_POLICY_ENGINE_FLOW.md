# Inflation / Policy / Yield Engine Flow

Status: Active
Last Verified: 2026-08-03

## 목적

사용자의 `Core PCE -> FOMC 정책 -> 10년물 저항대 -> S&P 500 조건부 스트레스` 질문을 기존 경제 사이클
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
  -> finance/inflation_policy_equity_stress.py
       PIT next-year EPS × forward multiple calibration + conditional scenarios
  -> finance/inflation_policy_validation.py
       chronological metrics + baseline + calibration publication gate
  -> finance/inflation_policy_pipeline.py
       compact model artifact / snapshot with independent equity_json
  -> finance/data/inflation_policy_results.py
  -> app/services/overview/inflation_policy.py
       typed DB-only read model + publication guard
  -> app/services/overview/inflation_policy_commands.py
       USER criterion save + exact-artifact bounded rate/equity scenarios
  -> app/web/overview/market_context_helpers.py
       render-edge transport + separate command nonce/cache
  -> economic_cycle_workbench React `물가·정책 경로`
```

정상 UI는 4차 workbench에서 저장 snapshot을 읽는다. provider/FRED 조회와 canonical
확률 계산을 화면 렌더링 중 수행하지 않으며, 같은 transport에 붙은 기존 경제 사이클
payload는 서비스 입력·fallback·침체 확률로 사용하지 않는다.

## Module Ownership

| Owner | Responsibility |
|---|---|
| `finance/loaders/inflation_policy.py` | 한 cutoff의 strict bundle, 과거 origin 재구성용 전체 eligible vintage, PIT USER/AUTO definition과 exact cutoff artifact read |
| `finance/inflation_policy_model.py` | Core PCE 모멘텀, CPI·PPI·임금·trimmed-mean bridge, 정규화 ridge와 rolling-origin component weight |
| `finance/inflation_path.py` | 월별 index 복리 경로, Q4 평균 기반 Q4/Q4, SEP-versioned 5상태와 사용자 threshold probability |
| `finance/policy_path.py` | 익명 SEP 금리점의 순이동 marginal, 실제 의결·dissent 방향, versioned state-to-policy 반응행렬 |
| `finance/yield_resistance.py` | 오른쪽 확인 이후에만 알려지는 pivot, adaptive tolerance, 동적 zone과 2개 driver lens |
| `finance/inflation_policy_simulation.py` | 정책 25bp와 10년물 25bp를 기계적으로 연결하지 않는 순방향·조건부 역산 계약 |
| `finance/inflation_policy_equity_stress.py` | complete same-workbook 차년도 EPS vintage와 origin별 저장 가격·금리의 year-end PIT panel, 공개시각 rolling ridge, paired residual, 3-baseline/coverage gate와 bounded 사용자 AI EPS/지수 수준 scenario |
| `finance/inflation_policy_validation.py` | CRPS/MAE/coverage, Brier/log loss/ECE, baseline 비교와 fail-closed publication gate |
| `finance/inflation_policy_pipeline.py` | exact cutoff 학습·재현, production equity bundle→panel→artifact→`joint_macro_paths`→simulation 실행, snapshot별 live equity context와 component-independent result 직렬화, compact evidence, 명시적 저장 CLI |
| `app/services/overview/inflation_policy.py` | snapshot JSON 검증, 상태 사유·AUTO/USER zone·equity gate·근거/신선도·5차 침체 미연결 경계를 포함한 `inflation_policy_v1` read model |
| `app/services/overview/inflation_policy_commands.py` | USER-only criterion 저장과 선택 snapshot의 정확히 일치하는 READY artifact만 쓰는 bounded rate/equity scenario command |
| `app/web/overview/market_context_helpers.py` | cycle과 독립 read model을 렌더 직전에만 합성하고 command nonce/cache/result를 cycle refresh와 분리 |
| `app/web/streamlit_components/economic_cycle_workbench/` | 기존 경기 국면 기본값, 순방향 판단·동적 저항·목표 역산·S&P 500 조건부 stress·근거 disclosure를 제공하는 React presentation |

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
- equity origin은 당시 공개된 official S&P 500 차년도 EPS vintage와 직전 저장 시장
  가격·금리만 쓴다. Shiller trailing EPS, 현재 수정값이나 이후 공개 estimate를 과거
  origin에 대입하지 않는다.
- forward EPS는 한 workbook release의 같은 basis/source에 네 분기가 모두 있는 경우만
  합산한다. yield revision은 loader에서 전체 eligible vintage를 보존한 뒤 origin마다
  다시 고르며, 역사 label은 year-end endpoint와 Q4 Core PCE 공개시각 중 늦은
  `label_available_at` 이후 fold에서만 사용한다.
- equity validation은 constant EPS, constant multiple, unconditional index-change baseline과
  80% interval coverage를 함께 검사한다. 현재 scenario context는 학습 마지막 역사 row가
  아니라 live snapshot에서 따로 만들며 artifact cutoff를 변경하지 않는다.
- core coefficients와 verified joint paths는 각각 `core_pce_hybrid`, `joint_macro_paths`
  component로 저장해 UPSERT identity를 공유하지 않는다. equity model artifact에는 계수·paired
  residual·검증만 저장하고, 현재 index/EPS/start-yield는 해당 snapshot의 `equity_json`이
  소유한다. 사용자 command도 선택 snapshot context를 사용한다.
- legacy 일봉에 별도 공개시각이 없으므로 미국 정규장 마감 전 replay는 당일 close를
  제외한다. simulation은 순서 독립적인 최대 16개 paired-residual quantile sample을
  forward path마다 교차해 path 입력 순서와 결과 분포를 분리한다.
- measured EPS revision, months-to-year-end, DGS2/DGS10/DFII10/T10YIE 시작값과 모든
  공동경로 endpoint는 필수다. 누락을 0bp/0%로 대체하지 않고 equity만
  `scenario_context_incomplete` `NOT_AVAILABLE`로 닫는다.

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
`NOT_AVAILABLE`이다. equity 엔진과 UI는 연결됐지만 actual official EPS vintage가 0건이고
검증된 공동 거시경로도 없어 equity는 `NOT_AVAILABLE`이며, 신규 침체 모델도 5차 전까지
같은 상태다.

equity production runner와 scenario command는 payload 존재만으로 공동경로를 승인하지
않는다. exact `joint_macro_paths` artifact의 독립 `joint_path_publication_status=READY`와
`equity-stress-publication-v1` contract가 모두 확인될 때만 계산한다.

UI는 전체 snapshot이 `READY`일 때만 다섯 상태·threshold·정책 확률을 현재 판단으로
표시한다. `LIMITED`에서도 DGS10 관측값과 날짜가 붙은 자동 zone은 보조 근거로 보이지만
저장된 확률 숫자는 숨긴다. 자동 zone은 읽기 전용이고 수정은 별도 USER definition으로만
저장한다. equity는 `READY`일 때만 target probability를 표시하고 `LIMITED`에서는
EPS·multiple 범위만, `NOT_AVAILABLE`에서는 공식 EPS/공동경로 준비 조건만 보여준다.

## Related Docs

- [Data DB Pipeline Flow](./DATA_DB_PIPELINE_FLOW.md)
- [Inflation / Policy Data Refresh](../runbooks/INFLATION_POLICY_DATA_REFRESH.md)
- [Inflation Policy Yield Path phase](../../phases/active/inflation-policy-yield-path/PLAN.md)
