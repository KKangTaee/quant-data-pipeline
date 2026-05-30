# Overview Market Intelligence First Slice

Status: Active
Started: 2026-05-28

## 이걸 하는 이유?

Overview 개편의 첫 개발 단위는 외부 calendar ingestion보다 위험이 낮고 즉시 가치가 큰 DB-backed market scan이다.
기존 price/profile DB만으로 일/주/月 top movers와 월별 sector / industry leadership을 보여주면, 이후 FOMC / earnings calendar를 붙이기 전에도 사용자는 시장 현재 상태를 빠르게 읽을 수 있다.

## Scope

- Streamlit-free market intelligence service 추가
- Coverage 1000 / 2000 movers 계산
- sector / industry monthly leadership 계산
- Overview tab UI 추가
- 기존 candidate ops 보존
- focused service tests 추가

## Out Of Scope

- FOMC collector
- earnings collector
- DB schema 변경
- heatmap visualization
- 유료 API
- Overview 직접 웹 파싱

## Verification

- `uv run python -m unittest tests.test_service_contracts`
- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py`
- `.aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `git diff --check`
- Browser smoke for `Workspace > Overview`
