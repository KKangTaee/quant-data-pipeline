# Notes

- 공식 S&P 500 페이지는 `Index Earnings` XLSX 링크를 제공한다.
- 자동 curl과 browser download event는 403/timeout으로 파일을 받지 못했다.
- 접근 제한은 우회하지 않고 사용자가 내려받은 공식 파일을 등록하는 제품 흐름을 사용한다.
- 기존 normalized workbook 계약은 하위 호환으로 유지한다.
- Wayback 보존본 `2026-05-27` workbook으로 실제 sheet 구조를 확인했다. sheet 목록은 `ESTIMATES&PEs`, `SECTOR EPS`, `QUARTERLY DATA`, `SALES`, `BEATS AND SHARES`, `FORWARD SCHEDULE`다.
- 공식 `QUARTERLY DATA`는 별도 status 열 대신 sheet title과 `QUARTER END / OPERATING EARNINGS PER SHR / AS REPORTED EARNINGS PER SHR` 다단 머리글을 사용한다. 값이 비어 있는 최신 미완료 분기는 저장하지 않는다.
- 보존본은 parser 구조 QA에만 사용했고 DB canonical 자료로 적재하지 않았다.
