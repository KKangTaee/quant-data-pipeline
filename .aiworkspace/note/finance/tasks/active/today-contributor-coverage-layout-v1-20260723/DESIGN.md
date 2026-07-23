# Today Contributor Coverage / Review Layout V1 Design

Status: User-approved
Last Updated: 2026-07-23

## Confirmed Root Cause

Actual default portfolio has five active direct holdings with computable cumulative contributions:

| Symbol | Contribution |
|---|---:|
| AMD | +$12,136.60 |
| TEM | -$462.00 |
| RKLB | -$440.00 |
| SOXX | -$265.08 |
| QQQ | -$146.31 |

`app/services/today.py::_project_portfolio` currently selects positive top 2 and negative bottom 2 separately. Only AMD is positive, so the final `positives + negatives` array contains AMD, TEM, and RKLB. SOXX and QQQ are valid but omitted by the display policy.

The right panel stretches to the left panel height. Its nested CSS grid uses the default stretch alignment, distributing three review rows over the remaining height and creating the abnormal vertical gaps shown in the user screenshot.

## Considered Approaches

1. Show every computable contributor as the existing cards, ordered by absolute impact.
2. Keep four cards and add a local `전체 보기` expansion.
3. Replace cards with a compact table.

The user approved approach 1. It removes unexplained omission without introducing a hidden interaction or replacing the established card visual language.

## Data Contract

- Preserve every `contribution_by_item` entry whose value is numeric, including zero.
- Join the contribution to its item symbol and cumulative item return exactly as today.
- Sort by descending absolute contribution value; break equal absolute values by symbol for deterministic output.
- Tone is `positive`, `negative`, or `neutral` for positive, negative, or zero contributions.
- Missing/non-numeric contribution entries remain unavailable rather than being fabricated as zero. The UI explains this through coverage text derived from `contributors.length / active_item_count`.
- The payload shape remains compatible and `today_home_v4` / `today_portfolio_island_v1` schema versions do not change. The contributor array becomes more complete but retains the same field purposes.
- Live overlay uses the same ordering and neutral-tone rule so an OPEN refresh does not reorder cards by a different policy.

## UI Contract

- Contributor header copy:
  - all active items computable: `전체 N개 · 영향 큰 순`
  - partial computation: `기여 계산 N/M개 · 영향 큰 순`
  - no active items: existing empty-state copy
- Keep two-column contributor cards on desktop and one column at the existing phone breakpoint.
- Continue showing item cumulative return and portfolio cumulative contribution as distinct values.
- Add a `today-review-section` class. Its content aligns to the top, and the review list uses max-content rows with a consistent 8px gap and zero paragraph margin.
- Keep the two outer detail panels equal height on desktop; only the internal review text distribution changes.

## Error And Edge Handling

- A computable zero contribution renders `$0` with neutral text color.
- If fewer contribution rows exist than active items, the header reports coverage instead of implying a complete list.
- If a live partial overlay supplies a smaller contributor set, the same coverage label makes the limitation explicit.
- No provider call, DB write, or navigation event is added.

## Test Contract

### Python

- A five-item fixture proves that all five numeric contribution rows survive projection.
- Output order is absolute contribution descending with deterministic symbol tie-break.
- Zero is retained and uses neutral tone.

### React

- Full coverage renders `전체 5개 · 영향 큰 순` and all symbols.
- Partial coverage renders `기여 계산 3/5개 · 영향 큰 순`.
- Review markup uses the dedicated section class.
- CSS contract prevents stretched review rows and preserves phone single-column contributors.

### Browser

- Actual default portfolio shows all five symbols.
- Review rows stay top-aligned with even spacing.
- 1280, 760, and 420px have zero horizontal overflow and no console errors.

## Tradeoff

The contributor panel can grow to five rows for the current maximum ten active items. This is accepted because Today already supports up to ten tracked items, all items remain directly visible, and the user explicitly preferred completeness over a collapsed list.
