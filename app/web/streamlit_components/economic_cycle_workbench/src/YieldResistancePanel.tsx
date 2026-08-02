import type { InflationPolicyPayload, ResistanceZone } from "./inflationPolicyTypes";

type Props = {
  rates: InflationPolicyPayload["rates"];
};

const driverLabels: Record<string, string> = {
  policy_driven: "정책 기대 주도",
  term_premium_driven: "기간 프리미엄 주도",
  inflation_driven: "기대인플레이션 주도",
  real_growth_driven: "실질금리·성장 주도",
  mixed: "혼합 주도",
};
const confirmationLabels: Record<string, string> = {
  UNCONFIRMED: "미확인",
  MIXED: "혼합",
  CONFIRMED: "인플레이션 확인",
};
const stateLabels: Record<string, string> = {
  APPROACH: "접근",
  ATTEMPT: "돌파 시도",
  CONFIRMED: "돌파 확인",
  HOLD: "안착",
  FAILED: "돌파 실패",
};

function nestedNumber(source: Record<string, unknown>, key: string) {
  const value = source[key];
  return typeof value === "number" ? value : null;
}

function bp(value: number | null) {
  return value == null ? "자료 없음" : `${value > 0 ? "+" : ""}${value.toFixed(1)}bp`;
}

function ZoneCard({ zone }: { zone: ResistanceZone }) {
  return (
    <article className={`resistance-zone-card owner-${zone.owner.toLowerCase()}`}>
      <header><span>{zone.owner_label}</span><b>{stateLabels[String(zone.state || "")] || "사용자 가정"}</b></header>
      <strong>{zone.definition_name || `${zone.instrument} 기준`}</strong>
      <p>{zone.instrument} {zone.zone_lower_pct.toFixed(2)}~{zone.zone_upper_pct.toFixed(2)}%</p>
      <small>
        {zone.owner === "AUTO"
          ? `${zone.timeframes.join("/") || "동적"}일 전고점 군집 · ${zone.known_at || "기준일 없음"}`
          : `${zone.saved_at || zone.known_at || "저장일 없음"} 저장 · 자동 기준과 별도`}
      </small>
    </article>
  );
}

function YieldResistancePanel({ rates }: Props) {
  const tenYear = rates.ten_year;
  const currentValue = typeof tenYear.current_value_pct === "number" ? tenYear.current_value_pct : null;
  const driver = rates.driver_decomposition;
  const policyTerm = (driver.policy_term_lens || {}) as Record<string, unknown>;
  const realInflation = (driver.real_inflation_lens || {}) as Record<string, unknown>;
  const confirmation = rates.inflation_confirmation;
  const confirmationStatus = String(confirmation.status || "UNCONFIRMED");
  return (
    <section className="yield-resistance-panel workbench-panel" aria-labelledby="yield-resistance-title">
      <div className="ip-section-heading">
        <div><span>FORWARD · TREASURY</span><h3 id="yield-resistance-title">10년물 동적 저항 기준</h3></div>
        <small>4.7% 고정선이 아니라 시점별 전고점 군집</small>
      </div>
      <div className="yield-driver-summary">
        <article><span>현재 DGS10</span><strong>{currentValue == null ? "—" : `${currentValue.toFixed(2)}%`}</strong><small>{String(tenYear.observation_date || "관측일 없음")}</small></article>
        <article><span>주도 요인</span><strong>{driverLabels[String(driver.dominant_driver || "mixed")] || "판단 제한"}</strong><small>정책과 실질·물가 lens 분리</small></article>
        <article><span>물가 확인</span><strong>{confirmationLabels[confirmationStatus] || "미확인"}</strong><small>{String(confirmation.reason || "확인 근거 없음")}</small></article>
      </div>
      <div className="yield-lens-grid">
        <article>
          <span>정책·기간 프리미엄 lens</span>
          <strong>2년 정책 proxy {bp(nestedNumber(policyTerm, "two_year_policy_proxy_change_bp"))}</strong>
          <small>{rates.term_premium_status === "READY" ? `기간 프리미엄 ${bp(nestedNumber(policyTerm, "term_premium_change_bp"))}` : "기간 프리미엄 자료 없음"}</small>
        </article>
        <article>
          <span>실질금리·기대인플레이션 lens</span>
          <strong>실질 10년 {bp(nestedNumber(realInflation, "real_10y_change_bp"))}</strong>
          <small>10년 BEI {bp(nestedNumber(realInflation, "breakeven_10y_change_bp"))}</small>
        </article>
      </div>
      <div className="resistance-zone-grid">
        {rates.resistance_zones.length
          ? rates.resistance_zones.map((zone) => <ZoneCard zone={zone} key={zone.definition_id} />)
          : <p className="ip-limited-copy">저장된 자동 또는 사용자 금리 기준이 없습니다.</p>}
      </div>
    </section>
  );
}

export default YieldResistancePanel;
