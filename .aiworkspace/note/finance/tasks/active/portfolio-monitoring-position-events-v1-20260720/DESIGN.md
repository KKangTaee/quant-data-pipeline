# Portfolio Monitoring Position Events V1 Design

Status: Approved
Date: 2026-07-20

## 이걸 하는 이유?

현재 `Operations > Portfolio Monitoring`은 직접 개별주식 등록 시 최초 정수 수량을 받을 수 있지만 이후에는 `추적 종료`와 `추적 종료 취소`만 지원한다. 잘못 입력한 최초 수량을 정정하거나 실제 추가매수·일부매도를 반영할 저장 명령, 거래 원장, 성과 계산과 사용자 행동이 없다. 사용자가 실제로 보유한 수량과 현금흐름을 기준으로 같은 종목을 계속 추적할 수 있어야 한다.

## 승인된 접근법

기존 `monitoring_portfolio_item` 시작 계약을 삭제하거나 과거 거래를 덮어쓰지 않고, 개별종목 포지션 이벤트를 append-only revision chain으로 저장한다.

- 기존 item row는 최초 입력 provenance를 유지한다.
- 최초 수량 정정은 시작일과 entry close를 유지한 채 유효 최초 수량을 교체하는 이벤트다.
- 추가매수와 일부매도는 거래일 이후 보유수량과 외부 현금흐름을 바꾸는 이벤트다.
- 거래 수정은 같은 root event를 supersede하는 새 revision을 append한다.
- 거래 취소는 같은 root event를 void하는 새 revision을 append한다.
- projection은 root별 terminal revision만 적용하고 과거 revision은 audit evidence로 보존한다.
- 이벤트가 없는 기존 항목은 현재 item 계약과 기존 가치곡선을 그대로 사용한다.

## 적용 경계

다음 조건을 모두 만족하는 항목만 포지션 이벤트를 허용한다.

- `source_type == direct_security`
- `instrument_kind == stock`
- `funding_mode == fixed_shares`
- 상태가 `active` 또는 `data_review`

ETF, fixed-notional 종목, Final Review selected strategy와 퀀트 백테스트에는 관련 action을 노출하거나 명령을 허용하지 않는다. 전량매도는 기존 tracking-end 경계에 남기며 이번 거래 원장은 일부매도 후 최소 1주를 요구한다.

## 저장 계약

새 canonical table `monitoring_security_position_event`를 둔다. 구체적인 SQL type과 index 길이는 구현 계획에서 기존 schema 관례에 맞추되 다음 의미를 고정한다.

| Field | Meaning |
|---|---|
| `position_event_id` | immutable revision identity |
| `root_event_id` | 최초 create와 후속 replace/void를 묶는 business event identity |
| `supersedes_event_id` | 바로 이전 revision identity |
| `monitoring_item_id` | direct-stock fixed-shares item identity |
| `event_order` | root create 때 부여하고 revision에서 유지하는 item-local deterministic order |
| `event_action` | `create`, `replace`, `void` |
| `position_effect` | `initial_quantity_correction`, `buy`, `sell` |
| `trade_date` | 실제 거래일. 최초 수량 정정은 item effective start date |
| `quantity` | 정수 수량. void revision은 superseded event payload를 참조 |
| `execution_price` | buy/sell 실제 체결 단가. 최초 수량 정정에는 없음 |
| `reference_close` | 입력 당시 exact-date DB close snapshot |
| `execution_price_source` | `db_close_default` 또는 `manual_override` |
| `fee_usd` | 선택적 수수료, 기본 0 |
| `note` | 사용자 메모 |
| `command_id` | 기존 멱등 command와 연결되는 identity |
| `created_at` | revision audit timestamp |

물리 삭제와 기존 revision payload update는 하지 않는다. 동일 item에는 유효한 `initial_quantity_correction` root가 최대 하나이며 이후 정정은 그 root의 replace revision으로 이어진다. buy/sell 수정도 원래 root와 `event_order`를 유지하므로 과거 거래 수정이 같은 날 다른 거래의 순서를 바꾸지 않는다. 새 root의 `event_order`는 item lock 안에서 단조 증가하도록 부여한다.

## 명령 계약

기존 `monitoring_portfolio_command` 멱등 경계를 재사용하고 다음 semantic command를 추가한다.

- `correct_initial_quantity`
- `record_position_trade`
- `replace_position_trade`
- `void_position_trade`

