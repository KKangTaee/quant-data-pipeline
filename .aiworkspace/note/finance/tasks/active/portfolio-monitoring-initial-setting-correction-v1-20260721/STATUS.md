# Portfolio Monitoring Initial Setting Correction V1 Status

Status: Complete — roadmap 4/4

- `개별 추적 결과 > 보유내역` action을 `최초 설정 정정`으로 바꾸고 새 추적 시작일과 새 최초 수량을 한 dialog에서 입력하도록 구현했다.
- 요청일 이후 첫 DB 시장일·종가와 최초 투자금을 변경 전/후로 확인하며, Python command가 같은 resolution과 이후 거래 유효성을 transaction 안에서 다시 검증한다.
- correction revision의 requested/effective date, entry close, initial shares/capital을 유효 초기 계약으로 투영해 개별 lane과 그룹 timeline을 함께 다시 계산한다.
- 기존 `correct_initial_quantity` / `initial_quantity_correction`, legacy null-date fallback, 추가매수·일부매도, split-first, event order, Modified Dietz `0.5` 계약을 유지했다.
- 운영 schema의 nullable date column 2개를 idempotent하게 추가했고 기존 group/item/command/event row `1/5/8/0`과 registry/saved checksum을 보존했다.
- Python 156개, React 32개, typecheck/build와 actual route·420px overflow·console QA를 완료했다. Browser 저장 interaction은 QA iframe selection round-trip 제약으로 자동화 command/component 회귀가 소유한다.
- ETF, fixed notional, selected strategy, quant backtest, full sell, tax lot, broker/account sync는 범위 밖이다.
