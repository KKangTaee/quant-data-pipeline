# Risks

- If local historical analog coverage is insufficient, the reference section may still show a `자료 부족` state. The V3 change should make this quieter, not hide it.
- Existing `interpretation_cues` key can be retained for compatibility while changing labels / title semantics.
- No open implementation blocker remains for V3.
- Future work should only add drill-in / interaction if the user asks for a deeper read path; V3 intentionally avoids prediction, trading signal, provider/schema work, and job-result diagnostics.
