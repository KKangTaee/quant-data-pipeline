import React from "react";
import { WindowData } from "./contracts";
import { statusLabels } from "./presentation";

export default function IntradayChangeSummary({
  window: w,
}: {
  window: WindowData;
}) {
  return (
    <section className={`story tone-${w.reading.tone}`}>
      <div className="story-label">
        <span className="eyebrow">선택 구간의 종합 해석</span>
        <span className={`status ${w.status.toLowerCase()}`}>
          {statusLabels[w.status]}
        </span>
      </div>
      <h2>{w.reading.headline}</h2>
      <p className="story-summary">{w.reading.interpretation}</p>
      <div className="verdicts">
        {w.reading.condition_results.map((c) => (
          <span key={c.key} className={`pill tone-${c.tone}`}>
            {c.verdict}
          </span>
        ))}
      </div>
    </section>
  );
}
