# Current Project Audit

## Snapshot

이번 요청은 미국장 개장 중 데이터만 보는 기존 `Workspace > Overview`를 확장해, 선물장이 움직이는 동안 주요 자산 선물의 OHLCV 캔들과 급변 신호를 read-only로 확인하려는 제품 방향 리서치다.

핵심 목적은 자동매매나 주문이 아니라, 한국장 또는 미국장 현물 개장 전에 글로벌 선물 흐름이 가파르게 움직이는지 미리 감지하는 것이다.

## Local Evidence

| Area | Local source | What it proves |
| --- | --- | --- |
| Product boundary | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | 현재 finance 제품은 evidence-first quant workspace이며 live approval, broker order, auto rebalance가 아니다. |
| Architecture | `.aiworkspace/note/finance/docs/architecture/README.md` | UI에서 provider를 직접 fetch하지 않고 ingestion -> DB -> loader/service -> UI 흐름을 유지해야 한다. |
| Overview ownership | `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Overview market intelligence는 `finance/data/market_intelligence.py`, `app/jobs/ingestion_jobs.py`, `app/services/overview_market_intelligence.py`, `app/web/overview_dashboard.py`가 담당한다. |
| Current Overview runbook | `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md` | Overview는 이미 browser-session gated auto refresh, Data Health, Market Movers, Sector / Industry, Events를 운영한다. |
| Local code | `app/web/overview_dashboard.py` | `st.fragment(run_every=...)` 기반 자동 갱신 패턴과 market refresh status bar가 이미 있다. |
| Chart stack | `pyproject.toml`, `app/web/overview_dashboard.py` | 현재 앱은 Streamlit + Altair 중심이며 Plotly는 의존성이 없다. |

## Surface Classification

| Surface | Role | Notes |
| --- | --- | --- |
| `Workspace > Overview` | User-facing market intelligence | 1차 위치로 적합하다. 기존 Market Movers와 같은 시장 컨텍스트 화면이다. |
| `Workspace > Ingestion` | Mixed / ops | futures OHLCV refresh, symbol preset refresh, provider smoke result를 실행하는 위치다. |
| `Operations > Selected Portfolio Dashboard` | User-facing selected monitoring | 선정 포트폴리오 모니터링 화면이다. broad futures monitor를 직접 넣기보다 연결 신호 정도만 나중에 고려한다. |
| `Backtest > ...` | Strategy research workflow | 선물 monitor는 후보 생성/검증 흐름과 분리해야 한다. |

## Current Strengths

- Overview에 이미 Market Intelligence 탭 구조, refresh status, run history, Data Health 개념이 있다.
- app/jobs와 app/services 경계가 있어 provider fetch를 UI render 안에 넣지 않고 확장할 수 있다.
- Streamlit fragment 기반 browser-session refresh 패턴이 있어 futures polling에도 재사용 가능하다.
- `yfinance`가 프로젝트 의존성에 있고 로컬 `.venv`에서 `yfinance 1.1.0`이 확인됐다.
- 2026-06-02 로컬 스모크에서 주요 CME 계열 Yahoo futures 심볼의 1분봉이 내려왔다.

## Current Weaknesses

- 현재 DB schema와 market intelligence service는 주식/이벤트 중심이며 futures instrument, futures OHLCV, futures provider run status를 위한 명시적 저장소가 없다.
- 선물은 거래 시간이 자산/거래소/휴장일별로 다르고, 23시간에 가까운 세션을 단순 NYSE open/close로 설명하면 오해가 생긴다.
- 무료 provider는 실시간성, 지연 시간, rate limit, 심볼 coverage, 계속성 보장이 약하다.
- 매초 provider fetch는 무료 소스와 Streamlit 런타임 모두에 부담이 크다.
- Altair로 캔들 차트는 구현 가능하지만, 전문 트레이딩 차트 수준의 pan/zoom/수천봉 렌더링은 TradingView Lightweight Charts나 별도 frontend가 더 적합하다.

## yfinance Smoke Result

2026-06-02에 `.venv/bin/python`으로 `yf.download(symbol, period="1d", interval="1m")`를 확인했다.

| Bucket | Symbols with 1m rows | Notes |
| --- | --- | --- |
| Equity index | `ES=F`, `NQ=F`, `YM=F`, `RTY=F`, `MES=F`, `MNQ=F`, `M2K=F` | 1일 1분봉 rows가 약 1,100개 수준으로 내려왔다. |
| Commodities | `CL=F`, `GC=F`, `SI=F`, `HG=F`, `NG=F`, `MCL=F` | 원유, 금, 은, 구리, 천연가스 1분봉이 내려왔다. |
| Rates | `ZN=F`, `ZB=F` | 미국 10년/30년 국채 선물 1분봉이 내려왔다. |
| FX futures | `6E=F`, `6J=F`, `6B=F`, `6A=F`, `6C=F` | EUR, JPY, GBP, AUD, CAD futures proxy로 사용 가능하다. |
| Crypto futures | `BTC=F`, `MBT=F`, `ETH=F` | optional watchlist로 가능하지만 noise와 venue 차이를 표시해야 한다. |
| Failed in smoke | `DX=F`, `VX=F` | Yahoo quote not found 또는 empty였다. 1차 preset에서 제외한다. |

## Audit Conclusion

선물 모니터링은 기존 Overview의 새 탭으로 시작하는 것이 가장 자연스럽다. 단, 구현은 "실시간 트레이딩 터미널"이 아니라 "무료 provider 기반 개장 전 위험/방향 스캐너"로 정의해야 한다.

1차 구현은 `yfinance` 1분봉 polling, DB 저장, Overview read model, Altair candlestick, 급변 score, provider status, refresh cadence 표시로 제한한다. CME official real-time/paid API, KRX derivatives, 전문 chart frontend는 후속 옵션으로 둔다.
