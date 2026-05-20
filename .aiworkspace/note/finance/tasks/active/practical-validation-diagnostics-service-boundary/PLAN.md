# Practical Validation Diagnostics Service Boundary Plan

Status: Complete
Created: 2026-05-20

## 이걸 하는 이유?

Practical Validation의 12개 diagnostic 계산과 validation profile 해석은 화면 렌더링이 아니라 엔진 / 서비스 성격의 로직이다.
이 로직이 `app/web`에 남아 있으면 UI가 바뀌어도 재사용하기 어렵고, service가 web helper를 import하는 역방향 경계가 유지된다.

## Scope

- `app/web/backtest_practical_validation_helpers.py`의 Streamlit-free diagnostic helper를 service module로 이동한다.
- 기존 UI import는 service boundary를 통해 이어지도록 갱신한다.
- service import가 Streamlit을 로드하지 않는 contract test를 보강한다.
- project map / script map / flow 문서를 현재 위치에 맞춘다.

## Non-Scope

- diagnostic 계산식 자체 변경
- provider connector / curve helper 분리
- registry schema 변경
- Streamlit 화면 UX 변경

## Completion Criteria

- Diagnostics helper lives under `app/services`.
- Code imports reference the new service module.
- Focused service contract tests pass without loading Streamlit.
- Boundary lint passes with only transitional advisory warnings.
