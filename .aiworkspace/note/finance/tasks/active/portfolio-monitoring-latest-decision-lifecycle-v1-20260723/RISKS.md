# Portfolio Monitoring Latest Decision Lifecycle V1 Risks

- legacy row에 `selection_source_id`가 없으면 `source_type/source_id`, 마지막으로 `decision_id`로 fallback해야 한다.
- 최신 selected row가 새 `decision_id`를 가지므로 기존 Monitoring item은 requested/effective decision provenance를 분리해야 한다.
- Final Review 이동 hint가 후보 selector와 맞지 않으면 사용자가 후보를 수동 선택할 수 있어야 하며 registry를 자동 변경하면 안 된다.
- item-local blocker가 정상 item의 group 계산까지 전부 중단하지 않도록 partial projection을 유지해야 한다.
- current worktree의 사용자 registry, saved setup, run history, generated QA artifact는 stage하지 않는다.
