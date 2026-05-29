# Risks

- Historical validation rows may only have legacy provider `diagnostic_status=PASS` without provenance. They should not be over-promoted.
- DB bridge / price-derived proxy can be useful but is weaker than official provider evidence for investability decisions.
- This task does not estimate market impact for a specific order size; that remains a later sensitivity / execution model task.
- Some older saved validation results may route to REVIEW until they are rerun with provider context schema v2 evidence.
