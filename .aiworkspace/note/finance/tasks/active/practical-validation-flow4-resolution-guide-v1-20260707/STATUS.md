# Practical Validation Flow 4 Resolution Guide V1

Status: Complete
Date: 2026-07-07

## Why

Flow 4의 기존 `보강 위치`는 사용자가 이동할 화면 이름만 알려줬다. 일부 위치는 실제 탭 / expander와 맞지 않았고, 위치만으로는 무엇을 검증했고 무엇이 부족하며 어떤 조치를 해야 하는지 판단하기 어려웠다.

## Done

- Flow 4 criteria card에 `resolution_guide` contract를 추가했다.
- 각 기준 상세를 `검증한 것 / 부족한 것 또는 확인할 것 / 해야 할 일 / 확인 위치`로 렌더링한다.
- Data Coverage, Validation Efficacy, Realism, Construction, Risk Contribution, Component Role / Weight 같은 audit row 기반 기준은 non-PASS `Criteria`와 `Next Action`을 우선 사용한다.
- 사용자-facing 위치를 실제 화면 경로 기준으로 세분화했다.
  - `Flow4 > 데이터 > 데이터 품질 / 편향 통제 상세`
  - `Flow4 > Provider / Data 보강 액션`
  - `Flow4 > 구성 / 리스크 > 위험 기여 상세`
  - `Flow4 > 실전성 > 검증 강도 / 강건성 상세`
- Flow 3 결론, Final Review gate, provider 수집 로직, registry / saved JSONL write 경계는 바꾸지 않았다.

## Not Changed

- validation threshold / gate policy
- replay execution logic
- provider ingestion orchestration
- Practical Validation result registry schema rewrite
- Final Review selected-route policy
- live approval / broker order / auto rebalance boundary
