# UI Engine Boundary Lint Notes

## Initial Decision

- Make `app/services` Streamlit-free checks hard failures.
- Keep `app.web` imports from service as advisory because current services still use Streamlit-free transitional modules.
- Guard staged generated / registry / saved files because this check will often run before commit.

## Observed Advisory Debt

Current service files still import some `app.web.runtime` or Streamlit-free helper modules.
This is acceptable for the current boundary foundation, but future cleanup can move those runtime/repository helpers out of `app.web`.
