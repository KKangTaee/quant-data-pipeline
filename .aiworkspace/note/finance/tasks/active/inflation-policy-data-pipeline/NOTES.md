# Inflation Policy Data Pipeline Notes

- 2026-08-02: UI 시안 승인 뒤 실제 구현 순서는 data -> engine -> workbench로 확정했다.
- 기존 경제 사이클 서비스와 결과는 새 데이터/모델의 dependency가 아니다.
- 2026 SEP 분포는 aggregate count만 저장하며 participant mapping을 생성하지 않는다.
- FRED HTTP·pagination·normalization·UPSERT primitive만 공통 module로 분리했다. 기존
  경제 사이클 catalog와 수집 orchestration은 기존 module에 남겼다.
- verified clock이 없는 series는 `END_OF_DAY_ET`로 보수적으로 공개시각을 잡는다.
- 독립 catalog는 inflation, labor cost, labor, activity, policy, rates를 포함하며
  `finance.economic_cycle_catalog`를 import하지 않는다.
- BEA NIPA `T20804` index level은 저장된 release 안에서 전월 index와 비교해 breadth를
  계산한다. 필수 headline/goods/services/core가 없거나 2개월 history가 없으면
  `NOT_AVAILABLE`이다.
- SEP parser는 공식 accessible HTML의 제목을 기준으로 Table 1, Figure 2, Figure 3을
  구분한다. 2026년 6월 익명 집계에서 rate dots 합계 18명과 Core PCE `3.5-3.6` 4명을
  검증하되, 두 분포 사이의 개인별 연결은 생성하지 않는다.
- SEP 공개 시각은 페이지의 공식 `For release at` 문구를 미국 동부시간으로 해석하고,
  URL 날짜와 다르면 저장하지 않는다.
- FOMC 정책 결정은 target range, 찬반 수, 반대자 이름과 명시적 선호 방향을 저장한다.
  2026-07-29 결정은 3.50-3.75% 동결, 9-3, 세 명 모두 `HIKE_25`로 공식 원문에서
  검증했다. 임의의 hawkish/dovish 점수는 만들지 않는다.
- 정책 이력은 날짜 오름차순으로 파싱해 직전 range를 연결한다. 수집 범위의 첫 회의처럼
  과거 결정이 없으면 미래 값으로 채우지 않고 `PARTIAL`로 둔다.
- New York Fed ACM workbook의 `ACM Daily.DATE`와 `ACMTP10`을 사용한다. 모델이 월별로
  재추정되어 과거 값도 바뀔 수 있으므로 workbook의 과거 행을 과거 공개 빈티지로
  소급하지 않는다. 모든 행은 실제 `collected_at`을 release/realtime origin으로 갖는다.
- ACM은 기간 프리미엄을 분해하는 보조 추정치이며 New York Fed/FOMC의 공식 전망값이
  아니다. 충분한 자체 수집 빈티지가 쌓일 때까지 replay coverage는 `LIMITED`다.
