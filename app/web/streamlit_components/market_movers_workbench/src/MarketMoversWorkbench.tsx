import React, { useEffect, useMemo, useRef, useState } from "react";
import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import {
  buildPriceMomentumRange,
  priceMomentumRangeLabel,
  PriceMomentumRange,
} from "./priceMomentum";
import { buildStockResearchHandoffEvent } from "./marketResearchHandoff";
import "./style.css";

export type MarketMoverAction = {
  id: string;
  label: string;
  kind: "primary" | "secondary" | "disabled";
  detail?: string;
};

export type MarketMoverFilterControl = {
  id: string;
  label: string;
  value: string;
  options: Array<{ value: string; label: string }>;
  disabled?: boolean;
};

export type MarketMoversSectorBreadthPayload = {
  schema_version: "market_movers_sector_breadth_react_v1";
  component: "MarketMoversSectorBreadth";
  map: {
    schema_version: "market_movers_sector_map_v1";
    section_header: { kicker: string; title: string; detail: string };
    tone: string;
    status: string;
    headline: string;
    detail: string;
    freshness: string;
    participation: { label: string; value: string; detail: string; rail_pct: number };
    leadership: { label: string; value: string; detail: string };
    dispersion: { label: string; value: string; detail: string };
    lanes: Array<{
      rank: string | number;
      sector: string;
      tone: string;
      direction: "positive" | "negative";
      return_label: string;
      bar_pct: number;
      bar_width_pct: number;
      participation_label: string;
      participation_detail: string;
      cap_detail: string;
      top_gainer_detail: string;
      top_loser_detail: string;
    }>;
    boundary_note: string;
  };
  detail_table: {
    visible: boolean;
    default_open: boolean;
    title: string;
    columns: string[];
    rows: Array<Record<string, string | number | null>>;
    empty_text: string;
  };
};

export type MarketMoversTrustPanel = {
  schema_version: "market_movers_react_trust_panel_v1";
  visible: boolean;
  default_open: boolean;
  has_issues: boolean;
  title: string;
  kicker: string;
  state: string;
  tone: string;
  headline: string;
  detail?: string;
  items: Array<{ label: string; value: string; detail?: string }>;
  warnings: string[];
  grouped_rows: Array<Record<string, string | number>>;
  group_columns: string[];
  empty_text: string;
  suggested_action: { label: string; action_id: string; detail: string };
  boundary_note: string;
};

export type MarketMoversWorkbenchPayload = {
  schema_version: "market_movers_react_workbench_v1";
  component: "MarketMoversWorkbench";
  summary: {
    title: string;
    context: string;
    trust_state: string;
    trust_detail?: string;
    tone: string;
    action_label?: string;
    items: Array<{ label: string; value: string; detail?: string }>;
  };
  controls: {
    coverage: string;
    universe_limit: number;
    period: string;
    sector: string;
    top_n: number;
    mode: string;
  };
  filter_controls: {
    visible: boolean;
    items: MarketMoverFilterControl[];
  };
  refresh_mode: {
    visible: boolean;
    label: string;
    value: string;
    options: Array<{ value: string; label: string }>;
    disabled: boolean;
  };
  trust_panel: MarketMoversTrustPanel;
  eod_refresh_preflight?: Record<string, unknown>;
  control_ownership: {
    mode: "python_state_react_ui";
    migrated_controls: string[];
    deferred_controls: string[];
  };
  actions: MarketMoverAction[];
  action_note?: string;
};

export type MarketMoverInvestigationPanePayload = {
  schema_version: "market_mover_investigation_react_pane_v1";
  component: "MarketMoverInvestigationPane";
  symbol: string;
  panel: {
    title: string;
    subtitle: string;
    rank_badge: string;
    facts: Array<{ label: string; value: string; detail?: string }>;
    status_items: Array<{ label: string; value: string; tone: string }>;
    boundary_note: string;
  };
  actions: MarketMoverAction[];
  note: string;
};

type DecisionRow = Record<string, unknown>;

type DecisionGroupPeriod = {
  status?: string;
  flow?: DecisionRow[];
  bellwethers?: DecisionRow[];
  groups?: DecisionRow[];
  coverage?: Record<string, unknown>;
  date_window?: Record<string, unknown>;
};

export type MarketMoversDecisionWorkbenchPayload = {
  schema_version: "market_movers_decision_workbench_v1";
  component: "MarketMoversDecisionWorkbench";
  command_line: {
    values: {
      coverage: string;
      period: string;
      ranking_mode: string;
      top_n: number;
    };
    controls: MarketMoverFilterControl[];
  };
  trust: Record<string, unknown>;
  timing: {
    current_time: string;
    market_date: string;
    data_as_of: string;
    last_refreshed_at: string;
  };
  ranking: {
    period: string;
    ranking_mode: string;
    label: string;
    kind: string;
    rows: DecisionRow[];
    sort_basis?: string;
    empty_reason?: string;
  };
  group_context: {
    sector?: Record<string, DecisionGroupPeriod>;
    industry?: Record<string, DecisionGroupPeriod>;
  };
  breadth_selection: {
    group_by: "sector" | "industry";
    period: "daily" | "weekly" | "monthly";
  };
  selection: {
    symbol: string;
    row: DecisionRow;
    research?: Record<string, unknown> | null;
    financial_controls: {
      frequencies: Array<{ id: "quarterly" | "annual"; label: string }>;
      factor_groups: Array<{
        id: string;
        label: string;
        factors: Array<{
          id: string;
          label: string;
          unit: string;
          available_by_frequency: Record<string, boolean>;
        }>;
      }>;
      default_frequency: "quarterly" | "annual";
      default_factor?: string | null;
    };
  };
  actions: MarketMoverAction[];
  action_note?: string;
};

type MarketMoversPayload =
  | MarketMoversWorkbenchPayload
  | MarketMoversDecisionWorkbenchPayload
  | MarketMoverInvestigationPanePayload
  | MarketMoversSectorBreadthPayload;

type Props = Omit<ComponentProps, "args"> & {
  args: {
    payload?: MarketMoversPayload;
  };
};

function toneColor(tone: string) {
  const normalized = String(tone || "neutral").toLowerCase();
  if (normalized === "positive") {
    return "#0f766e";
  }
  if (normalized === "warning") {
    return "#b45309";
  }
  if (normalized === "danger") {
    return "#dc2626";
  }
  return "#64748b";
}

function clampPercent(value: number | string | undefined) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return 0;
  }
  return Math.max(0, Math.min(100, numeric));
}

function syncFrameHeightSoon() {
  Streamlit.setFrameHeight();
  window.requestAnimationFrame(() => Streamlit.setFrameHeight());
  window.setTimeout(() => Streamlit.setFrameHeight(), 160);
}

type InvestigationProps = {
  payload: MarketMoverInvestigationPanePayload;
  onAction: (action: MarketMoverAction) => void;
};

function MarketMoverInvestigationPane({ payload, onAction }: InvestigationProps) {
  return (
    <section
      className="mm-investigation"
      data-schema-version={payload.schema_version}
      data-symbol={payload.symbol}
    >
      <div className="mm-investigation__head">
        <div>
          <div className="mm-investigation__kicker">수동 조사 패널</div>
          <div className="mm-investigation__title">{payload.panel.title}</div>
          <div className="mm-investigation__subtitle">{payload.panel.subtitle}</div>
        </div>
        <span className="mm-investigation__rank">{payload.panel.rank_badge}</span>
      </div>
      <div className="mm-investigation__facts">
        {payload.panel.facts.map((fact) => (
          <div className="mm-investigation__fact" key={`${fact.label}-${fact.value}`}>
            <span>{fact.label}</span>
            <strong>{fact.value}</strong>
            {fact.detail ? <small>{fact.detail}</small> : null}
          </div>
        ))}
      </div>
      <div className="mm-investigation__status">
        {payload.panel.status_items.map((item) => (
          <span
            className="mm-investigation__status-item"
            key={`${item.label}-${item.value}`}
            style={{ "--mm-status-tone": toneColor(item.tone) } as React.CSSProperties}
          >
            {item.label} · {item.value}
          </span>
        ))}
      </div>
      <div className="mm-investigation__action-row">
        <div className="mm-investigation__actions" aria-label="Market mover investigation actions">
          {payload.actions.map((action) => (
            <button
              className={`mm-workbench__action mm-workbench__action--${action.kind}`}
              disabled={action.kind === "disabled"}
              key={action.id}
              onClick={() => onAction(action)}
              type="button"
            >
              <span className="mm-workbench__action-label">{action.label}</span>
              {action.detail ? <span className="mm-workbench__action-detail">{action.detail}</span> : null}
            </button>
          ))}
        </div>
        <span>{payload.note}</span>
      </div>
      <div className="mm-investigation__boundary">{payload.panel.boundary_note}</div>
    </section>
  );
}

