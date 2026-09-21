# Notes

- 사용자 승인: 전월 말 월간 판단 유지, 자산별 확인 포인트 최신화.
- 2026-09-21 read-only DB 조사: 공식 snapshot `2026-08-31`, updated_at
  `2026-09-01 08:26:19`. 자산 자료는 08-31 기준 READY, 09-21 기준 15개 stale.
- UI는 오늘 기준 REFRESH_AVAILABLE, command는 target(08-31) 기준 READY여서
  버튼을 눌러도 수집 없이 성공 메시지를 반환했다.
- 기존 screenshot 4개 untracked 파일은 사용자 산출물로 보존한다.
- 실제 checkout은 `master`; 실행 중인 앱과 같은 checkout에서 승인된 수정을 적용한다.
- 독립 리뷰에서 신규 테스트의 `None` 입력이 실제 실행 월에 의존함을 지적했다.
  `overview_actions.date`와 `economic_cycle_freshness.date`를 함께 고정해 해결했다.
- 실제 갱신 후 S&P 가격 09-18, FRED 09-17~18, EIA 주간 09-11,
  선물·달러 provider daily row 09-20. 수집 날짜와 관측 날짜는 다르다.
- 정상 월간 국면의 headline/점수/전환확률을 재학습하거나 재발행하지 않았다.
- canonical doc change 없음. Root handoff/manifest/Roadmap의 우선순위 변경도 없다.
