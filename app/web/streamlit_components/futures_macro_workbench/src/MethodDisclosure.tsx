import type { CalculationScope, MethodPayload } from "./FuturesMacroWorkbench";

function MethodDisclosure({
  method,
  boundaryNote,
  scope,
  onToggle,
}: {
  method: MethodPayload;
  boundaryNote: string;
  scope: CalculationScope;
  onToggle: () => void;
}) {
  const metrics = [
    ["원천", method.source],
    ["관측창", "최근 1D · 5D · 20D"],
    ["Family", `${scope.available_family_count}/${scope.required_family_count}`],
    ["직접 입력", `${scope.direct_family_input_count}개 선물`],
  ];
  return (
    <details className="fm-workbench__method fm-workbench__disclosure" onToggle={onToggle}>
      <summary>방법론과 품질</summary>
      <div className="fm-workbench__method-grid">
        {metrics.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}
      </div>
      <div className="fm-workbench__scope-note">
        <span>계산 범위</span>
        <strong>
          선물 {scope.collected_count}개 수집 · family 직접 입력 {scope.direct_family_input_count}개 · family {scope.available_family_count}/{scope.required_family_count}
        </strong>
        <small>달러인덱스는 경제 사이클 공유 context · 은은 원본 관찰 전용</small>
      </div>
      {method.caveats.length > 0 ? <ul>{method.caveats.map((item) => <li key={item}>{item}</li>)}</ul> : null}
      <p>{boundaryNote}</p>
    </details>
  );
}

export default MethodDisclosure;
