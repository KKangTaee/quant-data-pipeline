import React, { useEffect, useRef } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import "./style.css";

type Phase = "recovery" | "expansion" | "slowdown" | "recession";
type PublicationStatus = "READY" | "LIMITED";
type EstimateStatus = "VERIFIED" | "PROVISIONAL" | "UNAVAILABLE";
type Probabilities = Record<Phase, number>;

type Horizon = {
  horizon_months: 0 | 1 | 2;
  label: string;
  probabilities: Probabilities | null;
  dominant_phase: Phase | null;
  dominant_phase_label?: string | null;
  confidence: number | null;
  publication_status: PublicationStatus;
  estimate_status?: EstimateStatus;
  estimate_label?: string;
  reason?: string | null;
};

type HistoryPoint = {
  date: string;
  phase: Phase | null;
  probabilities: Probabilities | null;
  status: PublicationStatus;
  estimate_status?: EstimateStatus;
  nber_recession: boolean;
};

type Evidence = {
  factor: string;
  series_id?: string | null;
  group: "real_economy" | "forecast_context";
  direction: "강화" | "약화" | "중립";
  value?: number | null;
  source_date?: string | null;
  source_basis?: string;
};

type MarketImplication = {
  asset_group: "rates" | "equities" | "gold_dollar" | "commodities";
  label: string;
  phase_context: string;
  context: string;
  is_directional_forecast: false;
};

type CyclePayload = {
  schema_version: "economic_cycle_v1";
  status: "READY" | "LIMITED" | "ERROR";
  as_of_date?: string | null;
  model_version?: string | null;
  headline?: {
    phase?: Phase | null;
    phase_label?: string;
    summary?: string;
  };
  horizons: Horizon[];
  cycle_clock?: {
    recent_path?: {
      date: string;
      phase: Phase | null;
      status: PublicationStatus;
      estimate_status?: EstimateStatus;
    }[];
    forecast_markers?: {
      horizon_months: number;
      phase: Phase | null;
      status: PublicationStatus;
      estimate_status?: EstimateStatus;
    }[];
    expected_transition?: string | null;
  };
  evidence: Evidence[];
  market_implications: MarketImplication[];
  history: HistoryPoint[];
  sources?: { name: string; source_date: string; basis?: string }[];
  limitations: string[];
};

type Props = ComponentProps & { args: { payload?: CyclePayload } };
type PlotPoint = { x: number; y: number };

const PHASE_ORDER: Phase[] = ["recovery", "expansion", "slowdown", "recession"];
const PHASE_LABEL: Record<Phase, string> = {
  recovery: "회복",
  expansion: "확장",
  slowdown: "둔화",
  recession: "침체",
};
const HORIZON_LABEL: Record<number, string> = {
  0: "현재",
  1: "1개월 후",
  2: "2개월 후",
};
const ESTIMATE_LABEL: Record<EstimateStatus, string> = {
  VERIFIED: "검증된 모델 추정",
  PROVISIONAL: "잠정 모델 추정",
  UNAVAILABLE: "판단 불가",
};
const FACTOR_LABEL: Record<string, string> = {
  activity_score: "생산·소비 활동",
  labor_income_score: "고용·소득",
  activity_momentum_3m: "실물 모멘텀",
  labor_income_momentum_3m: "고용 모멘텀",
  financial_leading_score: "금리·신용·금융여건",
  inflation_policy_score: "물가·정책 압력",
};

const formatPercent = (value: number) => `${Math.round(value * 100)}%`;
const formatMonth = (value?: string | null) => value ? value.slice(0, 7).replace("-", ".") : "-";

function probabilityCoordinate(probabilities: Probabilities): PlotPoint {
  const level = probabilities.expansion + probabilities.slowdown
    - probabilities.recovery - probabilities.recession;
  const momentum = probabilities.recovery + probabilities.expansion
    - probabilities.slowdown - probabilities.recession;
  return {
    x: 180 + Math.max(-1, Math.min(1, level)) * 128,
    y: 160 - Math.max(-1, Math.min(1, momentum)) * 112,
  };
}

function resolveEstimateStatus(item: {
  estimate_status?: EstimateStatus;
  publication_status?: PublicationStatus;
  status?: PublicationStatus;
  probabilities?: Probabilities | null;
}): EstimateStatus {
  if (item.estimate_status && item.estimate_status in ESTIMATE_LABEL) {
    return item.estimate_status;
  }
  if (!item.probabilities) return "UNAVAILABLE";
  return (item.publication_status || item.status) === "READY"
    ? "VERIFIED"
    : "PROVISIONAL";
}

function pointList(points: PlotPoint[]) {
  return points.map((point) => `${point.x},${point.y}`).join(" ");
}

