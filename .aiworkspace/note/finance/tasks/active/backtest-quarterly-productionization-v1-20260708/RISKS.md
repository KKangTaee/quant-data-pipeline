# Risks

- Quarterly promotion can overstate data reliability if statement shadow coverage remains sparse or filing timing is not enforced; mitigated by post-run Factor Readiness, but still a product interpretation risk.
- Legacy saved/history rows may still use `_prototype` strategy keys; compatibility is intentionally preserved by keeping strategy keys and only changing user-facing labels.
- Provider no-data symbols must not keep showing repair buttons that cannot resolve the issue.
- Existing untracked QA artifacts in the worktree must not be staged accidentally.
