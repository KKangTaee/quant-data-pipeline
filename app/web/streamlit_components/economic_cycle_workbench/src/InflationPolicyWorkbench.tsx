import EquityStressPanel from "./EquityStressPanel";
import InflationEvidencePanel from "./InflationEvidencePanel";
import InflationStatePanel from "./InflationStatePanel";
import PolicyPathPanel from "./PolicyPathPanel";
import RecessionRiskPanel from "./RecessionRiskPanel";
import ReverseScenarioPanel from "./ReverseScenarioPanel";
import YieldResistancePanel from "./YieldResistancePanel";
import type { InflationPolicyWorkbenchProps } from "./inflationPolicyTypes";

function InflationPolicyWorkbench({ payload, onCommand }: InflationPolicyWorkbenchProps) {
  const showInflationProbabilities = payload.inflation.publication_status === "READY";
  const showPolicyProbabilities = payload.policy.publication_status === "READY";
  const showCombinedConclusion = showInflationProbabilities && showPolicyProbabilities;
  const q4 = payload.inflation.q4_quantiles_pct;
  const dominantState = [...payload.inflation.state_rows]
    .sort((left, right) => right.probability - left.probability)[0];
  const nextMeeting = Object.entries(payload.policy.next_meeting_probabilities)
    .sort((left, right) => right[1] - left[1])[0];
  const nearestZone = payload.rates.resistance_zones.find((zone) => zone.owner === "AUTO")
    || payload.rates.resistance_zones[0];
  return (
    <main className="inflation-policy-workbench" data-status={payload.publication_status}>
      <header className="inflation-policy-placeholder-hero">
        <span>U.S. INFLATION · POLICY · YIELDS</span>
        <h2>연말 Core PCE 경로</h2>
        <p>{payload.headline.summary}</p>
        <small>{payload.headline.history_label} · {payload.as_of_at || "기준시각 없음"}</small>
      </header>
      {showCombinedConclusion ? (
        <section className="inflation-policy-conclusion" aria-label="물가 정책 금리 현재 결론">
          <article><span>연말 Core PCE 중간값</span><strong>{q4.p50?.toFixed(2) || "—"}%</strong><small>{q4.p20?.toFixed(2) || "—"}~{q4.p80?.toFixed(2) || "—"}%</small></article>
          <article><span>가장 큰 물가 상태</span><strong>{dominantState?.label || "—"}</strong><small>{dominantState ? `${Math.round(dominantState.probability * 100)}%` : "확률 없음"}</small></article>
          <article><span>다음 회의</span><strong>{nextMeeting?.[0] === "hold" ? "동결" : nextMeeting?.[0] === "hike" ? "인상" : "인하"}</strong><small>{nextMeeting ? `${Math.round(nextMeeting[1] * 100)}%` : "확률 없음"}</small></article>
          <article><span>가까운 DGS10 기준</span><strong>{nearestZone ? `${nearestZone.zone_lower_pct.toFixed(2)}~${nearestZone.zone_upper_pct.toFixed(2)}%` : "—"}</strong><small>{nearestZone?.owner_label || "기준 없음"}</small></article>
          <article className="next-condition-card"><span>다음 확인 조건</span><strong>Core PCE 0.4~0.5% 시 posterior 변화 확인</strong><small>한 번의 발표로 인상 여부를 확정하지 않습니다.</small></article>
        </section>
      ) : (
        <section className="inflation-policy-unavailable" aria-live="polite">
          <strong>{payload.publication_status === "LIMITED" ? "검증 제한 상태" : "현재 공개 가능한 경로가 없습니다."}</strong>
          <p>{payload.headline.summary}</p>
        </section>
      )}
      <InflationStatePanel inflation={payload.inflation} showProbabilities={showInflationProbabilities} />
      <PolicyPathPanel policy={payload.policy} showProbabilities={showPolicyProbabilities} />
      <YieldResistancePanel rates={payload.rates} />
      <ReverseScenarioPanel payload={payload} onCommand={onCommand} />
      <EquityStressPanel payload={payload} onCommand={onCommand} />
      <RecessionRiskPanel recession={payload.recession} />
      <InflationEvidencePanel payload={payload} />
    </main>
  );
}

export default InflationPolicyWorkbench;
