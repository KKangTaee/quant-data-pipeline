# Status

Status: Active
Last Updated: 2026-07-05

## Current State

V1 taxonomy / roadmap planning is documented and ready for user review.

Completed in this task:

- Read project instructions, finance docs, Backtest UI flow docs, and Practical Validation core files.
- Classified the request as Backtest UI / Practical Validation roadmap work.
- Confirmed no code implementation should happen before the design / roadmap is approved.
- Created this active task bundle.
- Drafted Practical Validation taxonomy and V1-V8 implementation direction.
- Updated active task pointers and root handoff logs.
- Ran documentation verification checks.

## Current Conclusion

The Practical Validation problem is not a lack of validation logic. The main issue is that diagnostics, audits, modules, board map, and selected-route preflight are all visible as peer concepts.

The next implementation should create a screen-oriented workspace read model before broad UI movement.

## Next Action

After user approval of this design:

1. Start V1 implementation with a read-model contract test.
2. Add `app/services/backtest_practical_validation_workspace.py`.
3. Build grouping helpers for core evidence, conditional evidence, downstream reference, and technical details.
4. Keep visible UI changes minimal until V4.

## Verification State

No code changed yet.

Documentation verification still needed before closing this planning task:

- None for this documentation-only planning pass.

Completed checks:

- task file existence check
- task placeholder scan for unresolved markers
- `git diff --check` for changed docs

Browser QA and py_compile were not run because no code or UI implementation changed.
