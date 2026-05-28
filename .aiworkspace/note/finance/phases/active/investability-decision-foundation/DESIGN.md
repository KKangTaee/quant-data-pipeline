# Investability Decision Foundation Design

Status: Active
Created: 2026-05-28

## Design Summary

이 phase의 설계 기준은 간단하다.
Backtest 결과를 더 많이 저장하는 대신, 하나의 판단이 어떤 데이터와 검증을 거쳐 나온 것인지 더 엄격하게 읽는다.

```text
Backtest source
  -> Practical Validation result
  -> Final Review investability packet
  -> selected-route gate
  -> read-only Selected Portfolio Dashboard / optional monitoring snapshot
```

## Storage Policy

새 JSONL 저장 기능은 기본적으로 추가하지 않는다.

허용되는 경우:

- workflow의 source-of-truth append-only registry인 경우
- 사용자가 명시적으로 재사용할 saved portfolio setup인 경우
- Final Review decision row처럼 최종 판단 record에 compact evidence snapshot을 붙이는 경우
- Selected Portfolio Dashboard에서 사용자가 명시적으로 monitoring snapshot 저장을 누른 경우

금지하거나 후순위로 둔다.

- 단계 이동마다 같은 내용을 반복 저장하는 기능
- 사용자 free-form memo를 따로 모으는 JSONL
- raw provider response, full holdings row, full macro series를 JSONL에 저장하는 기능
- run history / run artifact를 장기 판단 record처럼 승격하는 기능
- source-of-truth가 아닌 derived display cache JSONL

기본 위치:

| Data type | Durable location |
| --- | --- |
| Selection source | `.aiworkspace/note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl` |
| Practical Validation result | `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl` |
| Final decision | `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` |
| Saved reusable setup | `.aiworkspace/note/finance/saved/` |
| Optional monitoring snapshot | `.aiworkspace/note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` |
| Provider / holdings / macro raw-ish data | MySQL DB through `finance/data/*` and loaders |
| Local execution history | `.aiworkspace/note/finance/run_history/`, not durable product decision |

## Validation Gate Policy

`SELECT_FOR_PRACTICAL_PORTFOLIO`는 live approval이 아니라 `실전 검토 통과 후보`다.
그래도 아래 gap이 있으면 selected route를 막는 것이 기본 정책이다.

| Condition | Default Handling |
| --- | --- |
| hard blocker | selected route blocked |
| missing core price / malformed critical source | selected route blocked |
| invalid or missing component weight contract | selected route blocked |
| critical Practical Validation diagnostic is `NOT_RUN` | selected route blocked |
| benchmark parity missing for benchmarked profile | selected route blocked or re-review |
| provider / holdings / operability coverage is proxy-only for major allocation | hold or re-review by default |
| leveraged / inverse ETF without objective and holding-period evidence | selected route blocked |
| paper observation blocker remains | selected route blocked |
| assumptions / limitations only | selectable only when no critical blocker remains |

Waiver policy:

- V1 does not implement waiver.
- Until a structured waiver exists, critical gap means selected route is blocked.
- A future waiver task may allow selected route only with reason, expiry or re-review date, monitoring trigger, and explicit critical-gap acknowledgement.
- Waiver must never become a generic "user said okay" memo field.

## Critical Diagnostic Candidate Set

초기 critical 후보는 아래 영역이다.
세부 profile별 matrix는 `validation-gate-hardening-v1`에서 확정한다.

| Area | Why Critical |
| --- | --- |
| Data Trust / Source Contract | 데이터가 틀리면 이후 판단이 무의미하다 |
| Benchmark Parity | 비교 기준이 없거나 기간이 다르면 백테스트 해석이 약해진다 |
| Provider / Operability | ETF 비용, 규모, 유동성, 거래 가능성을 확인해야 한다 |
| Holdings / Exposure Look-through | 겉보기 비중과 실제 underlying exposure가 다를 수 있다 |
| Stress / Scenario | 특정 시장 구간에서의 취약성을 확인해야 한다 |
| Robustness / Sensitivity / Overfit | parameter, window, component 의존도를 확인해야 한다 |
| Leveraged / Inverse Suitability | 목적과 보유 기간이 없으면 실전 검토 위험이 크다 |
| Paper Observation | 선택 전 관찰 공백이 남아 있으면 tracking 대상 의미를 분명히 해야 한다 |

## Data Acquisition Policy

데이터가 부족할 때의 기본 순서:

1. 무료 API 또는 공식 source가 있는지 먼저 확인한다.
2. 있으면 `finance/data/*` ingestion job으로 수집하고 DB에 저장한다.
3. 무료 API가 없으면 검증 가능한 웹 source를 찾고, crawler/parser를 ingestion layer에 둔다.
4. crawler 결과도 DB에 저장하고 source / endpoint / collected_at / as_of_date / parser version / coverage status를 남긴다.
5. loader가 compact context를 만들고, service가 validation evidence로 변환한다.
6. UI는 부족 데이터와 수집 버튼을 보여주지만 remote source를 직접 fetch하지 않는다.

필수 provenance 후보:

| Field | Meaning |
| --- | --- |
| `source_name` | provider, issuer, FRED, exchange, or official page name |
| `source_url` | API endpoint or crawled page URL when applicable |
| `collected_at` | ingestion time |
| `as_of_date` | source data effective date when available |
| `coverage_status` | actual / bridge / proxy / missing |
| `parser_version` | crawler/parser contract version when applicable |
| `symbol_scope` | symbols covered by this snapshot |
| `staleness_days` | age from latest available source date |

## UX / Wording Policy

사용자-facing 표현은 투자 승인처럼 들리지 않게 한다.

| Avoid | Prefer |
| --- | --- |
| 투자 가능 후보 | 실전 검토 통과 후보 |
| live readiness | Final Review 입력 준비 또는 실전 검토 readiness |
| 승인 / 주문 / 실행 | 선정 / 관찰 / 재검토 / monitoring |
| 자동 리밸런싱 | drift preview / review trigger |

Final Review와 Selected Dashboard는 항상 아래 경계를 유지한다.

- 투자 조언이 아니다.
- 미래 수익 보장이 아니다.
- broker order를 만들지 않는다.
- account holding 자동 연결을 하지 않는다.
- auto rebalance를 하지 않는다.

## Implementation Boundary

| Domain | Owner Skill | Notes |
| --- | --- | --- |
| Final Review / packet / gate UI | `finance-backtest-web-workflow` | service read model first, UI render second |
| provider / macro / holdings persistence | `finance-db-pipeline` | ingestion -> DB -> loader -> service |
| robustness / sensitivity runtime | `finance-strategy-implementation` plus backtest workflow | proven existing runtime preferred |
| documentation sync | `finance-doc-sync` | roadmap, flow, root logs only after scope changes |
| integration review | `finance-integration-review` | use before merging broad cross-domain changes |
