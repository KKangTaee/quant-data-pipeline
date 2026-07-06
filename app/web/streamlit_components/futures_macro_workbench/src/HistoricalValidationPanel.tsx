import type { FuturesMacroAction, FuturesMacroMetric, FuturesMacroWorkbenchPayload } from "./FuturesMacroWorkbench";

type HistoricalValidationPanelProps = {
  validation: FuturesMacroWorkbenchPayload["validation"];
  onAction: (action: FuturesMacroAction) => void;
};

function MetricTile({ item }: { item: FuturesMacroMetric }) {
  return (
    <div className="fm-workbench__metric" key={`${item.label}-${item.value}`}>
      <span>{item.label}</span>
      <strong>{item.value}</strong>
      {item.detail ? <small>{item.detail}</small> : null}
    </div>
  );
}

function HistoricalValidationPanel({ validation, onAction }: HistoricalValidationPanelProps) {
  const insightTiles = [
    validation.insight.current_state,
    validation.insight.sample,
    validation.insight.directionality,
    validation.insight.evidence_bridge,
  ];

  return (
    <section className="fm-workbench__validation-card" aria-label="과거 점검">
      <div className="fm-workbench__validation-header">
        <div>
          <div className="fm-workbench__validation-eyebrow">과거 점검</div>
          <div className="fm-workbench__section-title">{validation.insight.purpose || validation.title}</div>
          <div className="fm-workbench__section-detail">{validation.insight.basis || validation.detail}</div>
        </div>
        <div className="fm-workbench__validation-state">
          <span>{validation.state}</span>
          <strong>{validation.detail}</strong>
        </div>
      </div>

      <div className="fm-workbench__validation-summary">
        <p>{validation.insight.confidence_effect}</p>
      </div>

      <div className="fm-workbench__validation-status-grid">
        {validation.metrics.map((item) => (
          <MetricTile item={item} key={`${item.label}-${item.value}`} />
        ))}
      </div>

      <div className="fm-workbench__validation-control">
        <button
          className="fm-workbench__validation-action"
          onClick={() => onAction(validation.action)}
          title={validation.action.detail}
          type="button"
        >
          {validation.action.label}
        </button>
        {validation.action.detail ? <small>{validation.action.detail}</small> : null}
      </div>

      <div className="fm-workbench__validation-result-grid">
        {insightTiles.map((item) => (
          <MetricTile item={item} key={`${item.label}-${item.value}`} />
        ))}
      </div>
    </section>
  );
}

export default HistoricalValidationPanel;
