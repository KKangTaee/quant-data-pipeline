# Overview Legacy Dashboard Removal V17-V24 Risks

- Legacy file risk is resolved in V24: `app/web/overview/legacy_dashboard.py` has been deleted.
- Residual risk is compatibility drift: `app/web/overview_dashboard.py` still explicitly exports private helper names for existing tests/imports.
- Future cleanup can remove compatibility exports one by one after imports move to domain helper modules directly.
