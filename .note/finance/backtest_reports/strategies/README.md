# Strategy Backtest Hubs

## 목적

이 폴더는 전략별로 backtest 결과를 다시 읽기 쉽게 묶어두는 허브 문서 모음이다.

쉽게 말하면:

- `phase13/` 아래 문서: 결과 원문 archive
- `strategies/` 아래 문서: 전략별 요약 허브와 전략별 backtest log

구조다.

## 현재 전략 허브

- `GTAA.md`
- `QUALITY_STRICT_ANNUAL.md`
- `VALUE_STRICT_ANNUAL.md`
- `QUALITY_VALUE_STRICT_ANNUAL.md`

## 전략별 backtest log

- `GTAA_BACKTEST_LOG.md`
- `QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md`
- `VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
- `QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
- `BACKTEST_LOG_TEMPLATE.md`

이 문서들은 앞으로 전략별로:

- 어떤 세팅으로 돌렸는지
- 결과가 어땠는지
- 왜 다시 볼 가치가 있는지

를 누적 기록하는 용도다.

## 읽는 순서

1. 전략 허브 문서를 먼저 본다
2. 해당 전략의 backtest log에서 최근 run 기록을 본다
3. 필요한 경우에만 phase archive의 세부 report를 연다

이렇게 하면 같은 전략 관련 문서를 phase별 파일명으로 하나씩 찾지 않아도 되고,
최근에 어떤 설정을 돌렸는지도 전략 기준으로 바로 다시 볼 수 있다.

허브 문서에는 이제 최근 log entry의 핵심 설정과 결과를 짧게 다시 보여주는
`최근 backtest log snapshot` 섹션을 같이 유지한다.
