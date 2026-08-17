# Master Merge Resolution Risks

- shared `tests/test_service_contracts.py`에는 이번 Futures Macro 변경 밖의 기존 contract drift가
  보고돼 있다. 이번 통합은 task-owned focused suite와 변경된 contract node를 별도로 검증한다.
- exchange holiday calendar 부재와 provider 지연은 기존 residual risk다. 불완전한 장중 자료는
  최신 완료 세션으로 fail closed해야 한다.
- registry/saved/run-history와 다수 QA 이미지는 이번 merge commit에 포함하지 않는다.
- current worktree `.venv`는 Python symlink만 있고 pytest/pip가 없다. 이번 검증은 incoming을
  만든 `sub-dev`의 locked Python runtime과 현재 worktree source를 조합해 실행했다.
