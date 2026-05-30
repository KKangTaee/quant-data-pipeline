# Plan

## 이걸 하는 이유?

Overview Events는 FOMC official row와 earnings estimate row를 같은 `market_event_calendar` table에서 읽는다. 정식 기능으로 쓰려면 사용자가 “공식 일정인지”, “provider 추정치인지”, “오래된 추정치인지”를 table과 status card에서 바로 구분할 수 있어야 한다.

## Scope

- Events read model에 `Source Type`, `Freshness`, `Age Days`를 추가한다.
- FOMC official row와 yfinance earnings estimate row의 coverage count를 분리한다.
- earnings estimate stale 기준을 14일로 정의하고 warning을 노출한다.
- All / FOMC / Earnings filter와 기존 DB read-only boundary를 유지한다.
- schema 변경과 새 collector source 추가는 하지 않는다.

## Done Criteria

- FOMC row는 `Official`, earnings prototype row는 `Provider Estimate`로 보인다.
- 오래된 earnings estimate는 `Stale estimate`로 표시되고 warning이 보인다.
- service contract tests가 official / estimate / stale estimate case를 검증한다.
