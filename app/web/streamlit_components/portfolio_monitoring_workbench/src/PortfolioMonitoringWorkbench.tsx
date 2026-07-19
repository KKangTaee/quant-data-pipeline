import React, { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import type { DiagnosisRow, ItemRow, PortfolioMonitoringWorkspace } from "./contracts";
import {
  applySourceType,
  availableFundingModes,
  buildAddItemPayload,
  buildCatalogSearchEvent,
  buildCommonBasisBanner,
  buildGroupChartSeries,
  buildDiagnosisSections,
  buildMacroObservationPresentation,
  buildRiskCalibrationPresentation,
  createItemDraft,
  formatMetric,
  itemBuilderRecoveryKey,
  nearestChartPointIndex,
  normalizeItemBuilderState,
  placeChartTooltip,
  selectActiveGroup,
  selectItem,
  validateItemDraft,
} from "./workbenchState";
import type { ItemDraft } from "./workbenchState";
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
        <text x={inset.left} y={height - 10} className="pm-axis-date">{compactDate(series[0].date)}</text>
        <text x={width - inset.right} y={height - 10} textAnchor="end" className="pm-axis-date">{compactDate(series[series.length - 1]?.date ?? null)}</text>
      </svg>
    </div>
  );
}

function DiagnosisCard({ row, compact = false }: { row: DiagnosisRow; compact?: boolean }) {
  return (
    <article className={`pm-diagnosis-card is-${row.classification} severity-${row.severity.toLowerCase()}`}>
      <header><span>{row.severity}</span><b>{row.confidence} 근거</b></header>
      <h3>{row.meaning}</h3>
      <p>{row.measured_fact}</p>
      {!compact && (
        <details>
          <summary>판정 근거 전체 보기</summary>
          <dl>
            <div><dt>측정값</dt><dd>{row.measured_fact}</dd></div>
            <div><dt>판정 기준</dt><dd>{row.threshold}</dd></div>
            <div><dt>영향 비중</dt><dd>{formatMetric(row.affected_weight, "percent")}</dd></div>
            <div><dt>근거 범위</dt><dd>{formatMetric(row.coverage, "percent")} · {row.source_dates.join(", ") || "날짜 확인 필요"}</dd></div>
            <div><dt>변화 조건</dt><dd>{row.change_condition}</dd></div>
            <div><dt>다음 확인</dt><dd>{row.next_check}</dd></div>
          </dl>
        </details>
      )}
    </article>
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
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(serverGroup?.portfolio_group_id ?? null);
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(initialItemBuilder?.drawerOpen ?? false);
  const [drawerStep, setDrawerStep] = useState<1 | 2 | 3>(initialItemBuilder?.drawerStep ?? 1);
  const [catalogQuery, setCatalogQuery] = useState(initialItemBuilder?.catalogQuery ?? "");
  const [draft, setDraft] = useState<ItemDraft>(() => initialItemBuilder?.draft ?? createItemDraft(initialCommandId));
  const [localCommandState, setLocalCommandState] = useState<"idle" | "pending" | "success" | "error">("idle");
  const addButtonRef = useRef<HTMLButtonElement>(null);
  const drawerCloseRef = useRef<HTMLButtonElement>(null);
  const consumedRecoveryKeyRef = useRef<string | null>(itemBuilderRecoveryKey(initialItemBuilder));

  useEffect(() => {
    setSelectedGroupId(serverGroup?.portfolio_group_id ?? null);
  }, [serverGroup?.portfolio_group_id]);

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
  const metrics = activeGroup?.metrics;
  const diagnosis = workspace.diagnosis ?? {
    policy_version: "portfolio_monitoring_policy_v1",
    top_three: [], strengths: [], weaknesses: [], data_gaps: [], all_rows: [], coverage: 0,
  };
  const diagnosisSections = buildDiagnosisSections(diagnosis);
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

            <section className="pm-panel pm-diagnosis-panel" aria-label="포트폴리오 강점과 취약점">
              <header className="pm-section-heading">
                <div><span>PORTFOLIO DIAGNOSIS</span><h2>지금 확인할 변화</h2></div>
                <small>{diagnosis.policy_version} · 측정값과 해제 조건 기반</small>
              </header>
              <div className="pm-now-grid">
                {diagnosisSections.now.map((row) => <DiagnosisCard key={row.rule_id} row={row} compact />)}
                {!diagnosisSections.now.length && <div className="pm-diagnosis-empty">현재 상위 확인 신호가 없습니다. 근거가 충분해지면 최대 3개만 먼저 표시합니다.</div>}
              </div>
              <div className="pm-diagnosis-columns">
                <section><h3>강점</h3>{diagnosisSections.strengths.map((row) => <DiagnosisCard key={row.rule_id} row={row} />)}{!diagnosisSections.strengths.length && <p>확정된 강점 근거가 아직 없습니다.</p>}</section>
                <section><h3>취약점</h3>{diagnosisSections.weaknesses.map((row) => <DiagnosisCard key={row.rule_id} row={row} />)}{!diagnosisSections.weaknesses.length && <p>현재 기준을 넘은 취약점이 없습니다.</p>}</section>
                <section><h3>데이터 부족</h3>{diagnosisSections.dataGaps.map((row) => <DiagnosisCard key={row.rule_id} row={row} />)}{!diagnosisSections.dataGaps.length && <p>핵심 분류 근거의 coverage가 유지되고 있습니다.</p>}</section>
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
                    <div className="pm-detail-actions">
                      <button type="button" className="pm-text-action" onClick={() => emit({ id: "open_item_detail", monitoring_item_id: selectedItem.monitoring_item_id })}>상세 그래프와 근거 보기 →</button>
                      {selectedItem.status !== "ended" && <button type="button" className="pm-end-action" onClick={() => {
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
