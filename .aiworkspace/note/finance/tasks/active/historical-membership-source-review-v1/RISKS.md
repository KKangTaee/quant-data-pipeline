# Historical Membership Source Review V1 Risks

Status: Complete
Created: 2026-05-28

## Risks

- Public current snapshots do not prove historical membership.
- A symbol missing from a current file is not delisting proof.
- Nasdaq Daily List is strong but subscription / approval based, so it does not satisfy the current free-source-first path.
- SEC ticker exchange files help CIK mapping but SEC does not guarantee full accuracy or scope.

## Mitigation

- Store current symbol directory rows only as partial `listing_observed` evidence.
- Keep survivorship PASS criteria unchanged.
- Use SEC as CIK / exchange cross-check, not as complete membership proof.
