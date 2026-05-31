# Structured Waiver Policy

Status: Active
Last Verified: 2026-05-28

## Purpose

이 문서는 Final Review selected-route gate에서 waiver를 허용할지 판단하는 정책이다.

현재 구현은 waiver를 지원하지 않는다.
`app/services/backtest_evidence_read_model.py`의 gate policy는 `waiver_supported=False`를 유지한다.

이 문서는 future implementation이 필요할 때 지켜야 할 조건을 정의한다.

## Decision

V1 policy decision:

- `BLOCK` severity는 waiver 불가.
- `REVIEW_REQUIRED` severity는 future task에서만 제한적으로 waiver 가능.
- `WATCH`는 waiver가 필요하지 않은 관찰 상태다.
- waiver는 pass가 아니다. waived evidence는 계속 gap으로 표시한다.
- waiver는 live approval, broker order, auto rebalance가 아니다.

## Severity Policy

| Severity | Selected Route | Waiver Policy | Examples |
|---|---|---|---|
| `BLOCK` | Blocked | Not waiverable | hard blocker, missing core price, malformed source, invalid weights, critical `NOT_RUN`, missing leveraged / inverse objective |
| `REVIEW_REQUIRED` | Hold / re-review by default | Future limited waiver possible | stale but usable provider snapshot, partial holdings coverage, paper observation gap with explicit monitoring trigger |
| `WATCH` | Allowed | No waiver needed | non-critical limitation that should stay visible |
| `PASS` | Allowed | No waiver needed | evidence sufficient for the profile |

## Minimum Structured Fields

If waiver is implemented later, it must use structured fields.

Required fields:

| Field | Meaning |
|---|---|
| `waiver_id` | Stable id for this waiver snapshot |
| `policy_group` | Gate policy group being waived |
| `severity` | Must be `REVIEW_REQUIRED`; `BLOCK` is not accepted |
| `gap` | Compact original blocker / review-required text |
| `reason_code` | Controlled reason category, not arbitrary memo |
| `reason_detail` | Short bounded explanation |
| `expires_at` or `review_by` | Date when waiver must be revisited |
| `review_trigger` | Concrete trigger that forces re-review |
| `scope` | Candidate / component / decision scope |
| `acknowledged_limits` | Explicit list of known limitations |
| `created_at` | Waiver creation time |
| `operator` | Human / process identifier if available |

Forbidden:

- open-ended free-form memo
- indefinite waiver with no expiry or review date
- waiver that changes `NOT_RUN` to `PASS`
- waiver that creates order / approval / rebalance behavior

## Storage Boundary

V1 does not add persistence.

If implemented later:

- Prefer compact `structured_waiver_snapshot` inside the Final Review decision row.
- Do not create a new waiver JSONL registry by default.
- Do not write waiver automatically when the user opens Final Review.
- Keep full provider / holdings / macro evidence in DB or existing validation evidence.
- Use `docs/data/STORAGE_GOVERNANCE.md` before adding any new persistence path.

## UI Boundary

Default UI behavior remains:

- If gate outcome is `blocked`, selected route is blocked.
- If gate outcome is `hold_or_re_review`, selected route is not the default.
- User can still record hold / reject / re-review decisions.

If waiver UI is implemented later:

- Put it behind an explicit advanced section.
- Show the original gap and severity next to the waiver controls.
- Require expiry / review trigger before enabling selected route.
- Keep the final copy as `실전 검토 통과 후보`, not approval.

## Implementation Status

Current implementation status:

- `waiver_supported=False`
- no waiver UI
- no waiver persistence
- critical gaps continue to block selected route
