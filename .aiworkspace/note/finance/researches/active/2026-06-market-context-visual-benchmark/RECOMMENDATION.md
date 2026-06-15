# Recommendation

Status: Adopted for Implementation
Last Updated: 2026-06-15

## Short Answer

Cards are not the required answer. For `Overview > Market Context`, the best next decision is choosing one of three directions:

1. `Market Brief Tape`: fastest and safest.
2. `Narrative + Evidence Rail`: best for explanation and user comprehension.
3. `Heatmap + Timeline Board`: most visual, highest implementation and QA cost.

## Recommended Choice

My recommendation is option B, `Narrative + Evidence Rail`, unless the user strongly wants a more terminal-like dense view.

Why:

- It directly addresses the user's complaint that the current screen feels visually unorganized.
- It reduces card nesting while keeping the current summary-first intent.
- It makes "what happened / what changes interpretation / where to verify" easier to read.
- It can reuse existing read models without new data infrastructure.

## Implementation Implication If Chosen

- Keep the top headline.
- Convert `brief_rows` into a compact numbered narrative.
- Move data status / events / sentiment / historical analog / source confidence into a right-side or below-on-mobile evidence rail.
- Keep provenance visible but visually secondary.
- Use color only for status accents, not broad trading-signal encoding.

## Adopted Direction

The user preferred mixing option 1 and option 3 rather than choosing a single pattern. The implemented first pass is:

- Option 1 strength: a 5-cell market tape for `자료 상태`, `Top Mover`, `Breadth`, `Macro`, and `Next Event`.
- Option 3 strength: a sector pressure map plus event timeline immediately below the headline.
- Existing evidence rows and supporting disclosures remain, but they are secondary to the tape/board reading flow.

Implementation task: `.aiworkspace/note/finance/tasks/active/overview-market-context-hybrid-visual-v1-20260615/`.
