# Portfolio Monitoring Latest Decision Lifecycle V1 Plan

Status: Design Approved
Date: 2026-07-23

## 이걸 하는 이유?

append-only Final Review 이력은 보존하면서 Portfolio Monitoring의 신규 선택과 기존 실행은 후보별 최신 판단을 따라야 한다.

## 전체 roadmap

1. 최신 판단 identity와 lifecycle 계약을 고정한다.
2. 신규 catalog와 기존 selected-strategy replay/read model을 연결한다.
3. `추적 자격 변경` UI, Final Review 재확인, 기존 추적 종료 행동을 연결한다.
4. 실제 registry/Browser QA와 문서 동기화를 완료한다.

## 범위

- 포함: 최신 판단 projection, 신규 후보 필터, 기존 항목 실행 잠금, 재확인/종료 행동.
- 제외: 과거 row 재작성, 자동 삭제/종료, Monitoring-local 판단 override, 주문 기능.

## 중단 조건

최신 판단 identity가 실제 registry source chain과 일관되지 않거나 Final Review 이동이 현재 stage ownership을 우회해야 한다면 구현을 중단하고 설계를 다시 확인한다.
