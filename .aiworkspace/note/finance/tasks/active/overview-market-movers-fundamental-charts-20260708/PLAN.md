# Overview Market Movers Fundamental Charts

## 이걸 하는 이유?

변동종목의 조사단서 > 기본 지표는 PER / EPS / 당기순이익을 숫자와 표로만 보여준다. 사용자는 기존 UI를 바꾸기보다 하단에서 같은 근거를 그래프로 빠르게 비교하길 원한다. 이번 작업은 기존 표를 보존하면서 PER, EPS, 당기순이익, 유동비율, FCF를 연간/분기 막대 그래프로 확인할 수 있게 만드는 것이다.

## 1차: 데이터 계약 고정

- 대상: `app/services/overview/why_it_moved.py`, `app/web/overview/market_movers_helpers.py`
- 완료 조건: snapshot/model payload에 `metric_charts`가 생기고, UI가 DB를 직접 읽지 않는다.

## 2차: 하단 그래프 UI

- 대상: `app/web/overview/components/market_movers.py`
- 완료 조건: 기존 기본 지표 표 아래에 지표 탭과 연간/분기 탭이 생기며, 빈 데이터는 빈 상태로 처리한다.

## 3차: 품질/근거 유지

- 대상: 서비스 snapshot 계산과 모델 포맷
- 완료 조건: 유동비율은 current assets/current liabilities에서, FCF는 statement shadow의 free cash flow에서 계산/노출한다. 공시일/기간 근거를 차트 row에 함께 둔다.

## 4차: 검증과 문서 동기화

- 대상: contract tests, compile, Streamlit UI QA, docs/root handoff
- 완료 조건: 관련 테스트와 정적 검증을 통과하고, 남은 QA 공백을 명시한다.
