# Inflation / Policy Point-in-Time Data Refresh

Status: Active
Last Verified: 2026-08-03

## 목적

Core PCE, FOMC SEP·정책 결정, 국채금리와 기간 프리미엄 원천을 UI나 기존 경제
사이클 결과에 의존하지 않고 MySQL의 독립 Point-in-Time 원장으로 갱신한다. raw
갱신과 DB-only 모델 재현·저장은 별도 명령이며, 수집 명령 자체는 확률·저항대·주가
스트레스 결과를 계산하지 않는다.

## 언제 사용하는가

- inflation-policy 엔진의 현재 또는 historical replay 입력을 준비할 때
- 새 FOMC 성명이나 SEP가 공개된 뒤 익명 분포와 의결 이력을 갱신할 때
- FRED/ALFRED 물가·노동·활동·금리 빈티지를 다시 적재할 때
- 필수 source coverage 때문에 모델 materialization이 차단됐는지 확인할 때

## 입력과 사전 조건

- local MySQL이 실행 중이고 `finance_meta`를 생성·사용할 수 있어야 한다.
- `FRED_API_KEY`는 필수다. CLI는 프로젝트 local env를 먼저 읽는다.
- `BEA_API_KEY`는 선택이다. 없으면 PCE 구성항목 breadth는 `NOT_AVAILABLE`이지만
  headline Core PCE와 필수 정책·금리 경로는 계속 준비할 수 있다.
- Federal Reserve와 New York Fed 공식 페이지에 접근할 수 있어야 한다.
- `--as-of-at`은 수집 실행의 관측 시각이다. 과거 공개 시각을 새로 만들어내는
  옵션이 아니며, 저장된 row는 source별 검증된 `released_at` 경계를 따른다.

## 실행 명령

현재 시각으로 raw source를 갱신한다.

```bash
.venv/bin/python -m app.jobs.inflation_policy_refresh
```

재현 가능한 실행 기록을 위해 관측 시각을 명시할 수 있다.

```bash
.venv/bin/python -m app.jobs.inflation_policy_refresh \
  --as-of-at 2026-08-02T12:00:00+09:00
```

외부 scheduler에서 전체 Overview job을 평가할 때는 평일 24시간 cadence의
`inflation_policy_raw` job이 `safe`, `standard`, `broad` profile에 포함된다.
브라우저 진입으로 실행되는 `browser_safe`에는 포함되지 않는다.

```bash
.venv/bin/python -m app.jobs.overview_automation --profile safe --dry-run
.venv/bin/python -m app.jobs.overview_automation --profile standard
```

## 모델 재현과 명시적 저장

먼저 읽기 전용으로 exact cutoff를 재현한다. `--as-of-at` 이후 공개된 행은 참조월이
과거여도 제외된다.

```bash
.venv/bin/python -m finance.inflation_policy_pipeline \
  --as-of-at 2026-07-29T18:00:00+00:00 \
  --run-kind historical_replay
```

출력과 publication status를 확인한 뒤 같은 business key를 저장하려면
`--persist`를 명시한다. 이 옵션이 없으면 DB write가 없다.

```bash
.venv/bin/python -m finance.inflation_policy_pipeline \
  --as-of-at 2026-07-29T18:00:00+00:00 \
  --model-version inflation-policy-hybrid-v1 \
  --run-kind historical_replay \
  --persist
```

저장은 `READY|LIMITED` artifact/snapshot만 허용한다. hybrid 학습이 불가능하거나
critical input이 없으면 `NOT_AVAILABLE`을 반환하고 artifact/snapshot을 쓰지 않는다.
같은 `model_version + cutoff + component`와 `as_of_at + model_version + run_kind`는
UPSERT된다.

artifact의 `trained_cutoff_at`은 실제 hybrid fit cutoff이며 replay cutoff와 정확히
일치해야 한다. Core PCE 학습이 실패하거나 cutoff/관측월이 맞지 않는 artifact가 주입된 run은 Treasury
read payload를 독립 계산할 수 있어도 신규 artifact/snapshot은 저장하지 않는다.

## 기대 결과

출력은 한 줄 JSON이다.

- `materialization_allowed=true`: 필수 source와 필수 series가 모두 존재한다.
- `status=success`: 필수·선택 source가 모두 준비됐다.
- `status=partial_success`: 필수 경로는 준비됐지만 BEA 구성항목 또는 ACM 같은
  선택 source가 `LIMITED`/`NOT_AVAILABLE`이다.
- `required_series_gaps=[]`: `PCEPILFE`, `DGS2`, `DGS10`, `DFII10`, `T10YIE`
  필수 입력에 누락이 없다.
- `failed_sources=[]`: FRED/ALFRED, SEP, FOMC 결정 필수 수집기가 성공했다.

