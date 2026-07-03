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

  return (
    <section className="mm-workbench" data-schema-version={payload.schema_version}>
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
      <div className="mm-workbench__actions" aria-label="Market Movers actions">
        {payload.actions.map((action) => (
          <button
            className={`mm-workbench__action mm-workbench__action--${action.kind}`}
            disabled={action.kind === "disabled"}
            key={action.id}
            type="button"
          >
            {action.label}
          </button>
        ))}
      </div>
    </section>
  );
}

export default withStreamlitConnection(MarketMoversWorkbench);
