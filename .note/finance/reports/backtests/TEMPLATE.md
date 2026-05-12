# Backtest Report Template

Status: Template
Last Verified: 2026-05-12

## Title

`YYYY-MM-DD_<strategy-or-candidate>_<goal>.md`

## Metadata

| Field | Value |
|---|---|
| Created | YYYY-MM-DD |
| Source Session | main / candidate-search / ux-ui-polishing / other |
| Report Type | run / candidate_evidence / validation / strategy_log_entry |
| Related Registry ID | optional |
| Related Saved Setup | optional |

## 이걸 하는 이유?

이 report가 어떤 판단을 돕기 위해 만들어졌는지 적는다.

## Inputs

| 항목 | 값 |
|---|---|
| Period | |
| Universe | |
| Benchmark | |
| Strategy / Portfolio | |
| Rebalance | |
| Major Settings | |

## Result Summary

| Metric | Result | Interpretation |
|---|---:|---|
| CAGR | | |
| MDD | | |
| Sharpe / Sortino | | |
| Benchmark Spread | | |
| Promotion / Guardrail | | |

## Interpretation

- 결과가 후보 판단에 어떤 의미가 있는지 적는다.
- 단순히 수치가 좋다/나쁘다가 아니라, 왜 다시 볼 가치가 있는지 또는 왜 제외해야 하는지 적는다.

## Limitations

- 데이터 범위, look-ahead risk, survivorship risk, provider gap, proxy 사용 여부를 적는다.

## Next Action

- strategy log append
- candidate evidence 승격
- registry 반영
- 추가 backtest 필요
- discard

## Verification

실행한 명령, UI 경로, 데이터 기준일을 적는다.
