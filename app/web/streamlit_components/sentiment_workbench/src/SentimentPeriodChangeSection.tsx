import { displayValue, signedValue } from "./SentimentWorkbench";
import type { PeriodChangeMetric, SentimentWorkbenchPayload } from "./SentimentWorkbench";

type Props = {
  periodChanges: SentimentWorkbenchPayload["period_changes"];
};

function metricRange(metric: PeriodChangeMetric) {
  if (!metric.available) return metric.detail;
  return `${metric.start_date || "-"} ${displayValue(metric.start_value, metric.unit_label)} → ${metric.end_date || "-"} ${displayValue(metric.end_value, metric.unit_label)}`;
}

function SentimentPeriodChangeSection({ periodChanges }: Props) {
  return (
    <section className="sentiment-workbench__period-change-section" aria-labelledby="sentiment-period-change-title">
      <div className="sentiment-workbench__section-heading">
        <div>
          <span>Observed change</span>
          <h3 id="sentiment-period-change-title">기간별 심리 변화</h3>
        </div>
        <small>미래 예측이 아닌 저장된 CNN·AAII 실제 관측 변화</small>
      </div>
      <div className="sentiment-workbench__period-change-grid">
        {periodChanges.periods.map((period) => (
          <article className="sentiment-workbench__period-card" data-period={period.key} key={period.key}>
            <header>
              <div>
                <span>{period.key}</span>
                <strong>{period.period_label}</strong>
              </div>
              <b className={`sentiment-workbench__period-status sentiment-workbench__period-status--${period.status.toLowerCase()}`}>
                {period.status_label}
              </b>
            </header>
            <small className="sentiment-workbench__period-basis">{period.basis}</small>
            <div className="sentiment-workbench__period-metrics">
              {period.metrics.map((metric) => (
                <div
                  className="sentiment-workbench__period-metric"
                  data-change-direction={metric.change_direction}
                  data-source={metric.key}
                  key={metric.key}
                >
                  <header>
                    <span>{metric.label}</span>
                    <small data-tone={metric.tone}>{metric.end_state || metric.status_label}</small>
                  </header>
                  {metric.available ? (
                    <div className="sentiment-workbench__period-value">
                      <strong>{displayValue(metric.end_value, metric.unit_label)}</strong>
                      <b>{signedValue(metric.change, metric.unit_label)}</b>
                    </div>
                  ) : (
                    <div className="sentiment-workbench__period-unavailable">
                      <strong>{metric.status_label}</strong>
                      <span>현재 {displayValue(metric.end_value, metric.unit_label)}</span>
                    </div>
                  )}
                  <p>{metricRange(metric)}</p>
                </div>
              ))}
            </div>
            <div
              className="sentiment-workbench__period-relationship"
              data-available={period.relationship.available ? "true" : "false"}
              data-tone={period.relationship.tone}
            >
              <span>두 축의 관계</span>
              <strong>{period.relationship.summary}</strong>
            </div>
          </article>
        ))}
      </div>
      <p className="sentiment-workbench__period-change-summary">{periodChanges.summary}</p>
    </section>
  );
}

export default SentimentPeriodChangeSection;