function MarketMoversSectorBreadth({ payload }: { payload: MarketMoversSectorBreadthPayload }) {
  const stats = [payload.map.participation, payload.map.leadership, payload.map.dispersion];
  const railPct = clampPercent(payload.map.participation.rail_pct);

  return (
    <section
      className="mm-sector-breadth"
      data-schema-version={payload.schema_version}
      style={
        {
          "--mm-sector-tone": toneColor(payload.map.tone),
          "--mm-sector-rail": `${railPct}%`,
        } as React.CSSProperties
      }
    >
      <div className="mm-sector-breadth__head">
        <div>
          <div className="mm-sector-breadth__kicker">{payload.map.section_header.kicker}</div>
          <div className="mm-sector-breadth__title">{payload.map.section_header.title}</div>
          <div className="mm-sector-breadth__detail-copy">{payload.map.section_header.detail}</div>
        </div>
        <span className="mm-sector-breadth__status">{payload.map.status}</span>
      </div>
      <div className="mm-sector-breadth__result">
        <div className="mm-sector-breadth__result-title">{payload.map.headline}</div>
        <div className="mm-sector-breadth__result-detail">
          {payload.map.detail} · 기준: {payload.map.freshness}
        </div>
      </div>
      <div className="mm-sector-breadth__rail">
        <span className="mm-sector-breadth__rail-fill" />
      </div>
      <div className="mm-sector-breadth__stats">
        {stats.map((item) => (
          <div className="mm-sector-breadth__stat" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <small>{item.detail}</small>
          </div>
        ))}
      </div>
      <div className="mm-sector-breadth__lanes" aria-label="섹터별 확산 맥락">
        {payload.map.lanes.map((lane) => {
          const barWidth = clampPercent(lane.bar_width_pct);
          return (
            <div
              className={`mm-sector-breadth__lane mm-sector-breadth__lane--${lane.direction}`}
              key={`${lane.rank}-${lane.sector}`}
              style={
                {
                  "--mm-sector-lane-tone": toneColor(lane.tone),
                  "--mm-sector-lane-bar": `${barWidth}%`,
                } as React.CSSProperties
              }
            >
              <div className="mm-sector-breadth__lane-head">
                <span>
                  #{lane.rank} · {lane.sector}
                </span>
                <strong>{lane.return_label}</strong>
              </div>
              <div className="mm-sector-breadth__track">
                <span className="mm-sector-breadth__bar" />
              </div>
              <div className="mm-sector-breadth__lane-copy">
                {lane.participation_detail} · {lane.cap_detail}
              </div>
              <div className="mm-sector-breadth__lane-foot">
                {lane.top_gainer_detail} / {lane.top_loser_detail}
              </div>
            </div>
          );
        })}
      </div>
      {payload.map.boundary_note ? (
        <div className="mm-sector-breadth__boundary">{payload.map.boundary_note}</div>
      ) : null}
      {payload.detail_table.visible ? (
        <details
          className="mm-sector-breadth__detail"
          onToggle={syncFrameHeightSoon}
          open={payload.detail_table.default_open}
        >
          <summary className="mm-sector-breadth__detail-summary">
            <span>{payload.detail_table.title}</span>
            <small>{payload.detail_table.rows.length} rows</small>
          </summary>
          {payload.detail_table.rows.length > 0 ? (
            <div className="mm-sector-breadth__table" aria-label={payload.detail_table.title}>
              <div
                className="mm-sector-breadth__table-row mm-sector-breadth__table-row--head"
                style={
                  {
                    "--mm-sector-detail-columns": `repeat(${payload.detail_table.columns.length}, minmax(0, 1fr))`,
                  } as React.CSSProperties
                }
              >
                {payload.detail_table.columns.map((column) => (
                  <span key={column}>{column}</span>
                ))}
              </div>
              {payload.detail_table.rows.map((row, index) => (
                <div
                  className="mm-sector-breadth__table-row"
                  key={`sector-detail-${index}`}
                  style={
                    {
                      "--mm-sector-detail-columns": `repeat(${payload.detail_table.columns.length}, minmax(0, 1fr))`,
                    } as React.CSSProperties
                  }
                >
                  {payload.detail_table.columns.map((column) => (
                    <span key={column}>{String(row[column] ?? "-")}</span>
                  ))}
                </div>
              ))}
            </div>
          ) : (
            <div className="mm-sector-breadth__empty">{payload.detail_table.empty_text}</div>
          )}
        </details>
      ) : null}
    </section>
  );
}

const GROUP_MODES = ["sector", "industry"] as const;
const GROUP_PERIODS = ["daily", "weekly", "monthly"] as const;

function textValue(row: DecisionRow | undefined, ...keys: string[]) {
  for (const key of keys) {
    const value = row?.[key];
    if (value !== null && value !== undefined && String(value).trim()) {
      return String(value);
    }
  }
  return "-";
}

function numberValue(row: DecisionRow | undefined, ...keys: string[]) {
  for (const key of keys) {
    const numeric = Number(row?.[key]);
    if (Number.isFinite(numeric)) {
      return numeric;
    }
  }
  return null;
}

function formatSignedPercent(value: unknown) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? `${numeric >= 0 ? "+" : ""}${numeric.toFixed(2)}%` : "-";
}

function returnTone(value: unknown) {
  const numeric = typeof value === "string"
    ? Number(value.replace(/[,%+]/g, "").trim())
    : Number(value);
  if (!Number.isFinite(numeric) || numeric === 0) return "neutral";
  return numeric > 0 ? "positive" : "negative";
}

function formatCompact(value: unknown) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return "-";
  }
  const absolute = Math.abs(numeric);
  if (absolute >= 1_000_000_000_000) return `${(numeric / 1_000_000_000_000).toFixed(1)}T`;
  if (absolute >= 1_000_000_000) return `${(numeric / 1_000_000_000).toFixed(1)}B`;
  if (absolute >= 1_000_000) return `${(numeric / 1_000_000).toFixed(1)}M`;
  if (absolute >= 1_000) return `${(numeric / 1_000).toFixed(1)}K`;
  return numeric.toLocaleString("ko-KR", { maximumFractionDigits: 2 });
}

function rankingMetric(row: DecisionRow, mode: string) {
  if (mode === "volume_leaders") {
    return { label: "거래대금", value: `$${formatCompact(row["Dollar Volume"] ?? row["Volume Metric"])}` };
  }
  if (mode === "unusual_volume") {
    const relative = Number(row["Relative Volume"]);
    return { label: "상대 거래량", value: Number.isFinite(relative) ? `${relative.toFixed(2)}x` : "-" };
  }
  return { label: "수익률", value: formatSignedPercent(row["Return %"]) };
}

const PERIOD_LABELS: Record<string, string> = {
  daily: "일간",
  weekly: "주간",
  monthly: "월간",
};

function MarketPulse({ payload }: { payload: MarketMoversDecisionWorkbenchPayload }) {
  const period = payload.ranking.period;
  const leadingSector = (payload.group_context.sector?.[period]?.flow || [])[0];
  const items = [
    { label: "관측 기준", value: `${PERIOD_LABELS[period] || period} · ${payload.ranking.label}` },
    { label: "표시 종목", value: `${payload.ranking.rows.length.toLocaleString()}개` },
    leadingSector ? {
      label: "선도 섹터",
      value: textValue(leadingSector, "group", "Group"),
      detail: formatSignedPercent(numberValue(leadingSector, "relative_strength_pp")),
    } : null,
    { label: "자료 상태", value: String(payload.trust.state || "UNKNOWN") },
  ].filter(Boolean) as Array<{ label: string; value: string; detail?: string }>;

  return (
    <section className="mm-decision__pulse" aria-label="현재 시장 관측 요약">
      {items.map((item) => (
        <div className="mm-decision__pulse-item" key={item.label}>
          <small>{item.label}</small>
          <strong>{item.value}</strong>
          {item.detail ? <span className={`mm-return--${returnTone(item.detail)}`}>{item.detail}</span> : null}
        </div>
      ))}
    </section>
  );
}

function MarketMoversTimingAndActions({
  payload,
  onEvent,
}: {
  payload: MarketMoversDecisionWorkbenchPayload;
  onEvent: (event: Record<string, unknown>) => void;
}) {
  const timingItems = [
    ["현재 시각", payload.timing.current_time],
    ["최근 완료 시장일", payload.timing.market_date],
    ["랭킹 데이터 기준", payload.timing.data_as_of],
    ["마지막 수동 갱신", payload.timing.last_refreshed_at],
  ];
  return (
    <section className="mm-decision__timing-actions" aria-label="변동 종목 데이터 시각과 수동 갱신">
      <div className="mm-decision__timing-grid">
        {timingItems.map(([label, value]) => (
          <span key={label}><small>{label}</small><strong>{value}</strong></span>
        ))}
      </div>
      <div className="mm-decision__action-row">
        {payload.actions.map((action) => (
          <button
            className={`mm-decision__action mm-decision__action--${action.kind}`}
            disabled={action.kind === "disabled"}
            key={action.id}
            onClick={() => onEvent({ id: action.id })}
            type="button"
          >{action.label}</button>
        ))}
      </div>
      {payload.action_note ? <p>{payload.action_note}</p> : null}
    </section>
  );
}

