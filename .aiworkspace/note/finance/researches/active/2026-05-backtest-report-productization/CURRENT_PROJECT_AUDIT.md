# Current Project Audit

## Snapshot

현재 finance 프로젝트는 단순 백테스트 실행 도구를 넘어, 전략 후보를 만들고 검증한 뒤 최종 선택과 모니터링으로 이어지는 workflow를 갖고 있다.

현행 durable product flow:

```text
Ingestion -> Backtest Analysis -> Practical Validation -> Final Review -> Selected Portfolio Dashboard
```

백테스트 결과와 리포트에 직접 관련된 로컬 근거는 다음 위치에 있다.

| Area | Local evidence | Current role |
| --- | --- | --- |
| Result display | `app/web/backtest_result_display.py` | Streamlit에서 summary metric, chart, warning, data trust를 표시 |
| Runtime history | `app/web/runtime/history.py` | backtest run history append/read helper |
| Performance summary | `finance/performance.py` | CAGR, standard deviation, Sharpe, maximum drawdown 등 기본 성과 요약 |
| Backtest reports | `.aiworkspace/note/finance/reports/backtests/` | 사람이 읽는 strategy/runs/validation report workspace |
| Report template | `.aiworkspace/note/finance/reports/backtests/TEMPLATE.md` | 수동/반수동 report 작성 기준 |
| Runtime flow docs | `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` | backtest result bundle, metadata, warning, data trust 흐름 |
| Final/selected replay | `app/web/backtest_practical_validation_replay.py`, `app/web/runtime/final_selected_portfolios.py` | validation/final selection evidence를 다시 읽는 구조 |

## Existing Strengths

| Strength | Why it matters |
| --- | --- |
| Evidence-first product direction | 단순 수익률이 아니라 data trust, validation, final decision까지 연결할 수 있다. |
| Report workspace already exists | `reports/backtests` 아래에 strategy hub, run report, validation report 위치가 준비되어 있다. |
| Result bundle carries useful context | summary, meta, warnings, chart data, data trust metadata를 report source로 활용할 수 있다. |
| Final Review / Selected Dashboard까지 이어짐 | "좋은 전략인지"에서 끝나지 않고 "왜 선택했는지"까지 연결할 수 있다. |
| Registry and saved setup boundaries exist | report가 source-of-truth를 덮어쓰지 않고 read model로 동작할 수 있다. |

## Surface Classification

| Surface | Classification | Notes |
| --- | --- | --- |
| Backtest Analysis result screen | Mixed | 사용자가 보는 핵심 화면이지만 실험/디버그 정보도 함께 있다. |
| Backtest Run History | Internal / ops leaning | run replay와 조사에는 유용하지만, 외부 사용자용 report library로 보기에는 아직 거칠다. |
| `reports/backtests` Markdown docs | Mixed | 사람이 읽을 수 있지만 현재는 product artifact보다 작업/분석 문서에 가깝다. |
| Practical Validation replay | User-facing candidate | 전략 채택 근거를 보여주는 제품 surface로 발전 가능하다. |
| Final Review | User-facing candidate | decision evidence와 limitation을 묶는 report viewer 후보가 된다. |
| Selected Portfolio Dashboard | User-facing candidate | 최종 선택 결과를 다시 열람하는 read-only dashboard 후보가 된다. |
| Ops Review / ingestion / registry inspection | Internal | Streamlit 내부 research/ops console로 남기는 편이 적합하다. |

## Weaknesses

| Weakness | Impact |
| --- | --- |
| Stable `BacktestReportPack` contract가 없다 | UI, Markdown report, future API/Next.js viewer가 같은 report object를 읽기 어렵다. |
| report 생성 경로가 수동 문서 중심이다 | 좋은 결과가 나와도 일관된 report artifact로 저장/재열람하기 어렵다. |
| run history, registry, report docs의 link model이 약하다 | 어떤 report가 어떤 run/validation/decision에서 왔는지 추적성이 약해질 수 있다. |
| 성과 metric set이 외부 benchmark 대비 좁다 | core summary는 CAGR, volatility, Sharpe, MDD 중심이고 Sortino, Calmar, rolling, drawdown period, alpha/beta 등은 report-ready로 정리되지 않았다. |
| export/share surface가 없다 | Markdown workspace는 있지만 제품 관점의 shareable report, download, stable report id가 없다. |
| report QA 기준이 분산되어 있다 | stale data, missing benchmark, period mismatch, NOT_RUN validation 같은 제한사항이 한 리포트 안에 고정적으로 드러나야 한다. |
| possible path drift가 있다 | `app/web/runtime/history.py`가 `.note/finance` 경로를 참조하는 것으로 보여, canonical `.aiworkspace/note/finance`와의 정합성 확인이 필요하다. |

## Report Readiness

현 프로젝트는 report productization의 재료는 이미 많다. 다만 아직 "리포트"가 독립 객체로 존재하지 않는다.

현재는 다음처럼 흩어져 있다.

```text
Streamlit latest result
  + run history JSONL
  + reports/backtests Markdown workspace
  + validation/final review replay
  + registry/saved source rows
```

다음 단계의 핵심은 이 재료를 바로 UI로 옮기는 것이 아니라, 먼저 다음 계약을 만드는 것이다.

```text
BacktestReportPack
  metadata
  source links
  input assumptions
  performance metrics
  benchmark comparison
  chart-ready series
  data trust / warnings
  validation / final review links
  limitations
  next action
```

## Audit Conclusion

백테스트 결과 리포트 제품화는 현재 프로젝트 방향과 잘 맞는다. 특히 `reports/backtests`가 이미 존재하므로 새 제품 개념을 억지로 붙이는 것이 아니라, 기존 결과와 evidence workflow를 durable report artifact로 묶는 작업에 가깝다.

다만 1차 구현은 큰 viewer나 export가 아니라 `BacktestReportPack` contract와 Markdown draft generator가 적절하다. 이 순서가 registry/source-of-truth를 건드리지 않으면서도 실제 사용 가능한 제품 surface로 가는 가장 작은 단계다.
