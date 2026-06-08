# Reference Contextual Links V4 2026-06-08

Status: In Progress

## Goal

주요 업무 화면에서 사용자가 막혔을 때 `Reference > Guides`와 `Reference > Glossary`로 바로 이어지는 read-only contextual help를 제공한다.

## 이걸 하는 이유?

1차는 task-first Reference Center를 만들었고, 2차는 journey / playbook을 확장했으며, 3차는 Guides와 Glossary의 운영 용어 사전을 통합했다.
하지만 사용자는 Backtest Analysis, Practical Validation, Final Review, Portfolio Monitoring 같은 실제 작업 화면에서 막혔을 때 Reference 탭을 직접 찾아가야 한다.
4차는 각 owner screen의 맥락 안에서 필요한 Reference entry point를 노출해 사용자가 현재 화면에서 다음 확인 위치를 바로 찾게 만든다.

## Scope

- Streamlit-free contextual help catalog service를 만든다.
- 얇은 Streamlit render helper로 화면별 접힌 Reference help expander를 표시한다.
- 1차 연결 화면은 Backtest Analysis, Practical Validation, Final Review, Operations Console, Operations > Portfolio Monitoring으로 제한한다.
- Contract tests로 service shape, Streamlit-free import, Reference-only link boundary를 고정한다.
- 관련 durable docs와 task/root handoff를 동기화한다.

## Out Of Scope

- `GLOSSARY.md` 전체 rewrite.
- Reference 검색 URL query deep-linking.
- Ingestion / Overview 전체 surface 연결.
- DB / registry / saved setup / provider fetch / job 실행 / live approval / broker order / auto rebalance.

## Completion Criteria

- RED -> GREEN contextual help tests가 통과한다.
- 주요 화면에 read-only Reference help expander가 표시된다.
- Browser QA에서 최소 한 Backtest 화면과 Portfolio Monitoring 화면에서 helper가 보인다.
- Focused verification, compile, UI boundary, `git diff --check`가 통과한다.
