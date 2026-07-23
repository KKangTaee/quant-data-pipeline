# Portfolio Monitoring Latest Decision Lifecycle V1 Runs

- 2026-07-23: current registry 6 rows가 모두 `SELECT_FOR_PRACTICAL_PORTFOLIO`, `monitoring_candidate=true`임을 read-only로 확인했다.
- 2026-07-23: 과거 selected와 최신 hold가 같은 source에 있어도 기존 catalog가 과거 selected를 반환하는 최소 재현을 확인했다.
- 2026-07-23: Portfolio Monitoring catalog/selected-strategy focused tests 11개가 현재 baseline에서 통과했다.
- registry, saved setup, run history는 변경하지 않았다.
- 2026-07-23: 4개 구현 task, exact interface, RED/GREEN 명령, 커밋, protected artifact audit를 포함한 TDD plan을 작성했다.
- plan placeholder/spec coverage/type consistency self-review와 `git diff --check`를 통과했다.
- 2026-07-23: lifecycle service RED에서 missing module을 확인한 뒤 Python unit 5개를 GREEN으로 전환했다.
- 2026-07-23: catalog/selected-strategy/read-model/dashboard command focused Python `78 passed`, React `34 passed`, typecheck/build를 통과했다.
- 2026-07-23: broad selected command는 `18 failed, 957 passed, 49 subtests passed`였다. 구현 직전 commit `45795d0b7`의 detached worktree에서 `tests/test_service_contracts.py`를 재실행해 동일 18 failures와 `849 passed, 41 subtests passed`를 확인하고 임시 worktree를 제거했다.
- 2026-07-23: production loader read-only probe는 registry 6 rows / latest subjects 6 / latest selected subjects 6이었다. Synthetic latest hold는 catalog 0, `TRACKING_ELIGIBILITY_CHANGED`, locked true, effective decision `latest-hold`였다.
- 2026-07-23: actual `/selected-portfolio-dashboard` Browser QA에서 1440px iframe `1269/1269`, 760px `717/717`로 horizontal overflow 0과 browser error 0을 확인했다. actual registry에는 superseded subject가 없어 lock card는 synthetic automated contract로 검증했다.
- 2026-07-23: QA screenshot `portfolio-monitoring-latest-decision-lifecycle-v1-qa.png`는 generated artifact로 남기고 stage하지 않았다.
- 2026-07-23 closeout: lifecycle/catalog/selected-strategy/read-model/page/component/command/schema Python `108 passed, 8 subtests passed`, py_compile, React `34 passed`, typecheck, deterministic production build와 `git diff --check`를 통과했다.
