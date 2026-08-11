# Risks

- NBER is a binary recession chronology, not direct four-phase ground truth.
- 117 transition events may still be insufficient for out-of-sample baseline
  superiority after episode blocking.
- current eight-indicator disagreement must remain visible rather than being
  silently overridden.
- a core-state pass does not imply either forecast model will pass.
- UI work before the combined gate would repeat the earlier development error.
- Actual core state failed only the pre-registered raw stability gate: 48 of 177
  raw episodes were one month (27.12% versus 25%). Lowering the threshold after
  observing this result would invalidate the checkpoint.
- Model code and synthetic chronological tests are implemented, but no actual
  probability quality claim exists because the core gate correctly stopped the
  DB experiment before fitting.
