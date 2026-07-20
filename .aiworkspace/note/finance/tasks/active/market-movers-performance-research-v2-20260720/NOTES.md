# Notes

- DB-only group snapshot 실측 합계는 약 22초였고 actual uncached Browser entry는 약 46초였다.
- monthly sector snapshot의 9개 query 중 market-date aggregation query 하나가 약 8.06초였다. sector/industry에서 같은 query가 중복된다.
- selected research는 TER/COHR 각각 약 0.85초였으므로 Top Rank 지연의 주원인은 Streamlit 전체 rerun과 six-snapshot eager load다.
- group/research cache TTL은 현재 120초다.
- financial trend limit은 annual 8, quarterly 32다. 실제 DB에서 TER는 annual 12/quarterly 54, COHR는 12/52, LITE는 11/32 rows가 있었다.
- decision payload에는 actions가 들어가지만 `MarketMoversDecisionWorkbench`가 렌더링하지 않는다.
- 기존 command/unified summary model에는 effective timestamp/freshness가 있으나 decision payload contract에는 전달되지 않는다.
- events tab은 statement status/as-of만 표시하고 news/filing metadata rows를 연결하지 않는다.
- 구현 후 initial decision payload는 현재 breadth key 하나만 계산하고 coverage/key별 session snapshot을 재사용한다.
- annual/quarterly trend 상한은 10/40 observations이며, factor chart는 currency/EPS 기본 bar와 ratio/percent 기본 line을 제공한다.
- events tab은 DB filing ledger 최대 5건을 즉시 표시하고, news/Korean-news/latest SEC metadata는 selected-symbol button action으로만 session에 저장한다.
- broader Market Movers roadmap의 sector conditional outlook은 이번 성능·조사 보완 범위가 아니며 OOS publication gate 전까지 수치 공개를 보류한다.
