# Risk-On Momentum 5D Productionization Risks

State: active
Last Updated: 2026-07-26

## Open Risks

| Risk | Required Handling |
|---|---|
| Current Top1000/S&P500 membership is applied to past dates | Preserve explicit current-universe status; add PIT/delisting evidence or fail closed before promotion |
| Hot-path rewrite changes D+1 timing or trade ordering | Add parity tests before implementation and compare full result/trade frames |
| Reduced default random count weakens research evidence | Separate standard from explicit deep mode and record actual iteration count |
| Reused prepared data leaks state between variants | Keep portfolio/RNG/result state outside the immutable prepared object and test repeated independence |
| Generic Practical Validation misreads daily swing | Add a distinct Daily Swing module and horizon-specific evidence |
| Raw artifact path is mistaken for durable evidence | Store compact metadata/counts only; raw rows remain generated |
| Production label enables an unsafe CTA | Change maturity only after Level2/Final Review policy tests pass |
| Monitoring is mistaken for trading automation | Keep manual review, stale expiry and no-order boundaries visible and tested |
| 60-second target is not reached by indexed optimization | Measure after each root-cause fix; discuss a deeper vectorized rewrite before expanding scope |

## Blocker Policy

Missing historical membership/delisting data does not block 1차 runtime optimization.
It blocks an unqualified production promotion if the product cannot distinguish
current-universe historical research from PIT-backed evidence.
