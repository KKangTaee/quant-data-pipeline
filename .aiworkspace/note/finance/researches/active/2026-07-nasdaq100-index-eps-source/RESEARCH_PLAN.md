# Nasdaq-100 Index EPS Source Research Plan

Status: Active
Last Updated: 2026-07-12

## Research Question

S&P 500 가치평가 화면과 동일한 월별 log(PER) 구간 및 FOMC SEP 기반 적정 지수 시나리오를 Nasdaq-100에 적용하기 위해, 최소 60개월의 NDX index-level TTM EPS 또는 trailing P/E를 합법적이고 자동화 가능한 방식으로 어떻게 확보할 수 있는가?

## Scope

- Nasdaq-100(NDX) 및 QQQ 환산을 우선 대상으로 한다.
- 공식 공개자료, 공식 라이선스 데이터, 상용 index-fundamentals provider, SEC/holdings 기반 자체 산출을 비교한다.
- scraping, 접근 제한 우회, 현재 구성 종목의 무근거 과거 소급 적용은 제외한다.
- 가격·EPS·구성/가중치·release vintage·라이선스·자동화 가능성을 분리해서 평가한다.

## Method

- 현재 DB snapshot을 audit한다.
- 공식 product/API 문서를 우선해 3~5개 조달 경로를 비교한다.
- direct index aggregate와 constituent reconstruction을 분리한다.
- source claim은 documented/inferred/unknown으로 구분한다.

## Outputs

- `CURRENT_PROJECT_AUDIT.md`
- `BENCHMARKS.md`
- `SOURCES.md`
- `RECOMMENDATION.md`
- `RISKS.md`

## Completion Criteria

- 3~5개 현실적인 조달 경로를 source evidence와 함께 비교한다.
- 각 경로가 60개월 backfill을 즉시 지원하는지 또는 앞으로만 축적 가능한지 구분한다.
- 권장 primary source와 허용 가능한 fallback을 제시한다.
- 구현 전에 확인해야 할 계약·필드·PIT 질문을 남긴다.