모든 command는 대상 item을 transaction 안에서 lock하고 현재 effective event projection과 모든 후속 event를 재검증한 뒤 append한다. 같은 `command_id`와 같은 fingerprint는 이전 성공 결과를 replay하고, 같은 ID의 다른 payload는 conflict다.

과거 수량 또는 거래를 바꾸었을 때 이후 sell이 보유수량을 초과하게 되면 전체 command를 거부한다. 화면의 사전 preview는 편의 기능이며 서버 검증이 최종 권위다.

## 거래일과 가격 경계

- 거래일은 item effective start date 이상이고 현재 latest stored market date 이하이어야 한다.
- buy/sell 거래일은 DB에 exact daily price row가 있는 시장일이어야 하며 다음 거래일로 자동 이동하지 않는다.
- UI는 거래일을 선택하면 exact-date DB close를 execution price 기본값으로 자동 입력한다.
- 사용자는 자동 입력된 execution price를 실제 체결가로 수정할 수 있으며, 수정 시 `manual_override`로 구분한다.
- 거래일을 바꾸면 새 날짜의 DB close로 execution price를 다시 채우고 `db_close_default` 상태로 되돌린다.
- 서버는 command 시점의 exact-date DB close를 다시 확인하고 `reference_close`와 최종 `execution_price`를 함께 저장한다. 두 값의 Decimal equality로 `db_close_default` 또는 `manual_override`를 판정하며 client flag를 신뢰하지 않는다.
- execution price는 양수여야 한다.
- quantity는 정수 1주 이상이어야 한다.
- fee는 0 이상이며 비어 있으면 0이다.
- sell fee는 gross proceeds보다 작아야 하며 순출금액이 양수여야 한다.
- sell은 해당 revision order 직전 보유수량보다 작아야 한다. 같거나 크면 전량매도로 보고 차단한다.
- tracking end 이후 거래는 허용하지 않는다. ended item은 먼저 기존 `추적 종료 취소`로 활성화해야 한다.

## 포지션과 현금흐름 계산

projection은 다음 순서로 직접종목 lane을 만든다.

1. 최신 유효 최초 수량 정정이 있으면 그 수량을, 없으면 item `input_shares`를 사용한다.
2. 최초 투자금은 `effective initial shares × existing entry_close`다.
3. split은 기존과 같이 해당 시장일 거래 이벤트보다 먼저 effective units에 반영한다.
4. 유효 buy/sell을 `trade_date`, `event_order`, `root_event_id` 순으로 적용한다.
5. buy는 `quantity × execution_price + fee`의 양수 외부 입금이다.
6. sell은 `quantity × execution_price - fee`의 양수 외부 출금이며 포지션 외부로 빠진다.
7. dividend cash는 보유수량과 지급일 기준으로 기존 lane 내부 현금에 누적한다.
8. current value는 남은 shares의 DB close 평가액과 lane 내부 dividend cash의 합이다.
9. dollar P&L은 `current value + cumulative withdrawals - cumulative contributions`다. contributions에는 최초 투자금과 buy 입금이 포함된다.

수익률은 외부 입출금을 투자 성과로 오인하지 않는 daily Modified Dietz unit-value index로 계산한다. 거래 시간이 입력되지 않으므로 같은 날 flow는 일중 중간 시점 가중치 `0.5`를 일관되게 사용한다.

- 일별 순외부흐름 `F = buy contribution - sell withdrawal`로 둔다.
- 일별 수익률은 `(end value - begin value - F) / (begin value + 0.5 × F)`다.
- buy/sell execution price와 fee는 위 contribution/withdrawal에 직접 반영된다.
- 최초 시작일은 정정된 initial capital을 기준 unit value `1.0`으로 둔다.
- 분모가 0 이하이거나 필요한 begin/end value가 없으면 임의 수익률을 만들지 않고 `data_review`로 표시한다.
- 일별 수익률을 연결한 unit-value index에서 total return, CAGR과 MDD를 산출한다.
- 그룹은 공통 관측일의 item begin/end value와 순외부흐름을 각각 합산해 같은 식을 적용하고 기존 latest-common-basis-date 원칙을 유지한다.

## 사용자 흐름

선택한 eligible 개별종목 상세에 `보유내역` 영역을 둔다. 화면의 주인공은 현재 보유 상태와 다음 action이며 raw command/job 진단 패널을 만들지 않는다.

### 요약

- 현재 보유수량
- 최초 수량과 시작일
- 누적 추가매수 금액
- 누적 매도·출금 금액
- 현재 평가금액
- 현금흐름 조정 손익과 수익률

