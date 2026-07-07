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
    source_count: number;
    stale_count: number;
    missing_count: number;
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
      <div className="sentiment-workbench__hero">
        <div className="sentiment-workbench__hero-copy">
          <div className="sentiment-workbench__phase-row">
            <span className="sentiment-workbench__phase-pill">{payload.summary.phase_label}</span>
            <span className="sentiment-workbench__kicker">Sentiment</span>
          </div>
          <h2 className="sentiment-workbench__headline">{payload.summary.headline}</h2>
          {payload.summary.summary ? (
            <p className="sentiment-workbench__summary-copy">{payload.summary.summary}</p>
          ) : null}
          <div className="sentiment-workbench__fallback-note">{payload.boundary_note}</div>
        </div>

        <aside
          className="sentiment-workbench__freshness-panel"
          style={{ "--sentiment-tone": toneColor(payload.freshness.tone) } as React.CSSProperties}
        >
          <div className="sentiment-workbench__freshness-label">자료 기준</div>
          <strong className="sentiment-workbench__freshness-date">{payload.freshness.latest_observation_date}</strong>
          <div className="sentiment-workbench__freshness-detail">{payload.freshness.detail}</div>
          <div className="sentiment-workbench__freshness-counts">
            <span>source {payload.freshness.source_count}</span>
            <span>missing {payload.freshness.missing_count}</span>
            <span>stale {payload.freshness.stale_count}</span>
          </div>

          <div className="sentiment-workbench__command">
            <div>
              <div className="sentiment-workbench__command-title">{payload.command.title}</div>
              <div className="sentiment-workbench__command-detail">{payload.command.detail}</div>
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
            </div>
            {pendingActionLabel ? (
              <div className="sentiment-workbench__action-feedback" aria-live="polite">
                요청 전송 · {pendingActionLabel}
              </div>
            ) : null}
          </div>
        </aside>
      </div>

      <div className="sentiment-workbench__metric-grid">
        {payload.summary.metrics.map((metric) => (
          <div
            className="sentiment-workbench__metric-card"
            key={`${metric.label}-${metric.value}`}
            style={{ "--metric-tone": toneColor(metric.tone) } as React.CSSProperties}
          >
            <div className="sentiment-workbench__metric-label">{metric.label}</div>
            <div className="sentiment-workbench__metric-value">{metric.value}</div>
            {metric.detail ? <div className="sentiment-workbench__metric-detail">{metric.detail}</div> : null}
          </div>
        ))}
        {payload.summary.metrics.length === 0 ? (
          <div className="sentiment-workbench__metric-card sentiment-workbench__metric-card--empty">
            <div className="sentiment-workbench__metric-label">Data</div>
            <div className="sentiment-workbench__metric-value">-</div>
            <div className="sentiment-workbench__metric-detail">저장된 sentiment metric이 없습니다.</div>
          </div>
        ) : null}
      </div>
    </section>
  );
}

export default withStreamlitConnection(SentimentWorkbench);
