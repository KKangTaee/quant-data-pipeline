# Risks

## Watch

- Do not hide genuinely missing / failed data.
- Do not treat closed-session stale intraday age as a successful real-time update.
- Do not duplicate or fork the NYSE session calendar logic more than necessary.
- Keep the top Market Context brief context-only; no trading / recommendation semantics.

## Residual

- Closed-session suppression is intentionally narrow: stale / due intraday age is lowered, but failed / missing sources can still become actionable refresh items.
- Event and source confidence caveats remain visible in evidence sections; they are not converted into market conclusions.
