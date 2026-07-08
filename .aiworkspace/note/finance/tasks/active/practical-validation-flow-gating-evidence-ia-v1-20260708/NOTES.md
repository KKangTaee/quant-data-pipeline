# Practical Validation Flow Gating / Evidence IA V1 Notes

## Initial Findings

- `render_practical_validation_workspace` currently builds `validation_result` after Flow 2 and renders Flow 3 / Flow 4 / Flow 5 unconditionally.
- Data collection can resolve only part of Data Coverage / Conditional Evidence gaps: provider snapshot, holdings / exposure, macro context, and DB price window. Replay, method strength, component role / weight, and Final Review judgment should not get a collection button.
- Existing lower evidence tabs duplicate Flow 4 criteria detail and should become a supporting evidence appendix rather than the primary reading path.
