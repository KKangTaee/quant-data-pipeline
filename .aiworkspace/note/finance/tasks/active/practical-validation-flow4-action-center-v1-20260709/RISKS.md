# Risks

- Browser QA completed with a generated local screenshot. The screenshot is not staged.
- `npm audit` still reports existing frontend dependency vulnerabilities from the Vite component tree; no forced dependency update was applied because this task only changes UI copy / hierarchy.
- Generated screenshots, run history, and local browser artifacts must remain unstaged.
