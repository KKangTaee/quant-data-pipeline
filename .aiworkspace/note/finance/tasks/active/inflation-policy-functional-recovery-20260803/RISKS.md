# Inflation Policy Functional Recovery Risks

- FOMC decision history는 current calendar와 2016~2020 historical material에서 공식
  rate decision 86건으로 복구됐다. 향후 calendar DOM, historical SEP compilation 링크나
  target-range/vote 문구가 바뀌면 parser 회귀 테스트와 official-page smoke를 함께 갱신한다.
- 12월 SEP와 동시 발표된 연말 결정은 검증 origin이 아니다. 이 strict horizon 조건을
  제거하면 정책 artifact가 다시 결과 누수로 READY가 될 수 있다.
- unsupported rate statement를 non-rate statement로 간주해 skip하면 다음 회의의
  before-range와 label이 함께 오염된다. nonmeeting panel만 discovery에서 제외하고 회의
  statement parser 오류는 반드시 수집 실패로 남긴다.
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
