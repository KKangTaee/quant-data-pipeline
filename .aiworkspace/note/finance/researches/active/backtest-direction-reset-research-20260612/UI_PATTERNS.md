# UI And Workflow Patterns

Status: Active
Last Updated: 2026-06-12 KST

## Summary

The reset direction is `execution-first, evidence-handoff second`.

Backtest Analysis should help the user answer:

- Can I run this strategy or mix?
- Can I compare it with alternatives?
- Can I reproduce the setup later through history or saved replay?
- Is this result eligible to become a Practical Validation source?

It should not try to answer every provider, governance, final decision, or monitoring question on the same first screen.

## Pattern Catalog

### Pattern 1. Task-First Backtest Entry

- Seen in: Portfolio Visualizer, QuantConnect, current 4C Backtest Analysis.
- User problem: The user wants to run or compare strategies before reading governance context.
- Interaction shape: Single Strategy / Portfolio Mix Builder visible first; reference controls live below or in Reference.
- Data required: strategy catalog, form defaults, latest result bundle, compare result, saved replay context.
- Why it matters: This keeps Backtest Analysis from becoming an operations console.
- Fit for this project: Very high. 4C already implemented the first version.
- Risks: If hidden references are still too numerous, future work may quietly rebuild the heavy panel problem.

### Pattern 2. Four-Object Handoff

- Seen in: QuantConnect result/history/report split, IBKR report workflow, Koyfin model portfolio snapshots.
- User problem: Users confuse successful run, saved setup, validation evidence, and monitoring state.
- Interaction shape: Show four labels consistently:
  - `Run Result`: output from this execution.
  - `Replayable Setup`: history/saved configuration can reproduce the run.
  - `Validation Source`: candidate is ready to enter Practical Validation.
  - `Monitoring Record`: selected-route candidate is being observed after Final Review.
- Data required: result bundle metadata, history payload, saved portfolio record, Practical Validation source traits, Final Review decision id.
- Why it matters: It prevents "saved" from meaning "validated" and "high CAGR" from meaning "approved."
- Fit for this project: High. The underlying storage boundaries already exist.
- Risks: Requires careful copy and compact badges, not a large new panel.

### Pattern 3. Maturity Badge With Gate Reason

- Seen in: Portfolio123 robustness framing, QuantConnect OOS holdout, existing strategy evidence inventory.
- User problem: Strategy execution support is mistaken for candidate readiness.
- Interaction shape: Each strategy or result gets one compact maturity label plus one gate reason.
- Suggested labels:
  - `Candidate-ready source`
  - `Runtime-hardened / evidence needed`
  - `Research lane`
  - `Prototype`
  - `Legacy / compatibility`
- Data required: strategy key, replay support, current anchor, validation readiness, monitoring policy.
- Why it matters: This is the strategy maturity model without reopening the 3A panel sprawl.
- Fit for this project: High.
- Risks: If labels become too many or too visible, it can again distract from running strategies.

### Pattern 4. Validation Handoff Strip

- Seen in: QuantConnect OOS policy as gate, Portfolio123 robustness/stress-testing guidance.
- User problem: User needs to know what makes a result eligible for Practical Validation.
- Interaction shape: A small post-result strip says:
  - replay contract status
  - data trust / warning count
  - maturity label
  - next allowed action
  - missing gate reason
- Data required: result bundle meta, warnings, strategy maturity row, history/saved replay parity.
- Why it matters: It creates a handoff without adding a new evidence workbench.
- Fit for this project: Very high as a 1차 candidate.
- Risks: Must not run validation, write registry rows, or imply Final Review approval.

### Pattern 5. Research Lane Isolation

- Seen in: QuantConnect Research Environment vs backtest result page; current Risk-On governance board.
- User problem: Daily swing research has useful diagnostics but a different cadence and artifact model.
- Interaction shape: Keep Risk-On Momentum 5D as a named research lane with generated artifact caveats, not a standard candidate lane.
- Data required: Risk-On result bundle, trade/scanner artifact references, macro mode, universe assumptions, survivorship notes.
- Why it matters: It avoids forcing daily signals into monthly/annual validation gates.
- Fit for this project: High.
- Risks: Users may want to promote it because it has rich evidence. Gate must be stricter, not looser.

### Pattern 6. ETF Evidence Caveat Row

- Seen in: Koyfin ETF holdings/contribution caveat.
- User problem: ETF holdings/exposure evidence can look more historically complete than it is.
- Interaction shape: Any ETF provider/holdings/exposure evidence should show source freshness, historical constituent limitation, missing delisting/acquisition caveat, and compact coverage.
- Data required: provider snapshot freshness, holdings/exposure source type, coverage count, historical constituent availability.
- Why it matters: ETF strategy maturity should not be inflated by partial provider evidence.
- Fit for this project: High for Practical Validation and ETF evidence expansion.
- Risks: Belongs downstream; do not direct-fetch provider data in Backtest Analysis.

### Pattern 7. Monitoring Summary First, Drilldown Later

- Seen in: Koyfin model portfolio summary/drift, IBKR PortfolioAnalyst reports.
- User problem: Operations should answer "what needs attention?" before showing every evidence table.
- Interaction shape: Portfolio Monitoring hero/status summary, then selected strategy detail and reports.
- Data required: selected decision rows, scenario freshness, evidence readiness, open review issues.
- Why it matters: Prevents post-selection monitoring from turning back into strategy research.
- Fit for this project: Already aligned with current Operations direction.
- Risks: Future Backtest changes should not pull monitoring details back into Backtest Analysis.

## Patterns That Conflict With Current Boundaries

| Pattern | Conflict | Handling |
| --- | --- | --- |
| Broker-adjacent consolidated portfolio analytics | Could imply account sync, real holdings, or orders. | Keep as inspiration for reports/monitoring only. No broker order, account sync, auto rebalance. |
| End-to-end build/backtest/execute products | Could make live execution seem like the natural next step. | Treat live execution as out of boundary. Current product ends at decision support and read-only monitoring. |
| Strategy marketplace or community strategy browsing | Could distract from evidence maturity and local data correctness. | Parking lot only. |
| Heavy research notebook diagnostics | Could recreate Backtest Analysis panel overload. | Keep notebooks/reports/reference separate from the default run screen. |
| ETF holdings contribution visuals | Can overstate historical holdings accuracy. | Always show caveats and source/freshness limits. |

## Patterns That Should Remain Internal / Ops Only

| Pattern | Why Internal |
| --- | --- |
| Raw provider response inspection | Full provider payload belongs in DB/ops, not compact product flow. |
| Run history JSONL surgery | Generated/local artifact maintenance, not user-facing product work. |
| Registry repair / migration tools | Admin/task work only. |
| Direct FRED/provider fetch controls from Backtest Analysis | Violates Ingestion -> DB -> Loader -> UI boundary. |
| Full daily swing trade/scanner artifact browsing | Generated artifact detail; only compact evidence should enter validation later. |

## Candidate Questions For Feature Opportunity

- Can 1차 be a compact handoff/maturity contract without adding a panel?
- Should 2차 move existing 3A~4B references toward Reference / report surfaces instead of keeping them inside Backtest Analysis?
- Which ETF strategy gets the first evidence-expansion pass: GRS because 5A hardened it, or Risk Parity / Dual Momentum because 5B just improved their contracts?
- What exact evidence lets a quarterly prototype lose the prototype label?
- What compact evidence from Risk-On Momentum can enter Practical Validation without making it a daily trading signal?
