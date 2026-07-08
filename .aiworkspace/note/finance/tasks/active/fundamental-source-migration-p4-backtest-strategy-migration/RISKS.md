# Phase 4. Backtest Strategy Migration Risks

- Old saved/history records may still display `Quality Snapshot` when replaying legacy broad runs. That is intentional compatibility, not a new default path.
- The broad yfinance factor runner still exists and must remain until Phase 7 decommissioning decides final legacy exposure.
- Quarterly prototypes remain selectable as explicit variants; they should not be treated as production-ready until synthetic Q4 / quarterly source QA is complete.
