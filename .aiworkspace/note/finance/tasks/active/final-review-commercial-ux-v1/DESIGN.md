# Design

## UX Structure

```text
Final Review
  -> Decision Command Center
  -> Decision Flow Rail
  -> Candidate Board / Review Queue
  -> Decision Cockpit
  -> Final Decision Action
  -> Evidence Drawer
  -> Decision History / Dashboard Handoff
```

## Principles

- Summary before table.
- Decision state before raw evidence.
- Action before appendix.
- Read-only boundary always visible where user might mistake a screen for approval or order.
- Existing validation evidence is reused, not recomputed.

## Component Direction

Create `app/web/backtest_final_review_components.py` with small HTML/CSS render helpers:

- command center
- decision rail
- lane cards
- section headers
- action panel
- alert stack

This keeps `backtest_final_review.py` focused on data and workflow orchestration.

## Visual Tone

- Quiet operational dashboard, not landing page.
- 8px or less radius.
- No decorative gradient/orb background.
- More dense than marketing, but less raw than developer tables.
- Tables remain available in expanders or lower sections.
