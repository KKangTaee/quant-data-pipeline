# Feature Candidates

Scoring: 1 low, 5 high. `Priority`는 지금 시작할 순서다.

| Priority | Candidate | Impact | Effort | Risk | Confidence | Fit | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| P0 | `BacktestReportPack` contract | 5 | 3 | 3 | 5 | 5 | 바로 시작 |
| P0 | Markdown report draft generator | 4 | 3 | 2 | 4 | 5 | contract와 함께 |
| P1 | Report source/link model | 4 | 2 | 2 | 4 | 5 | report draft와 함께 |
| P1 | Report Library index | 3 | 2 | 2 | 4 | 4 | draft 생성 후 |
| P1 | Read-only Streamlit Strategy Report Viewer | 4 | 3 | 2 | 4 | 4 | 1차 viewer |
| P2 | Expanded report metrics | 4 | 4 | 3 | 4 | 4 | metric definition 후 |
| P2 | Final Review Evidence Report | 4 | 3 | 3 | 4 | 5 | validation/final review 연결 후 |
| P2 | Read-only Next.js Report Viewer | 4 | 4 | 3 | 3 | 5 | API contract 이후 |
| P3 | HTML/PDF export | 3 | 4 | 3 | 3 | 4 | report schema 안정화 후 |
| P3 | Trade/order detail report | 3 | 4 | 4 | 3 | 3 | simulation artifact 확장 후 |
| Park | AI narrative report writer | 3 | 4 | 4 | 2 | 3 | evidence summary로만 나중 |
| Park | Public share links / auth | 4 | 5 | 5 | 2 | 3 | product deployment 결정 후 |

## P0. `BacktestReportPack` Contract

Goal:

- 백테스트 결과를 Markdown, Streamlit, future API/Next.js viewer가 함께 읽을 수 있는 report read model로 만든다.

Recommended fields:

```text
report_id
generated_at
source_run
strategy
inputs
period
performance_summary
benchmark_summary
chart_series_refs
data_trust
validation_refs
decision_refs
warnings
limitations
next_action
artifact_paths
```

Why now:

- report productization의 가장 작은 안정 단위다.
- registry/run history를 덮어쓰지 않고 read-only artifact로 시작할 수 있다.
- 이후 Next.js/API 작업과도 연결된다.

Success criteria:

- 하나의 backtest result 또는 run history row에서 JSON-compatible report pack을 만들 수 있다.
- report pack은 Streamlit import 없이 테스트 가능하다.
- missing benchmark, stale data, NOT_RUN validation을 warning/limitation으로 표현할 수 있다.

## P0. Markdown Report Draft Generator

Goal:

- `BacktestReportPack`에서 `.aiworkspace/note/finance/reports/backtests/runs/YYYY/` 아래 Markdown draft를 생성한다.

First slice:

- 단일 strategy 또는 weighted portfolio 한 종류만 지원한다.
- 기존 `TEMPLATE.md` 구조를 따른다.
- chart 이미지는 생성하지 않고 chart-ready series 또는 source reference만 기록한다.

Output example:

```text
.aiworkspace/note/finance/reports/backtests/runs/2026/
  <YYYY-MM-DD>-<strategy-or-run-id>-report.md
```

Out of scope:

- PDF export
- HTML export
- chart image rendering
- registry rewrite
- final decision write

## P1. Report Source / Link Model

Goal:

- report가 어떤 run, validation, final review, registry row에서 왔는지 추적 가능하게 한다.

Minimum links:

| Field | Meaning |
| --- | --- |
| `run_id` | backtest run identifier if available |
| `history_path` | source run history JSONL |
| `report_path` | generated Markdown report path |
| `validation_id` | Practical Validation artifact if available |
| `decision_id` | Final Review decision if available |
| `registry_refs` | source registry row references if available |

Why:

- report가 문서로만 남으면 시간이 지나면서 source drift가 생긴다.
- source link가 있으면 report viewer, library, QA가 쉬워진다.

## P1. Report Library Index

Goal:

- 생성된 report를 다시 찾을 수 있는 index를 만든다.

Minimum columns:

```text
report_id
title
strategy_or_portfolio
generated_at
period
cagr
sharpe
max_drawdown
validation_status
warning_count
report_path
source_run
```

Potential location:

- 처음에는 `reports/backtests/INDEX.md` 갱신 또는 별도 generated index 검토
- registry 성격이 강해지면 append-only JSONL은 별도 승인 후 검토

## P1. Read-Only Streamlit Strategy Report Viewer

Goal:

- 기존 Streamlit 내부 console 안에서 report pack을 읽고 제품형 report layout을 실험한다.

Why Streamlit first:

- report contract가 안정되기 전에 Next.js를 바로 만들면 UI 작업이 schema 변경에 흔들릴 수 있다.
- 기존 사용자가 바로 확인할 수 있다.

Exit criteria:

- viewer가 쓸만하면 Next.js read-only viewer 후보로 승격한다.
- viewer가 불편하면 contract와 content hierarchy부터 고친다.

## P2. Expanded Report Metrics

Candidates:

- Sortino ratio
- Calmar ratio or return over max drawdown
- rolling Sharpe / rolling volatility
- monthly/yearly return table
- drawdown period table
- benchmark beta/alpha/information ratio
- turnover / exposure if source data exists

Rule:

- metric definition과 data availability를 먼저 문서화한다.
- 계산할 수 없는 metric은 빈 값으로 숨기지 않고 `not available`과 reason을 남긴다.

## P2. Final Review Evidence Report

Goal:

- Backtest report를 Practical Validation과 Final Review decision까지 연결한다.

Why:

- 이 프로젝트의 차별점은 "성과가 좋음"보다 "선택 근거가 검증됨"에 있다.

Minimum content:

- final decision
- decision reason
- validation status
- failed/not-run checks
- required re-review triggers
- source report links

## P2. Read-Only Next.js Report Viewer

Goal:

- API/service contract 이후, report pack을 read-only product UI로 보여준다.

Why later:

- Stage 2 UI platform research의 추천과 연결된다.
- 다만 지금은 report content contract가 먼저다.

## P3. HTML/PDF Export

Goal:

- strategy report를 외부 공유 가능한 HTML/PDF로 내보낸다.

Why later:

- export는 content와 contract가 안정된 뒤에 가치가 커진다.
- 초기부터 PDF를 만들면 layout QA와 chart rendering scope가 과도해진다.

## Parking Lot. AI Narrative Report Writer

AI narrative는 나중에 가능하지만, 다음 조건이 필요하다.

- structured report pack만 source로 사용한다.
- 모든 수치와 warning은 source field를 참조한다.
- 투자 추천 문장이나 live execution 문장을 만들지 않는다.
- generated narrative에는 "evidence summary" 성격을 명시한다.
