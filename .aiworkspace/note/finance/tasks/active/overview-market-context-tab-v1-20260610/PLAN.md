# Overview Market Context Tab V1 Plan

## Why

Overview의 첫 화면에서 macro / market context cockpit과 deep tab 안내를 하나의 독립된 entry surface로 보이게 한다.

## Scope

- Add `Market Context` as the first Workspace > Overview deep tab.
- Move market context refresh, cockpit, Source Confidence, Deep Tab guide, and Overview Map into that tab.
- Keep existing DB-backed read model and Overview action facade boundaries.
- Do not add providers, schemas, registry writes, saved JSONL writes, or trading / validation decision semantics.

## Steps

1. Add a focused service contract test for the new first-tab IA.
2. Implement the minimal Streamlit tab restructuring in `app/web/overview_dashboard.py`.
3. Run focused tests, compile, boundary check, diff check, and Browser QA.
4. Update task notes / root handoff logs and commit the coherent implementation unit.
