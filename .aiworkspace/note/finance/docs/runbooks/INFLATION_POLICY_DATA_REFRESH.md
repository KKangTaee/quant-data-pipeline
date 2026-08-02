# Inflation / Policy Point-in-Time Data Refresh

Status: Active
Last Verified: 2026-08-02

## 목적

Core PCE, FOMC SEP·정책 결정, 국채금리와 기간 프리미엄 원천을 UI나 기존 경제
사이클 결과에 의존하지 않고 MySQL의 독립 Point-in-Time 원장으로 갱신한다. 이
절차는 raw context만 수집하며 확률·저항대·주가 스트레스 결과를 계산하지 않는다.

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

## 기대 결과

출력은 한 줄 JSON이다.

- `materialization_allowed=true`: 필수 source와 필수 series가 모두 존재한다.
- `status=success`: 필수·선택 source가 모두 준비됐다.
- `status=partial_success`: 필수 경로는 준비됐지만 BEA 구성항목 또는 ACM 같은
  선택 source가 `LIMITED`/`NOT_AVAILABLE`이다.
- `required_series_gaps=[]`: `PCEPILFE`, `DGS2`, `DGS10`, `DFII10`, `T10YIE`
  필수 입력에 누락이 없다.
- `failed_sources=[]`: FRED/ALFRED, SEP, FOMC 결정 필수 수집기가 성공했다.

2026-08-02 실제 source smoke에서는 26개 FRED/ALFRED series, 2021~2026 SEP와
2026 FOMC 결정 5건을 적재했고 `materialization_allowed=true`였다. `BEA_API_KEY`
부재로 PCE 구성항목은 `NOT_AVAILABLE`, 현재 ACM workbook은 과거 공개 빈티지를
복원할 수 없어 term premium은 `LIMITED`였다.

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

집중 검증:

```bash
.venv/bin/python -m pytest \
  tests/test_fred_vintages.py \
  tests/test_inflation_policy_catalog.py \
  tests/test_bea_pce_components.py \
  tests/test_fomc_policy_data.py \
  tests/test_nyfed_term_premium.py \
  tests/test_inflation_policy_loaders.py \
  tests/test_inflation_policy_refresh.py -q
```

## 관련 문서

- [Data / DB Pipeline Flow](../architecture/DATA_DB_PIPELINE_FLOW.md)
- [DB Schema Map](../data/DB_SCHEMA_MAP.md)
- [Automation Scripts Guide](./AUTOMATION_SCRIPTS.md)
- [Inflation Policy Yield Path phase](../../phases/active/inflation-policy-yield-path/PLAN.md)
