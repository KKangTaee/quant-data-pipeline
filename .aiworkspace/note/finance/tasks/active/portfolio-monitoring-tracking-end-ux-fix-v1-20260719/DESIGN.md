# Portfolio Monitoring Tracking End UX Fix V1 Design

Status: Approved
Last Updated: 2026-07-19

## Problem

`추적 종료`는 기록 삭제가 아니라 종료 시점 평가금액을 현금으로 고정하는 기능이다.
하지만 현재 종료 resolver는 요청일 이후의 가격만 허용한다. 주말·휴장일이나 당일 종가가
아직 저장되지 않은 시점에는 사용할 값이 없어 command가 실패하고 item은 `active`로 남는다.
React는 add-item draft command만 결과 메시지와 연결하므로 이 실패를 본문에 보여주지 않는다.
또한 모든 item을 한 목록에 섞고 valuation lane의 raw `ACTIVE`를 상세 eyebrow로 표시해,
종료 기록과 활성 추적의 차이가 불명확하다.

## Approved Design

1. 종료 요청일 현재 사용할 수 있는 가장 최근 가치 row를 종료 평가값으로 사용한다.
   즉 `date <= requested_end_date` 중 가장 최신 row를 선택하고 실제 날짜를
   `tracking_end_effective_date`로 저장한다.
2. 종료된 item은 삭제하지 않는다. 종료일 이후 그룹 가치곡선에서는 `exit_value`를
   현금처럼 고정하고 과거 기여도와 차트 접근을 유지한다.
3. `종목·전략 결과`의 첫 목록은 활성 항목만 보여준다. 종료 항목은 접힌 `종료 기록`
   영역으로 분리하며 사용자가 열어 상세를 다시 확인할 수 있다.
4. 상세 eyebrow는 raw valuation lane status를 직접 노출하지 않고 item lifecycle 기준의
   `활성 추적 / 확인 필요 / 종료 기록`으로 표시한다. 우측 pill은 기존
   `추적 중 / 확인 필요 / 추적 종료`와 같은 lifecycle을 사용한다.
5. 가장 최근 command 결과는 drawer 바깥 본문 배너에 표시한다. 종료 성공과 실패가
   rerun 뒤에도 보이며, 사용자가 닫을 수 있다.

## Tradeoff

휴장일 종료는 다음 거래일까지 기다리는 대신 최근 저장 종가로 즉시 확정된다. 따라서
요청일과 실제 종료 평가일이 다를 수 있지만, 두 날짜를 DB에 함께 저장하고 사용자가
원한 즉시 추적 중단을 보장한다. 데이터가 오래된 경우에도 저장된 최신 값이 사용되므로
command 배너에서 실제 적용일을 함께 안내하는 것이 중요하다.

## Scope

- `app/web/final_selected_portfolio_dashboard.py`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- focused Python page/command tests

## Out Of Scope

- item hard delete
- broker sell/order action
- DB schema 변경
- valuation/diagnosis 정책 재설계
- 기존 종료 기록의 재계산

## Success Criteria

- 주말 요청일에도 이전 최신 거래일 가치로 종료 command가 성공한다.
- 종료 item은 활성 목록에서 빠지고 `종료 기록`에서 선택 가능하다.
- 상세에 raw `ACTIVE`가 남지 않으며 lifecycle 상태가 일관된다.
- 종료 성공·실패가 본문 command 배너로 표시된다.
