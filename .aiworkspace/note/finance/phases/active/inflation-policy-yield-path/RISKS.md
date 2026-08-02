# Inflation Policy Yield Path Risks

- 기존 경기 사이클 결과를 편의상 재사용하면 새 분석의 독립성이 무너진다.
- release timestamp를 observation date로 대체하면 FOMC 시점 replay에 look-ahead가 생긴다.
- SEP 분포끼리 개인별 대응을 추론하면 공개 자료가 제공하지 않는 관계를 조작하게 된다.
- 10년물 상승은 물가 외에 성장, 실질금리, 기간 프리미엄, 국채 공급으로도 발생한다.
- worktree에 사용자 소유 변경과 generated QA 파일이 있어 task 대상만 선별 stage해야 한다.
- 현재 환경은 `BEA_API_KEY`가 없어 component breadth를 공개할 수 없고, ACM workbook은
  historical vintage archive가 아니어서 기간 프리미엄 replay가 `LIMITED`다.
- 3차 UI가 비교 가능 baseline 개선을 `READY`로 바꾸거나 월간 결과를 연말·정책·돌파
  probability 전체로 확대하면 publication boundary가 무너진다. 현재 component별
  `LIMITED/NOT_AVAILABLE`을 그대로 전달해야 한다.
- 현재 reverse engine의 수학 계약은 있지만 calibrated joint rate path가 없어 실제
  snapshot은 `NOT_AVAILABLE`이다. UI fixture나 수동 25bp 매핑으로 채우지 않는다.