type CommandLineProps = {
  payload: MarketMoversDecisionWorkbenchPayload;
  onControl: (control: MarketMoverFilterControl, value: string) => void;
};

function MarketMoversCommandLine({ payload, onControl }: CommandLineProps) {
  const trustState = String(payload.trust.state || "UNKNOWN");
  const metrics = (payload.trust.metrics || {}) as Record<string, Record<string, unknown>>;
  const returnMetric = metrics.return || {};
  const valid = Number(returnMetric.valid);
  const total = Number(returnMetric.total);
  const denominator = Number.isFinite(valid) && Number.isFinite(total) ? `${valid.toLocaleString()} / ${total.toLocaleString()}` : "-";
  return (
    <header className="mm-decision__command">
      <div className="mm-decision__surface-header">
        <div className="mm-decision__hero-copy">
          <div className="mm-decision__eyebrow">MARKET MOVERS</div>
          <h1>변동 종목</h1>
          <p>무엇이 움직였는지 찾고, 시장 확산을 확인한 뒤, 선택 종목의 저장 근거를 조사합니다.</p>
        </div>
        <div className={`mm-decision__trust mm-decision__trust--${trustState.toLowerCase()}`}>
          <span>자료 상태</span>
          <strong>{trustState}</strong>
          <small>랭킹 가능 {denominator}</small>
        </div>
      </div>
      <section className="mm-decision__command-band" aria-label="변동 종목 탐색 조건">
        <div className="mm-decision__controls">
          {payload.command_line.controls.map((control) => (
            <label className="mm-decision__control" key={control.id}>
              <span>{control.label}</span>
              <select
                disabled={control.disabled}
                onChange={(event) => onControl(control, event.target.value)}
                value={control.value}
              >
                {control.options.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </label>
          ))}
        </div>
      </section>
    </header>
  );
}

type RankingBoardProps = {
  payload: MarketMoversDecisionWorkbenchPayload;
  activeSymbol: string;
  onSelect: (row: DecisionRow) => void;
};

function RankingBoard({ payload, activeSymbol, onSelect }: RankingBoardProps) {
  const rows = payload.ranking.rows;
  return (
    <section className="mm-decision__ranking">
      <div className="mm-decision__section-head">
        <div>
          <span>RANKING</span>
          <h3>{payload.ranking.label} 상위 종목</h3>
        </div>
        <small>{rows.length}개 · {payload.ranking.sort_basis || "선택 기준"}</small>
      </div>
      {rows.length ? (
        <div className="mm-decision__rank-list" role="listbox" aria-label={`${payload.ranking.label} 상위 종목`}>
          {rows.map((row, index) => {
            const symbol = textValue(row, "Symbol", "symbol");
            const metric = rankingMetric(row, payload.ranking.ranking_mode);
            const returnPct = numberValue(row, "Return %", "return_pct");
            return (
              <button
                aria-selected={symbol === activeSymbol}
                className={`mm-decision__rank-row${symbol === activeSymbol ? " is-selected" : ""}`}
                key={`${symbol}-${index}`}
                onClick={() => onSelect(row)}
                role="option"
                style={{ "--mm-row-tone": returnPct !== null && returnPct < 0 ? "#b9554c" : "#19765f" } as React.CSSProperties}
                type="button"
              >
                <strong className="mm-decision__rank-number">{textValue(row, "Rank", "rank")}</strong>
                <span className="mm-decision__rank-identity">
                  <strong>{symbol}</strong>
                  <small>{textValue(row, "Name", "name")}</small>
                </span>
                <span className="mm-decision__rank-sector">
                  <strong>{textValue(row, "Sector", "sector")}</strong>
                  <small>{textValue(row, "Industry", "industry")}</small>
                </span>
                <span className="mm-decision__rank-volume">
                  <strong>{formatCompact(row["Volume"] ?? row["Current Volume"])}</strong>
                  <small>거래량</small>
                </span>
                <span className={`mm-decision__rank-metric mm-return--${returnTone(returnPct)}`}>
                  <small>{metric.label}</small>
                  <strong>{metric.value}</strong>
                </span>
              </button>
            );
          })}
        </div>
      ) : (
        <div className="mm-decision__empty">{payload.ranking.empty_reason || "표시할 랭킹 종목이 없습니다."}</div>
      )}
    </section>
  );
}

type BreadthContextProps = {
  payload: MarketMoversDecisionWorkbenchPayload;
  onRequest: (groupBy: "sector" | "industry", period: "daily" | "weekly" | "monthly") => void;
};

function BreadthContext({ payload, onRequest }: BreadthContextProps) {
  const initialMode = GROUP_MODES.includes(payload.breadth_selection.group_by)
    ? payload.breadth_selection.group_by
    : "sector";
  const [groupMode, setGroupMode] = useState<(typeof GROUP_MODES)[number]>(initialMode);
  const initialPeriod = GROUP_PERIODS.includes(payload.breadth_selection.period)
    ? payload.breadth_selection.period
    : "daily";
  const [groupPeriod, setGroupPeriod] = useState<(typeof GROUP_PERIODS)[number]>(initialPeriod);
  const periodPayload = payload.group_context[groupMode]?.[groupPeriod] || {};
  const flows = periodPayload.flow || [];
  const [selectedGroup, setSelectedGroup] = useState("");
  const activeGroup = flows.find((row) => textValue(row, "group", "Group") === selectedGroup) || flows[0];
  const activeGroupName = textValue(activeGroup, "group", "Group");
  const bellwethers = (periodPayload.bellwethers || []).filter(
    (row) => textValue(row, "Group", "group") === activeGroupName,
  );
  const stateLabels: Record<string, string> = {
    BROAD_STRENGTHENING: "확산하며 강화",
    NARROW_CAP_LED: "대형주 중심의 좁은 상승",
    WEAKENING: "확산 약화",
    REVERSAL_WATCH: "반전 관찰",
    MIXED: "혼재",
  };
  const switchMode = (mode: (typeof GROUP_MODES)[number]) => {
    setGroupMode(mode);
    setSelectedGroup("");
    onRequest(mode, groupPeriod);
  };
  const switchPeriod = (period: (typeof GROUP_PERIODS)[number]) => {
    setGroupPeriod(period);
    setSelectedGroup("");
    onRequest(groupMode, period);
  };
  return (
    <aside className="mm-decision__breadth">
      <div className="mm-decision__section-head">
        <div>
          <span>BREADTH CONTEXT</span>
          <h3>시장 확산 맥락</h3>
        </div>
      </div>
      <div className="mm-decision__breadth-toolbar">
        <div className="mm-decision__breadth-control-group">
          <span>분류</span>
          <div className="mm-decision__segmented" aria-label="그룹 기준">
            {["sector", "industry"].map((mode) => (
              <button className={groupMode === mode ? "is-active" : ""} key={mode} onClick={() => switchMode(mode as (typeof GROUP_MODES)[number])} type="button">
                {mode === "sector" ? "섹터" : "산업"}
              </button>
            ))}
          </div>
        </div>
        <i aria-hidden="true" />
        <div className="mm-decision__breadth-control-group">
          <span>기간</span>
          <div className="mm-decision__periods" aria-label="확산 기간">
            {["daily", "weekly", "monthly"].map((period) => (
              <button className={groupPeriod === period ? "is-active" : ""} key={period} onClick={() => switchPeriod(period as (typeof GROUP_PERIODS)[number])} type="button">
                {{ daily: "일", weekly: "주", monthly: "월" }[period]}
              </button>
            ))}
          </div>
        </div>
      </div>
      {flows.length ? (
        <>
          <div className="mm-decision__flow-list">
            {flows.slice(0, groupMode === "industry" ? 10 : 11).map((row) => {
              const group = textValue(row, "group", "Group");
              const breadth = numberValue(row, "positive_symbol_share_pct", "Positive Symbol Share %") || 0;
              const relative = numberValue(row, "relative_strength_pp") || 0;
              return (
                <button className={group === activeGroupName ? "is-selected" : ""} key={group} onClick={() => setSelectedGroup(group)} type="button">
                  <span><strong>{group}</strong><small>{stateLabels[textValue(row, "state")] || textValue(row, "state")}</small></span>
                  <span className="mm-decision__flow-track"><i style={{ width: `${clampPercent(breadth)}%` }} /></span>
                  <span><strong className={`mm-return--${returnTone(relative)}`}>{formatSignedPercent(relative)}</strong><small>시장 대비</small></span>
                </button>
              );
            })}
          </div>
          <div className="mm-decision__group-detail">
            <div>
              <span>선택 {groupMode === "sector" ? "섹터" : "산업"}</span>
              <strong>{activeGroupName}</strong>
              <small>{textValue(activeGroup, "next_observation")}</small>
            </div>
            <div className="mm-decision__group-facts">
              <span><small>상승 참여</small><strong>{formatSignedPercent(numberValue(activeGroup, "positive_symbol_share_pct"))}</strong></span>
              <span><small>동일가중</small><strong className={`mm-return--${returnTone(numberValue(activeGroup, "equal_weight_return_pct"))}`}>{formatSignedPercent(numberValue(activeGroup, "equal_weight_return_pct"))}</strong></span>
              <span><small>시총가중</small><strong className={`mm-return--${returnTone(numberValue(activeGroup, "market_cap_weighted_return_pct"))}`}>{formatSignedPercent(numberValue(activeGroup, "market_cap_weighted_return_pct"))}</strong></span>
            </div>
          </div>
          <div className="mm-decision__bellwethers">
            <div className="mm-decision__mini-head"><strong>시총 Top 3</strong><small>수익률 리더와 별도</small></div>
            {bellwethers.length ? bellwethers.slice(0, 3).map((row) => (
              <div key={`${activeGroupName}-${textValue(row, "Symbol")}`}>
                <span><strong>#{textValue(row, "Rank")}</strong><b>{textValue(row, "Symbol")}</b><small>{textValue(row, "Name")}</small></span>
                <span><strong className={`mm-return--${returnTone(row["Return %"])}`}>{formatSignedPercent(row["Return %"])}</strong><small>시총 {formatCompact(row["Market Cap"])}</small></span>
              </div>
            )) : <div className="mm-decision__empty">시총 근거가 충분한 대장주가 없습니다.</div>}
          </div>
        </>
      ) : <div className="mm-decision__empty">선택 기간의 {groupMode === "sector" ? "섹터" : "산업"} 흐름을 계산할 수 없습니다.</div>}
    </aside>
  );
}

type QuickResearchProps = {
  row: DecisionRow;
  onOpen: () => void;
};

function QuickResearch({ row, onOpen }: QuickResearchProps) {
  return (
    <section className="mm-decision__quick">
      <div className="mm-decision__quick-identity">
        <span>SELECTED RESEARCH</span>
        <strong>{textValue(row, "Symbol")} · {textValue(row, "Name")}</strong>
        <small>{textValue(row, "Sector")} · {textValue(row, "Industry")}</small>
      </div>
      <div className="mm-decision__quick-facts">
        <span><small>선택 기간 수익률</small><strong className={`mm-return--${returnTone(row["Return %"])}`}>{formatSignedPercent(row["Return %"])}</strong></span>
        <span><small>상대 거래량</small><strong>{numberValue(row, "Relative Volume") !== null ? `${numberValue(row, "Relative Volume")?.toFixed(2)}x` : "-"}</strong></span>
        <span><small>시가총액</small><strong>{formatCompact(row["Market Cap"])}</strong></span>
      </div>
      <button onClick={onOpen} type="button">상세 조사 열기</button>
    </section>
  );
}

type ChartPoint = {
  label: string;
  value: number;
  displayValue: string;
  axisLabel?: string;
};

function chartCoordinateList(points: ChartPoint[], width = 720, height = 250) {
  if (!points.length) return [];
  const values = points.map((point) => point.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || Math.max(Math.abs(max), 1);
  const insetX = 28;
  const insetY = 24;
  return points.map((point, index) => {
    const x = insetX + (index / Math.max(points.length - 1, 1)) * (width - insetX * 2);
    const y = height - insetY - ((point.value - min) / span) * (height - insetY * 2);
    return { x, y };
  });
}

function chartCoordinates(points: ChartPoint[], width = 720, height = 250) {
  return chartCoordinateList(points, width, height)
    .map(({ x, y }) => `${x.toFixed(1)},${y.toFixed(1)}`)
    .join(" ");
}

function financialBarGeometry(points: ChartPoint[], width = 720, height = 250) {
  if (!points.length) return { bars: [], zeroY: height - 24 };
  const values = points.map((point) => point.value);
  const min = Math.min(0, ...values);
  const max = Math.max(0, ...values);
  const span = max - min || 1;
  const insetX = 28;
  const insetY = 24;
  const usableWidth = width - insetX * 2;
  const zeroY = height - insetY - ((0 - min) / span) * (height - insetY * 2);
  const slot = usableWidth / Math.max(points.length, 1);
  const barWidth = Math.max(3, Math.min(22, slot * 0.68));
  const bars = points.map((point, index) => {
    const centerX = insetX + slot * (index + 0.5);
    const valueY = height - insetY - ((point.value - min) / span) * (height - insetY * 2);
    return {
      centerX,
      x: centerX - barWidth / 2,
      y: Math.min(valueY, zeroY),
      width: barWidth,
      height: Math.max(1, Math.abs(zeroY - valueY)),
      valueY,
      tone: returnTone(point.value),
    };
  });
  return { bars, zeroY };
}

function formatFinancialPeriodLabel(periodEnd: string, frequency: "quarterly" | "annual") {
  const date = new Date(`${periodEnd}T00:00:00`);
  if (Number.isNaN(date.getTime())) return periodEnd;
  const year = date.getFullYear();
  if (frequency === "annual") return String(year);
  return `${year} Q${Math.ceil((date.getMonth() + 1) / 3)}`;
}

function financialChartWidth(pointCount: number, frequency: "quarterly" | "annual") {
  const pointWidth = frequency === "quarterly" ? 58 : 72;
  return Math.max(720, pointCount * pointWidth + 56);
}

function financialTooltipLeftPx(
  coordinateX: number,
  scrollLeft: number,
  clientWidth: number,
  chartWidth: number,
) {
  const viewportWidth = clientWidth > 0 ? clientWidth : chartWidth;
  const minLeft = Math.min(chartWidth - 72, Math.max(72, scrollLeft + 72));
  const maxLeft = Math.max(minLeft, Math.min(chartWidth - 72, scrollLeft + viewportWidth - 72));
  return Math.max(minLeft, Math.min(maxLeft, coordinateX));
}

function priceChartTickIndexes(pointCount: number, range: string) {
  if (pointCount <= 0) return [];
  const targetCount = range === "1M" ? 5 : 7;
  if (pointCount <= targetCount) return Array.from({ length: pointCount }, (_, index) => index);
  return Array.from(
    new Set(Array.from({ length: targetCount }, (_, index) => (
      Math.round((index * (pointCount - 1)) / (targetCount - 1))
    ))),
  );
}

function formatPriceAxisLabel(dateValue: string, range: string) {
  const date = new Date(`${dateValue}T00:00:00`);
  if (Number.isNaN(date.getTime())) return dateValue;
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return range === "1M" ? `${month}-${day}` : `${date.getFullYear()}-${month}-${day}`;
}

function PriceMomentumChart({ research }: { research: Record<string, unknown> }) {
  const [range, setRange] = useState<PriceMomentumRange>("6M");
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const ytd = (research.ytd_return || {}) as Record<string, unknown>;
  const rawSeries = Array.isArray(ytd.price_series)
    ? ytd.price_series as DecisionRow[]
    : Array.isArray(ytd.series) ? ytd.series as DecisionRow[] : [];
  const rangeSeries = buildPriceMomentumRange(rawSeries, range);
  const points: ChartPoint[] = rangeSeries.map((row) => ({
    label: row.date,
    value: row.returnPct,
    displayValue: `${formatSignedPercent(row.returnPct)} · $${row.price.toFixed(2)}`,
  }));
  const latest = points[points.length - 1];
  const lowest = points.length ? points.reduce((left, right) => left.value < right.value ? left : right) : null;
  const highest = points.length ? points.reduce((left, right) => left.value > right.value ? left : right) : null;
  const coordinates = chartCoordinateList(points);
  const resolvedIndex = activeIndex === null ? Math.max(0, points.length - 1) : Math.min(activeIndex, points.length - 1);
  const activePoint = activeIndex === null ? null : points[resolvedIndex];
  const activeCoordinate = activeIndex === null ? null : coordinates[resolvedIndex];
  const priceTooltipPlacement = activeCoordinate && activeCoordinate.y < 92 ? "below" : "above";
  const priceTickIndexes = priceChartTickIndexes(points.length, range);
  const moveActivePoint = (event: React.PointerEvent<SVGSVGElement>) => {
    const bounds = event.currentTarget.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (event.clientX - bounds.left) / Math.max(bounds.width, 1)));
    setActiveIndex(Math.round(ratio * Math.max(points.length - 1, 0)));
  };
  return (
    <div className="mm-decision__chart-layout">
      <div className="mm-decision__chart-panel">
        <div className="mm-decision__chart-toolbar">
          <div><strong>조정주가 흐름</strong><small>선택 기간 시작=0%</small></div>
          <div className="mm-decision__range-controls">
            {["1M", "3M", "6M", "1Y"].map((item) => (
              <button className={range === item ? "is-active" : ""} key={item} onClick={() => setRange(item as PriceMomentumRange)} type="button">{item}</button>
            ))}
          </div>
        </div>
        {points.length >= 2 ? (
          <div className="mm-decision__svg-wrap">
            <svg
              aria-label={`${range} 조정주가 정규화 흐름`}
              onBlur={() => setActiveIndex(null)}
              onFocus={() => setActiveIndex(Math.max(0, points.length - 1))}
              onKeyDown={(event) => {
                if (event.key === "ArrowLeft") setActiveIndex(Math.max(0, resolvedIndex - 1));
                if (event.key === "ArrowRight") setActiveIndex(Math.min(points.length - 1, resolvedIndex + 1));
              }}
              onPointerLeave={() => setActiveIndex(null)}
              onPointerMove={moveActivePoint}
              preserveAspectRatio="none"
              role="img"
              tabIndex={0}
              viewBox="0 0 720 250"
            >
              <line x1="28" x2="692" y1="226" y2="226" />
              <line x1="28" x2="692" y1="24" y2="24" />
              <polyline fill="none" points={chartCoordinates(points)} stroke="#397fb7" strokeLinejoin="round" strokeWidth="3" />
              {activeCoordinate ? <line className="mm-decision__chart-guide" x1={activeCoordinate.x} x2={activeCoordinate.x} y1="24" y2="226" /> : null}
              {activeCoordinate ? <circle className="mm-decision__chart-dot" cx={activeCoordinate.x} cy={activeCoordinate.y} r="5" /> : null}
            </svg>
            {activePoint && activeCoordinate ? (
              <div
                className="mm-decision__chart-tooltip"
                data-placement={priceTooltipPlacement}
                style={{
                  left: `clamp(72px, ${(activeCoordinate.x / 720) * 100}%, calc(100% - 72px))`,
                  top: `${priceTooltipPlacement === "below" ? activeCoordinate.y + 12 : Math.max(8, activeCoordinate.y - 12)}px`,
                }}
              >
                <strong>{activePoint.label}</strong>
                <span className={`mm-return--${returnTone(activePoint.value)}`}>{activePoint.displayValue}</span>
              </div>
            ) : null}
            <div className="mm-decision__chart-ticks mm-decision__chart-ticks--price" aria-hidden="true">
              {priceTickIndexes.map((index) => {
                const point = points[index];
                const coordinate = coordinates[index];
                return (
                  <span
                    key={`${point.label}-price-tick`}
                    style={{ left: `clamp(42px, ${((coordinate?.x || 0) / 720) * 100}%, calc(100% - 42px))` }}
                  >{formatPriceAxisLabel(point.label, range)}</span>
                );
              })}
            </div>
          </div>
        ) : <div className="mm-decision__chart-empty">선택 범위에 표시할 저장 가격 이력이 부족합니다.</div>}
      </div>
      <aside className="mm-decision__chart-readout">
        <span className="is-primary"><small>{priceMomentumRangeLabel(range)}</small><strong className={`mm-return--${returnTone(latest?.value)}`}>{latest ? formatSignedPercent(latest.value) : "-"}</strong></span>
        <span className="is-latest"><small>최근 값</small><strong className={`mm-return--${returnTone(latest?.value)}`}>{latest?.displayValue || "-"}</strong></span>
        <span className="is-high"><small>범위 최고</small><strong className={`mm-return--${returnTone(highest?.value)}`}>{highest ? formatSignedPercent(highest.value) : "-"}</strong></span>
        <span className="is-low"><small>범위 최저</small><strong className={`mm-return--${returnTone(lowest?.value)}`}>{lowest ? formatSignedPercent(lowest.value) : "-"}</strong></span>
        <p>{String(ytd.basis || "DB daily adjusted close")}</p>
      </aside>
    </div>
  );
}

