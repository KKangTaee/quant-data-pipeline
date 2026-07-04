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

type Props = ComponentProps & {
  args: {
    payload?: MarketMoversWorkbenchPayload;
  };
};

function MarketMoversWorkbench({ args }: Props) {
  const payload = args.payload;

  useEffect(() => {
    Streamlit.setFrameHeight();
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
