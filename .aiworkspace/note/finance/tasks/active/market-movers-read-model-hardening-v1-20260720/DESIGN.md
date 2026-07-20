# Market Movers Read-Model Hardening V1 Design

Status: Implementation Plan Ready
Last Updated: 2026-07-20

## 이걸 하는 이유?

승인된 변동 종목 A안은 ranking, 확산 맥락, 선택 종목 조사를 한 shell에서 연결한다. UI부터 바꾸면 현재 raw sector alias, 불명확한 missing denominator, return leader와 대장주의 혼용, 잘못된 historical PER가 새 화면에 그대로 고정된다. 3차는 이 의미를 먼저 교정한다.

## Source Design

- `.aiworkspace/note/finance/researches/active/2026-06-market-movers-redesign-v2-benchmark/RECOMMENDATION.md`

## Boundary

- service façade는 기존 함수명을 유지한다.
- 새 pure read-model module이 의미와 상태를 소유한다.
- web payload adapter는 JSON 변환만 소유한다.
- React shell은 4차에 구현한다.
- conditional outlook은 5차에 구현한다.

## Data Flow

```text
DB / existing loaders
  -> market_movers.py / why_it_moved.py façades
  -> taxonomy / readiness / group flow / research read models
  -> market_movers_decision_payload_v1
  -> Phase 4 React shell
```

## Key Decisions

- sector는 canonical 11-sector로 filter/group 전에 정규화한다.
- industry는 provider label을 stable display key로만 정리하며 GICS equivalence를 주장하지 않는다.
- market-cap Top 3와 positive-return leader는 별도 계약이다.
- current flow는 evidence state이며 forecast가 아니다.
- historical PER는 제거한다.
- current PER는 PIT filing ledger에서 reported diluted EPS 네 분기가 모두 있을 때만 계산한다.
