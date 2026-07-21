# Portfolio Monitoring Initial Setting Correction V1 Design

Status: Implemented and verified
Date: 2026-07-21

## 이걸 하는 이유?

`Operations > Portfolio Monitoring > 개별 추적 결과 > 보유내역`에는 `최초 수량 정정`이 있지만 최초 추적 시작일을 수정할 수 없다. 최초 등록에서 날짜를 잘못 입력하면 수량만 바로잡을 수 있고, 시작 종가·최초 투자금·성과곡선의 기준 날짜는 잘못된 값으로 계속 남는다.

사용자가 같은 종목의 추적 이력을 끊지 않고 최초 시작일과 수량을 함께 정정하되, 원본 입력과 정정 이력은 감사 근거로 보존해야 한다.

## 승인된 접근법

기존 append-only `monitoring_security_position_event` revision chain을 확장한다.

- 사용자 화면의 `최초 수량 정정`을 `최초 설정 정정`으로 바꾼다.
- 사용자는 새 요청 시작일, 새 최초 수량, 선택 메모를 입력한다.
- Python이 DB 가격 이력에서 요청일 이후 첫 사용 가능한 시장일과 종가를 다시 결정한다.
- 정정은 기존 item row를 덮어쓰지 않고 initial-correction root의 새 revision으로 저장한다.
- 원본 item과 과거 correction revision은 그대로 보존한다.
- 저장 후 개별 lane, 그룹 가치곡선, 현금흐름 조정 성과를 새 초기 계약으로 전부 다시 투영한다.

기존 command/effect identifier인 `correct_initial_quantity`와 `initial_quantity_correction`은 저장 호환성을 위해 유지한다. 내부 의미만 “최초 수량만 정정”에서 “최초 입력 계약 정정”으로 확장하며 사용자-facing 명칭은 `최초 설정 정정`을 사용한다.

## 고려한 다른 접근

### A. Append-only 초기 계약 정정 확장 — 채택

- 기존 revision chain과 command idempotency를 재사용한다.
- 최초 입력과 모든 정정 이력이 남는다.
- 기존 추가매수·일부매도와 전체 가치곡선을 같은 projection에서 재검증할 수 있다.
- optional schema/read-model 확장이 필요하지만 데이터 무결성이 가장 높다.

### B. `monitoring_portfolio_item` 시작 필드 직접 수정 — 미채택

- 구현은 단순하지만 최초 입력 provenance와 과거 계산 기준을 잃는다.
- 기존 position-event append-only 계약과 충돌한다.

### C. 기존 추적 종료 후 같은 종목 재등록 — 미채택

- 저장 모델 변경은 작지만 동일 종목의 거래·성과 이력이 끊기고 사용자가 수정 대신 재구성을 수행해야 한다.

## 사용자 흐름

1. 사용자가 `개별 추적 결과`에서 대상 종목을 선택한다.
2. `보유내역 > 최초 설정 정정`을 연다.
3. 편집기는 현재 요청 시작일과 현재 유효 최초 수량을 기본값으로 채운다.
4. 사용자가 새 추적 시작일 또는 수량을 수정한다.
5. 날짜가 바뀌면 Python이 저장된 DB 가격만 읽어 새 적용 시장일과 시작 종가를 반환한다.
6. 편집기는 변경 전/후 요청일, 적용일, 시작 종가, 최초 투자금을 비교해 보여준다.
7. 모든 검증을 통과하면 사용자가 저장한다.
8. 서버는 item과 event chain을 lock하고 동일 resolution과 이후 거래 유효성을 다시 확인한 뒤 revision을 append한다.
9. 화면은 같은 종목 선택을 유지한 채 새 시작일부터 다시 계산된 개별·그룹 결과를 보여준다.

## 날짜 의미

최초 등록과 같은 두 날짜 계약을 유지한다.

- `requested_start_date`: 사용자가 선택한 날짜
- `effective_start_date`: 요청일 이후 첫 사용 가능한 DB 시장일
- `entry_close`: 적용일의 저장 종가

주말·휴장일을 다음 시장일로 해석하되 임의 가격을 만들지 않는다. 요청일 이후 사용할 수 있는 DB 가격이 없거나 미래 범위이면 저장을 막는다. UI/provider 직접 fetch는 하지 않으며 가격 gap은 기존 Ingestion 경계에서 해결한다.

## 저장 계약

기존 `monitoring_security_position_event`에 initial correction 전용 optional 값을 additive하게 보존한다.

- `requested_start_date`: initial correction에서만 새 사용자 요청일
- `effective_start_date`: initial correction에서만 resolved 시장일
- 기존 `trade_date`: initial correction에서는 `effective_start_date`와 같게 저장
- 기존 `reference_close`: initial correction에서는 새 `entry_close` snapshot
- 기존 `quantity`: 새 최초 수량
- `execution_price`, `execution_price_source`, `fee_usd`: 기존 initial correction 의미를 유지하며 체결 이벤트로 취급하지 않는다

기존 initial-quantity correction row는 두 새 날짜 필드가 없으므로 원본 item의 `requested_start_date`, `effective_start_date`, `entry_close`를 fallback으로 사용한다. registry/saved JSONL과 기존 item row는 재작성하지 않는다.

