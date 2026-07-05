import React, { useEffect } from "react";
import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import "./style.css";

export type MarketMoverAction = {
  id: string;
  label: string;
  kind: "primary" | "secondary" | "disabled";
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
  control_ownership: {
    mode: "python_state_react_ui";
    migrated_controls: string[];
    deferred_controls: string[];
  };
  actions: MarketMoverAction[];
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

type MarketMoversPayload =
  | MarketMoversWorkbenchPayload
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
              {action.label}
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
          <div className="mm-sector-breadth__kicker">시장 확산 지도</div>
          <div className="mm-sector-breadth__title">{payload.map.headline}</div>
          <div className="mm-sector-breadth__detail-copy">
            {payload.map.detail} · 기준: {payload.map.freshness}
          </div>
        </div>
        <span className="mm-sector-breadth__status">{payload.map.status}</span>
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

  if (payload.component === "MarketMoverInvestigationPane") {
    return <MarketMoverInvestigationPane payload={payload} onAction={emitAction} />;
  }

  if (payload.component === "MarketMoversSectorBreadth") {
    return <MarketMoversSectorBreadth payload={payload} />;
  }

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
          className={`mm-workbench__trust-panel mm-workbench__trust-panel--${payload.trust_panel.tone}`}
          onToggle={syncFrameHeightSoon}
          open={payload.trust_panel.default_open}
        >
          <summary className="mm-workbench__trust-summary">
            <span>
              <span className="mm-workbench__trust-kicker">{payload.trust_panel.kicker}</span>
              <strong>{payload.trust_panel.title}</strong>
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
        <div className="mm-workbench__actions" aria-label="Market Movers actions">
          {payload.actions.map((action) => (
            <button
              className={`mm-workbench__action mm-workbench__action--${action.kind}`}
              disabled={action.kind === "disabled"}
              key={action.id}
              onClick={() => emitAction(action)}
              type="button"
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

export default withStreamlitConnection(MarketMoversWorkbench);
