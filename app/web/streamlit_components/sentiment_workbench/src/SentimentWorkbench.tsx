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

type SentimentAnalysisStep = {
  title: string;
  status?: string;
  detail?: string;
  tone?: string;
};

type SentimentDriverItem = {
  series: string;
  label_ko: string;
  score?: string;
  rating?: string;
  tone?: string;
  direction?: string;
  current_reading?: string;
};

type SentimentDriverLane = {
  key: string;
  label: string;
  tone?: string;
  count: number;
  items: SentimentDriverItem[];
};

type SentimentComponentExplanation = {
  series: string;
  label_ko: string;
  score?: number | string;
  rating_label_ko?: string;
  tone?: string;
  direction?: string;
  what_it_checks?: string;
  current_reading?: string;
};

type SentimentNextCheck = {
  target: string;
  reason?: string;
  watch_for?: string;
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
  analysis_steps: SentimentAnalysisStep[];
  drivers: {
    lanes: SentimentDriverLane[];
  };
  component_explanations: SentimentComponentExplanation[];
  next_checks: SentimentNextCheck[];
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

function displayValue(value: number | string | undefined) {
  if (value === undefined || value === null || value === "") {
    return "-";
  }
  if (typeof value === "number") {
    return Number.isFinite(value) ? value.toFixed(1) : "-";
  }
  return value;
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
  const metricByLabel = (label: string) => payload.summary.metrics.find((metric) => metric.label === label);
  const cnnMetric = metricByLabel("CNN Fear & Greed");
  const aaiiBearishMetric = metricByLabel("AAII Bearish");
  const bullBearSpreadMetric = metricByLabel("Bull-Bear Spread");

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

      <section className="sentiment-workbench__cross-read">
        <div className="sentiment-workbench__section-heading">
          <span>CNN / AAII 같이 보기</span>
          <small>service analysis</small>
        </div>
        <div className="sentiment-workbench__cross-metrics">
          {[cnnMetric, aaiiBearishMetric, bullBearSpreadMetric].filter(Boolean).map((metric) => (
            <div
              className="sentiment-workbench__cross-metric"
              key={metric!.label}
              style={{ "--metric-tone": toneColor(metric!.tone) } as React.CSSProperties}
            >
              <span>{metric!.label}</span>
              <strong>{metric!.value}</strong>
              {metric!.detail ? <small>{metric!.detail}</small> : null}
            </div>
          ))}
        </div>
        <div className="sentiment-workbench__analysis-steps">
          {payload.analysis_steps.map((step) => (
            <article
              className="sentiment-workbench__analysis-step"
              key={`${step.title}-${step.status || ""}`}
              style={{ "--metric-tone": toneColor(step.tone) } as React.CSSProperties}
            >
              <div className="sentiment-workbench__analysis-title">{step.title}</div>
              {step.status ? <div className="sentiment-workbench__analysis-status">{step.status}</div> : null}
              {step.detail ? <p>{step.detail}</p> : null}
            </article>
          ))}
        </div>
      </section>

      <section className="sentiment-workbench__driver-section">
        <div className="sentiment-workbench__section-heading">
          <span>무엇이 이 심리를 만들었나</span>
          <small>CNN 구성요소 grouping</small>
        </div>
        <div className="sentiment-workbench__driver-lanes">
          {payload.drivers.lanes.map((lane) => (
            <div
              className="sentiment-workbench__driver-lane"
              key={lane.key}
              style={{ "--metric-tone": toneColor(lane.tone) } as React.CSSProperties}
            >
              <div className="sentiment-workbench__driver-lane-header">
                <span>{lane.label}</span>
                <strong>{lane.count}</strong>
              </div>
              <div className="sentiment-workbench__driver-cards">
                {lane.items.map((item) => (
                  <article className="sentiment-workbench__driver-card" key={`${lane.key}-${item.series}`}>
                    <div className="sentiment-workbench__driver-card-top">
                      <span>{item.label_ko || item.series}</span>
                      <strong>{displayValue(item.score)}</strong>
                    </div>
                    {item.rating ? <div className="sentiment-workbench__driver-rating">{item.rating}</div> : null}
                    {item.current_reading ? <p>{item.current_reading}</p> : null}
                  </article>
                ))}
                {lane.items.length === 0 ? (
                  <div className="sentiment-workbench__driver-empty">해당 방향의 구성요소가 없습니다.</div>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="sentiment-workbench__component-section">
        <div className="sentiment-workbench__section-heading">
          <span>CNN 구성요소 상세</span>
          <small>component explanations</small>
        </div>
        <div className="sentiment-workbench__component-list">
          {payload.component_explanations.map((component) => (
            <article
              className="sentiment-workbench__component-item"
              key={component.series}
              style={{ "--metric-tone": toneColor(component.tone) } as React.CSSProperties}
            >
              <div className="sentiment-workbench__component-score">{displayValue(component.score)}</div>
              <div className="sentiment-workbench__component-copy">
                <div className="sentiment-workbench__component-title">
                  <span>{component.label_ko || component.series}</span>
                  {component.rating_label_ko ? <strong>{component.rating_label_ko}</strong> : null}
                </div>
                {component.what_it_checks ? <p>{component.what_it_checks}</p> : null}
                {component.current_reading ? <small>{component.current_reading}</small> : null}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="sentiment-workbench__next-checks">
        <div className="sentiment-workbench__section-heading">
          <span>다음에 확인할 것</span>
          <small>next checks</small>
        </div>
        <div className="sentiment-workbench__next-check-list">
          {payload.next_checks.map((check) => (
            <article
              className="sentiment-workbench__next-check"
              key={`${check.target}-${check.reason || ""}`}
              style={{ "--metric-tone": toneColor(check.tone) } as React.CSSProperties}
            >
              <div className="sentiment-workbench__next-check-target">{check.target}</div>
              {check.reason ? <p>{check.reason}</p> : null}
              {check.watch_for ? <small>{check.watch_for}</small> : null}
            </article>
          ))}
        </div>
      </section>
    </section>
  );
}

export default withStreamlitConnection(SentimentWorkbench);
