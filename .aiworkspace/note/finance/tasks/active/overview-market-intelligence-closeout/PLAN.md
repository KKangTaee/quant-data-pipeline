# Plan

## 이걸 하는 이유?

Overview market intelligence phase의 주요 기능은 구현됐지만, 운영자가 다음 세션에서 어떤 순서로 데이터를 refresh하고 어떤 QA로 정상 여부를 판단할지 아직 한 곳에 정리되지 않았다. phase closeout은 구현을 더 늘리기보다, 현재 기능을 반복 운영 가능한 상태로 정리하는 작업이다.

## Scope

- phase 문서의 stale wording을 현재 구현 상태에 맞춘다.
- Overview market intelligence 운영 runbook을 추가한다.
- closeout 검증 명령과 결과를 task 문서에 남긴다.
- 추가 기능 구현은 하지 않는다.

## Done Criteria

- runbook에서 Market Movers, FOMC, Earnings refresh 순서와 실패 대응을 찾을 수 있다.
- phase docs가 Events placeholder / later wording을 더 이상 현재 상태처럼 말하지 않는다.
- focused tests, boundary check, diff check가 통과한다.
