# Backtest Component Static Distribution V1 Status

Status: Written design review pending
Updated: 2026-07-19

## Current

- 사용자와 Backtest 전체 12개를 Overview 방식의 `component_static/`으로 통일하는 범위를 합의했다.
- 현재 component inventory, loader 경로, Vite outDir, Git 추적 상태와 기존 service contract test의 `frontend/build/index.html` 의존을 확인했다.
- 구현 전 written design을 확정했다.

## Next

- 사용자의 written design 검토 승인을 받는다.
- 승인 후 상세 구현 계획과 TDD 순서를 작성한다.
- 1차 contract test부터 구현을 시작한다.

## Scope Guard

- UI, 계산, registry, DB 동작은 변경하지 않는다.
- qweb 또는 다른 launcher는 다시 만들지 않는다.
