# Futures Macro Thermometer V1 Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Daily data is missing or shorter than 6 months | Scores can be unstable | Show explicit data sufficiency warning and symbol-level coverage. |
| Free provider symbols can change | Missing components distort scores | Keep missing ticker evidence visible and avoid hiding unavailable members. |
| Futures movements can be delayed or illiquid off-hours | User may over-trust interpretation | Show caution copy in the macro tab. |
| Simple rules can conflict in mixed markets | Summary may overstate one scenario | Show scenario plus score cards and per-ticker standardized moves. |
