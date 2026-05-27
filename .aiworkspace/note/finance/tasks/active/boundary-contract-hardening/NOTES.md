# Boundary Contract Hardening Notes

Status: Active
Created: 2026-05-27

## Decisions

- The transition advisory for `app.services/app.runtime -> app.web` can now become a hard failure because Task 6 removed the remaining advisory imports.
- Keep the checker focused on top-level service/runtime files, matching its existing scope.
- Do not add browser QA for helper script / test-only changes.

## Result

- `APP_WEB_IMPORT_RE` now records `kind == "app_web_import"` as a hard violation.
- `tests.test_service_contracts` has a temp-file behavior test that proves `app.web` imports fail the boundary scan.
- Runbooks now describe `app.web` imports from service/runtime as hard failure, not advisory.
