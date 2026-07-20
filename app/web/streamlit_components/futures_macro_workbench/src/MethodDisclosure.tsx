import type { HorizonCard, MethodPayload } from "./FuturesMacroWorkbench";

function MethodDisclosure({
  method,
  horizons,
  boundaryNote,
  onToggle,
}: {
  method: MethodPayload;
  horizons: HorizonCard[];
  boundaryNote: string;
  onToggle: () => void;
}) {
  const metrics = [
    ["원천", method.source],
    ["독립 표본", method.effective_episodes],
    ["Brier", method.brier],
    ["기준 Brier", method.baseline_brier],
    ["확률 보정", method.calibration],
  ];
  const provisional = horizons.filter(
    (item) => item.kind === "conditional_outlook"
      && item.probability_status === "PROVISIONAL"
      && item.disclosure_probabilities.length > 0,
  );
  return (
    <details className="fm-workbench__method fm-workbench__disclosure" onToggle={onToggle}>
      <summary>방법론과 품질</summary>
      <div className="fm-workbench__method-grid">
        {metrics.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}
      </div>
      {provisional.length > 0 ? (
        <div className="fm-workbench__provisional-disclosure">
          <strong>검증 중 분포 · 첫 화면 비공개</strong>
          {provisional.map((item) => (
            <div key={`disclosure-${item.key}`}>
              <span>{item.label}</span>
              <small>{item.disclosure_probabilities.map((row) => `${row.label} ${Math.round(row.value * 100)}%`).join(" · ")}</small>
            </div>
          ))}
        </div>
      ) : null}
      {method.caveats.length > 0 ? <ul>{method.caveats.map((item) => <li key={item}>{item}</li>)}</ul> : null}
      <p>{boundaryNote}</p>
    </details>
  );
}

export default MethodDisclosure;
