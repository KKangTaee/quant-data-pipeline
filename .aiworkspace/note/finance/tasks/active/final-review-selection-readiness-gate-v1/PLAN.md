# Final Review Selection Readiness Gate V1

## Goal

Final Review를 live 투입 전 감사 checklist가 아니라, 검증 근거를 바탕으로 Selected Portfolio Dashboard에서 추적할 최종 후보를 선정하는 decision-readiness gate로 재정렬한다.

## 이걸 하는 이유?

현재 selected-route gate는 `REVIEW` 항목 대부분을 선정 차단으로 해석해, Practical Validation을 통과한 후보도 Final Review에서 거의 저장되지 않는다. 사용자가 원하는 최종 질문인 "진짜 실제 돈을 넣어도 되는가"는 별도 Live / Deployment Readiness 단계로 다뤄야 하며, Final Review는 후보 선정과 추적 조건을 명확히 남기는 단계여야 한다.

## Scope

- High / Medium / Low 약점 리뷰와 gate matrix를 task 문서에 남긴다.
- weighted mix selection source의 role / weight rationale evidence mapping을 보강한다.
- Final Review selected-route gate를 `selection_readiness` 기준으로 분리한다.
- 기존 엄격한 live/deployment 성격의 policy는 `deployment_readiness_policy_snapshot`으로 보존한다.
- selected decision row에 open review items를 compact하게 저장한다.

## Out Of Scope

- broker/account 연결, 주문, 자동 리밸런싱, live approval.
- 새 DB schema, provider/FRED 직접 fetch.
- Live / Deployment Readiness 전체 화면 구현.
- 기존 registry rewrite.
