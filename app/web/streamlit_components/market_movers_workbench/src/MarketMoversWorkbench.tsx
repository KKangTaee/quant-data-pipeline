import React, { useEffect } from "react";
import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import "./style.css";

export type MarketMoverAction = {
  id: string;
  label: string;
  kind: "primary" | "secondary" | "disabled";
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
  refresh_mode: {
    visible: boolean;
    label: string;
    value: string;
    options: Array<{ value: string; label: string }>;
    disabled: boolean;
  };
  control_ownership: {
    mode: "streamlit_owned";
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
      <div className="mm-workbench__grid" aria-label="Market Movers summary">
        {payload.summary.items.map((item) => (
          <div className="mm-workbench__metric" key={`${item.label}-${item.value}`}>
            <div className="mm-workbench__metric-label">{item.label}</div>
            <div className="mm-workbench__metric-value">{item.value}</div>
            {item.detail ? <div className="mm-workbench__metric-detail">{item.detail}</div> : null}
          </div>
        ))}
      </div>
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
