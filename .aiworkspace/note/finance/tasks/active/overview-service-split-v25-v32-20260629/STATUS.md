# Overview Service Split V25-V32 Status

Status: Active
Started: 2026-06-29

## Progress

- 2026-06-29: V25-V32 service split task opened. Target is to move Overview market intelligence implementation bodies from the monolithic `app/services/overview_market_intelligence.py` into domain service modules while preserving compatibility imports.
- 2026-06-29: V25 task baseline and QA criteria documented.
- 2026-06-29: V26 Sentiment service body extracted into `app/services/overview/sentiment.py`; legacy import path remains compatible.
- 2026-06-29: V27 Events service body extracted into `app/services/overview/events.py`; event calendar and macro week lane implementation now live on the domain surface.

## Current Step

- V28: Data Health service extraction.
