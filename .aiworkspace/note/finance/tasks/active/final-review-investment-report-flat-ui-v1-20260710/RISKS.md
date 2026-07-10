# Risks

## 2026-07-10

- Browser QA is required because this is primarily a visual hierarchy change.
- Build assets under `frontend/build/` are ignored by `.gitignore`; changed hashed assets must be staged explicitly.
- Existing generated screenshots and run history must remain unstaged.
- QA screenshot is generated and left untracked; do not stage it unless the user explicitly requests artifact commit.
- The current improvement is layout / readability only. It does not add new evidence, new score logic, or automated improvement portfolio generation.
- Browser QA covered the existing sample candidate at desktop width. Mobile responsive behavior is protected by CSS source review and contract scope but not separately screenshotted in this pass.
