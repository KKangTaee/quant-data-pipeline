# Portfolio Monitoring Latest Decision Lifecycle V1 Risks

- legacy row에 `selection_source_id`가 없으면 `source_type/source_id`, 마지막으로 `decision_id`로 fallback해야 한다.
- 최신 selected row가 새 `decision_id`를 가지므로 기존 Monitoring item은 requested/effective decision provenance를 분리해야 한다.
- Final Review 이동 hint가 후보 selector와 맞지 않으면 사용자가 후보를 수동 선택할 수 있어야 하며 registry를 자동 변경하면 안 된다.
- item-local blocker가 정상 item의 group 계산까지 전부 중단하지 않도록 partial projection을 유지해야 한다.
- current worktree의 사용자 registry, saved setup, run history, generated QA artifact는 stage하지 않는다.

## Residual Gaps

- actual Final Review registry 6개 subject는 모두 최신 selected라 actual 화면에서 잠금 카드를 만들 수 없었다. registry를 오염시키지 않고 synthetic lifecycle/read-model/React 테스트로 잠금·재개 계약을 검증했다.
- broad `tests/test_service_contracts.py`의 18개 failure는 implementation 이전 baseline과 동일하다. Practical Validation sentiment, legacy Final Review assertion, Futures Macro/AAII 영역의 별도 drift이며 이 task 범위에서 수정하지 않았다.
- Final Review는 전달한 active source hint를 우선 사용하지만 해당 후보가 더 이상 eligible selector에 없으면 기존 selector fallback을 따른다. 이 경우에도 registry나 Monitoring item을 자동 수정하지 않는다.
