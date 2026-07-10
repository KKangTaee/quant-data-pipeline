# Notes

## 2026-07-10

- User-visible problem: nested boxes and repeated card grids make the report hard to scan.
- Product direction: first-read should answer `선정 가능한가`, `왜 후보인가`, `무엇을 확인해야 하나`; lower sections should support audit/detail only.
- Benchmark translation: take scan-first grouping and simple language principles from Upbit / Toss-style investment surfaces, but do not add trading, broker, order, or live approval behavior.
- React now owns only visual priority: candidate meta strip, two-column `왜 후보인가` / `무엇을 확인해야 하나`, capped strength / watch rows, interpretation rows, and detail disclosures.
- Python still owns all read-model values and semantics: scorecard, score cap, Level2 REVIEW disposition, route decision, save guidance, Monitoring handoff, and compatibility selection rationale / required notes.
- First-read old card-grid classes are intentionally blocked by source contract so future changes do not drift back into nested dashboard layout.
