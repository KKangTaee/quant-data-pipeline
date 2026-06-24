# Overview Legacy Cleanup V6-V10 Status

## 2026-06-25

- Started V6-V10 sequential cleanup after the user approved phased development with QA after each phase.
- V6 complete: audited active legacy calls, retained compatibility names, removable standalone tab wrappers, and Candidate Ops snapshot helpers.
- V7 complete: moved Overview primary navigation constants / selector functions into `app/web/overview/navigation.py`; active page now imports the navigation surface directly while legacy keeps compatibility imports.
- V8 complete: moved the Overview IA closeout read-model body into `app/services/overview/ia.py`; web helper now exposes it through a service import.