2026-08-03 실제 source smoke에서는 26개 FRED/ALFRED series, current calendar와
2016~2020 historical material에서 SEP 40개 release·5,787개 distribution row와
rate decision 86건을 적재했고 `materialization_allowed=true`였다. `BEA_API_KEY`
부재로 PCE 구성항목은 `NOT_AVAILABLE`, 현재 ACM workbook은 과거 공개 빈티지를
복원할 수 없어 term premium은 `LIMITED`였다.

2026-08-03 03:15 UTC current materialization에서는 1개월 Core PCE와 SPF 혼합 Q4/Q4,
다음회의·연말 policy, DGS2/DGS10/DFII10/T10YIE 공동 경로와 dynamic resistance event가
각 chronological baseline/calibration gate를 통과했다. inflation/policy/rates/reverse는
`READY`이고, 10년물 자동 기준은 active `4.58~4.65%`, 다음 overhead `4.79%`다.
4.79% 도달 역산은 2,000개 중 1,690개 경로가 지지한다. 통합 snapshot은 equity와
독립 침체 component가 남아 `LIMITED`지만 이미 READY인 네 macro component의 수치는
그 상태와 무관하게 공개한다. 4.7%를 전역 상수로 사용하지 않는다.

## 실패 처리

- `materialization_allowed=false`: 확률 snapshot을 만들지 않는다. `failed_sources`와
  `required_series_gaps`를 먼저 해결하고 raw refresh를 다시 실행한다.
- `FRED_API_KEY is required`: 프로젝트 local env의 key를 확인한다. revised CSV로
  우회하거나 미래 값으로 채우지 않는다.
- FRED vintage limit 오류: collector가 한 요청의 vintage date 수를 안전 한도 아래로
  분할하는지 확인하고 `tests/test_fred_vintages.py`를 실행한다.
- SEP/FOMC parser 오류: 공식 페이지의 release-specific header, participant note,
  vote paragraph가 바뀌었는지 확인한다. 익명 SEP 분포 사이의 개인별 대응은 추론하지
  않는다.
- `pce_components=not_available`: headline 경로와 구분한다. BEA key를 제공하기 전까지
  breadth 기능만 비활성 상태로 둔다.
- `term_premium=LIMITED`: 현재 workbook의 과거 행을 과거 시점에 소급하지 않는다.
  실제 collection 빈티지가 누적될 때까지 historical replay에서는 제한을 유지한다.
- `benchmark_suite_incomplete`: 비교 가능한 carry-forward·3개월·6개월 baseline은
  모두 저장하지만 SEP/공식 benchmark가 준비되기 전 artifact를 `READY`로 올리지 않는다.
- `q4_path_rolling_origin_validation_not_ready`: 월간 artifact 결과를 연말 확률로
  승격하지 않는다. snapshot의 `LIMITED`를 유지한다.
- `policy_rolling_origin_validation_not_ready`: 공식 calendar 전체를 다시 수집하고
  historical material까지 실제 rate statement만 선택됐는지 확인한다. 연말 origin은
  December 동시결과를 제외한 `SEP released_at < final decision released_at`만 센다.
- `joint_rate_path_validation_not_ready`: 저장된 저항 zone은 볼 수 있지만 목표 zone
  역산은 `NOT_AVAILABLE`로 둔다.
- `core_pce_artifact_not_publishable` 또는 artifact cutoff 오류: 물가·정책·역산은
  차단한다. Treasury read payload는 독립 계산하되 해당 실패 run은 저장하지 않는다.

집중 검증:

```bash
.venv/bin/python -m pytest \
  tests/test_fred_vintages.py \
  tests/test_inflation_policy_catalog.py \
  tests/test_bea_pce_components.py \
  tests/test_fomc_policy_data.py \
  tests/test_nyfed_term_premium.py \
  tests/test_inflation_policy_loaders.py \
  tests/test_inflation_policy_refresh.py \
  tests/test_inflation_policy_model.py \
  tests/test_inflation_policy_pipeline.py \
  tests/test_inflation_policy_validation.py \
  tests/test_inflation_policy_simulation.py \
  tests/test_yield_resistance.py -q
```

## 관련 문서

- [Data / DB Pipeline Flow](../architecture/DATA_DB_PIPELINE_FLOW.md)
- [Inflation / Policy Engine Flow](../architecture/INFLATION_POLICY_ENGINE_FLOW.md)
- [DB Schema Map](../data/DB_SCHEMA_MAP.md)
- [Automation Scripts Guide](./AUTOMATION_SCRIPTS.md)
- [Inflation Policy Yield Path phase](../../phases/active/inflation-policy-yield-path/PLAN.md)
