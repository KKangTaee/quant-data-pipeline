# Notes

- This task improves validation effectiveness by surfacing missing DB/latest market/replay contract evidence before recheck execution.
- It should not add user memo, preset, monitoring log, or automatic JSONL persistence.
- Readiness checks global latest market date and replay contract shape. Symbol-level per-ticker freshness remains a later deeper DB evidence task.
