# Structured Waiver Policy V1 Risks

Status: Active
Created: 2026-05-28

## Risks

- Waiver can turn missing evidence into an apparent pass.
- Waiver can become another free-form memo storage surface.
- Waiver can make `실전 검토 통과 후보` sound closer to investment approval.

## Mitigation

- Do not allow waiver for `BLOCK`.
- If implemented later, allow only selected `REVIEW_REQUIRED` gaps with explicit expiry / review trigger.
- Keep waiver as compact decision evidence, not a separate user memo registry.

## Closeout Notes

- No code, UI, schema, or persistence behavior changed.
- The policy intentionally raises the bar before any waiver implementation exists.
