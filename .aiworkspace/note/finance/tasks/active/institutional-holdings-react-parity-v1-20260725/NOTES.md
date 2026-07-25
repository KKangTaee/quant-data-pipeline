# Institutional Holdings React Parity V1 Notes

## Implemented Facts

- `Institutional Holdings` normal data surface is already a Streamlit custom React component.
- Healthy React rendering no longer shows a Streamlit title, caption, contextual help, SEC refresh expander or detailed-table fallback around the component. Those remain unavailable-component fallback only.
- Today uses React-owned context / portfolio / action surfaces and keeps only data / event orchestration in Python.
- Market Research uses React-owned header and two-tier navigation while Python owns URL / session normalization and selected-module dispatch.
- `InstitutionalStudioShell.tsx` owns the responsive studio frame and canonical navigation, while mature chart / holdings logic remains in the existing workbench.
- `workbenchState.ts` owns the canonical `overview / holdings / security / popularity` destination list shared by desktop and mobile.
- The React data disclosure owns dataset label/URL/local ZIP/User-Agent inputs and renders the last refresh result.

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
- Final visual direction: `C · Modular Research Studio`.
- Desktop uses a component-local research rail; it is not the app-global Streamlit sidebar.
- Tablet / mobile replace the rail with a React-owned top switcher / drawer sharing the same canonical view and manager state.
- Today / Market Research visual tokens remain the baseline even though the Institutional layout is intentionally more tool-like.

## Implementation Outcome

- Physical split stayed focused: shell/navigation moved to one presentation component and all domain-specific portfolio/security rendering stayed in the existing workbench.
- Refresh fields use the versioned workbench payload and explicit `collect_sec_13f_dataset` event; no new API or DB schema was added.
- Drawer closes before server-rerun events and supports Escape with focus return.
- Reference Center deep-link integration was not added because the existing caveats and SEC source link cover the approved scope; this is not a regression from the prior page.
