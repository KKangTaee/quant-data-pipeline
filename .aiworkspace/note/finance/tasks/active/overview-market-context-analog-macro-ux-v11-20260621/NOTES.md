# Notes

## Product Interpretation

- User wants fewer generic cards and a clearer analytical reading path.
- The problem is not a Streamlit limitation. Current UI renders useful read-model payloads too literally.
- V11 should treat historical analog as a user-facing analysis surface:
  - 기준 선택
  - 기준 설명
  - 과거 사례 조건
  - 결과 요약
  - Macro condition comparison
  - limitations / evidence

## Boundaries

- Keep `Ingestion -> DB -> Loader/Service -> UI`.
- Keep Macro / FRED / Events / Sentiment as context-only unless already marked as hard condition in the service model.
- Do not use prediction / recommendation / buy / sell / signal wording.

## Implementation Notes

- Streamlit widgets cannot be embedded inside the raw HTML section, so the controls are placed immediately before the analog HTML section under `과거 유사 맥락 기준 선택`.
- The rendered analog HTML now separates broad analog from macro-conditioned comparison as sibling sections, so Macro no longer appears as a card nested inside `참고: 과거 유사 맥락`.
- `Macro 조건 포함 비교` still has dense detail rows because the underlying condition audit is large; future polish can collapse lower-priority condition details if needed.
