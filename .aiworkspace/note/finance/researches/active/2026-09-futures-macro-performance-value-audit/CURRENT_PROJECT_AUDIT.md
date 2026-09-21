# 현재 제품 감사

Date: 2026-09-21
Evidence: 코드·브라우저·저장된 실행 및 검증 결과·읽기 전용 계산 재현

## 제품 역할과 사용 흐름

선물 매크로는 사용자용 시장 관측 화면이다. 운영 콘솔이나 자동매매 화면이 아니다. 주식·국채·통화·원자재의 가격 움직임을 묶어 현재 해석, 반대 근거, 다음 관측 조건을 제공한다. 화면의 1D / 5D / 20D는 지나온 기간이며 미래 수익률 전망 기간이 아니다. 장중에는 완료 일봉과 공통 시점까지 닫힌 5분봉으로 잠정 관측을 구성한다.

좋은 사용 흐름은 관측 시점 확인 → 가장 두드러진 축 확인 → 다른 축의 동조/반대 확인 → 관련 보유자산의 민감도와 다음 확인 조건 점검이다. 현재 UI에는 정보가 있지만 각 섹션이 이 흐름에서 맡는 역할이 충분히 전달되지 않는다.

## 갱신 실측

2026-09-21 09:09:04~09:10:15 KST, collect_futures_macro_daily 기록 1건:

| 단계 | 초 | 의미 |
|---|---:|---|
| 전체 | 70.567517 | job 전체; 브라우저 전 구간 지연과 동일한 측정은 아님 |
| 일봉 수집·저장 | 6.102276 | 17개 symbol, 1년 overlap, 4,267 rows |
| 입력 비교 | 3.101733 | 완료 세션 입력 fingerprint 비교 |
| snapshot 계산·저장 | 57.831465 | 전체 약 82%; thermometer와 과거 예측 검증을 포함 |
| 나머지 | 약 3.53 | 장중 수집·확정 확인 등 나머지 경로; 개별 시간은 로그로 분리 불가 |

수집 내부 download/normalize는 5.876897초, UPSERT는 0.209884초다. 이 실행에는 10년 bootstrap이 없었다. 장중 2d/5m 수집도 수행됐다. 따라서 이 사례의 주 병목을 DB 쓰기, 최초 10년 다운로드 또는 네트워크만으로 설명할 수 없다.

완료 입력이 같고 schema/algorithm이 호환되면 nested replay를 재사용하는 guard가 이미 존재한다. 이번 실행은 재사용 조건을 만족하지 않아 materialization을 수행했다. 이전 row와의 입력·schema·algorithm 중 무엇이 달랐는지는 이 로그만으로 특정할 수 없다. 모든 클릭이 반드시 70초 걸린다는 뜻은 아니다.

## 읽기 전용 재현

동일 평가 시점과 저장된 입력 fingerprint `eba5e197e07e922ad714a650ca1df2c8c7e20da476c027dfb818df54dc261f12`로 provider fetch와 DB 쓰기 없이 계산했다. 완료 candle 43,279행, feature 2,403세션, 저장된 경기국면 replay 116행, 공식 이벤트 26행을 사용했다.

- 입력 준비 3.468793초; thermometer의 legacy validation 제외 계산 1.488152초.
- pattern outlook 60.334051초: forward outcome 생성 11.142초, nested 5D/20D 검증 49.191초.
- 내부 forecast 7,481회, analog ranking 5,798회, 모델 선택 53회. 내부 타이머는 중첩하므로 서로 합산하지 않는다.
- 각 예측 시점에서 기준모형 2개와 후보 4개 × temperature 3개를 검토한다. 시점별 train scaling, 거리 계산, sorting, de-overlap이 반복된다.
- `include_validation=False`는 thermometer의 legacy validation만 끈다. 별도로 호출하는 `build_pattern_outlook_snapshot`은 5D/20D nested 검증을 수행한다.
- 과거 경기국면 replay를 새로 만드는 시간이 아니라, 저장된 replay를 이용한 선물 outlook 검증 시간이다.

## 화면의 지표가 실제로 뜻하는 것

