# Institutional Holdings Flow

Status: Active
Last Verified: 2026-08-17

## Purpose

`Research > Institutional Holdings`는 Market Movers와 분리된 기관 / 투자 대가 portfolio research surface다.

Market Movers는 선택된 급등락 종목이 왜 관심받는지 보는 곳이고, Institutional Holdings는 특정 manager의 delayed SEC Form 13F holdings와 분기별 reported change를 탐색하는 곳이다.

## User Flow

```text
Research > Institutional Holdings
  -> page entry: local 13F due calendar + DB submission/portfolio rows only
  -> due/current/partial 판단; page entry에서 SEC network request 없음
  -> due일 때 데이터 기준 disclosure에 `업데이트 확인 및 갱신`
  -> explicit click
     -> official bulk window discovery
     -> published: full SEC ZIP reconciliation
     -> not published: curated watchlist EDGAR submissions/index/raw XML fallback
  -> MySQL finance_meta.institutional_13f_* accession ledger
  -> amendment-aware effective quarter loader
  -> React content-first page header / bounded manager picker / horizontal destination tabs
  -> selected manager context hero / filing basis
  -> portfolio context / 분기 리뷰 / full holdings / security / popularity
  -> 분기 리뷰: NEW / ADD / KEEP / REDUCE / DROP + 두 covered-sleeve proxy
  -> full holdings explorer: ticker / issuer / CUSIP search + mapping / sector filters + sort + 50-row page
  -> mapped holding click or explicit security search
  -> DB-backed price chart / selected-manager position / latest-filing holders
  -> source filing link review
```

정상 사용자 경로는 target report period만 server event에 전달한다. Dataset URL, local ZIP,
User-Agent 입력은 `Data > Data Operations`의 advanced recovery로 남고 Institutional
Holdings 정상 React 화면에는 노출하지 않는다.

## Screen Ownership

| Step | Owner |
|---|---|
| Hybrid source collection | `finance/data/institutional_13f.py`, `finance/data/institutional_13f_edgar.py`, `app/jobs/ingestion_jobs.py`; bulk-first/EDGAR fallback과 manager별 transaction을 소유한다 |
| DB read path | `finance/loaders/institutional_13f.py`; raw accession에서 effective quarter를 만들고 notice를 포함한 latest submission period와 저장 가격을 읽는다 |
| Refresh/review read model | `app/services/institutional_13f_refresh.py`, `app/services/institutional_quarter_review.py`; local due action, share-based change, 두 coverage-aware proxy를 만든다 |
| Portfolio visual read model / caveats | `app/services/institutional_portfolios.py`; v3 context summary, coverage, full holdings explorer, explicit security search, comparison state, manager picker, freshness, caveats를 만든다 |
| Streamlit adapter / event state / unavailable fallback | `app/web/institutional_portfolios.py`, `app/web/streamlit_app.py`; 정상 React 경로에서는 route, DB/service payload와 explicit server event만 소유한다 |
| React visual workbench | `app/web/institutional_portfolios_react_component.py`, `app/web/streamlit_components/institutional_portfolios_workbench/`; `InstitutionalStudioShell`의 content-first page header, manager/data controls, horizontal destination tabs와 portfolio/security presentation을 소유한다 |

## V3 Workbench Contract

