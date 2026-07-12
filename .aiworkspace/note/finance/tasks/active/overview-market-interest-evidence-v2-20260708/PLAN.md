# Overview Market Interest Evidence V2 Plan

Status: Active
Started: 2026-07-08

## 이걸 하는 이유?

V1은 안전했지만 사용자가 지적한 것처럼 `원문 확인` 링크 허브에 가까웠다. 이번 V2는 Market Movers 선택 종목에서 실제로 앱이 확인한 뉴스 / 한국어 뉴스 / SEC metadata를 `시장 관심` 탭 안에 보여주고, 원문 링크는 보조 disclosure로 낮춘다.

## Scope

- 1차: `시장 관심` read model 상태와 섹션 구조를 V2로 바꾼다.
- 2차: `시장 관심 근거 확인` 버튼이 기존 뉴스 / 한국어 뉴스 / SEC metadata를 함께 조회한다.
- 3차: 애널리스트 관심은 구조화 source 미연결 상태와 source-ready contract로 정리한다. FMP/Finnhub API 연동은 키/약관 승인 전이므로 이번 범위에서 제외한다.
- 4차: 13F는 issuer SEC filing과 다른 `기관 보유 배경 · 13F 지연 자료`로 표시한다.
- 5차: `뉴스`, `SEC 공시`, `외부 검색`, `원문 확인`을 별도 중심 탭으로 두지 않고 `시장 관심` 안의 evidence/disclosure로 흡수한다.

## Non Goals

- FMP/Finnhub/Naver API credential integration.
- SEC 13F DB schema / ingestion / CUSIP-symbol mapping.
- Article body, analyst report body, filing body collection or storage.
- Recommendation, score, buy/sell signal, automatic catalyst classification.
- Live trading, broker order, portfolio approval, auto rebalance.

## Implementation Plan

Detailed agentic plan: `docs/superpowers/plans/2026-07-08-market-interest-evidence-v2.md`

## Verification

- TDD RED/GREEN focused tests.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests ...`
- `.venv/bin/python -m py_compile app/services/overview/market_interest.py app/web/overview/market_movers_helpers.py`
- `git diff --check`
- Browser QA screenshot, not committed.
