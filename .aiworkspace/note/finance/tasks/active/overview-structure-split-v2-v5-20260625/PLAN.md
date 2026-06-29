# Overview Structure Split V2-V5 Plan

## 이걸 하는 이유?

V1에서 `Workspace > Overview`의 active page shell과 primary tab entrypoint를 `app/web/overview/` package로 옮겼지만, 탭 내부 orchestration과 component / service import surface는 아직 legacy 경계에 남아 있다. V2-V5는 사용자가 자는 동안 차수별 QA를 거치며 UI 노출과 엔진/read-model 경계를 더 선명하게 만든다.

## Roadmap

1. V2: primary tab modules가 tab-level orchestration을 소유한다. Legacy `_render_*_tab()` 직접 위임을 제거하고, 필요한 legacy helper 호출만 남긴다.
2. V3: overview visual component import surface를 `app/web/overview/components/` 아래 domain module로 분리한다.
3. V4: overview service/read-model import surface를 `app/services/overview/` 아래 domain module로 분리한다.
4. V5: Streamlit-free service, component import purity, web/job/data boundary guard tests를 강화한다.

## Out Of Scope

- 계산 로직 변경
- provider / DB schema / registry / saved JSONL 변경
- UI 디자인 변경
- trading signal / validation gate / monitoring signal / broker order / auto rebalance semantics 추가