function splitPointSegments(points: Array<PlotPoint | null>): PlotPoint[][] {
  const segments: PlotPoint[][] = [];
  let current: PlotPoint[] = [];
  points.forEach((point) => {
    if (point) {
      current.push(point);
      return;
    }
    if (current.length) segments.push(current);
    current = [];
  });
  if (current.length) segments.push(current);
  return segments;
}

function HorizonCard({ horizon }: { horizon: Horizon }) {
  const available = Boolean(horizon.probabilities && horizon.dominant_phase);
  const estimateStatus = resolveEstimateStatus(horizon);
  const provisional = horizon.estimate_status === "PROVISIONAL" || estimateStatus === "PROVISIONAL";
  const verified = horizon.estimate_status === "VERIFIED" || estimateStatus === "VERIFIED";
  const label = horizon.estimate_label || ESTIMATE_LABEL[estimateStatus];
  return (
    <article className={`horizon-card estimate-${estimateStatus.toLowerCase()}`} tabIndex={0}>
      <header>
        <div>
          <span>{HORIZON_LABEL[horizon.horizon_months] || horizon.label}</span>
          <strong>{available && horizon.dominant_phase ? `${PHASE_LABEL[horizon.dominant_phase]} 우세` : "판단 불가"}</strong>
        </div>
        <div className="horizon-state">
          <b className={verified ? "badge-verified" : provisional ? "badge-provisional" : "badge-unavailable"}>
            {label}
          </b>
          {available && horizon.confidence != null ? <em>{formatPercent(horizon.confidence)}</em> : null}
        </div>
      </header>
      {available && horizon.probabilities ? (
        <>
          <div className="probability-list" aria-label={`${horizon.label} 국면 확률`}>
            {PHASE_ORDER.map((phase) => (
              <div className="probability-row" key={phase}>
                <span>{PHASE_LABEL[phase]}</span>
                <div className="probability-bar" aria-label={`${PHASE_LABEL[phase]} ${formatPercent(horizon.probabilities[phase])}`}>
                  <i className={`phase-${phase}`} style={{ width: formatPercent(horizon.probabilities[phase]) }} />
                </div>
                <strong>{formatPercent(horizon.probabilities[phase])}</strong>
              </div>
            ))}
          </div>
          {provisional ? <p className="validation-note">검증: {horizon.reason || "일부 공개 기준 미달"}</p> : null}
        </>
      ) : (
        <p className="unavailable-copy">{horizon.reason || "유효한 모델 확률을 계산하지 못했습니다."}</p>
      )}
    </article>
  );
}

function QuadrantChart({ payload }: { payload: CyclePayload }) {
  const recent = payload.history.slice(-12);
  const observedSegments = splitPointSegments(
    recent.map((item) => item.probabilities ? probabilityCoordinate(item.probabilities) : null),
  );
  const recentObservedDots = recent
    .slice(-6)
    .flatMap((item) => item.probabilities ? [probabilityCoordinate(item.probabilities)] : []);
  const forecastSlots = [0, 1, 2].map((horizon) =>
    payload.horizons.find((item) => item.horizon_months === horizon) || null
  );
  const forecastSegments = splitPointSegments(
    forecastSlots.map((item) => item?.probabilities ? probabilityCoordinate(item.probabilities) : null),
  );
  const forecastHorizons = forecastSlots.filter(
    (item): item is Horizon & { probabilities: Probabilities } => Boolean(item?.probabilities),
  );
  const current = forecastSlots[0]?.probabilities ? forecastSlots[0] : null;
  const currentPoint = current ? probabilityCoordinate(current.probabilities) : null;

  return (
    <section className="cycle-map-panel" aria-labelledby="cycle-map-title">
      <div className="section-heading">
        <div><span>Cycle map</span><h3 id="cycle-map-title">레벨과 모멘텀으로 읽는 순환 위치</h3></div>
        <small>실선은 최근 12개월 · 점선은 현재부터 +2개월</small>
      </div>
      <div className="cycle-map-body">
        <svg className="cycle-quadrant" viewBox="0 0 360 320" role="img" aria-label="회복 확장 둔화 침체 2×2 경제사이클 경로">
          <rect className="quadrant recovery-zone" x="24" y="24" width="156" height="136" />
          <rect className="quadrant expansion-zone" x="180" y="24" width="156" height="136" />
          <rect className="quadrant recession-zone" x="24" y="160" width="156" height="136" />
          <rect className="quadrant slowdown-zone" x="180" y="160" width="156" height="136" />
          <line className="quadrant-axis" x1="180" y1="24" x2="180" y2="296" />
          <line className="quadrant-axis" x1="24" y1="160" x2="336" y2="160" />
          <text className="quadrant-label" x="38" y="48">회복</text>
          <text className="quadrant-label" x="292" y="48">확장</text>
          <text className="quadrant-label" x="38" y="282">침체</text>
          <text className="quadrant-label" x="292" y="282">둔화</text>
          <text className="axis-label" x="180" y="314">성장 레벨 →</text>
          <text className="axis-label vertical-label" x="9" y="160">모멘텀 →</text>
          {observedSegments.map((segment, index) => (
            segment.length > 1
              ? <polyline className="observed-path" points={pointList(segment)} key={`observed-segment-${index}`} />
              : null
          ))}
          {recentObservedDots.map((point, index) => (
            <circle className="observed-dot" cx={point.x} cy={point.y} r={index === recentObservedDots.length - 1 ? 3.5 : 2.5} key={`observed-${index}`} />
          ))}
          {forecastSegments.map((segment, index) => (
            segment.length > 1
              ? <polyline className="forecast-path" points={pointList(segment)} key={`forecast-segment-${index}`} />
              : null
          ))}
          {currentPoint ? <circle className={`current-cycle-dot ${current && resolveEstimateStatus(current) === "PROVISIONAL" ? "is-provisional" : ""}`} cx={currentPoint.x} cy={currentPoint.y} r="8" /> : null}
          {forecastHorizons.filter((item) => item.horizon_months > 0).map((item) => {
            const point = probabilityCoordinate(item.probabilities);
            const estimateStatus = resolveEstimateStatus(item);
            return (
              <g key={item.horizon_months} className={`forecast-point estimate-${estimateStatus.toLowerCase()}`}>
                <circle cx={point.x} cy={point.y} r={item.horizon_months === 1 ? 6 : 5} />
                <text x={point.x + 9} y={point.y - 8}>+{item.horizon_months}M</text>
              </g>
            );
          })}
        </svg>
        <div className="cycle-map-legend">
          <span><i className="legend-observed" />과거 관측 경로</span>
          <span><i className="legend-forecast" />미래 모델 경로</span>
          <span><i className="legend-provisional" />잠정 추정</span>
        </div>
        <p>확률이 오른쪽일수록 성장 레벨이 높고, 위쪽일수록 모멘텀이 강합니다. 경계에 가까울수록 두 국면이 경합합니다.</p>
      </div>
    </section>
  );
}

