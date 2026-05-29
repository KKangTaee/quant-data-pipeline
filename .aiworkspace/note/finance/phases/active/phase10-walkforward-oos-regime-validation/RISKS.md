# Phase 10 Walk-forward / OOS / Regime Validation Risks

Status: Active
Created: 2026-05-29

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| In-sample overfit remains hidden | 좋은 전체기간 백테스트를 deployable 후보로 과대평가 | OOS / walk-forward evidence를 Final Review gate에 연결 |
| Period is too short for split validation | 임의 split이 오히려 잘못된 판단을 만들 수 있음 | insufficient period를 `REVIEW` 또는 `NEEDS_INPUT`으로 표시 |
| Regime source is missing or stale | regime split이 임의 라벨링이 될 수 있음 | DB / macro loader source map 후 구현 |
| Benchmark parity is weak | strategy / benchmark 비교가 같은 기간을 보지 않을 수 있음 | split contract에 benchmark coverage와 aligned period 포함 |
| Storage sprawl returns | 의미 없는 JSONL / memo / preset 저장이 늘어남 | compact evidence read model 우선, raw data는 DB boundary로 제한 |
| User confuses selected-route with live trading approval | 검증 화면이 주문 승인처럼 보일 수 있음 | Final Review / Selected Dashboard는 live approval, order, rebalance가 아님을 유지 |
| Proxy-only walk-forward evidence is over-trusted | DB price proxy can differ from actual strategy path | Carry curve source strength and avoid proxy-only PASS |
| Runtime OOS metadata diverges from Practical Validation audit | Same candidate can show different temporal review semantics | Build a service-level compact temporal validation contract and reuse it |

## Residual Unknowns For 10-1

- 현재 result bundle curve가 모든 후보 유형에서 enough monthly / daily returns를 제공하는지 확인이 필요하다.
- Macro regime bucket을 현재 loader만으로 만들 수 있는지, 추가 free API / public source가 필요한지 확인이 필요하다.
