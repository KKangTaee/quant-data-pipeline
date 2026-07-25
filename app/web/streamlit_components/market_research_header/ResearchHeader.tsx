import type { ReactNode } from "react";
import "./style.css";

export type ResearchHeaderTone =
  | "neutral"
  | "info"
  | "positive"
  | "caution"
  | "negative";

export type ResearchHeaderVariant =
  | "cycle"
  | "futures"
  | "sentiment"
  | "events";

export type ResearchHeaderFact = {
  id: string;
  label: string;
  value: ReactNode;
  tone?: ResearchHeaderTone;
  showIndicator?: boolean;
};

export type ResearchHeaderAction = {
  id: string;
  label: string;
  kind: "primary" | "secondary";
  title?: string;
  disabled?: boolean;
  onClick: () => void;
};

export type ResearchHeaderMeta = {
  id: string;
  label: ReactNode;
};

export type ResearchHeaderProps = {
  titleId: string;
  variant: ResearchHeaderVariant;
  eyebrow: string;
  kicker: string;
  title: ReactNode;
  transition?: ReactNode;
  summary: ReactNode;
  detail?: ReactNode;
  facts?: ResearchHeaderFact[];
  actions?: ResearchHeaderAction[];
  actionFeedback?: ReactNode;
  notice?: ReactNode;
  meta?: ResearchHeaderMeta[];
};

function ResearchHeader({
  titleId,
  variant,
  eyebrow,
  kicker,
  title,
  transition,
  summary,
  detail,
  facts = [],
  actions = [],
  actionFeedback,
  notice,
  meta = [],
}: ResearchHeaderProps) {
  return (
    <section
      aria-labelledby={titleId}
      className={`research-header research-header--${variant}`}
    >
      <div className="research-header__top">
        <span className="research-header__eyebrow">{eyebrow}</span>
        {actions.length > 0 ? (
          <div className="research-header__action-area">
            <div className="research-header__actions">
              {actions.map((action) => (
                <button
                  className={`research-header__action research-header__action--${action.kind}`}
                  disabled={action.disabled}
                  key={action.id}
                  onClick={action.onClick}
                  title={action.title}
                  type="button"
                >
                  {action.label}
                </button>
              ))}
            </div>
            {actionFeedback ? (
              <span className="research-header__action-feedback">
                {actionFeedback}
              </span>
            ) : null}
          </div>
        ) : null}
      </div>

      <div className="research-header__grid">
        <div className="research-header__copy">
          <span className="research-header__kicker">{kicker}</span>
          <h2 id={titleId}>{title}</h2>
          {transition ? (
            <strong className="research-header__transition">{transition}</strong>
          ) : null}
          <p className="research-header__summary">{summary}</p>
          {detail ? (
            <small className="research-header__detail">{detail}</small>
          ) : null}
        </div>

        {facts.length > 0 ? (
          <aside className="research-header__facts">
            {facts.map((fact) => {
              const tone = fact.tone || "neutral";
              return (
                <div className="research-header__fact" key={fact.id}>
                  <span className="research-header__fact-label">{fact.label}</span>
                  <strong
                    className={`research-header__fact-value research-header__fact-value--${tone}`}
                  >
                    {fact.showIndicator ? (
                      <i aria-hidden="true" className="research-header__state-dot" />
                    ) : null}
                    {fact.value}
                  </strong>
                </div>
              );
            })}
          </aside>
        ) : null}
      </div>

      {notice ? <div className="research-header__notice">{notice}</div> : null}
      {meta.length > 0 ? (
        <div className="research-header__meta">
          {meta.map((item) => (
            <span key={item.id}>{item.label}</span>
          ))}
        </div>
      ) : null}
    </section>
  );
}

export default ResearchHeader;
