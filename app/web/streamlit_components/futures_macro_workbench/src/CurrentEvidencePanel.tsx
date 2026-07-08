import type { FuturesMacroWorkbenchPayload } from "./FuturesMacroWorkbench";

type CurrentEvidencePanelProps = {
  evidence: FuturesMacroWorkbenchPayload["evidence"];
  boundaryNote: string;
  onHeightChange: () => void;
};

function CurrentEvidencePanel({ evidence, boundaryNote, onHeightChange }: CurrentEvidencePanelProps) {
  return (
    <details className="fm-workbench__evidence" onToggle={onHeightChange} open={evidence.default_open}>
      <summary>
        <span>{evidence.title}</span>
        <small>{boundaryNote}</small>
      </summary>
      <div className="fm-workbench__evidence-sections">
        {evidence.sections.map((section) => (
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
  );
}

export default CurrentEvidencePanel;
