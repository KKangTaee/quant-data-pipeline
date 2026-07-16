import React, { useEffect, useRef } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import "./style.css";

type Phase = "recovery" | "expansion" | "slowdown" | "recession";
type PublicationStatus = "READY" | "LIMITED";
type Probabilities = Record<Phase, number>;

type Horizon = {
  horizon_months: 0 | 1 | 2;
  label: string;
  probabilities: Probabilities | null;
  dominant_phase: Phase | null;
  dominant_phase_label?: string | null;
  confidence: number | null;
  publication_status: PublicationStatus;
  reason?: string | null;
};

type HistoryPoint = {
  date: string;
  phase: Phase | null;
  probabilities: Probabilities | null;
  status: PublicationStatus;
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
    phase_order?: Phase[];
    recent_path?: { date: string; phase: Phase | null; status: PublicationStatus }[];
    forecast_markers?: { horizon_months: number; phase: Phase | null; status: PublicationStatus }[];
    expected_transition?: string | null;
  };
  evidence: Evidence[];
  market_implications: MarketImplication[];
  history: HistoryPoint[];
  sources?: { name: string; source_date: string; basis?: string }[];
  limitations: string[];
};

type Props = ComponentProps & { args: { payload?: CyclePayload } };

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

function phasePoint(phase: Phase, radius: number) {
  const index = PHASE_ORDER.indexOf(phase);
  const angle = (-90 + index * 90) * Math.PI / 180;
  return {
    x: 150 + Math.cos(angle) * radius,
    y: 150 + Math.sin(angle) * radius,
  };
}

function probabilityPath(probabilities: Probabilities) {
  const points = PHASE_ORDER.map((phase) => {
    const point = phasePoint(phase, 58 + probabilities[phase] * 48);
    return `${point.x},${point.y}`;
  });
  return `${points.join(" ")} ${points[0]}`;
}

function HorizonCard({ horizon }: { horizon: Horizon }) {
  const ready = horizon.publication_status === "READY" && horizon.probabilities;
  return (
    <article className={`horizon-card status-${horizon.publication_status.toLowerCase()}`} tabIndex={0}>
      <header>
        <div>
          <span>{HORIZON_LABEL[horizon.horizon_months] || horizon.label}</span>
          <strong>{ready && horizon.dominant_phase ? PHASE_LABEL[horizon.dominant_phase] : "판단 제한"}</strong>
        </div>
        {ready && horizon.confidence != null ? <b>{formatPercent(horizon.confidence)}</b> : null}
      </header>
      {ready ? (
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
      ) : (
        <p className="limited-copy">{horizon.reason || "검증 근거가 충분해질 때까지 숫자 확률을 표시하지 않습니다."}</p>
      )}
    </article>
  );
}

