import React, { useEffect, useState } from "react";
import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import "./style.css";

type SentimentAction = {
  id: "refresh" | "reload";
  label: string;
  kind: "primary" | "secondary";
  detail?: string;
};

type SentimentMetric = {
  label: string;
  value: string;
  detail?: string;
  tone?: string;
};

type SentimentWorkbenchPayload = {
  schema_version: "sentiment_react_workbench_v1";
  component: "SentimentWorkbench";
  command: {
    title: string;
    detail: string;
    actions: SentimentAction[];
  };
  summary: {
    phase_label: string;
    headline: string;
    summary: string;
    tone: string;
    metrics: SentimentMetric[];
  };
  freshness: {
    latest_observation_date: string;
    detail: string;
    tone: string;
  };
  boundary_note: string;
  action_boundary: "python_dispatch_only";
};

type Props = ComponentProps & {
  args: {
    payload?: SentimentWorkbenchPayload;
  };
};

function toneColor(tone: string | undefined) {
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

function syncFrameHeightSoon() {
  Streamlit.setFrameHeight();
  window.requestAnimationFrame(() => Streamlit.setFrameHeight());
  window.setTimeout(() => Streamlit.setFrameHeight(), 160);
}

function SentimentWorkbench({ args }: Props) {
  const payload = args.payload;
  const [pendingActionLabel, setPendingActionLabel] = useState("");

  useEffect(() => {
    syncFrameHeightSoon();
  });

  if (!payload) {
    return null;
  }

  const isWorkbenchPayload = payload.component === "SentimentWorkbench";
  if (!isWorkbenchPayload) {
    return null;
  }

  const emitAction = (action: SentimentAction) => {
    setPendingActionLabel(action.label);
    Streamlit.setComponentValue({ event: { id: action.id, nonce: Date.now() } });
  };

  return (
    <section
      className="sentiment-workbench"
      data-action-boundary={payload.action_boundary}
      data-schema-version={payload.schema_version}
      style={{ "--sentiment-tone": toneColor(payload.summary.tone) } as React.CSSProperties}
    >
      <div className="sentiment-workbench__command">
        <div>
          <div className="sentiment-workbench__kicker">Sentiment</div>
          <div className="sentiment-workbench__command-title">{payload.command.title}</div>
          <div className="sentiment-workbench__command-detail">{payload.command.detail}</div>
        </div>
        <div className="sentiment-workbench__freshness" style={{ "--sentiment-tone": toneColor(payload.freshness.tone) } as React.CSSProperties}>
          <span>자료 기준</span>
          <strong>{payload.freshness.latest_observation_date}</strong>
          <small>{payload.freshness.detail}</small>
        </div>
        <div className="sentiment-workbench__actions" aria-label="Sentiment actions">
          {payload.command.actions.map((action) => (
            <button
              className={`sentiment-workbench__action sentiment-workbench__action--${action.kind}`}
              key={action.id}
              onClick={() => emitAction(action)}
              title={action.detail}
              type="button"
            >
              {action.label}
            </button>
          ))}
          {pendingActionLabel ? (
            <div className="sentiment-workbench__action-feedback" aria-live="polite">
              요청 전송 · {pendingActionLabel}
            </div>
          ) : null}
        </div>
      </div>

      <div className="sentiment-workbench__fallback-note">{payload.boundary_note}</div>
    </section>
  );
}

export default withStreamlitConnection(SentimentWorkbench);
