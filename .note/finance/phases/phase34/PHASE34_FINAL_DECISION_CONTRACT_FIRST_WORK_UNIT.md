# Phase 34 Final Decision Contract First Work Unit

## 목적

Phase 34의 첫 번째 작업은 `Final Portfolio Selection Decision Pack`의 decision row 계약과 저장소 경계를 확정하는 것이다.

## 쉽게 말하면

최종 선정 판단 한 줄에 무엇을 적을지 먼저 정한다.
이 판단은 "실전 후보로 선정한다"는 검토 기록이지, broker 주문이나 자동매매 지시가 아니다.

## 2026-05-03 보정 후 현재 해석

이 문서는 Phase34 첫 구현 당시의 계약 초안이다.
이후 사용자 UX 검토를 반영해 main flow는 `Backtest > Final Review`로 분리됐고,
`source_paper_ledger_id`는 legacy / compatibility field로 남긴다.
현재 사용자-facing record는 단일 후보 또는 saved proposal을 source로 읽고,
paper observation 기준은 `source_observation_id`와 `paper_tracking_snapshot` 안에 포함한다.

## 왜 필요한가

- Phase 33의 paper ledger는 "관찰 대상으로 등록했다"는 기록이다.
- Phase 34는 그 관찰 기록을 읽고 `선정`, `보류`, `거절`, `재검토` 중 하나로 판단해야 한다.
- final decision 계약 없이 UI부터 만들면 최종 선정 기록이 live approval처럼 오해될 수 있다.
- 보류 / 거절 / 재검토도 중요한 결과이므로 선정 성공 케이스만 저장하면 안 된다.

## 예상 저장소

- `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`

이 저장소는 append-only final decision record를 위한 별도 장부다.
Paper Portfolio Tracking Ledger, Portfolio Proposal Registry, Current Candidate Registry를 덮어쓰지 않는다.

## 예상 row 핵심 필드

- `decision_id`
- `schema_version`
- `created_at`
- `updated_at`
- `decision_status`
- `decision_route`
- `source_observation_id`
- `source_paper_ledger_id`
- `source_type`
- `source_id`
- `source_title`
- `selected_components`
- `decision_evidence_snapshot`
- `risk_and_validation_snapshot`
- `paper_tracking_snapshot`
- `operator_reason`
- `operator_constraints`
- `phase35_handoff`
- `live_approval`
- `order_instruction`

## decision route 초안

- `SELECT_FOR_PRACTICAL_PORTFOLIO`
  - 최종 실전 후보 포트폴리오로 선정한다.
  - 단, live approval이나 주문 지시는 아니다.
- `HOLD_FOR_MORE_PAPER_TRACKING`
  - paper tracking 기간이나 조건이 더 필요하다.
- `REJECT_FOR_PRACTICAL_USE`
  - 현 조건에서는 실전 후보로 쓰지 않는다.
- `RE_REVIEW_REQUIRED`
  - 특정 blocker, 데이터 gap, market regime, operator constraint 때문에 재검토한다.

## 이번 작업에서 하지 않는 것

- final decision UI를 만들지 않는다.
- final decision row를 실제 저장하지 않는다.
- live approval, broker order, 자동매매를 만들지 않는다.
- Phase35 post-selection operating guide를 완성하지 않는다.

## 완료 기준

- final decision row schema가 코드 구현 전에 문서에서 먼저 같은 의미로 읽힌다.
- `selected` decision과 live approval / order instruction의 경계가 분명하다.
- Phase 33 paper ledger row 또는 Final Review inline paper observation을 final decision input으로 읽는 기준이 정리된다.
