import type { FamilyDirectionRow } from "./FuturesMacroWorkbench";

function DirectionCell({ row, window }: { row: FamilyDirectionRow; window: "one_day" | "five_day" | "twenty_day" }) {
  const state = row[window];
  return <span className={`fm-workbench__direction-cell tone-${state.tone}`}>{state.label}</span>;
}

function DirectionHeaders() {
  return <div className="fm-workbench__direction-headers"><span>방향축</span><span>1D</span><span>5D</span><span>20D</span></div>;
}

function DirectionRow({ row }: { row: FamilyDirectionRow }) {
  return (
    <div className="fm-workbench__direction-row">
      <strong>{row.label}</strong>
      <DirectionCell row={row} window="one_day" />
      <DirectionCell row={row} window="five_day" />
      <DirectionCell row={row} window="twenty_day" />
    </div>
  );
}

type Props = {
  coreDirections: FamilyDirectionRow[];
  confirmationSignals: FamilyDirectionRow[];
  confirmationSummary: string;
};

function FamilyDirectionSection({ coreDirections, confirmationSignals, confirmationSummary }: Props) {
  return (
    <section className="fm-workbench__families" aria-labelledby="fm-family-title">
      <div className="fm-workbench__section-heading">
        <div><span>Core alignment</span><h3 id="fm-family-title">선물군별 방향 정렬</h3></div>
        <small>핵심 방향과 확인 신호를 분리해 읽습니다</small>
      </div>
      <div className="fm-workbench__core-directions">
        <h4>핵심 방향 정렬</h4>
        <DirectionHeaders />
        {coreDirections.map((row) => <DirectionRow key={row.key} row={row} />)}
      </div>
      <div className="fm-workbench__confirmation-block">
        <div><span>Confirmation</span><h4>확인 신호</h4><p>{confirmationSummary}</p></div>
        <div className="fm-workbench__confirmation-grid">
          {confirmationSignals.map((row) => (
            <article key={row.key}>
              <strong>{row.label}</strong>
              <div><DirectionCell row={row} window="one_day" /><DirectionCell row={row} window="five_day" /><DirectionCell row={row} window="twenty_day" /></div>
              <small>최근 1D · 5D · 20D</small>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

export default FamilyDirectionSection;
