# Final Review Level3 React V2-V6

## Goal

Backtest `Final Review / Level3`를 Gate / checklist 중심 화면에서 사람이 읽는 최종 투자 검토서형 workflow로 개선한다.

## 이걸 하는 이유?

1차에서 Final Review 판단 record와 Portfolio Monitoring handoff 저장 경계는 분리되었다. 하지만 사용자는 아직 최종 판단 요약, 강점 / 약점, Level2 REVIEW 처리 결과, 점수, 모니터링 조건, 약점 개선 가능성을 한 화면에서 읽기 어렵다. Level3는 실제 투입 전 마지막 선별 단계이므로, Python service가 판단 read model을 만들고 React가 이를 명확한 검토서 UI로 표시해야 한다.

## Roadmap

| 차수 | 목적 | 개발 범위 | 완료 조건 |
|---|---|---|---|
| 2차 | Final Review 투자 검토서 기본 화면 | Python decision report read model + React report component + Final Review page 배치 | 선택 후보에 대해 최종 판단 요약 / 핵심 이유 / 강점 / 약점 / 다음 행동이 React 화면으로 보인다 |
| 3차 | Level2 REVIEW 처리 summary | Practical Validation REVIEW role을 Final Review disposition으로 번역 | blocker / warning / open review / monitoring follow-up이 구분되어 보인다 |
| 4차 | 점수 / 추천 체계 | score band, recommendation, route guide를 service contract로 정리 | 추천 / 보류 / 탈락 / 모니터링 후보 판단 기준이 일관되게 보인다 |
| 5차 | 저장 / 선정 / Monitoring handoff UX | judgment record 저장과 Monitoring 후보 handoff의 visible boundary 정리 | 사용자가 저장 결과와 Monitoring 연결 조건을 혼동하지 않는다 |
| 6차 | 약점 개선안 최소 기능 | 약점별 개선 candidate action과 current-vs-improved expectation summary | 전략 생성 없이도 어떤 약점을 어떻게 줄일지 검토할 수 있다 |

각 차수는 `개발 -> QA -> 커밋` 순서로 닫는다.

## Boundaries

- React는 presentation과 click intent만 담당한다.
- Python service/read model이 score, recommendation, REVIEW disposition, weakness improvement proposal, 저장 readiness를 만든다.
- Final Review page/helper가 session state와 store append를 소유한다.
- provider / DB / API fetch, registry rewrite, saved JSONL cleanup, live approval, broker order, account sync, auto rebalance는 이번 범위가 아니다.
- registry / saved JSONL / run history / generated artifact는 명시 요청 없이는 stage하지 않는다.

## Verification

- Targeted Python service contract tests.
- React source / build checks for new component.
- `py_compile` for touched Python files.
- `git diff --check`.
- Browser QA for Final Review screen with screenshot artifact.
