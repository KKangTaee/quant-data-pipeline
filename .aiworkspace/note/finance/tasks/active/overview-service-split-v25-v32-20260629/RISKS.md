# Overview Service Split V25-V32 Risks

## Known Risks

- Mechanical extraction can miss private helper dependencies.
- Existing tests import the legacy service path directly, so compatibility facade must remain until tests and callers are migrated.
- Market Context cockpit composes snapshots from several domains; move it after the underlying domains are available.
