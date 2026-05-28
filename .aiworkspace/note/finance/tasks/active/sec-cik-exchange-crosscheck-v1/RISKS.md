# SEC CIK Exchange Crosscheck V1 Risks

Status: Active
Created: 2026-05-28

## Risks

- SEC current association can be over-interpreted as historical listing membership.
- SEC ticker file can lag or differ from exchange current symbol files.
- ETF / stock kind cannot be inferred from SEC file alone.

## Mitigation

- Store rows only as `listing_observed` partial evidence.
- Use existing DB symbol kind map when available; default unknown kind gap remains conservative.
- Keep Data Coverage Audit PASS criteria unchanged.

## Remaining Gaps

- This does not provide old ticker -> new ticker event history.
- Repeated snapshot diff logic is still pending in `computed-snapshot-lifecycle-v1`.
- SEC Submissions former-name / archive scale-up remains a separate future option.
