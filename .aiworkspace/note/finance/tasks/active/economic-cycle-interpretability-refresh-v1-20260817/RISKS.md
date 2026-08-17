# Risks

- RTDSM provider downloads remain external I/O and can be slow or unavailable; the UI must fail closed and retain last-good current snapshots.
- Existing legacy intramonth automation is out of the manual official-state path; removing or migrating that scheduled job is not required for this screen task unless tests show it still mutates the official current snapshot.
- Asset `economic_state` continues to use the established pathway interpretation contract. It is presented once and must not be relabeled as the exact RTDSM state evidence.
- Direction colors for rates and spreads can be mistaken for favorable/unfavorable signals; the UI requires a persistent direction-only legend.

