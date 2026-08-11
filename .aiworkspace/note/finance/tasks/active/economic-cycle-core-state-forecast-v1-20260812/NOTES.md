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
