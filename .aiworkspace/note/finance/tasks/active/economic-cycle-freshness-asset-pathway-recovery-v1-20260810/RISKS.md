# Risks

## 남은 외부 리스크

- FRED/ALFRED, EIA와 yfinance 응답 시간·rate limit은 로컬 코드 밖의 변동 요인이다.
- bounded concurrency는 worker 4개를 넘기지 않고 DB write는 단일 caller thread에서 수행한다.
- official S&P actual EPS가 없으면 그 경로의 제한은 의도적으로 남는다.
- 저장소 전체 pytest는 단일 process에서 Streamlit singleton 재초기화와 여러 기존 contract drift 때문에 336건 실패한다. 대표 첫 실패는 단독 process에서 통과했고 경제사이클 141 tests도 독립 process에서 모두 통과했으므로, 이번 task의 회귀가 아니라 별도 test isolation/기존 영역 정리 범위로 남긴다.

## 닫힌 리스크

- 자산 row가 stale하다는 이유만으로 마지막 측정값까지 `자료 부족`으로 사라지던 문제는 `DELAYED` 표시와 signal eligibility 분리로 닫았다.
- 동시 provider fetch가 DB write thread-safety를 훼손할 위험은 caller-thread deterministic UPSERT와 PIT fingerprint 불변 검증으로 닫았다.
- 좁은 화면 리본 tooltip의 가로 overflow는 420px Browser QA와 source contract로 닫았다.
