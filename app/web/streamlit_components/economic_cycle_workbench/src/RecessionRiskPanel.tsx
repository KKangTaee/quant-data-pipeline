import type { RecessionRiskPayload } from "./inflationPolicyTypes";

type Props = { recession: RecessionRiskPayload };

const FEATURE_LABELS: Record<string, string> = {
  unemployment_gap_pct: "실업률 저점 대비 상승",
  payroll_3m_pct: "비농업 고용 3개월",
  claims_yoy_pct: "신규 실업수당 전년비",
  manufacturing_hours_3m_delta: "제조업 주당시간 3개월",
  temp_help_yoy_pct: "임시고용 전년비",
  industrial_production_3m_pct: "산업생산 3개월",
  real_income_6m_pct: "실질소득 6개월",
  real_consumption_6m_pct: "실질소비 6개월",
  yield_curve_slope_pct: "10년-2년 금리차",
  high_yield_oas_3m_delta_pct: "하이일드 스프레드 3개월",
};

function RecessionRiskPanel({ recession }: Props) {
  const ready = recession.publication_status === "READY"
    && recession.probability_12m != null;
  return (
    <section className="workbench-panel recession-risk-panel" aria-labelledby="recession-risk-title">
      <header className="ip-section-heading">
        <div>
          <span>INDEPENDENT RECESSION RISK · 12M</span>
          <h3 id="recession-risk-title">향후 12개월 침체 확률</h3>
        </div>
        <small>기존 경기 사이클 확률을 재사용하지 않습니다.</small>
      </header>
      {ready ? (
        <>
          <div className="recession-risk-summary">
            <article><span>침체 확률</span><strong>{Math.round(recession.probability_12m! * 100)}%</strong></article>
            <article><span>5단계 상태</span><strong>{recession.risk_label || recession.risk_state || "—"}</strong></article>
            <article><span>예측 범위</span><strong>{recession.horizon_months}개월</strong></article>
          </div>
          <div className="recession-driver-list" aria-label="침체 확률 주요 동인">
            {recession.top_drivers.map((driver) => (
              <article key={driver.feature}>
                <strong>{FEATURE_LABELS[driver.feature] || driver.feature}</strong>
                <span>{driver.direction === "risk_up" ? "위험 상승" : "위험 완화"}</span>
                <small>기여도 {driver.contribution >= 0 ? "+" : ""}{driver.contribution.toFixed(2)}</small>
              </article>
            ))}
          </div>
          <p className="ip-method-note">{recession.reason}</p>
        </>
      ) : (
        <div className="ip-limited-box">
          <strong>침체 확률 공개 기준 미충족</strong>
          <p>{recession.reason}</p>
        </div>
      )}
    </section>
  );
}

export default RecessionRiskPanel;
