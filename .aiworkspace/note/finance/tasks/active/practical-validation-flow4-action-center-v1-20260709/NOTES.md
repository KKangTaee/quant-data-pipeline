# Notes

## Decisions

- `카테고리별 검증 결과`는 판정판으로 유지한다.
- `데이터 보강 대상`과 Python 수집 버튼은 사용자-facing으로 하나의 `데이터 보강 / 수집 실행` action center 안에서 읽히게 한다.
- `Provider`는 내부 데이터 출처 / 수집 path 의미이므로 first-read 제목에서는 낮추고, 상세 설명과 원자료에만 남긴다.
- 수집 버튼은 기존 Python provider collection boundary를 계속 사용한다.

## Durable Interpretation

Provider means an external or source-backed data evidence path, not a broker or trading provider. Examples are ETF issuer data, holdings / exposure snapshots, FRED macro series, and source map discovery.
