# Overview Service Split V25-V32 Status

Status: Active
Started: 2026-06-29

## Progress

- 2026-06-29: V25-V32 service split task opened. Target is to move Overview market intelligence implementation bodies from the monolithic `app/services/overview_market_intelligence.py` into domain service modules while preserving compatibility imports.
- 2026-06-29: V25 task baseline and QA criteria documented.
- 2026-06-29: V26 Sentiment service body extracted into `app/services/overview/sentiment.py`; legacy import path remains compatible.
- 2026-06-29: V27 Events service body extracted into `app/services/overview/events.py`; event calendar and macro week lane implementation now live on the domain surface.
- 2026-06-29: V28 Data Health service body extracted into `app/services/overview/data_health.py`; collection ops and ingestion handoff implementation now live on the domain surface.
- 2026-06-29: V29 Market Movers service body extracted into `app/services/overview/market_movers.py`; movers, group leadership, breadth, and date window helpers now live on the domain surface.
- 2026-06-29: V30 Market Context service body extracted into `app/services/overview/market_context.py`; cockpit and source confidence now compose the split domain services.

## Current Step

- V31: Why It Moved service extraction.