function EvidenceGroup({ title, subtitle, rows }: { title: string; subtitle: string; rows: Evidence[] }) {
  return (
    <section className="evidence-group">
      <header><div><h4>{title}</h4><p>{subtitle}</p></div><span>{rows.length}개 근거</span></header>
      <div className="evidence-list">
        {rows.length ? rows.map((item, index) => (
          <article key={`${item.factor}-${index}`} tabIndex={0}>
            <div><strong>{FACTOR_LABEL[item.factor] || item.series_id || item.factor}</strong><small>{formatMonth(item.source_date)} · {item.source_basis || "PIT 기준"}</small></div>
            <span className={`direction direction-${item.direction}`}>{item.direction}</span>
          </article>
        )) : <p className="empty-copy">표시할 근거가 아직 없습니다.</p>}
      </div>
    </section>
  );
}

function RegimeRibbon({ history, horizons }: { history: HistoryPoint[]; horizons: Horizon[] }) {
  const forecast = horizons.filter((item) => item.horizon_months > 0);
  return (
    <section className="ribbon-section" aria-labelledby="ribbon-title">
      <div className="section-heading"><div><span>Regime ribbon</span><h3 id="ribbon-title">과거·현재·미래를 한 시간축으로 보기</h3></div><small>최근 5년 + 2개월 전망</small></div>
      <div className="ribbon-legend"><span className="legend-model">모델 우세 국면</span><span className="nber-recession">NBER 침체</span><span className="limited-hatch">잠정 추정</span></div>
      <div className="regime-ribbon" role="list" aria-label="월별 경제 국면 이력과 전망">
        {history.map((item, index) => (
          <div className={`ribbon-month ${item.phase ? `phase-${item.phase}` : "phase-missing"} ${resolveEstimateStatus(item) === "PROVISIONAL" ? "is-limited" : ""}`} role="listitem" tabIndex={0} key={`${item.date}-${index}`} title={`${formatMonth(item.date)} · ${item.phase ? PHASE_LABEL[item.phase] : "판단 불가"} · ${ESTIMATE_LABEL[resolveEstimateStatus(item)]} · NBER ${item.nber_recession ? "침체" : "비침체"}`}>
            {item.nber_recession ? <i className="nber-recession" aria-label="NBER 침체" /> : null}
            {resolveEstimateStatus(item) === "PROVISIONAL" ? <i className="limited-hatch" aria-label="잠정 모델 추정" /> : null}
            {index === history.length - 1 ? <i className="current-marker" aria-label="현재" /> : null}
          </div>
        ))}
        {forecast.map((item) => (
          <div className={`ribbon-month forecast-ribbon ${item.dominant_phase ? `phase-${item.dominant_phase}` : "phase-missing"}`} role="listitem" tabIndex={0} key={`forecast-${item.horizon_months}`} title={`+${item.horizon_months}M · ${item.dominant_phase ? PHASE_LABEL[item.dominant_phase] : "판단 불가"} · ${ESTIMATE_LABEL[resolveEstimateStatus(item)]}`}>
            {resolveEstimateStatus(item) === "PROVISIONAL" ? <i className="limited-hatch" aria-label="잠정 모델 추정" /> : null}
          </div>
        ))}
      </div>
      <div className="ribbon-axis"><span>{formatMonth(history[0]?.date)}</span><span>{formatMonth(history[Math.floor(history.length / 2)]?.date)}</span><span>현재</span><span>+2M</span></div>
    </section>
  );
}

