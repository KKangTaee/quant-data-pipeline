# Overview Market Context Events Data Trust V1 Risks

## Open Risks

- Local DB still has no stored `MACRO_CPI` rows for `2026-06-10` or `2026-07-14`. The read model is ready to surface CPI, but Macro Calendar collection or BLS `.ics` import must populate the rows.
- Actual BLS/BEA/Fed/Yahoo network collection may be blocked or partially unavailable in this environment. Parser fixture tests verify local behavior, but provider reachability remains a runtime risk.
- The requested pytest command cannot run until `pytest` is installed in the local environment; focused `unittest` coverage passed instead.
- Similar-regime / prediction work is explicitly deferred to 4차 and should not be mixed into this event trust task.
