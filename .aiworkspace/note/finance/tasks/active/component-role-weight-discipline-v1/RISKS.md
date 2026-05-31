# Component Role / Weight Discipline V1 Risks

Status: Complete
Created: 2026-05-29

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Inferred roles look like explicit user intent | role evidence가 실제 proposal source보다 강하게 보일 수 있음 | explicit role source와 inferred / missing source를 분리 |
| Weight rationale becomes memo persistence | 사용자의 메모용 저장 기능으로 확장될 수 있음 | existing component metadata만 읽고 새 저장 기능은 만들지 않음 |
| Profile role fit is over-enforced | 다양한 전략 구성이 불필요하게 blocked 될 수 있음 | V1은 `REVIEW` / `NEEDS_INPUT`로 표시하고 selected-route enforcement는 11-5로 분리 |

## Residual

- V1 role category normalization is intentionally compact and conservative.
- Selected-route gate policy enforcement remains Phase 11 task 11-5.
