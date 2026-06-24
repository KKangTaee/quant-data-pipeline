# Overview Futures Macro Mixed Substates V1 Risks

## Open Risks

- Too many subtype labels can make a conservative context screen look like overconfident prediction.
- Mixed subtypes must not change historical validation semantics or imply trade direction.
- UI copy must fit within the existing Futures Macro hero without adding noisy diagnostic rows.

## Mitigation

- The top-level scenario remains `혼재된 매크로 흐름`; subtype fields are supporting copy only.
- Historical validation still keys off the unchanged `scenario` field.
- No provider, DB schema, registry, saved setup, validation gate, monitoring signal, or trading semantics were added.
