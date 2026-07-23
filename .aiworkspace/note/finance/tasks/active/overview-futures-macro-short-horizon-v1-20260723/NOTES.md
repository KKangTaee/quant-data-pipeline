# Overview Futures Macro Short-Horizon V1 Notes

Last Updated: 2026-07-23

## Confirmed Facts

- Original core futures preset had 16 symbols. `DX-Y.NYB` was later added for Economic Cycle, so current collection has 17.
- Current actual snapshot as of 2026-07-22 reports `standardized_count=17`, `symbol_count=17`, and pattern `available_family_count=6/6`.
- `SCORE_DEFINITIONS` direct member union has 15 symbols. `SI=F` and `DX-Y.NYB` are not family score inputs.
- Current 5D status is `NO_EDGE`: model Brier `0.5582115` versus best unconditional baseline `0.5566554`; coordinate median error `0.7602570` versus baseline `0.7441459`.
- Current actual family state contains a useful contradiction: risk-on 5D is negative and safe-haven 5D is also negative, so a simple defensive headline is incomplete.

## Decisions

- Keep the fast three-step decision flow.
- Show four core directions and two confirmation signals instead of six equal rows.
- Keep internal model/status names; improve user-facing explanation.
- Preserve 20D backend evidence but remove future 20D and 2D path from the default surface.
- Do not alter family membership in this task.
- Separate routine overlap refresh from full bootstrap and add an unchanged-input fast path.

## Visual Approval

- Visual companion session: `.superpowers/brainstorm/53349-1784762573/`
- Final approved mockup: `content/futures-macro-core-confirmation-v4.html`
- Visual artifacts remain generated/untracked and are not part of the spec commit.
