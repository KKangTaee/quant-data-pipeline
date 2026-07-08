import { useState } from "react";
import type { CSSProperties } from "react";
import type { FuturesMacroFlowPeriod, FuturesMacroWorkbenchPayload } from "./FuturesMacroWorkbench";

type RecentFlowSectionProps = {
  flow: FuturesMacroWorkbenchPayload["flow"];
  onHeightChange: () => void;
  toneColor: (tone: string | undefined) => string;
};

function RecentFlowSection({ flow, onHeightChange, toneColor }: RecentFlowSectionProps) {
  const [selectedFlowKey, setSelectedFlowKey] = useState("");
  const fallbackFlowPeriod: FuturesMacroFlowPeriod = {
    key: "1W",
    label: "1W",
    title: flow.title,
    basis: flow.basis,
    summary: flow.summary,
    cards: flow.cards,
  };
  const flowPeriods = flow.periods && flow.periods.length > 0 ? flow.periods : [fallbackFlowPeriod];
  const initialFlowKey = flow.default_period || flowPeriods[0]?.key || "1W";
  const effectiveFlowKey = flowPeriods.some((period) => period.key === selectedFlowKey) ? selectedFlowKey : initialFlowKey;
  const selectedFlow = flowPeriods.find((period) => period.key === effectiveFlowKey) || flowPeriods[0] || fallbackFlowPeriod;

  return (
    <section className="fm-workbench__flow-section fm-workbench__section-card" aria-label="최근 흐름">
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
                      onHeightChange();
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
            <div className="fm-workbench__flow-card" key={`${selectedFlow.key}-${card.label}`} style={{ "--fm-tone": toneColor(card.tone) } as CSSProperties}>
              <span>{card.label}</span>
              <strong>{card.value}</strong>
              <small>{card.detail}</small>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default RecentFlowSection;