- `schema_version`은 `institutional_portfolios_workbench_v3`다.
- canonical destination은 `포트폴리오 맥락 / 분기 리뷰 / 전체 보유 / 종목 상세 / 기관 보유 랭킹` 다섯 개이며 모든 viewport에서 같은 수평 tablist와 `StudioView` state를 사용한다.
- 선택 destination은 full-height left inset bar 없이 text contrast, subtle background와 짧은 bottom underline으로 표시한다. 좁은 화면에서는 tablist 자체만 수평 스크롤되고 page overflow나 별도 drawer를 만들지 않는다.
- manager는 상단 bounded disclosure picker에서 검색·선택한다. 성공한 선택은 검색어를 비우고 requested CIK을 확정하며, load 실패는 기존 manager body를 유지하고 picker 안에 오류를 표시한다. Streamlit의 `.stMain` scroll container를 보존해 긴 manager 사이 전환 뒤 화면이 임의 위치로 이동하지 않게 한다.
- 정상 경로에서 Streamlit title / contextual help / refresh expander / detailed-table fallback은 렌더링하지 않는다. React component가 없을 때만 legacy fallback을 사용한다.
- 첫 화면은 선택 기관의 concentration, largest mapped sector, ticker mapping coverage, previous-quarter readiness를 먼저 요약한다.
- `coverage`는 holding count mapping, mapped reported-value weight, performance-covered weight를 분리한다.
- `holdings_explorer.rows`는 service가 만든 전체 logical holding rows다. React는 이를 조용히 절단하지 않고 50개 고정 page로 렌더링한다.
- 현재 전체 holdings array는 component payload에 계속 직렬화된다. 50-row pagination은 렌더링 DOM만 제한하므로 대형 포트폴리오에서는 payload 크기와 Streamlit rerun latency가 커질 수 있으며, 이것이 실제 병목이 되면 server-side pagination을 후속 선택지로 검토한다.
- holdings search / mapping filter / sector filter / sort / page는 React local state이며 Streamlit rerun을 요구하지 않는다.
- manager selection, manager search, security drilldown / explicit search, popularity load, price collection과 13F hybrid refresh는 명시 event로 Streamlit에 전달한다. Hybrid refresh event는 target report period만 받고 source URL/ZIP/User-Agent는 받지 않는다.
- `분기 리뷰`의 변화 분류, weight, adjusted-close common-equity price coverage, proxy return/contribution은 Python이 계산한다. 저장된 effective history가 3개 이상이면 모든 인접 분기 전환을 한 가격 window로 구성하고 React는 전환 선택/filter/표시만 담당하며 재무 계산을 다시 하지 않는다.
- `분기 리뷰` contribution은 이전 보고 비중 × 종목 수익률의 포트폴리오 수익 기여(`%p`)이며, 종목 수익률(`%`)과 단위를 분리하고 양·음 기여 목록을 sign별로 표시한다.
- `기관 보유 랭킹`은 보유 기관 수 기준이고, 금액은 해당 분기 13F 보고 보유가액 합계다. 이 금액은 시가총액, 거래량 또는 현재 보유액이 아니다.
- 모바일은 manager/data control을 한 열로 쌓고 destination tablist를 수평 스크롤한다. manager search / selection과 dataset refresh 상태는 각 disclosure 내부에서 국소적으로 보여준다.
- manager 검색 결과가 0건이면 watchlist 포함 여부와 관계없이 선택한 normalized CIK의 live manager context를 유지하고 검색어 / 0건 상태를 manager picker에 명시한다. sample preview나 임의 manager로 바꾸지 않는다.
- explicit security search가 선택 manager의 보유 row에는 없더라도 Institutional Interest holder에서 안전한 mapped identity를 찾으면 해당 ticker의 저장 가격 chart와 holder list를 연다. 안전한 identity는 검색어가 normalized ticker / CUSIP과 정확히 일치하거나, 검색 결과 전체의 `(ticker, CUSIP)` identity가 하나뿐일 때만 확정한다. 서로 다른 identity가 여러 개면 `ambiguous` 안내를 표시하고 가격을 조회하지 않는다. 선택 manager가 해당 종목을 보유하지 않으면 position은 `available=false`와 unavailable reason으로 표시하며 0 비중을 만들지 않는다.
- 이전 comparable filing이 없으면 `comparison_available=false`, change groups는 비우고 unavailable reason만 표시한다. 현재 row를 신규 매수처럼 표현하지 않는다.
- unresolved / ambiguous holding은 issuer와 CUSIP을 유지하되 안전한 ticker가 생길 때까지 chart / price action을 열지 않는다.
- `13F-NT`는 제출 완료 판단에는 포함하지만 holdings가 없으므로 최신 portfolio pointer나 분기 변화 row를 만들지 않는다.

## Product Rules

- This surface is read-only research context, not a stock recommender.
- Reported changes are not buy / sell signals.
- 13F filings may be delayed up to 45 days after quarter end.
- 13F rows do not fully show shorts, cash, derivatives, hedge structure, non-reportable securities, or trading intent.
- CUSIP-symbol mapping is best-effort display metadata. Count coverage와 reported-value weight coverage를 같은 수치로 합치지 않는다.
- `institutional_13f_refresh_status`는 마지막 수집일 / 최신 보고분기 / stale reason을 보여주는 제품 freshness metadata다. Full holdings source-of-truth는 filing / holding DB rows다.
- Watchlist manager picker는 seed CIK와 저장 manager row를 병합해 보여준다. Seed가 있다고 해당 manager holdings가 로컬 DB에 저장됐다는 뜻은 아니다.
- The surface does not write workflow registries, saved portfolio setup, broker orders, approval records, or auto-rebalance actions.
- Empty DB state may show a clearly labeled preview workbench so the product layout is understandable, but preview rows must not be represented as current official holdings.

## Verified Actual Snapshot

2026-08-17 actual SEC/MySQL smoke에서 Q2 bulk window는 아직 미공개였고 Berkshire accession
`0001193125-26-352200` raw XML 89 rows를 확인했다. Watchlist 12개 모두 Q2 filing ledger에
반영됐고 그중 2개는 `13F-NT`, holdings는 1,640 rows다. 같은 refresh 재실행 뒤 accession
수는 12개로 유지됐다. Berkshire/Bridgewater/Duquesne는 Q2/Q1 effective quarter가 모두
로드됐고 Berkshire adjusted-close 두 proxy는 +8.42% / +6.48%, price coverage 99.99%였다.

2026-08-17 React v3 actual QA에서 desktop `분기 리뷰`, mobile drawer destination,
두 proxy/coverage/change filter/table, 최신 freshness `2026-06-30`과 1280/760/420 page overflow 없음을 확인했다.
Browser console error/warning은 0건이었다.

2026-08-17 content-first UI actual QA에서 Bill Ackman → David Tepper → Warren Buffett
연속 전환, 전환 뒤 `.stMain` scrollTop 0 유지, 다섯 destination의 background + short underline
선택 표시, desktop bounded picker와 390px stacked controls / horizontal tabs를 확인했다. Browser
console error/warning은 0건이었다.

## IA Decision

The surface belongs in `Workspace` because it is a research and data exploration workflow.
It does not belong in `Operations` because it is not monitoring the user's selected portfolio or system run health.
It does not belong in `Reference` because the user performs active manager / holding exploration rather than reading static guidance.
