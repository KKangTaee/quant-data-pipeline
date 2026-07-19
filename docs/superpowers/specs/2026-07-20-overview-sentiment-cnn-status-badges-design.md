# Overview Sentiment CNN Component Status Badges Design

Date: 2026-07-20
Status: User-approved visual direction; pending written-spec review

## Why This Change

The expanded `CNN 구성요소` evidence list currently renders every score and rating with the same visual treatment. Users must read each rating word to distinguish `극단적 공포`, `공포`, `중립`, and `탐욕`, which makes a seven-row evidence list slower to scan.

This change makes the server-owned CNN state immediately distinguishable without turning the full evidence list into a multi-colored dashboard.

## Approved Direction

Use the user-selected **A. 상태 배지형** treatment.

- Keep the component name, explanation, numeric score, current reading, and change text unchanged.
- Keep the numeric score in the existing neutral foreground color.
- Render only the rating text as a compact rounded status badge.
- Do not tint the full row and do not wrap the score and rating in a larger metric card.
- Apply the treatment only to CNN component evidence. The AAII comparison panel remains unchanged.

## Status Palette

The React view consumes the existing service-owned `tone` field; it does not recompute CNN thresholds.

| Service tone | User-visible state | Badge treatment |
|---|---|---|
| `danger` | 극단적 공포 | berry red text, pale berry background, berry border |
| `warning` | 공포 | warm amber text, pale amber background, amber border |
| `neutral` | 중립 or unavailable fallback | slate text, pale slate background, slate border |
| `positive` | 탐욕 or 극단적 탐욕 | teal text, pale teal background, teal border |

The badge always retains its rating text, so color is a secondary cue rather than the only state signal. `탐욕` and `극단적 탐욕` use the same positive color family while their text keeps the severity distinction.

## Component And Data Flow

1. `app/services/overview/sentiment.py` remains the owner of score thresholds, direction, rating label, and `tone`.
2. The existing `evidence.cnn_components` payload continues to provide each item's `rating` and `tone`.
3. `SentimentEvidenceDisclosure.tsx` adds the tone as a stable badge styling hook and renders the existing rating text inside the badge.
4. `style.css` owns badge sizing, contrast, border, and tone-specific colors.

No DB, ingestion, loader, refresh action, payload version, or AAII behavior changes are required.

## Fallback And Accessibility

- Missing or unknown `tone` values use the neutral badge treatment.
- Missing rating text uses the existing neutral placeholder rather than an empty colored shape.
- Badge foreground/background combinations must remain readable at the current compact evidence font size.
- The full state word remains visible; no meaning is encoded by color alone.
- The badge may wrap only when necessary on narrow screens and must not cause horizontal overflow.

## Responsive Behavior

- Desktop keeps the current two-column evidence layout and right-aligned score area.
- Mobile keeps the existing single-column evidence layout.
- The score and badge stay grouped in the right-hand metric area.
- The badge must not expand the row height materially beyond the current compact evidence row.

## Testing And QA

- Add a source-contract regression that requires a tone styling hook on CNN badges and all four tone styles in CSS.
- Verify the test fails before implementation and passes after implementation.
- Rebuild the sentiment React production bundle.
- Run the focused sentiment service/frontend regression suite.
- Perform actual Browser QA with the detail disclosure open on desktop and a narrow mobile viewport.
- Confirm at least `극단적 공포`, `공포`, `중립`, and `탐욕` are visually distinguishable, rating text remains present, AAII is unchanged, and there is no horizontal overflow.

## Acceptance Criteria

- A user can distinguish extreme fear, fear, neutral, and greed rows without reading every explanatory sentence.
- The numeric score remains visually neutral and comparable across rows.
- CNN classification thresholds are not duplicated in React.
- Unknown states remain readable and neutral.
- AAII rendering and all existing chart, tooltip, and disclosure behavior remain unchanged.

## Out Of Scope

- Full-row background tinting
- Larger score cards inside each evidence row
- Changes to CNN or AAII classification rules
- Changes to Hero, current evidence cards, charts, outlook cards, or raw evidence tables
- New market-sentiment data sources
