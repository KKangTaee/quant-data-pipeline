# Overview Futures Macro Mixed Substates V1 Plan

## Goal

`Workspace > Overview > Futures Macro`에서 자주 보이는 `혼재된 매크로 흐름`을 더 행동 가능한 read-only context로 쪼갠다. 현재 선물 일봉 score만 사용하며, macro 전문성 보강 2차(FRED / VIX / credit spread)는 이번 범위에서 제외한다.

## 이걸 하는 이유?

현재 futures macro scenario는 명확한 risk-on / risk-off / rate / inflation 조합이 아니면 대부분 `혼재된 매크로 흐름`으로 fallback한다. 보수적인 판정 자체는 안전하지만, 사용자는 mixed가 어떤 종류의 mixed인지 읽기 어렵다. 이번 차수는 mixed 상태를 하위 유형으로 분해해 “왜 아직 확정 scenario가 아닌지”와 “현재 무엇이 충돌하는지”를 바로 보이게 한다.

## Scope

- `generate_market_interpretation`에 mixed 하위 상태를 추가한다.
- 큰 scenario label은 기존 `혼재된 매크로 흐름`을 유지해 기존 validation / compatibility를 보존한다.
- summary, evidence, UI brief model에서 `sub_scenario`, `regime_hint`, `mixed_reason` 같은 보조 copy를 노출한다.
- service contract tests로 대표 mixed 유형을 고정한다.
- durable docs와 task logs를 정렬한다.

## Out Of Scope

- FRED `T10Y3M`, `VIXCLS`, `BAA10Y`, real yield, breakeven inflation score 추가.
- provider / DB schema / ingestion / registry / saved JSONL 변경.
- trading signal, recommendation, Practical Validation gate, monitoring signal, broker order, auto rebalance 의미 추가.
- 기존 historical validation hit rule을 mixed 방향성 예측으로 바꾸는 일.

## Stop Condition

- Mixed 상태가 최소 4개 하위 context로 분류된다.
- Existing directional scenario labels remain unchanged.
- Focused contract tests, py_compile, `git diff --check`, and Browser QA complete.