function factorDisplayValue(value: number, unit: string) {
  if (unit === "percent") return `${value.toFixed(2)}%`;
  if (unit === "ratio") return `${value.toFixed(2)}x`;
  if (unit === "currency_per_share") return `$${value.toFixed(2)}`;
  return formatCompact(value);
}

type FinancialFactorChartProps = {
  research: Record<string, unknown>;
  controls: MarketMoversDecisionWorkbenchPayload["selection"]["financial_controls"];
};

function FinancialFactorChart({ research, controls }: FinancialFactorChartProps) {
  const [frequency, setFrequency] = useState<"quarterly" | "annual">(controls.default_frequency);
  const [factorId, setFactorId] = useState(controls.default_factor || "");
  const firstGroup = controls.factor_groups.find((group) => group.factors.some((factor) => factor.id === factorId));
  const [groupId, setGroupId] = useState(firstGroup?.id || controls.factor_groups[0]?.id || "income");
  const frequencySeries = ((research.financial_factor_series || {}) as Record<string, unknown>)[frequency] as Record<string, unknown> | undefined;
  const factors = (frequencySeries?.factors || {}) as Record<string, Record<string, unknown>>;
  const factor = factors[factorId] || {};
  const unit = String(factor.unit || "number");
  const [chartMode, setChartMode] = useState<"bar" | "line">("bar");
  const [activeFinancialIndex, setActiveFinancialIndex] = useState<number | null>(null);
  const [isFinancialDragging, setIsFinancialDragging] = useState(false);
  const [financialViewport, setFinancialViewport] = useState({ scrollLeft: 0, clientWidth: 720 });
  const financialScrollRef = useRef<HTMLDivElement | null>(null);
  const financialSvgRef = useRef<SVGSVGElement | null>(null);
  const financialDragRef = useRef({ pointerId: -1, startX: 0, startScrollLeft: 0 });
  const rawPoints = Array.isArray(factor.points) ? factor.points as DecisionRow[] : [];
  const points: ChartPoint[] = rawPoints.map((row) => {
    const value = numberValue(row, "value") || 0;
    const periodEnd = textValue(row, "period_end");
    return {
      label: periodEnd,
      axisLabel: formatFinancialPeriodLabel(periodEnd, frequency),
      value,
      displayValue: factorDisplayValue(value, unit),
    };
  });
  const activeGroup = controls.factor_groups.find((group) => group.id === groupId) || controls.factor_groups[0];
  const currentValuation = (research.current_valuation || {}) as Record<string, unknown>;
  const chartWidth = financialChartWidth(points.length, frequency);
  const financialCoordinates = chartCoordinateList(points, chartWidth);
  const barGeometry = financialBarGeometry(points, chartWidth);
  const resolvedFinancialIndex = activeFinancialIndex === null
    ? Math.max(0, points.length - 1)
    : Math.min(activeFinancialIndex, points.length - 1);
  const activeFinancialPoint = activeFinancialIndex === null ? null : points[resolvedFinancialIndex];
  const activeFinancialCoordinate = activeFinancialIndex === null
    ? null
    : chartMode === "bar"
      ? {
          x: barGeometry.bars[resolvedFinancialIndex]?.centerX || 0,
          y: barGeometry.bars[resolvedFinancialIndex]?.valueY || 0,
        }
      : financialCoordinates[resolvedFinancialIndex];
  const financialTooltipPlacement = activeFinancialCoordinate && activeFinancialCoordinate.y < 92 ? "below" : "above";
  const financialTooltipLeft = activeFinancialCoordinate
    ? financialTooltipLeftPx(
        activeFinancialCoordinate.x,
        financialViewport.scrollLeft,
        financialViewport.clientWidth,
        chartWidth,
      )
    : 0;
  const syncFinancialViewport = (viewport: HTMLDivElement) => {
    const nextViewport = { scrollLeft: viewport.scrollLeft, clientWidth: viewport.clientWidth };
    setFinancialViewport((current) => (
      current.scrollLeft === nextViewport.scrollLeft && current.clientWidth === nextViewport.clientWidth
        ? current
        : nextViewport
    ));
  };
  useEffect(() => {
    setChartMode(unit === "percent" || unit === "ratio" ? "line" : "bar");
  }, [factorId, frequency, unit]);
  useEffect(() => {
    setActiveFinancialIndex(null);
    const frame = window.requestAnimationFrame(() => {
      const viewport = financialScrollRef.current;
      if (viewport) {
        viewport.scrollLeft = Math.max(0, viewport.scrollWidth - viewport.clientWidth);
        syncFinancialViewport(viewport);
      }
    });
    return () => window.cancelAnimationFrame(frame);
  }, [factorId, frequency, points.length, research]);
  const revealFinancialPoint = (index: number) => {
    const viewport = financialScrollRef.current;
    const svg = financialSvgRef.current;
    const coordinate = financialCoordinates[index];
    if (!viewport || !svg || !coordinate) return;
    const renderedWidth = svg.getBoundingClientRect().width;
    const pointX = (coordinate.x / chartWidth) * renderedWidth;
    const nextLeft = Math.max(0, pointX - viewport.clientWidth / 2);
    viewport.scrollTo({ left: nextLeft, behavior: "smooth" });
  };
  const setFinancialPointFromClientX = (clientX: number) => {
    const svg = financialSvgRef.current;
    if (!svg || !points.length) return;
    const bounds = svg.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (clientX - bounds.left) / Math.max(bounds.width, 1)));
    setActiveFinancialIndex(Math.round(ratio * Math.max(points.length - 1, 0)));
  };
  const beginFinancialDrag = (event: React.PointerEvent<HTMLDivElement>) => {
    if (event.button !== 0) return;
    financialDragRef.current = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startScrollLeft: event.currentTarget.scrollLeft,
    };
    setIsFinancialDragging(true);
    event.currentTarget.setPointerCapture(event.pointerId);
    setFinancialPointFromClientX(event.clientX);
  };
  const handleFinancialPointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    setFinancialPointFromClientX(event.clientX);
    if (financialDragRef.current.pointerId !== event.pointerId) return;
    event.currentTarget.scrollLeft = financialDragRef.current.startScrollLeft
      - (event.clientX - financialDragRef.current.startX);
    syncFinancialViewport(event.currentTarget);
  };
  const endFinancialDrag = (event: React.PointerEvent<HTMLDivElement>) => {
    if (financialDragRef.current.pointerId !== event.pointerId) return;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    financialDragRef.current.pointerId = -1;
    setIsFinancialDragging(false);
  };
  const chooseFrequency = (nextFrequency: "quarterly" | "annual") => {
    setFrequency(nextFrequency);
    const currentControl = controls.factor_groups.flatMap((group) => group.factors).find((item) => item.id === factorId);
    if (!currentControl?.available_by_frequency[nextFrequency]) {
      const fallback = controls.factor_groups.flatMap((group) => group.factors).find((item) => item.available_by_frequency[nextFrequency]);
      if (fallback) {
        setFactorId(fallback.id);
        const fallbackGroup = controls.factor_groups.find((group) => group.factors.some((item) => item.id === fallback.id));
        if (fallbackGroup) setGroupId(fallbackGroup.id);
      }
    }
  };
  return (
    <div className="mm-decision__financial">
      <div className="mm-decision__financial-control-row">
        <div>
          <span>보고 주기</span>
          <div className="mm-decision__financial-frequency">
            {controls.frequencies.map((item) => (
              <button className={frequency === item.id ? "is-active" : ""} key={item.id} onClick={() => chooseFrequency(item.id)} type="button">{item.label}</button>
            ))}
          </div>
        </div>
        <div>
          <span>재무 영역</span>
          <div className="mm-decision__financial-groups">
            {controls.factor_groups.map((group) => (
              <button className={groupId === group.id ? "is-active" : ""} key={group.id} onClick={() => setGroupId(group.id)} type="button">{group.label}</button>
            ))}
          </div>
        </div>
      </div>
      <div className="mm-decision__financial-factor-row">
        <span>재무 Factor</span>
        <div className="mm-decision__financial-factors">
          {(activeGroup?.factors || []).map((factorControl) => {
            const available = Boolean(factorControl.available_by_frequency[frequency]);
            return (
              <button
                className={factorId === factorControl.id ? "is-active" : ""}
                disabled={!available}
                key={factorControl.id}
                onClick={() => setFactorId(factorControl.id)}
                title={available ? `${factorControl.label} 표시` : `${frequency === "quarterly" ? "분기" : "연간"} 근거 없음`}
                type="button"
              >{factorControl.label}</button>
            );
          })}
        </div>
      </div>
      <div className="mm-decision__chart-layout">
        <div className="mm-decision__chart-panel">
          <div className="mm-decision__chart-toolbar">
            <div><strong>{String(factor.label || "재무 factor")}</strong><small>{frequency === "quarterly" ? "분기" : "연간"} · 단일 factor</small></div>
            <div className="mm-decision__chart-mode" aria-label="재무 차트 표현">
              <button className={chartMode === "bar" ? "is-active" : ""} onClick={() => setChartMode("bar")} type="button">막대</button>
              <button className={chartMode === "line" ? "is-active" : ""} onClick={() => setChartMode("line")} type="button">선</button>
            </div>
          </div>
          {points.length ? (
            <div
              aria-label="재무 차트 가로 탐색 영역"
              className="mm-decision__chart-scroll"
              data-dragging={isFinancialDragging ? "true" : "false"}
              onPointerCancel={endFinancialDrag}
              onPointerDown={beginFinancialDrag}
              onPointerLeave={() => {
                if (financialDragRef.current.pointerId < 0) setActiveFinancialIndex(null);
              }}
              onPointerMove={handleFinancialPointerMove}
              onPointerUp={endFinancialDrag}
              onScroll={(event) => syncFinancialViewport(event.currentTarget)}
              ref={financialScrollRef}
            >
              <div className="mm-decision__chart-inner" style={{ minWidth: "100%", width: `${chartWidth}px` }}>
                <div className="mm-decision__svg-wrap">
                  <svg
                    aria-label={`${String(factor.label || factorId)} ${frequency === "quarterly" ? "분기" : "연간"} 추이`}
                    onBlur={() => setActiveFinancialIndex(null)}
                    onFocus={() => setActiveFinancialIndex(Math.max(0, points.length - 1))}
                    onKeyDown={(event) => {
                      let nextIndex = resolvedFinancialIndex;
                      if (event.key === "ArrowLeft") nextIndex = Math.max(0, resolvedFinancialIndex - 1);
                      else if (event.key === "ArrowRight") nextIndex = Math.min(points.length - 1, resolvedFinancialIndex + 1);
                      else if (event.key === "Home") nextIndex = 0;
                      else if (event.key === "End") nextIndex = Math.max(0, points.length - 1);
                      else return;
                      event.preventDefault();
                      setActiveFinancialIndex(nextIndex);
                      revealFinancialPoint(nextIndex);
                    }}
                    preserveAspectRatio="none"
                    ref={financialSvgRef}
                    role="img"
                    tabIndex={0}
                    viewBox={`0 0 ${chartWidth} 250`}
                  >
                    <line x1="28" x2={chartWidth - 28} y1={chartMode === "bar" ? barGeometry.zeroY : 226} y2={chartMode === "bar" ? barGeometry.zeroY : 226} />
                    <line x1="28" x2={chartWidth - 28} y1="24" y2="24" />
                    {chartMode === "bar" ? barGeometry.bars.map((bar, index) => (
                      <rect
                        className={`mm-decision__financial-bar mm-return-fill--${bar.tone}${activeFinancialIndex === index ? " is-active" : ""}`}
                        height={bar.height}
                        key={`${points[index].label}-${index}`}
                        rx="2"
                        width={bar.width}
                        x={bar.x}
                        y={bar.y}
                      />
                    )) : (
                      <polyline fill="none" points={chartCoordinates(points, chartWidth)} stroke="#2f7f73" strokeLinejoin="round" strokeWidth="3" />
                    )}
                    {activeFinancialCoordinate ? <line className="mm-decision__chart-guide" x1={activeFinancialCoordinate.x} x2={activeFinancialCoordinate.x} y1="24" y2="226" /> : null}
                    {activeFinancialCoordinate && chartMode === "line" ? <circle className="mm-decision__chart-dot" cx={activeFinancialCoordinate.x} cy={activeFinancialCoordinate.y} r="5" /> : null}
                  </svg>
                  {activeFinancialPoint && activeFinancialCoordinate ? (
                    <div
                      className="mm-decision__chart-tooltip"
                      data-placement={financialTooltipPlacement}
                      style={{
                        left: `${financialTooltipLeft}px`,
                        top: `${financialTooltipPlacement === "below" ? activeFinancialCoordinate.y + 12 : Math.max(8, activeFinancialCoordinate.y - 12)}px`,
                      }}
                    >
                      <strong>{activeFinancialPoint.axisLabel}</strong>
                      <small>{activeFinancialPoint.label}</small>
                      <span>{activeFinancialPoint.displayValue}</span>
                    </div>
                  ) : null}
                </div>
                <div className="mm-decision__chart-ticks" aria-hidden="true">
                  {points.map((point, index) => (
                    <span
                      key={`${point.label}-tick`}
                      style={{ left: `${((financialCoordinates[index]?.x || 0) / chartWidth) * 100}%` }}
                    >{point.axisLabel}</span>
                  ))}
                </div>
              </div>
            </div>
          ) : <div className="mm-decision__chart-empty">선택 factor의 {frequency === "quarterly" ? "분기" : "연간"} 근거가 없습니다.</div>}
        </div>
        <aside className="mm-decision__chart-readout">
          <span><small>최근 값</small><strong>{points[points.length - 1]?.displayValue || "-"}</strong></span>
          <span><small>기간 수</small><strong>{points.length}</strong></span>
          <span><small>제외 기간</small><strong>{Number(factor.excluded_count || 0)}</strong></span>
          <span><small>현재 PER</small><strong>{currentValuation.status === "OK" ? `${Number(currentValuation.current_per).toFixed(2)}x` : "계산 불가"}</strong></span>
          {currentValuation.status !== "OK" ? <p>보고된 희석 EPS 네 분기가 모두 있어야 current PER를 표시합니다.</p> : null}
        </aside>
      </div>
    </div>
  );
}

