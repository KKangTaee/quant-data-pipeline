# Portfolio Monitoring Latest Decision Lifecycle V1 Status

Status: Complete
Updated: 2026-07-23

## Roadmap

- 1/4 Design and current-state diagnosis: complete
- 2/4 Service/catalog/replay lifecycle: complete
- 3/4 User action UI and routing: complete
- 4/4 Verification and documentation: complete

## Outcome

- 사용자 승인 방식은 `최신 판단을 current truth로 사용하고 기존 Monitoring 항목은 삭제하지 않은 채 실행 잠금`이다.
- 후보별 최신 Final Review row만 신규 catalog에 반영하고, 기존 selected-strategy item은 requested decision과 latest effective decision을 함께 보존한다.
- 최신 non-select 판단은 해당 item의 새 replay/Scenario만 잠근다. 다른 정상 item은 계속 계산한다.
- `최신 판단 재확인`은 서버가 최신 source를 다시 확인한 뒤 Final Review로 이동하며, 계속 추적은 새 selected 판단으로만 해제한다. 종료는 기존 `추적 종료` 명령을 사용한다.

## Verification

- Focused Python lifecycle/catalog/replay/read-model/dashboard command tests: pass.
- Portfolio Monitoring React tests `34 passed`; TypeScript typecheck와 production build: pass.
- Actual registry read-only probe: 6 subjects / 6 latest selected. Synthetic old-selected + latest-hold는 catalog 제외와 `TRACKING_ELIGIBILITY_CHANGED`, item-local lock을 확인했다.
- Actual `/selected-portfolio-dashboard`: desktop 1440px와 760px에서 horizontal overflow 0, browser error 0, 정상 item action을 확인했다.
- Broad `tests/test_service_contracts.py`는 현재 `18 failed, 957 passed`이며 implementation 직전 commit에서도 동일 18개가 실패했다. 이 task가 추가한 회귀가 아니라 기존 Practical Validation/Sentiment/Final Review/Futures 계약 drift로 분리한다.
