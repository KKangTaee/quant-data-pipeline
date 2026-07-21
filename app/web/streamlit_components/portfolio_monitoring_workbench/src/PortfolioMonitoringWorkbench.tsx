import React, { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import type { DiagnosisDisplayGroupView, DiagnosisRow, ItemRow, MarketChartRow, PortfolioMonitoringWorkspace, SelectedItemMarketChart } from "./contracts";
import {
  applySourceType,
  availableFundingModes,
  buildAddItemPayload,
  buildCatalogSearchEvent,
  buildChartDateTicks,
  buildCommonBasisBanner,
  buildGroupChartSeries,
  buildDiagnosisSections,
  buildFullMarketChartViewport,
  buildMacroObservationPresentation,
  buildMarketChartBounds,
  buildPriceRefreshSummary,
  buildRiskCalibrationPresentation,
  createItemDraft,
  formatMetric,
  itemBuilderRecoveryKey,
  itemLifecycleLabel,
  MIN_MARKET_CHART_VISIBLE_ROWS,
  nearestChartPointIndex,
  nearestMarketChartRowIndex,
  normalizeItemBuilderState,
  panMarketChartViewport,
  partitionItemRows,
  placeChartTooltip,
  selectActiveGroup,
  selectItem,
  validateItemDraft,
  zoomMarketChartViewport,
} from "./workbenchState";
import type { ItemDraft } from "./workbenchState";
import { PositionLedgerPanel } from "./PositionLedgerPanel";
import "./style.css";

function compactDate(value: string | null) {
  if (!value) return "-";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat("ko-KR", { month: "short", day: "numeric" }).format(date);
}

function statusLabel(status: string) {
  if (status === "ended") return "추적 종료";
  if (status === "data_review" || status === "PARTIAL") return "확인 필요";
  if (status === "active" || status === "READY") return "추적 중";
  return status;
}

function newCommandId() {
  const token = typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `portfolio-monitoring-${token}`;
}

function todayText() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

function priceText(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 }).format(value);
}

function volumeText(value: number | null) {
  return value == null ? "자료 없음" : new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

function ValueChart({ rows, items }: { rows: Array<Record<string, string | number | null>>; items: ItemRow[] }) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const series = buildGroupChartSeries(rows, items.map((item) => item.monitoring_item_id));
  const values = series.map((point) => point.total).filter((value): value is number => value != null);
  if (series.length < 2 || values.length < 2) {
    return <div className="pm-empty-chart">가치곡선을 표시할 관측치가 아직 충분하지 않습니다.</div>;
  }
  const width = 960;
  const height = 280;
  const inset = { top: 22, right: 22, bottom: 36, left: 66 };
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const padding = Math.max((maxValue - minValue) * 0.16, maxValue * 0.015, 1);
  const low = minValue - padding;
  const high = maxValue + padding;
  const x = (index: number) => inset.left + (index / Math.max(series.length - 1, 1)) * (width - inset.left - inset.right);
  const y = (value: number) => inset.top + ((high - value) / (high - low)) * (height - inset.top - inset.bottom);
  const path = series
    .map((point, index) => point.total == null ? null : `${index === 0 ? "M" : "L"}${x(index).toFixed(1)},${y(point.total).toFixed(1)}`)
    .filter(Boolean)
    .join(" ");
  const area = `${path} L${x(series.length - 1)},${height - inset.bottom} L${x(0)},${height - inset.bottom} Z`;
  const ticks = [0, 0.5, 1];
  const desktopDateTicks = buildChartDateTicks(series, 5);
  const mobileDateTicks = buildChartDateTicks(series, 3);
  const activePoint = activeIndex == null ? null : series[activeIndex] ?? null;
  const activeX = activeIndex == null ? null : x(activeIndex);
  const activeY = activePoint?.total == null ? null : y(activePoint.total);
  const tooltipWidth = 142;
  const tooltipHeight = 48;
  const tooltipPlacement = activeX == null || activeY == null
    ? null
    : placeChartTooltip(activeX, activeY, {
      chartWidth: width,
      plotTop: inset.top,
      plotBottom: height - inset.bottom,
      tooltipWidth,
      tooltipHeight,
    });

  const updateActivePoint = (event: React.PointerEvent<SVGRectElement>) => {
    const svg = event.currentTarget.ownerSVGElement;
    if (!svg) return;
    const bounds = svg.getBoundingClientRect();
    if (!bounds.width) return;
    const pointerX = ((event.clientX - bounds.left) / bounds.width) * width;
    setActiveIndex(nearestChartPointIndex(series, pointerX, inset.left, width - inset.right));
  };

  return (
    <div className="pm-chart-wrap">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="포트폴리오 가치곡선">
        <defs>
          <linearGradient id="pmArea" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3182ce" stopOpacity="0.14" />
            <stop offset="100%" stopColor="#3182ce" stopOpacity="0.01" />
          </linearGradient>
        </defs>
        {ticks.map((tick) => {
          const value = high - (high - low) * tick;
          const tickY = inset.top + (height - inset.top - inset.bottom) * tick;
          return (
            <g key={tick}>
              <line x1={inset.left} y1={tickY} x2={width - inset.right} y2={tickY} className="pm-grid-line" />
              <text x={inset.left - 10} y={tickY + 4} textAnchor="end" className="pm-axis-label">{formatMetric(value, "currency")}</text>
            </g>
          );
        })}
        <path d={area} fill="url(#pmArea)" />
        <path d={path} className="pm-value-line" />
        {series.map((point, index) => point.total == null ? null : (
          <g
            className="pm-chart-point"
            key={`${point.date}-${index}`}
            tabIndex={0}
            onFocus={() => setActiveIndex(index)}
            onBlur={() => setActiveIndex(null)}
          >
            <circle cx={x(index)} cy={y(point.total)} r={3.4} />
            <title>{`${compactDate(point.date)} · ${formatMetric(point.total, "currency")}`}</title>
          </g>
        ))}
        <rect
          className="pm-chart-hit-area"
          x={inset.left}
          y={inset.top}
          width={width - inset.left - inset.right}
          height={height - inset.top - inset.bottom}
          onPointerMove={updateActivePoint}
          onPointerLeave={() => setActiveIndex(null)}
        />
        {activePoint?.total != null && activeX != null && activeY != null && tooltipPlacement && (
          <g className="pm-chart-hover" pointerEvents="none">
            <line
              className="pm-chart-hover-line"
              x1={activeX}
              y1={inset.top}
              x2={activeX}
              y2={height - inset.bottom}
            />
            <circle className="pm-chart-active-point" cx={activeX} cy={activeY} r={5.5} />
            <g className="pm-chart-tooltip" transform={`translate(${tooltipPlacement.x} ${tooltipPlacement.y})`}>
              <rect width={tooltipWidth} height={tooltipHeight} rx={9} />
              <text x={12} y={18} className="pm-chart-tooltip-date">{compactDate(activePoint.date)}</text>
              <text x={12} y={37} className="pm-chart-tooltip-value">{formatMetric(activePoint.total, "currency")}</text>
            </g>
          </g>
        )}
        <g className="pm-date-ticks-desktop">
          {desktopDateTicks.map((tick, position) => (
            <text
              key={tick.index}
              x={x(tick.index)}
              y={height - 10}
              textAnchor={position === 0 ? "start" : position === desktopDateTicks.length - 1 ? "end" : "middle"}
              className="pm-axis-date"
            >{compactDate(tick.date)}</text>
          ))}
        </g>
        <g className="pm-date-ticks-mobile">
          {mobileDateTicks.map((tick, position) => (
            <text
              key={tick.index}
              x={x(tick.index)}
              y={height - 10}
              textAnchor={position === 0 ? "start" : position === mobileDateTicks.length - 1 ? "end" : "middle"}
              className="pm-axis-date"
            >{compactDate(tick.date)}</text>
          ))}
        </g>
      </svg>
    </div>
  );
}

