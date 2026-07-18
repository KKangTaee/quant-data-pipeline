# Institutional Portfolios Flow

Status: Active
Last Verified: 2026-07-18

## Purpose

`Workspace > Institutional Portfolios`는 Market Movers와 분리된 기관 / 투자 대가 portfolio research surface다.

Market Movers는 선택된 급등락 종목이 왜 관심받는지 보는 곳이고, Institutional Portfolios는 특정 manager의 delayed SEC Form 13F holdings와 분기별 reported change를 탐색하는 곳이다.

## User Flow

```text
Workspace > Ingestion
  -> SEC Form 13F 데이터셋 수집
  -> MySQL finance_meta.institutional_13f_* + refresh status
  -> Workspace > Institutional Portfolios
  -> selected manager context hero / filing basis
  -> allocation / concentration / comparison readiness / mapping and performance coverage
  -> full holdings explorer: ticker / issuer / CUSIP search + mapping / sector filters + sort + 50-row page
  -> mapped holding click or explicit security search
  -> DB-backed price chart / selected-manager position / latest-filing holders
  -> source filing link review
```

`Workspace > Institutional Portfolios`에서도 접힌 `SEC 13F data refresh` 보조 패널로 같은 official dataset 수집 job을 실행할 수 있다. 이 패널은 최신화 보조 action이며 첫 화면의 주인공은 manager / portfolio explorer다.

## Screen Ownership

| Step | Owner |
|---|---|
| Official dataset collection | `finance/data/institutional_13f.py`, `app/jobs/ingestion_jobs.py`, `app/web/ingestion/*` |
| DB read path | `finance/loaders/institutional_13f.py`; refresh status도 loader를 통해 읽는다 |
| Visual read model / caveats | `app/services/institutional_portfolios.py`; v2 context summary, coverage, full holdings explorer, explicit security search, comparison state, watchlist rail, freshness, caveats를 만든다 |
| Streamlit shell / event state | `app/web/institutional_portfolios.py`, `app/web/streamlit_app.py` |
| React visual workbench | `app/web/institutional_portfolios_react_component.py`, `app/web/streamlit_components/institutional_portfolios_workbench/`; context-first layout와 local search / filter / sort / pagination state를 소유한다 |

## V2 Workbench Contract

- `schema_version`은 `institutional_portfolios_workbench_v2`다.
- 첫 화면은 선택 기관의 concentration, largest mapped sector, ticker mapping coverage, previous-quarter readiness를 먼저 요약한다.
- `coverage`는 holding count mapping, mapped reported-value weight, performance-covered weight를 분리한다.
- `holdings_explorer.rows`는 service가 만든 전체 logical holding rows다. React는 이를 조용히 절단하지 않고 50개 고정 page로 렌더링한다.
- 현재 전체 holdings array는 component payload에 계속 직렬화된다. 50-row pagination은 렌더링 DOM만 제한하므로 대형 포트폴리오에서는 payload 크기와 Streamlit rerun latency가 커질 수 있으며, 이것이 실제 병목이 되면 server-side pagination을 후속 선택지로 검토한다.
- holdings search / mapping filter / sector filter / sort / page는 React local state이며 Streamlit rerun을 요구하지 않는다.
- manager selection, manager search, security drilldown / explicit search, popularity load, price collection은 명시 event로 Streamlit에 전달한다.
- manager 검색 결과가 0건이면 선택한 live manager context를 유지하고 검색어 / 0건 상태를 manager rail에 명시한다. sample preview나 임의 manager로 바꾸지 않는다.
- explicit security search가 선택 manager의 보유 row에는 없더라도 Institutional Interest holder에서 안전한 mapped identity를 찾으면 해당 ticker의 저장 가격 chart와 holder list를 연다. 이때 selected-manager position은 `available=false`와 unavailable reason으로 표시하며 0 비중을 만들지 않는다.
- 이전 comparable filing이 없으면 `comparison_available=false`, change groups는 비우고 unavailable reason만 표시한다. 현재 row를 신규 매수처럼 표현하지 않는다.
- unresolved / ambiguous holding은 issuer와 CUSIP을 유지하되 안전한 ticker가 생길 때까지 chart / price action을 열지 않는다.

## Product Rules

- This surface is read-only research context, not a stock recommender.
- Reported changes are not buy / sell signals.
- 13F filings may be delayed up to 45 days after quarter end.
- 13F rows do not fully show shorts, cash, derivatives, hedge structure, non-reportable securities, or trading intent.
- CUSIP-symbol mapping is best-effort display metadata. Count coverage와 reported-value weight coverage를 같은 수치로 합치지 않는다.
- `institutional_13f_refresh_status`는 마지막 수집일 / 최신 보고분기 / stale reason을 보여주는 제품 freshness metadata다. Full holdings source-of-truth는 filing / holding DB rows다.
- Watchlist manager rail은 seed CIK와 저장 manager row를 병합해 보여준다. Seed가 있다고 해당 manager holdings가 로컬 DB에 저장됐다는 뜻은 아니다.
- The surface does not write workflow registries, saved portfolio setup, broker orders, approval records, or auto-rebalance actions.
- Empty DB state may show a clearly labeled preview workbench so the product layout is understandable, but preview rows must not be represented as current official holdings.

## Verified Actual Snapshot

2026-07-18 actual DB smoke에서 Berkshire `29`, Bridgewater `993`, Duquesne `70` logical holding rows가 각각 explorer row 수와 일치했다. Bridgewater는 `1–50 / 993`, `51–100 / 993`, 총 20 page로 확인했다. 세 기관 모두 local previous filing이 없어 comparison unavailable이었으며 change groups는 표시하지 않았다.

## IA Decision

The surface belongs in `Workspace` because it is a research and data exploration workflow.
It does not belong in `Operations` because it is not monitoring the user's selected portfolio or system run health.
It does not belong in `Reference` because the user performs active manager / holding exploration rather than reading static guidance.
