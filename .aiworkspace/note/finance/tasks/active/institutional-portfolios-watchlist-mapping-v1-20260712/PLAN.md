# Institutional Portfolios Watchlist / Mapping V1 Plan

## 이걸 하는 이유?

Institutional Portfolios는 SEC 13F DB를 실제로 읽고 있지만, 유명 투자자 alias와 CIK 매핑이 부족해 사용자가 드러켄밀러 같은 이름으로 찾기 어렵다. 또한 13F CUSIP-symbol mapping이 불완전하거나 중복되면 가격 차트가 잘못 연결될 수 있다.

## 범위

1. 대가 watchlist / alias seed를 확장하고 `institutional_13f_manager_watchlist`를 읽을 수 있는 loader 경계를 연다.
2. manager search가 SEC filer명뿐 아니라 watchlist alias로도 매칭되게 한다.
3. ambiguous CUSIP-symbol mapping은 차트/성과용 symbol로 쓰지 않고 unresolved로 표시한다.
4. 선택 종목의 가격 데이터 상태를 `symbol missing`, `ambiguous mapping`, `price missing`, `ready`로 분리한다.

## 제외

- Dataroma / Fintel scraping
- WhaleWisdom 유료 API adapter
- OpenFIGI adapter 구현
- live trading / broker / auto rebalance 의미
