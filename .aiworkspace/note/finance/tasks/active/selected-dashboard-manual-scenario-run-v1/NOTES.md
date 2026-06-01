# Notes

- User observation: after first portfolio scenario run, adding another strategy appears to trigger the lower scenario / individual performance section automatically and causes a long wait.
- Initial code read: portfolio-wide recheck is behind `포트폴리오 시나리오 실행`, but `st.tabs` renders all strategy detail tabs and each tab builds Monitoring Scenario evidence on page rerun.
- Main fix should reduce eager render and make stale results explicit.
- Session result keys were decision-only before this task. That could reuse a scenario result across different dashboard portfolios or changed slot settings.
- New behavior: a result is current only when portfolio id, slot id, selected decision id, start, end, latest-end mode, and capital match the current slot signature.
- Portfolio-wide update defaults to pending / stale strategies only; `전체 재실행` is the explicit full refresh path.
- Full replay is still sequential because each selected strategy contract calls the existing candidate replay runtime. This is not a UI auto-run bug, but it can still be slow for many strategies or long periods.
