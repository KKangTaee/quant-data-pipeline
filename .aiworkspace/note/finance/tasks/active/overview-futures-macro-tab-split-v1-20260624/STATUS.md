# Overview Futures Macro Tab Split V1 Status

## 2026-06-24

- Task opened after user approved the 1차 / 2차 / 3차 sequence.
- RED contract tests added for tab order, slug/display mapping, renderer dispatch, Market Context helper opt-out, light cockpit copy, historical analog removal from default renderer, and latest raw date query shape.
- Production changes implemented:
  - Overview primary tabs now include `Futures Macro` / `선물 매크로`.
  - `Market Context` helper defaults to `include_futures_macro=False` and `include_historical_analog=False`.
  - `Market Context` renderer no longer renders historical analog controls, reading flow, or repair action on the first entry screen.
  - Cockpit service can build a five-card light cockpit without futures macro rows or source confidence.
  - `Futures Macro` tab renders the existing detailed futures macro panel.
  - latest raw date query now uses ordered latest row lookup instead of `MAX(date)`.
- Local timing after split:
  - light Market Context cockpit default after historical analog opt-out: about 0.522s.
  - Market Context cockpit with historical analog opt-in: about 1.491s.
  - full cockpit with futures macro and historical analog: about 7.732s.
  - futures macro snapshot without validation: about 0.209s.
  - futures macro snapshot with validation: about 7.494s.
- Verification complete: `git diff --check`, py_compile, 136 Overview contract tests, timing script, and Browser QA passed.
