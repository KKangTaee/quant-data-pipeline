# Inflation Policy Functional Recovery Risks

- FOMC decision history를 statement index 최신 페이지만 읽으면 policy validation 표본이
  계속 부족하다. 공식 historical release URL backfill이 필요하다.
- Philadelphia Fed SPF 확률분포는 Q4/Q4 survey benchmark이지 월별 Core PCE nowcast의
  대체물이 아니다. horizon을 섞지 않는다.
- current official S&P workbook를 과거 origin에 복제하면 forward EPS PIT가 조작된다.
- free/public source가 historical consensus vintage를 제공하지 않으면 equity READY를
  만들기 위해 trailing EPS나 현재 estimate로 우회하지 않는다.
- joint rate path를 25bp policy move와 10년물 25bp로 기계 매핑하면 사용자의 원래
  분석 취지와 데이터 의미를 모두 훼손한다.
- 기존 task/phase의 `complete` 상태는 구현 파일 존재를 뜻했지만 실제 사용 가능성을
  과장한다. recovery 진행에 맞춰 2~4차를 재개 상태로 정렬해야 한다.
- worktree의 사용자 registry 수정과 untracked artifact를 커밋하지 않는다.
