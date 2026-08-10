import type { FutureFiveDayValidation } from "./FuturesMacroWorkbench";

function formatBrier(value: number | null) {
  return value == null || !Number.isFinite(value) ? "-" : value.toFixed(4);
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
          <dt>모델 Brier</dt>
          <dd>{formatBrier(validation.model_brier)}</dd>
        </div>
        <div>
          <dt>기본 빈도 Brier</dt>
          <dd>{formatBrier(validation.baseline_brier)}</dd>
        </div>
      </dl>
    </section>
  );
}

export default ForecastValidationGate;
