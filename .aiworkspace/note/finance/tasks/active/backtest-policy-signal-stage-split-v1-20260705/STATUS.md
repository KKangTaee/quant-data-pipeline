# Backtest Policy Signal Stage Split V1 Status

Status: Completed
Date: 2026-07-05

## 진행

- 서비스 inventory에 `first_stage_rows`, `second_stage_review_rows`, 설명 필드를 추가했다.
- Backtest Analysis의 Policy Signals 보드를 React component로 연결했다.
- Practical Validation의 `Backtest에서 넘어온 2차 확인 항목` 카드와 상세 표가 새 설명 필드를 읽게 했다.
- Handoff card의 `먼저 해결` count를 1차 source blocker 기준으로 맞춰 Policy Signals 보드와 같은 숫자를 보게 했다.
- 기존 Python HTML 기반 Policy Signals gate fallback dead code를 제거했다.

## 완료 조건

- Backtest Analysis는 1차에서 확정 가능한 통과 / 차단 기준만 자세히 보여준다.
- 2차에서 확인할 review 신호는 Handoff와 Practical Validation entry queue로 전달된다.
- React component는 UI 전용이고 Python 서비스 / registry / source 등록 로직을 호출하지 않는다.
- focused tests, compile, Browser QA를 완료했다.
