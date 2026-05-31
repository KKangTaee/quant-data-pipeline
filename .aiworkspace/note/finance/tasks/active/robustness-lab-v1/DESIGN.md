# Robustness Lab V1 Design

Status: Active
Created: 2026-05-28

## Design Summary

Robustness Lab은 새 계산 엔진이 아니라 기존 Practical Validation diagnostics의 read model이다.

```text
stress window rows
rolling validation
sensitivity rows
overfit audit
  -> robustness_lab_board
  -> Practical Validation display
  -> Final Review display
  -> final decision evidence rows
```

## Data Shape

`robustness_validation.robustness_lab_board`에 compact dict를 둔다.

핵심 필드:

- `schema_version`
- `status`
- `summary`
- `summary_rows`
- `stress_rows`
- `sensitivity_rows`
- `follow_up_rows`
- `metrics`
- `limitations`

## Storage Boundary

- full run history와 raw strategy-specific perturbation output은 저장하지 않는다.
- workflow JSONL에는 compact row만 들어간다.
- board는 기존 Practical Validation result의 일부이므로 새 registry를 만들지 않는다.

## UI Boundary

- Practical Validation은 board를 사용해 stress / sensitivity 근거를 먼저 보여준다.
- Final Review는 같은 board를 요약해서 최종 판단 근거로 읽는다.
- Final Review는 여전히 후보 선정 판단이며 live approval이 아니다.
