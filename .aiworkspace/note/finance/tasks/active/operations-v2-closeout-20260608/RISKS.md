# Risks

## 2026-06-08

- Direct local `/operations` first-load QA can show a Streamlit Page not found modal. Use root `/` -> top navigation -> `Operations Overview` for canonical local QA until the Streamlit routing behavior is revisited.
- Archive helper code and old Backtest History / Candidate Library data were not deleted in Operations V2. Removing them remains a separate audit / migration decision because those helpers can still support compatibility and historical inspection paths.
- Operations Overview remains read-only. It does not execute provider fetches, replay scenarios, write registries/saved setup, place orders, sync accounts, or auto rebalance.
