# UI And Workflow Patterns

Status: Complete
Last Updated: 2026-07-16

## Product Goal

Let the user answer five questions without reading raw tables: where is the U.S. economy now, how did it get there, where may it move in one and two months, how uncertain is that path, and which evidence changed the view.

## Pattern 1. Cycle Clock As The Main Spatial Model

- Use a two-axis phase plane: horizontal `추세 대비 활동 수준`, vertical `경기 모멘텀`.
- Divide it into `회복`, `확장`, `둔화`, `침체` quadrants.
- Plot the last 12–18 monthly observations as a fading trail.
- Emphasize the latest point; plot +1M and +2M forecasts with dashed arrows and uncertainty ellipses.
- This answers location and direction better than a conventional single line chart.
- Risk: precise coordinates can imply more certainty than the model supports. Show probability and confidence alongside the point.

## Pattern 2. Regime Ribbon For Calendar History

- Place a 10Y / 20Y / all-history ribbon below the clock.
- Color each month by the most likely model phase; shade official NBER recessions separately with a labeled hatch.
- Append +1M and +2M forecast segments with diagonal or translucent fill so forecast is never mistaken for history.
- Hover/detail shows the probability vector, data cutoff, and top drivers for that month.
- This solves the phase clock's weakness: the clock shows trajectory but not calendar duration.

## Pattern 3. Probability Horizon Strip

- Show `현재`, `1개월 후`, `2개월 후` in one aligned strip.
- Each horizon uses the same four-color probability bar and prints the leading phase plus percentage.
- Add confidence state (`충분`, `주의`, `제한`) based on calibration and input coverage, not model probability alone.
- Do not use a speedometer or one-number score; it hides alternate scenarios.

## Pattern 4. Evidence Pillars Before Raw Indicators

- Summarize four pillars: `실물 활동`, `고용·소득`, `물가·정책`, `금융 여건`.
- Each pillar shows direction, breadth, latest reference month, and the one or two largest contributors.
- Put `금리·신용·달러·금` in a separate `시장이 선반영하는 맥락` row.
- Expanders can show original series, transformation, source, release date, and vintage.
- The first screen remains a workflow answer, not a diagnostic job panel.

## Pattern 5. Vintage And Ragged-Edge Disclosure

- The header shows `판단 기준일`, `가장 오래된 핵심 입력`, `다음 주요 발표`.
- A compact evidence drawer explains which reference months are mixed and whether any series is provisional or revised.
- Current probability can update as releases arrive, but the previous forecast remains replayable by vintage.

## Recommended Page Order

1. Current phase sentence and probability horizon strip.
2. Cycle clock with historical trail and +1M/+2M forecast.
3. Calendar regime ribbon.
4. Four evidence pillars and `시장 선반영 맥락` overlay.
5. Method, source, vintage, and historical validation details.

## Pattern Conflicts With Current Boundaries

| Pattern | Conflict | Handling |
| --- | --- | --- |
| Buy/sell labels by phase | Turns context into an investment instruction | Exclude from V1 and keep downstream investment decisions separate. |
| Gold / dollar / rates determine the phase | Confuses financial regimes with real activity | Use them only as leading or explanatory overlays. |
| One deterministic future phase | Hides uncertainty and model instability | Always show the full four-phase probability distribution. |
| NBER-style definitive recession copy | Misrepresents a retrospective chronology | Label the result `모델 추정` and show official NBER history separately. |
| Raw job status on the first screen | Violates real-use improvement rules | Keep collection diagnostics in Ingestion; show only actionable freshness/cutoff. |
| Direct source fetch during render | Breaks the repository data boundary | Preserve `Ingestion -> DB -> Loader -> Service -> UI`. |