종목별 일간 수익률을 당일까지의 60일 변동성으로 나누고, 부호/가중치를 적용해 선물군 평균을 만든다. 5D와 20D는 이 일별 값의 합을 각각 √5, √20으로 나눈다. 표시 임계값은 ±0.5다. 이는 수익률 %, 미래 확률 또는 통계적 유의수준이 아니다. 평균을 뺀 표준 z-score도 아니며 자산군 상관구조까지 표준화한 척도도 아니다.

| 표시 | 실제 입력 | 올바른 해석 경계 |
|---|---|---|
| 위험선호 | ES/NQ/YM/RTY | 미국 주가지수 선물의 가격 방향 |
| 금리 부담 | ZN/ZB 수익률 부호 반전 | 국채선물 약세를 금리 상승 압력의 대리 지표로 사용; 실제 금리변화 bp 아님 |
| 달러 압력 | EUR/JPY/GBP/AUD/CAD 선물 부호 반전 | 주요 통화 대비 달러 강세 압력; DXY 자체 수익률 아님 |
| 물가 압력 | CL/HG/NG, NG 가중치 0.5 | 원자재 가격 압력; CPI나 기대인플레이션을 직접 측정하지 않음 |
| 성장 기대 | RTY/HG/CL/AUD | 경기민감 가격의 동조; GDP 전망치 아님 |
| 방어 수요 | GC/ZN/ZB/JPY | 금·국채·엔 가격의 동조; 실제 자금유입 측정 아님 |

17개 수집 symbol 중 15개가 점수 계산에 직접 쓰인다. DXY는 공유 맥락, 은은 원시 관측으로 별도 보존한다. 여러 군에 국채·원유·구리·엔·호주달러 등이 중복되므로 확인 신호를 완전히 독립된 증거로 세면 안 된다.

## 2026-09-21 관측 화면의 읽기

브라우저에 표시된 09-21 세션 장중 잠정 관측 기준이다. 마지막 공통 관측은 미국 동부 09-20 20:00(한국 09-21 09:00), 완료 일봉 기준은 09-18이다. 이후 시장 상황을 뜻하지 않는다.

| 축 | 1D 새 변화 | 5D 단기 방향 | 20D 배경 |
|---|---|---|---|
| 위험선호 | 강화 | 중립 | 중립 |
| 금리 부담 | 확대 | 확대 | 확대 |
| 달러 압력 | 중립 | 중립 | 확대 |
| 물가 압력 | 중립 | 중립 | 중립 |

성장 기대와 방어 수요의 5D도 중립이다. 따라서 가장 유력한 관측은 국채 약세/금리 부담이며, 시장 전체의 위험회피라고 단정할 정도의 교차자산 확인은 없다. 오늘 주가지수 강세는 최근 5D 방향의 확립과 구분해야 한다.

‘혼재’는 명확한 위험선호·방어·물가금리 부담 조건에 해당하지 않는 fallback도 포함한다. ‘지속 중’은 적어도 한 선물군의 5D와 20D 방향이 정렬됐다는 규칙이지 시장 전체의 추세 지속 확률이 아니다. ‘반대 근거 없음’은 관측된 군 중 임계값을 넘는 반대 신호가 없다는 뜻이며 해석의 확증이 아니다.

최근 화면의 60개 관측(06-29~09-21, 마지막 잠정치 포함)은 혼재 53, 위험선호 3, 물가금리 부담 3, 방어 1이다. 저장된 완료 일봉 60세션(06-26~09-18)도 같은 분포다. 한 창의 88.3%가 혼재이므로 현재 색상 이력은 변화 구별에 주는 정보량이 제한적이다. 전체 역사에 일반화하지 않는다.

## 예측 유효성

저장된 09-18 완료 snapshot에서 미래 5D/20D의 probability / coordinate / vector gate는 모두 `NO_EDGE`다.

| 예측 horizon | 현재 선택 | OOS Brier | 무조건부 기준 Brier | 판정 |
|---|---|---:|---:|---|
| 5D | M1_MOMENTUM, temperature 2 | 0.5468906 | 0.5457589 | 더 낮을수록 좋은 지표에서 기준보다 소폭 나쁨 |
| 20D | B0_UNCONDITIONAL | 0.4722321 | 0.4722321 | 기준모형 선택, 개선 없음 |

