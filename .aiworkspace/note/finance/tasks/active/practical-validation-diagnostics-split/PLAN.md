# Practical Validation Diagnostics Split Plan

Status: Active
Created: 2026-05-27

## 이걸 하는 이유?

`app/services/backtest_practical_validation_diagnostics.py`는 Practical Validation의 source 생성, profile 해석, curve context, stress / sensitivity, final result assembly를 모두 담고 있다.
이 파일이 커질수록 UI와 engine 경계는 유지되더라도, service 내부에서 어떤 책임을 고쳐야 하는지 찾기 어려워진다.

이 task는 계산 결과를 바꾸지 않고 diagnostics service를 helper family 단위로 나눈다.
첫 단계는 가장 안전한 source/profile builder 분리였고, 두 번째 단계는 shared curve context helper 분리였다.
세 번째 단계는 rolling / stress / baseline / sensitivity evidence helper 분리다.

## Scope

포함한다.

- `7-01`: validation profile / selection source builder 분리
- 이후 후보:
  - `7-02`: curve context helper 분리
  - `7-03`: stress / sensitivity evidence helper 분리
  - `7-04`: orchestration import / public contract 정리

포함하지 않는다.

- Practical Validation 결과 schema 변경
- diagnostic status / score 계산 변경
- provider loader / ingestion 변경
- Streamlit 화면 변경
- registry / saved JSONL 변경

## Done Criteria For 7-01

- source/profile builder가 별도 Streamlit-free service module에 있다.
- 기존 import 경로가 크게 깨지지 않도록 diagnostics module에서도 public builder가 계속 노출된다.
- service contract tests가 통과한다.
- boundary lint가 통과한다.
- browser QA가 필요한지 판단이 기록된다.

## Done Criteria For 7-02

- compact curve snapshot / curve normalize / DB price proxy / component curve combine helper가 별도 Streamlit-free service module에 있다.
- Compare와 Candidate Review는 diagnostics가 아니라 curve context helper에서 compact snapshot 함수를 직접 import한다.
- diagnostics orchestration은 기존 public compatibility를 유지한다.
- service contract tests와 boundary lint가 통과한다.
- browser QA가 필요한지 판단이 기록된다.

## Done Criteria For 7-03

- rolling / stress / baseline / sensitivity / correlation / market context / overfit audit helper가 별도 Streamlit-free service module에 있다.
- diagnostics service는 12개 diagnostic assembly와 component context orchestration에 집중한다.
- service import smoke test가 새 helper module을 포함한다.
- service contract tests와 boundary lint가 통과한다.
- browser QA가 필요한지 판단이 기록된다.
