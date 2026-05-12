# Phase 18 Value Fill Anchor-Near Follow-Up Second Pass

## 목적

- `Fill Rejected Slots With Next Ranked Names` contract를
  `Value` current practical anchor 근처에 더 직접 적용하면
  same-gate lower-MDD rescue가 가능한지 다시 확인한다.
- first structural probe가 아니라,
  current best practical point에 가장 가까운 후보군만 좁게 다시 본다.

## 탐색 범위

공통 contract:

- `2016-01-01 ~ 2026-04-01`
- `US Statement Coverage 100`
- `Historical Dynamic PIT Universe`
- `Trend Filter = on`
- `rejected_slot_fill_enabled = on`
- `partial_cash_retention_enabled = false`
- `risk_off_mode = cash_only`
- `Market Regime = off`
- practical benchmark / liquidity / validation / guardrail contract 유지

factor / top-N 범위:

- `base + psr`
  - `Top N = 12 / 13 / 14 / 15 / 16`
- `base + psr + pfcr`
  - `Top N = 12 / 13 / 14 / 15 / 16`

## 결과 요약

| label | CAGR | MDD | Promotion | Shortlist | Deployment |
|---|---:|---:|---|---|---|
| `base + psr`, `Top N = 12` | `24.67%` | `-31.12%` | `hold` | `hold` | `blocked` |
| `base + psr`, `Top N = 13` | `24.63%` | `-29.48%` | `hold` | `hold` | `blocked` |
| `base + psr`, `Top N = 14` | `25.23%` | `-28.37%` | `hold` | `hold` | `blocked` |
| `base + psr`, `Top N = 15` | `24.94%` | `-29.29%` | `hold` | `hold` | `blocked` |
| `base + psr`, `Top N = 16` | `24.67%` | `-28.41%` | `hold` | `hold` | `blocked` |
| `base + psr + pfcr`, `Top N = 12` | `25.22%` | `-26.10%` | `hold` | `hold` | `blocked` |
| `base + psr + pfcr`, `Top N = 13` | `24.47%` | `-24.89%` | `hold` | `hold` | `blocked` |
| `base + psr + pfcr`, `Top N = 14` | `23.63%` | `-26.94%` | `hold` | `hold` | `blocked` |
| `base + psr + pfcr`, `Top N = 15` | `22.37%` | `-27.95%` | `hold` | `hold` | `blocked` |
| `base + psr + pfcr`, `Top N = 16` | `22.62%` | `-27.46%` | `hold` | `hold` | `blocked` |

## 해석

이번 second pass 결론은 분명하다.

1. `Value` current practical anchor 근처에서는
   fill contract가 gate rescue를 만들지 못했다
2. best lower-MDD near-miss는
   `base + psr + pfcr`, `Top N = 13`
   의 `24.47% / -24.89%`였지만,
   여전히 `hold / blocked`였다
3. current practical anchor
   `28.13% / -24.55% / real_money_candidate / paper_probation / review_required`
   를 대체할 조합은 없었다

## 결론

- `next-ranked eligible fill`은
  current first pass 기준
  “실제로 써볼 가치가 있는 구조 레버”인 것은 맞다
- 하지만 `Value` practical anchor 근처에서 다시 좁혀본 second pass까지 포함하면,
  **same-gate lower-MDD rescue는 아직 없다**

즉 지금 읽는 게 맞다:

- `Value` current practical anchor는 그대로 유지
- `next-ranked eligible fill`은
  다음 larger redesign lane을 여는 참고 evidence로 남김
