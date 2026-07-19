import type { WatchCondition } from "./SentimentWorkbench";

type Props = {
  watchConditions: WatchCondition[];
};

function WatchConditionsSection({ watchConditions }: Props) {
  return (
    <section className="sentiment-workbench__watch-section" aria-labelledby="sentiment-watch-title">
      <div className="sentiment-workbench__section-heading">
        <div><span>Watch</span><h3 id="sentiment-watch-title">다음 확인 조건</h3></div>
        <small>정렬·반전·지속 세 경로를 관찰</small>
      </div>
      <div className="sentiment-workbench__watch-grid">
        {watchConditions.map((item) => (
          <article data-watch-path={item.key} key={item.key}>
            <span>{item.label}</span>
            <p>{item.condition}</p>
            <small>{item.basis}</small>
          </article>
        ))}
      </div>
    </section>
  );
}

export default WatchConditionsSection;
