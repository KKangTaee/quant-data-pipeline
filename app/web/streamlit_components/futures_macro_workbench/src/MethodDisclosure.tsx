import type { MethodPayload } from "./FuturesMacroWorkbench";

function MethodDisclosure({ method, boundaryNote }: { method: MethodPayload; boundaryNote: string }) {
  const metrics = [
    ["원천", method.source],
    ["독립 표본", method.effective_episodes],
    ["Brier", method.brier],
    ["기준 Brier", method.baseline_brier],
    ["확률 보정", method.calibration],
  ];
  return (
    <details className="fm-workbench__method">
      <summary>방법론과 품질</summary>
      <div className="fm-workbench__method-grid">
        {metrics.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}
      </div>
      {method.caveats.length > 0 ? <ul>{method.caveats.map((item) => <li key={item}>{item}</li>)}</ul> : null}
      <p>{boundaryNote}</p>
    </details>
  );
}

export default MethodDisclosure;
