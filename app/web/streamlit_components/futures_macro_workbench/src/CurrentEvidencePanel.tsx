import type { EvidencePayload } from "./FuturesMacroWorkbench";

function CurrentEvidencePanel({ evidence }: { evidence: EvidencePayload }) {
  return (
    <section className="fm-workbench__evidence" aria-labelledby="fm-evidence-title">
      <div className="fm-workbench__section-heading">
        <div><span>Evidence bridge</span><h3 id="fm-evidence-title">{evidence.title}</h3></div>
      </div>
      <div className="fm-workbench__evidence-groups">
        {evidence.groups.map((group) => (
          <article className={`evidence-${group.key}`} key={group.key}>
            <header><strong>{group.label}</strong><span>{group.items.length}</span></header>
            {group.items.length > 0 ? (
              <ul>{group.items.map((item) => <li key={item}>{item}</li>)}</ul>
            ) : (
              <p>표시할 근거가 아직 없습니다.</p>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}

export default CurrentEvidencePanel;
