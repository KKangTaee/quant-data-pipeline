import type { InflationPolicyPayload } from "./inflationPolicyTypes";

type Props = {
  policy: InflationPolicyPayload["policy"];
  showProbabilities: boolean;
};

const policyLabels: Record<string, string> = {
  cut_3_plus: "3회 이상 인하",
  cut_2: "2회 인하",
  cut_1: "1회 인하",
  hold: "동결",
  hike_1: "1회 인상",
  hike_2: "2회 인상",
  hike_3_plus: "3회 이상 인상",
};
const nextLabels: Record<string, string> = { cut: "인하", hold: "동결", hike: "인상" };
const order = ["cut_3_plus", "cut_2", "cut_1", "hold", "hike_1", "hike_2", "hike_3_plus"];
const pct = (value: number) => `${Math.round(value * 100)}%`;

function PolicyPathPanel({ policy, showProbabilities }: Props) {
  const nextMeeting = Object.entries(policy.next_meeting_probabilities)
    .sort((left, right) => right[1] - left[1]);
  return (
    <section className="policy-path-panel workbench-panel" aria-labelledby="policy-path-title">
      <div className="ip-section-heading">
        <div><span>FORWARD · FOMC</span><h3 id="policy-path-title">다음 회의와 연말 정책 경로</h3></div>
        <small>SEP 익명 분포를 개인별 물가 전망과 연결하지 않음</small>
      </div>
      {showProbabilities ? (
        <>
          <div className="next-meeting-grid">
            {nextMeeting.map(([key, probability]) => (
              <article key={key}><span>{nextLabels[key] || key}</span><strong>{pct(probability)}</strong></article>
            ))}
          </div>
          <div className="net-policy-paths" aria-label="연말까지 정책 순변화 확률">
            {order.map((key) => (
              <div key={key}>
                <span>{policyLabels[key]}</span>
                <div><i style={{ width: pct(policy.net_move_probabilities[key] || 0) }} /></div>
                <strong>{pct(policy.net_move_probabilities[key] || 0)}</strong>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="ip-limited-copy">{policy.reason} 다음 회의·연말 확률은 검증 후 공개합니다.</p>
      )}
    </section>
  );
}

export default PolicyPathPanel;