function CycleClock({ payload }: { payload: CyclePayload }) {
  const current = payload.horizons.find((item) => item.horizon_months === 0);
  const recent = (payload.cycle_clock?.recent_path || []).filter((item): item is typeof item & { phase: Phase } => Boolean(item.phase)).slice(-18);
  const trace = recent.map((item, index) => {
    const radius = 78 + (index / Math.max(1, recent.length - 1)) * 20;
    const point = phasePoint(item.phase, radius);
    return `${point.x},${point.y}`;
  }).join(" ");
  const currentPoint = current?.dominant_phase ? phasePoint(current.dominant_phase, 98) : null;
  return (
    <section className="cycle-clock-panel" aria-labelledby="cycle-clock-title">
      <div className="section-heading">
        <div><span>Cycle clock</span><h3 id="cycle-clock-title">레벨과 모멘텀으로 읽는 순환 위치</h3></div>
        <small>실선은 최근 18개월 · 점선은 확률상 우세 국면</small>
      </div>
      <div className="cycle-clock">
        <svg viewBox="0 0 300 300" role="img" aria-label="회복 확장 둔화 침체 순환 시계">
          <circle className="clock-ring" cx="150" cy="150" r="98" />
          <circle className="clock-core" cx="150" cy="150" r="48" />
          <text className="clock-core-label" x="150" y="144">현재 우세 국면</text>
          <text className="clock-core-value" x="150" y="166">{current?.dominant_phase ? PHASE_LABEL[current.dominant_phase] : "판단 제한"}</text>
          {PHASE_ORDER.map((phase) => {
            const point = phasePoint(phase, 120);
            return <g key={phase} className={`clock-node node-${phase}`}><circle cx={point.x} cy={point.y} r="22" /><text x={point.x} y={point.y + 4}>{PHASE_LABEL[phase]}</text></g>;
          })}
          {trace ? <polyline className="solid-trace" points={trace} /> : null}
          {currentPoint ? <circle className="current-dot" cx={currentPoint.x} cy={currentPoint.y} r="6" /> : null}
          {(payload.cycle_clock?.forecast_markers || []).map((marker) => {
            if (!currentPoint || !marker.phase || marker.status !== "READY") return null;
            const target = phasePoint(marker.phase, marker.horizon_months === 1 ? 108 : 116);
            return <g key={marker.horizon_months}><line className="forecast-marker dotted" x1={currentPoint.x} y1={currentPoint.y} x2={target.x} y2={target.y} /><circle className={`forecast-dot horizon-${marker.horizon_months}`} cx={target.x} cy={target.y} r={marker.horizon_months === 1 ? 7 : 5} /><text className="forecast-label" x={target.x + 8} y={target.y - 8}>+{marker.horizon_months}M</text></g>;
          })}
          {current?.probabilities ? <polygon className="probability-shape" points={probabilityPath(current.probabilities)} /> : null}
        </svg>
        <p>시계는 정해진 한 경로를 단정하지 않습니다. 네 국면 확률과 최근 이동을 함께 읽습니다.</p>
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

function RegimeRibbon({ history }: { history: HistoryPoint[] }) {
  return (
    <section className="ribbon-section" aria-labelledby="ribbon-title">
      <div className="section-heading"><div><span>10-year regime ribbon</span><h3 id="ribbon-title">모델 국면과 NBER 침체를 분리해 보기</h3></div><small>최근 121개 월말</small></div>
      <div className="ribbon-legend"><span className="legend-model">모델 우세 국면</span><span className="nber-recession">NBER 침체</span><span className="limited-hatch">제한적</span></div>
      <div className="regime-ribbon" role="list" aria-label="월별 경제 국면 이력">
        {history.map((item, index) => (
          <div className={`ribbon-month ${item.phase ? `phase-${item.phase}` : "phase-missing"} ${item.status === "LIMITED" ? "is-limited" : ""}`} role="listitem" tabIndex={0} key={`${item.date}-${index}`} title={`${formatMonth(item.date)} · ${item.phase ? PHASE_LABEL[item.phase] : "판단 제한"} · NBER ${item.nber_recession ? "침체" : "비침체"}`}>
            {item.nber_recession ? <i className="nber-recession" aria-label="NBER 침체" /> : null}
            {item.status === "LIMITED" ? <i className="limited-hatch" aria-label="제한적 결과" /> : null}
            {index === history.length - 1 ? <i className="current-marker" aria-label="현재" /> : null}
          </div>
        ))}
      </div>
      <div className="ribbon-axis"><span>{formatMonth(history[0]?.date)}</span><span>{formatMonth(history[Math.floor(history.length / 2)]?.date)}</span><span>{formatMonth(history[history.length - 1]?.date)}</span></div>
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

  const realEvidence = payload.evidence.filter((evidence) => evidence.group === "real_economy");
  const forecastEvidence = payload.evidence.filter((evidence) => evidence.group === "forecast_context");
  return (
    <main className="cycle-workbench" data-status={payload.status} ref={rootRef}>
      <header className="cycle-hero">
        <div><span className="eyebrow">U.S. ECONOMIC CYCLE</span><h2>{payload.headline?.phase_label || "판단 제한"} 국면을 확률로 읽습니다</h2><p>{payload.headline?.summary || "저장된 경제사이클 결과를 확인합니다."}</p></div>
        <div className="hero-basis"><span>데이터 기준</span><strong>{payload.as_of_date || "-"}</strong><small>{payload.status === "READY" ? "검증된 지평만 숫자 공개" : "일부 지평 판단 제한"}</small></div>
      </header>

      <section className="horizon-section" aria-labelledby="horizon-title">
        <div className="section-heading"><div><span>Probability path</span><h3 id="horizon-title">현재와 앞으로 1·2개월</h3></div><small>각 카드의 합계는 100%</small></div>
        <div className="horizon-grid">{payload.horizons.map((horizon) => <HorizonCard key={horizon.horizon_months} horizon={horizon} />)}</div>
      </section>

      <div className="cycle-layout">
        <CycleClock payload={payload} />
        <section className="evidence-panel" aria-labelledby="evidence-title">
          <div className="section-heading"><div><span>Evidence</span><h3 id="evidence-title">국면을 움직인 근거</h3></div><small>강화 · 약화 · 중립</small></div>
          <EvidenceGroup title="실물경제 근거" subtitle="현재 국면을 정하는 생산·고용·소득" rows={realEvidence} />
          <EvidenceGroup title="전망 맥락" subtitle="1·2개월 확률을 조정하는 금융·물가·정책" rows={forecastEvidence} />
        </section>
      </div>

      <section className="market-implications" aria-labelledby="implication-title">
        <div className="section-heading"><div><span>Conditional market context</span><h3 id="implication-title">시장의 다음 질문</h3></div><small>전망·행동 신호가 아닌 조건부 맥락</small></div>
        <div className="implication-grid">{payload.market_implications.map((item) => <article key={item.asset_group} tabIndex={0}><span>{item.label}</span><strong>{item.phase_context} 맥락</strong><p>{item.context}</p></article>)}</div>
      </section>

      <RegimeRibbon history={payload.history} />

      <details className="method-disclosure">
        <summary>방법론과 품질</summary>
        <div className="method-grid"><div><span>모델 버전</span><strong>{payload.model_version || "-"}</strong></div><div><span>기준일</span><strong>{payload.as_of_date || "-"}</strong></div><div><span>검증 상태</span><strong>{payload.status}</strong></div></div>
        <p>모델과 NBER 이력을 분리해 표시합니다. 이 결과는 NBER의 공식 경기판정이 아니며 수익률 예측이나 매매 지시가 아닙니다.</p>
        <ul>{payload.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
      </details>
    </main>
  );
}

export default withStreamlitConnection(EconomicCycleWorkbench);
