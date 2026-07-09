# Risks

- Final Review policy still uses PV audits for selected-route gating. This task should clarify surface ownership without changing gate engine behavior unless tests require a narrow read-model adjustment.
- Browser QA used a fresh local server on port 8517 because older 8501 / 8505 servers were started with file watcher disabled and showed stale UI copy.
- The historical roadmap still contains older completed tasks that say REVIEW-only groups were hidden; the current-state top entry now supersedes that policy rather than rewriting history.
