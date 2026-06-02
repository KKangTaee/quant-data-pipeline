# Notes

- 5차와 6차는 Selected Dashboard 내부 확장이며, 별도 top-level page는 만들지 않는다.
- 6차 preflight는 "투입 가능 승인"이 아니라 "투입 판단 전에 남은 blocker 확인"이다.
- 7차 후보 탐색은 append-only registry 원칙을 지키고, 통과 후보가 없으면 저장하지 않는다.
- Open Issues / Follow-up는 Final Decision V2 row에 저장된 `open_review_items`와 `paper_tracking_snapshot.review_triggers`를 읽는다. `monitoring_log_auto_write=False`로 고정한다.
- Deployment Readiness preflight는 `deployment_readiness_policy_snapshot`을 중심으로 Selected Dashboard의 기존 read-only evidence를 합쳐 status를 계산한다. 이 결과가 `READY`여도 live approval이 아니며, 현재 UI에는 주문 / 계좌 연결 / 자동 리밸런싱 action이 없다.
- 2026-06-01 fresh search 기준으로 non-GTAA 후보는 legacy current/proposal registry에만 있고, Practical Validation-passed Clean V2 source가 아니다. Final Review selection-only 정책상 저장하지 않는 것이 맞다.