type StockResearchTabsProps = {
  payload: MarketMoversDecisionWorkbenchPayload;
  activeSymbol: string;
  onEvent: (event: Record<string, unknown>) => void;
};

function StockResearchTabs({ payload, activeSymbol, onEvent }: StockResearchTabsProps) {
  const [tab, setTab] = useState<"price" | "financial" | "events">("price");
  const research = payload.selection.symbol === activeSymbol ? payload.selection.research : null;
  const eventEvidence = ((research?.event_evidence || {}) as Record<string, unknown>);
  const dbFilingStatus = String(eventEvidence.db_filing_status || "EMPTY");
  const dbFilingSource = String(eventEvidence.db_filing_source || "저장 공시 ledger");
  const dbFilingMessage = String(eventEvidence.db_filing_message || "");
  const dbFilings = Array.isArray(eventEvidence.db_filings) ? eventEvidence.db_filings as DecisionRow[] : [];
  const newsEvidence = [
    ...(Array.isArray(eventEvidence.news) ? eventEvidence.news as DecisionRow[] : []),
    ...(Array.isArray(eventEvidence.korean_news) ? eventEvidence.korean_news as DecisionRow[] : []),
  ];
  const secEvidence = Array.isArray(eventEvidence.sec_filings) ? eventEvidence.sec_filings as DecisionRow[] : [];
  const researchTabs = [
    ["price", "가격·모멘텀"],
    ["financial", "재무"],
    ["events", "뉴스·공시"],
  ] as const;
  const moveResearchTab = (event: React.KeyboardEvent<HTMLButtonElement>, currentIndex: number) => {
    let nextIndex = currentIndex;
    if (event.key === "ArrowRight") nextIndex = (currentIndex + 1) % researchTabs.length;
    else if (event.key === "ArrowLeft") nextIndex = (currentIndex - 1 + researchTabs.length) % researchTabs.length;
    else if (event.key === "Home") nextIndex = 0;
    else if (event.key === "End") nextIndex = researchTabs.length - 1;
    else return;

    event.preventDefault();
    const nextTab = researchTabs[nextIndex][0];
    const ownerDocument = event.currentTarget.ownerDocument;
    setTab(nextTab);
    ownerDocument.defaultView?.requestAnimationFrame(() => {
      ownerDocument.getElementById(`mm-decision-tab-${nextTab}`)?.focus();
    });
  };
  return (
    <section className="mm-decision__research">
      <div className="mm-decision__research-head">
        <div><span>DEEP RESEARCH</span><h3>{activeSymbol} 상세 조사</h3></div>
        <div className="mm-decision__tabs" role="tablist">
          {researchTabs.map(([id, label], index) => (
            <button
              aria-controls={`mm-decision-panel-${id}`}
              aria-selected={tab === id}
              className={tab === id ? "is-active" : ""}
              id={`mm-decision-tab-${id}`}
              key={id}
              onKeyDown={(event) => moveResearchTab(event, index)}
              onClick={() => setTab(id)}
              role="tab"
              tabIndex={tab === id ? 0 : -1}
              type="button"
            >{label}</button>
          ))}
        </div>
        <button
          className="mm-decision__stock-analysis-link"
          onClick={() => onEvent(buildStockResearchHandoffEvent(activeSymbol))}
          type="button"
        >
          개별 종목 분석
        </button>
      </div>
      <div aria-labelledby="mm-decision-tab-price" hidden={tab !== "price"} id="mm-decision-panel-price" role="tabpanel">
        {research ? <PriceMomentumChart research={research} /> : (
          <div className="mm-decision__research-loading">선택 종목의 저장 근거를 불러오는 중입니다.</div>
        )}
      </div>
      <div aria-labelledby="mm-decision-tab-financial" hidden={tab !== "financial"} id="mm-decision-panel-financial" role="tabpanel">
        {research ? <FinancialFactorChart controls={payload.selection.financial_controls} research={research} /> : (
          <div className="mm-decision__research-loading">선택 종목의 저장 근거를 불러오는 중입니다.</div>
        )}
      </div>
      <div aria-labelledby="mm-decision-tab-events" hidden={tab !== "events"} id="mm-decision-panel-events" role="tabpanel">
        {research ? (
          <div className="mm-decision__events-panel">
            <div className="mm-decision__events-head">
              <div>
                <strong>뉴스·공시 근거</strong>
                <p>DB에 저장된 공시는 즉시 표시하고, 외부 뉴스와 최신 SEC 메타데이터는 요청할 때만 조회합니다.</p>
              </div>
              <div className="mm-decision__evidence-actions">
                <button onClick={() => onEvent({ id: "fetch_news_evidence", symbol: activeSymbol, name: textValue(payload.selection.row, "Name", "name") })} type="button">뉴스 근거 조회</button>
                <button onClick={() => onEvent({ id: "fetch_sec_evidence", symbol: activeSymbol })} type="button">SEC 최신 조회</button>
              </div>
            </div>
            <div className="mm-decision__events-status">
              <span><small>저장 재무제표</small><strong>{String(((research.financial_statement_collection || {}) as Record<string, unknown>).status || "UNKNOWN")}</strong></span>
              <span><small>외부 근거</small><strong>{String(eventEvidence.status || "NOT_REQUESTED")}</strong></span>
              <span><small>기준일</small><strong>{String(research.as_of_date || "-")}</strong></span>
              <span><small>조회 시각</small><strong>{String(eventEvidence.fetched_at_utc || "세션 미조회")}</strong></span>
            </div>
            <div className="mm-decision__evidence-section">
              <div className="mm-decision__evidence-title"><strong>저장 공시 근거</strong><small>{dbFilingStatus} · 최대 5건</small></div>
              <div className={`mm-decision__evidence-message mm-decision__evidence-message--${dbFilingStatus.toLowerCase()}`}><strong>{dbFilingSource}</strong>{dbFilingMessage ? <span>{dbFilingMessage}</span> : null}</div>
              {dbFilings.length ? dbFilings.map((row, index) => (
                <a className="mm-decision__evidence-card" href={textValue(row, "url", "URL")} key={`${textValue(row, "accession_no")}-${index}`} rel="noreferrer" target="_blank">
                  <span>{textValue(row, "form_type") || "공시"}</span>
                  <strong>{textValue(row, "report_date") || "보고기간 미상"}</strong>
                  <small>공시 {textValue(row, "filing_date", "available_at") || "-"} · {textValue(row, "accession_no") || "accession 미상"}</small>
                </a>
              )) : <div className="mm-decision__evidence-empty">{dbFilingStatus === "ERROR" ? (dbFilingMessage || "저장 공시 ledger를 조회하지 못했습니다.") : "기준일 이전에 저장된 10-K / 10-Q 공시가 없습니다."}</div>}
            </div>
            <div className="mm-decision__evidence-grid">
              <div className="mm-decision__evidence-section">
                <div className="mm-decision__evidence-title"><strong>뉴스 근거</strong><small>세션 전용 · 최대 10건</small></div>
                {newsEvidence.length ? newsEvidence.map((row, index) => (
                  <a className="mm-decision__evidence-card" href={textValue(row, "URL", "url")} key={`${textValue(row, "Title", "title")}-${index}`} rel="noreferrer" target="_blank">
                    <span>{textValue(row, "Source", "source") || "뉴스"}</span>
                    <strong>{textValue(row, "Title", "title") || "제목 없음"}</strong>
                    <small>{textValue(row, "Published At", "published_at") || "게시 시각 미상"}</small>
                  </a>
                )) : <div className="mm-decision__evidence-empty">‘뉴스 근거 조회’를 누르면 선택 종목의 근거 링크를 이 세션에만 표시합니다.</div>}
              </div>
              <div className="mm-decision__evidence-section">
                <div className="mm-decision__evidence-title"><strong>SEC 최신 메타데이터</strong><small>세션 전용 · 최대 5건</small></div>
                {secEvidence.length ? secEvidence.map((row, index) => (
                  <a className="mm-decision__evidence-card" href={textValue(row, "URL", "url")} key={`${textValue(row, "Form", "form_type")}-${index}`} rel="noreferrer" target="_blank">
                    <span>{textValue(row, "Form", "form_type") || "SEC"}</span>
                    <strong>{textValue(row, "Title", "title") || "SEC filing"}</strong>
                    <small>{textValue(row, "Filing Date", "filing_date") || "공시일 미상"}</small>
                  </a>
                )) : <div className="mm-decision__evidence-empty">‘SEC 최신 조회’를 누르면 최신 filing 메타데이터를 추가합니다.</div>}
              </div>
            </div>
          </div>
        ) : <div className="mm-decision__research-loading">선택 종목의 저장 근거를 불러오는 중입니다.</div>}
      </div>
    </section>
  );
}

