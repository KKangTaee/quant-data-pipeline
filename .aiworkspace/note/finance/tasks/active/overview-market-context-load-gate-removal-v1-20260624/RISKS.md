# Overview Market Context Load Gate Removal V1 Risks

## Open Risks

- Removing the gate restores the expected flow but also restores the visible initial wait when Market Context is the default tab.
- A future optimization should target the expensive read model pieces, especially futures macro validation, rather than hiding the whole Market Context behind a manual button.

## Closed Or Bounded Risks

- The internal text-tab selector remains; this task does not reintroduce anchor-based tab navigation.
