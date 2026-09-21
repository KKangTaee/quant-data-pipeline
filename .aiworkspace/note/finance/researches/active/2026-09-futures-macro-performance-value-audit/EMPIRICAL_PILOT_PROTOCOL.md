# 조건부 결과 계산의 예비 검증 — 결과 확인 전 고정

Date: 2026-09-21
State: complete
Purpose: 다른 업체의 사용 여부가 아니라 제안한 계산이 실제 데이터에서 어떤 근거·한계를 갖는지 확인한다.

## 고정 범위

- condition: 현재 앱의 완료 일봉 feature에서 rate_pressure__5d_z >= 0.5 AND dollar_pressure__5d_z >= 0.5. 앞선 가이드의 예시 조건 하나만 사용한다. 결과에 따라 조건/threshold/horizon/대상을 변경하지 않는다.
- target: SPY / QQQ / TLT, horizon 5개 ETF 거래 세션.
- 관측 시점: 완료 선물 일봉 date. target 시작은 그 date 이후 첫 ETF 거래 세션의 조정 시가, 종료는 시작 포함 5번째 거래 세션의 조정 종가다. 현금 배당/분할 adjustment factor는 adj_close/close를 시가에도 적용하며 이는 조정 가격 변화 proxy다.
- 데이터: 현재 저장된 DB를 SELECT-only로 읽는다. 수집·DB write 없음. 2016년 이후 공통 이력, 실제 조회 당시 완료 가능한 마지막 outcome까지만 사용한다.
- 조건 episode: 조건이 false→true가 된 첫 ETF 분석 날짜. 직전 선택 episode의 결과 기간과 겹치는 origin은 제외한다. 지속 구간의 매일을 별도 사례로 세지 않는다.
- 구간 비교: 2020년 말까지와 2021년 이후를 모두 제시한다. 초기 구간으로 현재 조건을 tuning하지 않는다.
- 기술 통계: n/N 하락, return 중앙값, Wilson 95% 구간(독립 binomial 근사에 한정), 같은 기간 모든 유효일의 unconditional 비율. 중첩되는 baseline은 기술적 기준이며 독립 검정 표본처럼 처리하지 않는다.
- 순차 평가: 2021년 이후 각 episode에서 그 시점 이전에 결과가 완성된 과거 episode만으로 하락 비율을 추정한다. 과거 episode >=30일 때만 score한다. 비교는 그 시점까지 결과가 완성된 unconditional 하락 비율과 target 자신의 직전 5일 방향을 조건으로 한 단순 기준이다. Brier loss 차이를 같은 평가 사례에서 비교한다.
- 데이터 건전성: 가격 누락·양수/유한값·adjustment 여부·unique date·미래 outcome 누출을 확인한다. 기존 feature의 과거 구간을 잘라 재계산해 prefix 일치 여부를 확인한다.
- 추론 한계: 단일 조건/세 target/단일 horizon의 screening이다. 최근 보정된 가격의 vintage, provider 계약 roll, 신호당 적은 사례, 결과 비교의 다중성 때문에 전체 설계의 검증 완료 또는 예측 우위를 선언하지 않는다. 표본 부족도 결과다.

## 산출물

임시 계산 스크립트와 JSON 출력은 generated artifact로 관리하며 commit하지 않는다. 실제 측정값·판정·남은 공백은 EMPIRICAL_PILOT_RESULT.md에 요약한다. 기존 가상 n/N을 실제 결과처럼 사용하지 않는다.

실행 완료: [EMPIRICAL_PILOT_RESULT.md](./EMPIRICAL_PILOT_RESULT.md). 고정 조건·대상·horizon을 유지했다.
