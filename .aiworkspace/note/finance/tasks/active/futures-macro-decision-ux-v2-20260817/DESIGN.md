# Futures Macro Decision UX V2 Design

State: complete
Last Updated: 2026-08-17

## 승인 기록

- 2026-08-17: 사용자가 `의사결정 중심 재구성` 권장안 2를 승인했다.
- 승인 범위는 compact hero, 활성 세션 장중 수집, 최신 완료 일봉 fallback, 결과 중심
  1D/5D/20D, 정확한 `NO_EDGE` 표현, `Next Check` 제거다.

## 이걸 하는 이유?

현재 Futures Macro 화면은 데이터와 검증 근거를 보유하지만 방법론 안내와 반복된 상태 카드가 실제
결론보다 앞에 보인다. 또한 장중 5분봉 수집 조건이 daily finalization probe에 묶여 있어 Sunday
evening처럼 활성 trade-date가 존재해도 최신 관측 수집이 생략될 수 있다.

사용자는 첫 화면에서 다음 질문을 끝낼 수 있어야 한다.

1. 지금 보는 값은 장중 관측인가, 마지막 완료 일봉인가?
2. 1D / 5D / 20D에서 무엇이 강화, 약화, 지속, 반전됐는가?
3. 현재 5D 흐름을 다음 5거래일로 연장할 검증된 근거가 있는가?

## 제품 계약

### 최신 데이터 갱신

- `active_futures_session_date(evaluation_time)`가 활성 trade-date를 반환하면 daily session
  probe의 상태와 무관하게 bounded `2d/5m` 수집을 한 번 시도한다.
- daily overlap 수집은 기존대로 매번 실행해 최신 완료 일봉을 확보한다.
- settlement-stable finalization은 기존 probe와 17/17 atomic 계약을 유지하며, 미리 수집한
  5분봉 결과를 재사용한다.
- 활성 세션이 없으면 5분봉 수집을 생략하고 마지막 정상 완료 일봉을 사용한다.
- 활성 세션이지만 provider bar가 없거나 적격 family가 부족하면 마지막 정상 완료 일봉을
  유지하고 `새 장중 관측 없음`을 사용자에게 표시한다.
- incomplete/stale 장중 값은 완료 값으로 승격하지 않고 forecast history에도 넣지 않는다.

### 상단 hero

- Futures variant에만 compact layout을 적용해 다른 Research 화면을 바꾸지 않는다.
- 제목, 체제, 한 줄 결론을 왼쪽 상단부터 바로 읽게 하고 facts는 오른쪽 2x2로 배치한다.
- facts는 `현재 데이터`, `현재 기준`, `검증 기준`, `관측 범위`로 제한한다.
- command detail은 meta pill에서 제거하고 실제 근거 최대 2개만 남긴다.
- 장중 fallback일 때만 compact notice로 `새 장중 관측 없음 · YYYY-MM-DD 완료 일봉 사용`을
  표시한다. 비거래 시간의 정상 완료 일봉 사용은 경고로 취급하지 않는다.

### 1D / 5D / 20D 결과

상단 읽기 가이드 rail과 카드 하단 instruction은 제거한다. 세 카드는 결과만 말한다.

- 1D: 5D 대비 `새로 나타남`, `반전`, `기존 방향 지속`, `변화 없음`을 family별로 요약한다.
- 5D: 핵심 family를 위험선호/방어 방향으로 정규화해 `정렬`, `엇갈림`, `단일 축`, `우위 없음`을
  말한다.
- 20D: 5D와 20D의 material family 관계를 `지속`, `반전`, `혼재`, `관계 없음`으로 말한다.
- 자유 생성 문장이 아니라 family value와 `SIGNAL_Z_THRESHOLD`에서 결정적으로 생성한다.
- confirmation 문구에서도 `확인합니다` 같은 안내형 종결을 제거한다.

### 향후 5거래일 검증

- validation gate는 숨기지 않는다. 음성 검증 결과도 잘못된 예측을 막는 제품 근거이기 때문이다.
- `NO_EDGE`는 `검증 완료 · 향후 5거래일 예측 우위 없음`으로 표시한다.
- 표본과 평가 수가 충분하다는 사실과 모델 Brier가 기본 빈도보다 나쁘다는 사실을 함께 쓴다.
- 정확한 통과 날짜를 약속하지 않는다. 새 완료 세션마다 재평가되지만 데이터 증가만으로
  `VERIFIED`가 보장되지 않는다.
