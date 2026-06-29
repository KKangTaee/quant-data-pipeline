# Overview Nav Internal Lazy Load V1 Design

## Navigation

Use `st.pills` with `selection_mode="single"` and `required=True`.
The internal option values stay English labels so existing renderer dispatch remains stable.
`format_func` renders Korean-first labels such as `시장 맥락 · Market Context`.
CSS is scoped to the Overview selector area and no `<a href>` anchors are rendered.

The visual style follows the user-provided underline tab reference:

- inactive tabs are plain text with no pill/card fill.
- the selector row owns one thin bottom border.
- the active tab uses red text plus a red underline.
- Streamlit's internal widget owns the state change, so switching tabs stays inside the current browser tab.

## Initial Loading

On a fresh Overview visit, the shell renders title, caption, session banner, and primary nav first.
If the active tab is the default `Market Context` and it has not been explicitly loaded in this session, show a small action panel with a `시장 맥락 불러오기` button.
Clicking the button marks the tab loaded and renders the existing Market Context body.
Selecting non-default tabs renders their tab body immediately because the selection itself is an explicit action.

## Loading Cause

`load_overview_macro_context_cockpit` currently fans out into market movers, sector leadership, futures macro, sentiment, events, collection ops, and historical analog before rendering Market Context.
The lazy gate avoids this fan-out during the first browser load.
