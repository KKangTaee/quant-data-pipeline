# Final Portfolio Selection Decisions Guide

## 이 문서는 무엇인가

이 문서는 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`을
어떤 용도로 쓰고, Current Candidate / Pre-Live / Portfolio Proposal / Paper Observation과
어떻게 구분하는지 설명한다.

## 쉽게 말하면

Final Portfolio Selection Decision은
"검증 근거와 paper observation 기준까지 본 이 후보나 proposal을 최종 실전 후보로 선정할지, 더 볼지, 거절할지, 재검토할지"를 남기는 장부다.

이 장부는 마지막 판단 기록에 가깝지만, 그래도 live approval이나 broker 주문은 아니다.
실제 투자 운영 기준은 Phase 35에서 별도 guide로 정리한다.

## 파일 위치

| 구분 | 위치 | 역할 |
|---|---|---|
| Final decision registry | `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` | 최종 선정 / 보류 / 거절 / 재검토 판단과 Phase35 handoff 저장 |
| Runtime helper | `app/web/runtime/final_selection_decisions.py` | final decision JSONL append / load helper |
| UI | `Backtest > Final Review` | 단일 후보 또는 저장된 proposal을 읽어 validation / robustness / paper observation / 최종 판단 기록 |

첫 row를 저장할 때 파일이 생성된다.
파일이 없거나 row가 없으면 저장된 final decision review 영역은 비어 있는 상태로 읽는다.

## 저장 row 핵심 필드

| 필드 | 뜻 |
|---|---|
| `decision_id` | final decision record의 stable id |
| `schema_version` | final decision row schema version |
| `decision_route` | `SELECT_FOR_PRACTICAL_PORTFOLIO`, `HOLD_FOR_MORE_PAPER_TRACKING`, `REJECT_FOR_PRACTICAL_USE`, `RE_REVIEW_REQUIRED` 중 하나 |
| `source_observation_id` | Final Review에서 만든 inline paper observation 기준 id |
| `source_paper_ledger_id` | legacy paper ledger source id. 현재 main flow에서는 비어 있을 수 있음 |
| `source_type` / `source_id` | 단일 후보인지 portfolio proposal인지와 source id |
| `selected_components` | 최종 판단에 들어간 active component와 target weight |
| `decision_evidence_snapshot` | Phase34 evidence route, score, blocker, review item, 주요 metric |
| `risk_and_validation_snapshot` | Phase31 / Phase32 validation과 robustness snapshot |
| `paper_tracking_snapshot` | inline paper observation 기준, benchmark, cadence, baseline, trigger |
| `operator_decision` | 사람이 남긴 판단 사유, 제약 조건, 다음 행동 |
| `phase35_handoff` | Phase 35 운영 가이드로 넘길 준비 상태 |
| `live_approval` / `order_instruction` | 항상 `false`로 두는 실행 경계 |

## 기본 사용 방법

1. `Backtest > Final Review`를 연다.
2. 검토할 current candidate 또는 saved portfolio proposal을 선택한다.
3. Validation, Robustness / Stress 질문, Paper Observation 기준을 확인한다.
4. `최종 판단`을 선정 / 보류 / 거절 / 재검토 중 하나로 고른다.
5. `판단 사유`, `운영 제약`, `다음 행동`을 남긴다.
6. 기록 조건이 통과하면 `최종 검토 결과 기록`을 누른다.
7. 저장 후 `기록된 최종 검토 결과 확인`에서 Phase35 handoff를 다시 읽는다.

## route 의미

| Route | 의미 |
|---|---|
| `SELECT_FOR_PRACTICAL_PORTFOLIO` | 최종 실전 후보로 선정하고 Phase35 최종 투자 지침 확인 대상으로 넘긴다. 승인 / 주문은 아니다. |
| `HOLD_FOR_MORE_PAPER_TRACKING` | 추가 paper observation 기간이나 trigger 확인이 필요해 보류한다. |
| `REJECT_FOR_PRACTICAL_USE` | 현재 근거로는 실전 후보에서 제외한다. |
| `RE_REVIEW_REQUIRED` | 구성, 비중, validation, robustness, paper tracking 조건을 다시 봐야 한다. |

## 중요한 경계

- Final Review preview를 여는 것만으로는 final decision이 저장되지 않는다.
- `최종 검토 결과 기록`을 눌러야 append-only row가 저장된다.
- `SELECT_FOR_PRACTICAL_PORTFOLIO`도 live approval이나 주문 지시가 아니다.
- final decision 저장은 current candidate, Pre-Live, Portfolio Proposal registry를 덮어쓰지 않는다.
- Paper Ledger registry는 호환성 / 운영 artifact로 유지하지만, 현재 main flow에서 별도 저장을 필수로 요구하지 않는다.
- Phase 35 handoff는 최종 투자 지침 확인 준비 상태이지 자동매매 연결이 아니다.

## 현재 한계

- Phase 35 Post-Selection Guide는 구현되어 있으며, Final Review record를 읽는 no-extra-save preview surface다.
- 실제 broker order, 자동매매, live approval은 범위 밖이다.
- paper PnL 시계열 자동 계산은 아직 없으므로, 현재 decision evidence는 validation snapshot / inline paper observation 기준 / operator note 기반으로 해석한다.
