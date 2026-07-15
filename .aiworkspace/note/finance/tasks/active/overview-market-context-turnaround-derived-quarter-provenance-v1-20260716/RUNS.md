# Runs

## 2026-07-16 Diagnosis

- actual MRNA DB-only read model: turnaround `READY`, statement basis `2026-03-31`.
- timeline inspection: 2023-Q4 revenue/GP/TTM margin missing, operating income `+6M` present.
- raw statement inspection: FY2023 revenue `6.848B`, cost `4.693B`, operating income `-4.239B` present.
- resolver inspection: revenue Q1/Q2 and Q3/FY use two allowlisted concept names; exact concept grouping prevents Q4 derivation.
- UI inspection: `contiguousTurnaroundSegments` intentionally breaks non-finite slots; screen copy states no interpolation.

No production code or tests changed during diagnosis/design.
