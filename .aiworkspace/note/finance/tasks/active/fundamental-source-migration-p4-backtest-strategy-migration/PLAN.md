# Phase 4. Backtest Strategy Migration Plan

## 이걸 하는 이유?

Market Movers와 source contract가 EDGAR-first로 정리되어도 Backtest Analysis 기본 진입이 broad yfinance factor path처럼 보이면 사용자는 새 canonical source를 쓰지 않을 수 있다. Phase 4는 새 backtest 시작점을 statement annual factor path로 옮기고, legacy broad Quality는 saved/history compatibility 경로로 낮춘다.

## 범위

- `app/services/backtest_strategy_catalog.py`: strategy option ordering, default single/compare options, legacy broad key contract.
- `app/web/backtest_strategy_catalog.py`: web wrapper export sync.
- `app/web/backtest_single_strategy.py`: Single Strategy default selection.
- `app/web/backtest_compare.py`: Portfolio Mix Builder default compare selection.
- `app/web/backtest_common.py`: Broad vs Strict guide wording.
- `tests/test_backtest_strategy_evidence_inventory.py`: catalog/default/UI contract tests.
- `docs/flows/BACKTEST_UI_FLOW.md`, `docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md`: user flow and source boundary alignment.

## 완료 조건

- 새 Single Strategy 진입 기본값이 `Quality + Value / Strict Annual`이다.
- Portfolio Mix Builder 기본 전략이 `Quality + Value`, `GTAA`, `Equal Weight` bridge 조합이다.
- legacy broad `Quality Snapshot`은 새 사용자 선택지에 노출되지 않고 replay / compatibility 경로로만 남는다.
- saved/history replay compatibility를 위해 legacy key와 runner는 삭제하지 않는다.
