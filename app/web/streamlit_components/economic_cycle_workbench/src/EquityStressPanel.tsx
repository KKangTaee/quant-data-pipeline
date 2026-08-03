import { useMemo, useState } from "react";
import type {
  EquityStressPayload,
  InflationPolicyCommand,
  InflationPolicyPayload,
} from "./inflationPolicyTypes";

type Props = {
  payload: InflationPolicyPayload;
  onCommand: (command: InflationPolicyCommand) => void;
};

function finite(value: unknown): number | null {
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function mapping(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? value as Record<string, unknown>
    : {};
}

function signedPercent(value: unknown): string {
  const parsed = finite(value);
  if (parsed === null) return "—";
  return `${parsed >= 0 ? "+" : ""}${parsed.toFixed(1)}%`;
}

function probability(value: unknown): string {
  const parsed = finite(value);
  return parsed === null ? "—" : `${(parsed * 100).toFixed(1)}%`;
}

function level(value: unknown, digits = 0): string {
  const parsed = finite(value);
  return parsed === null
    ? "—"
    : parsed.toLocaleString("ko-KR", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

function quantileRow(values: Record<string, number>, suffix = "") {
  return ["p20", "p50", "p80"].map((key) => (
    <b key={key}>{key.toUpperCase()} {level(values[key], suffix === "배" ? 2 : 0)}{suffix}</b>
  ));
}

function resultPayload(payload: InflationPolicyPayload): EquityStressPayload {
  if (payload.command_result?.command_id !== "run_equity_stress_scenario") {
    return payload.equity_stress;
  }
  return {
    ...payload.equity_stress,
    ...payload.command_result,
    publication_status: payload.command_result.publication_status || "NOT_AVAILABLE",
    reason: String(payload.command_result.reason || payload.equity_stress.reason),
    index_quantiles: mapping(payload.command_result.index_quantiles) as Record<string, number>,
    eps_quantiles: mapping(payload.command_result.eps_quantiles) as Record<string, number>,
    multiple_quantiles: mapping(payload.command_result.multiple_quantiles) as Record<string, number>,
    threshold_probabilities: mapping(payload.command_result.threshold_probabilities) as Record<string, number>,
    target_decompositions: mapping(payload.command_result.target_decompositions) as Record<string, Record<string, unknown>>,
  };
}

function EquityStressPanel({ payload, onCommand }: Props) {
  const result = resultPayload(payload);
  const initialTarget = useMemo(() => {
    const key = Object.keys(result.threshold_probabilities)[0];
    const parsed = key ? finite(key.split(":").at(-1)) : null;
    if (parsed !== null && parsed > 0) return parsed;
    const current = finite(result.current_index_level);
    return current !== null && current > 0 ? Math.round(current * 0.95) : 1;
  }, [result.current_index_level, result.threshold_probabilities]);
  const [aiUplift, setAiUplift] = useState(result.user_ai_eps_uplift_pct || 0);
  const [targetLevel, setTargetLevel] = useState(initialTarget);
  const aiError = aiUplift < -30 || aiUplift > 50
    ? "AI EPS 변화 가정은 -30%에서 +50% 사이여야 합니다."
    : null;
  const targetError = targetLevel <= 0 ? "확인할 지수 수준은 0보다 커야 합니다." : null;
  const available = result.publication_status === "READY" || result.publication_status === "LIMITED";
  const thresholds = Object.entries(result.threshold_probabilities);

  const runScenario = () => {
    if (aiError || targetError) return;
    onCommand({
      id: "run_equity_stress_scenario",
      nonce: `run_equity_stress_scenario:${Date.now()}`,
      payload: {
        target_level: targetLevel,
        user_ai_eps_uplift_pct: aiUplift,
        as_of_at: payload.as_of_at,
      },
    });
  };

  return (
    <section className="workbench-panel equity-stress-panel" aria-labelledby="equity-stress-title">
      <header className="ip-section-heading">
        <div>
          <span>EQUITY · EPS × MULTIPLE</span>
          <h3 id="equity-stress-title">S&amp;P 500 조건부 스트레스</h3>
        </div>
        <small>물가·정책·금리 경로에서 차년도 EPS와 forward multiple의 연말 범위를 함께 봅니다.</small>
      </header>

      {!available ? (
        <section className="equity-input-gate" aria-live="polite">
          <strong>공식 S&amp;P 500 EPS 빈티지 필요</strong>
          <p>Ingestion에서 공식 Index Earnings workbook을 등록하고 공동 물가·정책·금리 경로 검증을 완료해야 합니다.</p>
          <small>{result.reason}</small>
        </section>
      ) : (
        <>
          <div className="equity-assumption-grid">
            <article>
              <span>측정된 차년도 EPS 수정</span>
              <strong>{signedPercent(result.measured_next_year_eps_revision_pct)}</strong>
              <small>공식 release vintage에서 관측</small>
            </article>
            <article>
              <span>사용자 AI 수익화 가정</span>
              <strong>{signedPercent(result.user_ai_eps_uplift_pct)}</strong>
              <small>EPS에만 별도로 적용</small>
            </article>
          </div>

          <div className="equity-range-grid" aria-label="조건부 주가 구성요소 범위">
            <article><span>연말 지수 범위</span><div>{quantileRow(result.index_quantiles)}</div></article>
            <article><span>차년도 forward EPS</span><div>{quantileRow(result.eps_quantiles)}</div></article>
            <article><span>forward multiple</span><div>{quantileRow(result.multiple_quantiles, "배")}</div></article>
          </div>

          {result.publication_status === "READY" && thresholds.length ? (
            <div className="equity-threshold-list">
              <span>사용자 확인 수준 이하의 조건부 확률</span>
              {thresholds.map(([key, value]) => {
                const target = finite(key.split(":").at(-1));
                return <b key={key}>{level(target)} 이하 · {probability(value)}</b>;
              })}
            </div>
          ) : (
            <p className="ip-limited-copy">검증이 제한된 상태에서는 범위만 표시하고 수준별 확률은 공개하지 않습니다.</p>
          )}

          <form className="equity-scenario-form" onSubmit={(event) => { event.preventDefault(); runScenario(); }}>
            <label>
              <span>AI EPS 변화 가정</span>
              <input type="number" min="-30" max="50" step="0.1" value={aiUplift} onChange={(event) => setAiUplift(Number(event.target.value))} />
            </label>
            <label>
              <span>확인할 S&amp;P 500 수준</span>
              <input type="number" min="1" step="1" value={targetLevel} onChange={(event) => setTargetLevel(Number(event.target.value))} />
            </label>
            <button className="ip-primary-action" type="submit" disabled={Boolean(aiError || targetError)}>조건부 범위 계산</button>
          </form>
          {aiError || targetError ? <p className="ip-form-error" role="alert">{aiError || targetError}</p> : null}
        </>
      )}
      <p className="equity-association-disclosure">조건부 연관 분석이며 인과효과가 아닙니다.</p>
    </section>
  );
}

export default EquityStressPanel;