## Projection 계약

position-event projection은 terminal initial correction revision에서 다음 유효 초기 계약을 만든다.

- effective requested start date
- effective market start date
- effective entry close
- effective initial shares
- effective initial capital = shares × entry close

valuation은 가격 이력을 읽기 전에 effective initial contract를 결정하고, 원본 item보다 이른 날짜로 정정된 경우에도 필요한 가격 범위를 로드한다. 개별 lane의 시작일·시작 종가·초기 자본과 그룹 staggered-cash timeline도 같은 projected contract를 사용한다.

split은 기존처럼 적용 시장일 거래보다 먼저 처리하고, buy/sell은 `trade_date`, `event_order`, `root_event_id` 순서를 유지한다. Modified Dietz `0.5` 현금흐름 가중치와 buy 입금/sell 출금 의미는 변경하지 않는다.

## 서버 검증

서버가 최종 권위를 가진다.

- 대상은 기존과 동일하게 active/data-review direct U.S. stock + fixed shares만 허용한다.
- 요청 날짜와 수량은 command fingerprint에 포함한다.
- 새 적용일은 latest stored market date를 넘을 수 없다.
- 적용일 종가는 양수여야 한다.
- 새 적용일 이전에 남게 되는 유효 buy/sell이 있으면 저장을 거부한다.
- 새 초기 수량으로 전체 거래를 다시 적용했을 때 일부매도가 보유수량 이상이면 저장을 거부한다.
- tracking end 상태는 기존 eligibility에 따라 먼저 reopen해야 한다.
- 같은 command ID의 동일 payload는 replay하고 다른 payload는 conflict다.
- concurrent revision 변경과 stale correction revision은 transaction 안에서 거부한다.

실패하면 기존 projection과 저장값을 유지하고, 충돌한 거래일 또는 가격 부족 사유를 사용자 언어로 표시한다.

## UI 계약

`PositionLedgerPanel`의 correction dialog를 다음처럼 바꾼다.

- 제목과 action: `최초 설정 정정`
- 입력: `새 추적 시작일`, `새 최초 수량`, `메모`
- 현재값 기본 채움
- 날짜 변경 시 close-resolution intent를 보내고 rerun 뒤 편집 상태를 복구
- 비교 preview: 요청일, 적용일, 시작 종가, 최초 투자금의 변경 전/후
- resolution이 준비되지 않았거나 validation error가 있으면 저장 버튼 비활성화
- 안내: “새 적용일부터 전체 거래 이력과 성과를 다시 계산합니다.”

추가매수·일부매도 editor의 거래일·체결가 수정 흐름은 변경하지 않는다.

## 코드 소유 경계

- schema: `finance/data/db/schema.py`
- schemas/command validation: `app/services/portfolio_monitoring/schemas.py`, `commands.py`
- revision persistence/projection: `persistence.py`, `position_events.py`
- effective initial contract/valuation: `valuation.py`, `read_model.py`
- DB-only date resolution and Streamlit bridge: `app/web/final_selected_portfolio_dashboard.py`
- React contract/editor/panel: `app/web/streamlit_components/portfolio_monitoring_workbench/src/`
- tests: `tests/test_portfolio_monitoring_*.py` and component Vitest

## 적용 경계

- direct stock + fixed shares의 최초 설정 정정만 포함한다.
- ETF, fixed notional, selected strategy, quant backtest는 변경하지 않는다.
- full sell, tax lot/FIFO, broker/account sync, provider fetch, registry rewrite는 포함하지 않는다.
- 기존 추가매수·일부매도 수정/취소, tracking end/reopen 계약은 유지한다.

## 검증 계약

### Python RED→GREEN

- initial correction input의 날짜 validation과 fingerprint
- additive schema와 legacy null-row parsing
- requested/effective/entry-close resolution 저장과 command replay/conflict
- 기존 correction root의 replace revision과 audit preservation
- earlier/later start correction, market holiday resolution, missing price
- 새 시작일 이전 trade와 새 수량으로 invalid해지는 sell 차단
- corrected entry close/initial capital/full-history valuation
- group staggered-cash timeline과 KPI 재계산
- event 없는 item과 legacy correction row 회귀
- Streamlit close-resolution/recovery/dispatch JSON contract

### React RED→GREEN

- current date/quantity prefill
- date change resolution request와 rerun recovery
- old/new preview와 save gating
- correction command payload에 requested date 포함
- 기존 trade editor 회귀

### Closeout

- Portfolio Monitoring Python full regression
- React test/typecheck/build/static distribution
- actual desktop/420px에서 date correction interaction, preview, save, same-item recovery, overflow/console QA
- durable data/architecture/flow docs와 task/root handoff sync
- generated QA screenshot은 commit하지 않는다

## 완료 기준

- 사용자가 최초 시작일과 수량을 한 dialog에서 정정할 수 있다.
- 새 요청일·적용 시장일·종가·최초 투자금이 저장과 UI에서 일치한다.
- 개별/그룹 성과가 새 초기 계약으로 재계산된다.
- 기존 거래를 시간상 무효화하는 날짜 변경은 구체적 사유와 함께 차단된다.
- 기존 item/event/registry/saved 데이터와 범위 밖 자산 유형이 보존된다.
