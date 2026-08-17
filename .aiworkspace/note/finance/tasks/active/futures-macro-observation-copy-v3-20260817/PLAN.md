# Futures Macro Observation Copy V3 Plan

State: active
Last Updated: 2026-08-17

## 이걸 하는 이유?

현재 1D·5D·20D 카드는 계산 결과를 보여주지만 `기존 방향 지속:`처럼 축약돼 있어,
사용자가 무엇이 변했고 그 변화가 전체 방향에서 어떤 의미인지 다시 해석해야 한다.

## 목표

- 중복된 `현재 관측 · 1D/5D/20D` 라벨을 제거한다.
- 각 카드를 `관측된 변화`와 `전체 의미 또는 한계`의 두 문장으로 만든다.
- 숫자 임계값이나 방법론 설명을 본문에 추가하지 않는다.

## 실행 단계

1. 문장별 회귀 테스트를 추가하고 기존 축약형 출력에서 실패를 확인한다.
2. Python의 결정적 narrative 생성기와 React 카드 마크업을 수정한다.
3. focused test, production build, 실제 화면과 모바일 폭 QA를 수행한다.

## 범위

- `app/web/overview/futures_macro_helpers.py`
- `app/web/streamlit_components/futures_macro_workbench/src/ShortHorizonDecisionSection.tsx`
- 관련 component CSS와 short-horizon tests

## 완료 조건

- 세 카드가 제목 아래 결과 문장만 표시한다.
- 단일 축, 정렬, 엇갈림, 지속, 반전, 관계 없음이 각각 두 문장으로 설명된다.
- 관련 Python tests, TypeScript build, Browser QA가 통과한다.
