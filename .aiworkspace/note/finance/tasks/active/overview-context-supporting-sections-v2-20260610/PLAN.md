# Overview Context Supporting Sections V2 Plan

## Why

Market Context V2의 summary rail은 좋아졌지만 `Source Confidence`와 `Overview Map`이 여전히 첫 화면에서 큰 면적을 차지한다.
이번 2차는 보조 근거를 기본 접힘 섹션으로 바꿔 cockpit의 읽는 순서를 더 선명하게 만든다.

## Scope

- Render `Source Confidence / 출처 신뢰도` as a collapsed disclosure by default.
- Render `Overview Map / 화면 지도` as a collapsed disclosure by default.
- Keep status, detail, and boundary information available when expanded.
- Keep existing DB-backed models and refresh/action boundaries.

## Out Of Scope

- Refresh result UX detail.
- Scheduler / automation policy.
- New provider, schema, registry / saved JSONL writes.
- Validation / Final Review / monitoring / trading semantics.

## Steps

1. Add failing renderer/CSS contract tests for collapsible supporting sections.
2. Update `app/web/overview_ui_components.py` HTML/CSS only.
3. Run focused tests, compile, boundary check, diff check, and Browser QA.
4. Update task/root docs and commit.
