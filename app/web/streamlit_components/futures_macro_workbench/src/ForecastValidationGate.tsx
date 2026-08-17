import type { FutureFiveDayValidation } from "./FuturesMacroWorkbench";

function formatBrierDelta(model: number | null, baseline: number | null) {
  if (model == null || baseline == null || !Number.isFinite(model) || !Number.isFinite(baseline)) {
    return "-";
  }
  const delta = model - baseline;
  const signed = `${delta > 0 ? "+" : ""}${delta.toFixed(4)}`;
  if (delta > 0) return `${signed} · 기준보다 나쁨`;
  if (delta < 0) return `${signed} · 기준보다 좋음`;
  return `${signed} · 기준과 같음`;
}

function ForecastValidationGate({ validation }: { validation: FutureFiveDayValidation }) {
  return (
    <section
      className={`fm-workbench__forecast-gate estimate-${validation.status.toLowerCase()}`}
      aria-labelledby="fm-forecast-gate-title"
    >
      <div className="fm-workbench__forecast-gate-copy">
        <span>Completed-session forecast gate</span>
        <h3 id="fm-forecast-gate-title">현재 흐름을 향후 5거래일로 연장할 수 있는가?</h3>
        <strong>{validation.title}</strong>
        <p>{validation.detail}</p>
        <b>{validation.policy}</b>
      </div>
      <dl className="fm-workbench__forecast-metrics">
        <div>
          <dt>검증 기준일</dt>
          <dd>{validation.reference_date || "-"}</dd>
        </div>
        <div>
          <dt>독립 표본</dt>
          <dd>{validation.episode_count > 0 ? `${validation.episode_count}개` : "-"}</dd>
        </div>
        <div>
          <dt>시간순 평가</dt>
          <dd>{validation.evaluation_count > 0 ? `${validation.evaluation_count}회` : "-"}</dd>
        </div>
        <div>
          <dt>기본 대비 Brier</dt>
          <dd>{formatBrierDelta(validation.model_brier, validation.baseline_brier)}</dd>
        </div>
      </dl>
    </section>
  );
}

export default ForecastValidationGate;
