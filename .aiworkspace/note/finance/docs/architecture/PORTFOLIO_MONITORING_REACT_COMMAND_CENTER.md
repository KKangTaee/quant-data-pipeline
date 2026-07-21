# Portfolio Monitoring React Command Center

Status: Active
Last Verified: 2026-07-21

## 목적

`Operations > Portfolio Monitoring`은 Backtest에서 선별된 전략과 미국 주식·ETF를 사용자가 만든 그룹 단위로 추적하고, 성과·노출·행동·매크로 근거를 한 화면에서 재확인하는 decision-support surface다. 실제 주문이나 계좌 운용 화면이 아니다.

## 화면과 소유권

- route와 Streamlit navigation entry는 `app/web/final_selected_portfolio_dashboard.py`가 유지한다.
- Python bridge는 `portfolio_monitoring_workspace_v2` projection과 검증된 command intent만 React에 전달한다.
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`가 Portfolio-first Command Center와 Context Drawer를 렌더링한다.
- `app/services/portfolio_monitoring/`이 저장 명령, catalog, 가치곡선, exposure, diagnosis, macro context, history, calibration과 read model을 소유한다.
- React는 입력 intent와 표현만 소유한다. effective date, 가치, MDD/CAGR, 진단 severity/confidence, calibration publication status는 Python이 계산한다.

## 사용자 흐름

1. 최초 진입 시 deterministic default group 하나를 확보한다.
2. 그룹을 선택·추가·이름 변경한다.
3. Context Drawer에서 미국 주식·ETF 또는 Final Review의 `monitoring_candidate=True` 전략을 고른다.
4. 시작일과 fixed notional을 지정하거나, direct security에 한해 시작 종가 기준 정수 수량을 지정한다.
5. 최대 10개 active item의 공통 가치곡선과 투자금·현재금액·수익률·MDD·CAGR을 확인한다.
6. 선택 항목이 direct 미국 주식의 fixed-shares 방식이면 `보유내역 > 최초 설정 정정`에서 최초 요청 시작일과 수량을 함께 정정하거나 추가매수·일부매도를 기록한다. 최초 설정 정정은 요청일 이후 첫 DB 시장일·종가와 최초 투자금을 변경 전/후로 확인한 뒤 저장하며, 이후 거래와 개별·그룹 성과를 새 초기 계약으로 다시 계산한다. 거래일의 정확한 DB 종가가 기본 체결가이며 실제 체결가로 수정할 수 있다. 거래 revision 수정·취소도 감사 이력을 남긴다. 이 영역의 수량·현금흐름·평가금액은 선택 종목 자체의 최신 평가일을 함께 표시하며, 여러 종목을 합산하는 상단 그룹 공통 기준일과 섞지 않는다.
7. 직접 미국 주식·ETF는 선택 상세에서 저장 일봉의 close line 또는 OHLCV candle과 volume을 확인한다. 최대 120개 row 안에서 wheel 또는 버튼으로 최소 15거래일까지 확대하고, 확대 상태에서는 수평 drag로 기간을 이동하거나 `전체 보기`로 복귀한다. Final Review 전략은 가치곡선만 표시하며 합성 candle을 만들지 않는다.
8. 종료된 항목은 접힌 종료 기록에서 선택한다. `추적 종료 취소`는 새 항목을 만들지 않고 동일 item의 종료일·종료금액을 비워 원래 시작일부터 연속 추적으로 다시 투영한다. 복구 시에도 active 10개 한도와 동일 source 중복 제한을 재검증한다.
9. 개별 lane, 강점·취약점·데이터 부족, 매크로 관찰, 위험 검증 상태와 진단 이력을 확인한다. 상관 집중과 현재 낙폭처럼 같은 의미가 반복되는 판정은 의미 가족별 한 카드로 먼저 읽고, 펼친 상세에서 종목·종목쌍별 원시 근거를 모두 확인한다. 강점·취약점·데이터 부족 목록은 760px 초과 화면에서 560px 이후 내부 스크롤하며, 760px 이하에서는 중첩 스크롤 없이 페이지 흐름으로 펼쳐진다.

## 데이터 경계

화면 render 중 provider fetch를 하지 않는다. 경로는 `Ingestion -> DB -> Loader/Adapter -> Service -> Streamlit bridge -> React`다. 직접 종목 가격 상세은 `finance.loaders.price.load_price_history`의 일봉을 최신 120거래일 compact `selected_item_market_chart`로 전달한다. 거래 입력은 같은 DB loader의 exact-date close를, 최초 설정 정정은 요청일 이후 첫 stored close를 사용한다. React는 날짜·수량 intent와 비교 preview만 소유하고 Python이 적용일·종가·초기 자본을 확정한다. 거래 command는 `monitoring_security_position_event`에 append-only revision을 남기고 service가 split-first 수량·현금흐름·가치곡선을 다시 투영한다. 확대/이동 viewport는 React client state이며 Python rerun이나 추가 DB read를 만들지 않는다. desktop은 pointer wheel/drag, 420px mobile은 세로 scroll을 보존하는 명시적 zoom/reset controls만 제공한다. Final Review row는 후보 identity와 replay contract를 제공하지만 기존 append-only decision을 수정하지 않는다. legacy saved JSONL은 migration 입력으로만 읽고 재작성하지 않는다.

## 판단 경계

진단은 versioned deterministic rule의 측정값·임계값·기준일·coverage·바뀌는 조건을 표시한다. Python projection의 `display_groups`는 현재 `correlation_cluster`와 `current_drawdown`만 표시용으로 묶고, `weaknesses`·`all_rows`·history snapshot은 판정 사실 단위를 보존한다. React는 additive group contract를 표현하며 legacy payload는 one-member group으로 읽는다. 매크로는 함께 관찰할 위험 맥락이며 원인이나 방향을 단정하지 않는다. 검증된 calibration artifact가 `READY`이고 현재 config fingerprint와 맞을 때만 조건부 확률을 공개한다. 그 외에는 `SUPPRESSED` 또는 관찰 전용으로 남긴다.

추가매수는 외부 입금, 일부매도 순대금은 외부 출금으로 성과를 조정한다. 일부매도 후 최소 1주를 남기며 전량매도는 tracking end가 소유한다. 이 화면은 tax lot/FIFO, group cash account, live approval, broker order, broker/account sync, auto rebalance를 만들지 않는다.

## 관련 문서

- 데이터 계약: `../data/PORTFOLIO_MONITORING_DATA_CONTRACT.md`
- migration/QA: `../runbooks/PORTFOLIO_MONITORING_MIGRATION_AND_QA.md`
- 사용자 흐름: `../flows/PORTFOLIO_SELECTION_FLOW.md`
