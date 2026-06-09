# Overview Market Context Readability V2 Plan

## Why

Market Context V1/V1.5는 정보를 많이 보여주지만 카드가 많아 첫 화면에서 읽는 순서가 약하다.
이번 작업은 사용자가 먼저 결론과 다음 확인 순서를 읽고, 필요한 카드만 내려가며 확인하게 만든다.

## Scope

- Make the cockpit headline clearer: source/data review wording instead of implying the market itself is broken.
- Add summary metadata for review count, data-health count, and next deep-tab path.
- Render a compact summary rail before the cards.
- Keep the top three analytical cards prominent and make the remaining context cards lower-density.

## Out Of Scope

- New providers, DB schema, registry/saved JSONL writes.
- Overview render-time external fetch.
- Scheduler or automation changes.
- Validation gate, Final Review decision, monitoring signal, trading action.

## Steps

1. Add failing tests for the revised headline and summary rail CSS/HTML.
2. Update the cockpit read model in `app/services/overview_market_intelligence.py`.
3. Update the renderer and CSS in `app/web/overview_ui_components.py`.
4. Run focused tests, compile, boundary check, diff check, and Browser QA.
5. Update task/root docs and commit the coherent UI polish unit.
