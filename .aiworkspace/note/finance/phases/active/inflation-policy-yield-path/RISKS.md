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
- 3차 UI는 `LIMITED/NOT_AVAILABLE` 확률 비공개, AUTO/USER 분리, DB-only command와
  cycle-independent recession 경계를 테스트와 Browser QA로 고정했다.
- 4차 주가 스트레스가 S&P 500 6,400 같은 사용자 숫자를 전역 target으로 승격하거나
  동시발생을 인과효과로 해석하면 안 된다. 독립 episode 정의와 chronological holdout이 필요하다.
- FactSet archive 후보 103개 중 80개 release/160행만 두 CY 라벨과 구조 검증을 통과했다.
  제외된 23개를 OCR 추정치로 채우지 않으며 collector partial health를 공개한다.
- equity PIT validation은 year-end label이 실제 공개된 뒤의 fold에서만 학습하고,
  production/command 모두 versioned equity artifact와 independently READY joint path를
  요구한다. payload 존재만으로 publication gate를 우회하지 않는다.
- verified joint paths는 core artifact UPSERT와 충돌하지 않는 `joint_macro_paths` component,
  live index/EPS/start-yield는 model artifact가 아닌 snapshot `equity_json`을 사용한다.
- measured EPS revision, 시작금리·공동경로 endpoint 누락은 0으로 보정하지 않고 equity
  `NOT_AVAILABLE`로 닫는다.
- 5차 침체 연결 시 4차 equity model feature에 기존 경제 사이클 확률을 편의상 넣지 않는다.
  독립 침체 artifact가 `READY`인 경우에만 별도 versioned feature로 추가한다.
- 4차 closeout은 actual PIT EPS 80 release, 77 completed origin, MAE/baseline/OOS coverage,
  focused regression, React 17건, production build와 actual Browser command로 검증했다.
