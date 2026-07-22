# Notes

- `select_item`은 read-only 선택인데도 Python bridge의 공통 event 경로를 타며 전체
  `runtime.rerun()`을 유발한다.
- 활성 그룹 lane은 모든 항목에 대해 이미 로드되므로 항목별 position projection은 추가
  lane 계산 없이 만들 수 있다.
- 직접 종목 차트는 기존 120행 제한을 재사용하며 그룹 활성 항목 한도는 10개다.

