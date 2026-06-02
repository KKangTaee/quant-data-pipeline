# Futures Macro Thermometer V1 Plan

## 이걸 하는 이유?

선물 봉차트만으로는 개장 전 시장 성격을 빠르게 판단하기 어렵다. 수집된 주요 선물 일봉을 표준화해 `risk-on`, 금리 부담, 달러 압력, 안전자산 선호 같은 글로벌 매크로 해석을 한 화면에서 보조한다.

## Scope

- 주요 선물 1년 일봉 수집을 허용하는 `1d` interval support
- Streamlit-free macro thermometer service
- 점수 산출 로직과 문장 생성 로직 분리
- `Workspace > Overview > Futures Monitor` 내부 분석 탭
- `Workspace > Ingestion`에서 일봉 backfill 실행 가능
- 서비스 계약 테스트와 Browser QA

## Non Goals

- 투자 판단 자동화
- 정규장 방향 예측 보장
- live order, alert, rebalance
- exchange-grade realtime provider 전환

## Proposed File Areas

| Area | Files |
| --- | --- |
| Collector | `finance/data/futures_market.py` |
| Service | `app/services/futures_macro_thermometer.py` |
| Overview UI | `app/web/overview_dashboard.py` |
| Ingestion UI | `app/web/streamlit_app.py` |
| Tests | `tests/test_service_contracts.py` |
| Docs | `.aiworkspace/note/finance/docs/` |

## Done Criteria

- 1년 일봉 backfill이 가능하다.
- 점수 6종과 티커별 standardized move / 기간 수익률 / 252일 위치가 계산된다.
- 시장 해석 문장, 시나리오, 근거 티커, 주의 문구가 UI에 노출된다.
- 기존 선물 차트 / refresh 기능은 유지된다.
- focused tests, compile, diff check, Browser QA가 통과한다.
