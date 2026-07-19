# Portfolio Monitoring React Command Center

Status: Active
Last Verified: 2026-07-19

## 목적

`Operations > Portfolio Monitoring`은 Backtest에서 선별된 전략과 미국 주식·ETF를 사용자가 만든 그룹 단위로 추적하고, 성과·노출·행동·매크로 근거를 한 화면에서 재확인하는 decision-support surface다. 실제 주문이나 계좌 운용 화면이 아니다.

## 화면과 소유권

- route와 Streamlit navigation entry는 `app/web/final_selected_portfolio_dashboard.py`가 유지한다.
- Python bridge는 `portfolio_monitoring_workspace_v1` projection과 검증된 command intent만 React에 전달한다.
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`가 Portfolio-first Command Center와 Context Drawer를 렌더링한다.
- `app/services/portfolio_monitoring/`이 저장 명령, catalog, 가치곡선, exposure, diagnosis, macro context, history, calibration과 read model을 소유한다.
- React는 입력 intent와 표현만 소유한다. effective date, 가치, MDD/CAGR, 진단 severity/confidence, calibration publication status는 Python이 계산한다.

## 사용자 흐름

1. 최초 진입 시 deterministic default group 하나를 확보한다.
2. 그룹을 선택·추가·이름 변경한다.
3. Context Drawer에서 미국 주식·ETF 또는 Final Review의 `monitoring_candidate=True` 전략을 고른다.
4. 시작일과 fixed notional을 지정하거나, direct security에 한해 시작 종가 기준 정수 수량을 지정한다.
5. 최대 10개 active item의 공통 가치곡선과 투자금·현재금액·수익률·MDD·CAGR을 확인한다.
6. 직접 미국 주식·ETF는 선택 상세에서 저장 일봉의 close line 또는 OHLCV candle과 volume을 확인한다. 최대 120개 row 안에서 wheel 또는 버튼으로 최소 15거래일까지 확대하고, 확대 상태에서는 수평 drag로 기간을 이동하거나 `전체 보기`로 복귀한다. Final Review 전략은 가치곡선만 표시하며 합성 candle을 만들지 않는다.
7. 개별 lane, 강점·취약점·데이터 부족, 매크로 관찰, 위험 검증 상태와 진단 이력을 확인한다.

## 데이터 경계

화면 render 중 provider fetch를 하지 않는다. 경로는 `Ingestion -> DB -> Loader/Adapter -> Service -> Streamlit bridge -> React`다. 직접 종목 가격 상세은 `finance.loaders.price.load_price_history`의 일봉을 최신 120거래일 compact `selected_item_market_chart`로 전달하며, 불완전한 OHLC row는 제외하고 volume 결측만 허용한다. 확대/이동 viewport는 React client state이며 Python rerun이나 추가 DB read를 만들지 않는다. desktop은 pointer wheel/drag, 420px mobile은 세로 scroll을 보존하는 명시적 zoom/reset controls만 제공한다. Operations Console summary는 이 상세 projection을 요청하지 않는다. Final Review row는 후보 identity와 replay contract를 제공하지만 기존 append-only decision을 수정하지 않는다. legacy saved JSONL은 migration 입력으로만 읽고 재작성하지 않는다.

## 판단 경계

진단은 versioned deterministic rule의 측정값·임계값·기준일·coverage·바뀌는 조건을 표시한다. 매크로는 함께 관찰할 위험 맥락이며 원인이나 방향을 단정하지 않는다. 검증된 calibration artifact가 `READY`이고 현재 config fingerprint와 맞을 때만 조건부 확률을 공개한다. 그 외에는 `SUPPRESSED` 또는 관찰 전용으로 남긴다.

이 화면은 live approval, broker order, broker/account sync, auto rebalance를 만들지 않는다.

## 관련 문서

- 데이터 계약: `../data/PORTFOLIO_MONITORING_DATA_CONTRACT.md`
- migration/QA: `../runbooks/PORTFOLIO_MONITORING_MIGRATION_AND_QA.md`
- 사용자 흐름: `../flows/PORTFOLIO_SELECTION_FLOW.md`
