# Risks

## 2026-06-10

- The manual bundle can still take time or return provider-level partial failures; this task only makes those outcomes visible.
- No retry/action queue is added in this step.
- Automatic refresh policy, scheduler hardening, and action queue persistence remain 4차/후속 scope.
- Streamlit dataframe may still horizontally constrain long provider messages; row action copy was shortened, but raw provider messages stay visible as returned.
