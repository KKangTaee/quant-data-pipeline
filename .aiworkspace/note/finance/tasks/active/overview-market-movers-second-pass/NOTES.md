# Notes

- Browser-session auto refresh should run only the selected Market Movers coverage, not all intraday jobs.
- Existing local run history shows Top1000 quote-fast snapshots around 6.5-7.1 seconds and Top2000 around 12.5 seconds, but provider timeout / fallback can stretch much longer.
- Momentum comparison should be framed as context for trend persistence, not as a buy/sell recommendation.
- Volume Rank should not sort the already return-ranked Top N subset. It now ranks a separate `volume_rows` frame over the returnable universe.
- Daily volume means the current stored intraday snapshot / EOD day. Weekly / monthly / yearly volume means the current return window's average daily volume / average daily dollar volume plus total period volume / dollar volume.
- Top2000 yearly still spends most time resolving the eligible date window, not aggregating volume. The new volume aggregation itself is roughly 1 second locally after index-forced symbol/date reads.
- Catalyst Links are a manual investigation launchpad, not a catalyst classifier. The service builds a row model from selected symbol, name, period, coverage, rank type, and rank; the UI only renders those outbound rows.
- Catalyst Links intentionally do not fetch Yahoo / Google / SEC / IR pages from the UI. Search URLs are prebuilt so users can inspect sources manually in a new browser context.
- Why It Moved V1.5 keeps the same manual-investigation boundary but adds the selected mover's existing row context before outbound research. It is not an automatic cause detector and should not label a movement as earnings, filing, macro, analyst, or sentiment driven.
- Compact metadata lookup is button-triggered for one selected ticker only. Selectbox changes rebuild the read model and outbound links, but do not call yfinance, SEC, or any external source.
- Compact news metadata stores only title, source / publisher, published time, and URL in current Streamlit session state. Compact SEC metadata stores only form, filing date, title / description, and URL. Article bodies and filing bodies are intentionally excluded.
- Session-only was chosen because V1.5 is an investigation aid with provider fragility and no durable evidence review policy yet. DB-backed compact metadata belongs to a later V2 only after retention, source quality, freshness, and replay semantics are approved.
