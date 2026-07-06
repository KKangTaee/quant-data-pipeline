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
    <div className="fm-workbench__validation">
      <div className="fm-workbench__validation-copy">
        <div className="fm-workbench__section-title">{validation.insight.purpose || validation.title}</div>
        <div className="fm-workbench__section-detail">{validation.insight.basis || validation.detail}</div>
        <p>{validation.insight.confidence_effect}</p>
        <button
          className="fm-workbench__validation-action"
          onClick={() => onAction(validation.action)}
          title={validation.action.detail}
          type="button"
        >
          {validation.action.label}
        </button>
      </div>
      <div className="fm-workbench__validation-insight">
        {insightTiles.map((item) => (
          <MetricTile item={item} key={`${item.label}-${item.value}`} />
        ))}
      </div>
      <div className="fm-workbench__validation-metrics">
        {validation.metrics.map((item) => (
          <MetricTile item={item} key={`${item.label}-${item.value}`} />
        ))}
      </div>
    </div>
  );
}

export default HistoricalValidationPanel;
