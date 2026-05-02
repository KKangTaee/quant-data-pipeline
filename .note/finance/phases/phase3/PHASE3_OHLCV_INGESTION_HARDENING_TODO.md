# Phase 3 OHLCV Ingestion Hardening TODO

## 목적
이 문서는 stock + ETF 공통 OHLCV 수집 경로를
안정화하고 최적화하는 작업 보드다.

## 현재 챕터 범위

1. `nyse_price_history` 저장 구조 판단
2. OHLCV fetch / write 성능 개선
3. Daily Market Update가 stock + ETF를 올바르게 반영하도록 수정
4. 실제 ETF 심볼 적재 검증

## 큰 TODO 보드

### A. Storage Decision
상태:
- `completed`

세부 작업:
- `[completed]` stock + ETF를 동일 price table로 유지할지 결정
  - loader / backtest / query 경로 관점에서 판단

### B. Ingestion Optimization
상태:
- `completed`

세부 작업:
- `[completed]` yfinance batch fetch 병목 완화
  - chunk / retry / parallel fetch 구조 개선
- `[completed]` start/end 처리 보강
  - 기간 지정 수집 정확도 개선
- `[completed]` OHLCV 결과 통계 보강
  - missing symbol / processed symbol 집계 개선

### C. Daily Market Update Correctness
상태:
- `completed`

세부 작업:
- `[completed]` Manual 심볼 입력 해석 UX 정리
  - preset/custom 혼동 제거
- `[completed]` Daily Market Update 기본 source 정리
  - broad market refresh에서 ETF 포함 기본값 적용

### D. Validation
상태:
- `completed`

세부 작업:
- `[completed]` ETF OHLCV 적재 검증
  - `VIG`, `SCHD`, `DGRO`, `GLD`
- `[completed]` DB 기반 sample 재검증
  - `get_equal_weight_from_db(...)`

## 현재 작업 중 항목

현재 `in_progress`:
- `없음`

바로 다음 체크 대상:
- `다음 스텝 결정`
