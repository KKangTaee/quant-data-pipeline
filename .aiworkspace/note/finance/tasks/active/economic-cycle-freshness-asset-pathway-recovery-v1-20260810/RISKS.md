# Risks

- FRED/ALFRED, EIA와 yfinance 응답 시간·rate limit은 로컬 코드 밖의 변동 요인이다.
- bounded concurrency는 worker 4개를 넘기지 않고 DB write는 단일 caller thread에서 수행한다.
- official S&P actual EPS가 없으면 그 경로의 제한은 의도적으로 남는다.
