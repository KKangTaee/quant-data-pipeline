# Risks

- User-selected Trend Groups may be unavailable after changing group mode or coverage if the group is absent from the current universe. Current mitigation: preserve valid selections and fall back only when none remain.
- Extra trend groups widen DB price reads. Current mitigation: service expands trend rows only to selected names plus visible Top N groups.
- Positive previous-return markers use previous period return magnitude on the same x-axis as current return magnitude. This keeps visual placement compact, but users should read tooltip labels for signed previous return when sign matters.
