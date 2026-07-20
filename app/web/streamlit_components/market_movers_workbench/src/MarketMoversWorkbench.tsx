import React, { useEffect, useMemo, useState } from "react";
import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
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

type Props = ComponentProps & {
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
      <div className="mm-decision__hero">
        <div>
          <div className="mm-decision__eyebrow">MARKET MOVERS</div>
          <h2>움직임을 찾고, 확산을 확인하고, 종목을 조사합니다</h2>
          <p>랭킹과 시장 맥락을 같은 선택 상태로 연결한 결정형 워크벤치입니다.</p>
        </div>
        <div className={`mm-decision__trust mm-decision__trust--${trustState.toLowerCase()}`}>
          <span>자료 상태</span>
          <strong>{trustState}</strong>
          <small>랭킹 가능 {denominator}</small>
        </div>
      </div>
      <div className="mm-decision__controls" aria-label="변동 종목 탐색 조건">
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
                style={{ "--mm-row-tone": returnPct !== null && returnPct < 0 ? "#dc2626" : "#0f766e" } as React.CSSProperties}
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
                <span className="mm-decision__rank-metric">
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
};

function BreadthContext({ payload }: BreadthContextProps) {
  const [groupMode, setGroupMode] = useState<(typeof GROUP_MODES)[number]>("sector");
  const initialPeriod = GROUP_PERIODS.includes(payload.ranking.period as (typeof GROUP_PERIODS)[number])
    ? payload.ranking.period as (typeof GROUP_PERIODS)[number]
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
  };
  const switchPeriod = (period: (typeof GROUP_PERIODS)[number]) => {
    setGroupPeriod(period);
    setSelectedGroup("");
  };
  return (
    <aside className="mm-decision__breadth">
      <div className="mm-decision__section-head">
        <div>
          <span>BREADTH CONTEXT</span>
          <h3>시장 확산 맥락</h3>
        </div>
      </div>
      <div className="mm-decision__segmented" aria-label="그룹 기준">
        {["sector", "industry"].map((mode) => (
          <button className={groupMode === mode ? "is-active" : ""} key={mode} onClick={() => switchMode(mode as (typeof GROUP_MODES)[number])} type="button">
            {mode === "sector" ? "섹터" : "산업"}
          </button>
        ))}
      </div>
      <div className="mm-decision__periods" aria-label="확산 기간">
        {["daily", "weekly", "monthly"].map((period) => (
          <button className={groupPeriod === period ? "is-active" : ""} key={period} onClick={() => switchPeriod(period as (typeof GROUP_PERIODS)[number])} type="button">
            {{ daily: "일", weekly: "주", monthly: "월" }[period]}
          </button>
        ))}
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
                  <span><strong>{formatSignedPercent(relative)}</strong><small>시장 대비</small></span>
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
              <span><small>동일가중</small><strong>{formatSignedPercent(numberValue(activeGroup, "equal_weight_return_pct"))}</strong></span>
              <span><small>시총가중</small><strong>{formatSignedPercent(numberValue(activeGroup, "market_cap_weighted_return_pct"))}</strong></span>
            </div>
          </div>
          <div className="mm-decision__bellwethers">
            <div className="mm-decision__mini-head"><strong>시총 Top 3</strong><small>수익률 리더와 별도</small></div>
            {bellwethers.length ? bellwethers.slice(0, 3).map((row) => (
              <div key={`${activeGroupName}-${textValue(row, "Symbol")}`}>
                <span><strong>#{textValue(row, "Rank")}</strong><b>{textValue(row, "Symbol")}</b><small>{textValue(row, "Name")}</small></span>
                <span><strong>{formatSignedPercent(row["Return %"])}</strong><small>시총 {formatCompact(row["Market Cap"])}</small></span>
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
        <span><small>선택 기간 수익률</small><strong>{formatSignedPercent(row["Return %"])}</strong></span>
        <span><small>상대 거래량</small><strong>{numberValue(row, "Relative Volume") !== null ? `${numberValue(row, "Relative Volume")?.toFixed(2)}x` : "-"}</strong></span>
        <span><small>시가총액</small><strong>{formatCompact(row["Market Cap"])}</strong></span>
      </div>
      <button onClick={onOpen} type="button">상세 조사 열기</button>
    </section>
  );
}

type StockResearchTabsProps = {
  payload: MarketMoversDecisionWorkbenchPayload;
  activeSymbol: string;
};

function StockResearchTabs({ payload, activeSymbol }: StockResearchTabsProps) {
  const [tab, setTab] = useState<"price" | "financial" | "events">("price");
  const research = payload.selection.symbol === activeSymbol ? payload.selection.research : null;
  return (
    <section className="mm-decision__research">
      <div className="mm-decision__research-head">
        <div><span>DEEP RESEARCH</span><h3>{activeSymbol} 상세 조사</h3></div>
        <div className="mm-decision__tabs" role="tablist">
          {([
            ["price", "가격·모멘텀"],
            ["financial", "재무"],
            ["events", "뉴스·공시"],
          ] as const).map(([id, label]) => (
            <button className={tab === id ? "is-active" : ""} key={id} onClick={() => setTab(id)} role="tab" type="button">{label}</button>
          ))}
        </div>
      </div>
      {!research ? (
        <div className="mm-decision__research-loading">선택 종목의 저장 근거를 불러오는 중입니다.</div>
      ) : tab === "price" ? (
        <div className="mm-decision__research-placeholder">저장된 가격 이력과 모멘텀 차트를 표시합니다.</div>
      ) : tab === "financial" ? (
        <div className="mm-decision__research-placeholder">보고 주기와 재무 factor를 분리해 표시합니다.</div>
      ) : (
        <div className="mm-decision__research-placeholder">저장된 뉴스·공시 근거와 필요한 수집 action을 표시합니다.</div>
      )}
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
  return (
    <main className="mm-decision" data-schema-version={payload.schema_version}>
      <MarketMoversCommandLine payload={payload} onControl={emitControl} />
      <div className="mm-decision__workbench">
        <RankingBoard activeSymbol={activeSymbol} onSelect={selectRow} payload={payload} />
        <BreadthContext payload={payload} />
      </div>
      {activeRow ? <QuickResearch onOpen={() => { setDetailOpen(true); syncFrameHeightSoon(); }} row={activeRow} /> : null}
      {detailOpen ? <StockResearchTabs activeSymbol={activeSymbol} payload={payload} /> : null}
      <footer className="mm-decision__boundary">현재 흐름과 저장 근거를 연결한 조사 화면이며, 매매 추천이나 미래 수익률 예측이 아닙니다.</footer>
    </main>
  );
}

function MarketMoversWorkbench({ args }: Props) {
  const payload = args.payload;

  useEffect(() => {
    syncFrameHeightSoon();
  });

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
