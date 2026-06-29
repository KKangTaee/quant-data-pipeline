# Plan

## 이걸 하는 이유?

`Overview > Market Context`의 `참고: 과거 유사 맥락`은 현재 시장 흐름과 비슷했던 과거 구간의 이후 분포를 보여주지만, 기존 UI는 제목과 표가 바로 이어져 사용자가 "무엇을 기준으로 찾았고 어떻게 읽어야 하는지"를 먼저 이해하기 어려웠다.

이번 작업은 계산 로직을 바꾸지 않고, 자료가 충분한 상태에서 유사맥락을 정의 -> 핵심 해석 -> 상세 표 순서로 읽게 만드는 UX 1차~3차 개선이다.

## Scope

- `app/web/overview_ui_components.py`
  - 유사맥락 설명 문장 추가
  - 핵심 요약 수치 strip 추가
  - 핵심 자산 / 보조 자산 표 분리
- `tests/test_service_contracts.py`
  - HTML 순서와 CSS class 계약 추가
- 문서 closeout
  - roadmap / task manifest / root handoff log 최소 정렬

## Out Of Scope

- Historical analog 계산식 변경
- Macro / futures / event 조건 확장
- 과거 anchor date 목록 drill-down
- 새 provider / DB schema / loader 추가
- registry / saved JSONL write
- prediction, recommendation, validation gate, monitoring signal, trading action
