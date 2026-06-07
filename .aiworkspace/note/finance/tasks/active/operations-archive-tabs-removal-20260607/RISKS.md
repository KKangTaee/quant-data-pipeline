# Operations Archive Tabs Removal Risks

## Remaining Risks

- Direct hidden archive page reachability is not guaranteed after removal from `st.navigation`; this is acceptable for this slice because the user-facing goal is to remove archive tabs from Operations.
- Archive data / helper code still exists. Actual deletion needs a separate read/write path audit.
- Browser QA confirmed the rendered top navigation, but direct `/operations` navigation emits Streamlit `_stcore` 404 resource messages in browser console. The page renders normally; treat as a QA note unless it becomes user-visible.

## Boundaries Preserved

- No registry / saved JSONL rewrite.
- No run history deletion.
- No live approval, broker order, account sync, or auto rebalance behavior.
