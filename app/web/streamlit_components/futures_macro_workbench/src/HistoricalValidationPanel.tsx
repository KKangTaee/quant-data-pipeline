import type { FuturesMacroAction, FuturesMacroMetric, FuturesMacroWorkbenchPayload } from "./FuturesMacroWorkbench";

type HistoricalValidationPanelProps = {
  pendingValidation: boolean;
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

function HistoricalValidationPanel({ pendingValidation, validation, onAction }: HistoricalValidationPanelProps) {
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

      <div className="fm-workbench__validation-control">
        <button
          className="fm-workbench__validation-action"
          disabled={pendingValidation}
          onClick={() => onAction(validation.action)}
          title={validation.action.detail}
          type="button"
        >
          {validation.action.label}
        </button>
        {validation.action.detail ? <small>{validation.action.detail}</small> : null}
        {pendingValidation ? (
          <div className="fm-workbench__validation-loading" role="status">
            <span />
            과거 표본 계산 중...
          </div>
        ) : null}
      </div>

      <div className="fm-workbench__validation-status-grid">
        {validation.metrics.map((item) => (
          <MetricTile item={item} key={`${item.label}-${item.value}`} />
        ))}
      </div>

      <div className="fm-workbench__validation-conclusion-grid">
        {validation.conclusion.map((item) => (
          <MetricTile item={item} key={`${item.label}-${item.value}`} />
        ))}
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
