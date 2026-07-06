import type { CSSProperties } from "react";
import type { FuturesMacroWorkbenchPayload } from "./FuturesMacroWorkbench";

type MacroContextSectionProps = {
  payload: FuturesMacroWorkbenchPayload;
  toneColor: (tone: string | undefined) => string;
};

function MacroContextSection({ payload, toneColor }: MacroContextSectionProps) {
  return (
    <section className="fm-workbench__macro-section fm-workbench__section-card" aria-label="매크로 컨텍스트">
      <div className="fm-workbench__brief">
        <div className="fm-workbench__brief-copy">
          <div className="fm-workbench__kicker">{payload.brief.kicker}</div>
          <div className="fm-workbench__title">{payload.brief.title}</div>
          {payload.brief.sub_scenario ? (
            <div className="fm-workbench__subscenario">
              {payload.brief.sub_scenario}
              {payload.brief.regime_hint ? ` · ${payload.brief.regime_hint}` : ""}
            </div>
          ) : null}
          <p>{payload.brief.summary}</p>
          {payload.brief.reason ? <p className="fm-workbench__reason">{payload.brief.reason}</p> : null}
          {payload.brief.evidence.length > 0 ? (
            <div className="fm-workbench__evidence-line">
              {payload.brief.evidence.slice(0, 2).map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          ) : null}
        </div>
        <div className="fm-workbench__brief-side">
          <div className="fm-workbench__confidence">
            <span>근거 강도</span>
            <strong>{payload.brief.confidence_label}</strong>
            <small>{payload.brief.confidence_detail}</small>
          </div>
          {payload.brief.metrics.map((item) => (
            <div className="fm-workbench__metric" key={`${item.label}-${item.value}`} style={{ "--fm-tone": toneColor(item.tone) } as CSSProperties}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              {item.detail ? <small>{item.detail}</small> : null}
            </div>
          ))}
        </div>
      </div>

      <div className="fm-workbench__scores" aria-label="Futures Macro score chips">
        {payload.scores.map((score) => (
          <div className="fm-workbench__score" key={score.label} style={{ "--fm-tone": toneColor(score.tone) } as CSSProperties}>
            <span>{score.label}</span>
            <strong>{score.value}</strong>
            <small>{score.direction} · {score.coverage}</small>
            {score.polarity ? (
              <small className="fm-workbench__score-hint">
                {score.polarity.split(" · ").map((line) => (
                  <span className="fm-workbench__score-hint-line" key={line}>{line}</span>
                ))}
              </small>
            ) : null}
          </div>
        ))}
      </div>
    </section>
  );
}

export default MacroContextSection;
