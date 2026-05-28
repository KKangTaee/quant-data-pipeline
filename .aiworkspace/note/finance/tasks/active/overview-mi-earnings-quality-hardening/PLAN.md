# Plan

## 이걸 하는 이유?

Overview Events의 earnings calendar는 yfinance primary estimate와 Nasdaq cross-check로 작동한다.
하지만 사용자가 운영 중에 가장 궁금해할 질문은 "어떤 ticker가 빠졌고 왜 빠졌는지", "현재 row를 얼마나 믿어도 되는지", "다음 액션이 무엇인지"다.

## Scope

- Earnings 수집 결과에 symbol-level diagnostics를 추가한다.
- no earnings date, outside collection window, provider error, invalid symbol 같은 reason을 job result와 failure artifact에 남긴다.
- Overview Events row에 source/validation/freshness 기반 quality action을 표시한다.
- Ingestion과 Overview refresh 결과에서 earnings diagnostics를 바로 볼 수 있게 한다.

## Non-goals

- Company IR 공식 parser를 새로 붙이지 않는다.
- 새 DB table을 만들지 않는다.
- 실시간 자동 refresh schedule은 다루지 않는다.
