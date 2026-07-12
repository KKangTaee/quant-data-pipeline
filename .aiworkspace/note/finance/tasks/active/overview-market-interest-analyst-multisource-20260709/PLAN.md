# Overview Market Interest Analyst Multi-Source Plan

Status: Active
Started: 2026-07-09

## 이걸 하는 이유?

Market Movers에서 선택 종목의 `애널리스트 관심`이 외부 링크 안내에 머물러 실제로 프로그램이 파악한 조사 단서를 보여주지 못한다. 사용자는 여러 공개 금융 사이트의 애널리스트 평가를 한 화면에서 비교하고 싶어하지만, Nasdaq / WSJ / MarketWatch / Yahoo는 데이터 제공자와 약관 제약이 다르다. 따라서 V1은 선택 종목 버튼 조회, 세션 전용 구조화 단서, 원문 교차확인 링크를 결합한다.

## Scope

- Overview > Market Movers > 선택 종목 > 시장 관심 탭.
- 선택 종목 1개에 대해서만 동작.
- 사용자가 `시장 관심 근거 확인` 버튼을 누를 때만 yfinance analyst metadata를 조회한다.
- Yahoo/yfinance 구조화 단서: 최근 upgrades/downgrades, 목표가 요약, recommendation distribution.
- Nasdaq.com / WSJ Markets / MarketWatch / Yahoo Finance: 원문 교차확인 카드와 링크.
- DB schema, ingestion, registry, saved JSONL 변경 없음.

## Non-Goals

- 종목 추천, 점수화, 매수/매도 신호 생성.
- Market Movers 전체 종목 자동 분석.
- article body, analyst report body, filing body 저장.
- Nasdaq / WSJ / MarketWatch HTML 자동 크롤러 또는 우회 로직.
- 유료 API / 로그인 / 캡차 / paywall 우회.
- live trading, broker order, auto rebalance 연결.

## 단계

1. yfinance 구조화 analyst metadata fetch/normalize.
2. market_interest read model에 analyst rows와 multi-source source cards 통합.
3. Streamlit 시장 관심 렌더러에서 애널리스트 action / 목표가 / 추천 분포 / 교차확인 출처를 표시.
4. 버튼 흐름에서 selected-symbol analyst metadata를 세션 전용으로 병합.
5. focused tests, py_compile, diff check, Browser QA, 문서 sync, commit.

## 변경 예상 파일

- `app/services/overview/market_interest.py`
- `app/web/overview/market_movers_helpers.py`
- `tests/test_service_contracts.py`
- `.aiworkspace/note/finance/tasks/active/overview-market-interest-analyst-multisource-20260709/*`
- `docs/superpowers/plans/2026-07-09-market-interest-multi-source-analyst.md`
