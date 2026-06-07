# Reference Drift Guard / QA Polish V5 Design

Status: Active
Date: 2026-06-08

## Service Boundary

`app/services/reference_contextual_help.py` remains Streamlit-free and owns the contextual help catalog.
The new drift report is a pure read model:

- read contextual help catalog
- read shared `get_reference_concept_dictionary()`
- compare terms, link targets, duplicate surface keys, raw guide focus markers
- return a compact `PASS` / `REVIEW` report

The report does not write files, update registries, fetch providers, or affect validation gates.

## UI Boundary

`app/web/reference_contextual_help.py` only renders controlled catalog text.
The renderer keeps links restricted by the service catalog and removes unnecessary HTML escaping that turned controlled guide path text into awkward visible entities.

## Test Strategy

- Add a RED focused test for `build_reference_contextual_help_drift_report()`.
- Keep existing lookup copy/link tests.
- Run related Reference catalog tests and service contract tests before completion.

## QA

Use Browser QA against Streamlit to confirm one real workflow surface renders the contextual help with the polished guide path.
The QA screenshot is generated output and is not committed.
