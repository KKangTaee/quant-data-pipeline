# Risks

- Do not change gate calculation, replay execution, provider collection, or persistence while changing UI wording.
- Do not hide technical status entirely; keep it as a compact tag for debugging.
- Avoid adding another explanatory layer. Flow 3 must read as an action queue, Flow 4 as a criteria status summary.

## Closeout

- Gate calculation, replay execution, provider collection, registry / saved JSONL, and Final Review persistence were not changed.
- Technical statuses remain as compact `기술 기준` tags and detail disclosures, while first-read labels use issue / criteria language.
- Browser QA showed existing Streamlit dataframe Arrow and `use_container_width` warnings unrelated to this task; they remain out of scope.
