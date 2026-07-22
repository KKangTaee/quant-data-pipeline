# Practical Validation Enrichment Recheck UX V1

## Goal

Level2에서 외부 데이터 보강을 실행한 사용자가 현재 상태와 다음 행동을 즉시 이해하고, 보강된 데이터로 재검증한 뒤 새 결과 저장과 Final Review 이동까지 같은 React 원셸에서 이어서 완료하게 한다.

## 이걸 하는 이유?

현재 수집기와 검증 안전장치는 정상 동작하지만, React 원셸 전환 때 기존 복구 진행 표시가 렌더 경로에서 빠졌다. 수집 후 replay가 안전하게 초기화되어도 화면은 이를 녹색 완료 알림과 일반 Step 2로만 보여 주므로 사용자는 작업이 끝났는지, 다시 무엇을 눌러야 하는지 판단해야 한다.

## Scope

- 외부 데이터 보강 결과와 `recheck_required` 상태를 Decision Workspace read model에 연결한다.
- 알림을 성공/주의/오류 의미가 있는 구조화 상태로 바꾼다.
- React decision surface에 `자료 보강 -> 재검증 -> 저장 -> Final Review` 진행 맥락과 현재 CTA를 통합한다.
- 수집 결과는 성공/부분 성공/실패를 compact하게 요약하고 raw job/row 상세는 first-read에 노출하지 않는다.
- 기존 provider 수집기, DB schema, 검증 기준, append-only registry 계약은 변경하지 않는다.

## Roadmap

- 1차: 상태 계약과 회귀 테스트
- 2차: React 진행 UX와 fallback 통합
- 3차: 회귀 검증, actual Browser QA, durable docs sync

## Stop Condition

- 보강 직후 warning/current 상태와 `보강된 데이터로 재검증` CTA가 보인다.
- 재검증 후 진행 상태가 결과 확인/저장 또는 남은 blocker 해결로 전환된다.
- 부분 실패를 전체 성공으로 표시하지 않는다.
- 저장/Final Review Gate와 수집/재검증 실행 경계가 유지된다.
