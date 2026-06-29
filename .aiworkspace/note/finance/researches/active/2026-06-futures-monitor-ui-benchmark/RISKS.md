# Risks

Status: Draft
Last Updated: 2026-06-23

## Research Risks

- Toss Securities evidence is partly company-authored and may emphasize positioning over actual day-to-day UI friction.
- Some benchmark sources are product marketing pages rather than live UI inspection.
- Professional trading tools include order/trading features that must not be copied into this project.

## Design Risks

- A Streamlit-only implementation may still feel less polished than the benchmark references.
- Watch rail replacement can make symbol editing less obvious if not paired with a clear edit affordance.
- A market brief hero can accidentally sound like recommendation; wording must stay context-only.
- Too much hiding of raw evidence can reduce trust; evidence disclosures must remain easy to find.

## Implementation Risks

- CSS-heavy layout may become fragile across Streamlit versions.
- Responsive layout must be checked because current controls already consume substantial width.
- Chart annotations may require more work than a first Streamlit slice deserves.

