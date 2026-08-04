# Inflation Policy Preparation Baseline UX Plan

State: active
Last Verified: 2026-08-04

## 이걸 하는 이유?

`다음 Core PCE 발표 전 준비표`는 현재 확률 대비 변화량만 표시해 사용자가
`+15.5%p`의 기준을 화면에서 찾을 수 없다. 현재 연말 순인상 경로의 구성과 합계를
같은 문맥에 표시해 표를 별도 계산 없이 읽을 수 있게 한다.

## Roadmap

1. 현재 비교 기준, 순변화 용어와 표시 정밀도를 React UI와 테스트에 반영한다.
2. production asset을 재빌드하고 실제 DB 화면 QA와 문서 closeout을 수행한다.

## 완료 조건

- 준비표 바로 위에서 재가속 기준과 연말 순인상 기준을 확인할 수 있다.
- 순인상 기준은 `1회 / 2회 / 3회 이상 / 합계`를 같은 정밀도로 표시한다.
- 변화량이 현재 기준 대비 `%p`라는 의미와 25bp 순변화 계약이 명확하다.
- 기존 확률 계산, DB payload와 정책 모델은 바뀌지 않는다.
- React 회귀, typecheck, build와 Browser QA가 통과한다.
