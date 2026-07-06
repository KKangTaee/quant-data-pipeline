import React, { useEffect, useState } from "react";
import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import "./style.css";

export type FuturesMacroAction = {
  id: "daily_refresh" | "reload" | "load_validation";
  label: string;
  kind: "primary" | "secondary";
  detail?: string;
};

export type FuturesMacroMetric = {
  label: string;
  value: string;
  detail?: string;
  tone?: string;
};

export type FuturesMacroScore = {
  label: string;
  value: string;
  direction: string;
  coverage: string;
  tone: string;
  polarity?: string;
  description?: string;
};

export type FuturesMacroFlowCard = {
  label: string;
  value: string;
  detail: string;
  meaning?: string;
  tone: string;
};

export type FuturesMacroFlowPeriod = {
  key: string;
  label: string;
  title: string;
  basis: string;
  summary: string;
  cards: FuturesMacroFlowCard[];
};

export type FuturesMacroEvidenceItem = {
  title: string;
  score_label?: string;
  symbol?: string;
  contribution_z?: string;
  impact_label?: string;
  meaning: string;
};

export type FuturesMacroEvidenceSection = {
  key: string;
  label: string;
  description: string;
  count: number;
  empty_label: string;
  items: FuturesMacroEvidenceItem[];
};

export type FuturesMacroWorkbenchPayload = {
  schema_version: "futures_macro_react_workbench_v1";
  component: "FuturesMacroWorkbench";
  command: {
    title: string;
    detail: string;
    validation_state: {
      state: string;
      detail: string;
      tone: string;
      loaded_at: string;
    };
    actions: FuturesMacroAction[];
  };
  brief: {
    kicker: string;
    title: string;
    sub_scenario: string;
    regime_hint: string;
    summary: string;
    reason: string;
    confidence_label: string;
    confidence_detail: string;
    evidence: string[];
    metrics: FuturesMacroMetric[];
  };
  scores: FuturesMacroScore[];
  flow: {
    title: string;
    basis: string;
    summary: string;
    cards: FuturesMacroFlowCard[];
    default_period?: string;
    periods?: FuturesMacroFlowPeriod[];
  };
  validation: {
    title: string;
    state: string;
    detail: string;
    metrics: FuturesMacroMetric[];
  };
  evidence: {
    title: string;
    default_open: boolean;
    sections: FuturesMacroEvidenceSection[];
  };
  action_boundary: "python_dispatch_only";
  boundary_note: string;
};

