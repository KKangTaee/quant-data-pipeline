# Design

## Current Problem

Streamlit tabs eagerly render every tab body. The dashboard currently creates one tab per selected strategy and each tab calls the Monitoring Scenario setup / evidence helpers. This can trigger DB-backed readiness / provider checks for every strategy immediately after a strategy is added.

Full Performance Recheck itself is still behind a button, but the eager detail render makes the page feel like scenario execution started automatically.

## Target Behavior

- Strategy add / slot save only updates saved setup.
- Existing scenario result for the edited strategy is cleared or marked stale so the board does not present an old result as current.
- Section 3 keeps one explicit portfolio-wide run button.
- Individual strategy inspection becomes a selected-strategy detail view instead of eager tabs.

## Tradeoff

This keeps the implementation inside Streamlit without adding async infrastructure. Full portfolio execution can still be slow because it sequentially replays selected strategy contracts; that runtime cost should be addressed later with caching, incremental run selection, or background jobs if needed.
