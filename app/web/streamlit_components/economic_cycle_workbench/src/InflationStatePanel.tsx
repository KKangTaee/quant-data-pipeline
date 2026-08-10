import type { InflationPolicyPayload, NextReleaseScenario } from "./inflationPolicyTypes";

type Props = {
  inflation: InflationPolicyPayload["inflation"];
  policy: InflationPolicyPayload["policy"];
  showProbabilities: boolean;
  showPolicyProbabilities: boolean;
};

const printRows = [0.1, 0.2, 0.3, 0.4, 0.5];

const pct = (value: number) => `${Math.round(value * 100)}%`;
const exactPct = (value: number) => `${(value * 100).toFixed(2)}%`;
const signedPoints = (value?: number | null) => value == null
  ? "—"
  : `${value > 0 ? "+" : ""}${(value * 100).toFixed(1)}%p`;

function scenarioFor(rows: NextReleaseScenario[], mom: number) {
  return rows.find((row) => Math.abs(row.mom_pct - mom) < 1e-9);
}

function InflationStatePanel({
  inflation,
  policy,
  showProbabilities,
  showPolicyProbabilities,
}: Props) {
  const stateTotal = inflation.state_rows.reduce((sum, item) => sum + item.probability, 0);
  const thresholds = Object.entries(inflation.threshold_probabilities)
    .sort(([left], [right]) => Number(left) - Number(right));
  const reacceleration = inflation.state_probabilities.reacceleration || 0;
  const shockReacceleration = inflation.state_probabilities.shock_reacceleration || 0;
  const hikeOne = policy.net_move_probabilities.hike_1 || 0;
  const hikeTwo = policy.net_move_probabilities.hike_2 || 0;
  const hikeThreePlus = policy.net_move_probabilities.hike_3_plus || 0;
  const hikeTotal = hikeOne + hikeTwo + hikeThreePlus;
  return (
    <section className="inflation-state-panel workbench-panel" aria-labelledby="inflation-state-title">
      <div className="ip-section-heading">
        <div><span>FORWARD · INFLATION</span><h3 id="inflation-state-title">연말 Core PCE 다섯 상태</h3></div>
        <small>{showProbabilities ? `5상태 합계 ${Math.round(stateTotal * 100)}%` : inflation.reason}</small>
      </div>

      {showProbabilities ? (
        <div className="inflation-state-list" aria-label="연말 Core PCE 5상태 확률">
          {inflation.state_rows.map((row) => (
            <div className={`inflation-state-row state-${row.id}`} key={row.id}>
              <span>{row.label}</span>
              <div className="inflation-state-track" aria-label={`${row.label} ${pct(row.probability)}`}>
                <i style={{ width: pct(row.probability) }} />
              </div>
              <strong>{pct(row.probability)}</strong>
            </div>
          ))}
        </div>
      ) : (
        <p className="ip-limited-copy">검증 게이트를 통과하기 전에는 상태 확률을 현재 판단으로 표시하지 않습니다.</p>
      )}

      <div className="inflation-thresholds">
        <h4>중요 연말 수준 도달 확률</h4>
        {showProbabilities && thresholds.length ? (
          <div>
            {thresholds.map(([threshold, probability]) => (
              <article key={threshold}>
                <span>{Number(threshold).toFixed(1)}%</span>
                <strong>{pct(probability)}</strong>
              </article>
            ))}
          </div>
        ) : <p>3.4% · 3.5% · 3.6% 중요 수준은 검증 후 확률로 공개합니다.</p>}
      </div>

      <div className="next-release-preparation">
        <div className="ip-subheading">
          <div><span>NEXT RELEASE</span><h4>다음 Core PCE 발표 전 준비표</h4></div>
          <small>한 번의 발표를 자동 인상 신호로 해석하지 않음</small>
        </div>
        <section
          className="next-release-current-baseline"
          aria-label="다음 Core PCE 현재 비교 기준"
        >
          <header>
            <div><span>CURRENT BASELINE</span><strong>현재 비교 기준</strong></div>
            <small>아래 변화량은 이 확률에서 움직이는 폭입니다.</small>
          </header>
          <div className="baseline-card-grid">
            <article className="baseline-card">
              <div className="baseline-card-total">
                <span>물가 재가속 합계</span>
                <strong>{showProbabilities ? exactPct(reacceleration + shockReacceleration) : "물가 경로 검증 후 공개"}</strong>
              </div>
              {showProbabilities ? (
                <div className="baseline-breakdown">
                  <span>재가속 <b>{exactPct(reacceleration)}</b></span>
                  <span>충격성 재가속 <b>{exactPct(shockReacceleration)}</b></span>
                </div>
              ) : null}
            </article>
            <article className="baseline-card">
              <div className="baseline-card-total">
                <span>연말 순인상 경로 합계</span>
                <strong>{showPolicyProbabilities ? exactPct(hikeTotal) : "정책 경로 검증 후 공개"}</strong>
              </div>
              {showPolicyProbabilities ? (
                <div className="baseline-breakdown">
                  <span>순 1회 <b>{exactPct(hikeOne)}</b></span>
                  <span>순 2회 <b>{exactPct(hikeTwo)}</b></span>
                  <span>순 3회 이상 <b>{exactPct(hikeThreePlus)}</b></span>
                </div>
              ) : null}
            </article>
          </div>
          <p>정책 경로는 25bp 단위 연말 순변화이며, 중간 FOMC 회의의 실제 순서를 뜻하지 않습니다.</p>
        </section>
        <div className="next-release-table-wrap">
          <table>
            <thead><tr><th>가정</th><th>현재 전망 대비 재가속 변화</th><th>현재 전망 대비 연말 순인상 경로 변화</th><th>해석</th></tr></thead>
            <tbody>
              {printRows.map((mom) => {
                const scenario = scenarioFor(inflation.next_release_scenarios, mom);
                const inflationAvailable = showProbabilities
                  && (scenario?.inflation_publication_status || scenario?.publication_status) === "READY";
                const policyAvailable = inflationAvailable
                  && (scenario?.policy_publication_status || scenario?.publication_status) === "READY";
                return (
                  <tr key={mom} aria-label={`Core PCE ${mom.toFixed(1)}% 시나리오`}>
                    <th>Core PCE {mom.toFixed(1)}%</th>
                    <td>{inflationAvailable ? signedPoints(scenario?.reacceleration_delta) : "—"}</td>
                    <td>{policyAvailable ? signedPoints(scenario?.hike_delta) : "—"}</td>
                    <td>{inflationAvailable
                      ? policyAvailable
                        ? "기존 경로를 posterior로 갱신"
                        : "연말 물가 변화 계산 · 정책 검증 대기"
                      : scenario?.reason || "검증 전"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

export default InflationStatePanel;
