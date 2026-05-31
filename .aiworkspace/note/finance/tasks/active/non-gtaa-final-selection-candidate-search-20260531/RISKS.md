# Risks

- Current selected-route policy may block many otherwise good candidates because provider / realism / risk contribution evidence must be complete, not merely good enough.
- Single-strategy candidates may fail risk contribution by design if the audit expects component-level contribution evidence.
- Factor snapshot strategies may be unsupported by Practical Validation replay if replay mapping only covers ETF strategy keys.
- The legacy non-GTAA Quality selected row can provide the redesign seed, but migrating it into V2 must be labeled as a legacy migration. It should not be represented as a fresh candidate that passed the current stricter selected-route gate.
- Fixing the current-gate blockers likely requires evidence model work, not only more strategy search: preserve weighted component rationales, add aggregate cost / turnover / sensitivity evidence, improve provider look-through and validation robustness evidence, then rerun selection.
