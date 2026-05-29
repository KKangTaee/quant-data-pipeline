# Concentration / Overlap / Exposure Contract V1 Notes

Status: Complete
Created: 2026-05-29

## Notes

- Existing `provider_coverage.look_through_board` already contains the compact fields needed for V1.
- This task should not add DB collectors because provider context already reads DB loader output.
- The contract must distinguish `provider_backed`, `partial_provider`, `proxy_only`, and `missing_provider` source strength.
- 11-2 intentionally does not add selected-route gate enforcement. That remains 11-5 scope.
- Full holdings and raw provider rows remain in DB / provider context; the audit stores compact rows only.
