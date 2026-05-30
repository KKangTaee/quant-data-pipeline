# Backtest Portfolio Mix Builder Flow V1

Status: Active
Started: 2026-05-30

## 이걸 하는 이유?

Backtest Analysis의 기존 `Compare & Portfolio Builder`는 개별 전략 비교, 개별 후보 handoff, weighted mix 생성, saved mix replay가 한 화면에 섞여 있었다.
사용자 입장에서는 이 화면이 "비교 화면"인지 "여러 전략을 섞어 하나의 후보를 만드는 화면"인지 흐름이 모호했다.

이번 작업은 이 화면의 주 목적을 `Portfolio Mix Builder`로 재정의한다.
Backtest Analysis는 단일 전략 후보 또는 mix 후보를 만들어 Practical Validation으로 넘기는 1차 후보 생성 단계가 되고,
진짜 후보 간 비교는 이후 별도 `Candidate Comparison` 성격의 read-only 도구로 분리할 수 있도록 경계를 정리한다.

## Scope

- Backtest Analysis submode label을 `Portfolio Mix Builder` 기준으로 정리한다.
- 기존 legacy `Compare & Portfolio Builder` route는 계속 호환한다.
- mix 생성 화면의 copy를 `component 실행 -> weight 조합 -> mix 후보 판단 -> Practical Validation handoff` 흐름으로 정리한다.
- 개별 전략 후보를 이 화면에서 바로 넘기는 compare handoff를 숨기고, mix 전체 handoff만 주 action으로 둔다.
- mix handoff 버튼은 mix 후보 readiness가 통과 또는 조건부 통과일 때만 활성화한다.
- Saved mix는 reusable setup임을 유지하되, replay / data trust / component gate가 막으면 handoff를 막는다.
- 저장 기능을 새로 늘리지 않는다. 기존 saved mix setup 저장은 유지하되 후보 검증 저장으로 오해하지 않게 문구를 조정한다.

## Out Of Scope

- 별도 `Candidate Comparison` 화면 신규 구현.
- DB ingestion, strategy runtime, core backtest engine 변경.
- 새 registry / user memo / preset 저장 추가.
- Practical Validation / Final Review의 검증 로직 재설계.

## Exit Criteria

- Backtest Analysis에서 `Portfolio Mix Builder`가 visible mode로 표시된다.
- legacy route / session state의 `Compare & Portfolio Builder` 요청은 새 mode로 정상 이동한다.
- current weighted mix handoff는 readiness gate에 따라 enabled / disabled가 갈린다.
- 개별 전략 candidate handoff는 mix builder 본문에서 더 이상 주 action으로 노출되지 않는다.
- 관련 service contract / compile / diff check가 통과한다.
