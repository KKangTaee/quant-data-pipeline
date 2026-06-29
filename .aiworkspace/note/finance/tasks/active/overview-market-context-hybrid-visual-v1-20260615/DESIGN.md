# Overview Market Context Hybrid Visual V1 Design

Status: Active
Created: 2026-06-15

## Selected Direction

Use an A+C hybrid:

```text
Headline
-> tape: data / mover / breadth / macro / event
-> visual board: sector pressure map + event timeline
-> evidence rows: movement / breadth / macro / interpretation cues
-> supporting disclosures: historical analog, source confidence, boundary
```

## UX Intent

- Tape answers: "what should I know in 10 seconds?"
- Sector pressure map answers: "is the move broad, concentrated, or mixed?"
- Event timeline answers: "what near event can change interpretation?"
- Evidence rows answer: "where did this come from and which deep tab should I open?"

## Boundaries

The heatmap is context-only. Color encodes stored market pressure, not buy/sell signals. It must not create Practical Validation PASS/BLOCKER, Final Review decision, monitoring signal, order, auto rebalance, registry write, saved setup write, provider fetch, or DB schema change.
