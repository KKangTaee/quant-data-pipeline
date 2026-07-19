# Notes

- 그룹 가치곡선은 `total_value` 성과선이며 OHLCV로 합성하지 않는다.
- 실제 candle은 direct 미국 주식·ETF의 DB 일봉에만 제공한다.
- strategy 상세는 item value curve만 제공한다.
- 그룹 가치곡선과 `selected_item_market_chart`는 독립 projection이다. 한쪽의 데이터 부족이 다른 쪽의 성과·기여 정보를 숨기지 않는다.
- 가격 경로는 `finance.loaders.price.load_price_history -> page callback -> market_chart service -> read model -> React`이며 화면 render 중 provider fetch를 하지 않는다.
- 선택 id가 없거나 현재 그룹에서 찾을 수 없으면 첫 active item을 사용하고, 종료 항목뿐이면 첫 item으로 안정적으로 fallback한다.
- Operations Console summary는 `include_selected_item_market_chart=False`를 명시해 상세 가격 DB read를 추가하지 않는다.
- 직접 종목 line은 candle과 같은 row의 close를 사용한다. 별도 가격 series를 조합하지 않는다.
