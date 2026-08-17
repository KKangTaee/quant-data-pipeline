# Futures Macro Decision UX — Current Project Audit

## 결론 요약

- 최신화 문제는 단순히 휴장 시 완료 일봉을 쓰는 스펙이 아니다. 장중 관측일을 계산하는 로직은
  존재하지만, 5분봉 수집 조건이 daily session probe의 `pending` 상태에 묶여 있어 일요일 저녁 등
  다음 trade-date 장중에 최신 관측 수집이 생략될 수 있다.
- 현재 5거래일 검증은 데이터 부족이나 짧은 검증 범위가 아니다. 실제 snapshot은 독립 표본 120개,
  시간순 평가 325회를 보유하고 있으며 모델이 기본 빈도를 이기지 못해 `NO_EDGE`로 판정됐다.
- 화면은 관측 결과보다 읽는 방법과 계산 규칙을 반복한다. 1D / 5D / 20D 카드는 각 시간축에서
  실제로 일어난 변화·정렬·반전을 말하고, 방법론은 보조 disclosure로 내려야 한다.
- `Next Check`의 현재 내용은 사용자 행동으로 연결되지 않는 threshold 안내다. 주 화면에서는 제거하고,
  계산 범위가 필요하면 방법론 disclosure에 합치는 편이 맞다.

## 제품 약속과 사용자 질문

Futures Macro 화면의 핵심 사용자 질문은 다음 세 가지다.

1. 지금 사용하는 정보는 최신 장중 관측인가, 마지막 완료 일봉인가?
2. 어제·최근 5일·최근 20일 사이에 실제로 무엇이 강화, 약화, 반전, 상쇄됐는가?
3. 관측된 5일 흐름을 다음 5거래일 예측으로 연장할 통계적 근거가 있는가?

현재 화면은 위 질문에 필요한 데이터는 대부분 가지고 있으나, 공간과 문구의 우선순위가 방법론 중심이라
답을 찾는 데 불필요한 해석 비용이 발생한다.

## 화면과 코드 소유 경계

| 영역 | 현재 소유 파일 | 확인된 역할 |
|---|---|---|
| 공통 research hero | `app/web/streamlit_components/market_research_header/ResearchHeader.tsx`, `style.css` | 제목, 근거, 상태 facts, refresh action |
| Futures Macro hero payload | `app/web/streamlit_components/futures_macro_workbench/src/MacroContextSection.tsx` | 현재/완료 관측 구분과 경고 표시 |
| 1D/5D/20D 판단 | `ShortHorizonDecisionSection.tsx`, `app/web/overview/futures_macro_helpers.py` | 시간축별 카드와 문구 생성 |
| 5D 검증 | `ForecastValidationGate.tsx`, `app/services/futures_macro_pattern_validation.py` | walk-forward 결과와 gate 판정 |
| Next Check | `CalculationScopeSection.tsx` | 변화 조건과 계산 범위 표시 |
| refresh orchestration | `app/jobs/overview_actions.py`, `app/jobs/futures_macro_daily_finalization.py` | daily/5m 수집과 완료 일봉 확정 |
| 장중 read model | `app/services/futures_macro_intraday.py` | active trade-date 관측 또는 완료 일봉 fallback |

## 1. 상단 hero 공간 감사

### 확인된 원인

공통 header grid가 왼쪽 본문과 오른쪽 facts rail을 2열로 배치하면서 `align-items: end`를 사용한다.
오른쪽에는 세로 fact 카드 네 개가 쌓이고 왼쪽 본문은 짧아, 왼쪽이 하단 정렬되면서 제목 위에 큰
빈 공간이 생긴다.

### 개선 원칙

- 전역 header를 바로 바꾸지 않고 Futures Macro 범위에서 레이아웃을 조정한다.
- 제목·한 줄 결론·데이터 시점을 하나의 compact decision block으로 묶는다.
- 상태 facts는 세로 4단이 아니라 2x2 또는 가로 compact rail로 바꾼다.
- 경고 box는 데이터가 실제로 오래됐거나 fallback이 발생한 경우에만 표시한다.
- 화면 첫 fold는 `현재 상태`, `무엇이 변했는가`, `어느 시점 데이터인가`를 답해야 한다.

## 2. 최신 데이터 갱신 감사

### 현재 구현

- daily OHLCV overlap 수집은 refresh마다 실행된다.
- 5분봉 수집은 daily session probe가 `pending`일 때만 실행된다.
- read model은 별도로 active futures trade-date를 계산해 장중 관측과 완료 일봉 fallback을 구분한다.

### 확인된 결함

일요일 저녁처럼 CME 다음 trade-date 세션이 열려 있어도 daily probe가
`future_session_not_eligible`이면 5분봉 수집이 실행되지 않는다. 따라서 read model은 현재 세션을
알고 있으면서도 필요한 5분봉이 없어 마지막 완료 일봉으로 fallback한다.

### 권장 동작

