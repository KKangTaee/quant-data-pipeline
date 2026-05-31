# Notes

- 기존 `Compare & Portfolio Builder`는 사용자-facing label과 내부 route label이 섞여 있다.
- `backtest_workflow_routes.py`에서 legacy route를 유지하면서 visible analysis mode만 `Portfolio Mix Builder`로 바꾸는 방식이 가장 좁다.
- `backtest_compare.py`의 `_render_candidate_draft_readiness_box()`는 개별 전략 후보 handoff용이다. 이 기능 자체는 삭제하지 않고, 현재 mix builder 흐름에서 호출하지 않는 방식으로 future candidate comparison에 남겨둘 수 있다.
- current mix handoff는 `weighted_bundle`, component data trust, component Real-Money gate, weight discipline을 읽어 stop/go를 판단하면 된다.
- Mix candidate gate는 단일 전략의 1차 readiness helper와 같은 해석을 사용한다. 즉 component별 `Promotion != hold`, 실행 원천 blocker 없음, 검증 원천 blocker 없음이 handoff의 핵심 blocker 기준이다.
- `Portfolio Mix Builder`는 저장 setup을 새로 늘리지 않는다. 기존 `Save Portfolio Mix`는 reusable setup이고, Clean V2 source handoff는 mix 후보 통과 후 다음 검증으로 넘기는 workflow 기록이다.
- `Compare & Portfolio Builder` 문자열은 legacy route compatibility 상수로만 남긴다.
