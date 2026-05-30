# Risks

- Industry groups can be noisy when Top N is large; default should stay compact.
- The trend calculation is DB-backed and can be heavier than the old monthly-only snapshot for Top 2000 / Industry. Keep default Top N compact and revisit caching if interaction becomes slow.
- Expanded Daily / Weekly / Monthly windows increase DB work for Top 2000 + Industry views. If the UI feels slow in regular use, add a short-lived cache around the group leadership read model.
- Positive Return Share is an exploratory decomposition of positive ticker returns, not a formal sector attribution model. Use wording and table columns to avoid reading it as cap-weighted contribution.
- Daily trend rows now combine historical EOD daily windows with one current intraday point. This is useful for current leadership, but charts should keep `Price Mode` / `Return Window` visible so users do not confuse intraday and EOD windows.
