# Risks

- Legacy source rows will not have selection history unless replayed or resent through the new handoff path.
- Weighted mix portfolio-level exact look-through is component-level in V1; component histories are shown separately rather than merged into a single full holdings table.
- Selection history quality depends on the strategy result frame exposing ticker / weight columns. Strategies that only return aggregate equity curves will still show performance context but not monthly holdings.
