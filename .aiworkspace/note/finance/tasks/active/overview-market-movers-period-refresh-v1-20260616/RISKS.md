# Risks

- Real OHLCV provider execution may be slow or rate-limited, especially Top1000 / Top2000.
- Browser QA should verify button rendering without necessarily executing large provider collection.
- The active task folder is created for this implementation record; retained historical active folders are not treated as open tasks.
- Actual provider collection was not run in QA. Remaining risk is provider volatility / runtime cost when the user presses `가격 이력 갱신`, especially for Top1000 / Top2000.
