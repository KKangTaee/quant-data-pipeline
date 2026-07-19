# Status

Status: Complete

Completed:

- 3차 채권·금리: DGS2, DGS10, 10년-2년 금리차, DFII10, T10YIE 경로 연결
- 4차 주식: `^GSPC` 단일 대표지수와 DFII10, BAA10Y, VIXCLS, actual TTM EPS 경로 연결
- 5차 원자재: WTI·EIA 수급, 구리·달러·미국 활동, 기존 금 경로 연결
- 공통 UI: `현재 움직임 / 함께 관찰된 경로 / 현재 해석 / 향후 1·2개월 확인 조건`으로 통일
- Actual DB 적재, focused regression, TypeScript, production build, desktop/mobile Browser QA 완료

Actual coverage:

- 채권·금리: `SUFFICIENT`
- S&P 500: `PARTIAL` — 완료된 actual EPS 분기 8개가 없어 EPS 경로만 자료 부족
- 금: `SUFFICIENT`
- 달러: `PARTIAL` — 해외 상대금리 미연결
- 원자재: `PARTIAL` — 구리 활동 경로가 미국 지표에 한정

Next:

- actual S&P EPS 공식 완료 분기 자료가 적재되면 독립 EPS 경로를 재평가한다.
- 해외 상대금리와 구리의 승인된 글로벌 활동지표는 별도 범위로 남긴다.
