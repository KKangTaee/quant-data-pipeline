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

type IntramonthFactorDelta = {
  factor: string;
  baseline: number;
  current: number;
  delta: number;
};

type IntramonthSourceCoverage = {
  requested_series?: number | null;
  available_series?: number | null;
  series?: {
    series_id?: string | null;
    status?: string | null;
    latest_observation_date?: string | null;
    staleness_days?: number | null;
  }[];
};

type IntramonthSnapshot = {
  baseline_as_of_date: string;
  as_of_date: string;
  estimate_status: "PROVISIONAL";
  estimate_label: string;
  model_version?: string | null;
  current_horizon: Horizon;
  probability_deltas: Probabilities;
  factor_deltas: IntramonthFactorDelta[];
  source_collected_at?: string | null;
  source_coverage: IntramonthSourceCoverage;
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

type EvidenceTone = "positive-level" | "weak-level" | "support" | "burden" | "neutral";
type EvidencePresentation = {
  statusLabel: string;
  tone: EvidenceTone;
  description: string;
};

type PathwayStatus = "SUPPORTS_RISE" | "SUPPORTS_FALL" | "MIXED" | "NEUTRAL" | "UNAVAILABLE";
type CoverageStatus = "SUFFICIENT" | "PARTIAL" | "INSUFFICIENT";
type PriceStatus = "RISING" | "FALLING" | "MIXED" | "NEUTRAL" | "UNAVAILABLE";

type SeriesEvaluation = {
  series_id: string;
  as_of_date?: string | null;
  release_date?: string | null;
  current_value?: number | null;
  unit?: string | null;
  freshness: "CURRENT" | "UNAVAILABLE";
  reason_code?: string | null;
  changes: Record<string, number | null>;
  thresholds?: Record<string, number | null>;
  directions: Record<string, string>;
};

type AssetPathway = {
  pathway_id: string;
  label: string;
  status: PathwayStatus;
  status_label: string;
  reason_code?: string | null;
  core?: boolean;
  series: { series_id: string; status: PathwayStatus; evaluation: SeriesEvaluation }[];
};

type MovementMetric = {
  metric_id: string;
  label: string;
  as_of_date?: string | null;
  current_value?: number | null;
  level_unit?: string | null;
  change_unit?: string | null;
  changes: Record<string, number | null>;
  directions?: Record<string, string>;
  freshness?: "CURRENT" | "UNAVAILABLE";
  reason_code?: string | null;
};

type ObservedPathway = {
  pathway_id: string;
  label: string;
  status: "OBSERVED" | "UNAVAILABLE" | PathwayStatus;
  status_label?: string;
  reason_code?: string | null;
  series: SeriesEvaluation | { series_id: string; status: PathwayStatus; evaluation: SeriesEvaluation }[];
  interpretation?: string;
};

type EconomicState = {
  summary: string;
  observations: {
    factor: string;
    label: string;
    direction: "STRENGTHENING" | "WEAKENING" | "NEUTRAL" | "UNAVAILABLE";
    value?: number | null;
    source_date?: string | null;
  }[];
};

type PriceContext = {
  symbol: string;
  as_of_date?: string | null;
  status: PriceStatus;
  reason_code?: string | null;
  returns: {
    one_week: number | null;
    one_month: number | null;
    three_months: number | null;
  };
  freshness?: "CURRENT" | "UNAVAILABLE";
  source_basis: string;
};

type UnmeasuredPathway = {
  pathway_id: string;
  label: string;
  reason_code: string;
};

type MarketImplication = {
  asset_group: "rates" | "equities" | "gold" | "dollar" | "commodities";
  label: string;
  economic_as_of_date?: string | null;
  analysis_status: "READY" | "PARTIAL" | "LIMITED";
  coverage: CoverageStatus;
  economic_state: EconomicState;
  pathways?: AssetPathway[];
  unmeasured_pathways?: UnmeasuredPathway[];
  current_movement?: MovementMetric[];
  observed_pathways?: ObservedPathway[];
  current_interpretation?: string[];
  next_check_conditions?: string[];
  provenance?: string[];
  limitations?: string[];
  assets?: CommodityAsset[];
  narrative: string;
  summary: string;
  context: string;
  price_context?: PriceContext | null;
  is_directional_forecast: false;
};

type CommodityAsset = {
  asset_id: "wti" | "copper" | "gold";
  label: string;
  coverage: CoverageStatus;
  price_context?: PriceContext | null;
  current_movement?: MovementMetric[];
  observed_pathways?: ObservedPathway[];
  current_interpretation?: string[];
  next_check_conditions?: string[];
  provenance?: string[];
  limitations?: string[];
  narrative: string;
};

type CyclePayload = {
  schema_version: "economic_cycle_v2";
  status: "READY" | "LIMITED" | "ERROR";
  as_of_date?: string | null;
  model_version?: string | null;
  intramonth?: IntramonthSnapshot | null;
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

type Props = Omit<ComponentProps, "args"> & { args: { payload?: CyclePayload } };
type PlotPoint = { x: number; y: number };
type RibbonStyle = React.CSSProperties & { "--history-month-count": number };

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
  financial_leading_score: "금융·선행 여건",
  inflation_policy_score: "물가·정책 압력",
};

function resolveEvidencePresentation(item: Evidence): EvidencePresentation {
  const direction = item.direction;
  if (item.factor === "activity_score" || item.factor === "labor_income_score") {
    const subject = item.factor === "activity_score" ? "생산·소비 관련 지표" : "고용·소득 관련 지표";
    if (direction === "강화") return {
      statusLabel: "기준 이상",
      tone: "positive-level",
      description: `${subject}의 종합점수가 자기 과거 기준보다 높아 현재 경기 위치를 지지하는 근거입니다.`,
    };
    if (direction === "약화") return {
      statusLabel: "기준 이하",
      tone: "weak-level",
      description: `${subject}의 종합점수가 자기 과거 기준보다 낮아 현재 경기 위치를 낮추는 근거입니다.`,
    };
    return {
      statusLabel: "기준 부근",
      tone: "neutral",
      description: `${subject}의 종합점수가 자기 과거 기준 부근으로 현재 경기 위치에 중립적인 근거입니다.`,
    };
  }
  if (item.factor === "financial_leading_score") {
    if (direction === "강화") return {
      statusLabel: "전망 지원",
      tone: "support",
      description: "금리차·신용스프레드·금융여건·선행지표 조합이 향후 1·2개월 경기 전망을 지지하는 방향입니다.",
    };
    if (direction === "약화") return {
      statusLabel: "전망 부담",
      tone: "burden",
      description: "금리차·신용스프레드·금융여건·선행지표 조합이 향후 1·2개월 경기 전망을 제약하는 방향입니다.",
    };
  }
  if (item.factor === "inflation_policy_score") {
    if (direction === "강화") return {
      statusLabel: "전망 부담",
      tone: "burden",
      description: "근원물가·기대인플레이션·정책금리 조합의 압력이 높아 향후 1·2개월 경기 전망에 부담을 주는 방향입니다.",
    };
    if (direction === "약화") return {
      statusLabel: "부담 완화",
      tone: "support",
      description: "근원물가·기대인플레이션·정책금리 조합의 압력이 낮아 향후 1·2개월 경기 전망의 부담이 완화된 상태입니다.",
    };
  }
  return {
    statusLabel: "영향 중립",
    tone: "neutral",
    description: "현재 종합점수는 자기 과거 기준 부근으로 전망에 미치는 영향이 중립적입니다.",
  };
}

const formatPercent = (value: number) => `${Math.round(value * 100)}%`;
const formatSignedPoint = (value: number) => `${value > 0 ? "+" : ""}${(value * 100).toFixed(1)}%p`;
const formatSignedScore = (value: number) => `${value > 0 ? "+" : ""}${value.toFixed(2)}`;
const formatSignedPercent = (value: number | null) => value == null
  ? "-"
  : `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
const formatSeriesChange = (value: number | null, unit?: string | null) => value == null
  ? "-"
  : `${value > 0 ? "+" : ""}${value.toFixed(1)}${unit === "bp" ? "bp" : "%"}`;
const formatMovementLevel = (value: number | null, unit?: string | null) => value == null
  ? "-"
  : unit === "percent" ? `연 ${value.toFixed(2)}%`
  : `${value.toFixed(2)} ${unit || ""}`.trim();
const formatMonth = (value?: string | null) => value ? value.slice(0, 7).replace("-", ".") : "-";

const ECONOMIC_TO_EVIDENCE_DIRECTION: Record<
  Exclude<EconomicState["observations"][number]["direction"], "UNAVAILABLE">,
  Evidence["direction"]
> = {
  STRENGTHENING: "강화",
  WEAKENING: "약화",
  NEUTRAL: "중립",
};

function resolveEconomicStatePresentation(
  observation: EconomicState["observations"][number],
): Pick<EvidencePresentation, "statusLabel" | "tone"> {
  if (observation.direction === "UNAVAILABLE") {
    return { statusLabel: "자료 부족", tone: "neutral" };
  }
  const group = observation.factor === "activity_score" || observation.factor === "labor_income_score"
    ? "real_economy"
    : "forecast_context";
  return resolveEvidencePresentation({
    factor: observation.factor,
    group,
    direction: ECONOMIC_TO_EVIDENCE_DIRECTION[observation.direction],
  });
}

const COVERAGE_LABEL: Record<CoverageStatus, string> = {
  SUFFICIENT: "핵심 경로 충족",
  PARTIAL: "일부 경로 측정",
  INSUFFICIENT: "측정 경로 부족",
};

const PRICE_STATUS_LABEL: Record<PriceStatus, string> = {
  RISING: "상승",
  FALLING: "하락",
  MIXED: "기간별 혼재",
  NEUTRAL: "중립",
  UNAVAILABLE: "확인 불가",
};

const CHANGE_LABEL: Record<string, string> = {
  "5d": "1주(5거래일)",
  "21d": "1개월(21거래일)",
  "63d": "3개월(63거래일)",
  "4w": "최근 4주",
  "52w": "전년 동기",
  yoy_ttm: "완료 분기 TTM 전년 대비",
};

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

function dominantProbabilityPhase(probabilities: Probabilities): Phase {
  return PHASE_ORDER.reduce((winner, phase) =>
    probabilities[phase] > probabilities[winner] ? phase : winner
  );
}

function cycleTooltipPosition(point: PlotPoint) {
  return {
    x: Math.min(210, Math.max(28, point.x - 58)),
    y: point.y < 74 ? point.y + 14 : point.y - 46,
  };
}

function cyclePointLabel(
  period: string,
  phase: Phase,
  confidence: number,
  estimateStatus: EstimateStatus,
) {
  return `${period} · ${PHASE_LABEL[phase]} 우세 · ${formatPercent(confidence)} · ${ESTIMATE_LABEL[estimateStatus]}`;
}

function CyclePointTooltip({
  point,
  label,
  title,
  detail,
}: {
  point: PlotPoint;
  label: string;
  title: string;
  detail: string;
}) {
  const position = cycleTooltipPosition(point);
  return (
    <g className="cycle-hover-target" role="img" tabIndex={0} aria-label={label}>
      <circle className="cycle-hover-area" cx={point.x} cy={point.y} r="10" />
      <g className="cycle-tooltip" transform={`translate(${position.x} ${position.y})`}>
        <rect width="122" height="36" rx="7" />
        <text className="cycle-tooltip-title" x="8" y="14">{title}</text>
        <text className="cycle-tooltip-detail" x="8" y="27">{detail}</text>
      </g>
    </g>
  );
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
  const probabilities = horizon.probabilities;
  const available = Boolean(probabilities && horizon.dominant_phase);
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
      {available && probabilities ? (
        <>
          <div className="probability-list" aria-label={`${horizon.label} 국면 확률`}>
            {PHASE_ORDER.map((phase) => (
              <div className="probability-row" key={phase}>
                <span>{PHASE_LABEL[phase]}</span>
                <div className="probability-bar" aria-label={`${PHASE_LABEL[phase]} ${formatPercent(probabilities[phase])}`}>
                  <i className={`phase-${phase}`} style={{ width: formatPercent(probabilities[phase]) }} />
                </div>
                <strong>{formatPercent(probabilities[phase])}</strong>
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

function IntramonthFlow({
  intramonth,
  monthly,
}: {
  intramonth: IntramonthSnapshot;
  monthly?: Horizon;
}) {
  const current = intramonth.current_horizon;
  const latestSourceDate = (intramonth.source_coverage.series || [])
    .map((item) => item.latest_observation_date || "")
    .filter(Boolean)
    .sort()
    .at(-1) || null;
  const coverage = intramonth.source_coverage;
  const coverageLabel = coverage.requested_series != null
    ? `${coverage.available_series ?? 0}/${coverage.requested_series}개 원천`
    : "원천 범위 확인 중";
  const phaseDeltaEntries = PHASE_ORDER.map((phase) => ({
    phase,
    delta: intramonth.probability_deltas[phase],
  }));
  return (
    <section className="intramonth-flow-panel" aria-labelledby="intramonth-flow-title">
      <div className="section-heading">
        <div><span>Intramonth flow</span><h3 id="intramonth-flow-title">월말 이후 경제사이클 흐름</h3></div>
        <small>과거 월말은 유지하고 새로 공개된 정보만 별도 비교</small>
      </div>
      <div className="intramonth-flow-grid">
        <article className="intramonth-endpoint baseline-endpoint" tabIndex={0}>
          <span>월말 추정</span>
          <strong>{intramonth.baseline_as_of_date}</strong>
          <b>{monthly?.dominant_phase ? `${PHASE_LABEL[monthly.dominant_phase]} 우세` : "판단 불가"}</b>
          <small>{monthly?.confidence != null ? formatPercent(monthly.confidence) : "-"}</small>
        </article>

        <div className="intramonth-change" aria-label="월말 대비 월중 변화">
          <div className="intramonth-change-arrow" aria-hidden="true"><i /><span>월말 대비 변화</span><i /></div>
          <div className="intramonth-probability-deltas">
            {phaseDeltaEntries.map(({ phase, delta }) => (
              <span className={delta > 0 ? "delta-up" : delta < 0 ? "delta-down" : "delta-flat"} key={phase}>
                {PHASE_LABEL[phase]} <strong>{formatSignedPoint(delta)}</strong>
              </span>
            ))}
          </div>
          <div className="intramonth-factor-deltas">
            {intramonth.factor_deltas.map((item) => (
              <span key={item.factor}>
                {FACTOR_LABEL[item.factor] || item.factor}
                <strong className={item.delta > 0 ? "delta-up" : item.delta < 0 ? "delta-down" : "delta-flat"}>
                  {formatSignedScore(item.delta)}
                </strong>
              </span>
            ))}
          </div>
        </div>

        <article className="intramonth-endpoint current-endpoint" tabIndex={0}>
          <span>현재 입수정보 기반 잠정 계산</span>
          <strong>{intramonth.as_of_date}</strong>
          <b>{current.dominant_phase ? `${PHASE_LABEL[current.dominant_phase]} 우세` : "판단 불가"}</b>
          <small>{current.confidence != null ? formatPercent(current.confidence) : "-"}</small>
        </article>
      </div>
      <div className="intramonth-source-line">
        <span>계산 기준일 <strong>{intramonth.as_of_date}</strong></span>
        <span>마지막 수집 <strong>{intramonth.source_collected_at || "-"}</strong></span>
        <span>주요 원천 최신일 <strong>{latestSourceDate || "-"}</strong></span>
        <span>입수 범위 <strong>{coverageLabel}</strong></span>
      </div>
    </section>
  );
}

function QuadrantChart({ payload }: { payload: CyclePayload }) {
  const recent = payload.history.slice(-12);
  const observedSegments = splitPointSegments(
    recent.map((item) => item.probabilities ? probabilityCoordinate(item.probabilities) : null),
  );
  const observedHoverPoints = recent.flatMap((item) => {
    if (!item.probabilities) return [];
    const phase = item.phase || dominantProbabilityPhase(item.probabilities);
    const estimateStatus = resolveEstimateStatus(item);
    const confidence = item.probabilities[phase];
    const period = formatMonth(item.date);
    return [{
      key: item.date,
      point: probabilityCoordinate(item.probabilities),
      label: cyclePointLabel(period, phase, confidence, estimateStatus),
      title: `${period} · ${PHASE_LABEL[phase]} 우세`,
      detail: `${formatPercent(confidence)} · ${ESTIMATE_LABEL[estimateStatus]}`,
    }];
  });
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
  const currentProbabilities = current?.probabilities;
  const currentPoint = currentProbabilities ? probabilityCoordinate(currentProbabilities) : null;
  const intramonthHorizon = payload.intramonth?.current_horizon;
  const intramonthProbabilities = intramonthHorizon?.probabilities;
  const intramonthPoint = intramonthProbabilities
    ? probabilityCoordinate(intramonthProbabilities)
    : null;

  return (
    <section className="cycle-map-panel" aria-labelledby="cycle-map-title">
      <div className="section-heading">
        <div><span>Cycle map</span><h3 id="cycle-map-title">레벨과 모멘텀으로 읽는 순환 위치</h3></div>
        <small>실선은 최근 12개월 · 주황 점선은 +2개월 · 보라 점선은 월중</small>
      </div>
      <div className="cycle-map-body">
        <svg className="cycle-quadrant" viewBox="0 0 360 320" role="group" aria-label="회복 확장 둔화 침체 2×2 경제사이클 경로">
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
          {currentPoint && intramonthPoint ? (
            <line
              className="intramonth-bridge-path"
              x1={currentPoint.x}
              y1={currentPoint.y}
              x2={intramonthPoint.x}
              y2={intramonthPoint.y}
            />
          ) : null}
          {currentPoint ? <circle className={`current-cycle-dot ${current && resolveEstimateStatus(current) === "PROVISIONAL" ? "is-provisional" : ""}`} cx={currentPoint.x} cy={currentPoint.y} r="8" /> : null}
          {intramonthPoint ? (
            <circle className="intramonth-cycle-dot" cx={intramonthPoint.x} cy={intramonthPoint.y} r="6.5" />
          ) : null}
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
          {observedHoverPoints.map((item) => (
            <CyclePointTooltip
              key={`history-tooltip-${item.key}`}
              point={item.point}
              label={item.label}
              title={item.title}
              detail={item.detail}
            />
          ))}
          {forecastHorizons.map((item) => {
            const point = probabilityCoordinate(item.probabilities);
            const phase = item.dominant_phase || dominantProbabilityPhase(item.probabilities);
            const estimateStatus = resolveEstimateStatus(item);
            const confidence = item.confidence ?? item.probabilities[phase];
            const period = HORIZON_LABEL[item.horizon_months] || item.label;
            const label = cyclePointLabel(period, phase, confidence, estimateStatus);
            return (
              <CyclePointTooltip
                key={`forecast-tooltip-${item.horizon_months}`}
                point={point}
                label={label}
                title={`${period} · ${PHASE_LABEL[phase]} 우세`}
                detail={`${formatPercent(confidence)} · ${ESTIMATE_LABEL[estimateStatus]}`}
              />
            );
          })}
          {intramonthPoint && intramonthProbabilities && intramonthHorizon ? (
            <CyclePointTooltip
              point={intramonthPoint}
              label={cyclePointLabel(
                payload.intramonth?.as_of_date || "월중",
                intramonthHorizon.dominant_phase || dominantProbabilityPhase(intramonthProbabilities),
                intramonthHorizon.confidence
                  ?? intramonthProbabilities[
                    intramonthHorizon.dominant_phase || dominantProbabilityPhase(intramonthProbabilities)
                  ],
                "PROVISIONAL",
              )}
              title={`${payload.intramonth?.as_of_date || "월중"} · ${PHASE_LABEL[
                intramonthHorizon.dominant_phase || dominantProbabilityPhase(intramonthProbabilities)
              ]} 우세`}
              detail="현재 입수정보 기반 잠정 계산"
            />
          ) : null}
        </svg>
        <div className="cycle-map-legend">
          <span><i className="legend-observed" />과거 관측 경로</span>
          <span><i className="legend-forecast" />미래 모델 경로</span>
          {payload.intramonth ? <span><i className="legend-intramonth" />월말→월중 잠정 흐름</span> : null}
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
        {rows.length ? rows.map((item, index) => {
          const presentation = resolveEvidencePresentation(item);
          return (
            <article key={`${item.factor}-${index}`} tabIndex={0}>
              <div className="evidence-row-heading">
                <strong>{FACTOR_LABEL[item.factor] || item.series_id || item.factor}</strong>
                <span className={`evidence-status evidence-tone-${presentation.tone}`}>{presentation.statusLabel}</span>
              </div>
              <small>{formatMonth(item.source_date)} · {item.source_basis || "PIT 기준"}</small>
              <p className="evidence-description">{presentation.description}</p>
            </article>
          );
        }) : <p className="empty-copy">표시할 근거가 아직 없습니다.</p>}
      </div>
    </section>
  );
}

function EconomicStateBlock({ state }: { state: EconomicState }) {
  return (
    <section className="economic-state-block">
      <h5>사이클 판단의 공통 경제 배경</h5>
      <p>{state.summary}</p>
      <div className="economic-observations">
        {state.observations.map((observation) => {
          const presentation = resolveEconomicStatePresentation(observation);
          return (
            <span
              key={observation.factor}
              className={`evidence-tone-${presentation.tone}`}
            >
              {observation.label} · {presentation.statusLabel}
            </span>
          );
        })}
      </div>
    </section>
  );
}

function SeriesMetrics({ evaluation }: { evaluation: SeriesEvaluation }) {
  const changes = Object.entries(evaluation.changes || {});
  const primary = changes.filter(([key]) => key !== "5d").slice(0, 2);
  const details = <>
    {changes.map(([key, value]) => (
      <span key={key}>{CHANGE_LABEL[key] || key} {formatSeriesChange(value, evaluation.unit)}</span>
    ))}
    <span>기준일 {evaluation.as_of_date || evaluation.release_date || "-"}</span>
    <span>최신성 {evaluation.freshness === "CURRENT" ? "정상" : "자료 부족"}</span>
  </>;
  return (
    <div className="series-metrics" tabIndex={0}>
      <div className="series-primary-metrics">
        <strong>{evaluation.series_id}</strong>
        {primary.length ? primary.map(([key, value]) => (
          <span key={key}>{CHANGE_LABEL[key] || key} {formatSeriesChange(value, evaluation.unit)}</span>
        )) : <span>측정값 {evaluation.current_value == null ? "-" : evaluation.current_value.toFixed(2)}</span>}
      </div>
      <div className="pathway-hover-details" role="tooltip">{details}</div>
      <details className="pathway-details">
        <summary>세부 데이터</summary>
        <div>{details}</div>
      </details>
    </div>
  );
}

function PathwayGroup({
  title,
  pathways,
}: {
  title: string;
  pathways: AssetPathway[];
}) {
  return (
    <section className="pathway-group">
      <h5>{title}</h5>
      <div className="pathway-list">
        {pathways.length ? pathways.map((pathway) => (
          <article className={`pathway-item pathway-${pathway.status.toLowerCase()}`} key={pathway.pathway_id}>
            <header>
              <strong>{pathway.label}</strong>
              <span>{pathway.status_label}</span>
            </header>
            {pathway.series.map((series) => (
              <SeriesMetrics key={series.series_id} evaluation={series.evaluation} />
            ))}
          </article>
        )) : <p className="pathway-empty">해당 방향으로 확인된 측정 경로가 없습니다.</p>}
      </div>
    </section>
  );
}

function PricePathway({ item }: { item: MarketImplication }) {
  const price = item.price_context;
  if (!price) return null;
  const windows = [
    ["1주(5거래일)", price.returns.one_week],
    ["1개월(21거래일)", price.returns.one_month],
    ["3개월(63거래일)", price.returns.three_months],
  ] as const;
  return (
    <section className="price-pathway">
      <header>
        <h5>현재 움직임</h5>
        <b className={`price-status price-${price.status.toLowerCase()}`}>
          {PRICE_STATUS_LABEL[price.status]}
        </b>
      </header>
      <div className="price-return-grid" aria-label={`${item.label} 기간별 가격 변화율`}>
        {windows.map(([label, value]) => (
          <div key={label}>
            <span>{label}</span>
            <strong className={value == null ? "return-empty" : value > 0 ? "return-positive" : value < 0 ? "return-negative" : "return-flat"}>
              {formatSignedPercent(value)}
            </strong>
          </div>
        ))}
      </div>
      <p className="implication-basis">경제 {formatMonth(item.economic_as_of_date)} · 가격 {formatMonth(price.as_of_date)} · {price.symbol}</p>
    </section>
  );
}

function CurrentMovementBlock({
  label,
  economicAsOfDate,
  price,
  rows = [],
}: {
  label: string;
  economicAsOfDate?: string | null;
  price?: PriceContext | null;
  rows?: MovementMetric[];
}) {
  const priceItem = price ? {
    label,
    economic_as_of_date: economicAsOfDate,
    price_context: price,
  } as MarketImplication : null;
  const hasRateUnit = rows.some((row) => row.level_unit === "percent" || row.level_unit === "bp");
  return (
    <section className="observation-block current-movement-block">
      <h5>현재 움직임</h5>
      {hasRateUnit ? <p className="movement-unit-note">현재 값은 최신 저장 관측치이며, 금리 변화는 bp 기준입니다.</p> : null}
      {priceItem ? <PricePathway item={priceItem} /> : (
        <div className="movement-grid">
          {rows.length ? rows.map((row) => (
            <article className="movement-item" key={row.metric_id}>
              <header><strong>{row.label}</strong><span>{formatMovementLevel(row.current_value, row.level_unit)}</span></header>
              <SeriesMetrics evaluation={{
                series_id: row.metric_id,
                as_of_date: row.as_of_date,
                current_value: row.current_value,
                unit: row.change_unit,
                freshness: row.freshness || "UNAVAILABLE",
                reason_code: row.reason_code,
                changes: row.changes || {},
                directions: row.directions || {},
              }} />
            </article>
          )) : <p className="pathway-empty">표시할 현재 움직임이 없습니다.</p>}
        </div>
      )}
    </section>
  );
}

function ObservedPathwaysBlock({
  observed = [],
  legacy = [],
}: {
  observed?: ObservedPathway[];
  legacy?: AssetPathway[];
}) {
  if (!observed.length && legacy.length) {
    return <section className="observation-block"><PathwayGroup title="함께 관찰된 경로" pathways={legacy} /></section>;
  }
  return (
    <section className="observation-block observed-pathways-block">
      <h5>함께 관찰된 경로</h5>
      <div className="pathway-list">
        {observed.length ? observed.map((pathway) => {
          const seriesRows = Array.isArray(pathway.series)
            ? pathway.series.map((row) => row.evaluation)
            : [pathway.series];
          return (
            <article className={`pathway-item pathway-${String(pathway.status).toLowerCase()}`} key={pathway.pathway_id}>
              <header><strong>{pathway.label}</strong><span>{pathway.status === "UNAVAILABLE" ? "자료 부족" : "관찰됨"}</span></header>
              {pathway.interpretation ? <p>{pathway.interpretation}</p> : null}
              {seriesRows.map((series) => <SeriesMetrics key={series.series_id} evaluation={series} />)}
            </article>
          );
        }) : <p className="pathway-empty">표시할 관찰 경로가 없습니다.</p>}
      </div>
    </section>
  );
}

function InterpretationBlock({ rows }: { rows: string[] }) {
  return (
    <section className="observation-block interpretation-block">
      <h5>현재 해석</h5>
      <ul>{rows.map((row, index) => <li key={`${row}-${index}`}>{row}</li>)}</ul>
    </section>
  );
}

function NextCheckBlock({ rows }: { rows: string[] }) {
  return (
    <section className="observation-block next-check-block">
      <h5>향후 1·2개월 확인 조건</h5>
      <ul>{rows.map((row, index) => <li key={`${row}-${index}`}>{row}</li>)}</ul>
    </section>
  );
}

function AssetObservationBody({
  label,
  economicAsOfDate,
  price,
  movement,
  observed,
  legacy,
  interpretation,
  nextChecks,
}: {
  label: string;
  economicAsOfDate?: string | null;
  price?: PriceContext | null;
  movement?: MovementMetric[];
  observed?: ObservedPathway[];
  legacy?: AssetPathway[];
  interpretation: string[];
  nextChecks: string[];
}) {
  return <>
    <CurrentMovementBlock label={label} economicAsOfDate={economicAsOfDate} price={price} rows={movement} />
    <ObservedPathwaysBlock observed={observed} legacy={legacy} />
    <InterpretationBlock rows={interpretation} />
    <NextCheckBlock rows={nextChecks} />
  </>;
}

function UnmeasuredPathways({ rows }: { rows: UnmeasuredPathway[] }) {
  return (
    <section className="unmeasured-pathways">
      <h5>현재 데이터 범위 밖</h5>
      <div>
        {rows.map((row) => (
          <span key={row.pathway_id}>{row.label}</span>
        ))}
      </div>
    </section>
  );
}

function MarketImplicationCard({ item }: { item: MarketImplication }) {
  const interpretation = item.current_interpretation?.length ? item.current_interpretation : [item.narrative || item.summary || item.context];
  const nextChecks = item.next_check_conditions?.length
    ? item.next_check_conditions
    : ["다음 월의 가격과 관찰 경로가 같은 방향을 유지하는지 확인합니다."];
  return (
    <article className="implication-card is-connected" tabIndex={0}>
      <header>
        <div>
          <span>{item.label}</span>
          <strong>측정된 시장 경로와 현재 움직임</strong>
        </div>
        <div className="implication-overall">
          <span>데이터 범위</span>
          <b className={`coverage-status coverage-${item.coverage.toLowerCase()}`}>
            {COVERAGE_LABEL[item.coverage]}
          </b>
        </div>
      </header>
      <p className="implication-summary">{item.narrative || item.summary || item.context}</p>
      <EconomicStateBlock state={item.economic_state} />
      {item.assets?.length ? (
        <div className="commodity-asset-grid">
          {item.assets.map((asset) => (
            <article className="commodity-asset-card" key={asset.asset_id}>
              <header><strong>{asset.label}</strong><span className={`coverage-status coverage-${asset.coverage.toLowerCase()}`}>{COVERAGE_LABEL[asset.coverage]}</span></header>
              <p>{asset.narrative}</p>
              <AssetObservationBody
                label={asset.label}
                economicAsOfDate={item.economic_as_of_date}
                price={asset.price_context}
                movement={asset.current_movement}
                observed={asset.observed_pathways}
                interpretation={asset.current_interpretation?.length ? asset.current_interpretation : [asset.narrative]}
                nextChecks={asset.next_check_conditions?.length ? asset.next_check_conditions : nextChecks}
              />
            </article>
          ))}
        </div>
      ) : (
        <AssetObservationBody
          label={item.label}
          economicAsOfDate={item.economic_as_of_date}
          price={item.price_context}
          movement={item.current_movement}
          observed={item.observed_pathways}
          legacy={item.pathways}
          interpretation={interpretation}
          nextChecks={nextChecks}
        />
      )}
      {item.unmeasured_pathways?.length ? <UnmeasuredPathways rows={item.unmeasured_pathways} /> : null}
    </article>
  );
}

function RegimeRibbon({ history, horizons }: { history: HistoryPoint[]; horizons: Horizon[] }) {
  const forecastSlots = [1, 2].map((horizon) =>
    horizons.find((item) => item.horizon_months === horizon) || null
  );
  const ribbonStyle: RibbonStyle = {
    "--history-month-count": Math.max(history.length, 1),
  };
  return (
    <section className="ribbon-section" aria-labelledby="ribbon-title">
      <div className="section-heading"><div><span>Regime ribbon</span><h3 id="ribbon-title">과거·현재·미래를 한 시간축으로 보기</h3></div><small>최근 5년 + 2개월 전망</small></div>
      <div className="ribbon-legend"><span className="legend-model">모델 우세 국면</span><span className="nber-recession">NBER 침체</span><span className="limited-hatch">잠정 추정</span></div>
      <div className="regime-ribbon" role="list" aria-label="월별 경제 국면 이력과 전망" style={ribbonStyle}>
        {history.length ? history.map((item, index) => (
          <div className={`ribbon-month ${item.phase ? `phase-${item.phase}` : "phase-missing"} ${resolveEstimateStatus(item) === "PROVISIONAL" ? "is-limited" : ""}`} role="listitem" tabIndex={0} key={`${item.date}-${index}`} title={`${formatMonth(item.date)} · ${item.phase ? PHASE_LABEL[item.phase] : "판단 불가"} · ${ESTIMATE_LABEL[resolveEstimateStatus(item)]} · NBER ${item.nber_recession ? "침체" : "비침체"}`}>
            {item.nber_recession ? <i className="nber-recession" aria-label="NBER 침체" /> : null}
            {resolveEstimateStatus(item) === "PROVISIONAL" ? <i className="limited-hatch" aria-label="잠정 모델 추정" /> : null}
            {index === history.length - 1 ? <i className="current-marker" aria-label="현재" /> : null}
          </div>
        )) : (
          <div className="ribbon-month ribbon-empty-history phase-missing" role="listitem" aria-label="과거 경제사이클 이력 없음" />
        )}
        {forecastSlots.map((item, index) => {
          const horizon = index + 1;
          if (!item) {
            return (
              <div
                className="ribbon-month forecast-ribbon phase-missing"
                role="listitem"
                tabIndex={0}
                key={`forecast-missing-${horizon}`}
                title={`+${horizon}M · 판단 불가`}
              />
            );
          }
          return (
            <div className={`ribbon-month forecast-ribbon ${item.dominant_phase ? `phase-${item.dominant_phase}` : "phase-missing"}`} role="listitem" tabIndex={0} key={`forecast-${item.horizon_months}`} title={`+${item.horizon_months}M · ${item.dominant_phase ? PHASE_LABEL[item.dominant_phase] : "판단 불가"} · ${ESTIMATE_LABEL[resolveEstimateStatus(item)]}`}>
              {resolveEstimateStatus(item) === "PROVISIONAL" ? <i className="limited-hatch" aria-label="잠정 모델 추정" /> : null}
            </div>
          );
        })}
      </div>
      <div className="ribbon-axis"><span>{formatMonth(history[0]?.date)}</span><span>{formatMonth(history[Math.floor(history.length / 2)]?.date)}</span><span>현재</span><span>+2M</span></div>
    </section>
  );
}

function MonthlySignalGuide() {
  return (
    <details className="cycle-usage-guide">
      <summary>
        <div>
          <span>Reading guide</span>
          <strong>월별 사이클 신호 활용법</strong>
        </div>
        <small>관찰 → 준비 → 조정 검토</small>
      </summary>

      <div className="cycle-guide-body">
        <p className="cycle-guide-intro">
          이 지도는 장기 경기판정이 아니라 월별 변화의 방향을 빠르게 읽는 조기경보입니다. 한 번의 이동보다 지속성과 근거의 범위를 함께 확인합니다.
        </p>

        <div className="cycle-guide-steps" aria-label="월별 신호 확인 순서">
          <article>
            <span>1 · 관찰</span>
            <strong>한 달 신호</strong>
            <p>일시적 충격일 수 있으므로 방향이 바뀌었는지 먼저 관찰합니다.</p>
          </article>
          <article>
            <span>2 · 준비</span>
            <strong>같은 방향이 여러 달</strong>
            <p>변화가 이어지면 다음 국면 가능성과 대응 여력을 점검합니다.</p>
          </article>
          <article>
            <span>3 · 조정 검토</span>
            <strong>실물·금융·가격 동시 확인</strong>
            <p>서로 다른 근거가 같은 방향을 가리킬 때 포트폴리오 조정을 검토합니다.</p>
          </article>
        </div>

        <div className="cycle-guide-phase-grid">
          <article className="guide-phase-recovery">
            <span>회복 신호</span>
            <strong>낮은 성장 레벨에서 모멘텀이 개선</strong>
            <p>개선의 지속성과 금융여건 완화를 확인합니다. 침체에서 벗어나는 초기 신호이지 대세 상승의 확정은 아닙니다.</p>
          </article>
          <article className="guide-phase-expansion">
            <span>확장 신호</span>
            <strong>성장 레벨과 모멘텀이 함께 강함</strong>
            <p>기업이익과 시장 참여 폭이 넓어지는지, 물가와 금리가 성장을 제약하기 시작하는지 확인합니다.</p>
          </article>
          <article className="guide-phase-slowdown">
            <span>둔화 신호</span>
            <strong>성장 레벨은 높지만 모멘텀이 약화</strong>
            <p>정상화인지 광범위한 약화인지 구분하고, 쏠림·부채·경기민감 노출을 점검합니다.</p>
          </article>
          <article className="guide-phase-recession">
            <span>침체 신호</span>
            <strong>성장 레벨과 모멘텀이 함께 약함</strong>
            <p>실물과 신용의 약화 범위가 넓어지는지 확인하고, 현금 수요와 감내 가능한 손실 범위를 점검합니다.</p>
          </article>
        </div>

        <section className="cycle-guide-transitions" aria-labelledby="cycle-guide-transition-title">
          <h4 id="cycle-guide-transition-title">국면 전환은 이렇게 읽습니다</h4>
          <div className="cycle-guide-transition-grid">
            <article><strong>침체 → 회복</strong><p>바닥 통과의 초기 신호로 읽고 지속성을 확인합니다.</p></article>
            <article><strong>회복 → 확장</strong><p>기대 개선이 실제 생산·고용·이익으로 이어지는지 확인합니다.</p></article>
            <article><strong>확장 → 둔화</strong><p>건전한 정상화인지 여러 지표의 동반 약화인지 구분합니다.</p></article>
            <article><strong>둔화 → 침체</strong><p>약화가 일시적 충격을 넘어 넓고 오래 지속되는지 확인합니다.</p></article>
          </div>
        </section>

        <p className="cycle-guide-boundary">
          참고: 월별 조기경보를 해석하기 위한 안내이며 NBER의 공식 경기판정이나 개별 행동 지시가 아닙니다.
        </p>
      </div>
    </details>
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
  if (!payload || payload.schema_version !== "economic_cycle_v2") return null;

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

      {payload.intramonth ? <IntramonthFlow intramonth={payload.intramonth} monthly={current} /> : null}

      <div className="cycle-layout">
        <QuadrantChart payload={payload} />
        <section className="evidence-panel" aria-labelledby="evidence-title">
          <div className="section-heading"><div><span>Evidence</span><h3 id="evidence-title">현재와 전망의 판단 근거</h3></div><small>현재 수준과 전망 영향을 구분해 표시</small></div>
          <EvidenceGroup title="현재 위치의 근거" subtitle="현재점에 반영되는 생산·소비와 고용·소득" rows={realEvidence} />
          <EvidenceGroup title="1·2개월 전망에 추가되는 근거" subtitle="현재 근거에 더해 미래 확률을 조정하는 금융·선행 여건과 물가·정책" rows={forecastEvidence} />
        </section>
      </div>

      <RegimeRibbon history={payload.history} horizons={payload.horizons} />

      <section className="market-implications" aria-labelledby="implication-title">
        <div className="section-heading"><div><span>Measured market pathways</span><h3 id="implication-title">자산별 확인 포인트</h3></div><small>경제 상태·측정 경로·실제 가격을 분리해 확인</small></div>
        <div className="implication-grid">
          {payload.market_implications.map((item) => <MarketImplicationCard key={item.asset_group} item={item} />)}
        </div>
      </section>

      <MonthlySignalGuide />

      <details className="method-disclosure">
        <summary>방법론과 품질</summary>
        <div className="method-grid"><div><span>모델 버전</span><strong>{payload.model_version || "-"}</strong></div><div><span>기준일</span><strong>{payload.as_of_date || "-"}</strong></div><div><span>검증 상태</span><strong>{ESTIMATE_LABEL[currentState]}</strong></div></div>
        <p>잠정 모델 추정은 계산 결과를 보여주되 검증 미달 사유를 함께 표시합니다. 모델과 NBER 이력을 분리해 표시하며, 금·달러 가격은 저장된 연속선물 일봉이라 계약 교체 효과가 포함될 수 있습니다. 이 결과는 NBER의 공식 경기판정이 아니고 수익률 예측이나 매매 지시가 아닙니다.</p>
        <ul>{payload.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
      </details>
    </main>
  );
}

export default withStreamlitConnection(EconomicCycleWorkbench);
