# Risks

- confirmation can reduce noise but introduces one-release lag
- confirmed state gates may pass while actual pressure/destination models fail
- candidate features must use only information available at the forecast origin
- dataset must not confirm an already-confirmed state a second time
- production UI must remain unchanged unless the full publication gate is READY
