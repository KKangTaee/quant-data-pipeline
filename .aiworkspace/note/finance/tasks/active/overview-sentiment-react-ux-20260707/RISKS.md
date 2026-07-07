# Overview Sentiment React UX Risks

- In-app Browser iframe click automation may be less reliable than visual screenshot QA; Python event parsing should be covered by tests.
- Existing worktree contains unrelated generated artifacts and `.DS_Store`; stage review is required before every commit.
- AAII/CNN collection can be blocked by source-side behavior; UI must represent missing/partial data without fabricating values.
- Evidence tables can be tall when history rows grow; React constrains table height with internal scroll, but very large future history windows may need pagination if the payload grows materially.
