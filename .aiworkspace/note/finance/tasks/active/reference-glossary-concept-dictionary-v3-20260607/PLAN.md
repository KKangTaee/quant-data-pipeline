# Reference Glossary / Concept Dictionary V3 2026-06-07

Status: Completed

## Goal

`Reference > Guides`의 상태 / 용어 lookup과 `Reference > Glossary`를 같은 Streamlit-free concept dictionary로 통합한다.

## 이걸 하는 이유?

1차는 Reference Center를 만들었고, 2차는 journey / playbook detail을 확장했다.
하지만 `Guides`의 concept rows와 `Glossary` page가 서로 다른 구현에서 관리되어 용어 설명이 drift될 수 있다.
3차는 사용자가 `NOT_RUN`, `BLOCKED`, `Provider Coverage`, `Portfolio Monitoring Scenario` 같은 핵심 용어를 Guides와 Glossary 어디서 검색해도 같은 의미와 owner screen을 보게 만든다.

## Scope

- 새 Streamlit-free glossary / concept catalog service를 만든다.
- `Guides` status lookup이 새 concept dictionary를 사용하게 한다.
- `Glossary` page가 기존 `GLOSSARY.md` sections와 curated concept dictionary를 함께 검색 / 표시하게 한다.
- Contract tests로 Streamlit-free import, curated concept shape, search behavior를 고정한다.
- Reference docs와 task/root handoff를 동기화한다.

## Out Of Scope

- `GLOSSARY.md` 본문 전체 rewrite.
- 타 화면에서 Reference contextual link 연결. 이는 4차 범위다.
- DB / registry / saved setup / provider fetch / job 실행 / live trading action.

## Completion Criteria

- RED -> GREEN catalog tests가 통과한다.
- `Guides`와 `Glossary`가 같은 curated concept dictionary를 사용한다.
- Browser QA에서 `Glossary`가 curated concept table과 durable `GLOSSARY.md` section을 함께 표시한다.
- Search behavior는 Streamlit-free unit test로 고정한다.
- Full focused verification, UI boundary check, Browser QA render check가 통과한다.
