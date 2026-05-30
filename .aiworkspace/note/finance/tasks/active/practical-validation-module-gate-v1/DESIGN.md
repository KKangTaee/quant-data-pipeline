# Practical Validation Module Gate V1 Design

Status: Active
Created: 2026-05-30

## Current Analysis

Current Practical Validation already has five visible sections:

1. source confirmation
2. validation profile
3. actual replay
4. diagnostic board
5. next step

The weak point is not the existence of diagnostics; it is routing.
The current result allows Final Review when `validation_route != BLOCKED`, so `Runtime replay NOT_RUN` and some `NEEDS_INPUT` rows can still move forward as review evidence.

## Direction

Add a Streamlit-free module planner:

- infer source traits from source kind, components, strategy keys, universe symbols, weights, replay contracts, and profile
- map diagnostics / audits / input checks into validation modules
- classify modules as required, conditional, or downstream reference
- produce a final review gate summary from required module statuses

The UI renders this module board before detailed diagnostics.
Existing detailed diagnostics and audits remain available, so no evidence is deleted.

## Module Groups

- Required for Final Review: source integrity, latest replay, benchmark parity, validation efficacy, data coverage, construction risk, backtest realism, robustness
- Conditional / strategy-specific: provider investability, leverage / inverse suitability, risk contribution, component role / weight, macro / regime
- Downstream reference: monitoring baseline, tax / account scope, selected-dashboard monitoring concepts

## Gate Policy

- `BLOCKED`, `NEEDS_INPUT`, or required `NOT_RUN` in required modules blocks save-and-move.
- `REVIEW` in required modules allows Final Review movement but marks the route as `READY_WITH_REVIEW`.
- Conditional modules do not block unless their own severity is `BLOCKED`.
- Downstream reference modules never block Practical Validation handoff.

## Files

- `app/services/backtest_practical_validation_modules.py`: source traits, module plan, final review gate builder
- `app/services/backtest_practical_validation_diagnostics.py`: attach module plan and gate to result
- `app/web/backtest_practical_validation.py`: format cleanup, module board render, save-and-move gate
- `app/services/backtest_practical_validation_source.py`: profile wording tweaks
- `tests/test_service_contracts.py`: focused contract coverage
