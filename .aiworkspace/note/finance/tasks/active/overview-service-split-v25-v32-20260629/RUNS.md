# Overview Service Split V25-V32 Runs

## 2026-06-29

- V25 QA: `test -f .../PLAN.md && test -f .../STATUS.md` -> pass.
- V25 QA: `.venv/bin/python -m py_compile app/services/overview_market_intelligence.py app/services/overview/sentiment.py app/services/overview/events.py app/services/overview/data_health.py app/services/overview/market_movers.py app/services/overview/market_context.py tests/test_service_contracts.py` -> pass.
- V26 RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_sentiment_service_owns_implementation_body` -> failed because `sentiment.py` was still a re-export wrapper.
- V26 QA: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_sentiment_service_owns_implementation_body` -> pass.
- V26 QA: `.venv/bin/python -m py_compile app/services/overview/sentiment.py tests/test_service_contracts.py` -> pass.
- V26 QA: direct `app.services.overview.sentiment.build_market_sentiment_snapshot` empty-frame smoke -> returned `MISSING` with expected read-model keys.
- V26 QA: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_snapshot_summarizes_cnn_and_aaii_context` -> pass.
- V27 RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_events_service_owns_implementation_body` -> failed because `events.py` was still a re-export wrapper.
- V27 QA: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_events_service_owns_implementation_body` -> pass.
- V27 QA: `.venv/bin/python -m py_compile app/services/overview/events.py tests/test_service_contracts.py` -> pass.
- V27 QA: direct `app.services.overview.events` empty-query smoke -> event snapshot `NO_EVENTS`, macro week lane `NO_DATA`.
- V27 QA: legacy path event tests `test_market_events_snapshot_macro_filter_reads_macro_prefix_rows`, `test_market_events_snapshot_warns_on_stale_earnings_estimates`, `test_overview_macro_week_lane_clusters_near_events_without_signal_language`, `test_overview_macro_week_lane_splits_recent_and_upcoming_major_macro_events` -> pass.
- V28 RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_data_health_service_owns_implementation_body` -> failed because `data_health.py` was still a re-export wrapper.
- V28 QA: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_data_health_service_owns_implementation_body` -> pass.
- V28 QA: `.venv/bin/python -m py_compile app/services/overview/data_health.py tests/test_service_contracts.py` -> pass.
- V28 QA: direct `app.services.overview.data_health` empty-query smoke -> collection ops `REVIEW`, handoff schema `overview_data_health_ingestion_handoff_v1`.
- V28 QA: legacy path data health tests `test_collection_ops_snapshot_combines_db_freshness_and_run_history`, `test_collection_ops_snapshot_tracks_market_sentiment_freshness`, `test_overview_data_health_handoff_ranks_problem_rows_and_points_to_collection_surfaces` -> pass.
