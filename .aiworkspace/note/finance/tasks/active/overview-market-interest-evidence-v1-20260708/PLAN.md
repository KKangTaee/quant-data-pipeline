# Overview Market Interest Evidence V1 Plan

Status: Active
Started: 2026-07-08

## 이걸 하는 이유?

Market Movers에서 선택한 종목을 볼 때 가격/거래량/기본 지표만으로는 사용자가 "왜 더 조사해야 하는가"를 빠르게 판단하기 어렵다.
이번 작업은 애널리스트 행동, 뉴스/SEC 공시, 13F 기관 보유 배경, 원문 링크를 한 곳에서 확인하는 조사 보조 패널을 만든다.

## Scope

- 1차: 선택 종목 수동 패널에 `시장 관심` UX를 추가한다.
- 2차: 선택 종목 1개, 사용자 버튼 클릭, 세션 전용 또는 outbound link 중심 MVP를 구현한다.
- 3차: SEC 13F는 official durable source 후보로 설계하고, CUSIP-symbol mapping과 지연/불완전 caveat를 명시한다. V1에서는 DB schema를 추가하지 않는다.
- 4차: `관심 근거 있음 / 원문 확인 필요 / 지연 자료 / 데이터 없음 / 미구축` 같은 보수적 상태만 보여준다.

## Non Goals

- 추천 종목 생성
- 점수화, buy/sell, 매수/매도 신호
- 자동 catalyst 판정
- article body, analyst report body, filing body 수집/저장
- 13F를 실시간 기관 매수로 표현
- live trading, broker order, auto rebalance 연결

## Expected Files

- `app/services/overview/market_interest.py`
- `app/web/overview/market_movers_helpers.py`
- `tests/test_service_contracts.py`
- `.aiworkspace/note/finance/docs/ROADMAP.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/data/README.md`
- root handoff logs

## Verification

- TDD RED/GREEN focused tests
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests`
- `.venv/bin/python -m py_compile ...`
- `git diff --check`
- Browser QA screenshot, not committed
