# Runs

- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_mover_research_snapshot_exposes_fundamental_chart_trends tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_mover_research_snapshot_model_builds_fundamental_chart_payload tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_mover_research_chart_html_renders_bar_rows tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_research_snapshot_component_adds_metric_and_frequency_tabs` -> PASS.
- `.venv/bin/python -m unittest -k market_mover_research tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` -> PASS, 12 tests.
- `.venv/bin/python -m py_compile app/services/overview/why_it_moved.py app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/web/overview/components/common.py` -> PASS.
- `git diff --check` -> PASS.
- Browser QA on `http://localhost:8510`: 기본 지표 표 유지, 하단 PER/EPS/당기순이익/유동비율/FCF tabs, annual/quarterly tabs, PER annual bars, FCF quarterly bars 확인. Screenshots are local generated artifacts.
