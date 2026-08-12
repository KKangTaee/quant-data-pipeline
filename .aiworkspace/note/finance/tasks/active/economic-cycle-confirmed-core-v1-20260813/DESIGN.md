# Design

Canonical design owner:

- `docs/superpowers/specs/2026-08-13-economic-cycle-confirmed-core-state-design.md`

Raw RTDSM quadrants are candidate evidence. Two consecutive usable releases of
the same candidate are required to change the official state, with no backdating
and no fixed destination order. Dataset and validation consume that confirmed
state exactly once.

Persistence, service, and React are conditional on actual combined `READY`.
The circular route visual remains; asset checkpoint ownership is frozen.
