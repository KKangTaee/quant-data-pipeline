# Notes

- Base Universe count is not treated as an execution problem when the preset loaded count matches the selected candidate pool.
- Price freshness issues are split into refreshable price issues and provider/source gap issues.
- Provider/source gap action is intentionally disabled because repeated OHLCV refresh can produce no rows and leave the user in a loop.
- Statement shadow gaps use targeted `run_extended_statement_refresh` with the missing symbols from the coverage preview.
- The React component emits a Streamlit component value instead of using a separate Streamlit button row.
