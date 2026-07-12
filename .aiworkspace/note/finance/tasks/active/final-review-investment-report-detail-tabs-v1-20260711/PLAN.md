# Final Review Investment Report Detail Tabs V1 Plan

## 이걸 하는 이유?

Final Review 투자 검토서의 first-read는 평면화됐지만, 하단 상세 영역은 `details` expander가 5개 세로로 쌓여 다시 긴 목록처럼 보인다. 사용자는 `근거 상세`, `저장 경계`, `개선 후보`, `Review 처리`, `Monitoring` 중 하나를 선택해 하단 내용만 바꿔 보는 편이 더 빠르게 탐색할 수 있다.

## Scope

- 1차: React source contract를 expander에서 tabs로 바꾸는 RED test 작성
- 2차: React `DetailTabs` 구조 구현
- 3차: CSS tab bar / active panel visual 정리와 build / tests
- 4차: Browser QA, docs sync, commit

## Out Of Scope

- Python score / gate / route / save / handoff 계산 변경
- Provider / DB fetch, registry / saved JSONL, run history write
- 새 투자 근거 생성, 개선 portfolio 자동 생성
- live approval, broker order, auto rebalance

## Checklist

- [x] 1차 RED contract
- [x] 2차 React detail tabs
- [x] 3차 CSS / build / tests
- [x] 4차 Browser QA / docs / commit
