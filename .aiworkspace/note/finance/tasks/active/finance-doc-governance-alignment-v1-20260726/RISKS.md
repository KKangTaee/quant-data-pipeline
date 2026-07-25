# Finance Document Governance Alignment V1 Risks

## Open Risks

- `main-dev`에는 이 branch에 없는 경제사이클 문서 변경이 있어 이후 통합 시 semantic reconciliation이 필요하다.
- runtime skill mirror는 repo 밖에 있으므로 source 변경 후 동일성 검증이 필요하다.
- legacy task 상태 표기가 다양하므로 새 상태 계약은 점진 적용해야 한다.
- root log가 매우 크지만 이번 범위에서 전면 압축하면 과거 handoff 손실 위험이 커 제외한다.
- full `tests.test_service_contracts`에는 이번 diff와 무관한 기존 18개 failure/error baseline이 남아 있다.

## Mitigations

- current canonical roles와 상태 우선순위를 명시해 통합 시 판단 기준으로 사용한다.
- `quick_validate.py`와 source/mirror diff를 둘 다 실행한다.
- 새로 만들거나 이번에 수정하는 상태 문서에만 `State:` 계약을 적용한다.
- root log는 필요한 상단 pointer만 최소 수정한다.
- 이번에 변경한 문서 계약은 focused test로 분리해 통과 여부를 확인하고, 기존 18개는 별도 제품 task에서 다룬다.
