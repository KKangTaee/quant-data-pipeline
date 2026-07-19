# Portfolio Monitoring Tracking End Reopen V1 Plan

Status: In Progress
Date: 2026-07-19

## 전체 흐름

1. 계약 고정: `reopen_item` 명령, 동일 항목 복구, 제한 조건을 테스트로 작성한다.
2. 서비스 구현: command enum, idempotent command handler, repository update를 연결한다.
3. 화면 구현: Python bridge와 React 종료 항목 액션을 연결한다.
4. 검증/정리: focused tests, typecheck/build, static asset 확인, 문서와 root handoff를 동기화한다.

## 이번 차수 범위

- 포함: 기존 종료 항목의 종료 취소와 활성 목록 복귀.
- 제외: 새 추적 episode 생성, 종료/재진입 이력을 복수 구간으로 저장하는 schema, broker 주문 및 자동 매매.

