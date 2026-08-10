# Inflation / Policy / Yield Engine Flow

Status: Active
Last Verified: 2026-08-04

## 목적

사용자의 `Core PCE -> FOMC 정책 -> 10년물 저항대 -> S&P 500 조건부 스트레스` 질문을 기존 경제 사이클
확률과 분리된 Point-in-Time 분석으로 계산한다. 4.7%, 3.5%, 월 0.4~0.5% 같은
숫자는 전역 인과 규칙이 아니라 시점별 자동 기준 또는 사용자 시나리오다.

## Runtime Flow

```text
released_at PIT macro vintages + Philadelphia Fed SPF + anonymous SEP + actual FOMC vote
  + verified FactSet annual EPS release vintages
  -> finance/loaders/inflation_policy.py
  -> finance/inflation_policy_model.py
       bridge + ridge + momentum one-month Core PCE nowcast
  -> finance/core_pce_q4.py
       monthly path + official SPF linear pool + chronological Q4/Q4 gate
  -> finance/inflation_path.py
       index recursion + Q4/Q4 distribution + five states
  -> finance/policy_path.py
       SEP rate-dot marginal + committee vote/dissent marginal
  -> finance/policy_validation.py
       completed decision/SEP targets + chronological baseline/calibration gate
  -> finance/yield_resistance.py
       confirmed pivots + 63/252/504-day zones + driver lenses
  -> finance/joint_rate_paths.py
       completed DGS2/DGS10/DFII10/T10YIE episodes + resistance-event validation
  -> finance/inflation_policy_simulation.py
       joint forward paths + target-conditional reverse summaries
  -> finance/inflation_policy_equity_stress.py
       PIT next-year EPS × forward multiple calibration + conditional scenarios
  -> finance/inflation_policy_recession.py
       10 independent PIT features + 24-month delayed USREC outcome + 12-month probability
  -> finance/inflation_policy_validation.py
       chronological metrics + baseline + calibration publication gate
  -> finance/inflation_policy_pipeline.py
       compact model artifact / snapshot with independent equity_json/recession_json
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
| `finance/data/spf_core_pce.py` / `finance/core_pce_q4.py` | Philadelphia Fed SPF Q4/Q4 probability-bin vintage 수집과 월간 모델/SPF 선형 pool, internally consistent first-release index-vintage target, chronological CRPS·coverage gate |
| `finance/data/factset_sp500_eps.py` | FactSet 월별 보고서의 공개일·annual bottom-up EPS 표 제목·연도·구조를 검증하고 current/next calendar-year release vintage를 fail-closed로 저장 |
| `finance/inflation_policy_model.py` | Core PCE 모멘텀, CPI·PPI·임금·trimmed-mean bridge, 정규화 ridge와 rolling-origin component weight |
| `finance/inflation_path.py` | 월별 index 복리 경로, Q4 평균 기반 Q4/Q4, SEP-versioned 5상태와 사용자 threshold probability |
| `finance/policy_path.py` | 익명 SEP 금리점의 순이동 marginal, 실제 의결·dissent 방향, versioned state-to-policy 반응행렬 |
| `finance/policy_validation.py` | 완료된 다음 회의 action과 연말 target을 쓰는 nested chronological smoothing 선택, Brier/ECE와 hold·previous-action·prior-SEP baseline gate |
| `finance/yield_resistance.py` | 오른쪽 확인 이후에만 알려지는 pivot, adaptive tolerance, 동적 zone과 2개 driver lens |
| `finance/joint_rate_paths.py` | completed monthly rate episode의 동시 변화를 current Q4/policy marginal과 rank-couple하고, endpoint CRPS와 PIT resistance-reach Brier/calibration으로 2,000개 공동 경로 공개를 결정 |
| `finance/inflation_policy_simulation.py` | 정책 25bp와 10년물 25bp를 기계적으로 연결하지 않는 순방향·조건부 역산 계약 |
| `finance/inflation_policy_equity_stress.py` | 당시 공개된 annual 차년도 EPS vintage와 origin별 저장 가격·금리의 year-end PIT panel, 공개시각 rolling ridge, paired residual, 3-baseline/과거 OOS residual coverage gate와 bounded 사용자 AI EPS/지수 수준 scenario |
| `finance/inflation_policy_recession.py` | 실업·고용·활동·금리의 분기별 PIT feature, target 종료 24개월 뒤 확정되는 12개월 NBER outcome, expanding-window Brier/calibration/episode gate와 5단계 위험 상태 |
| `finance/inflation_policy_validation.py` | CRPS/MAE/coverage, Brier/log loss/ECE, baseline 비교와 fail-closed publication gate |
| `finance/inflation_policy_pipeline.py` | exact cutoff 1개월/Q4·policy·equity·recession 학습/재현, 공동경로 simulation, 5개 다음 물가 발표 scenario와 독립 component 직렬화, compact evidence, 명시적 저장 CLI |
| `app/services/overview/inflation_policy.py` | snapshot JSON 검증, 상태 사유·AUTO/USER zone·equity/recession gate·근거/신선도를 포함한 `inflation_policy_v1` read model |
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
  않는다. 연말 정책 검증은 `SEP released_at < final decision released_at`인 양의 예측
  horizon만 허용하고 December 동시결과를 origin으로 세지 않는다.
- historical FOMC history는 official `Meeting - YYYY` panel의 exact `Statement`만
  발견 단계에서 선택한다. 실제 meeting statement의 target-range parser 오류는
  non-rate로 추정해 skip하지 않고 수집을 실패시킨다.
- 공동 금리 episode의 역사 Q4 actual은 completed outcome의 결합 순위에만 쓰며 현재
  forecast feature로 사용하지 않는다. 각 origin은 당시 알려진 동적 zone과 이전 연도의
  completed episode만 사용해 endpoint와 resistance event를 검증한다.
- equity origin은 당시 공개된 FactSet annual 차년도 bottom-up EPS vintage와 직전 저장 시장
  가격·금리만 쓴다. Shiller trailing EPS, 현재 수정값이나 이후 공개 estimate를 과거
  origin에 대입하지 않는다.
- forward EPS는 같은 release/source의 연간 next-calendar-year 값을 사용한다. FactSet
  분기 차트는 rolling 12-quarter 범위라 연초 차년도 Q1~Q4 합으로 사용하지 않는다.
  yield revision은 loader에서 전체 eligible vintage를 보존한 뒤 origin마다
  다시 고르며, 역사 label은 year-end endpoint와 Q4 Core PCE 공개시각 중 늦은
  `label_available_at` 이후 fold에서만 사용한다.
- equity validation은 constant EPS, constant multiple, unconditional index-change baseline과
  이전 fold의 OOS residual만으로 만든 80% interval coverage를 함께 검사한다. 현재 scenario context는 학습 마지막 역사 row가
  아니라 live snapshot에서 따로 만들며 artifact cutoff를 변경하지 않는다.
- recession target은 origin 이후 12개월 내 `USREC=1` 존재 여부이며 target 종료 뒤
  24개월이 지난 label만 다음 fold 학습에 들어간다. `USREC`과 기존 경제 사이클 확률은
  current feature가 아니다. current feature completeness 80% 미만이면 확률을 숨긴다.
- DGS2/DGS10 같은 미개정 일별 series는 observation-date EOD를 release anchor로 쓰고
  `realtime_start/end` revision identity는 별도로 보존한다. 월간/분기 revision series에는
  이 anchor를 적용하지 않는다.
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

현재 `core_pce_hybrid`, `core_pce_q4_linear_pool`, `policy_path`,
`joint_macro_paths`, `equity_stress`, `recession_risk`는 actual chronological gate를 통과했다. 공식 FOMC rate decision
86건과 SEP 40개 release를 기반으로 다음 회의 78개·연말 22개 evaluation origin을 검증했고, completed rate episode
110개와 resistance event 57개로 DGS2/DGS10/DFII10/T10YIE endpoint와 동적 zone event를
검증했다. 현재 snapshot의 inflation/policy/rates/reverse는 `READY`이며 DGS10 next
overhead 4.79% 도달 역산은 2,000개 중 1,690개 경로가 지지한다. FactSet의 검증된 EPS
80 release/160행으로 77 equity origin을 만들었고 nested chronological ridge의
index-change MAE 6.0751%가 best baseline 7.6929%보다 낮으며 OOS 80% interval coverage가
0.875라 equity도 `READY`다. 독립 침체는
138 origins/86 OOS folds/2 episodes에서 Brier 0.146934 < base-rate 0.157162,
calibration 0.024324로 `READY`다. 통합 snapshot과 6개 component 모두 `READY`다.

equity production runner와 scenario command는 payload 존재만으로 공동경로를 승인하지
않는다. exact `joint_macro_paths` artifact의 독립 `joint_path_publication_status=READY`와
`equity-stress-publication-v1` contract가 모두 확인될 때만 계산한다.

UI는 전체 snapshot 상태가 아니라 inflation/policy/rates/reverse/equity/recession 각 component의
publication status로 해당 숫자를 표시한다. exact stored reverse target을 form 기본값과
일치시키고 command도 같은 snapshot/artifact를 사용한다. 자동 zone은 읽기 전용이고
수정은 별도 USER definition으로만 저장한다. equity는 `READY`일 때만 target probability를 표시하고 `LIMITED`에서는
EPS·multiple 범위만, `NOT_AVAILABLE`에서는 검증된 EPS/공동경로 준비 조건만 보여준다.

## Related Docs

- [Data DB Pipeline Flow](./DATA_DB_PIPELINE_FLOW.md)
- [Inflation / Policy Data Refresh](../runbooks/INFLATION_POLICY_DATA_REFRESH.md)
- [Inflation Policy Yield Path phase](../../phases/active/inflation-policy-yield-path/PLAN.md)
