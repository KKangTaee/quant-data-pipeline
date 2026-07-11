# Notes

- UI boundary: React component와 Streamlit shell은 저장된 service payload만 읽는다. 외부 사이트 / SEC / price provider fetch는 UI에서 하지 않는다.
- Engine boundary: 13F는 `Ingestion -> DB -> loader -> service read model -> UI` 흐름을 유지한다.
- Price boundary: 보고 기준일 이후 성과는 local `finance_price.nyse_price_history` daily rows를 service에서 읽어 계산한다. 실제 현재 보유나 투자 성과가 아니라 "보고 기준일 구성 그대로 보유" 가정이다.
- Change board: 이전 filing이 없으면 증가 / 감소 / 매도 후보가 0이어도 오류가 아니다. UI는 `비교 기준 분기 없음`을 명확히 보여야 한다.
- CUSIP-symbol map은 local DB에 오염 가능성이 있어 display / performance 계산은 holding row의 `holding_symbol`을 우선한다.
