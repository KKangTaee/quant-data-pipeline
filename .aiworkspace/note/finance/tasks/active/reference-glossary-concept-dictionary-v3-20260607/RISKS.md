# Risks

- The curated dictionary can duplicate `GLOSSARY.md`; keep it focused on UI-critical operational statuses and concepts.
- Search result ordering must keep exact curated status hits visible before broad markdown matches.
- Browser automation changed the text input DOM value but did not reliably trigger Streamlit rerun during QA. Search semantics are covered by Streamlit-free unit tests; re-test the actual widget manually when 4차 contextual links touch Reference navigation.
