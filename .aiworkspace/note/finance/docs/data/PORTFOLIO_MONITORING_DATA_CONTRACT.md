# Portfolio Monitoring Data Contract

Status: Active
Last Verified: 2026-07-20

## 저장소

`finance_meta`의 canonical tables는 다음과 같다.

| Table | Responsibility |
|---|---|
| `monitoring_portfolio_group` | 사용자 그룹, default identity, name, optimistic version, soft lifecycle |
| `monitoring_portfolio_item` | direct security/selected strategy, 시작·종료, funding, entry, initial capital |
| `monitoring_security_position_event` | direct stock fixed-shares의 최초 수량 정정과 추가매수·일부매도 append-only revision 원장 |
| `monitoring_portfolio_command` | idempotency fingerprint와 command result |
| `monitoring_diagnosis_snapshot` | point-in-time 진단·매크로 관찰과 이후 21/63 session outcome |
| `monitoring_risk_calibration_artifact` | walk-forward calibration 결과와 publication gate |

기존 `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`은 legacy input이다. dry-run/apply는 source checksum과 provenance를 남기며 원본 파일을 재작성하지 않는다.

## Item 계약

- active item은 group당 최대 10개다. ended item은 한도에서 제외한다.
- direct stock/ETF는 fixed notional 또는 integer shares `>= 1`을 허용한다.
- selected strategy는 fixed notional만 허용한다.
- requested start 이후 첫 usable close가 effective start다. 값이 없으면 등록을 막는다.
- direct security 원장은 raw close를 primary price로 사용한다. split은 effective units에 반영하고 cash dividend는 재투자하지 않은 누적 cash로 더한다.
- fixed notional은 fractional virtual units를 허용하지만 integer shares 방식은 소수 주식을 허용하지 않는다.
- `reopen_item`은 ended item의 동일 identity와 원래 start/funding/entry/initial-capital 계약을 유지하고 종료 요청일·적용일·종료금액만 `NULL`, status를 `active`로 되돌린다. 새 episode나 재진입 가격을 만들지 않으며, active 10개 한도와 동일 source 중복을 다시 검증한다. 과거 command row는 audit로 유지한다.
- 최초 수량 정정과 거래 원장은 `direct_security + stock + fixed_shares` item에만 적용한다. ETF, selected strategy, fixed notional은 기존 계약을 유지한다.
- `create -> replace/void` revision은 payload를 덮어쓰거나 삭제하지 않는다. 같은 root는 최초 `event_order`를 유지하고 terminal revision만 계산에 반영하며 전체 chain은 감사 이력으로 표시한다.
- 거래일은 정확히 일치하는 저장 일봉 종가만 기본 체결가로 사용한다. 이후 거래일로 이동하지 않으며, 사용자가 값을 바꾸면 입력 당시 `reference_close`와 `manual_override` provenance를 함께 저장한다.
- 같은 날 계산 순서는 split 적용 후 `trade_date, event_order` 거래 적용이다. 일부매도 후 최소 1주를 유지하고 전량매도는 기존 tracking-end flow를 사용한다.

## 가치와 KPI

각 item lane은 `date, effective_units, market_value, dividend_cash, total_value, raw_return_index, adjusted_return_index, data_status`와 누적 입금·출금 정보를 낸다. 시작 전 자금과 tracking end 뒤 확정 가치는 수익률 0% cash lane으로 group curve에 포함한다.

추가매수는 외부 입금(`quantity * execution_price + fee`), 일부매도는 외부 출금(`quantity * execution_price - fee`)이다. 매도대금은 group 내부 cash로 남기지 않는다. 거래 시각을 받지 않는 V1의 일별 Modified Dietz는 같은 날 모든 외부 현금흐름에 고정 `0.5` 가중치를 적용한다. 이 값은 실제 장중 수익률이 아니라 일별 근사다.

그룹 KPI는 active item이 모두 평가 가능한 latest common basis date만 사용한다. 서로 다른 날짜의 최신 값을 합치지 않는다. 그룹 가치곡선은 item별 cashflow-neutral unit index를 누적 입금 기준으로 합성하고, 손익은 `현재 가치 + 누적 출금 - 누적 입금`으로 계산한다. 관측기간이 짧으면 CAGR을 과도하게 연율화하지 않고 short-window 상태를 표시한다.

## Point-in-time과 진단

profile, ETF holdings/exposure, price, economic-cycle, futures macro snapshot은 화면 시점에 DB에서 읽은 source date와 coverage를 보존한다. 미래 공시나 사후 수정값을 과거 snapshot에 섞지 않는 point-in-time 원칙을 따른다.

진단 snapshot identity는 group, as-of date, config fingerprint, policy version으로 고정한다. 확률 publication은 표본 수·positive count·Brier score·baseline 비교·reliability error를 통과한 artifact만 `READY`다. 미충족·fingerprint mismatch는 `SUPPRESSED`, 부분 근거는 `LIMITED`이며 UI가 임의로 확률을 계산하지 않는다.

Calibration artifact unique identity와 latest-reader scope에는 모두 `config_fingerprint`와 `policy_version`이 포함된다. 다른 설정의 최신 artifact가 현재 workspace의 유효 artifact를 가리거나 대체할 수 없다.

## 금지 경계

DB row는 broker/account 동기화나 주문 체결 확인이 아니다. position event의 입금·출금은 가상 Portfolio Monitoring 성과 계산 의미이며 tax lot/FIFO, 실현·미실현 원가, group cash account, cross-item transfer는 제공하지 않는다. provider raw response/full holdings는 각 canonical DB가 소유하며 command/result JSON에 복제하지 않는다.
