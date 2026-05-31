# Selected Provider Evidence Staleness Contract V1 Plan

Status: Complete
Created: 2026-05-29
Completed: 2026-05-29

## Goal

Selected Portfolio Dashboard의 Provider Evidence가 selected component ticker weight 기준 provider holdings / exposure / operability freshness와 coverage를 일관된 read-only contract로 표시하게 한다.

이걸 하는 이유?

- 선정 이후 provider holdings / exposure snapshot이 낡거나 부분 coverage이면 최종 선정 당시 판단을 그대로 유지할 수 없다.
- 기존 Provider Evidence는 DB read model을 갖고 있었지만, `Diagnostic Status`가 PASS인 row도 freshness / coverage field가 stale 또는 partial이면 selected monitoring에서는 review로 봐야 한다.
- 이 작업은 provider evidence 해석 강화이며, provider 수집 실행이나 monitoring log 저장 기능을 추가하지 않는다.

## Scope

- Selected Provider Evidence staleness contract 추가
- Provider display row의 diagnostic status, coverage, coverage weight, freshness를 함께 반영
- ETF Operability / ETF Holdings / ETF Exposure 필수 area 누락을 `NEEDS_INPUT`으로 표시
- Look-through board coverage를 selected monitoring policy row로 추가
- Dashboard Provider Evidence badge / table에 stale / partial / policy reason 표시
- Focused service contract tests 추가

## Out Of Scope

- 새 JSONL registry
- monitoring log 자동 저장
- user memo / preset / comment persistence
- provider 수집 버튼 또는 UI direct provider fetch
- DB schema / provider loader 변경
- broker order, live approval, auto rebalance
- account holdings 자동 연결

## Completion Criteria

- fresh actual operability / holdings / exposure evidence는 ready로 유지된다.
- stale actual evidence는 `REVIEW`로 낮아진다.
- partial / bridge / proxy coverage는 `REVIEW`로 낮아진다.
- missing required provider area와 missing holdings / exposure coverage는 `NEEDS_INPUT`으로 남는다.
- fallback symbol source는 `REVIEW`로 남는다.
- Execution boundary는 DB read-only, no DB write, no registry write, no monitoring log auto write, no approval / order / auto rebalance를 유지한다.
