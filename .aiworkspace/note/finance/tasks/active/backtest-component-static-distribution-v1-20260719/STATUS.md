# Backtest Component Static Distribution V1 Status

Status: Implementation plan ready
Updated: 2026-07-19

## Current

- 사용자와 Backtest 전체 12개를 Overview 방식의 `component_static/`으로 통일하는 범위를 합의했다.
- 현재 component inventory, loader 경로, Vite outDir, Git 추적 상태와 기존 service contract test의 `frontend/build/index.html` 의존을 확인했다.
- 구현 전 written design을 확정했고 사용자가 구현 진행을 승인했다.
- TDD, 12개 loader/Vite migration, committed static bundle, clean archive/Browser QA 순서의 구현 계획을 작성했다.

## Next

- `tests/test_component_static_distribution.py`의 RED부터 시작한다.
- 12개 loader/Vite 설정을 전환하고 전체 frontend를 다시 빌드한다.
- clean archive와 실제 Browser QA로 별도 npm build 없는 실행을 검증한다.

## Scope Guard

- UI, 계산, registry, DB 동작은 변경하지 않는다.
- qweb 또는 다른 launcher는 다시 만들지 않는다.
