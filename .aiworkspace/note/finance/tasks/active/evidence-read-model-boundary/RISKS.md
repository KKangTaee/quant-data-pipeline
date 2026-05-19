# Evidence Read Model Boundary Risks

## Open Risks

- Final Review helper still contains save-row construction and validation/paper observation orchestration; moving that requires a separate service contract.
- Selected Dashboard runtime read model is already read-only but still under `app/web/runtime`; this task only extracts common final decision evidence rows.
- UI table column ordering must remain stable because these rows are user-facing review evidence.

## Closed In This Slice

- Final Review saved decision status / table rows and Selected Dashboard evidence rows now use one shared service read model.
- The new read model service has no Streamlit dependency and no registry write behavior.
