import { OBSERVATION_LABEL } from "./FuturesMacroWorkbench";
import type { CommandPayload, FuturesMacroAction, HeroPayload } from "./FuturesMacroWorkbench";

type Props = {
  command: CommandPayload;
  hero: HeroPayload;
  pendingActionId: string;
  onAction: (action: FuturesMacroAction) => void;
};

function MacroContextSection({ command, hero, pendingActionId, onAction }: Props) {
  return (
    <section className="fm-workbench__hero" aria-labelledby="fm-hero-title">
      <div className="fm-workbench__command-row">
        <div>
          <span className="fm-workbench__eyebrow">{command.title}</span>
          <small>{command.detail}</small>
        </div>
        <div className="fm-workbench__actions" aria-label="선물 매크로 자료 동작">
          {command.actions.map((action) => (
            <button
              className={`fm-workbench__action fm-workbench__action--${action.kind}`}
              disabled={pendingActionId === action.id}
              key={action.id}
              onClick={() => onAction(action)}
              title={action.detail}
              type="button"
            >
              {pendingActionId === action.id ? "요청 중" : action.label}
            </button>
          ))}
        </div>
      </div>
      <div className="fm-workbench__hero-grid">
        <div className="fm-workbench__hero-copy">
          <span className="fm-workbench__kicker">{hero.kicker}</span>
          <h2 id="fm-hero-title">{hero.title}</h2>
          <div className="fm-workbench__transition">{hero.transition_label}</div>
          <p>{hero.summary}</p>
          {hero.today_summary ? <small className="fm-workbench__today">오늘의 재가격화 · {hero.today_summary}</small> : null}
        </div>
        <aside className="fm-workbench__hero-side">
          <div className={`fm-workbench__status observation-${hero.observation_status.toLowerCase()}`}>
            <span>관측 상태</span>
            <strong>{OBSERVATION_LABEL[hero.observation_status]}</strong>
          </div>
          <div><span>기준일</span><strong>{hero.as_of_date}</strong></div>
          <div><span>관측 범위</span><strong>{hero.coverage_label}</strong></div>
        </aside>
      </div>
      {hero.evidence.length > 0 ? (
        <div className="fm-workbench__hero-evidence">
          {hero.evidence.slice(0, 3).map((item) => <span key={item}>{item}</span>)}
        </div>
      ) : null}
    </section>
  );
}

export default MacroContextSection;
