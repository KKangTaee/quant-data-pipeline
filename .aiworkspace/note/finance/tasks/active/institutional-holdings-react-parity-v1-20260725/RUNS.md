# Institutional Holdings React Parity V1 Runs

## 2026-07-25 Diagnosis

- Reviewed finance docs, current Institutional Holdings tasks, Today / Market Research task records, Python page wrappers and React component sources.
- Started a dedicated local Streamlit server on port `8528`.
- Inspected actual Institutional Holdings, Today and Market Research at desktop and 420px.
- Confirmed Holdings functionality and data flow are healthy; the identified gap is page ownership, hierarchy, visual tokens and responsive first-read.
- Institutional and Market Research console review returned no error / warning. A temporary `/today` route probe produced the expected Streamlit page-not-found fallback before the valid root Today route was used; it is not a Today product regression.
- Browser tabs were finalized, viewport override reset and the dedicated server stopped.

## 2026-07-25 Design

- Created the active task shell and written React parity design.
- Visual Companion rendered three one-shot directions using the same Berkshire manager context and existing feature set.
- Terminal feedback is the primary selection record: the user replaced B with `C · Modular Research Studio`.
- Updated the written design for desktop research rail / main canvas and tablet/mobile studio switcher / drawer.
- No implementation code, registry, saved setup or generated artifact was changed.
