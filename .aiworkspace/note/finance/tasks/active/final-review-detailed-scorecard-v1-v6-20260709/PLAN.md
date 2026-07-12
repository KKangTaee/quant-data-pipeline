# Final Review Detailed Scorecard V1-V6 Plan

## 이걸 하는 이유?

현재 Final Review 점수는 `Selection Gate`, `Evidence Packet`, `Review Burden` 중심이라 선정 준비도는 볼 수 있지만, 사용자가 최종 포트폴리오를 고를 때 필요한 투자 매력도 / 리스크 / 근거 신뢰도 / Monitoring 적합성이 충분히 분리되지 않는다.

이번 작업은 종합점수를 유지하되 세부 점수와 감점 이유를 분리해, 사용자가 `추천 / 보류 / 탈락 / Monitoring 후보` 판단을 더 신뢰할 수 있게 만드는 것이 목적이다.

## 전체 범위

- 1차: Python detailed scorecard read model.
- 2차: React score breakdown UI.
- 3차: Level2 REVIEW impact mapping.
- 4차: score cap / route decision 정교화.
- 5차: Final Review selection rationale surface.
- 6차: integration QA, Browser QA, durable docs sync.

## 유지할 경계

- React는 presentation / UI event만 담당한다.
- score, classification, cap, route, rationale 계산은 Python service가 담당한다.
- provider / FRED / DB fetch, validation rerun, registry / saved write는 추가하지 않는다.
- Final Review와 Portfolio Monitoring은 live approval, broker order, auto rebalance가 아니다.
- `.aiworkspace/note/finance/registries/`, `.aiworkspace/note/finance/saved/`, run history, generated QA artifact는 명시 요청 없이 stage하지 않는다.

## 1차 - Detailed Scorecard Read Model

- 목적: 기존 단순 scorecard를 `overall + dimensions + drivers + limits` 구조로 확장한다.
- 변경 파일: `app/services/backtest_evidence_read_model.py`, `tests/test_service_contracts.py`.
- 완료 조건: service contract가 `Investment / Risk / Readiness / Evidence Quality / Monitoring Suitability` 5개 dimension과 weighted overall을 검증한다.

## 2차 - React Score Breakdown UI

- 목적: Final Review 투자 검토서에서 세부 점수와 주요 가산 / 감점 이유를 읽을 수 있게 한다.
- 변경 파일: `app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx`, `style.css`, build assets, tests.
- 완료 조건: React source / build가 `세부 점수`, `점수 영향`, `점수 제한`을 렌더링한다.

## 3차 - Level2 REVIEW Impact Mapping

- 목적: Level2 REVIEW를 단순 count 감점이 아니라 점수 축별 영향으로 연결한다.
- 변경 파일: `app/services/backtest_evidence_read_model.py`, React component, tests.
- 완료 조건: `pv_data_caution`, `pv_practical_caution`, `final_decision_input`, `monitoring_followup`, `final_readiness_blocker`가 각각 Evidence / Risk / Investment / Monitoring / Readiness 축에 반영된다.

## 4차 - Score Cap / Route Decision Refinement

- 목적: blocker와 open review 과다 상태가 높은 점수로 오해되지 않게 cap과 route를 정교화한다.
- 변경 파일: `app/services/backtest_evidence_read_model.py`, tests.
- 완료 조건: hard blocker, selected-route gate 미통과, critical open review, open review 과다에 따른 cap / route가 검증된다.

## 5차 - Selection Rationale Surface

- 목적: 사용자가 왜 추천 / 보류 / 탈락 / Monitoring 후보인지 한 문단으로 읽고 Final Review 판단 저장을 선택할 수 있게 한다.
- 변경 파일: Python report payload, React report, Streamlit fallback, tests.
- 완료 조건: report에 `selection_rationale`와 `required_final_decision_notes`가 포함되고 UI가 표시한다.

## 6차 - Integration QA / Docs Sync

- 목적: 1차~5차 통합 검증, Browser QA 캡처, durable docs와 root handoff log를 갱신한다.
- 변경 파일: task docs, `.aiworkspace/note/finance/docs/ROADMAP.md`, `PROJECT_MAP.md`, flow docs, root logs.
- 완료 조건: focused Python tests, React build, py_compile, diff check, Browser QA가 통과하고 커밋이 생성된다.
