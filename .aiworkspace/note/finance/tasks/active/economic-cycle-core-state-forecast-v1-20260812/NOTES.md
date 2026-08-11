# Notes

- current eight-indicator parity is no longer a publication gate because it is
  not the canonical long-history label.
- NBER chronology validates peak/trough/recession semantics but never fabricates
  recovery/expansion/slowdown/contraction labels.
- monthly origins receive episode-normalized weights; they are not counted as
  independent transition events.
- exact calendar-month phase prediction remains out of scope.
- a state change is confirmed only on the second consecutive release with the
  same candidate phase; the first release remains in the prior confirmed state.
- destination labels are unrestricted. For example, contraction to slowdown is
  a valid observed route and is never forced through recovery.
- pressure means confirmation within the next three usable publications. A
  positive label is known at confirmation; a negative label is known only when
  its full publication horizon closes.
- pressure and destination fitting use deterministic NumPy L2 logistic models;
  no new machine-learning dependency or random seed is involved.
- prediction rejects missing/non-finite features, and missing class support
  produces a `LIMITED` artifact rather than a fabricated probability.
- destination output compares all four phases and conditionally sets the
  current phase to zero before renormalizing the next-destination distribution.
- validation scores complete future episode blocks only after 40 prior
  confirmed events and requires every training target to be known strictly
  before the scoring episode begins.
- L2 selection uses only the trailing 20% of prior training episodes, while
  calibration uses only prior OOF predictions. The current scoring episode is
  never used by either procedure.
- pressure baselines are expanding event rate and duration hazard; destination
  baselines are current-phase frequency and the fixed-cycle route.
- actual checkpoint stopped before model fitting, so no actual probability,
  baseline-skill, or calibration claim is available.
- canonical docs changed because research ownership and the Roadmap decision
  changed; product purpose, snapshot/service/UI, DB schema, and asset pathways did not.
