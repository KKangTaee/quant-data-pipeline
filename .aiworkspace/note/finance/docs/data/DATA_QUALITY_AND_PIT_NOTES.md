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
- `nyse_symbol_lifecycle`은 historical universe / delisting evidence를 담기 위한 table이다.
  current listing snapshot row는 partial `listing_observed` evidence이고, requested period를 덮는 actual `historical_listing`, `delisting_feed`, 또는 actual `computed_from_snapshots` source가 있어야 survivorship control PASS 근거가 된다.
- SEC Form 25 / 25-NSE row는 official delisting / withdrawal evidence로 저장할 수 있지만, first listing date나 complete historical universe membership을 증명하지 않는다.
  Form 25 부재를 active listing proof로 해석하면 안 된다.
- Phase 8부터 lifecycle row는 `event_type`과 `event_date`를 명시한다.
  SEC Form 25는 `delisting` event이고 current listing snapshot은 `listing_observed` event이므로 두 evidence를 같은 PASS 근거처럼 해석하면 안 된다.
- Nasdaq public Symbol Directory current files는 `listing_observed` partial evidence로 저장할 수 있다.
  이 row는 current snapshot coverage를 넓히지만, missing symbol을 delisted로 만들거나 requested historical period membership을 증명하지 않는다.
- SEC `company_tickers_exchange.json` row는 current CIK / ticker / exchange identity cross-check로 저장할 수 있다.
  이 row도 current association일 뿐이므로 historical membership, delisting, ticker action proof가 아니다.
- computed snapshot lifecycle row는 existing current snapshot rows의 repeated observation window를 요약한다.
  Phase 8-5에서는 `coverage_status=partial`로 저장하며, missing snapshot을 delisting proof로 해석하지 않는다.
- Data Coverage Audit은 lifecycle evidence를 current snapshot, SEC identity cross-check, computed partial, actual coverage, delisting actual로 분리해 표시한다.
  이 분리는 operator 해석을 돕기 위한 read-only scoring이며, partial evidence를 PASS로 승격하지 않는다.
- `etf_operability_snapshot` `db_bridge` row는 official ETF provider actual data가 아니다.
- P2-2B official row는 iShares / SSGA / Invesco page의 current snapshot을 normalize한 것이다.
  다만 Invesco QQQ는 현재 expense ratio / inception만 확보되어 `partial`이며,
  source map 밖 ticker는 official coverage가 없을 수 있다.
  current snapshot이므로 과거 특정 시점의 운용성 truth로 쓰면 안 된다.
- `etf_holdings_snapshot`과 `etf_exposure_snapshot`은 official holdings / aggregate source에서 온 current snapshot이다.
  AOR은 현재 1차 ETF holdings만 저장하고, 2차 Aggregate Underlying look-through는 후속이다.
  GLD는 row-level source가 bar list PDF 성격이라 synthetic holdings row를 만들지 않는다.
  holdings와 exposure 모두 과거 특정 검증일의 point-in-time truth로 쓰려면 해당 날짜의 provider snapshot이 DB에 있어야 한다.
- `data-provenance-coverage-v1` 이후 Practical Validation provider context는 ETF provider snapshot의 source mix, as-of range, collected range, coverage status weight, freshness를 compact하게 보여준다.
  기본 provider freshness threshold는 45일이며, coverage가 충분해도 threshold를 넘은 stale snapshot은 `PASS`가 아니라 `REVIEW`로 남긴다.
- `validation-efficacy-hardening-v1` 이후 Practical Validation과 Final Review는 Validation Efficacy Audit에서 PIT / look-ahead / survivorship / provider freshness / temporal / OOS / regime gap을 별도 row로 노출한다.
  이 audit은 기존 compact evidence를 읽는 read model이며, historical universe / delisting evidence가 명시되지 않으면 survivorship / universe row를 `REVIEW`로 남긴다.
- `validation-efficacy-gate-policy-refinement-v2` 이후 temporal / OOS / regime non-PASS row는 Final Review selected-route gate evidence에도 병합된다. `REVIEW`는 hold / re-review 요구이고, `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker다.
- `look-through-exposure-board-v1` 이후 holdings / exposure snapshot은 compact board로만 workflow에 전달된다.
  이 board는 1차 ETF holdings / exposure 기준이며, ETF-of-ETF 2차 look-through는 아직 보장하지 않는다.
- `macro_series_observation`은 FRED observation date 기준 market-context series다.
  FRED API key가 없으면 official CSV download를 사용하며, Practical Validation에서는 최신 관측값과 staleness를 함께 봐야 한다.
  vintage / revision point-in-time까지 보장하는 ALFRED 계층은 아직 구현하지 않았다.
  Macro freshness threshold는 기존 Practical Validation 기준인 10일을 유지한다.

## Fundamentals / factors

좋은 점:

- legacy broad coverage summary layer가 있어 old replay나 explicit comparison을 빠르게 확인할 수 있다.
- direct / derived / inferred source metadata를 추적할 수 있다.
- valuation, profitability, growth 계열 factor를 빠르게 만들 수 있다.

주의점:

- `nyse_fundamentals`와 `nyse_factors`는 strict filing-time PIT source가 아니다.
- Phase 8 source migration closeout 이후 새 financial statement source 준비와 strict annual factor research는 EDGAR statement shadow path를 우선한다.
- broad yfinance fundamentals / factors는 production financial statement source가 아니라 saved/history replay compatibility 또는 explicit broad comparison layer다.
- fallback 계산값은 accounting-grade precision이 아닐 수 있다.
- provider account label과 coverage가 ticker별로 다를 수 있다.

## Detailed financial statements

좋은 점:

- filing / concept / period 단위 raw value를 저장한다.
- `filing_date`, `accepted_at`, `available_at`, `accession_no`, `form_type`를 함께 저장한다.
- EDGAR raw ledger와 statement shadow tables는 annual financial statement source migration의 canonical path다.

주의점:

- label standardization이 어렵다.
- 기업별 concept / unit / period 표현이 다를 수 있다.
- quarterly row와 annual row가 함께 존재할 수 있으며, synthetic Q4는 DB 저장 단계에서 만들지 않는다.
- quarterly consumer path는 `10-Q` / `10-Q/A` rows만 usable row로 읽는다. `10-K` / FY full-year flow values는 quarterly flow value로 쓰지 않는다.
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
- [ ] `docs/PROJECT_MAP.md`, `docs/data/`, `docs/architecture/` 중 어떤 문서를 갱신해야 하는가?
