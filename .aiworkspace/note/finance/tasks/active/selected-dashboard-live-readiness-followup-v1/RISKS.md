# Risks

- Deployment readiness language can be mistaken for live approval if the disabled boundary is not explicit.
- If `open_review_items` are only stored but not surfaced, Final Review may look too permissive.
- Candidate search in step 7 may still find no fresh selected row if existing registry evidence lacks hard prerequisites.
- Browser screenshot QA was not captured because the Browser MCP profile was locked. HTTP health and service contracts passed, but visual verification should be repeated when the Browser session is available.
- With zero selected V2 rows, the new Dashboard tabs are covered by service contracts and import/compile checks, but not by an end-to-end selected-row visual smoke in the current registry state.
