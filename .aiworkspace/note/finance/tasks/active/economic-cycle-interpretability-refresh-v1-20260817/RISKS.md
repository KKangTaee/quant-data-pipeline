# Risks

- RTDSM provider downloads remain external I/O and can be slow or unavailable; the UI must fail closed and retain last-good current snapshots.
- Existing legacy intramonth automation is out of the manual official-state path; removing or migrating that scheduled job is not required for this screen task unless tests show it still mutates the official current snapshot.
- Asset `economic_state` continues to use the established pathway interpretation contract. It is presented once and must not be relabeled as the exact RTDSM state evidence.
- Direction colors for rates and spreads can be mistaken for favorable/unfavorable signals; the UI requires a persistent direction-only legend.

## Closeout

- Philadelphia Fed 외부 응답 시간 때문에 수동 공식 갱신은 실제 QA에서 약 45초가 걸렸다. 화면 로딩은 결과 수신 시 정상 해제되며 실패 시 last-good snapshot을 유지한다.
- `source_collected_at`이 없는 기존 current row는 재접속 후 `마지막 성공 수집`이 `기록 없음`일 수 있다. 현재 세션의 성공 결과에는 완료시각을 우선 표시한다.
- 기존 intramonth 자동화 제거는 이번 승인 범위가 아니므로 별도 운영 정리 과제로 남긴다.
