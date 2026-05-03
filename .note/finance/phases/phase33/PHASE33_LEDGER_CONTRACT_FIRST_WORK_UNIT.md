# Phase 33 Ledger Contract First Work Unit

## 목적

Phase 33의 첫 번째 작업은 `Paper Portfolio Tracking Ledger` row 계약과 저장소 경계를 확정하는 것이다.

## 쉽게 말하면

paper tracking 장부 한 줄에 무엇을 적을지 먼저 정한다.
후보나 proposal을 실제 돈 없이 관찰하려면,
무엇을 언제부터 어떤 비중과 기준으로 추적하는지 남아 있어야 한다.

## 왜 필요한가

- 저장 row 계약 없이 UI부터 만들면 나중에 Phase 34 final selection이 읽을 근거가 흔들린다.
- paper tracking은 단순 memo가 아니라 시작 조건, benchmark, review cadence, 재검토 trigger를 포함해야 한다.
- current candidate registry, Pre-Live registry, Portfolio Proposal registry와 paper ledger를 분리해야 한다.

## 예상 저장소

- `.note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`

이 저장소는 append-only paper tracking record를 위한 별도 장부다.
기존 candidate / Pre-Live / Portfolio Proposal registry를 덮어쓰지 않는다.

## 예상 row 핵심 필드

- `ledger_id`
- `schema_version`
- `created_at`
- `updated_at`
- `paper_status`
- `source_type`
- `source_id`
- `source_title`
- `tracking_start_date`
- `tracking_benchmark`
- `review_cadence`
- `target_components`
- `phase32_handoff_snapshot`
- `baseline_snapshot`
- `tracking_rules`
- `review_triggers`
- `operator_note`

## 이번 작업에서 하지 않는 것

- paper PnL 시계열을 계산하지 않는다.
- live approval이나 주문 지시를 만들지 않는다.
- Phase 34 final selection decision을 만들지 않는다.
- 기존 registry row를 수정하지 않는다.

## 완료 기준

- paper ledger row schema가 코드와 문서에서 같은 의미로 읽힌다.
- Phase 32 handoff에서 paper ledger draft를 만들 수 있다.
- 저장소 경계가 current candidate / Pre-Live / Portfolio Proposal registry와 분리된다.