type Props = ComponentProps & {
  args: {
    payload?: FuturesMacroWorkbenchPayload;
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
  if (normalized === "primary") {
    return "#2563eb";
  }
  return "#64748b";
}

function syncFrameHeightSoon() {
  Streamlit.setFrameHeight();
  window.requestAnimationFrame(() => Streamlit.setFrameHeight());
  window.setTimeout(() => Streamlit.setFrameHeight(), 160);
}

function FuturesMacroWorkbench({ args }: Props) {
  const payload = args.payload;
  const [pendingActionLabel, setPendingActionLabel] = useState("");
  const [selectedFlowKey, setSelectedFlowKey] = useState("");

  useEffect(() => {
    syncFrameHeightSoon();
  });

  if (!payload) {
    return null;
  }

  const isWorkbenchPayload = payload.component === "FuturesMacroWorkbench";
  if (!isWorkbenchPayload) {
    return null;
  }

  const emitAction = (action: FuturesMacroAction) => {
    setPendingActionLabel(action.label);
    Streamlit.setComponentValue({ event: { id: action.id, nonce: Date.now() } });
  };

  const fallbackFlowPeriod: FuturesMacroFlowPeriod = {
    key: "1W",
    label: "1W",
    title: payload.flow.title,
    basis: payload.flow.basis,
    summary: payload.flow.summary,
    cards: payload.flow.cards,
  };
  const flowPeriods = payload.flow.periods && payload.flow.periods.length > 0 ? payload.flow.periods : [fallbackFlowPeriod];
  const initialFlowKey = payload.flow.default_period || flowPeriods[0]?.key || "1W";
  const effectiveFlowKey = flowPeriods.some((period) => period.key === selectedFlowKey) ? selectedFlowKey : initialFlowKey;
  const selectedFlow = flowPeriods.find((period) => period.key === effectiveFlowKey) || flowPeriods[0] || fallbackFlowPeriod;

  return (
    <section
      className="fm-workbench"
      data-action-boundary={payload.action_boundary}
      data-schema-version={payload.schema_version}
    >
      <div className="fm-workbench__command">
        <div className="fm-workbench__command-copy">
          <div className="fm-workbench__kicker">Futures Macro</div>
          <div className="fm-workbench__command-title">{payload.command.title}</div>
          <div className="fm-workbench__command-detail">{payload.command.detail}</div>
        </div>
        <div className="fm-workbench__validation-pill" style={{ "--fm-tone": toneColor(payload.command.validation_state.tone) } as React.CSSProperties}>
          <span>{payload.command.validation_state.state}</span>
          <strong>{payload.command.validation_state.detail}</strong>
        </div>
        <div className="fm-workbench__actions" aria-label="Futures Macro actions">
          {payload.command.actions.map((action) => (
            <button
              className={`fm-workbench__action fm-workbench__action--${action.kind}`}
              key={action.id}
              onClick={() => emitAction(action)}
              title={action.detail}
              type="button"
            >
              {action.label}
            </button>
          ))}
          {pendingActionLabel ? (
            <div className="fm-workbench__action-feedback" aria-live="polite">
              요청 전송 · {pendingActionLabel}
            </div>
          ) : null}
        </div>
      </div>

      <div className="fm-workbench__brief">
        <div className="fm-workbench__brief-copy">
          <div className="fm-workbench__kicker">{payload.brief.kicker}</div>
          <div className="fm-workbench__title">{payload.brief.title}</div>
          {payload.brief.sub_scenario ? (
            <div className="fm-workbench__subscenario">
              {payload.brief.sub_scenario}
              {payload.brief.regime_hint ? ` · ${payload.brief.regime_hint}` : ""}
            </div>
          ) : null}
          <p>{payload.brief.summary}</p>
          {payload.brief.reason ? <p className="fm-workbench__reason">{payload.brief.reason}</p> : null}
          {payload.brief.evidence.length > 0 ? (
            <div className="fm-workbench__evidence-line">
              {payload.brief.evidence.slice(0, 2).map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          ) : null}
        </div>
        <div className="fm-workbench__brief-side">
          <div className="fm-workbench__confidence">
            <span>근거 강도</span>
            <strong>{payload.brief.confidence_label}</strong>
            <small>{payload.brief.confidence_detail}</small>
          </div>
          {payload.brief.metrics.map((item) => (
            <div className="fm-workbench__metric" key={`${item.label}-${item.value}`} style={{ "--fm-tone": toneColor(item.tone) } as React.CSSProperties}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              {item.detail ? <small>{item.detail}</small> : null}
            </div>
          ))}
        </div>
      </div>

      <div className="fm-workbench__scores" aria-label="Futures Macro score chips">
        {payload.scores.map((score) => (
          <div className="fm-workbench__score" key={score.label} style={{ "--fm-tone": toneColor(score.tone) } as React.CSSProperties}>
            <span>{score.label}</span>
            <strong>{score.value}</strong>
            <small>{score.direction} · {score.coverage}</small>
            {score.polarity ? (
              <small className="fm-workbench__score-hint">
                {score.polarity.split(" · ").map((line) => (
                  <span className="fm-workbench__score-hint-line" key={line}>{line}</span>
                ))}
              </small>
            ) : null}
          </div>
        ))}
      </div>

      <div className="fm-workbench__flow">
        <div className="fm-workbench__section-head">
          <div>
            <div className="fm-workbench__section-title">{selectedFlow.title}</div>
            <div className="fm-workbench__section-detail">{selectedFlow.basis}</div>
            {flowPeriods.length > 1 ? (
              <div className="fm-workbench__flow-tabs" aria-label="Flow horizon">
                {flowPeriods.map((period) => (
                  <button
                    aria-pressed={period.key === effectiveFlowKey}
                    className={`fm-workbench__flow-tab${period.key === effectiveFlowKey ? " fm-workbench__flow-tab--active" : ""}`}
                    key={period.key}
                    onClick={() => {
                      setSelectedFlowKey(period.key);
                      syncFrameHeightSoon();
                    }}
                    type="button"
                  >
                    {period.label}
                  </button>
                ))}
              </div>
            ) : null}
          </div>
          <span>{selectedFlow.summary}</span>
        </div>
        <div className="fm-workbench__flow-grid">
          {selectedFlow.cards.map((card) => (
            <div className="fm-workbench__flow-card" key={`${selectedFlow.key}-${card.label}`} style={{ "--fm-tone": toneColor(card.tone) } as React.CSSProperties}>
              <span>{card.label}</span>
              <strong>{card.value}</strong>
              <small>{card.detail}</small>
            </div>
          ))}
        </div>
      </div>

      <div className="fm-workbench__validation">
        <div>
          <div className="fm-workbench__section-title">{payload.validation.title}</div>
          <div className="fm-workbench__section-detail">{payload.validation.detail}</div>
        </div>
        <div className="fm-workbench__validation-metrics">
          {payload.validation.metrics.map((item) => (
            <div className="fm-workbench__metric" key={`${item.label}-${item.value}`}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              {item.detail ? <small>{item.detail}</small> : null}
            </div>
          ))}
        </div>
      </div>

      <details className="fm-workbench__evidence" onToggle={syncFrameHeightSoon} open={payload.evidence.default_open}>
        <summary>
          <span>{payload.evidence.title}</span>
          <small>{payload.boundary_note}</small>
        </summary>
        <div className="fm-workbench__evidence-sections">
          {payload.evidence.sections.map((section) => (
            <div className="fm-workbench__evidence-section" key={section.key}>
              <div className="fm-workbench__evidence-section-head">
                <strong>{section.label}</strong>
                <span>{section.count}</span>
              </div>
              <p>{section.description}</p>
              {section.items.length > 0 ? (
                <div className="fm-workbench__evidence-items">
                  {section.items.map((item) => {
                    const evidenceMeta = [item.score_label, item.symbol, item.contribution_z].filter(Boolean).join(" · ");
                    return (
                      <div className="fm-workbench__evidence-item" key={item.title}>
                        <strong>{item.title}</strong>
                        {evidenceMeta ? <small className="fm-workbench__evidence-meta">{evidenceMeta}</small> : null}
                        {item.impact_label ? <span>{item.impact_label}</span> : null}
                        <p>{item.meaning}</p>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="fm-workbench__empty">{section.empty_label}</div>
              )}
            </div>
          ))}
        </div>
      </details>
    </section>
  );
}

export default withStreamlitConnection(FuturesMacroWorkbench);
