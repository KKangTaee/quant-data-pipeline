# Portfolio Monitoring Chart Clarity / OHLCV V1 Implementation Plan

> **Execution:** 현재 `codex/main-dev` 세션에서 순차 실행한다. 각 단계는 실패 테스트를 먼저
> 만들고 최소 구현으로 통과시킨 뒤 다음 단계로 이동한다.

**Goal:** 종합 가치곡선의 흐린 후광을 제거하고 실제 DB 일봉이 있는 미국 주식·ETF의
개별 상세에서 라인/OHLCV 캔들 차트를 제공한다.

**Architecture:** 그룹 성과곡선과 선택 종목 가격 차트를 서로 다른 projection으로 유지한다.
`read_model`은 선택 항목과 loader callback을 조율하고, Streamlit page runtime만 기존
`load_price_history`를 호출한다. React는 compact OHLCV contract만 받아 자체 SVG로 라인,
캔들, 거래량, tooltip을 렌더링한다.

**Tech Stack:** Python 3, pandas, unittest/pytest, Streamlit component, React 18,
TypeScript, SVG, Vitest, Vite.

---

## 1차 — 종합 가치곡선 선명도와 날짜 눈금

### Task 1. 날짜 눈금 helper를 테스트 우선으로 추가

**Files:**
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts`

1. `buildChartDateTicks(series, maxTicks)`가 시작/종료를 보존하고 실제 관측 index 중 최대
   5개(모바일 3개)의 고유 tick을 반환하는 실패 테스트를 추가한다.

```ts
expect(buildChartDateTicks(series, 5).map((tick) => tick.index))
  .toEqual([0, 2, 4, 6, 8]);
expect(buildChartDateTicks(series, 3).map((tick) => tick.index))
  .toEqual([0, 4, 8]);
```

2. 실행해 새 export 부재로 실패하는지 확인한다.

```bash
npm test -- --run src/workbenchState.test.ts
```

3. `Math.round(position * (length - 1) / (tickCount - 1))` 기반 최소 helper를 구현하고
   중복 index를 제거한다. 빈 series와 단일 관측도 처리한다.
4. 같은 테스트를 다시 실행해 통과시킨다.

### Task 2. 그룹 SVG 시각 계층을 정리

**Files:**
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`

1. `ValueChart`에서 모든 관측 circle을 제거하고 hover/focus용 active point만 남긴다.
2. `buildChartDateTicks`를 사용해 desktop/tablet 최대 5개 날짜를 렌더링하고 CSS media
   query에서 중간 tick 일부를 숨겨 420px 이하 최대 3개만 보이게 한다.
3. main line, grid, guide에 `vector-effect: non-scaling-stroke`를 적용한다.
4. main line 대비를 높이고 area opacity를 낮추되 Y domain과 tooltip 계산은 건드리지 않는다.
5. React unit test, typecheck를 실행한다.

```bash
npm test
npm run typecheck
```

6. 1차 변경을 커밋한다.

```bash
git add app/web/streamlit_components/portfolio_monitoring_workbench/src
git commit -m "포트폴리오 가치곡선 선명도 개선"
```

## 2차 — 선택 항목 OHLCV projection

### Task 3. read-model market chart contract를 테스트 우선으로 추가

**Files:**
- Create: `app/services/portfolio_monitoring/market_chart.py`
- Create: `tests/test_portfolio_monitoring_market_chart.py`
- Modify: `app/services/portfolio_monitoring/read_model.py`
- Modify: `tests/test_portfolio_monitoring_read_model.py`

1. 다음 실패 계약을 새 테스트에 만든다.
   - direct stock/ETF의 유효 OHLC row만 날짜순 정렬하고 최신 120개로 제한한다.
   - volume 결측은 `None`을 허용한다.
   - strategy는 loader를 호출하지 않고 `UNSUPPORTED`를 반환한다.
   - 없는 선택 id는 현재 item 목록 첫 항목으로 fallback한다.
   - empty/invalid frame은 `MISSING`, exception은 `ERROR`로 격리한다.

```python
projection = build_selected_item_market_chart(
    items,
    selected_item_id="item-a",
    basis_date=date(2026, 7, 18),
    loader=loader,
)
self.assertEqual(projection["status"], "READY")
self.assertLessEqual(len(projection["rows"]), 120)
```

2. 테스트를 실행해 모듈 부재 실패를 확인한다.

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_market_chart -v
```

3. `MarketChartLoader` callback, stable empty projection, row compacting을 구현한다.
4. `build_portfolio_monitoring_workspace`에 optional `selected_item_id`,
   `market_chart_loader`를 추가한다. loader가 없으면 projection key를 만들지 않아 Operations
   summary 경로의 추가 조회를 방지한다.
5. workspace top-level contract 테스트를 `selected_item_market_chart`의 조건부 포함 규칙에 맞춰
   수정하고 focused tests를 통과시킨다.

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_market_chart tests.test_portfolio_monitoring_read_model -v
```

