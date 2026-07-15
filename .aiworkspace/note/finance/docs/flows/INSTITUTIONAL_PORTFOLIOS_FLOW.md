# Institutional Portfolios Flow

Status: Active
Last Verified: 2026-07-09

## Purpose

`Workspace > Institutional Portfolios`는 Market Movers와 분리된 기관 / 투자 대가 portfolio research surface다.

Market Movers는 선택된 급등락 종목이 왜 관심받는지 보는 곳이고, Institutional Portfolios는 특정 manager의 delayed SEC Form 13F holdings와 분기별 reported change를 탐색하는 곳이다.

## User Flow

```text
Workspace > Ingestion
  -> SEC Form 13F 데이터셋 수집
  -> MySQL finance_meta.institutional_13f_* + refresh status
  -> Workspace > Institutional Portfolios
  -> manager search / watchlist React manager rail
  -> selected manager portfolio allocation donut
  -> top holdings / reported quarter changes / sector exposure
  -> holding click or symbol / CUSIP reverse lookup
  -> source filing link review
```

`Workspace > Institutional Portfolios`에서도 접힌 `SEC 13F data refresh` 보조 패널로 같은 official dataset 수집 job을 실행할 수 있다. 이 패널은 최신화 보조 action이며 첫 화면의 주인공은 manager / portfolio explorer다.

## Screen Ownership

| Step | Owner |
|---|---|
| Official dataset collection | `finance/data/institutional_13f.py`, `app/jobs/ingestion_jobs.py`, `app/web/ingestion/*` |
| DB read path | `finance/loaders/institutional_13f.py`; refresh status도 loader를 통해 읽는다 |
| Visual read model / caveats | `app/services/institutional_portfolios.py`; watchlist rail, freshness, payload contract를 만든다 |
| Streamlit shell / event state | `app/web/institutional_portfolios.py`, `app/web/streamlit_app.py` |
| React visual workbench | `app/web/institutional_portfolios_react_component.py`, `app/web/streamlit_components/institutional_portfolios_workbench/` |

## Product Rules

- This surface is read-only research context, not a stock recommender.
- Reported changes are not buy / sell signals.
- 13F filings may be delayed up to 45 days after quarter end.
- 13F rows do not fully show shorts, cash, derivatives, hedge structure, non-reportable securities, or trading intent.
- CUSIP-symbol mapping is best-effort display metadata.
- `institutional_13f_refresh_status`는 마지막 수집일 / 최신 보고분기 / stale reason을 보여주는 제품 freshness metadata다. Full holdings source-of-truth는 filing / holding DB rows다.
- Watchlist manager rail은 seed CIK와 저장 manager row를 병합해 보여준다. Seed가 있다고 해당 manager holdings가 로컬 DB에 저장됐다는 뜻은 아니다.
- The surface does not write workflow registries, saved portfolio setup, broker orders, approval records, or auto-rebalance actions.
- Empty DB state may show a clearly labeled preview workbench so the product layout is understandable, but preview rows must not be represented as current official holdings.

## IA Decision

The surface belongs in `Workspace` because it is a research and data exploration workflow.
It does not belong in `Operations` because it is not monitoring the user's selected portfolio or system run health.
It does not belong in `Reference` because the user performs active manager / holding exploration rather than reading static guidance.
