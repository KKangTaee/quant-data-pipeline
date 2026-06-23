# Futures Monitor Workbench V1.1 Risks

- Streamlit native controls can still look utilitarian; CSS and layout must keep the module compact without adding decorative nested cards.
- Current-state wording must not imply trade signal or recommendation.
- Validation summary must explain hit-rate limits for mixed scenarios so users do not read it as a directional forecast.
- Existing local generated artifacts must remain unstaged.

## Closeout

- No known functional blocker remains inside the approved V1.1 scope.
- Streamlit native select/segmented controls are still visually native. A future non-Streamlit / custom component watch rail would be a separate interaction rewrite, not part of V1.1.
- The local DB sample used for Browser QA had stale 1분봉 candles, so the module correctly showed `갱신 필요`; this is data state, not a UI failure.