### Task 4. Streamlit page runtime을 DB-only loader에 연결

**Files:**
- Modify: `app/web/final_selected_portfolio_dashboard.py`
- Modify: `tests/test_portfolio_monitoring_page.py`

1. page render가 session의 `portfolio_monitoring_selected_item_id`와
   `include_selected_item_market_chart=True`를 전달하는 실패 테스트를 추가한다.
2. Operations summary는 flag 기본값 `False`로 workspace를 만들고 market loader가 호출되지
   않는 회귀 테스트를 추가한다.
3. page service closure에 optional keyword를 추가하고 direct security callback에서
   `load_price_history(symbol, start_date=max(effective_start, basis-240일), end_date=basis,
   timeframe="1d")`를 사용한다.
4. focused page tests를 통과시킨다.

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_page tests.test_portfolio_monitoring_read_model tests.test_portfolio_monitoring_market_chart -v
```

5. 2차 변경을 커밋한다.

```bash
git add app/services/portfolio_monitoring app/web/final_selected_portfolio_dashboard.py tests/test_portfolio_monitoring_*.py
git commit -m "선택 종목 OHLCV 조회 계약 추가"
```

## 3차 — 개별 라인/캔들 UI

### Task 5. TypeScript contract와 차트 geometry를 테스트 우선으로 추가

**Files:**
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts`

1. `SelectedItemMarketChart`, `MarketChartRow`, status union을 contract에 추가한다.
2. candle domain이 low/high 전체를 포함하고 flat/invalid data를 안전하게 처리하는 helper,
   nearest candle index와 volume normalization helper의 실패 테스트를 작성한다.
3. 테스트 실패를 확인한 뒤 최소 geometry helper를 구현한다.

```bash
npm test -- --run src/workbenchState.test.ts
```

### Task 6. 개별 상세 가격/전략 차트 UI 구현

**Files:**
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`

1. direct security READY 상태에 `가격 차트`와 `라인 | 캔들` control을 추가한다.
2. line mode는 close line과 active tooltip, candle mode는 wick/body/volume bar와
   O/H/L/C/volume tooltip을 렌더링한다.
3. 선택 항목이 바뀌면 mode를 line으로 되돌린다.
4. strategy는 `active_group.curve`의 `item:<id>` value line과 설명을 표시하고 candle
   control은 만들지 않는다.
5. `MISSING/ERROR/UNSUPPORTED`는 가격 차트 영역만 대체하고 상단 지표는 유지한다.
6. desktop과 420px에서 툴팁과 control이 컨테이너를 넘지 않도록 CSS를 추가한다.
7. React test/typecheck/build를 실행한다.

```bash
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test
npm run typecheck
npm run build
```

8. 3차 변경을 커밋한다.

```bash
git add app/web/streamlit_components/portfolio_monitoring_workbench
git commit -m "선택 종목 라인과 캔들 차트 추가"
```

## 4차 — 통합 검증, Browser QA, 문서 정렬

### Task 7. 회귀 검증과 실제 브라우저 QA

**Files:**
- Verify: `tests/test_portfolio_monitoring_*.py`
- Verify: `app/web/streamlit_components/portfolio_monitoring_workbench/component_static/`
- Create local artifact only: `portfolio-monitoring-chart-clarity-ohlcv-qa.png`

1. 전체 Portfolio Monitoring Python regression을 실행한다.

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring_*.py' -v
```

2. React test/typecheck/build 결과를 재확인한다.
3. 실제 Streamlit/component 화면에서 다음을 Browser QA한다.
   - 그룹 라인의 정적 점 후광 제거와 desktop 5개/모바일 3개 날짜
   - 직접 종목 line/candle 전환
   - 상승/하락 candle, volume, OHLCV tooltip
   - strategy 설명 및 candle control 부재
   - 420px overflow 부재
4. QA screenshot은 repository root local artifact로만 보관하고 stage하지 않는다.

### Task 8. finance 문서와 최종 diff 정렬

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-clarity-ohlcv-v1-20260719/DESIGN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-clarity-ohlcv-v1-20260719/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-clarity-ohlcv-v1-20260719/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-clarity-ohlcv-v1-20260719/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-clarity-ohlcv-v1-20260719/RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

1. 설계 상태, 실제 변경 파일, 테스트 수와 Browser QA 결과를 기록한다.
2. 장기 데이터/화면 계약이 기존 docs와 달라진 경우에만 canonical docs를 최소 수정한다.
3. final diff와 generated artifact stage 여부를 확인한다.

```bash
git diff --check
git status --short
git diff --stat
```

4. documentation closeout을 커밋한다.

```bash
git add .aiworkspace/note/finance
git commit -m "포트폴리오 OHLCV 차트 작업 기록 정리"
```

5. 마지막으로 모든 검증을 새로 실행하고, 전체 roadmap에서 4차까지 완료되었는지와 남은
   위험(실데이터 availability 등)을 사용자에게 보고한다.
