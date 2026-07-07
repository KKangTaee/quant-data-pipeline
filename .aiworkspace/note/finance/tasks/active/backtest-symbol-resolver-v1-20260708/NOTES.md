# Backtest Symbol Resolver V1 Notes

## Decisions

- `4b698eb6`의 Market Movers 구현은 직접 병합하지 않는다.
- alias 저장은 새 `market_symbol_alias`가 아니라 `nyse_symbol_lifecycle` 중심으로 재설계한다.
- BK -> BNY는 일반화 테스트 fixture이며, production logic에 하드코딩하지 않는다.
- `resolution_status=candidate`는 UI가 보여주는 검토 후보, `resolution_status=active`는 사용자가 버튼으로 승인한 repair로 둔다.
- active repair는 Backtest source ticker를 rewrite하지 않고 OHLCV collection ticker만 resolved ticker로 바꾼다.

## Open Notes

- 후속 차수에서 SEC / Nasdaq / official corporate-action source를 후보 점수화에 더 깊게 연결해야 한다.
- 후속 PIT integration 전까지는 effective_date 이후 old/new ticker split을 자동으로 백테스트 가격 series에 합성하지 않는다.
