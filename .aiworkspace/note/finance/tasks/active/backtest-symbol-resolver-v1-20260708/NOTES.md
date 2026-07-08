# Backtest Symbol Resolver V1 Notes

## Decisions

- `4b698eb6`의 Market Movers 구현은 직접 병합하지 않는다.
- alias 저장은 새 `market_symbol_alias`가 아니라 `nyse_symbol_lifecycle` 중심으로 재설계한다.
- BK -> BNY는 일반화 테스트 fixture이며, production logic에 하드코딩하지 않는다.
- `resolution_status=candidate`는 UI가 보여주는 검토 후보, `resolution_status=active`는 사용자가 버튼으로 승인한 repair로 둔다.
- active repair는 Backtest source ticker를 rewrite하지 않고 OHLCV collection ticker만 resolved ticker로 바꾼다.
- 2차부터 candidate confidence는 단일 숫자만 보지 않고 same CIK, lifecycle coverage, resolved ticker price freshness, official/source reference를 `evidence_factors`로 함께 설명한다.
- `recommended_action=apply_ticker_change_repair`는 HIGH/MEDIUM confidence candidate에만 부여하고, LOW는 `review_symbol_identity`로 남긴다.
- DB 저장 시 `evidence_json`은 summary/status뿐 아니라 source quality, review note, evidence factor list를 보존한다.
- 3차 split contract는 runtime stitching이 아니라 metadata contract다. `source_range`는 source ticker가 유효했던 구간, `resolved_range`는 effective date 이후 resolved ticker 구간을 표현한다.
- `split_status=ready`는 source/resolved/effective_date가 모두 있는 경우에만 붙인다. effective date가 없으면 future PIT stitching이 안전하게 진행할 수 없으므로 ready로 간주하지 않는다.

## Open Notes

- SEC / Nasdaq / official corporate-action source feed 자체를 새로 수집하는 작업은 이번 2차 scope가 아니다. 현재는 existing lifecycle row의 `source`, `source_ref`, `evidence_json`을 structured evidence로 해석한다.
- 후속 PIT integration 전까지는 effective_date 이후 old/new ticker split을 자동으로 백테스트 가격 series에 합성하지 않는다.
