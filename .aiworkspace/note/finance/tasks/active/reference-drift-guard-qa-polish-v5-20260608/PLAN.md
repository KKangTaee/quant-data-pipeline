# Reference Drift Guard / QA Polish V5 Plan

Status: Active
Date: 2026-06-08

## 이걸 하는 이유?

4차에서 주요 workflow 화면에 contextual Reference help를 붙였지만, catalog가 Glossary concept dictionary와 따로 움직이면 링크는 살아 있어도 화면 안내가 오래된 용어를 가리킬 수 있다.
5차는 Reference help를 더 넓히는 작업이 아니라, 이미 붙은 연결이 깨지지 않도록 Streamlit-free guard와 화면 표시 polish를 추가한다.

## Scope

- `app/services/reference_contextual_help.py`에 drift report를 추가한다.
- contextual help의 glossary term이 shared concept dictionary에 존재하는지 검사한다.
- contextual help의 link target이 Reference route boundary 안에 있는지 검사한다.
- Streamlit caption에서 raw `>`가 `&gt;`처럼 보이지 않도록 guide focus copy를 정리한다.
- focused tests, compile, boundary checker, Browser QA를 실행한다.

## Out Of Scope

- Reference query deep-linking
- Ingestion / Overview 전체 surface contextual help 확장
- Glossary markdown 전체 rewrite
- DB / registry / saved JSONL rewrite
- provider fetch, broker order, live approval, auto rebalance

## Completion Criteria

- drift report focused regression test가 통과한다.
- Reference contextual help renderer가 HTML escape 때문에 guide path를 어색하게 표시하지 않는다.
- Browser QA에서 Portfolio Monitoring contextual help가 정상 렌더된다.
- durable docs와 root handoff log가 5차 완료 상태를 가리킨다.
