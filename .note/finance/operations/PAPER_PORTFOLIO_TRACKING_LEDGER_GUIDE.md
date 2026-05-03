# Paper Portfolio Tracking Ledger Guide

## 이 문서는 무엇인가

이 문서는 `.note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`을
어떤 용도로 쓰고, Current Candidate / Pre-Live / Portfolio Proposal registry와
어떻게 구분하는지 설명한다.

## 쉽게 말하면

Paper Portfolio Tracking Ledger는
"실제 돈을 넣기 전에 이 후보나 proposal을 어떤 조건으로 관찰할 것인가"를 남기는 장부다.

백테스트 결과나 proposal snapshot을 다시 보는 것만으로는 부족하다.
실전 후보로 가기 전에는 시작일, 비중, benchmark, review cadence, 재검토 trigger가 남아 있어야 한다.

## 파일 위치

| 구분 | 위치 | 역할 |
|---|---|---|
| Paper ledger | `.note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` | paper tracking 시작 조건과 Phase34 handoff 저장 |
| Runtime helper | `app/web/runtime/paper_portfolio_ledger.py` | paper ledger JSONL append / load helper |
| UI | `Backtest > Portfolio Proposal` | Validation Pack 아래 draft / save, 저장 ledger review |

첫 row를 저장할 때 파일이 생성된다.
파일이 없거나 row가 없으면 저장된 ledger review 영역은 비어 있는 상태로 읽는다.

## 저장 row 핵심 필드

| 필드 | 뜻 |
|---|---|
| `ledger_id` | paper tracking record의 stable id |
| `schema_version` | ledger row schema version |
| `paper_status` | `active_tracking`, `watch`, `paused`, `re_review`, `closed` 중 하나 |
| `source_type` / `source_id` | 단일 후보인지 portfolio proposal인지와 그 source id |
| `tracking_start_date` | paper tracking을 시작하는 기준일 |
| `tracking_benchmark` | paper 성과를 비교할 benchmark |
| `review_cadence` | 매주 / 매월 / 분기 / 리밸런싱 주기 / 이벤트 기반 검토 규칙 |
| `target_components` | 추적할 후보, role, target weight, baseline metric |
| `phase32_handoff_snapshot` | Validation / Robustness / Stress / Phase33 handoff snapshot |
| `baseline_snapshot` | 시작 시점 component 수, 비중 합계, weighted CAGR / MDD |
| `tracking_rules` | 시작일, benchmark, cadence, live approval 아님을 포함한 추적 규칙 |
| `review_triggers` | 재검토나 중단을 걸 조건 |
| `phase34_handoff` | Final Selection Decision Pack으로 넘길 준비 상태 |
| `operator_note` | 사람이 남긴 관찰 메모 |

## 기본 사용 방법

1. `Backtest > Portfolio Proposal`에서 단일 후보 direct path 또는 저장된 proposal Validation Pack을 연다.
2. `Robustness / Stress Validation Preview`와 `Phase 33 Handoff`를 확인한다.
3. `Paper Tracking Ledger Draft`에서 시작일, benchmark, review cadence, trigger, operator note를 확인한다.
4. 저장 조건이 통과하면 `Save Paper Tracking Ledger`를 누른다.
5. 저장 후 `저장된 Paper Tracking Ledger 확인`에서 row와 Phase34 handoff를 다시 읽는다.

## 중요한 경계

- Validation Pack을 여는 것만으로는 ledger가 저장되지 않는다.
- `Save Paper Tracking Ledger`를 눌러야 append-only row가 저장된다.
- 작성 중 proposal은 아직 durable source가 아니므로 proposal draft를 먼저 저장해야 paper ledger 저장이 열린다.
- 이 ledger는 live approval이 아니다.
- 이 ledger는 주문 지시가 아니다.
- Phase34 handoff가 `READY_FOR_FINAL_SELECTION_REVIEW`여도 최종 선정 자체는 Phase34에서 별도로 판단한다.

## 현재 한계

- paper PnL 시계열 자동 계산은 아직 없다.
- ledger는 시작 조건과 review rule을 저장하고, 현재 성과 변화는 기존 Pre-Live snapshot / Paper Tracking Feedback과 함께 해석한다.
- broker order, 자동매매, live approval은 범위 밖이다.
