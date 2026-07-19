import React, { useEffect, useMemo, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import type { ItemRow, PortfolioMonitoringWorkspace } from "./contracts";
import {
  buildCommonBasisBanner,
  buildGroupChartSeries,
  formatMetric,
  selectActiveGroup,
  selectItem,
} from "./workbenchState";
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

function ValueChart({ rows, items }: { rows: Array<Record<string, string | number | null>>; items: ItemRow[] }) {
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
  return (
    <div className="pm-chart-wrap">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="포트폴리오 가치곡선">
        <defs>
          <linearGradient id="pmArea" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.22" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.02" />
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
          <g className="pm-chart-point" key={`${point.date}-${index}`} tabIndex={0}>
            <circle cx={x(index)} cy={y(point.total)} r={3.4} />
            <title>{`${compactDate(point.date)} · ${formatMetric(point.total, "currency")}`}</title>
          </g>
        ))}
        <text x={inset.left} y={height - 10} className="pm-axis-date">{compactDate(series[0].date)}</text>
        <text x={width - inset.right} y={height - 10} textAnchor="end" className="pm-axis-date">{compactDate(series[series.length - 1]?.date ?? null)}</text>
      </svg>
    </div>
  );
}

function PortfolioMonitoringWorkbench({ args }: ComponentProps) {
  const workspace = (args?.payload ?? null) as PortfolioMonitoringWorkspace | null;
  const serverGroup = useMemo(
    () => selectActiveGroup(workspace?.groups ?? [], null),
    [workspace],
  );
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(serverGroup?.portfolio_group_id ?? null);
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);

  useEffect(() => {
    setSelectedGroupId(serverGroup?.portfolio_group_id ?? null);
  }, [serverGroup?.portfolio_group_id]);

  useEffect(() => {
    Streamlit.setFrameHeight();
  }, [workspace, selectedGroupId, selectedItemId]);

  if (!workspace) {
    return <div className="pm-empty">Portfolio Monitoring workspace를 불러오지 못했습니다.</div>;
  }
  const activeGroup = workspace.active_group;
  const selectedGroup = selectActiveGroup(workspace.groups, selectedGroupId);
  const selectedItem = selectItem(activeGroup?.item_rows ?? [], selectedItemId);
  const metrics = activeGroup?.metrics;
  const emit = (event: Record<string, unknown>) => {
    Streamlit.setComponentValue({ event: { ...event, nonce: `${Date.now()}-${Math.random()}` } });
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

  return (
    <main className="pm-workbench">
      <aside className="pm-group-rail" aria-label="포트폴리오 그룹">
        <header>
          <span>PORTFOLIOS</span>
          <button type="button" aria-label="포트폴리오 추가" onClick={() => emit({ id: "create_group", name: "새 포트폴리오" })}>+</button>
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
            <button type="button" className="pm-secondary" onClick={() => selectedGroup && emit({ id: "rename_group", portfolio_group_id: selectedGroup.portfolio_group_id, expected_version: selectedGroup.version })}>이름 변경</button>
            <button type="button" className="pm-primary" onClick={() => emit({ id: "open_item_drawer" })}>+ 종목 등록</button>
          </div>
        </header>

        {activeGroup ? (
          <>
            <div className={`pm-basis-banner ${activeGroup.status === "PARTIAL" ? "is-partial" : ""}`}>
              <span>{activeGroup.status === "PARTIAL" ? "확인 필요" : "공통 기준"}</span>
              <strong>{buildCommonBasisBanner(activeGroup)}</strong>
            </div>

            <section className="pm-kpi-grid" aria-label="포트폴리오 핵심 지표">
              <article><span>투자금</span><strong>{formatMetric(metrics?.invested_capital, "currency", metrics)}</strong><small>등록 원금 합계</small></article>
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

            <section className="pm-content-grid">
              <div className="pm-panel pm-items-panel">
                <header className="pm-section-heading">
                  <div><span>CONTRIBUTION</span><h2>종목·전략 결과</h2></div>
                  <small>종료 항목도 기록에 유지</small>
                </header>
                <div className="pm-item-list">
                  {activeGroup.item_rows.map((item) => {
                    const contribution = metrics?.contribution_by_item[item.monitoring_item_id] ?? (item.current_value - item.initial_capital);
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
                  })}
                  {!activeGroup.item_rows.length && <div className="pm-empty-list">첫 종목이나 백테스트 전략을 등록해 추적을 시작하세요.</div>}
                </div>
              </div>

              <div className="pm-panel pm-detail-panel">
                <header className="pm-section-heading"><div><span>SELECTED DETAIL</span><h2>개별 추적 결과</h2></div></header>
                {selectedItem ? (
                  <div className="pm-detail-body">
                    <div className="pm-detail-title"><div><span>{selectedItem.lane_status}</span><h3>{selectedItem.source_ref}</h3></div><b>{statusLabel(selectedItem.status)}</b></div>
                    <dl>
                      <div><dt>시작 투자금</dt><dd>{formatMetric(selectedItem.initial_capital, "currency", metrics)}</dd></div>
                      <div><dt>현재 가치</dt><dd>{formatMetric(selectedItem.current_value, "currency", metrics)}</dd></div>
                      <div><dt>기여 손익</dt><dd>{formatMetric(metrics?.contribution_by_item[selectedItem.monitoring_item_id], "currency", metrics)}</dd></div>
                    </dl>
                    {selectedItem.failure && <p className="pm-failure">{selectedItem.failure}</p>}
                    <button type="button" className="pm-text-action" onClick={() => emit({ id: "open_item_detail", monitoring_item_id: selectedItem.monitoring_item_id })}>상세 그래프와 근거 보기 →</button>
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
          <section className="pm-panel pm-empty-state"><h2>포트폴리오를 시작하세요</h2><p>기본 그룹에 미국 주식·ETF 또는 Final Review 통과 전략을 등록할 수 있습니다.</p><button type="button" className="pm-primary" onClick={() => emit({ id: "open_item_drawer" })}>첫 종목 등록</button></section>
        )}
      </section>
    </main>
  );
}

export default withStreamlitConnection(PortfolioMonitoringWorkbench);
