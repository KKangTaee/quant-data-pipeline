# Data Quality And PIT Notes

## 목적

이 문서는 finance data layer를 해석할 때 항상 같이 봐야 하는 품질, point-in-time, survivorship, stale data 위험을 정리한다.

## 핵심 원칙

- strong backtest result는 데이터 품질 검토 없이 투자 후보로 해석하지 않는다.
- `period_end` 기준 데이터와 filing availability 기준 데이터는 구분한다.
- current profile snapshot과 historical point-in-time universe는 구분한다.
- provider no-data, stale price, missing row는 backtest 기간과 결과 해석에 직접 영향을 줄 수 있다.

## Price data

좋은 점:

- OHLCV 외에 dividend와 split도 저장한다.
- stock과 ETF를 같은 price ledger에 저장해 mixed-asset backtest에 연결하기 쉽다.
- short-window refresh와 broad refresh의 execution profile이 분리되어 있다.

주의점:

- 거래소 세션 calendar와 corporate action policy가 전체 전략에서 완전히 통일된 것은 아니다.
- 현재 전략은 주로 `Close`를 사용한다.
- provider no-data와 rate-limit 분류는 heuristic일 수 있다.
- 특정 ticker의 stale / missing price는 공통 date intersection을 줄이거나 excluded ticker를 만들 수 있다.
- Phase 27 이후 백테스트 결과 화면은 `Data Trust Summary`에서 요청 종료일, 실제 결과 종료일, common latest price, excluded ticker, malformed price row를 먼저 보여주는 방향으로 간다.

## Profile / universe data

좋은 점:

- universe filtering과 ETF current-operability 판단에 실용적이다.
- `etf_operability_snapshot`은 profile과 price history에서 얻은 bridge/proxy evidence를 별도 snapshot으로 분리해,
  Practical Validation에서 출처와 coverage를 더 명확히 읽을 수 있게 한다.

주의점:

- `status`, `is_spac`, country, sector, industry는 provider 품질에 의존한다.
- historical listing / delisting / symbol-change truth가 아니다.
- survivorship bias를 완전히 제거하지 못한다.
- `etf_operability_snapshot` `db_bridge` row는 official ETF provider actual data가 아니다.
- P2-2B official row는 iShares / SSGA / Invesco page의 current snapshot을 normalize한 것이다.
  다만 Invesco QQQ는 현재 expense ratio / inception만 확보되어 `partial`이며,
  source map 밖 ticker는 official coverage가 없을 수 있다.
  current snapshot이므로 과거 특정 시점의 운용성 truth로 쓰면 안 된다.
- `etf_holdings_snapshot`과 `etf_exposure_snapshot`은 official holdings / aggregate source에서 온 current snapshot이다.
  AOR은 현재 1차 ETF holdings만 저장하고, 2차 Aggregate Underlying look-through는 후속이다.
  GLD는 row-level source가 bar list PDF 성격이라 synthetic holdings row를 만들지 않는다.
  holdings와 exposure 모두 과거 특정 검증일의 point-in-time truth로 쓰려면 해당 날짜의 provider snapshot이 DB에 있어야 한다.

## Fundamentals / factors

좋은 점:

- broad coverage summary layer가 있어 빠른 research가 가능하다.
- direct / derived / inferred source metadata를 추적할 수 있다.
- valuation, profitability, growth 계열 factor를 빠르게 만들 수 있다.

주의점:

- `nyse_fundamentals`와 `nyse_factors`는 strict filing-time PIT source가 아니다.
- fallback 계산값은 accounting-grade precision이 아닐 수 있다.
- provider account label과 coverage가 ticker별로 다를 수 있다.

## Detailed financial statements

좋은 점:

- filing / concept / period 단위 raw value를 저장한다.
- `filing_date`, `accepted_at`, `available_at`, `accession_no`, `form_type`를 함께 저장한다.
- 향후 custom PIT factor engine의 핵심 raw material이 될 수 있다.

주의점:

- label standardization이 어렵다.
- 기업별 concept / unit / period 표현이 다를 수 있다.
- quarterly row와 annual row가 함께 존재할 수 있으며, synthetic Q4는 DB 저장 단계에서 만들지 않는다.
- `nyse_financial_statement_labels`는 convenience summary이며, strict source of truth는 values table이다.

## PIT 해석 기준

| 기준 | 의미 | 위험 |
|---|---|---|
| `period_end` | 회계 기간 종료일 | 실제 공시 전 값을 쓸 수 있어 look-ahead risk |
| `filing_date` | filing 제출일 | provider / timezone 해석 필요 |
| `accepted_at` | SEC acceptance timestamp | PIT 기준으로 더 엄격하지만 coverage / parsing 확인 필요 |
| `available_at` | system이 usable하다고 보는 시점 | loader / rebuild logic과 일관성 확인 필요 |
| `accession_no` | filing identity | 중복 / amendment 처리 기준 필요 |

## 새 데이터 변경 시 체크리스트

- [ ] 이 데이터는 source, derived, shadow, convenience 중 무엇인가?
- [ ] `period_end`와 filing availability를 혼동하지 않았는가?
- [ ] point-in-time backtest에서 사용할 수 있는가?
- [ ] survivorship bias를 악화시키지 않는가?
- [ ] stale / missing row가 warning이나 metadata에 남는가?
- [ ] loader가 source of truth table을 올바르게 읽는가?
- [ ] `FINANCE_COMPREHENSIVE_ANALYSIS.md`, `data_architecture/`, `code_analysis/` 중 어떤 문서를 갱신해야 하는가?
