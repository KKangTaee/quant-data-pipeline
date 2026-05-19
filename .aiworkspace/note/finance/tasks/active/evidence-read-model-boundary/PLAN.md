# Evidence Read Model Boundary Plan

Status: Complete
Created: 2026-05-20

## 이걸 하는 이유?

Final Review와 Selected Portfolio Dashboard는 같은 최종 판단 row를 읽지만, evidence status / checks / display row 조립이 화면 helper 안에 흩어져 있다.
UI와 engine 경계를 더 분명히 하려면 최종 판단 evidence를 읽는 공통 read model을 Streamlit-free service로 두고, 각 화면은 그 결과를 렌더링만 해야 한다.

이 task는 새 화면이나 API를 만들지 않고, 최종 판단 row를 읽는 공통 evidence read model부터 분리한다.

## Scope

포함:

- Streamlit-free evidence read model service 생성
- Final Review saved decision status / table row 조립을 service로 이동
- Selected Dashboard evidence check row 조립을 service로 이동
- 화면 helper는 `pd.DataFrame` 변환과 UI-specific label/filter helper만 담당

제외:

- Final Review 저장 schema 변경
- Selected Dashboard write behavior 변경
- live approval / broker order / auto rebalance
- registry JSONL rewrite
- frontend framework 변경

## Done Criteria

- 새 service module이 Streamlit을 import하지 않는다.
- Final Review와 Selected Dashboard가 같은 service read model을 사용한다.
- Selected Dashboard는 read-only 정책을 유지한다.
- compile / import smoke / no-Streamlit check가 통과한다.
