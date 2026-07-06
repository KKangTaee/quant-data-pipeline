# Practical Validation Flow 4 Labels V1

Status: Complete
Date: 2026-07-06

## Why

Flow 4의 사용자-facing 이름과 `보강 위치`가 `근거 Workbench`, `Flow 4 · Data Coverage Audit / Provider Data Gaps`처럼 화면 이름과 내부 audit taxonomy를 섞어 보여줬다. 사용자는 어디를 봐서 무엇을 보강해야 하는지 바로 알기 어렵기 때문에 Flow 4를 화면 기준 언어로 정리했다.

## Done

- Flow 4 section title을 `근거 Workbench`에서 `검증 기준 상세`으로 변경했다.
- 카테고리 제목을 더 굵고 크게 보이게 하고, category head에 구분선을 추가했다.
- `보강 위치`를 `검증 기준 상세 · 데이터 품질 / Provider 보강`, `검증 기준 상세 · 검증 강도 / 강건성`, `Flow 2 · 실전 재검증 실행`처럼 사용자가 찾을 수 있는 위치명으로 통일했다.
- Flow 4 상세 evidence expander / provider gap heading도 한국어 사용자-facing 제목으로 정리했다.
- Durable flow docs와 boundary tests를 새 Flow 4 이름에 맞췄다.

## Not Changed

- validation threshold / gate policy
- replay execution logic
- provider collection logic
- registry / saved JSONL write behavior
- Final Review selected-route policy
- live approval / broker order / auto rebalance boundary