1. active trade-date를 daily finalization probe와 독립적으로 계산한다.
2. active trade-date가 마지막 완료 세션보다 최신이면 daily probe 상태와 무관하게 5분봉 수집을 시도한다.
3. 휴장, 장 종료, provider 무응답 등으로 새 bar가 없으면 daily overlap 결과를 다시 읽고 마지막 정상 완료
   세션을 사용한다.
4. UI는 실패처럼 보이는 generic 상태 대신 `새 관측 없음 · 2026-08-14 완료 세션 사용`처럼 현재
   사용 데이터와 이유를 함께 표시한다.
5. stale 또는 incomplete 장중 관측을 완료 데이터처럼 승격하지 않는다.

이 규칙은 장중에는 최신 관측을 우선하고, 새 자료가 없을 때는 최신 정상 완료 일봉을 보장한다.

## 3. 1D / 5D / 20D 판단 흐름 감사

### 현재 문제

현재 detail 문구는 다음처럼 사용법을 설명한다.

- 마지막 관측 세션의 변화가 5D 방향을 바꾸는지 확인
- 여러 family가 같은 방향인지 확인
- 5D가 20D 배경을 이어가거나 반전하는지 확인

위 문구는 카드 제목과 중복되며 실제 결과를 말하지 않는다. 상단의 1D/5D/20D rail도 카드 제목과
정보가 겹친다.

### 권장 정보 구조

- **1D — 새 변화:** 5D와 비교해 새로 강화·완화·반전된 family를 말한다. 변화가 서로 상쇄되면
  `금리 부담은 확대됐지만 달러 압력은 완화돼 새 충격은 상쇄됩니다`처럼 결론을 쓴다.
- **5D — 현재 단기 방향:** material family의 동조 여부를 말한다. 정렬되지 않았으면
  `핵심축이 같은 방향으로 정렬되지 않아 단기 우위가 없습니다`라고 명시한다.
- **20D — 배경과의 관계:** 5D와 20D가 지속, 반전, 혼재, 무변화 중 무엇인지 말한다. 지속과 반전이
  동시에 있으면 둘 다 보여주고 `혼재`로 결론 낸다.

상단 읽기 가이드와 카드 하단 instruction은 제거하고, 결과 문장만 남긴다. 세부 family 표는 근거로
유지하되 첫 화면의 주인공으로 올리지 않는다.

## 4. 향후 5거래일 검증 감사

### 실제 상태

현재 DB snapshot의 5D 검증 결과는 다음과 같다.

| 항목 | 실제 값 | 판정 |
|---|---:|---|
| 독립 표본 | 120 | 최소 60 충족 |
| 시간순 평가 | 325 | 최소 60 충족 |
| 모델 Brier | 0.558212 | 기본 빈도 0.556655보다 나쁨 |
| 모델 Log loss | 1.055494 | 기본 빈도 1.053533보다 나쁨 |
| Calibration error | 0.015622 | 기준 0.10 충족 |
| Fold 개선 비율 | 0.0 | 기준 0.60 미충족 |
| Bootstrap 개선 하한 | -0.159968 | 0 초과 기준 미충족 |

### 해석

- `NO_EDGE`는 `데이터가 없어 확인 못함`이 아니다.
- 검증은 이미 실행됐고, 현재 모델은 기본 빈도보다 안정적으로 낫지 않다는 음성 결론이다.
- 언제 `VERIFIED`가 될지 특정 날짜를 계산할 수 없다. 새 완료 세션마다 재검증되지만 데이터가 더
  쌓인다고 자동으로 통과하지 않으며, 현재 모델은 계속 `NO_EDGE`일 수 있다.

### 권장 표현

- 제목: `검증 완료 · 향후 5거래일 예측 우위 없음`
- 근거: `독립 표본 120개·시간순 평가 325회에서 모델 오차가 기본 빈도보다 높았습니다.`
- 정책: `현재 5D 흐름을 다음 5거래일 방향 예측으로 연장하지 않습니다.`
- 선택 보조값: `Brier +0.0016p`처럼 baseline 대비 차이를 짧게 표시한다.

이 gate의 가치는 예측을 억지로 노출하지 않는 데 있다. 다만 `확인 안 됨`처럼 대기 상태로 오해되는
copy는 반드시 상태 계약에 맞게 고쳐야 한다.

## 5. Next Check 감사

현재 항목은 `5D family score가 material threshold를 넘는지 확인합니다`라는 계산 규칙을 보여준다.
사용자가 다음에 할 수 있는 행동이나 관측 결과가 아니므로 주 화면에서 제거하는 것이 타당하다.

필요한 계산 범위와 threshold 설명은 `방법론` disclosure에 합치고 기본 상태에서는 접는다.

## 추천 우선순위

1. **1차 — 의미 계약 정리:** refresh fallback, validation status, 1D/5D/20D 결과 문장 계약 확정
2. **2차 — 화면 재배치:** compact hero, 결과 중심 3단 흐름, Next Check 제거, 검증 gate 재작성
3. **3차 — 구현 및 검증:** 수집 routing 수정, 단위/계약 테스트, 실제 DB 및 Browser QA

현재 완료 범위는 1차 진단이다. 디자인 선택 승인 후 2차 상세 설계와 3차 구현으로 이어간다.
