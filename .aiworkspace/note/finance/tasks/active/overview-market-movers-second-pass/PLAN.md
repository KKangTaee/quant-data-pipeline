# Overview Market Movers Second Pass Plan

Status: Active
Owner: sub-dev
Started: 2026-05-30

## 이걸 하는 이유?

Market Movers는 사용자가 장중 시장 리더와 약한 구간을 빠르게 읽는 Overview 핵심 화면이다. 1차 구현은 S&P 500 daily 자동 갱신과 수익률 ranking 중심으로 완성됐지만, 실제 사용 흐름에서는 Top1000 / Top2000 coverage, 거래량, 섹터별 시각 구분, 직전 기간 대비 momentum 해석이 함께 필요하다.

## Scope

- Market Movers daily browser-session auto refresh를 선택된 coverage 기준으로 확장한다.
- Market Movers read model에 volume / dollar volume과 직전 동일 기간 return / momentum delta를 추가한다.
- Market Movers chart를 return ranking, volume ranking, sector pulse로 확장한다.
- 양수 return bar는 sector color, 음수 return bar는 기존 danger red로 표시한다.
- Momentum 비교는 매매 신호가 아니라 후보 탐색용 보조 정보로 표시한다.
- Return Rank / Volume Rank에서 선택 가능한 ticker 기준으로 Catalyst Links를 제공한다.
- Catalyst Links는 Yahoo Finance, Google News, SEC company search, 회사 IR / earnings 검색으로 이동하는 outbound start point만 제공한다.

## Out Of Scope

- live alert, broker order, auto rebalance.
- 모든 coverage를 한 번에 돌리는 unattended broad refresh.
- Relative Volume 정식 지표. 평균 거래량 window가 필요하므로 후속으로 남긴다.
- AI 요약, 기사 본문 수집, 웹 크롤링, provider / website 직접 fetch.
- Backtest / Practical Validation workflow 변경.

## Expected Files

- `app/services/overview_market_intelligence.py`
- `app/web/overview_dashboard.py`
- `app/web/overview_ui_components.py`
- `app/jobs/overview_automation.py`
- `tests/test_service_contracts.py`
- `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`

## Verification

- `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_ui_components.py app/jobs/overview_automation.py app/services/overview_market_intelligence.py`
- focused `tests.test_service_contracts`
- `uv run python -m app.jobs.overview_automation --profile browser_safe --dry-run --json`
- `git diff --check`