### 최초 수량 정정

`최초 수량 정정` action은 기존 시작일과 시작 종가를 고정하고 새 정수 수량을 받는다. 저장 전 변경 전·후 수량과 최초 투자금 차이를 preview한다. 저장 후 최초 시점부터 전체 lane, group curve와 지표를 다시 projection한다.

### 매수·매도 기록

`매수·매도 기록` action은 유형, 거래일, 정수 수량, execution price, optional fee, note를 받는다. 거래일을 선택하면 exact-date DB close를 execution price에 자동 입력하며 사용자가 실제 체결가로 수정할 수 있다. 자동 종가와 수동 수정 여부를 입력란 아래에 표시하고 sell은 거래 전·후 수량을 preview한다.

### 거래 내역

선택 상세 아래 chronological ledger에서 최초 등록, 최초 수량 정정, buy, sell, replace와 void 상태, 거래 후 보유수량을 보여준다. 유효 거래에는 `수정`과 `취소`를 제공한다. 저장 성공 후 같은 선택 문맥을 유지하면서 transaction date 이후 가치곡선과 group KPI를 다시 표시한다.

## 오류 처리

사용자 입력 오류는 command 실패로 표시하되 기존 projection을 유지한다. 다음 상태는 저장을 차단하고 구체적인 해결 문구를 반환한다.

- 지원하지 않는 item type 또는 status
- exact-date DB market row 부재
- 시작일 이전, 미래 또는 tracking end 이후 거래
- 비정수·0 이하 quantity
- 0 이하 execution price 또는 음수 fee
- 보유수량 이상 sell
- replace/void로 인해 후속 sell이 invalid해지는 경우
- stale event revision 또는 concurrent command conflict

provider fetch는 화면 render나 command에서 수행하지 않는다. 가격 gap은 Ingestion의 기존 수집 경계에서 해결한다.

## 기존 데이터와 migration

- 새 table 생성은 additive migration이다.
- 기존 item row backfill은 하지 않는다.
- event가 없는 item의 value lane/read model JSON은 기존 결과와 같아야 한다.
- legacy saved JSONL, Final Review registry와 existing command rows를 재작성하지 않는다.
- 기존 tracking end/reopen identity와 active 10-item/source-duplicate 제한을 유지한다.

## 코드 소유 경계

- DB schema: `finance/data/db/schema.py`
- event schema/validation/command/repository: `app/services/portfolio_monitoring/`
- direct-security transaction-aware valuation: `app/services/portfolio_monitoring/valuation.py`
- workspace/read model: `app/services/portfolio_monitoring/read_model.py`
- Streamlit command/read bridge: `app/web/final_selected_portfolio_dashboard.py`
- React action, preview, ledger: `app/web/streamlit_components/portfolio_monitoring_workbench/`
- durable contract/docs: `.aiworkspace/note/finance/docs/data/PORTFOLIO_MONITORING_DATA_CONTRACT.md`, architecture/flow/project map/roadmap and task/root handoff docs

## 검증 계약

- schema/index/row parser와 append-only revision projection
- command idempotency, stale revision conflict, unsupported item gate
- 최초 수량 정정 전후 initial capital과 full-history replay
- 여러 buy/sell, 같은 날 복수 거래, replace/void와 후속 sell 재검증
- split/dividend와 거래가 함께 있는 unit/value/cashflow curve
- event 없는 기존 direct stock, ETF, strategy와 group KPI 회귀
- Python page dispatch/read model/JSON serialization
- React eligibility, DB close default fill, manual override, trade-date change refill, 입력 validation, before/after preview, ledger edit/void interaction
- TypeScript typecheck, production build, canonical static distribution
- actual desktop/mobile Browser interaction, layout, overflow QA와 generated screenshot 1장
- `git diff --check`, focused/full Portfolio Monitoring regression, durable docs/root handoff alignment

## 완료 기준

- 사용자가 개별종목 상세에서 최초 수량 오류를 정정하고 즉시 전체 이력 재계산을 확인할 수 있다.
- 사용자가 실제 체결가 기준 추가매수·일부매도를 기록하고 현재 보유수량과 현금흐름 조정 성과를 확인할 수 있다.
- 잘못 기록한 거래를 audit를 보존하며 수정·취소할 수 있다.
- 지원하지 않는 전략/ETF/투자금 항목은 기존 동작을 유지한다.
- 모든 필수 자동 검증과 actual Browser QA가 통과하고 문서가 구현 계약과 일치한다.
