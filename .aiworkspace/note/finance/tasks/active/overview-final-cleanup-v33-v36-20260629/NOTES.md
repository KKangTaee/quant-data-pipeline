# Notes

- Active Overview UI work should add renderer bodies under `app/web/overview/components/*`, not `app/web/overview_ui_components.py`.
- Tests should import private helper contracts from the owning helper module, not `app/web/overview_dashboard.py`.
- Internal app code should import Overview service functions from `app/services/overview/*`, not an aggregate market-intelligence facade.
- Data Health remains a read-only collection ops / handoff read model. It is not the overall Overview calculation engine.
