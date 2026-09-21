# 근거 목록

Access date: 2026-09-21

## 로컬 구현·관측

| 근거 | 위치 | 확인 내용 |
|---|---|---|
| 구현 | app/jobs/overview_actions.py:478 | 일봉 routine/bootstrap, 장중 수집, materialization 호출 |
| 구현 | app/services/futures_macro_snapshot.py:325 | fingerprint 재사용과 별도 macro/outlook builder |
| 구현 | app/services/futures_macro_pattern_validation.py:1743 | forward outcomes와 nested 두 horizon 검증 |
| 구현 | app/services/futures_macro_outlook_model.py:210 | momentum 거리 계산 뒤 macro 입력 결측으로 후보 제외 |
| 구현 | app/services/futures_macro_pattern.py:99 | return/60D volatility, family/window 집계 |
| 구현 | app/services/futures_macro_pattern.py:229 | transition과 regime 분류 |
| 구현 | app/services/futures_macro_thermometer.py:189 | 선물군 구성·가중치·대리 지표 정의 |
| 구현 | app/web/overview/futures_macro_helpers.py:760 | 핵심/확인축, 부호, 시나리오 문구 |
| 구현 | app/web/overview/futures_macro_helpers.py:1316 | 가장 큰 5D 축을 고르는 재가격화 해석 |
| 구현 | app/services/futures_macro_intraday.py | 공통 closed-bar cutoff, stale fallback, 잠정 일봉 |
| 구현 | finance/data/futures_market.py:382 | yfinance, auto_adjust=False, threads=False |
| 구현 | app/services/futures_macro_context.py | H0 contribution에서 macro context 추출 |
| 구현 | finance/economic_cycle_pipeline.py:712 | H0 factor contribution과 top evidence 분리 저장 |
| 구현 | finance/economic_cycle_model.py:13 | H0 4개, forecast 추가 2개 feature 계약 |
| 로그 | .aiworkspace/note/finance/run_history/WEB_APP_RUN_HISTORY.jsonl | 09-21 09:09:04 실행 70.567517초 및 단계별 timing; generated, 미커밋 |
| DB 관측 | 저장된 futures macro snapshot, 09-18 as-of | 5D/20D NO_EDGE, Brier baseline, ribbon 분포 |
| 계산 재현 | 독립 performance audit, SELECT-only | 동일 fingerprint 입력 준비·thermometer·outlook timing, 내부 호출 수, context 결측 |
| 계측 스크립트 | /tmp/futures_macro_readonly_timings.py, /tmp/futures_macro_readonly_summary.py | 계측 및 SELECT-only snapshot 요약; 로컬 임시 artifact, 미커밋 |
| 브라우저 | http://127.0.0.1:8501/overview?overview_tab=futures-macro | 현재 1D/5D/20D 상태, 재가격화 문구, 이력 DOM 60개 집계 |
| 스크린샷 | .playwright-mcp/futures-macro-audit-20260921.png | 조사 시점 재가격화 영역; generated, 미커밋 |

## 외부 1차 자료

| 출처 | URL | 뒷받침하는 사실 |
|---|---|---|
| CME Group | https://www.cmegroup.com/trading/interest-rates/basics-of-us-treasury-futures.html | 국채 가격과 금리/수익률의 역관계 |
| CME Group | https://www.cmegroup.com/market-data/cme-group-continuous-price-series.html | 연속 선물의 active/front contract 구성과 roll 정의 |

코드와 측정값은 구현 사실, ‘분리하면 크게 줄일 수 있다’와 UI 우선순위는 근거에 기반한 권고다. 개선 후 실측처럼 표현하지 않는다.

## Compact 조건부 전망 가이드의 추가 근거

- `app/services/futures_macro_pattern_validation.py:382`, `:1515`: 실제 자산 수익률 대신 family 점수 변화를 만드는 기존 outcome/pathways 계약.
- `app/services/futures_macro_outlook_model.py:200`: 과거-only train 및 결과 horizon 간격으로 중복을 줄이는 analog 선택.
- `finance/loaders/price.py:17`, `finance/loaders/economic_cycle_assets.py:46`: DB 기반 주식/ETF·선물 reader의 재사용 범위.
- SELECT-only / MySQL TRANSACTION READ ONLY로 `finance_price.nyse_price_history`의 SPY/QQQ/TLT/GLD/USO/UUP 및 `futures_ohlcv` 주요 7개 symbol의 count/min/max/adj_close non-null을 집계했다. provider fetch·DB write 없음. 실제 조건부 n/N 계산은 하지 않았다.
- https://otexts.com/fpp3/tscv.html — 2026-09-21 접근. 저자 제공 교재, rolling-origin 시계열 검증과 미래 데이터 제외.
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm — 2026-09-21 접근. NIST, 이항 비율의 Wilson/정확 구간.
- https://www.cmegroup.com/insights/economic-research/2026/uncovering-the-hidden-drivers-of-commodities.html — 2026-09-21 접근. CME 공식 분석, 자산 관계의 환경별 변화; 현재 앱의 실제 관계나 예측 성과를 뒷받침하는 출처는 아님.
