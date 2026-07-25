# Institutional Holdings React Parity V1 Notes

## Implemented Facts

- `Institutional Holdings` normal data surface is already a Streamlit custom React component.
- Streamlit still renders visible title, caption, contextual help, SEC refresh and detailed table fallback around the React component.
- Today uses React-owned context / portfolio / action surfaces and keeps only data / event orchestration in Python.
- Market Research uses React-owned header and two-tier navigation while Python owns URL / session normalization and selected-module dispatch.
- Institutional workbench source is currently 1,747 TSX lines and 2,102 CSS lines.

## Actual Render Findings

- Desktop normal render showed the Streamlit page title / caption / help disclosure before the React manager context.
- 420px render placed the first React manager context at roughly 400px from the top; Today began its first product card around 150px and Market Research began its product navigation / header around 100px.
- Current institutional surfaces use 8px panels, saturated cobalt selection, black segmented primary tabs and red secondary underline.
- Today / Market Research use larger rounded blue-gray surfaces, restrained shadows, muted semantic accents and clearer primary / secondary navigation grammar.
- Institutional browser console had no error / warning during the diagnosis.

## Decisions

- Reuse current platform pattern; do not invent a standalone frontend stack for one tab.
- React owns every normal-path visible product surface.
- Streamlit remains the thin adapter and unavailable fallback.
- No periodic fragment is added because Holdings is explicit-event driven.
- Preserve all existing portfolio / security research capabilities.
- Move refresh / help / caveat presentation into React instead of deleting them.
- Do not create an operational diagnostics panel.

## Open Detail For Implementation Planning

- Final physical file split should balance component ownership with avoiding excessive tiny files.
- Existing refresh input / result fields must be mapped into a versioned React event / payload contract.
- Contextual Reference handoff can reuse the current page-target mechanism through an `open_reference` event.