- publication threshold, baseline, Brier/log-loss/calibration/bootstrap 판정은 변경하지 않는다.
- metrics는 기준일, 독립 표본, 시간순 평가, baseline 대비 Brier 차이로 압축한다.

### Next Check

- `CalculationScopeSection`과 `Next Check` primary section은 제거한다.
- 계산 범위는 재현 근거이므로 `방법론과 품질` disclosure 안에 compact note로 이동한다.
- `change_conditions`는 다른 evidence/pathway 계약에 필요하므로 backend source에서 삭제하지
  않지만 primary decision flow에서는 렌더링하지 않는다.

## 파일 소유권

| 파일 | 변경 책임 |
|---|---|
| `app/jobs/overview_actions.py` | active trade-date 기반 5분봉 수집 routing |
| `app/web/overview/futures_macro_helpers.py` | 결과 narrative, validation copy, fallback provenance, v6 payload |
| `MacroContextSection.tsx` | compact facts와 장중 fallback notice |
| `ShortHorizonDecisionSection.tsx` | guide rail/detail 제거, 결과 카드 렌더링 |
| `ForecastValidationGate.tsx` | 검증 완료/미완료 상태와 Brier delta 표시 |
| `MethodDisclosure.tsx` | 계산 범위의 보조 근거 이동 |
| `FuturesMacroWorkbench.tsx` | v6 contract, Next Check 제거, method scope 연결 |
| `market_research_header/style.css` | Futures 전용 compact hero variant |
| `futures_macro_workbench/src/style.css` | 결과 카드/gate/disclosure compact styling |

DB schema와 기존 table 의미는 바뀌지 않는다.

## 상태별 사용자 결과

| 상태 | 상단 표시 | 현재 관측 | 미래 5D |
|---|---|---|---|
| 활성 세션 + fresh 5m | 장중 잠정 · 기준 시각 | 장중 1D/5D/20D | 완료 일봉 검증 유지 |
| 활성 세션 + partial fresh | 장중 잠정 · 일부 family | 가능한 family 결과 | 완료 일봉 검증 유지 |
| 활성 세션 + no/stale 5m | 새 장중 관측 없음 · 최신 완료 일봉 사용 | 완료 1D/5D/20D | 완료 일봉 검증 유지 |
| 비거래 시간/주말 | 마지막 완료 일봉 | 완료 1D/5D/20D | 완료 일봉 검증 유지 |
| `NO_EDGE` | 검증 완료 · 예측 우위 없음 | 관측 결과 유지 | 미래 연장 금지 |
| `UNAVAILABLE` | 검증 자료 부족 | 관측 결과 유지 | 표본/평가 부족 명시 |

## 접근성과 반응형

- 기존 heading/section landmark와 button keyboard contract를 유지한다.
- desktop에서는 hero fact 2x2, 760px 이하에서는 본문과 facts를 1열로 전환한다.
- 480px 이하 fact는 1열로 전환한다.
- 긴 한국어 결과 문장은 줄바꿈되고 horizontal overflow를 만들지 않는다.

## 제외 범위

- 검증 임계값 완화 또는 모델 재학습
- exchange holiday calendar 신규 도입
- provider 변경, websocket, 자동 refresh
- 실행 job/row/status 진단 패널
- 장중 provisional 값의 snapshot/history 저장

## 완료 조건

- Sunday evening active trade-date가 daily probe `future_session_not_eligible`이어도 5분봉 수집을
  한 번 시도하는 회귀 테스트가 통과한다.
- 비활성 세션은 5분봉을 수집하지 않고 최신 완료 일봉을 유지한다.
- 1D/5D/20D 카드에 안내형 detail이 없고 실제 변화 관계만 표시된다.
- `NO_EDGE`가 충분한 표본의 완료된 음성 결론으로 표시된다.
- `Next Check`가 primary UI에서 사라지고 계산 범위는 방법론 disclosure에 남는다.
- focused Python tests, changed service contracts, TypeScript production build, 실제 DB read와 Browser
  QA가 완료된다.
