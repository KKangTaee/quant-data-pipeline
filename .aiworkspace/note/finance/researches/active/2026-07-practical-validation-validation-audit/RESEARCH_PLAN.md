# Practical Validation Validation Audit

Status: Active
Created: 2026-07-06
Owner: Codex

## Why This Exists

Practical Validation Flow 3 / Flow 4가 좋아졌지만, 사용자가 아직 "무엇을 검증했고, 무엇이 부족하고, Final Review 이동 기준이 왜 여기서 보이는지"를 바로 이해하기 어렵다고 지적했다.

이번 리서치는 UI 문구 수정이 아니라 Practical Validation에서 실제로 쓰는 검증 항목이 신빙성 있고 과하지 않은지 먼저 감사하고, 다음 구현에서 제거 / 조건부 / 강등 / 유지할 기준을 정하는 작업이다.

## User Questions

- Flow 4에서 `Final Review로 넘기기 전 확인 기준`을 메인으로 노출하는 것이 맞는가?
- Flow 4는 카테고리별로 무엇을 검증했고 몇 개가 통과 / 실패했는지 보여주는 것이 맞지 않은가?
- 각 포트폴리오에 적용되는 검증들이 실제로 신빙성 있는 검증인가?
- 너무 과하거나 Practical Validation에서 볼 필요가 없는 검증은 없는가?
- 불필요한 검증은 제외하거나 후속 참고로 낮출 수 있는가?

## Scope

검토 범위:

- Practical Validation module planner / gate policy
- Practical Validation workspace read model
- Practical Validation Flow 3 / Flow 4 rendering contract
- validation efficacy, data coverage, construction risk, realism, stress / robustness, provider / macro diagnostics
- Final Review selected-route preflight의 위치와 의미

비범위:

- Provider 수집 실행
- JSONL registry rewrite
- backtest strategy runtime 변경
- Final Review 저장 정책 변경
- live approval / broker order / auto rebalance 의미 추가

## Tentative Development Roadmap

1차: 검증 체계 audit

- 현재 module / board / gate inventory를 정리한다.
- 유지 / 조건부 / 강등 / 제외 후보를 결정한다.
- 완료 조건: `CURRENT_PROJECT_AUDIT.md`와 `RECOMMENDATION.md`에 다음 구현 기준을 남긴다.

2차: validation taxonomy service 조정

- Flow 4가 `카테고리별 검증 결과`를 읽도록 module grouping을 바꾼다.
- `selected_route_preflight`는 category가 아니라 handoff summary로 분리한다.
- 완료 조건: service contract와 focused tests가 category count / failure list를 검증한다.

3차: gate severity 정리

- core blocker, review-required, conditional-only, reference-only를 명시한다.
- 중복 blocker를 제거하고, 과한 hard blocker를 review로 낮춘다.
- 완료 조건: `NOT_RUN`은 pass가 아니지만, 후보 특성과 무관한 조건은 block하지 않는다.

4차: Flow 4 UI 개편

- 상단 제목을 `카테고리별 검증 결과`로 바꾼다.
- 카테고리별 pass / failed / review / not-run count와 실패 항목을 먼저 보여준다.
- Final Review 이동 가능성은 우측 또는 하단 compact handoff summary로 낮춘다.

5차: QA / docs / commit

- focused tests, py_compile, diff check, Browser QA를 수행한다.
- 승인된 결과만 durable docs에 승격한다.
