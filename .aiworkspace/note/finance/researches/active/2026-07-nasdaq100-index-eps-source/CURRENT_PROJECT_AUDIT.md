# Current Project Audit

Status: Complete
Last Updated: 2026-07-14

## Summary

Market Context의 Nasdaq-100 `(QQQ proxy)` pipeline과 화면은 이미 구현됐다. 현재 병목은 기능 부재가 아니라 119개월 중 53개월이 95% earnings coverage gate를 통과하지 못하는 것이다. 직접 NDX P/E/EPS 원천 없이도 기능을 완성할 수 있지만, 기존 SEC 계산 오류를 먼저 고치고 historical EOD와 foreign/ADR actual의 누락을 단계적으로 복구해야 한다.

## Snapshot

2026-07-14 local DB 기준 monthly valuation은 2016-09~2026-07의 119행이며 `READY 66 / BLOCKED 53`이다. 최근 60개월 repair는 172,240행의 EOD/EPS observation을 보강했지만 같은 free source를 반복 호출하는 것만으로는 66개월을 넘지 못했다. 1/3/5년 history contract는 각각 최신 71/95/119개월이 모두 READY여야 하므로 현재 완성된 window는 없다.

## Current Product Promise

- 사용자가 현재 지수의 최근 5년 대비 멀티플 위치를 확인한다.
- FOMC SEP의 실질 GDP와 PCE를 합산한 자체 EPS 성장 시나리오로 예상 지수 구간을 본다.
- 결과를 공식 적정가, 애널리스트 컨센서스, 매수·매도 신호로 표현하지 않는다.
- UI는 외부 provider를 직접 호출하지 않고 `Ingestion -> DB -> Loader -> Service -> React` 경계를 유지한다.

## Implemented Capabilities Relevant To NDX

- 60개월/36개월 log(PER) 분포와 ±1σ/±2σ 구간 계산
- FOMC SEP 21개 release vintage(2021-03-17~2026-06-17)
- 1/3/5년 과거 시점 재구성
- QQQ 일봉 5,105건(2006-03-21~2026-07-07)
- SEC detailed statement filing 92,770건, 1,029 symbols
- QQQ holdings 210 rows, 2 vintages(2026-05-08/2026-05-29)
- SEC QQQ N-PORT public archive 22 quarters(2020-12-31~2026-03-31, no-auth backfill 가능)
- QQQ N-PORT holdings 3,049 unique key와 monthly proxy 119행 materialization
- coverage blocker에서 최근 60개월 부족분을 repeat-safe하게 수집하는 repair action
- 현재 repair planner 기준 보강 대상 50개, source 미지원 3개 식별

## Surface Role Classification

Market Context 가치평가 화면은 사용자-facing product surface다. provider token, request count, raw response 같은 운영 정보는 Ingestion/diagnostic 경계에 두고, 화면에는 출처·기준일·품질·계산 한계만 표시한다.

## Strengths

- 기존 계산 함수는 대부분 지수 중립적인 수학을 사용한다.
- FOMC SEP와 QQQ 가격은 재사용 가능하다.
- SEC filing의 `filing_date`, `accepted_at`, `available_at`가 있어 장기적으로 PIT 자체 산출을 연구할 기반은 있다.

## Weaknesses

- direct NDX index-level EPS/PER 원천은 여전히 없다. 다만 QQQ proxy 전용 table/loader/resolver는 이미 구현됐다.
- 53개 blocked month 중 50개는 `INSUFFICIENT_EARNINGS_COVERAGE`, 3개는 `NON_POSITIVE_AGGREGATE_EARNINGS`다.
- `derive_filing_aware_ttm_eps`가 비교표시된 FY fact를 실제 연말 fact처럼 취급해 `FY-Q1-Q2-Q3` 음수 분기를 만들 수 있다. 2020-04~06의 비정상 aggregate loss는 이 계산 오류로 재현된다.
- monthly weight drift가 raw close를 사용해 split 전후 수익률을 왜곡할 수 있다. 보유비중 drift에는 split-adjusted price, 같은 증권의 EPS/P-E identity에는 raw close를 구분해야 한다.
- early Alphabet는 현재 CIK의 companyfacts만으로 당시 filing lifecycle을 복구하지 못한다. historical CIK/security identity와 원문 filing resolver가 필요하다.
- foreign issuer의 현재 SEC CIK mapping과 IFRS/foreign EPS facts는 존재하지만, 기존 resolver가 non-USD/share, 20-F cadence, ADR/ADS ratio를 충분히 처리하지 않는다.

