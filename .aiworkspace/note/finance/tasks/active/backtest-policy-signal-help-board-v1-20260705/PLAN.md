# Backtest Policy Signal Help Board V1

## 이걸 하는 이유?

Backtest Analysis의 `검증 기준 상세`은 1차에서 확인한 기준과 2차에서 확인할 review queue가 함께 보여 사용자가 어느 화면에서 무엇을 판단해야 하는지 헷갈렸다.
이번 작업은 1차에서 확정 가능한 기준만 카테고리별로 보여주고, 각 기준이 무엇을 검증했는지 바로 이해할 수 있게 하는 데 목적이 있다.

## Scope

- `app/services/backtest_handoff_readiness.py`
  - policy signal row에 사용자 설명용 `plain_explanation`, `checked_items` 추가
- `app/web/components/backtest_policy_signal_board/`
  - React board를 1차 기준 category board + click help UI로 개편
  - 2차 review queue 상세 목록은 제거하고 Practical Validation 이동 안내만 유지
- `app/web/backtest_result_display.py`
  - React component에는 2차 상세 그룹 대신 count / notice만 전달
- Practical Validation source snapshot
  - 2차 화면에서 설명을 이어 쓸 수 있도록 compact policy signal row에 설명 필드 보존

## Non-Goals

- gate score, promotion policy, source registration 기준 변경 없음
- Practical Validation module / Final Review selected-route gate 변경 없음
- registry / saved JSONL row rewrite 없음
- strategy runtime 계산식 변경 없음

## Done Criteria

- Policy Signals board가 `Data Trust`, `Execution Source`, `Validation Source` 중심으로 1차 기준을 묶어 보여준다.
- 각 기준의 `?` 도움말에서 무엇을 확인했는지 짧은 설명과 세부 체크 항목을 볼 수 있다.
- Backtest Analysis에서 2차 review queue 상세 목록을 반복 노출하지 않는다.
- React build, focused contract tests, py_compile, Browser QA를 완료한다.
