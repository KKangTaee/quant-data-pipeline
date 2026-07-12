# Design

## Overall Shape

Final Review의 first-read surface는 `Final Review Investment Report`다.

Python service는 기존 investability packet, selection gate snapshot, open review items, saved decision context를 읽어 JSON-friendly report payload를 만든다. React component는 이 payload를 읽어 투자 검토서처럼 렌더링한다.

## Report Sections

- 최종 판단 요약: recommendation, score, route, monitoring handoff eligibility.
- 핵심 이유: why this decision, strongest evidence, weakest constraint.
- 강점: performance, benchmark, robustness, construction, data confidence.
- 약점: missing / stale / review-required evidence, gross-only / cost gap, mix construction gap.
- Level2 REVIEW 처리 결과: blocker, warning, open review, monitoring follow-up.
- Monitoring 조건: tracking trigger, recheck condition, handoff status.
- 약점 개선안: current weakness, proposed mitigation, expected effect, verification step.

## Stage Ownership

- Level2 REVIEW는 Level3에서 다시 실행하지 않는다.
- `final_readiness_blocker`와 selected-route hard blocker는 Level3 blocker다.
- `pv_data_caution` / `pv_practical_caution`은 최종 판단 warning이다.
- `final_decision_input`은 Final Review open review item이다.
- `monitoring_followup`은 Monitoring 추적 조건이다.

## UX Intent

첫 화면은 raw table이 아니라 사용자가 결론을 읽고 다음 행동을 결정하는 검토서다. Raw evidence는 기존 Evidence Appendix와 saved ledger에 남기고, React report는 요약 / 판단 / 행동 조건 중심으로 표시한다.