function EconomicCycleWorkbench({ args }: Props) {
  const payload = args.payload;
  const rootRef = useRef<HTMLElement>(null);
  useEffect(() => {
    Streamlit.setFrameHeight();
    if (!rootRef.current || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(() => Streamlit.setFrameHeight());
    observer.observe(rootRef.current);
    return () => observer.disconnect();
  }, [payload]);
  if (!payload || payload.schema_version !== "economic_cycle_v1") return null;

  const current = payload.horizons.find((item) => item.horizon_months === 0);
  const currentState = current ? resolveEstimateStatus(current) : "UNAVAILABLE";
  const realEvidence = payload.evidence.filter((evidence) => evidence.group === "real_economy");
  const forecastEvidence = payload.evidence.filter((evidence) => evidence.group === "forecast_context");
  return (
    <main className="cycle-workbench" data-status={payload.status} ref={rootRef}>
      <header className="cycle-hero">
        <div>
          <span className="eyebrow">U.S. ECONOMIC CYCLE</span>
          <h2>{payload.headline?.phase_label || "판단 불가"} {current?.dominant_phase ? "우세" : ""}</h2>
          <p>{payload.headline?.summary || "저장된 경제사이클 결과를 확인합니다."}</p>
        </div>
        <div className="hero-basis">
          <span>데이터 기준</span>
          <strong>{payload.as_of_date || "-"}</strong>
          <b className={`hero-status estimate-${currentState.toLowerCase()}`}>{ESTIMATE_LABEL[currentState]}</b>
        </div>
      </header>

      <section className="horizon-section" aria-labelledby="horizon-title">
        <div className="section-heading"><div><span>Probability path</span><h3 id="horizon-title">현재와 앞으로 1·2개월</h3></div><small>각 카드의 네 국면 합계는 100%</small></div>
        <div className="horizon-grid">{payload.horizons.map((horizon) => <HorizonCard key={horizon.horizon_months} horizon={horizon} />)}</div>
      </section>

      <div className="cycle-layout">
        <QuadrantChart payload={payload} />
        <section className="evidence-panel" aria-labelledby="evidence-title">
          <div className="section-heading"><div><span>Evidence</span><h3 id="evidence-title">국면을 움직인 근거</h3></div><small>강화 · 약화 · 중립</small></div>
          <EvidenceGroup title="실물경제 근거" subtitle="현재 국면을 정하는 생산·고용·소득" rows={realEvidence} />
          <EvidenceGroup title="전망 맥락" subtitle="1·2개월 확률을 조정하는 금융·물가·정책" rows={forecastEvidence} />
        </section>
      </div>

      <RegimeRibbon history={payload.history} horizons={payload.horizons} />

      <section className="market-implications" aria-labelledby="implication-title">
        <div className="section-heading"><div><span>Conditional market context</span><h3 id="implication-title">시장의 다음 질문</h3></div><small>전망·행동 신호가 아닌 조건부 맥락</small></div>
        <div className="implication-grid">{payload.market_implications.map((item) => <article key={item.asset_group} tabIndex={0}><span>{item.label}</span><strong>{item.phase_context} 맥락</strong><p>{item.context}</p></article>)}</div>
      </section>

      <details className="method-disclosure">
        <summary>방법론과 품질</summary>
        <div className="method-grid"><div><span>모델 버전</span><strong>{payload.model_version || "-"}</strong></div><div><span>기준일</span><strong>{payload.as_of_date || "-"}</strong></div><div><span>검증 상태</span><strong>{ESTIMATE_LABEL[currentState]}</strong></div></div>
        <p>잠정 모델 추정은 계산 결과를 보여주되 검증 미달 사유를 함께 표시합니다. 모델과 NBER 이력을 분리해 표시하며, 이 결과는 NBER의 공식 경기판정이 아니고 수익률 예측이나 매매 지시가 아닙니다.</p>
        <ul>{payload.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
      </details>
    </main>
  );
}

export default withStreamlitConnection(EconomicCycleWorkbench);
