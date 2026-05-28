# Decision Dossier Report V1 Notes

Status: Active
Created: 2026-05-28

## Findings

- Final Review saved rows already store compact decision evidence, investability packet, gate policy snapshot, selected components, paper observation, and operator decision.
- Selected Dashboard now has a read-only monitoring timeline, but that signal is session-state evidence and should not become a report registry write.
- `app/services/backtest_evidence_read_model.py` is the correct shared boundary because Final Review and Selected Dashboard already use it for evidence rows.

## Implementation Notes

- Dossier markdown is generated in memory and exposed through `st.download_button`; no report file is written automatically.
- Final Review dossier uses the saved final decision row only.
- Selected Dashboard dossier passes the current session-state monitoring timeline into the same service read model.
- `execution_boundary` repeats `read_only_dossier`, `report_auto_write=False`, `monitoring_log_auto_write=False`, `live_approval=False`, `order_instruction=False`, and `auto_rebalance=False`.
