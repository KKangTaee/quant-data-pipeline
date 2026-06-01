# Risks

- Existing saved Practical Validation JSONL rows keep their historical gate metadata until re-run or re-saved.
- The preflight should block selected-route handoff, but should not be confused with live/deployment readiness.
- Final Review dynamically checks legacy rows, so no registry rewrite is required. If a legacy row lacks enough compact evidence for preflight computation, it is conservatively hidden from Final Review.
