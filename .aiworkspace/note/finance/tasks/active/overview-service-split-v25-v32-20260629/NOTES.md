# Overview Service Split V25-V32 Notes

## 2026-06-29

- `app/services/overview_market_intelligence.py` currently owns the calculation body for Sentiment, Events, Data Health, Market Movers, Market Context cockpit, and Why It Moved helpers.
- `app/services/overview/*.py` currently acts mostly as domain import surfaces.
- Split should preserve old `app.services.overview_market_intelligence` imports until final compatibility cleanup.
