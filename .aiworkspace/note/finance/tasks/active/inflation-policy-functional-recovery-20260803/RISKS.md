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
- FactSet archive 103개 중 23개는 차트 page/두 CY 라벨/구조 검증 실패로 제외됐다. collector의
  partial health를 모델 source coverage와 혼동하지 않으며, parser 기준을 낮추거나 OCR
  숫자를 수동 추정해 채우지 않는다.
- FactSet 연간 bottom-up estimate는 날짜가 검증된 analyst estimate source이지 S&P 공식
  actual EPS가 아니다. source/basis를 유지하고 Market Context actual TTM과 섞지 않는다.
- joint rate path를 25bp policy move와 10년물 25bp로 기계 매핑하면 사용자의 원래
  분석 취지와 데이터 의미를 모두 훼손한다.
- 기존 task/phase의 `complete` 상태는 구현 파일 존재를 뜻했지만 실제 사용 가능성을
  과장했다. 4차는 actual DB·validation·command·Browser evidence가 모두 생긴 뒤에만
  다시 완료로 정렬했다.
- worktree의 사용자 registry 수정과 untracked artifact를 커밋하지 않는다.
- `USREC`은 NBER outcome label이며 현재 feature가 아니다. label delay 24개월을 제거하거나
  기존 경제 사이클 확률을 혼합하면 독립성과 시점 계약이 깨진다.
- 미개정 일별 시장 series만 observation-date EOD anchor를 쓴다. 월간/분기 수정 series에
  같은 anchor를 적용하면 미래 revision을 과거에 보게 된다.
- equity ridge strength는 outer evaluation 결과로 직접 고르지 않는다. 후보나 inner-fold
  규칙을 바꿀 때는 nested chronological validation 전체를 다시 실행한다.
- 공식 BAML OAS history가 현재 2023-08 이후로 제한되므로 과거 fold에서는 결측이다.
  제3자 값으로 소급 채우지 않고 current completeness와 OOS gate를 계속 확인한다.
