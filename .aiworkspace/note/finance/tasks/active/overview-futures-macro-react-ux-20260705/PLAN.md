# Overview Futures Macro React UX Plan

## Why

`Workspace > Overview > Futures Macro` currently loads heavy historical validation when the tab is opened. Local smoke timing showed the current macro snapshot without validation loads in about 0.2s, while validation-enabled loading takes about 7.6s. React migration should not start before this calculation boundary is split.

## Roadmap

1. Fast entry: load current futures macro snapshot without historical validation, and compute validation only on explicit user action.
2. React MVP: move the main Futures Macro brief, flow, scores, evidence, and actions into a dedicated React custom component.
3. Flow horizon: extend recent flow from 5D-only to 5D / 20D context.
4. Macro subtype: make mixed macro states more specific without pretending they are directional trading signals.
5. Validation persistence: decide whether historical validation should be session-only, process-cached, or materialized after daily refresh.
6. Final QA/docs: run Browser QA, update runbook/data docs if behavior is durable, and commit each coherent unit.

## Boundaries

- No provider change.
- No trading signal, recommendation, Practical Validation gate, Final Review decision, monitoring signal, broker order, or auto rebalance semantics.
- UI render must not fetch external provider data directly.
- Generated screenshots and local run history are not staged.
