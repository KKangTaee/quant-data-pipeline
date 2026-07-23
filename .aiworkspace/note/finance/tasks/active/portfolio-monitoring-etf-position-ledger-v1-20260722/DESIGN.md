# Portfolio Monitoring ETF 보유 수량 원장 설계

## 이걸 하는 이유?

Portfolio Monitoring은 direct security인 ETF를 `fixed_shares` 방식으로 등록할 수 있고,
실제 운영 DB의 QQQ와 SOXX도 각각 4주와 6주로 정상 저장되어 있다. 일반 가치곡선은 이
수량으로 시작 투자금과 현재가치를 올바르게 계산하지만, position event와 selected position
projection은 `instrument_kind == "stock"`만 허용한다. 그 결과 ETF 상세의 상단 가치는
정상인데 `보유내역`은 `-주`, `$0.00`, 빈 거래 이력으로 표시된다.

이 작업은 등록·평가·보유 원장 계약을 맞춰 `direct_security + fixed_shares` ETF가 실제
저장 수량과 거래 이력을 일관되게 사용하도록 한다.

## 확인된 현재 상태

- QQQ: `instrument_kind=etf`, `funding_mode=fixed_shares`, `input_shares=4`,
  `initial_capital=2970.95996094`, 현재 가치 약 `$2,839.13`.
- SOXX: `instrument_kind=etf`, `funding_mode=fixed_shares`, `input_shares=6`,
  `initial_capital=3598.20007324`, 현재 가치 약 `$3,316.14`.
- `validate_add_item_input`과 React item builder는 ETF `fixed_shares`를 허용한다.
- `build_direct_security_value_lane`은 주식·ETF 가격과 수량을 모두 평가하지만
  `lane.position`은 주식에만 생성한다.
- `_project_selected_position`은 ETF를 부적격으로 처리하고 React는 그 빈 projection을
  숫자 카드로 렌더링한다.

## 검토한 안

### A. ETF fixed-shares 원장을 주식과 동일하게 지원 — 채택

position eligibility를 `direct_security + stock/etf + fixed_shares`로 확장한다. 기존
append-only revision, DB 종가 기본값, 수동 체결가, split-first 수량, 배당 현금,
Modified Dietz 현금흐름 조정 계약을 그대로 재사용한다.

- 장점: 이미 저장된 ETF 수량을 보존하고 화면·수정·거래·성과가 하나의 계약을 사용한다.
- 비용: ETF split/dividend와 buy/sell 회귀를 명시적으로 추가해야 한다.
- 데이터 이전: 필요 없다. 기존 QQQ·SOXX는 다음 workspace 생성부터 자동으로 원장을 만든다.

### B. ETF 원장을 읽기 전용으로만 표시 — 보류

초기/현재 수량과 평가금액만 보여주고 수정·거래 action은 차단한다. 화면 오류는 줄지만
같은 `fixed_shares` 입력이 주식과 ETF에서 서로 다른 운영 의미를 가져 사용자 혼란이 남는다.

### C. ETF fixed-shares 등록을 차단하고 fixed-notional로 전환 — 제외

향후 등록을 막고 기존 ETF를 가상 투자금 방식으로 바꾼다. 이미 사용자가 입력한 정확한
4주·6주 계약을 훼손하고 기존 레코드 migration이 필요하므로 채택하지 않는다.

## 구현 계약

### 대상

- `source_type == "direct_security"`
- `instrument_kind in {"stock", "etf"}`
- `funding_mode == "fixed_shares"`

세 조건을 모두 만족할 때만 position ledger와 최초 설정 정정, 추가매수, 일부매도,
revision 수정·취소를 허용한다.

### 대상이 아닌 항목

- ETF `fixed_notional`
- stock `fixed_notional`
- selected strategy
- quant backtest 결과
- broker/account transaction과 실제 주문

이 항목들은 기존 경계를 유지한다.

## 데이터 흐름

```text
기존 ETF item(input_shares)
  -> DB OHLCV + position event revisions
  -> build_direct_security_value_lane
  -> stock/ETF 공통 PositionLedgerSummary
  -> selected position / item_details
  -> 보유수량·입출금·평가금액·현금흐름 조정 손익
  -> 최초 설정 정정 또는 추가매수·일부매도 command
```

ETF에 아직 position event가 없으면 `input_shares`가 최초 수량이 된다. 새 거래를 저장하면
기존 append-only `monitoring_security_position_event`가 같은 item id에 revision을 남긴다.

## 오류와 호환성

- ETF `fixed_notional`은 수량 원장 부적격 사유를 유지하고 수량/거래 숫자 카드를 정상
  보유내역처럼 표시하지 않는다.
- 기존 stock fixed-shares 계산과 command validation은 변경하지 않는다.
- 일부매도 후 최소 1주, 전량매도는 tracking end, exact-date DB close 기본값,
  manual override와 revision 감사 이력을 유지한다.
- ETF의 split과 dividend는 기존 daily price row의 `stock_splits`와 `dividends`를 사용한다.
  별도 ETF corporate-action table이나 provider fetch를 추가하지 않는다.
- DB schema와 기존 item/event row를 수정하지 않는다.

## 사용자 화면

- QQQ는 현재 보유수량 4주, 최초 4주, 현재 평가금액과 현금흐름 조정 손익을 표시한다.
- SOXX는 현재 보유수량 6주, 최초 6주를 같은 방식으로 표시한다.
- ETF fixed-shares에도 `최초 설정 정정`, `매수·매도 기록` action을 제공한다.
- 안내 문구의 `개별주식`은 실제 지원 범위에 맞춰 `개별 종목` 또는 `주식·ETF`로 바꾼다.

## 검증

- position events: ETF fixed-shares eligibility, 초기 수량, buy/sell, 최소 1주 규칙.
- valuation: ETF lane에 PositionLedgerSummary가 생기고 split/dividend를 반영한다.
- read model: ETF selected position이 eligible이며 현재/최초 수량과 평가금액을 전달한다.
- negative regression: ETF fixed-notional과 selected strategy는 계속 부적격이다.
- React/source contract: ETF 원장 숫자와 action을 렌더링하며 구 stock 화면을 보존한다.
- actual Browser QA: QQQ 4주와 SOXX 6주, 현재 가치, action 노출, clean console을 확인하고
  저장 command는 실행하지 않는다.

## 개발 차수

1. 실패 테스트로 ETF fixed-shares eligibility와 projection을 고정한다.
2. position event·valuation·read model의 공통 direct-security 수량 경계를 구현한다.
3. copy/React 회귀, Browser QA, durable docs와 커밋을 완료한다.