type MarketChartDrag = {
  pointerId: number;
  startClientX: number;
  plotWidth: number;
  startViewport: { startIndex: number; endIndex: number };
  didDrag: boolean;
};

function MarketPriceChart({ projection }: { projection: SelectedItemMarketChart }) {
  const [mode, setMode] = useState<"line" | "candle">("line");
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const allRows = projection.rows;
  const viewportKey = `${projection.monitoring_item_id ?? "none"}:${allRows.length}:${allRows[0]?.date ?? ""}:${allRows[allRows.length - 1]?.date ?? ""}`;
  const [viewport, setViewport] = useState(() => buildFullMarketChartViewport(allRows.length));
  const [isDragging, setIsDragging] = useState(false);
  const dragRef = useRef<MarketChartDrag | null>(null);

  useEffect(() => {
    setMode("line");
    setActiveIndex(null);
  }, [projection.monitoring_item_id]);

  useEffect(() => {
    setViewport(buildFullMarketChartViewport(allRows.length));
    setActiveIndex(null);
    setIsDragging(false);
    dragRef.current = null;
  }, [viewportKey]);

  if (projection.status !== "READY" || !allRows.length) {
    return (
      <div className={`pm-market-state is-${projection.status.toLowerCase()}`}>
        <strong>가격 차트를 표시할 수 없습니다.</strong>
        <span>{projection.reason || "저장된 가격 이력을 확인해 주세요."}</span>
      </div>
    );
  }

  const rows = allRows.slice(viewport.startIndex, viewport.endIndex + 1);
  const bounds = buildMarketChartBounds(rows);
  if (!bounds) return <div className="pm-market-state"><strong>가격 범위를 계산할 수 없습니다.</strong></div>;
  const width = 620;
  const height = 300;
  const inset = { top: 20, right: 16, bottom: 28, left: 58 };
  const priceBottom = 207;
  const volumeTop = 222;
  const volumeBottom = height - inset.bottom;
  const rawRange = bounds.maxPrice - bounds.minPrice;
  const padding = Math.max(rawRange * 0.08, bounds.maxPrice * 0.008, 0.01);
  const low = bounds.minPrice - padding;
  const high = bounds.maxPrice + padding;
  const plotWidth = width - inset.left - inset.right;
  const visibleCount = rows.length;
  const isFullViewport = visibleCount >= allRows.length;
  const canZoomIn = visibleCount > Math.min(MIN_MARKET_CHART_VISIBLE_ROWS, allRows.length);
  const rangeLabel = `${compactDate(rows[0]?.date ?? null)}–${compactDate(rows[rows.length - 1]?.date ?? null)} · ${visibleCount}거래일`;
  const x = (index: number) => inset.left + (index / Math.max(rows.length - 1, 1)) * plotWidth;
  const y = (value: number) => inset.top + ((high - value) / Math.max(high - low, 0.01)) * (priceBottom - inset.top);
  const closePath = rows.map((row, index) => `${index === 0 ? "M" : "L"}${x(index).toFixed(2)},${y(row.close).toFixed(2)}`).join(" ");
  const candleWidth = Math.max(1.5, Math.min(8, (plotWidth / Math.max(rows.length, 1)) * 0.66));
  const activeRow = activeIndex == null ? null : rows[activeIndex] ?? null;
  const activeX = activeIndex == null ? null : x(activeIndex);
  const activeY = activeRow == null ? null : y(activeRow.close);
  const tooltipWidth = 218;
  const tooltipHeight = 96;
  const tooltipPlacement = activeX == null || activeY == null
    ? null
    : placeChartTooltip(activeX, activeY, {
      chartWidth: width,
      plotTop: inset.top,
      plotBottom: volumeBottom,
      tooltipWidth,
      tooltipHeight,
    });
  const dateIndices = Array.from(new Set([0, Math.round((rows.length - 1) / 2), rows.length - 1]));

  const updateActive = (event: React.PointerEvent<SVGRectElement>) => {
    const svg = event.currentTarget.ownerSVGElement;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    if (!rect.width) return;
    const pointerX = ((event.clientX - rect.left) / rect.width) * width;
    setActiveIndex(nearestMarketChartRowIndex(rows.length, pointerX, inset.left, width - inset.right));
  };

  const resetViewport = () => {
    setViewport(buildFullMarketChartViewport(allRows.length));
    setActiveIndex(null);
  };

  const zoomAt = (direction: "in" | "out", anchorRatio = 0.5) => {
    setViewport((current) => zoomMarketChartViewport(current, allRows.length, anchorRatio, direction));
    setActiveIndex(null);
  };

  const handleWheel = (event: React.WheelEvent<SVGRectElement>) => {
    event.preventDefault();
    const svg = event.currentTarget.ownerSVGElement;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    if (!rect.width) return;
    const pointerX = ((event.clientX - rect.left) / rect.width) * width;
    const anchorRatio = (pointerX - inset.left) / plotWidth;
    zoomAt(event.deltaY < 0 ? "in" : "out", anchorRatio);
  };

  const handlePointerDown = (event: React.PointerEvent<SVGRectElement>) => {
    if (event.pointerType === "touch" || isFullViewport) return;
    const svg = event.currentTarget.ownerSVGElement;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    if (!rect.width) return;
    dragRef.current = {
      pointerId: event.pointerId,
      startClientX: event.clientX,
      plotWidth: rect.width * (plotWidth / width),
      startViewport: viewport,
      didDrag: false,
    };
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handlePointerMove = (event: React.PointerEvent<SVGRectElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) {
      if (!isDragging && event.pointerType !== "touch") updateActive(event);
      return;
    }
    const deltaX = event.clientX - drag.startClientX;
    if (!drag.didDrag && Math.abs(deltaX) < 4) {
      updateActive(event);
      return;
    }
    drag.didDrag = true;
    setIsDragging(true);
    setActiveIndex(null);
    setViewport(panMarketChartViewport(drag.startViewport, allRows.length, deltaX, drag.plotWidth));
  };

  const finishPointerDrag = (event: React.PointerEvent<SVGRectElement>) => {
    const drag = dragRef.current;
    if (drag?.pointerId === event.pointerId && event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    dragRef.current = null;
    setIsDragging(false);
    if (!drag?.didDrag && event.pointerType !== "touch") updateActive(event);
  };

  const cancelPointerDrag = () => {
    dragRef.current = null;
    setIsDragging(false);
    setActiveIndex(null);
  };

  return (
    <section className="pm-market-chart-section" aria-label={`${projection.source_ref ?? "선택 종목"} 가격 차트`}>
      <header>
        <div><span>PRICE HISTORY · 1D</span><strong>가격 차트</strong></div>
        <div className="pm-market-toolbar">
          <span className="pm-market-range">{rangeLabel}</span>
          <div className="pm-market-zoom-controls" role="group" aria-label="가격 차트 범위">
            <button type="button" aria-label="가격 차트 축소" disabled={isFullViewport} onClick={() => zoomAt("out")}>−</button>
            <button type="button" aria-label="가격 차트 확대" disabled={!canZoomIn} onClick={() => zoomAt("in")}>+</button>
            <button type="button" disabled={isFullViewport} onClick={resetViewport}>전체 보기</button>
          </div>
          <div className="pm-chart-mode-switch" role="group" aria-label="가격 차트 방식">
            <button type="button" className={mode === "line" ? "is-active" : ""} onClick={() => setMode("line")}>라인</button>
            <button type="button" className={mode === "candle" ? "is-active" : ""} onClick={() => setMode("candle")}>캔들</button>
          </div>
        </div>
      </header>
      <div className="pm-market-chart-shell">
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${projection.source_ref ?? "선택 종목"} ${mode === "line" ? "종가 라인" : "OHLCV 캔들"}`}>
          {[0, 0.5, 1].map((tick) => {
            const value = high - (high - low) * tick;
            const tickY = inset.top + (priceBottom - inset.top) * tick;
            return <g key={tick}><line x1={inset.left} y1={tickY} x2={width - inset.right} y2={tickY} className="pm-market-grid" /><text x={inset.left - 8} y={tickY + 4} textAnchor="end" className="pm-market-axis">{priceText(value)}</text></g>;
          })}
          {mode === "line" ? (
            <path d={closePath} className="pm-market-close-line" />
          ) : rows.map((row, index) => {
            const isUp = row.close >= row.open;
            const bodyTop = y(Math.max(row.open, row.close));
            const bodyHeight = Math.max(Math.abs(y(row.open) - y(row.close)), 1.4);
            return (
              <g key={row.date} className={`pm-market-candle ${isUp ? "is-up" : "is-down"}`}>
                <line x1={x(index)} y1={y(row.high)} x2={x(index)} y2={y(row.low)} />
                <rect x={x(index) - candleWidth / 2} y={bodyTop} width={candleWidth} height={bodyHeight} rx={0.6} />
              </g>
            );
          })}
          <line x1={inset.left} y1={volumeTop - 8} x2={width - inset.right} y2={volumeTop - 8} className="pm-market-volume-divider" />
          {rows.map((row, index) => {
            const volumeHeight = row.volume == null || bounds.maxVolume <= 0
              ? 0
              : ((row.volume / bounds.maxVolume) * (volumeBottom - volumeTop));
            return <rect key={row.date} className="pm-market-volume-bar" x={x(index) - candleWidth / 2} y={volumeBottom - volumeHeight} width={candleWidth} height={volumeHeight} rx={0.6} />;
          })}
          <text x={inset.left - 8} y={volumeTop + 7} textAnchor="end" className="pm-market-axis">VOL</text>
          {dateIndices.map((index, position) => <text key={index} x={x(index)} y={height - 8} textAnchor={position === 0 ? "start" : position === dateIndices.length - 1 ? "end" : "middle"} className="pm-market-date">{compactDate(rows[index].date)}</text>)}
          <rect
            className={`pm-market-hit-area ${!isFullViewport ? "is-draggable" : ""} ${isDragging ? "is-dragging" : ""}`}
            x={inset.left}
            y={inset.top}
            width={plotWidth}
            height={volumeBottom - inset.top}
            tabIndex={0}
            onWheel={handleWheel}
            onDoubleClick={resetViewport}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={finishPointerDrag}
            onPointerCancel={cancelPointerDrag}
            onLostPointerCapture={cancelPointerDrag}
            onPointerLeave={() => setActiveIndex(null)}
            onFocus={() => setActiveIndex(rows.length - 1)}
            onBlur={() => setActiveIndex(null)}
            onKeyDown={(event) => {
              if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
              event.preventDefault();
              setActiveIndex((current) => {
                const base = current ?? rows.length - 1;
                return Math.min(Math.max(base + (event.key === "ArrowRight" ? 1 : -1), 0), rows.length - 1);
              });
            }}
          />
          {activeRow && activeX != null && activeY != null && tooltipPlacement && (
            <g className="pm-market-hover" pointerEvents="none">
              <line x1={activeX} y1={inset.top} x2={activeX} y2={volumeBottom} />
              {mode === "line" && <circle cx={activeX} cy={activeY} r={4.5} />}
              <g className="pm-market-tooltip" transform={`translate(${tooltipPlacement.x} ${tooltipPlacement.y})`}>
                <rect width={tooltipWidth} height={tooltipHeight} rx={10} />
                <text x={12} y={17} className="pm-market-tooltip-date">{compactDate(activeRow.date)}</text>
                <text x={12} y={38}>O {priceText(activeRow.open)} · H {priceText(activeRow.high)}</text>
                <text x={12} y={57}>L {priceText(activeRow.low)} · C {priceText(activeRow.close)}</text>
                <text x={12} y={78}>거래량 {volumeText(activeRow.volume)}</text>
              </g>
            </g>
          )}
        </svg>
      </div>
    </section>
  );
}

function StrategyValueChart({ rows, itemId }: { rows: Array<Record<string, string | number | null>>; itemId: string }) {
  const series = buildGroupChartSeries(rows, [itemId])
    .map((point) => ({ date: point.date, value: point.items[itemId] }))
    .filter((point): point is { date: string; value: number } => point.value != null);
  if (series.length < 2) return <div className="pm-market-state"><strong>전략 가치곡선 관측치가 부족합니다.</strong></div>;
  const width = 620;
  const height = 190;
  const inset = { top: 18, right: 14, bottom: 26, left: 58 };
  const values = series.map((point) => point.value);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const padding = Math.max((maxValue - minValue) * 0.1, maxValue * 0.01, 1);
  const x = (index: number) => inset.left + (index / Math.max(series.length - 1, 1)) * (width - inset.left - inset.right);
  const y = (value: number) => inset.top + ((maxValue + padding - value) / Math.max(maxValue - minValue + padding * 2, 1)) * (height - inset.top - inset.bottom);
  const path = series.map((point, index) => `${index === 0 ? "M" : "L"}${x(index).toFixed(2)},${y(point.value).toFixed(2)}`).join(" ");
  return (
    <section className="pm-market-chart-section is-strategy" aria-label="전략 가치곡선">
      <header><div><span>STRATEGY VALUE</span><strong>전략 가치곡선</strong></div></header>
      <div className="pm-market-chart-shell"><svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="전략 가치곡선">
        <path d={path} className="pm-market-close-line" />
        <text x={inset.left} y={height - 7} className="pm-market-date">{compactDate(series[0].date)}</text>
        <text x={width - inset.right} y={height - 7} textAnchor="end" className="pm-market-date">{compactDate(series[series.length - 1].date)}</text>
      </svg></div>
      <p>전략에는 OHLCV 캔들이 없습니다. 등록 원금으로 환산한 일별 전략 가치만 표시합니다.</p>
    </section>
  );
}

function diagnosisSubject(row: DiagnosisRow, itemLabels: Record<string, string>) {
  const subjects = (row.subject_ids ?? []).map((itemId) => itemLabels[itemId] ?? "추적 항목");
  return subjects.join(row.rule_id.startsWith("correlation_cluster") ? " ↔ " : " · ");
}

function diagnosisGroupHeadline(group: DiagnosisDisplayGroupView) {
  if (group.member_count <= 1) return group.meaning;
  if (group.family === "correlation_cluster") return `함께 움직이는 조합 ${group.member_count}개`;
  if (group.family === "current_drawdown") return `낙폭 재확인 종목 ${group.member_count}개`;
  return `${group.meaning} · ${group.member_count}건`;
}

function DiagnosisCard({ group, itemLabels, compact = false }: {
  group: DiagnosisDisplayGroupView;
  itemLabels: Record<string, string>;
  compact?: boolean;
}) {
  const representativeSubject = diagnosisSubject(group.representative, itemLabels);
  return (
    <article className={`pm-diagnosis-card is-${group.classification} severity-${group.severity.toLowerCase()}`}>
      <header><span>{group.severity}</span><b>{group.confidence} 근거</b></header>
      <h3>{diagnosisGroupHeadline(group)}</h3>
      {group.member_count === 1 && representativeSubject && <small className="pm-diagnosis-subject">{representativeSubject}</small>}
      <p>{group.summary_fact}</p>
      {!compact && (
        <details>
          <summary>판정 근거 전체 보기{group.member_count > 1 ? ` · ${group.member_count}건` : ""}</summary>
          <div className="pm-diagnosis-member-list">
            {group.members.map((member) => {
              const subject = diagnosisSubject(member, itemLabels);
              return (
                <section key={member.rule_id} className="pm-diagnosis-member">
                  {subject && <h4>{subject}</h4>}
                  <dl>
                    <div><dt>측정값</dt><dd>{member.measured_fact}</dd></div>
                    <div><dt>판정 기준</dt><dd>{member.threshold}</dd></div>
                    <div><dt>영향 비중</dt><dd>{formatMetric(member.affected_weight, "percent")}</dd></div>
                    <div><dt>근거 범위</dt><dd>{formatMetric(member.coverage, "percent")} · {member.source_dates.join(", ") || "날짜 확인 필요"}</dd></div>
                    <div><dt>변화 조건</dt><dd>{member.change_condition}</dd></div>
                    <div><dt>다음 확인</dt><dd>{member.next_check}</dd></div>
                  </dl>
                </section>
              );
            })}
          </div>
        </details>
      )}
    </article>
  );
}

function DiagnosisColumn({ title, groups, emptyMessage, itemLabels }: {
  title: string;
  groups: DiagnosisDisplayGroupView[];
  emptyMessage: string;
  itemLabels: Record<string, string>;
}) {
  return (
    <section>
      <header className="pm-diagnosis-column-heading"><h3>{title}</h3><span>{groups.length}개</span></header>
      <div className="pm-diagnosis-list" tabIndex={groups.length ? 0 : undefined} aria-label={`${title} 진단 목록`}>
        {groups.map((group) => <DiagnosisCard key={group.group_id} group={group} itemLabels={itemLabels} />)}
        {!groups.length && <p>{emptyMessage}</p>}
      </div>
    </section>
  );
}

function PortfolioMonitoringWorkbench({ args }: ComponentProps) {
  const workspace = (args?.payload ?? null) as PortfolioMonitoringWorkspace | null;
  const initialCommandId = useMemo(() => newCommandId(), []);
  const initialItemBuilder = normalizeItemBuilderState(workspace?.item_builder_state, initialCommandId);
  const serverGroup = useMemo(
    () => selectActiveGroup(workspace?.groups ?? [], null),
    [workspace],
  );
  const projectedSelectedItemId = workspace?.selected_item_market_chart?.monitoring_item_id ?? null;
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(serverGroup?.portfolio_group_id ?? null);
  const [selectedItemId, setSelectedItemId] = useState<string | null>(projectedSelectedItemId);
  const [drawerOpen, setDrawerOpen] = useState(initialItemBuilder?.drawerOpen ?? false);
  const [drawerStep, setDrawerStep] = useState<1 | 2 | 3>(initialItemBuilder?.drawerStep ?? 1);
  const [catalogQuery, setCatalogQuery] = useState(initialItemBuilder?.catalogQuery ?? "");
  const [draft, setDraft] = useState<ItemDraft>(() => initialItemBuilder?.draft ?? createItemDraft(initialCommandId));
  const [localCommandState, setLocalCommandState] = useState<"idle" | "pending" | "success" | "error">("idle");
  const [dismissedCommandId, setDismissedCommandId] = useState<string | null>(null);
  const addButtonRef = useRef<HTMLButtonElement>(null);
  const drawerCloseRef = useRef<HTMLButtonElement>(null);
  const consumedRecoveryKeyRef = useRef<string | null>(itemBuilderRecoveryKey(initialItemBuilder));

  useEffect(() => {
    setSelectedGroupId(serverGroup?.portfolio_group_id ?? null);
  }, [serverGroup?.portfolio_group_id]);

  useEffect(() => {
    if (projectedSelectedItemId) setSelectedItemId(projectedSelectedItemId);
  }, [projectedSelectedItemId]);

  useEffect(() => {
    Streamlit.setFrameHeight();
  }, [workspace, selectedGroupId, selectedItemId, drawerOpen, drawerStep]);

  useEffect(() => {
    const recovered = normalizeItemBuilderState(workspace?.item_builder_state, initialCommandId);
    const recoveryKey = itemBuilderRecoveryKey(recovered);
    if (!recovered || !recoveryKey || consumedRecoveryKeyRef.current === recoveryKey) return;
    consumedRecoveryKeyRef.current = recoveryKey;
    setDrawerOpen(recovered.drawerOpen);
    setDrawerStep(recovered.drawerStep);
    setCatalogQuery(recovered.catalogQuery);
    setDraft(recovered.draft);
  }, [workspace?.item_builder_state, initialCommandId]);

  const serverCommand = workspace?.commands.find((command) => command.command_id === draft.commandId);
  useEffect(() => {
    if (!serverCommand) return;
    if (["success", "succeeded"].includes(serverCommand.status)) setLocalCommandState("success");
    if (["error", "failed"].includes(serverCommand.status)) setLocalCommandState("error");
    if (serverCommand.status === "pending") setLocalCommandState("pending");
  }, [serverCommand?.status, serverCommand?.command_id]);

  const closeDrawer = () => {
    setDrawerOpen(false);
    window.setTimeout(() => addButtonRef.current?.focus(), 0);
  };
  useEffect(() => {
    if (!drawerOpen) return;
    drawerCloseRef.current?.focus();
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && localCommandState !== "pending") closeDrawer();
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [drawerOpen, localCommandState]);

  if (!workspace) {
    return <div className="pm-empty">Portfolio Monitoring workspace를 불러오지 못했습니다.</div>;
  }
  const activeGroup = workspace.active_group;
  const selectedGroup = selectActiveGroup(workspace.groups, selectedGroupId);
  const selectedItem = selectItem(activeGroup?.item_rows ?? [], selectedItemId);
  const itemSections = partitionItemRows(activeGroup?.item_rows ?? []);
  const latestCommand = workspace.commands[0];
  const selectedMarketChart = workspace.selected_item_market_chart;
  const metrics = activeGroup?.metrics;
  const priceRefresh = workspace.price_refresh;
  const diagnosis = workspace.diagnosis ?? {
    policy_version: "portfolio_monitoring_policy_v1",
    top_three: [], strengths: [], weaknesses: [], data_gaps: [], all_rows: [], coverage: 0,
  };
  const diagnosisSections = buildDiagnosisSections(diagnosis);
  const diagnosisItemLabels = Object.fromEntries(
    (activeGroup?.item_rows ?? []).map((item) => [item.monitoring_item_id, item.source_ref]),
  );
  const macroPresentation = buildMacroObservationPresentation(
    workspace.macro_observation ?? { version: "portfolio_monitoring_macro_context_v1", state: "low", rows: [], top_rows: [] },
    workspace.source_health ?? { status: "LIMITED", publication: "LIMITED", coverage: 0, as_of_dates: {}, warnings: ["source health unavailable"] },
  );
  const riskPresentation = buildRiskCalibrationPresentation(
    workspace.risk_calibration ?? { publication_status: "SUPPRESSED", reasons: ["qualified calibration artifact is not available"] },
    workspace.diagnosis_history ?? [],
  );
  const emit = (event: Record<string, unknown>) => {
    Streamlit.setComponentValue({ event: { ...event, nonce: `${Date.now()}-${Math.random()}` } });
  };
  const openDrawer = () => {
    setDraft(createItemDraft(newCommandId()));
    setCatalogQuery("");
    setDrawerStep(1);
    setLocalCommandState("idle");
    setDrawerOpen(true);
  };
  const submitCatalogSearch = (event: FormEvent) => {
    event.preventDefault();
    emit(buildCatalogSearchEvent(catalogQuery, draft, drawerStep));
  };
  const chooseGroup = (groupId: string) => {
    setSelectedGroupId(groupId);
    setSelectedItemId(null);
    emit({ id: "select_group", portfolio_group_id: groupId });
  };
  const chooseItem = (itemId: string) => {
    setSelectedItemId(itemId);
    emit({ id: "select_item", monitoring_item_id: itemId });
  };
  const renderItemRow = (item: ItemRow) => {
    const contribution = metrics?.contribution_by_item[item.monitoring_item_id]
      ?? (item.current_value - item.initial_capital);
    return (
      <button
        type="button"
        key={item.monitoring_item_id}
        className={item.monitoring_item_id === selectedItem?.monitoring_item_id ? "pm-item-row is-selected" : "pm-item-row"}
        onClick={() => chooseItem(item.monitoring_item_id)}
      >
        <span className={`pm-status-dot status-${item.status}`} />
        <div><strong>{item.source_ref}</strong><small>{statusLabel(item.status)}</small></div>
        <div className="pm-item-value"><strong>{formatMetric(item.current_value, "currency", metrics)}</strong><small className={contribution < 0 ? "negative" : "positive"}>{formatMetric(contribution, "currency", metrics)}</small></div>
      </button>
    );
  };

  return (
    <main className="pm-workbench">
      <aside className="pm-group-rail" aria-label="포트폴리오 그룹">
        <header>
          <span>PORTFOLIOS</span>
          <button type="button" aria-label="포트폴리오 추가" onClick={() => {
            const name = window.prompt("새 포트폴리오 이름을 입력하세요.");
            if (name?.trim()) emit({ id: "create_group", command_id: newCommandId(), name: name.trim() });
          }}>+</button>
        </header>
        <div className="pm-group-list">
          {workspace.groups.map((group) => (
            <button
              type="button"
              key={group.portfolio_group_id}
              className={group.portfolio_group_id === selectedGroup?.portfolio_group_id ? "pm-group-card is-active" : "pm-group-card"}
              onClick={() => chooseGroup(group.portfolio_group_id)}
            >
              <span className="pm-group-dot" />
              <strong>{group.name}</strong>
              <small>{group.active_item_count}개 추적 · 전체 {group.history_item_count}</small>
            </button>
          ))}
        </div>
        <div className="pm-rail-note">
          <strong>최대 10개</strong>
          <span>활성 종목 기준</span>
        </div>
      </aside>

      <section className="pm-main">
        <header className="pm-hero">
          <div>
            <span className="pm-eyebrow">PORTFOLIO COMMAND CENTER</span>
            <h1>{selectedGroup?.name ?? "포트폴리오 모니터링"}</h1>
            <p>선정한 투자 후보를 하나의 공통 기준일로 추적하고, 다음 판단에 필요한 변화만 확인합니다.</p>
          </div>
          <div className="pm-command-band">
            <button type="button" className="pm-secondary" onClick={() => {
              if (!selectedGroup) return;
              const name = window.prompt("변경할 포트폴리오 이름을 입력하세요.", selectedGroup.name);
              if (name?.trim() && name.trim() !== selectedGroup.name) emit({ id: "rename_group", command_id: newCommandId(), portfolio_group_id: selectedGroup.portfolio_group_id, name: name.trim(), expected_version: selectedGroup.version });
            }}>이름 변경</button>
            <button ref={addButtonRef} type="button" className="pm-primary" onClick={openDrawer}>+ 종목 등록</button>
          </div>
        </header>

        {latestCommand && latestCommand.command_id !== dismissedCommandId && (
          <div className={`pm-command-feedback is-${latestCommand.status}`} role={latestCommand.status === "error" ? "alert" : "status"}>
            <div>
              <strong>{latestCommand.status === "error" ? "요청을 완료하지 못했습니다" : latestCommand.status === "warning" ? "일부 종목을 확인해 주세요" : "요청이 반영됐습니다"}</strong>
              <span>{latestCommand.message || "처리 결과를 확인해 주세요."}</span>
            </div>
            <button type="button" aria-label="처리 결과 닫기" onClick={() => setDismissedCommandId(latestCommand.command_id)}>×</button>
          </div>
        )}

        {activeGroup ? (
          <>
            <div className={`pm-basis-banner ${activeGroup.status === "PARTIAL" ? "is-partial" : ""} ${priceRefresh?.eligible ? "is-stale" : ""}`}>
              <div className="pm-basis-copy">
                <span>{activeGroup.status === "PARTIAL" ? "확인 필요" : "공통 기준"}</span>
                <div>
                  <strong>{buildCommonBasisBanner(activeGroup)}</strong>
                  {priceRefresh && <small>{buildPriceRefreshSummary(priceRefresh)}</small>}
                </div>
              </div>
              {priceRefresh?.eligible && selectedGroup && (
                <button type="button" className="pm-basis-action" onClick={() => emit({
                  id: "refresh_group_prices",
                  command_id: newCommandId(),
                  portfolio_group_id: selectedGroup.portfolio_group_id,
                })}>{priceRefresh.button_label || "보유 종목 가격 최신화"}</button>
              )}
            </div>

            <section className="pm-kpi-grid" aria-label="포트폴리오 핵심 지표">
              <article><span>누적 입금</span><strong>{formatMetric(metrics?.gross_contributions ?? metrics?.invested_capital, "currency", metrics)}</strong><small>최초 투자금 + 추가매수</small></article>
              <article><span>현재 가치</span><strong>{formatMetric(metrics?.current_value, "currency", metrics)}</strong><small>{compactDate(activeGroup.basis_date)} 기준</small></article>
              <article className={(metrics?.pnl ?? 0) < 0 ? "is-negative" : "is-positive"}><span>손익</span><strong>{formatMetric(metrics?.pnl, "currency", metrics)}</strong><small>{formatMetric(metrics?.total_return, "percent", metrics)}</small></article>
              <article><span>최대 낙폭</span><strong>{formatMetric(metrics?.mdd, "percent", metrics)}</strong><small>일별 가치곡선</small></article>
              <article><span>CAGR</span><strong>{formatMetric(metrics?.cagr, "cagr", metrics)}</strong><small>{metrics?.short_window ? "1년 미만 참고값" : "실제 경과일 기준"}</small></article>
            </section>

            <section className="pm-panel pm-chart-panel">
              <header className="pm-section-heading">
                <div><span>GROUP VALUE</span><h2>종합 가치곡선</h2></div>
                <small>투자 전·종료 후 자본은 현금으로 유지</small>
              </header>
              <ValueChart rows={activeGroup.curve} items={activeGroup.item_rows} />
            </section>

            <section className="pm-panel pm-diagnosis-panel" aria-label="포트폴리오 강점과 취약점">
              <header className="pm-section-heading">
                <div><span>PORTFOLIO DIAGNOSIS</span><h2>지금 확인할 변화</h2></div>
                <small>{diagnosis.policy_version} · 측정값과 해제 조건 기반</small>
              </header>
              <div className="pm-now-grid">
                {diagnosisSections.now.map((group) => <DiagnosisCard key={group.group_id} group={group} itemLabels={diagnosisItemLabels} compact />)}
                {!diagnosisSections.now.length && <div className="pm-diagnosis-empty">현재 상위 확인 신호가 없습니다. 근거가 충분해지면 최대 3개만 먼저 표시합니다.</div>}
              </div>
              <div className="pm-diagnosis-columns">
                <DiagnosisColumn title="강점" groups={diagnosisSections.strengths} emptyMessage="확정된 강점 근거가 아직 없습니다." itemLabels={diagnosisItemLabels} />
                <DiagnosisColumn title="취약점" groups={diagnosisSections.weaknesses} emptyMessage="현재 기준을 넘은 취약점이 없습니다." itemLabels={diagnosisItemLabels} />
                <DiagnosisColumn title="데이터 부족" groups={diagnosisSections.dataGaps} emptyMessage="핵심 분류 근거의 coverage가 유지되고 있습니다." itemLabels={diagnosisItemLabels} />
              </div>
            </section>

            <section className={`pm-panel pm-macro-panel state-${workspace.macro_observation?.state ?? "low"}`} aria-label="매크로 위험 관찰">
              <header className="pm-section-heading">
                <div><span>MACRO RISK OBSERVATION</span><h2>현재 매크로 관찰 · {macroPresentation.stateLabel}</h2></div>
                <small className={`pm-source-chip status-${(workspace.source_health?.status ?? "LIMITED").toLowerCase()}`}>{macroPresentation.sourceChip}</small>
              </header>
              <p className="pm-macro-lead">보유 노출과 저장된 경제사이클·선물·자산 경로가 동시에 맞는 조건만 표시합니다.</p>
              <div className="pm-macro-grid">
                {macroPresentation.rows.map((row) => (
                  <article key={row.rule_id} className={`pm-macro-card state-${row.state}`}>
                    <header><span>{row.severity}</span><b>{row.confidence} confidence</b></header>
                    <h3>{row.current_observation}</h3>
                    <p>영향 비중 {formatMetric(row.affected_weight, "percent")}</p>
                    <details>
                      <summary>조건과 다음 확인</summary>
                      <dl>
                        <div><dt>맞은 조건</dt><dd>{row.matched_conditions.join(" · ")}</dd></div>
                        <div><dt>변화 조건</dt><dd>{row.change_condition}</dd></div>
                        <div><dt>다음 확인</dt><dd>{row.next_check}</dd></div>
                        <div><dt>근거 날짜</dt><dd>{row.source_dates.join(", ") || "확인 필요"}</dd></div>
                      </dl>
                    </details>
                  </article>
                ))}
                {!macroPresentation.rows.length && <div className="pm-diagnosis-empty">현재 보유 노출과 동시에 맞는 매크로 위험 관찰이 없습니다.</div>}
              </div>
              {macroPresentation.staleWarning && <p className="pm-source-warning">Source 확인: {macroPresentation.staleWarning}</p>}
            </section>

            <section className="pm-panel pm-calibration-panel" aria-label="위험 검증과 진단 이력">
              <header className="pm-section-heading">
                <div><span>CALIBRATION & HISTORY</span><h2>위험 검증과 진단 이력</h2></div>
                <small className={`pm-source-chip status-${riskPresentation.status.toLowerCase()}`}>{riskPresentation.status}</small>
              </header>
              {riskPresentation.mode === "qualified_probability" ? (
                <div className="pm-qualified-risk">
                  <div><span>검증된 {riskPresentation.horizonSessions}거래일 위험 event 확률</span><strong>{formatMetric(riskPresentation.probability, "percent")}</strong><small>{riskPresentation.eventDefinition}</small></div>
                  <dl><div><dt>검증 표본</dt><dd>{riskPresentation.qualification}</dd></div><div><dt>OOS score</dt><dd>{riskPresentation.score}</dd></div></dl>
                  {riskPresentation.limitations.map((value) => <p key={value}>{value}</p>)}
                </div>
              ) : (
                <div className="pm-observation-only">
                  <strong>현재는 관찰 신호만 제공합니다.</strong>
                  <p>확률 공개 기준을 통과한 시간순 OOS artifact가 없어 수치를 표시하지 않습니다.</p>
                  {riskPresentation.reasons.map((reason) => <small key={reason}>{reason}</small>)}
                </div>
              )}
              <div className="pm-history-list">
                {riskPresentation.history.map((row) => (
                  <article key={`${row.as_of_date}-${row.severity}`}>
                    <span>{row.as_of_date}</span><b>{row.observation_state} · {row.severity}</b>
                    <small>{row.confidence} confidence · {row.resolved_at ? `${row.resolved_at} 해결` : "관찰 지속"} · {row.outcome ?? "결과 대기"}</small>
                  </article>
                ))}
                {!riskPresentation.history.length && <p>누적된 진단 이력이 아직 없습니다.</p>}
              </div>
            </section>

            <section className="pm-content-grid">
              <div className="pm-panel pm-items-panel">
                <header className="pm-section-heading">
                  <div><span>CONTRIBUTION</span><h2>종목·전략 결과</h2></div>
                  <small>종료 항목도 기록에 유지</small>
                </header>
                <div className="pm-item-list">
                  {itemSections.active.map(renderItemRow)}
                  {!itemSections.active.length && <div className="pm-empty-list">현재 활성 추적 항목이 없습니다.</div>}
                </div>
                {itemSections.ended.length > 0 && (
                  <details className="pm-ended-items" open={selectedItem?.status === "ended" || undefined}>
                    <summary>종료 기록 <span>{itemSections.ended.length}</span></summary>
                    <div className="pm-item-list">{itemSections.ended.map(renderItemRow)}</div>
                  </details>
                )}
              </div>

              <div className="pm-panel pm-detail-panel">
                <header className="pm-section-heading"><div><span>SELECTED DETAIL</span><h2>개별 추적 결과</h2></div></header>
                {selectedItem ? (
                  <div className="pm-detail-body">
                    <div className="pm-detail-title"><div><span>{itemLifecycleLabel(selectedItem)}</span><h3>{selectedItem.source_ref}</h3></div><b>{statusLabel(selectedItem.status)}</b></div>
                    <dl>
                      <div><dt>시작 투자금</dt><dd>{formatMetric(selectedItem.initial_capital, "currency", metrics)}</dd></div>
                      <div><dt>현재 가치</dt><dd>{formatMetric(selectedItem.current_value, "currency", metrics)}</dd></div>
                      <div><dt>기여 손익</dt><dd>{formatMetric(metrics?.contribution_by_item[selectedItem.monitoring_item_id], "currency", metrics)}</dd></div>
                    </dl>
                    {selectedItem.failure && <p className="pm-failure">{selectedItem.failure}</p>}
                    {workspace.selected_position.monitoring_item_id === selectedItem.monitoring_item_id && (
                      <PositionLedgerPanel
                        position={workspace.selected_position}
                        closeProjection={workspace.position_trade_close ?? null}
                        initialProjection={workspace.initial_position_entry ?? null}
                        recoveryState={workspace.position_editor_state}
                        latestCommand={latestCommand ?? null}
                        emit={emit}
                      />
                    )}
                    {selectedMarketChart?.monitoring_item_id !== selectedItem.monitoring_item_id ? (
                      <div className="pm-market-state"><strong>선택 항목 차트를 불러오는 중입니다.</strong></div>
                    ) : selectedMarketChart.source_type === "selected_strategy" ? (
                      <StrategyValueChart rows={activeGroup.curve} itemId={selectedItem.monitoring_item_id} />
                    ) : (
                      <MarketPriceChart projection={selectedMarketChart} />
                    )}
                    <div className="pm-detail-actions">
                      {selectedItem.status === "ended" ? <button type="button" className="pm-reopen-action" onClick={() => {
                        if (!window.confirm(`${selectedItem.source_ref}의 추적 종료를 취소할까요? 종료 상태와 종료금액이 취소되고 원래 시작일부터 계속 추적한 것으로 다시 계산됩니다.`)) return;
                        emit({ id: "reopen_item", command_id: newCommandId(), monitoring_item_id: selectedItem.monitoring_item_id });
                      }}>추적 종료 취소</button> : <button type="button" className="pm-end-action" onClick={() => {
                        if (!window.confirm(`${selectedItem.source_ref} 추적을 종료할까요? 종료 후에도 기록과 종료금액은 유지됩니다.`)) return;
                        emit({ id: "end_item", command_id: newCommandId(), monitoring_item_id: selectedItem.monitoring_item_id, requested_end_date: todayText() });
                      }}>추적 종료</button>}
                    </div>
                  </div>
                ) : <div className="pm-empty-list">왼쪽에서 항목을 선택하세요.</div>}
              </div>
            </section>

            <details className="pm-method">
              <summary>계산 기준과 제품 경계</summary>
              <div>
                <p>공통 기준: {workspace.method.basis}</p>
                <p>정렬 방식: {workspace.method.alignment}</p>
                <p>실시간 주문·자동 리밸런싱은 수행하지 않습니다.</p>
              </div>
            </details>
          </>
        ) : (
          <section className="pm-panel pm-empty-state"><h2>포트폴리오를 시작하세요</h2><p>기본 그룹에 미국 주식·ETF 또는 Final Review 통과 전략을 등록할 수 있습니다.</p><button type="button" className="pm-primary" onClick={openDrawer}>첫 종목 등록</button></section>
        )}
      </section>

      {drawerOpen && (
        <div className="pm-drawer-layer" role="presentation" onMouseDown={(event) => {
          if (event.currentTarget === event.target && localCommandState !== "pending") closeDrawer();
        }}>
          <section className="pm-drawer" role="dialog" aria-modal="true" aria-labelledby="pm-drawer-title">
            <header className="pm-drawer-header">
              <div><span>ADD MONITORING ITEM</span><h2 id="pm-drawer-title">종목·전략 등록</h2></div>
              <button ref={drawerCloseRef} type="button" aria-label="등록 창 닫기" onClick={closeDrawer} disabled={localCommandState === "pending"}>×</button>
            </header>
            <div className="pm-stepper" aria-label="등록 단계">
              {[1, 2, 3].map((step) => <span key={step} data-step={step} className={drawerStep >= step ? "is-active" : ""}><b>{step === 1 ? "대상" : step === 2 ? "투자 설정" : "확인"}</b></span>)}
            </div>

            {drawerStep === 1 && (
              <div className="pm-drawer-body">
                <div className="pm-source-switch">
                  <button type="button" className={draft.sourceType === "direct_security" ? "is-active" : ""} onClick={() => setDraft((current) => applySourceType(current, "direct_security"))}>미국 주식·ETF<small>DB에 저장된 상장 종목</small></button>
                  <button type="button" className={draft.sourceType === "selected_strategy" ? "is-active" : ""} onClick={() => setDraft((current) => applySourceType(current, "selected_strategy"))}>백테스트 전략<small>Final Review 통과 후보</small></button>
                </div>
                <form className="pm-catalog-search" onSubmit={submitCatalogSearch}>
                  <label htmlFor="pm-catalog-query">종목명·티커 또는 전략명</label>
                  <div><input id="pm-catalog-query" value={catalogQuery} onChange={(event) => setCatalogQuery(event.target.value)} placeholder={draft.sourceType === "direct_security" ? "예: AAPL, Gold ETF" : "예: GTAA, Risk Parity"} /><button type="submit">검색</button></div>
                </form>
                <div className="pm-catalog-list">
                  {workspace.catalog.items.filter((item) => item.source_type === draft.sourceType).map((item) => (
                    <button type="button" key={`${item.source_type}-${item.source_ref}`} className={draft.selectedSourceRef === item.source_ref ? "is-selected" : ""} onClick={() => setDraft((current) => ({ ...current, selectedSourceRef: item.source_ref, selectedLabel: item.label, selectedKind: item.instrument_kind }))}>
                      <div><strong>{item.source_ref}</strong><span>{item.label}</span></div><small>{item.instrument_kind.toUpperCase()} · {item.readiness}</small>
                    </button>
                  ))}
                  {!workspace.catalog.items.some((item) => item.source_type === draft.sourceType) && <p>검색어를 입력해 추적 대상을 찾으세요.</p>}
                </div>
              </div>
            )}

            {drawerStep === 2 && (
              <div className="pm-drawer-body">
                <div className="pm-selected-source"><span>선택 대상</span><strong>{draft.selectedSourceRef}</strong><small>{draft.selectedLabel}</small></div>
                <label className="pm-field">추적 시작일<input type="date" value={draft.requestedStartDate} onInput={(event) => { const requestedStartDate = event.currentTarget.value; setDraft((current) => ({ ...current, requestedStartDate })); }} /></label>
                <fieldset className="pm-funding-field"><legend>투자 방식</legend><div>{availableFundingModes(draft.sourceType).map((mode) => <button type="button" key={mode} className={draft.fundingMode === mode ? "is-active" : ""} onClick={() => setDraft((current) => ({ ...current, fundingMode: mode }))}>{mode === "fixed_notional" ? "투자금" : "보유 수량"}<small>{mode === "fixed_notional" ? "예: $10,000" : "정수 주식만"}</small></button>)}</div></fieldset>
                {draft.fundingMode === "fixed_notional" ? <label className="pm-field">투자금 (USD)<input type="number" min="1" step="1" value={draft.notional} onChange={(event) => setDraft((current) => ({ ...current, notional: event.target.value }))} /></label> : <label className="pm-field">주식 수량<input type="number" min="1" step="1" inputMode="numeric" value={draft.shares} onChange={(event) => setDraft((current) => ({ ...current, shares: event.target.value }))} /><small>소수점 없이 1주 이상 입력하세요.</small></label>}
                <div className="pm-entry-note"><strong>시작 가격 확인</strong><p>요청일이 휴장일이면 이후 첫 거래일의 저장 종가를 사용합니다. 이후 가격이 없으면 등록되지 않습니다.</p></div>
              </div>
            )}

            {drawerStep === 3 && (() => {
              const catalogItem = workspace.catalog.items.find((item) => item.source_type === draft.sourceType && item.source_ref === draft.selectedSourceRef);
              const validation = validateItemDraft(draft, { activeItems: activeGroup?.item_rows ?? [], capacity: 10, selectedReadiness: catalogItem?.readiness ?? null });
              const effectiveDate = String(catalogItem?.metadata?.effective_start_date ?? "등록 시 확정");
              return <div className="pm-drawer-body pm-review-body">
                <div className="pm-capacity"><span>활성 항목</span><strong>{activeGroup?.active_item_count ?? 0}/10</strong></div>
                <dl>
                  <div><dt>추적 대상</dt><dd>{draft.selectedSourceRef} · {draft.selectedKind}</dd></div>
                  <div><dt>요청 시작일</dt><dd>{draft.requestedStartDate || "-"}</dd></div>
                  <div><dt>예상 적용일</dt><dd>{effectiveDate}</dd></div>
                  <div><dt>투자 방식</dt><dd>{draft.fundingMode === "fixed_notional" ? `${formatMetric(Number(draft.notional), "currency")} 투자` : `${draft.shares || "-"}주 (정수)`}</dd></div>
                </dl>
                {validation && <p className="pm-review-error">{validation}</p>}
                {localCommandState !== "idle" && <p className={`pm-command-state is-${localCommandState}`}>{serverCommand?.message || (localCommandState === "pending" ? "등록 요청을 처리하고 있습니다." : localCommandState === "success" ? "등록이 완료됐습니다." : "등록 요청을 확인해 주세요.")}</p>}
                <button type="button" className="pm-submit-item" disabled={Boolean(validation) || localCommandState === "pending" || localCommandState === "success"} onClick={() => {
                  if (validation || !selectedGroup || localCommandState !== "idle" && localCommandState !== "error") return;
                  setLocalCommandState("pending");
                  emit({ id: "add_item", ...buildAddItemPayload(draft, selectedGroup.portfolio_group_id) });
                }}>{localCommandState === "pending" ? "등록 중…" : localCommandState === "success" ? "등록 완료" : "이 설정으로 등록"}</button>
              </div>;
            })()}

            <footer className="pm-drawer-footer">
              {drawerStep > 1 ? <button type="button" className="pm-secondary" disabled={localCommandState === "pending"} onClick={() => setDrawerStep((current) => Math.max(1, current - 1) as 1 | 2 | 3)}>이전</button> : <span />}
              {drawerStep < 3 && <button type="button" className="pm-primary" disabled={drawerStep === 1 ? !draft.selectedSourceRef : !draft.requestedStartDate} onClick={() => setDrawerStep((current) => Math.min(3, current + 1) as 1 | 2 | 3)}>다음</button>}
              {drawerStep === 3 && localCommandState === "success" && <button type="button" className="pm-primary" onClick={closeDrawer}>완료</button>}
            </footer>
          </section>
        </div>
      )}
    </main>
  );
}

export default withStreamlitConnection(PortfolioMonitoringWorkbench);
