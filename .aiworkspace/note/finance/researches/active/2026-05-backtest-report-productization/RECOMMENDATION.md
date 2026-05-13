# Recommendation

## One-Line Recommendation

백테스트 결과 제품화의 다음 단계는 큰 UI를 새로 만드는 것이 아니라, `BacktestReportPack` contract를 만들고 그 contract에서 Markdown 전략 리포트 초안을 생성하는 것이다.

## Why This Direction

현재 프로젝트에는 백테스트 결과를 리포트로 만들 재료가 이미 있다.

- Streamlit 결과 화면
- run history
- performance summary
- data trust / warnings
- Practical Validation replay
- Final Review decision
- `reports/backtests` 문서 workspace

하지만 이 재료들이 아직 하나의 안정적인 report artifact로 묶이지 않았다. 이 상태에서 Next.js viewer, PDF export, AI report writer부터 만들면 표현층이 먼저 커지고 source-of-truth가 흔들릴 가능성이 높다.

따라서 1차 목표는 "보여주는 화면"이 아니라 "무엇을 보여줄지"를 고정하는 것이다.

```text
Backtest result / history row
  -> BacktestReportPack
      -> Markdown draft report
      -> Streamlit report viewer
      -> future API / Next.js / HTML / PDF
```

## Recommended 1st Build Scope

### Step 1. `BacktestReportPack` Contract

목표:

- 백테스트 결과를 report-ready object로 변환한다.
- Streamlit, Markdown, API, future Next.js viewer가 같은 object를 읽도록 한다.

Minimum fields:

| Field group | Examples |
| --- | --- |
| Identity | report_id, generated_at, generator_version |
| Source | run_id, history_path, source_result_kind, registry_refs |
| Strategy | strategy_name, universe, period, rebalance/input summary |
| Performance | CAGR, Sharpe, standard deviation, max drawdown, start/end balance |
| Benchmark | benchmark symbol, benchmark return, excess return if available |
| Evidence | data trust, validation refs, final review refs |
| Warnings | missing data, stale source, benchmark missing, NOT_RUN validation |
| Limitations | unavailable metrics, incomplete artifact, scope caveats |
| Artifacts | report_path, chart_series_refs, source links |

### Step 2. Markdown Draft Generator

목표:

- `BacktestReportPack`를 기존 `reports/backtests/TEMPLATE.md` 스타일의 Markdown으로 저장한다.

처음에는 다음만 지원한다.

- 단일 strategy 또는 weighted portfolio 1종
- 현재 가능한 metric만 표시
- chart image 생성 없음
- source/warning/limitation section 필수

저장 위치:

```text
.aiworkspace/note/finance/reports/backtests/runs/YYYY/
```

### Step 3. Report Source Link QA

목표:

- report가 어떤 run/validation/decision에서 왔는지 추적 가능하게 한다.

필수 QA:

- source run을 찾을 수 있는가?
- report generated_at이 있는가?
- benchmark가 없을 때 limitation이 표시되는가?
- Practical Validation이 `NOT_RUN`이면 pass처럼 보이지 않는가?
- report가 registry/source-of-truth를 덮어쓰지 않는가?

## Recommended Next Phase After 1st Build

1차가 성공하면 다음 순서가 좋다.

| Phase | Output | Why |
| --- | --- | --- |
| A | Streamlit read-only Strategy Report Viewer | contract를 빠르게 눈으로 검증 |
| B | Report Library index | 여러 report를 다시 찾을 수 있게 함 |
| C | Expanded metrics | Sortino, rolling, drawdown period 등 report 품질 강화 |
| D | Final Review Evidence Report | 선택/보류/탈락 근거까지 연결 |
| E | Next.js read-only Report Viewer | product-grade 공유 화면 검증 |
| F | HTML/PDF export | contract 안정화 이후 외부 공유 강화 |

## What Not To Do Yet

지금 하지 않는 것이 좋은 것:

- 전체 Backtest UI를 Next.js로 재작성
- PDF/HTML export부터 시작
- AI가 투자 결론을 작성하는 report
- public share link / auth / multi-user
- trade/order detail report를 억지로 만들기

이유:

- 현재 필요한 것은 report rendering보다 report source contract다.
- 아직 모든 strategy/run type의 artifact shape가 동일하지 않을 가능성이 높다.
- export와 public share는 QA와 보안 범위가 커진다.

## Decision Rules

Proceed to viewer when:

- 하나의 report pack에서 Markdown draft가 안정적으로 생성된다.
- source link와 warning/limitation이 빠지지 않는다.
- report pack이 Streamlit 없이 테스트된다.

Proceed to Next.js when:

- report pack schema가 최소 2개 이상의 run type에서 유지된다.
- chart-ready data contract가 있다.
- URL로 특정 report를 다시 열어야 할 사용자 가치가 분명하다.

Proceed to PDF/HTML export when:

- report content hierarchy가 확정된다.
- chart rendering과 layout QA 기준이 정해진다.
- 외부 공유/제출 use case가 실제로 있다.

## Final Recommendation

4단계 1번 리서치의 결론은 `BacktestReportPack + Markdown draft generator`를 다음 구현 후보로 잡는 것이다. 이 기능은 현재 프로젝트의 evidence-first 방향과 잘 맞고, Stage 2에서 논의한 API/Next.js product surface로 가기 위한 중간 계약도 된다.

즉, 다음 개발은 "예쁜 리포트 화면"보다 "믿을 수 있는 리포트 객체"를 먼저 만드는 방향이 가장 안전하다.
