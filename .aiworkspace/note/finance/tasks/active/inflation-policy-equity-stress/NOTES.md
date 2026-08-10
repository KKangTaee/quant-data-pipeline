# Inflation Policy Equity Stress Notes

## 2026-08-03 Intake

- current code는 `finance/inflation_policy_*.py` 평면 module 구조다.
- `sp500_monthly_valuation` Shiller history는 strict PIT forward-EPS source가 아니다.
- actual DB: official EPS 0 rows, Shiller monthly 1,867 rows, `^GSPC` price 2,524 rows,
  DGS10·DFII10·T10YIE vintage history는 존재한다.
- 실제 결과는 엔진 구현과 별개로 입력·검증 gate를 통과하기 전 `NOT_AVAILABLE`이다.

## 2026-08-03 Integration

- `inflation_policy_snapshot.equity_json`은 inflation/policy/rates/reverse와 독립된
  compact section이다. legacy row나 malformed equity payload는 typed
  `NOT_AVAILABLE`로 닫으며 다른 section을 낮추지 않는다.
- `EquityStressResult`를 파이프라인에 직접 넘길 수 있고 measured EPS revision과
  사용자 AI uplift는 직렬화 뒤에도 별도 필드로 남는다.
- actual DB에는 공식 `sp500_index_earnings` row가 없으므로 Shiller trailing EPS를
  대신 쓰지 않았다. UI는 필요한 Ingestion 조치와 공동 경로 검증 조건을 설명한다.
- READY/LIMITED presentation은 React 회귀 테스트로 검증했고, actual Browser QA는
  데이터 hard gate 때문에 의도대로 `NOT_AVAILABLE`만 확인했다.

## 2026-08-03 Correctness Review

- 같은 workbook의 네 차년도 분기가 모두 존재하는 release vintage만 forward EPS로
  선택한다. 서로 다른 workbook release의 분기를 섞지 않으며 measured revision도 같은
  basis/source의 이전 complete vintage와만 비교한다.
- yield/macro history는 loader에서 전체 eligible vintage를 보존하고 각 origin cutoff에서
  다시 선택한다. 이후 공개된 revision을 과거 origin에 적용하지 않는다.
- 학습 feature는 origin부터 같은 해 year-end까지의 DGS2/DGS10/DFII10/T10YIE 변화와
  당시 공개 가능한 Q4/Q4 Core PCE다. label은 year-end endpoint와 Q4 PCE 공개시각 중
  늦은 `label_available_at` 이후 fold에서만 학습에 들어간다.
- 학습 마지막 역사 row와 현재 scenario 입력을 분리했다. 현재 저장 index/EPS/rate context는
  live snapshot cutoff에서 따로 만들고 artifact의 `trained_through`를 바꾸지 않는다.
- equity artifact는 `equity-stress-publication-v1` contract, 세 baseline, 80% interval
  coverage error를 기록한다. command와 production runner는 versioned artifact와 독립적으로
  `READY`가 확인된 joint path만 받아 우회 가능한 수동 경로를 차단한다.
- 검증 공동경로는 `core_pce_hybrid`와 별도인 `joint_macro_paths` component identity로
  조회한다. core artifact UPSERT가 공동경로 parameters/validation을 덮어쓰지 않는다.
- model artifact에는 live index/EPS/start-yield를 저장하지 않는다. 이 context는 해당
  `as_of_at`의 `equity_json`에 저장되고 사용자 scenario command도 선택 snapshot에서만 읽는다.
- timestamp가 없는 legacy 일봉은 미국 정규장 마감 전 cutoff에서 당일 close를 제외한다.
  paired residual은 순서 독립적인 최대 16개 quantile sample로 제한해 각 forward path와
  교차 적용하고, path를 안정 정렬해 입력 순서가 quantile/target probability를 바꾸지
  않게 했다.
- measured EPS revision, `months_to_year_end`, DGS2/DGS10/DFII10/T10YIE 시작값과 모든
  공동경로 endpoint를 publication 전 검사한다. 누락값은 0bp/0%가 아니라 typed
  `NOT_AVAILABLE`이다.
