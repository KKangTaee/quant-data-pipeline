# 실무 근거 신속 확인

Date: 2026-09-21
State: complete
Scope: 공개 1차 자료로 방법의 실제 사용과 적용 한계 확인; 새 예측 성능 검증 아님

## 앞선 제안의 근거 수준 정정

앞선 compact 가이드는 로컬 코드·DB, 시간 순서 검증·비율 불확실성 등 통계 방법론을 확인한 뒤 만든 제안이었다. 동일한 제품 사용 방식이 실무에 존재하는지까지 충분히 조사한 제안은 아니었다. 세 영역 UI, 선택 자산·조건·horizon은 이 제품을 위한 설계 판단이지 외부 기관이 인증한 설계가 아니다.

이번 확인 결과, **조건/유사 상황을 정의 → 과거 이후 자산 결과를 집계 → 기준과 비교해 판단에 활용**하는 분석 계열에는 실제 상용 리서치·위험관리 근거가 있다. 이를 근거로 연구 도구 개발은 타당하다고 판단한다. 우리 선물 조건의 예측 우위와 확률 calibration은 아직 검증되지 않았다.

## 직접적인 근거

1. [SentimenTrader 공개 화면](https://sentimentrader.com/)에는 최근 5거래일 패턴과 유사한 과거 패턴을 찾고 이후 1주·2주·1개월 등 성과를 보여주는 기능 설명과 표가 있다. **현재와 비슷한 과거 → 이후 실제 결과**라는 제안과 가장 직접적으로 맞닿는다. 공개 페이지의 빈 최신값/0건을 실제 현재 결과로 해석하지 않았고 유료 engine은 실행하지 않았다.
2. [SentimenTrader 공식 API](https://st-tools.sentimentrader.com/api-docs/backtest)는 조건 기반 backtest와 결과의 Total Positive / Total Negative / Each Return / EntryDate / ExitDate 등을 문서화한다. 조건별 결과 수와 사례를 추적하는 계산 계약이 실제 제품에 존재한다는 근거다. 문서의 예시 수익이나 승률을 검증된 실적으로 인용하지 않는다.
3. [MSCI의 stress-test 방법론](https://www.msci.com/research-and-insights/blog-post/building-predictive-stress-tests-msci-best-practices)은 시나리오를 정량화하고 다른 위험요인·포트폴리오로 파급시킨 뒤 견고성을 점검하는 절차를 제시한다. 교차자산 조건부 해석의 인접 실무 근거다. 특정 상황의 발생 확률이나 다음 5일 예측 정확도를 입증하지 않는다.
4. [Vanguard의 advisor stress testing](https://advisors.vanguard.com/strategies/portfolio-strategies/portfolio-analysis/stress-testing)은 역사적 사건·가상 충격과 portfolio/sleeve별 영향을 비교하는 workflow를 설명한다. 위험 맥락의 실무 활용 사례이며 우리 n/N 전망과 동일한 방법은 아니다.
5. [CFA Institute Backtesting & Simulation](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/backtesting-and-simulation)은 rolling-window 검증을 업계에서 쓰는 방법으로 설명하고, look-ahead/survivorship bias와 구조 변화, 역사적 분포가 미래를 대표한다는 가정의 한계를 다룬다. 우리 공개 기준에 시간 순서 검증을 두는 근거다.

## 검증된 부분과 아닌 부분

| 내용 | 판정 |
|---|---|
| 과거 조건/유사 상황 뒤 자산 움직임을 집계하는 방식 | 실제 상용 리서치에 문서·공개 화면 근거 있음 |
| 여러 자산을 함께 보고 시나리오 영향을 해석하는 방식 | 기관 위험관리 방법론에 근거 있음 |
| 과거 빈도와 기준 대비 차이를 사용자 근거로 제공 | 타당한 연구 기능; 표본·편향·비교 기준 확인 필요 |
| 과거 65%를 이번에도 정확히 65%로 표시 | 검증 전 불가; 가이드 예시 수치는 모두 가상 |
| 현재 선물군 가중치·±0.5 기준·5D/20D가 최선 | 확인되지 않음; 설계 후보 |
| 현재 UI 세 영역이 업계 표준 | 그런 주장은 하지 않음; 사용자 목적에 맞춘 제품 제안 |
| 우리 데이터로 유용한 forecast를 만들 수 있는지 | 미검증; 실제 outcome 정의와 OOS pilot 필요 |

## 개발 방향에 적용할 조건

1. 가격 조건과 임계값·대상·horizon을 먼저 고정하고 이후 결과를 본다. 많은 후보 중 잘 나온 사례만 선택하지 않는다.
2. 실제 자산 수익률로 측정하고 n/N·분포·동일 기간 baseline을 함께 제공한다. 자산 자체 추세만 쓴 단순 기준보다 정보가 추가되는지도 확인한다.
3. 연속 사건과 겹친 horizon을 중복 독립 표본처럼 세지 않고 불확실성·반대 사례·기간 안정성을 보여준다.
4. 과거 시점의 관측 가능 정보만으로 반복 평가하고, 마지막 남겨둔 기간에서 검증한다. roll·배당·분할·세션 마감 시각도 맞춘다.
5. 검증 실패 시 과거 관측표는 유지하고 전망의 우위 미확인을 표시한다. 기관이 같은 계열의 방법을 쓴다는 이유로 예측력 있는 것으로 승격하지 않는다.

## 신속 판정

개발 방향을 유지하되 첫 완료 조건은 ‘예측 숫자가 나옴’이 아니라 **실제 조건별 사례를 재현하고 기준 대비 정보가 있는지 확인함**으로 둔다. SPY/QQQ/TLT·향후 5거래일의 좁은 pilot부터 실제 비교를 수행하고, 20D 및 공동 시나리오는 같은 검증 계약으로 확장한다.

공식 자료 확인·적용 한계·개발 조건의 1~3차 신속 검증은 완료했다. 남은 단계는 우리 데이터로 하는 실제 통계 pilot이며, 이번 요청에서 코드 변경·수집·모형 실행은 하지 않았다.
