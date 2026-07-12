# Current Project Audit

Status: Complete
Last Updated: 2026-07-12

## Summary

현재 Market Context의 S&P 500 가치평가는 DB에 저장된 월별 지수 가격/EPS/PER, FOMC SEP vintage, 현재 SPX/SPY 가격을 service가 계산한 뒤 React가 표시한다. Nasdaq-100 확장 시 계산 엔진과 SEP는 재사용할 수 있지만 NDX index-level trailing P/E/EPS source가 비어 있다.

## Snapshot

현재 QQQ 가격과 FOMC SEP는 준비돼 있지만 NDX 가격, index-level EPS/P-E, 과거 구성·가중치는 준비되지 않았다.

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

## Surface Role Classification

Market Context 가치평가 화면은 사용자-facing product surface다. provider token, request count, raw response 같은 운영 정보는 Ingestion/diagnostic 경계에 두고, 화면에는 출처·기준일·품질·계산 한계만 표시한다.

## Strengths

- 기존 계산 함수는 대부분 지수 중립적인 수학을 사용한다.
- FOMC SEP와 QQQ 가격은 재사용 가능하다.
- SEC filing의 `filing_date`, `accepted_at`, `available_at`가 있어 장기적으로 PIT 자체 산출을 연구할 기반은 있다.

## Weaknesses

- DB에 `^NDX` 또는 `^IXIC` 가격 이력이 없다.
- NDX index-level EPS/PER 원천과 전용 table/loader/resolver가 없다.
- 과거 NDX 구성·가중치 snapshot이 없다.
- QQQ holdings 2개 vintage로는 1년 또는 5년을 즉시 재구성할 수 없다.

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
