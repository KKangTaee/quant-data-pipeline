# Notes

## Findings

- `git status --short` 기준 tracked 변경은 없고, untracked QA screenshots만 존재한다. 이 파일들은 generated artifact로 보고 stage하지 않는다.
- `docs/PROJECT_MAP.md`와 `docs/flows/BACKTEST_UI_FLOW.md`는 현재 Backtest / Practical Validation / Overview split 흐름을 대체로 잘 반영하고 있다.
- `docs/ROADMAP.md`는 상단에서 `practical-validation-boundary-cleanup-v1-20260708`을 latest completed task로 잡지만, 중간에 `backtest-quarterly-productionization-v1-20260708`도 다시 `Latest completed task`로 표시한다. Manifest 기준 최신 완료 task는 boundary cleanup이다.
- 현재 code structure 기준 Overview primary tabs는 `Market Context`, `Market Movers`, `Futures Macro`, `Sentiment`, `Events`다. `Futures Monitor` / `Sector / Industry` standalone primary tab 표현은 current docs에서 낮춰야 한다.
- 코드 리뷰 결과 `app/services/overview/data_health.py`의 Data Health handoff target과 `app/services/overview/market_context.py`의 cockpit / refresh plan 일부가 아직 `Futures Monitor 1m OHLCV`, `Workspace > Overview > Futures Monitor`, `Sector / Industry`를 current user-facing 경로처럼 노출했다.
- 해당 drift는 단순 문서 문제가 아니라 Market Context cockpit / Data Health handoff / refresh plan contract의 사용자-facing label 문제라, legacy input alias는 유지하고 출력 label을 `Futures Macro 1m OHLCV`, `Workspace > Overview > Futures Macro`, `Market Movers`로 정규화했다.

## Code Review Notes

- 리뷰는 stale path / missing file reference / boundary drift / generated artifact staging 위험 중심으로 진행했다.
- 추가 개발 후보: post-merge docs cleanup 때 `docs/INDEX.md`, `docs/ROADMAP.md`, task / phase `STATUS_MANIFEST.md`, Overview navigation, Overview data-health handoff string을 함께 훑는 작은 consistency check script를 만들면 pointer 중복과 legacy tab명 drift를 더 빨리 잡을 수 있다.