type DecisionWorkbenchProps = {
  payload: MarketMoversDecisionWorkbenchPayload;
  onEvent: (event: Record<string, unknown>) => void;
};

function MarketMoversDecisionWorkbench({ payload, onEvent }: DecisionWorkbenchProps) {
  const [activeSymbol, setActiveSymbol] = useState(payload.selection.symbol);
  const [detailOpen, setDetailOpen] = useState(false);
  const rowsBySymbol = useMemo(
    () => new Map(payload.ranking.rows.map((row) => [textValue(row, "Symbol", "symbol"), row])),
    [payload.ranking.rows],
  );
  const activeRow = rowsBySymbol.get(activeSymbol) || payload.selection.row;
  const emitControl = (control: MarketMoverFilterControl, value: string) => {
    onEvent({ id: "set_control", control: control.id, value });
  };
  const selectRow = (row: DecisionRow) => {
    const symbol = textValue(row, "Symbol", "symbol");
    setActiveSymbol(symbol);
    onEvent({ id: "select_symbol", symbol });
  };
  const requestBreadth = (groupBy: "sector" | "industry", period: "daily" | "weekly" | "monthly") => {
    onEvent({ id: "request_breadth", group_by: groupBy, period });
  };
  return (
    <main className="mm-decision" data-schema-version={payload.schema_version}>
      <MarketMoversCommandLine payload={payload} onControl={emitControl} />
      <MarketMoversTimingAndActions onEvent={onEvent} payload={payload} />
      <MarketPulse payload={payload} />
      <div className="mm-decision__workbench">
        <RankingBoard activeSymbol={activeSymbol} onSelect={selectRow} payload={payload} />
        <BreadthContext onRequest={requestBreadth} payload={payload} />
      </div>
      {activeRow ? <QuickResearch onOpen={() => { setDetailOpen(true); syncFrameHeightSoon(); }} row={activeRow} /> : null}
      {detailOpen ? <StockResearchTabs activeSymbol={activeSymbol} onEvent={onEvent} payload={payload} /> : null}
      <footer className="mm-decision__boundary">현재 흐름과 저장 근거를 연결한 조사 화면이며, 매매 추천이나 미래 수익률 예측이 아닙니다.</footer>
    </main>
  );
}

