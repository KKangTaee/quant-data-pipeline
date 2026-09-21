# Risks

- Provider가 최신 데이터를 반환하지 않으면 부분 성공 또는 미완료로 남아야 한다.
- 현재 freshness 정책은 일별 5영업일, 주별 14일의 허용 지연을 사용한다.
  이 수정은 기존 정책을 변경하지 않는다.
- 오래된 intramonth freshness 테스트의 baseline 실패 2개는 승인된 월간 계약으로
  정렬해 해소했다. 이전 nowcast 운영 문서의 전면 정리는 이번 범위가 아니다.
- 실제 source 수집과 화면 반영을 검증했다. 전체 저장소 테스트는 이 두 호출의
  날짜 수정 범위를 넘어가므로 실행하지 않았으며, 직접 관련된 107개를 검증했다.
- RTDSM snapshot의 source_collected_at은 기존 null이다. 현재 세션에서 asset
  성공 수집 시각은 UI result로 표시되지만, 영구 수집시각 표시 방식은 변경하지 않았다.