5D는 평가 338개/26 folds, 20D는 100개/25 folds이며 fold improvement ratio는 모두 0이다. `READY`는 계산 산출물이 있다는 뜻이지 예측 우위가 있다는 뜻이 아니다. 이 검증은 미래 자체 체제/좌표 등에 대한 검증이다. 매매비용을 고려한 포트폴리오 수익 개선 검증을 대신하지 않는다. `NO_EDGE`는 현재 가격 관측이 무효라는 뜻도, 영구히 예측력이 없다는 증명도 아니다. 현재 확인한 근거로 예측 우위를 주장할 수 없다는 뜻이다.

추가 발견: macro context 6개 필드 중 financial_leading_contribution / inflation_policy_contribution이 2,403세션 모두 결측이다. 경기국면 H0 설명은 activity/labor 4개 contribution만 저장하지만 선물 context는 forecast용 두 contribution까지 같은 JSON에서 요구한다. 그래서 M2 후보는 입력을 충족하지 못한다. momentum 거리를 먼저 계산한 뒤 탈락하므로 불필요한 계산도 발생한다. 현재 ‘추가 OOS 개선이 없었다’는 설명은 ‘입력 부족으로 평가 불가’와 구분해야 한다. 원점수나 0으로 대체하는 것은 동일 의미의 복구가 아니다.

## 소유 경계와 문서 정합성

| 영역 | 소유 코드 |
|---|---|
| 사용자 갱신 실행 | app/jobs/overview_actions.py |
| 저장 및 입력 재사용 | app/services/futures_macro_snapshot.py |
| 가격 관측 점수·체제 | app/services/futures_macro_pattern.py, futures_macro_thermometer.py |
| 장중 관측 | app/services/futures_macro_intraday.py |
| 예측·nested 검증 | app/services/futures_macro_pattern_validation.py, futures_macro_outlook_model.py |
| macro context 계약 | app/services/futures_macro_context.py, finance/economic_cycle_pipeline.py, finance/economic_cycle_model.py |
| UI 해석 payload | app/web/overview/futures_macro_helpers.py |
| React 표시 | app/web/streamlit_components/futures_macro_workbench/ |
| 수집·일봉/장중·snapshot 저장 | finance/data/futures_market.py, futures_session_finalization.py, futures_macro_snapshot.py |

PROJECT_MAP은 현재 관측 중심 화면과 hidden shadow 검증 보존을 정확히 구분한다. 다만 검증의 보존이 사용자 동기 갱신 경로의 필수 계산이어야 하는지는 별개의 설계 문제다. 일부 legacy header의 미래 1주·1개월 표현은 현재 정상 React 화면의 의미와 다르므로 향후 fallback 수정 시 확인한다.

## 데이터와 해석의 한계

- 공급사 연속 선물 가격을 사용한다. 명시적인 계약 roll 보정은 관측 계산 경로에서 확인되지 않았으며, 실제 이번 신호에 roll 왜곡이 있었다고 확인한 것은 아니다.
- 가격 상승 원인은 성장, 공급 충격, 포지션 정리 등 여러 가지일 수 있다. 고정 부호와 문장 규칙으로 인과관계를 검증할 수 없다.
- 현재 rolling feature는 해당 시점까지의 데이터로 계산하며, nested 모델은 과거-only train과 horizon separation을 둔다. 이번 감사가 데이터 vintage·계약 교체·전체 PIT 정확성을 전수 보증하지는 않는다.
- 장중 잠정치는 완결 일봉과 비교 시간이 다르며 일중 변동성 계절성 보정을 확인하지 않았다. 동일한 ±0.5 판정의 체감은 시간대에 따라 달라질 수 있다.
- 고정 17개 선물 universe로 주식 상장폐지 survivorship 문제가 주 대상은 아니지만, symbol별 역사·계약 구성·데이터 결측의 차이는 남는다.