function MarketMoversWorkbench({ args }: Props) {
  const payload = args.payload;

  useEffect(() => {
    let lastHeight = 0;
    const syncObservedHeight = () => {
      const nextHeight = Math.ceil(document.body.scrollHeight);
      if (nextHeight > 0 && nextHeight !== lastHeight) {
        lastHeight = nextHeight;
        Streamlit.setFrameHeight(nextHeight);
      }
    };
    const observer = new ResizeObserver(syncObservedHeight);
    observer.observe(document.documentElement);
    observer.observe(document.body);
    syncObservedHeight();
    return () => observer.disconnect();
  }, [payload]);

  if (!payload) {
    return null;
  }

  const emitAction = (action: MarketMoverAction) => {
    if (action.kind === "disabled") {
      return;
    }
    Streamlit.setComponentValue({ event: { id: action.id, nonce: Date.now() } });
  };

  const emitRefreshMode = (value: string) => {
    Streamlit.setComponentValue({ event: { id: "set_refresh_mode", value, nonce: Date.now() } });
  };

  const emitControl = (control: MarketMoverFilterControl, value: string) => {
    Streamlit.setComponentValue({
      event: { id: "set_control", control: control.id, value, nonce: Date.now() },
    });
  };

  const emitDecisionEvent = (event: Record<string, unknown>) => {
    Streamlit.setComponentValue({ event: { ...event, nonce: Date.now() } });
  };

  if (payload.component === "MarketMoverInvestigationPane") {
    return <MarketMoverInvestigationPane payload={payload} onAction={emitAction} />;
  }

  if (payload.component === "MarketMoversSectorBreadth") {
    return <MarketMoversSectorBreadth payload={payload} />;
  }

  if (payload.component === "MarketMoversDecisionWorkbench") {
    return <MarketMoversDecisionWorkbench payload={payload} onEvent={emitDecisionEvent} />;
  }

  const trustHasIssues = Boolean(payload.trust_panel.has_issues);

  return (
    <section
      className="mm-workbench"
      data-control-mode={payload.control_ownership.mode}
      data-schema-version={payload.schema_version}
    >
      <div className="mm-workbench__head">
        <div>
          <div className="mm-workbench__kicker">Market Movers</div>
          <div className="mm-workbench__title">{payload.summary.title}</div>
          <div className="mm-workbench__context">{payload.summary.context}</div>
        </div>
        <div className="mm-workbench__trust">
          <span>자료 상태</span>
          <strong>{payload.summary.trust_state}</strong>
          {payload.summary.trust_detail ? <small>{payload.summary.trust_detail}</small> : null}
        </div>
      </div>
      {payload.filter_controls.visible ? (
        <div className="mm-workbench__filters" aria-label="Market Movers filters">
          {payload.filter_controls.items.map((control) => (
            <label className="mm-workbench__filter" key={control.id}>
              <span>{control.label}</span>
              <select
                className="mm-workbench__filter-select"
                disabled={control.disabled}
                onChange={(event) => emitControl(control, event.target.value)}
                value={control.value}
              >
                {control.options.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          ))}
        </div>
      ) : null}
      <div className="mm-workbench__grid" aria-label="Market Movers summary">
        {payload.summary.items.map((item) => (
          <div className="mm-workbench__metric" key={`${item.label}-${item.value}`}>
            <div className="mm-workbench__metric-label">{item.label}</div>
            <div className="mm-workbench__metric-value">{item.value}</div>
            {item.detail ? <div className="mm-workbench__metric-detail">{item.detail}</div> : null}
          </div>
        ))}
      </div>
      {payload.trust_panel.visible ? (
        <details
          className={`mm-workbench__trust-panel mm-workbench__trust-panel--${payload.trust_panel.tone}${
            trustHasIssues ? " mm-workbench__trust-panel--has-issues" : ""
          }`}
          data-has-issues={trustHasIssues}
          onToggle={syncFrameHeightSoon}
          open={payload.trust_panel.default_open}
        >
          <summary className="mm-workbench__trust-summary">
            <span>
              <span className="mm-workbench__trust-kicker">{payload.trust_panel.kicker}</span>
              <strong className="mm-workbench__trust-title">
                {trustHasIssues ? <span aria-label="자료 품질 확인 필요" className="mm-workbench__trust-issue-dot" /> : null}
                {payload.trust_panel.title}
              </strong>
            </span>
            <span className="mm-workbench__trust-state">{payload.trust_panel.state}</span>
          </summary>
          <div className="mm-workbench__trust-body">
            <div className="mm-workbench__trust-copy">
              <strong>{payload.trust_panel.headline}</strong>
              {payload.trust_panel.detail ? <span>{payload.trust_panel.detail}</span> : null}
            </div>
            <div className="mm-workbench__trust-items">
              {payload.trust_panel.items.map((item) => (
                <div className="mm-workbench__trust-item" key={`${item.label}-${item.value}`}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                  {item.detail ? <small>{item.detail}</small> : null}
                </div>
              ))}
            </div>
            {payload.trust_panel.warnings.length > 0 ? (
              <div className="mm-workbench__trust-warnings" aria-label="커버리지 신뢰 경고">
                {payload.trust_panel.warnings.map((warning) => (
                  <div className="mm-workbench__trust-warning" key={warning}>
                    {warning}
                  </div>
                ))}
              </div>
            ) : null}
            <div className="mm-workbench__trust-table" aria-label="그룹 누락 진단">
              <div className="mm-workbench__trust-table-title">그룹 누락 진단</div>
              {payload.trust_panel.grouped_rows.length > 0 ? (
                <div className="mm-workbench__trust-rows">
                  {payload.trust_panel.grouped_rows.map((row, index) => (
                    <div className="mm-workbench__trust-row" key={`trust-row-${index}`}>
                      {payload.trust_panel.group_columns.map((column) => (
                        <div className="mm-workbench__trust-cell" key={column}>
                          <span>{column}</span>
                          <strong>{String(row[column] ?? "-")}</strong>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="mm-workbench__trust-empty">{payload.trust_panel.empty_text}</div>
              )}
            </div>
            <div className="mm-workbench__trust-action">
              <strong>{payload.trust_panel.suggested_action.label}</strong>
              <span>{payload.trust_panel.suggested_action.detail}</span>
            </div>
            {payload.trust_panel.boundary_note ? (
              <div className="mm-workbench__trust-boundary">{payload.trust_panel.boundary_note}</div>
            ) : null}
          </div>
        </details>
      ) : null}
      <div className="mm-workbench__action-row">
        {payload.refresh_mode.visible ? (
          <label className="mm-workbench__mode">
            <span>{payload.refresh_mode.label}</span>
            <select
              className="mm-workbench__mode-select"
              disabled={payload.refresh_mode.disabled}
              onChange={(event) => emitRefreshMode(event.target.value)}
              value={payload.refresh_mode.value}
            >
              {payload.refresh_mode.options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        ) : (
          <div />
        )}
        <div className="mm-workbench__action-stack">
          <div className="mm-workbench__actions" aria-label="Market Movers actions">
            {payload.actions.map((action) => (
              <button
                className={`mm-workbench__action mm-workbench__action--${action.kind}`}
                disabled={action.kind === "disabled"}
                key={action.id}
                onClick={() => emitAction(action)}
                type="button"
              >
                <span className="mm-workbench__action-label">{action.label}</span>
              </button>
            ))}
          </div>
          {payload.action_note ? <div className="mm-workbench__action-note">{payload.action_note}</div> : null}
        </div>
      </div>
    </section>
  );
}

export default withStreamlitConnection(MarketMoversWorkbench);
