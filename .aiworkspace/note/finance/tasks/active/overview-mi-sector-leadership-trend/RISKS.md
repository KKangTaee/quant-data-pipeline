# Risks

- Industry groups can be noisy when Top N is large; default should stay compact.
- The trend calculation is DB-backed and can be heavier than the old monthly-only snapshot for Top 2000 / Industry. Keep default Top N compact and revisit caching if interaction becomes slow.
