# Risks

- Official float-adjusted market cap is not available in the current DB, so V1 uses `close * latest-known shares_outstanding`.
- Historical listing / delisting coverage is partial unless lifecycle collectors have been run broadly.
- Current asset profile is still used for static metadata and may not fully represent historical listing state.
