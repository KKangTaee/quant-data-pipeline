# DESIGN - Validation Gate Hardening V1

Status: Active
Created: 2026-05-28

## Design Shape

V1은 기존 packet을 대체하지 않고, packet 안에 policy 해석 layer를 추가한다.

```text
validation result + diagnostics + paper observation
  -> investability evidence packet
  -> gate policy snapshot
  -> save evaluation for selected / hold / reject / re-review
```

## Gate Outcomes

| Outcome | Meaning |
| --- | --- |
| `select_ready` | critical blocker가 없고 selected route 저장 가능 |
| `hold_or_re_review` | selected route는 막고 hold / re-review로 유도 |
| `blocked` | selected route는 막고 blocker 해소 또는 reject 판단 필요 |

## Policy Group Model

각 check / gap은 아래 group 중 하나에 묶는다.

| Group | Examples |
| --- | --- |
| `data_trust` | missing core price, malformed source, invalid weight |
| `benchmark` | benchmark parity missing, benchmark coverage gap |
| `provider_coverage` | provider / holdings / exposure / operability missing or proxy-only |
| `stress_robustness` | stress, rolling, sensitivity, overfit diagnostics not run |
| `leveraged_inverse` | leveraged / inverse suitability gap |
| `paper_observation` | paper observation blocker |
| `assumption_only` | disclosure-only limitations |

## Profile Defaults

V1 profile policy is intentionally conservative.

| Profile | Critical groups |
| --- | --- |
| defensive | data trust, benchmark, provider coverage, stress robustness, leveraged inverse, paper observation |
| balanced | data trust, benchmark, provider coverage, stress robustness, leveraged inverse, paper observation |
| growth | data trust, benchmark, provider coverage, stress robustness, leveraged inverse |
| tactical hedge | data trust, benchmark, provider coverage, stress robustness, leveraged inverse |
| custom | same as balanced unless future profile config overrides |

Paper observation remains critical for defensive / balanced profiles and review-required for growth / tactical hedge in V1.
If the existing packet already emits a paper blocker, selected route remains blocked.

## Waiver

No waiver UI or persistence is implemented in this task.
The policy snapshot may expose `waiver_supported=false` and `waiver_required_for_select=true` when a future version could support it.

## Persistence

Final decision row may include:

- `investability_evidence_packet`
- `gate_policy_snapshot`

It must not include full provider holdings, macro series, crawler output, or raw diagnostic payloads beyond compact evidence already present.
