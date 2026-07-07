# Overview Market Movers Smart EOD Refresh

## 이걸 하는 이유?

Weekly / Monthly / Yearly Market Movers의 가격 이력 갱신이 매번 전체 universe에 대해 긴 lookback window를 다시 받아 시간이 오래 걸린다. 이미 최신인 심볼은 건너뛰고, 누락되었거나 오래된 심볼만 보강해 사용자가 갱신 버튼을 더 자주, 덜 부담스럽게 누를 수 있게 한다.

## 단계

1. Smart target / delta refresh 기반
   - 최신 심볼은 스킵한다.
   - stale 심볼은 마지막 저장일 다음 날부터 as-of 다음 날까지 delta 수집한다.
   - missing 심볼은 기존 collection period full window로 수집한다.
2. UI / 결과 표시
   - 갱신 대상, 최신 스킵, full window fallback 여부를 사용자가 이해할 수 있게 표시한다.
   - 진행 카드의 stopwatch/progress 흐름과 연결한다.
3. 품질 보강
   - 최신 row가 있어도 데이터가 불완전하거나 window coverage가 부족한 심볼을 보강 대상으로 포함한다.

## 범위

- `app/jobs/overview_actions.py`
- `app/web/overview/market_movers_helpers.py`
- `tests/test_service_contracts.py`

## 커밋 기준

각 차수는 개발, QA, 커밋 순서로 완료한다. QA screenshot, run history, local artifacts, `.DS_Store`는 명시 요청 없이 커밋하지 않는다.