## 2026-07-14 Implementation Feasibility Evidence

- calculator 오류만 수정해도 READY 후보는 `66 -> 최소 69`로 늘어난다.
- blocked month의 coverage는 모두 80% 이상이며 17개월은 이미 94% 이상이다. 많은 달은 WBA·ATVI·CELG 같은 미국 상장 1~2개 종목만 복구해도 95%를 넘는다.
- local repair target에서 historical EOD가 필요한 23개 symbol 중 Tiingo public catalog는 22개 exact symbol을 제공한다. 나머지 `SYMC`는 successor series `GEN`이 존재하므로 corporate-action alias를 검증하면 23개 모두 후보가 된다.
- QQQ N-PORT의 `market_value / shares`로 만든 실제 snapshot price anchor는 23개 historical EOD gap 모두에 존재한다. 총 171개 anchor를 확인했다.
- 현재 foreign/ADR 목록을 계속 누락으로 보수적으로 남기고 미국 상장 누락분만 SEC actual + Tiingo EOD로 복구하는 상한 시뮬레이션에서도 119/119개월이 95%를 넘었고 최저 coverage는 96.319%였다.
- 위 결과는 catalog/DB 기반 feasibility upper bound이지 production 성공 보장은 아니다. 실제 Tiingo payload, symbol recycle, EPS filing lifecycle과 public calibration을 통과해야 5년 graph 완료를 확정한다.

## Data And Validation Risks

- 현재 구성 종목을 과거에 소급하면 survivorship bias가 생긴다.
- 분기 period-end EPS를 실제 공개일 이전 월에 적용하면 look-ahead가 생긴다.
- provider aggregate의 적자 기업 처리, 복수 주식 클래스, ADR, divisor 방법이 공개되지 않으면 S&P/Shiller와 완전히 같은 의미라고 볼 수 없다.
- NDX 가격, P/E, EPS의 기준일이 다르면 `NDX / P/E = EPS` 교차검증이 왜곡된다.

## Benchmark Questions

1. 최소 60개월의 NDX trailing P/E를 API로 즉시 받을 수 있는가?
2. NDX EPS가 direct aggregate인지 `index level / P/E` 파생값인지 구분 가능한가?
3. historical series가 당시 공개 vintage인지 현재 재작성된 history인지?
4. 로컬 연구용 저장, 장기 DB 보관, 화면 표시가 라이선스 범위에 포함되는가?
5. 가격·P/E·EPS 기준일과 update cadence가 무엇인가?

## Open Questions

- GuruFocus indicator 6778의 적자 기업/복수 클래스 처리 방법은 공개 문서에서 확인되지 않았다.
- FactSet/LSEG 계약에서 NDX와 trailing actual P/E entitlement가 실제 포함되는지 quote/sample 확인이 필요하다.
- optional free-account Tiingo token으로 23개 historical EOD payload와 end date/name을 검증해야 한다.
- SEC CIK lifecycle, 20-F annual actual fallback, ADR/ADS ratio를 적용한 뒤 119/119 strict READY가 실제로 성립하는지 repair spike로 측정해야 한다.
- ADR ratio, 복수 클래스, foreign issuer, 2023 special rebalance를 반영한 뒤 공개 Nasdaq P/E 관측값과의 오차가 허용 범위인지 검증해야 한다.
