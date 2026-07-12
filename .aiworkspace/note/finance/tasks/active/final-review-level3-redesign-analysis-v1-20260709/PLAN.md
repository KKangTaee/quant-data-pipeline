# Final Review Level3 Redesign Analysis V1

## Goal

Backtest 마지막 단계인 `Final Review / Level3`의 현재 코드, read model, 저장, 화면 흐름, Practical Validation REVIEW handoff, Portfolio Monitoring 연결 경계를 진단하고, 구현 전 단계별 개선 방향을 정리한다.

## 이걸 하는 이유?

Level2 Practical Validation은 Flow3 / Flow4 중심으로 정리되었지만, Level3 Final Review는 아직 gate / checklist 중심으로 보이며 사용자가 실제로 “이 포트폴리오를 모니터링 후보로 삼을 만한가”를 투자 검토서처럼 판단하기 어렵다. 구현 전에 Level3의 본질, REVIEW 처리 기준, 점수 체계, 화면 흐름, Python service 경계를 먼저 합의해야 한다.

## Scope

- 현재 Final Review 코드 / helper / service / runtime storage 경계 파악
- Practical Validation REVIEW role이 Level3에서 어떻게 소비되어야 하는지 기준 제안
- 최종 판단 기준 / 점수 체계 초안 제안
- 사용자 화면 흐름과 Python service / engine / storage 경계 제안
- 1차~6차 개발 로드맵과 이번 차수 범위 제안

## Out Of Scope

- 코드 구현
- registry / saved JSONL / run history / generated artifact 정리 또는 staging
- provider / DB / API fetch 경로 추가
- live approval, broker order, account sync, auto rebalance 의미 추가

## Stop Condition

사용자에게 현재 상태 진단, 문제점, 개선 방향, 단계별 개발 가이드라인, 진행 전 확인 질문을 제시하고 방향성 승인을 기다린다.
