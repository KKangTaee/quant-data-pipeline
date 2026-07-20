# Portfolio Monitoring Reference Help Removal V1 Plan

## Goal

Portfolio Monitoring의 중복 contextual Reference panel과 전용 설정을 제거하고, 도움말 source-of-truth를 기존 Reference Center로 단일화한다.

## 이걸 하는 이유?

현재 패널은 실제 포트폴리오 업무보다 먼저 큰 영역을 차지하지만 고유 정보가 없다. 같은 내용을 Reference Center가 이미 소유하므로 화면 중복과 유지보수 중복을 함께 줄여야 한다.

## Scope

- 1차: Portfolio Monitoring help 호출·전용 catalog 설정·test contract 제거
- 2차: Portfolio Monitoring/Reference Browser QA와 durable docs closeout

## Stop Condition

- written spec 사용자 검토 전에는 구현하지 않는다.
- 다른 surface의 contextual help 제거는 이번 범위에 포함하지 않는다.
- canonical Reference Center item 세 개와 Portfolio Monitoring destination을 보존한다.

## Next Action

사용자가 `DESIGN.md`를 검토·승인하면 `superpowers:writing-plans`로 상세 TDD 구현 계획을 작성한다.

