# Today Contributor Coverage / Review Layout V1 Plan

Status: Design approved, implementation pending
Roadmap: 0/2 stages complete
Last Updated: 2026-07-23

## 이걸 하는 이유?

Today의 `종목별 성과 기여`는 실제 대표 포트폴리오 5종목 중 양수 상위 2개와 음수 하위 2개만 투영한다. 현재 데이터에서는 양수 종목이 AMD 하나라 최종 카드가 3개만 남고, 계산 가능한 SOXX와 QQQ가 아무 설명 없이 사라진다. 같은 행의 `우선 확인`은 늘어난 패널 높이에 맞춰 grid row가 stretch되어 세 항목 사이가 과도하게 벌어진다.

사용자가 포트폴리오 구성 종목을 누락으로 오해하지 않고, 영향이 큰 종목과 우선 확인 항목을 한 번에 빠르게 읽도록 두 문제를 함께 바로잡는다.

## Roadmap

### 1차 — Contributor coverage contract

- EOD contributor projection에서 계산 가능한 전체 종목을 보존한다.
- 절대 기여금액이 큰 순서로 정렬하고 0은 neutral로 처리한다.
- UI에서 `전체 N개 · 영향 큰 순` 또는 `기여 계산 N/M개 · 영향 큰 순`을 표시한다.
- 완료 조건: 실제 5종목이 AMD, TEM, RKLB, SOXX, QQQ 영향도 순서로 모두 노출되고 누락 시 coverage 이유가 보인다.

### 2차 — Review density / responsive QA

- `우선 확인` 항목을 상단부터 일정 간격으로 쌓는다.
- desktop의 같은 높이 패널은 유지하되 내부 row stretch를 제거한다.
- 760px와 420px에서 카드 및 문구 overflow를 검증한다.
- 완료 조건: 우선 확인 세 항목 간격이 일정하고 전체 contributor 목록이 responsive layout에서 잘리지 않는다.

## Scope

- `app/services/today.py`
- `app/web/streamlit_components/today_workbench/src/TodayPortfolioPanel.tsx`
- `app/web/streamlit_components/today_workbench/src/types.ts`
- `app/web/streamlit_components/today_workbench/src/style.css`
- Today Python / React contract tests와 canonical component build

## Out Of Scope

- 수익률, 기여금액, 평가액 계산식
- DB schema, 저장 cadence, provider 수집
- Today live-island / fragment 실행 경계
- Portfolio Monitoring 원본 화면

## Stop Condition

Python/React 회귀, typecheck/build, actual desktop·760·420px Browser QA와 문서 동기화가 모두 끝나면 완료한다.
