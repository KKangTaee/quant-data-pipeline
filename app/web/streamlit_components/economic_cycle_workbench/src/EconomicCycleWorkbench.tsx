import React, { useEffect, useRef, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import EconomicCycleHero from "./EconomicCycleHero";
import InflationPolicyWorkbench from "./InflationPolicyWorkbench";
import type { InflationPolicyCommand, InflationPolicyPayload } from "./inflationPolicyTypes";
import "./style.css";

type Phase = "recovery" | "expansion" | "slowdown" | "contraction";
type DataStatus = "READY" | "LIMITED" | "UNAVAILABLE";

type ObservedState = {
  as_of_date?: string | null;
  raw_level?: number | null;
  level?: number | null;
  momentum?: number | null;
  phase?: Phase | null;
  phase_label?: string | null;
  activity_level?: number | null;
  labor_income_level?: number | null;
  activity_momentum?: number | null;
  labor_income_momentum?: number | null;
  level_breadth?: number | null;
  momentum_breadth?: number | null;
  available_series?: number | null;
  stale_series?: number | null;
  duration_months?: number | null;
  confidence?: "HIGH" | "MEDIUM" | "LIMITED";
  confidence_label?: string;
  revision_sensitivity?: "STABLE" | "SENSITIVE" | "UNAVAILABLE";
  revision_sensitivity_label?: string;
  data_status?: DataStatus;
};

type RecentChange = {
  horizon_months: 1 | 3 | 6;
  label: string;
  status: "STRENGTHENING" | "WEAKENING" | "MIXED" | "UNAVAILABLE";
  status_label: string;
  composite_delta?: number | null;
  breadth?: number | null;
  available_pairs?: number;
  activity_delta?: number | null;
  labor_income_delta?: number | null;
};

type CyclePoint = {
  date: string;
  level: number;
  momentum: number;
  phase: Phase;
  phase_label: string;
  nber_recession: boolean;
  confidence?: string | null;
  revision_sensitivity?: string | null;
};

type TransitionCondition = {
  condition_id: "persistence" | "diffusion" | "corroboration";
  label: string;
  status: "MET" | "UNMET" | "UNAVAILABLE";
  value?: unknown;
  threshold?: string;
  value_label?: string;
  threshold_label?: string;
};

type CurrentTransition = {
  from_phase: Phase;
  from_phase_label: string;
  target_phase: Phase;
  target_phase_label: string;
  status: "WATCH" | "CONFIRMED";
  status_label: string;
  conditions_met: number;
  conditions_total: number;
  conditions: TransitionCondition[];
};

type TransitionContext = {
  factor: string;
  value?: number | null;
  relation: "TOWARD_TARGET" | "SUPPORT_CURRENT" | "MIXED";
  relation_label: string;
};

type TransitionMonitor = {
  observed_phase?: Phase | null;
  observed_phase_label?: string | null;
  anchor_phase?: Phase | null;
  anchor_phase_label?: string | null;
  anchor_started_at?: string | null;
  anchor_source?: "INITIALIZED" | "CONFIRMED" | "LEGACY_OBSERVED" | "UNKNOWN";
  anchor_source_label?: string;
  anchor_confirmed_at?: string | null;
  target_phase?: Phase | null;
  target_phase_label?: string | null;
  status: "MAINTAIN" | "WATCH" | "CONFIRMED";
  status_label: string;
  conditions_met: number;
  conditions_total: number;
  candidate_started_at?: string | null;
  confirmed_at?: string | null;
  non_adjacent_observation?: boolean;
  current_transition?: CurrentTransition | null;
  conditions: TransitionCondition[];
  context: TransitionContext[];
};

type TransitionForecastAlternative = {
  phase: Phase;
  phase_label: string;
  probability: number;
};

type TransitionForecastDriver = {
  driver_id: string;
  label: string;
  value: number;
  contribution: number;
  current_effect: "RAISES_PRESSURE" | "LOWERS_PRESSURE" | "NEUTRAL";
  current_effect_label: string;
  higher_value_effect: "RAISES_PRESSURE" | "LOWERS_PRESSURE" | "NEUTRAL";
  higher_value_effect_label: string;
  signal_group?: "CORE" | "DRIVER" | "PHASE_CONTEXT";
};

type TransitionForecast = {
  contract_version: "transition_forecast_v1";
  status: "READY";
  current_phase: Phase;
  current_phase_label: string;
  pressure: {
    probability: number;
    historical_percentile: number;
    level: "LOW" | "NORMAL" | "ELEVATED" | "HIGH";
    level_label: string;
    summary: string;
    horizon_releases: number;
    horizon_definition: "next_3_usable_releases";
  };
  destination: {
    probabilities: Record<Phase, number>;
    primary_phase: Phase;
    primary_phase_label: string;
    alternatives: TransitionForecastAlternative[];
    current_phase_excluded: true;
    horizon_definition: "next_confirmed_transition";
  };
  drivers: TransitionForecastDriver[];
  boundary: string;
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

type IntramonthChange = {
  baseline_as_of_date: string;
  as_of_date: string;
  provisional: true;
  label: string;
  model_version?: string | null;
  raw_level_delta?: number | null;
  observed_state?: ObservedState | null;
  recent_changes?: RecentChange[];
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
type SeriesFreshness = "CURRENT" | "DELAYED" | "UNAVAILABLE";
type AssetDataStatus = "CURRENT" | "DELAYED" | "INSUFFICIENT";
type FreshnessStatus = "READY" | "REFRESH_AVAILABLE" | "MISSING" | "ERROR";

type SeriesEvaluation = {
  series_id: string;
  as_of_date?: string | null;
  release_date?: string | null;
  current_value?: number | null;
  unit?: string | null;
  freshness: SeriesFreshness;
  reason_code?: string | null;
  supports_current_signal?: boolean;
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
  freshness?: SeriesFreshness;
  reason_code?: string | null;
  supports_current_signal?: boolean;
};

type ObservedPathway = {
  pathway_id: string;
  label: string;
  status: "OBSERVED" | "DELAYED" | "UNAVAILABLE" | PathwayStatus;
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
  freshness?: SeriesFreshness;
  supports_current_signal?: boolean;
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
  data_status?: AssetDataStatus;
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
  data_status?: AssetDataStatus;
  summary?: string;
  price_context?: PriceContext | null;
  current_movement?: MovementMetric[];
  observed_pathways?: ObservedPathway[];
  current_interpretation?: string[];
  next_check_conditions?: string[];
  provenance?: string[];
  limitations?: string[];
  narrative: string;
};

type FreshnessScope = {
  status: FreshnessStatus;
  refresh_required: boolean;
  message: string;
  latest_observation_date?: string | null;
};

type EconomicCycleFreshness = {
  status: FreshnessStatus;
  overall_status?: FreshnessStatus;
  persisted_as_of_date?: string | null;
  target_as_of_date?: string | null;
  last_successful_collection_at?: string | null;
  latest_source_observation_date?: string | null;
  refresh_required: boolean;
  refresh_required_scopes?: ("cycle_snapshot" | "asset_pathways")[];
  message: string;
  cycle_snapshot?: FreshnessScope & {
    persisted_as_of_date?: string | null;
    target_as_of_date?: string | null;
  };
  asset_pathways?: FreshnessScope;
  action?: {
    id: "refresh_economic_cycle_data";
    label: string;
    enabled: boolean;
  };
};

type RefreshResult = {
  status: "success" | "partial_success" | "incomplete" | "failed";
  message: string;
};

export type CyclePayload = {
  schema_version: "economic_cycle_v3";
  status: "READY" | "LIMITED" | "ERROR";
  as_of_date?: string | null;
  model_version?: string | null;
  intramonth_change?: IntramonthChange | null;
  data_freshness?: EconomicCycleFreshness;
  refresh_result?: RefreshResult;
  headline?: {
    phase?: Phase | null;
    phase_label?: string;
    summary?: string;
  };
  observed_state: ObservedState;
  recent_changes: RecentChange[];
  transition_monitor?: TransitionMonitor | null;
  transition_forecast?: TransitionForecast | null;
  cycle_map: {
    phase_order: Phase[];
    points: CyclePoint[];
  };
  evidence: Evidence[];
  market_implications: MarketImplication[];
  sources?: { name: string; source_date: string; basis?: string }[];
  limitations: string[];
  inflation_policy?: InflationPolicyPayload;
};

type Props = Omit<ComponentProps, "args"> & { args: { payload?: CyclePayload } };
type RibbonStyle = React.CSSProperties & { "--history-month-count": number };

const PHASE_ORDER: Phase[] = ["recovery", "expansion", "slowdown", "contraction"];
const PHASE_LABEL: Record<Phase, string> = {
  recovery: "회복",
  expansion: "확장",
  slowdown: "둔화",
  contraction: "위축",
};
const CYCLE_ROUTE_NODES: Record<Phase, { x: number; y: number; labelX: number; labelY: number }> = {
  recovery: { x: 70, y: 70, labelX: 70, labelY: 34 },
  expansion: { x: 250, y: 70, labelX: 250, labelY: 34 },
  slowdown: { x: 250, y: 250, labelX: 250, labelY: 286 },
  contraction: { x: 70, y: 250, labelX: 70, labelY: 286 },
};
const CYCLE_ROUTE_ARCS: Record<string, string> = {
  "recovery:expansion": "M70 70 C118 25 202 25 250 70",
  "expansion:slowdown": "M250 70 C295 118 295 202 250 250",
  "slowdown:contraction": "M250 250 C202 295 118 295 70 250",
  "contraction:recovery": "M70 250 C25 202 25 118 70 70",
};
const CONFIDENCE_LABEL: Record<string, string> = {
  HIGH: "높음",
  MEDIUM: "보통",
  LIMITED: "제한",
};
const REVISION_SENSITIVITY_LABEL: Record<string, string> = {
  STABLE: "안정",
  SENSITIVE: "민감",
  UNAVAILABLE: "비교 불가",
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
      statusLabel: "전환 지원",
      tone: "support",
      description: "금리차·신용스프레드·금융여건·선행지표 조합이 다음 국면 전환 조건을 지지하는 참고 맥락입니다.",
    };
    if (direction === "약화") return {
      statusLabel: "전환 제약",
      tone: "burden",
      description: "금리차·신용스프레드·금융여건·선행지표 조합이 다음 국면 전환 조건을 제약하는 참고 맥락입니다.",
    };
  }
  if (item.factor === "inflation_policy_score") {
    if (direction === "강화") return {
      statusLabel: "전환 제약",
      tone: "burden",
      description: "근원물가·기대인플레이션·정책금리 조합의 압력이 높아 다음 국면 전환 조건을 제약하는 참고 맥락입니다.",
    };
    if (direction === "약화") return {
      statusLabel: "제약 완화",
      tone: "support",
      description: "근원물가·기대인플레이션·정책금리 조합의 압력이 낮아 다음 국면 전환 제약이 완화된 참고 맥락입니다.",
    };
  }
  return {
    statusLabel: "영향 중립",
    tone: "neutral",
    description: "현재 종합점수는 자기 과거 기준 부근으로 다음 국면 전환 조건에 미치는 영향이 중립적입니다.",
  };
}

const formatRatio = (value?: number | null) => value == null ? "-" : `${Math.round(value * 100)}%`;
const formatSignedScore = (value: number) => `${value > 0 ? "+" : ""}${value.toFixed(2)}`;
const formatSignedPercent = (value: number | null) => value == null
  ? "-"
  : `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
const formatSeriesChange = (value: number | null, unit?: string | null) => value == null
  ? "-"
  : `${value > 0 ? "+" : ""}${value.toFixed(1)}${unit === "bp" ? "bp" : "%"}`;
const formatMovementLevel = (value?: number | null, unit?: string | null) => value == null
  ? "-"
  : unit === "percent" ? `연 ${value.toFixed(2)}%`
  : `${value.toFixed(2)} ${unit || ""}`.trim();
const formatMonth = (value?: string | null) => value ? value.slice(0, 7).replace("-", ".") : "-";
const formatKoreanMonth = (value?: string | null) => {
  const text = String(value || "");
  return text.length >= 7 ? `${text.slice(0, 4)}년 ${text.slice(5, 7)}월` : "기록 없음";
};

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

const SERIES_FRESHNESS_LABEL: Record<SeriesFreshness, string> = {
  CURRENT: "정상",
  DELAYED: "갱신 지연",
  UNAVAILABLE: "자료 부족",
};

const PATHWAY_STATUS_LABEL: Record<"OBSERVED" | "DELAYED" | "UNAVAILABLE", string> = {
  OBSERVED: "관찰됨",
  DELAYED: "갱신 지연",
  UNAVAILABLE: "자료 부족",
};

const CHANGE_LABEL: Record<string, string> = {
  "5d": "1주(5거래일)",
  "21d": "1개월(21거래일)",
  "63d": "3개월(63거래일)",
  "4w": "최근 4주",
  "52w": "전년 동기",
  yoy_ttm: "완료 분기 TTM 전년 대비",
};

export function selectCycleMapCheckpoints(points: CyclePoint[]): CyclePoint[] {
  const indexes = [points.length - 7, points.length - 4, points.length - 2, points.length - 1];
  return indexes
    .filter((index, position) => index >= 0 && indexes.indexOf(index) === position)
    .map((index) => points[index]);
}

function nextPhase(phase?: Phase | null): Phase | null {
  if (!phase) return null;
  const index = PHASE_ORDER.indexOf(phase);
  return index >= 0 ? PHASE_ORDER[(index + 1) % PHASE_ORDER.length] : null;
}

export function resolveMapDirectionPhase(
  monitor?: TransitionMonitor | null,
  observedPhase?: Phase | null,
): Phase | null {
  return monitor?.current_transition?.target_phase || nextPhase(observedPhase);
}

export type CycleRouteTransition = {
  from: Phase;
  to: Phase;
  status: "WATCH" | "CONFIRMED";
  source?: "FORECAST";
};

export function resolveCycleRouteTransition(
  monitor: TransitionMonitor | null | undefined,
  currentPhase: Phase | null | undefined,
  forecast?: TransitionForecast | null,
): CycleRouteTransition | null {
  if (
    forecast?.status === "READY"
    && currentPhase
    && forecast.current_phase === currentPhase
    && forecast.destination.primary_phase !== currentPhase
  ) {
    return {
      from: currentPhase,
      to: forecast.destination.primary_phase,
      status: "WATCH",
      source: "FORECAST",
    };
  }
  const current = monitor?.current_transition;
  if (current && current.from_phase !== current.target_phase) {
    return {
      from: current.from_phase,
      to: current.target_phase,
      status: current.status,
    };
  }
  if (!monitor || monitor.status === "MAINTAIN") return null;
  if (monitor.status === "CONFIRMED") {
    const from = monitor.anchor_phase;
    const to = monitor.target_phase;
    return from && to && from !== to ? { from, to, status: "CONFIRMED" } : null;
  }
  if (monitor.status !== "WATCH") return null;
  const to = resolveMapDirectionPhase(monitor, currentPhase);
  return currentPhase && to && currentPhase !== to
    ? { from: currentPhase, to, status: "WATCH" }
    : null;
}

function routePath(from: Phase, to: Phase): string {
  const registered = CYCLE_ROUTE_ARCS[`${from}:${to}`];
  if (registered) return registered;
  const start = CYCLE_ROUTE_NODES[from];
  const end = CYCLE_ROUTE_NODES[to];
  const midpointX = (start.x + end.x) / 2;
  const midpointY = (start.y + end.y) / 2;
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const length = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
  const offset = 28;
  const controlX = midpointX - (dy / length) * offset;
  const controlY = midpointY + (dx / length) * offset;
  return `M${start.x} ${start.y} Q${controlX.toFixed(1)} ${controlY.toFixed(1)} ${end.x} ${end.y}`;
}

export function summarizeCycleRouteHistory(points: CyclePoint[]): string {
  const checkpoints = selectCycleMapCheckpoints(points);
  if (!checkpoints.length) return "과거 이력 부족";
  const prefix = points.length >= 7 ? "최근 6개월" : "조회 가능한 기간";
  const first = checkpoints[0].phase;
  const current = checkpoints[checkpoints.length - 1].phase;
  if (checkpoints.every((point) => point.phase === current)) {
    return `${prefix} · ${PHASE_LABEL[current]} 유지`;
  }
  if (first === current) return `${prefix} · ${PHASE_LABEL[current]} 국면 내 변동`;
  return `${prefix} · ${PHASE_LABEL[first]}에서 ${PHASE_LABEL[current]}으로 변화`;
}

const RECENT_ROLE: Record<number, string> = {
  1: "최신 변화 감지",
  3: "방향 확인",
  6: "현재 국면의 배경",
};
const CONDITION_LABEL: Record<TransitionCondition["condition_id"], string> = {
  persistence: "지속성",
  diffusion: "확산도",
  corroboration: "활동·고용 동반 확인",
};

function CurrentObservedState({ state, recent }: { state: ObservedState; recent: RecentChange[] }) {
  const phase = state.phase;
  return (
    <section className="observed-state-section" aria-labelledby="observed-state-title">
      <div className="section-heading">
        <div><span>Observed state</span><h3 id="observed-state-title">현재 관측 국면</h3></div>
        <small>정식 월말 실물 데이터로 계산한 현재 위치</small>
      </div>
      <div className="observed-state-layout">
        <article className={`observed-state-card ${phase ? `phase-${phase}` : "phase-missing"}`}>
          <div className="observed-state-phase">
            <span>현재 국면</span>
            <strong>{phase ? PHASE_LABEL[phase] : "판단 불가"}</strong>
            <p>경기 수준과 최근 3개월 변화 속도를 함께 본 상대 성장순환 위치입니다.</p>
          </div>
          <dl className="observed-state-metrics">
            <div><dt>경기 수준</dt><dd>{state.level == null ? "-" : formatSignedScore(state.level)}</dd></div>
            <div><dt>3개월 모멘텀</dt><dd>{state.momentum == null ? "-" : formatSignedScore(state.momentum)}</dd></div>
            <div><dt>국면 지속</dt><dd>{state.duration_months == null ? "-" : `${state.duration_months}개월`}</dd></div>
            <div><dt>판단 신뢰도</dt><dd>{state.confidence_label || "제한"}</dd></div>
            <div><dt>수정 민감도</dt><dd>{state.revision_sensitivity_label || "비교 불가"}</dd></div>
            <div><dt>실물 커버리지</dt><dd>{state.available_series == null ? "-" : `${state.available_series}/8`}</dd></div>
          </dl>
        </article>
        <div className="recent-change-block">
          <header><div><span>Recent changes</span><h4>최근 1·3·6개월 변화</h4></div><small>강화·약화의 속도와 확산을 분리</small></header>
          <div className="recent-change-grid">
            {recent.length ? recent.map((item) => (
              <article className={`recent-change-card change-${item.status.toLowerCase()}`} key={item.horizon_months}>
                <header><span>{item.label}</span><b>{item.status_label}</b></header>
                <strong>{RECENT_ROLE[item.horizon_months]}</strong>
                <p>종합 변화 {item.composite_delta == null ? "-" : formatSignedScore(item.composite_delta)}</p>
                <small>같은 방향 지표 {formatRatio(item.breadth)} · {item.available_pairs ?? 0}/8개 비교</small>
              </article>
            )) : <p className="empty-copy">최근 변화를 계산할 자료가 아직 없습니다.</p>}
          </div>
        </div>
      </div>
    </section>
  );
}

function IntramonthChangePanel({ intramonth }: { intramonth: IntramonthChange }) {
  const latestSourceDate = (intramonth.source_coverage.series || [])
    .map((item) => item.latest_observation_date || "")
    .filter(Boolean)
    .sort()
    .at(-1) || null;
  const coverage = intramonth.source_coverage;
  const coverageLabel = coverage.requested_series != null
    ? `${coverage.available_series ?? 0}/${coverage.requested_series}개 원천`
    : "원천 범위 확인 중";
  const provisionalPhase = intramonth.observed_state?.phase;
  return (
    <section className="intramonth-change-panel" aria-labelledby="intramonth-change-title">
      <div className="section-heading">
        <div><span>Provisional update</span><h3 id="intramonth-change-title">월말 이후 잠정 변화</h3></div>
        <small>새로 입수된 정보이며 정식 월말 국면을 바꾸지 않습니다</small>
      </div>
      <div className="intramonth-change-grid">
        <article><span>비교 기준</span><strong>{intramonth.baseline_as_of_date}</strong><small>정식 월말</small></article>
        <article><span>잠정 계산일</span><strong>{intramonth.as_of_date}</strong><small>{provisionalPhase ? `${PHASE_LABEL[provisionalPhase]} 좌표` : "좌표 판단 제한"}</small></article>
        <article><span>실물 종합 변화</span><strong>{intramonth.raw_level_delta == null ? "-" : formatSignedScore(intramonth.raw_level_delta)}</strong><small>월말 대비 raw level</small></article>
        <div className="intramonth-factor-deltas">
          {intramonth.factor_deltas.map((item) => (
            <span key={item.factor}>{FACTOR_LABEL[item.factor] || item.factor}<strong className={item.delta > 0 ? "delta-up" : item.delta < 0 ? "delta-down" : "delta-flat"}>{formatSignedScore(item.delta)}</strong></span>
          ))}
        </div>
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

function CycleRouteMap({ payload }: { payload: CyclePayload }) {
  const currentPhase = payload.observed_state.phase;
  const transition = resolveCycleRouteTransition(
    payload.transition_monitor,
    currentPhase,
    payload.transition_forecast,
  );
  const activeRoutePath = transition ? routePath(transition.from, transition.to) : null;
  const historySummary = summarizeCycleRouteHistory(payload.cycle_map.points);
  const currentLabel = currentPhase ? PHASE_LABEL[currentPhase] : "판단 제한";
  const forecast = payload.transition_forecast;
  const statusCopy = transition && activeRoutePath
    ? transition.source === "FORECAST" && forecast
      ? `${PHASE_LABEL[transition.from]} → ${PHASE_LABEL[transition.to]} 가장 유력 · 전환 시 ${formatRatio(forecast.destination.probabilities[transition.to])}`
      : transition.status === "WATCH"
      ? `${PHASE_LABEL[transition.from]} → ${PHASE_LABEL[transition.to]} 방향 관찰 · 예측 아님`
      : `${PHASE_LABEL[transition.from]} → ${PHASE_LABEL[transition.to]} 국면 전환 확인`
    : payload.transition_monitor?.status === "MAINTAIN"
      ? "현재 국면 유지"
      : transition
        ? "인접하지 않은 전환 경로 · 상세 조건 확인"
        : payload.transition_monitor
          ? "전환 경로 관찰 전"
          : "전환 자료 부족";

  return (
    <section className="cycle-map-panel" aria-labelledby="cycle-map-title">
      <div className="section-heading">
        <div><span>Cycle route</span><h3 id="cycle-map-title">순환 경로로 본 현재 위치</h3></div>
        <small>{forecast ? "현재 국면과 모델이 비교한 다음 국면" : "현재 국면과 구조적 다음 인접 국면"}</small>
      </div>
      <div className="cycle-map-body">
        <svg
          className="cycle-route-map"
          viewBox="0 0 320 320"
          role="group"
          aria-label={`경제사이클 순환 경로 · 현재 관측 ${currentLabel} · ${statusCopy}`}
        >
          <defs>
            <marker id="cycle-route-watch-arrowhead" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
              <path d="M0,0 L7,3.5 L0,7 Z" />
            </marker>
            <marker id="cycle-route-confirmed-arrowhead" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
              <path d="M0,0 L7,3.5 L0,7 Z" />
            </marker>
          </defs>
          {Object.entries(CYCLE_ROUTE_ARCS).map(([key, path]) => (
            <path className="cycle-route-track" d={path} key={`route-track-${key}`} />
          ))}
          {transition && activeRoutePath ? (
            <path
              className={`cycle-route-direction route-${transition.status.toLowerCase()}`}
              d={activeRoutePath}
              markerEnd={`url(#cycle-route-${transition.status.toLowerCase()}-arrowhead)`}
              role="img"
              aria-label={statusCopy}
            />
          ) : null}
          {PHASE_ORDER.map((phase) => {
            const node = CYCLE_ROUTE_NODES[phase];
            const isCurrent = currentPhase === phase;
            const isNext = transition?.to === phase;
            const noteY = node.labelY > node.y ? node.y - 27 : node.y + 34;
            return (
              <g className="cycle-route-node" key={phase}>
                <circle
                  className={`cycle-route-node-core route-phase-${phase}${isCurrent ? " cycle-route-node-current" : ""}${isNext ? " cycle-route-node-next" : ""}`}
                  cx={node.x}
                  cy={node.y}
                  r={isCurrent ? 17 : isNext ? 14 : 11}
                />
                <text className="cycle-route-node-label" x={node.labelX} y={node.labelY}>{PHASE_LABEL[phase]}</text>
                {isCurrent ? <text className="cycle-route-node-note" x={node.x} y={noteY}>현재</text> : null}
                {!isCurrent && isNext ? <text className="cycle-route-node-note" x={node.x} y={noteY}>{forecast ? "가장 유력" : "다음 확인"}</text> : null}
              </g>
            );
          })}
          <g className="cycle-route-center">
            <text x="160" y="151">현재 관측 {currentLabel}</text>
            <text x="160" y="172">{payload.observed_state.duration_months ? `${payload.observed_state.duration_months}개월 지속` : "지속 기간 확인 중"}</text>
          </g>
        </svg>
        <strong className={`cycle-route-status route-status-${transition?.status.toLowerCase() || "limited"}`}>{statusCopy}</strong>
        <span className="cycle-route-history">{historySummary}</span>
        <p>{forecast
          ? "화살표는 전환이 발생할 경우 가장 유력한 다음 국면입니다. 정확한 전환 월을 뜻하지 않으며 다른 국면도 함께 비교합니다."
          : "화살표는 현재 확인 중인 구조적 인접 국면을 나타내며, 특정 시점의 이동이나 발생 확률을 예측하지 않습니다."}</p>
      </div>
    </section>
  );
}

function TransitionForecastPanel({ forecast, state }: { forecast: TransitionForecast; state: ObservedState }) {
  const primary = forecast.destination.primary_phase;
  const alternatives = forecast.destination.alternatives;
  const pressurePercent = Math.round(forecast.pressure.probability * 100);
  return (
    <section className={`transition-panel forecast-pressure-${forecast.pressure.level.toLowerCase()}`} aria-labelledby="transition-title">
      <div className="section-heading">
        <div><span>Transition outlook</span><h3 id="transition-title">현재 진단과 향후 방향</h3></div>
        <b>전환압력 {pressurePercent}% · {forecast.pressure.level_label}</b>
      </div>
      <div className="transition-summary-grid forecast-summary-grid">
        <article><span>현재 공식 국면</span><strong>{forecast.current_phase_label}{state.duration_months ? ` · ${state.duration_months}개월` : ""}</strong><small>{state.as_of_date || "기준일 확인 중"} · 2회 연속 확인 기준</small></article>
        <article><span>가까운 발표의 전환압력</span><strong>전환압력 {pressurePercent}%</strong><small>다음 {forecast.pressure.horizon_releases}개 유효 발표 안의 보정 확률</small></article>
        <article><span>전환 시 다음 국면</span><strong>{forecast.destination.primary_phase_label} {Math.round(forecast.destination.probabilities[primary] * 100)}%</strong><small>현재 국면을 제외한 조건부 비교</small></article>
        <article><span>모든 대안 비교</span><strong>{alternatives.map((item) => `${item.phase_label} ${Math.round(item.probability * 100)}%`).join(" · ")}</strong><small>고정 순환 순서를 강제하지 않음</small></article>
      </div>
      <div className="transition-route forecast-route" aria-label={`${forecast.current_phase_label}에서 ${forecast.destination.primary_phase_label} 예측 경로`}>
        <article className={`phase-${forecast.current_phase}`}><span>현재 공식 관측</span><strong>{forecast.current_phase_label}</strong><small>confirmed RTDSM 국면</small></article>
        <i aria-hidden="true">→</i>
        <article className={`phase-${primary}`}><span>현재 데이터에서 가장 유력</span><strong>{forecast.destination.primary_phase_label}</strong><small>전환 발생 조건부 {Math.round(forecast.destination.probabilities[primary] * 100)}%</small></article>
      </div>
      <p className="transition-boundary"><strong>{forecast.pressure.summary}</strong> {forecast.boundary}</p>
      <div className="transition-condition-heading"><strong>무엇이 전환압력을 움직이고 있나</strong><span>현재값의 모델 기여도 상위 6개</span></div>
      <div className="forecast-driver-grid">
        {forecast.drivers.slice(0, 6).map((driver) => (
          <article className={`driver-${driver.current_effect.toLowerCase()}`} key={driver.driver_id}>
            <header><span>{driver.label}</span><b>{driver.current_effect_label}</b></header>
            <strong>{driver.signal_group === "PHASE_CONTEXT" ? forecast.current_phase_label : `${driver.value > 0 ? "+" : ""}${driver.value.toFixed(2)}`}</strong>
            <small>{driver.signal_group === "PHASE_CONTEXT"
              ? "현재 국면에서 과거에 관측된 전환 빈도를 반영"
              : driver.higher_value_effect === "RAISES_PRESSURE"
              ? "이 값이 더 오르면 전환압력을 높이는 모델 방향"
              : driver.higher_value_effect === "LOWERS_PRESSURE"
                ? "이 값이 더 오르면 전환압력을 낮추는 모델 방향"
                : "추가 변화가 전환압력에 미치는 영향은 중립"}</small>
          </article>
        ))}
      </div>
      <p className="forecast-method-note">정책·물가·금리·신용·주택 지표는 전환 가능성을 계산하고, 실물 수준·모멘텀·확산도는 전환 후 가장 그럴듯한 국면을 비교합니다.</p>
    </section>
  );
}

function TransitionPanel({
  monitor,
  forecast,
  state,
  recent,
  intramonth,
}: {
  monitor?: TransitionMonitor | null;
  forecast?: TransitionForecast | null;
  state: ObservedState;
  recent: RecentChange[];
  intramonth?: IntramonthChange | null;
}) {
  if (forecast?.status === "READY") {
    return <TransitionForecastPanel forecast={forecast} state={state} />;
  }
  if (!monitor) {
    return <section className="transition-panel"><div className="section-heading"><div><span>Current transition</span><h3>현재 진단과 다음 확인</h3></div></div><p className="empty-copy">전환 조건을 계산할 자료가 아직 없습니다.</p></section>;
  }
  const observedPhase = monitor.observed_phase || state.phase;
  const current = monitor.current_transition;
  const fromPhase = current?.from_phase || observedPhase;
  const fromLabel = current?.from_phase_label || (fromPhase ? PHASE_LABEL[fromPhase] : "판단 불가");
  const targetPhase = current?.target_phase || nextPhase(fromPhase);
  const targetLabel = current?.target_phase_label || (targetPhase ? PHASE_LABEL[targetPhase] : "확인 대상 없음");
  const conditions = current?.conditions || monitor.conditions;
  const conditionsMet = current?.conditions_met ?? monitor.conditions_met;
  const conditionsTotal = current?.conditions_total ?? monitor.conditions_total;
  const transitionStatus = current?.status || (monitor.status === "CONFIRMED" ? "CONFIRMED" : "WATCH");
  const transitionStatusLabel = current?.status_label || monitor.status_label;
  const oneMonth = recent.find((item) => item.horizon_months === 1);
  const threeMonth = recent.find((item) => item.horizon_months === 3);
  const recentLabel = [
    oneMonth ? `1개월 ${oneMonth.status_label}` : null,
    threeMonth ? `3개월 ${threeMonth.status_label}` : null,
  ].filter(Boolean).join(" · ") || "방향 자료 부족";
  const anchorLabel = monitor.anchor_phase ? PHASE_LABEL[monitor.anchor_phase] : "-";
  const anchorHistoryLabel = monitor.anchor_source === "LEGACY_OBSERVED"
    ? "미확정 이력"
    : monitor.anchor_source === "CONFIRMED"
      ? "확인된 이력"
      : monitor.anchor_source_label || "기준 상태";
  const showSecondaryAnchor = Boolean(
    monitor.anchor_phase
    && (monitor.anchor_phase !== fromPhase || monitor.target_phase !== targetPhase),
  );
  const intramonthPhase = intramonth?.observed_state?.phase;
  return (
    <section className={`transition-panel transition-${transitionStatus.toLowerCase()}`} aria-labelledby="transition-title">
      <div className="section-heading">
        <div><span>Current transition</span><h3 id="transition-title">현재 진단과 다음 확인</h3></div>
        <b>{transitionStatusLabel} · {conditionsMet}/{conditionsTotal}</b>
      </div>
      <div className="transition-summary-grid">
        <article><span>정식 월말 국면</span><strong>{fromLabel}{state.duration_months ? ` · ${state.duration_months}개월` : ""}</strong><small>{state.as_of_date || "기준일 확인 중"}</small></article>
        <article><span>최근 방향</span><strong>{recentLabel}</strong><small>월말 관측값 기준</small></article>
        <article><span>다음 확인 국면</span><strong>{targetLabel}</strong><small>현재 국면에 인접한 다음 상태</small></article>
        <article><span>전환 근거</span><strong>{conditionsMet}/{conditionsTotal} 충족</strong><small>{transitionStatusLabel}</small></article>
      </div>
      <div className="transition-route" aria-label={`${fromLabel}에서 ${targetLabel} 전환 확인 경로`}>
        <article className={`phase-${fromPhase || "missing"}`}><span>현재 공식 관측</span><strong>{fromLabel}</strong><small>조건이 확인될 때까지 유지</small></article>
        <i aria-hidden="true">→</i>
        <article className={`phase-${targetPhase || "missing"}`}><span>다음에 확인할 인접 국면</span><strong>{targetLabel}</strong><small>시점·확률 예측 아님</small></article>
      </div>
      {intramonth ? (
        <div className="transition-provisional">
          <span>월중 잠정 변화 · {intramonth.as_of_date}</span>
          <strong>{intramonthPhase ? PHASE_LABEL[intramonthPhase] : "판단 제한"} 좌표 · {intramonth.raw_level_delta == null ? "-" : formatSignedScore(intramonth.raw_level_delta)}</strong>
          <small>정식 월말 판정 유지</small>
        </div>
      ) : null}
      <p className="transition-boundary"><strong>현재 {fromLabel} 유지</strong> · {targetLabel} 전환 여부를 먼저 확인합니다. 다음 국면은 발생 확률이 아니라 확인 순서를 뜻합니다.</p>
      <div className="transition-condition-heading"><strong>{fromLabel} → {targetLabel} 확인 조건</strong><span>{conditionsMet}/{conditionsTotal} 충족</span></div>
      <div className="transition-condition-grid">
        {conditions.map((condition) => (
          <article className={`condition-${condition.status.toLowerCase()}`} key={condition.condition_id}>
            <header><span>{condition.label || CONDITION_LABEL[condition.condition_id]}</span><b>{condition.status === "MET" ? "충족" : condition.status === "UNAVAILABLE" ? "자료 부족" : "미충족"}</b></header>
            <dl>
              <div><dt>현재값</dt><dd>{condition.value_label || (condition.status === "UNAVAILABLE" ? "자료 부족" : "계산값 확인 중")}</dd></div>
              <div><dt>충족 기준</dt><dd>{condition.threshold_label || condition.threshold || "다음 정식 발표에서 재확인"}</dd></div>
            </dl>
          </article>
        ))}
      </div>
      {showSecondaryAnchor ? (
        <div className="transition-anchor-secondary">
          <span>이전 모델 기준 · 보조 정보</span>
          <strong>{anchorLabel} 앵커 · {formatKoreanMonth(monitor.anchor_started_at)} · {anchorHistoryLabel}</strong>
          <small>현재 판단 경로에는 사용하지 않으며, 과거 상태 기록의 맥락으로만 표시합니다.</small>
          {monitor.context.length ? (
            <div className="transition-context"><strong>이전 모델 보조 맥락</strong>{monitor.context.map((item) => <span key={item.factor}>{FACTOR_LABEL[item.factor] || item.factor} · {item.relation_label}</span>)}</div>
          ) : null}
        </div>
      ) : null}
      {!showSecondaryAnchor && monitor.context.length ? (
        <div className="transition-context"><strong>보조 맥락</strong>{monitor.context.map((item) => <span key={item.factor}>{FACTOR_LABEL[item.factor] || item.factor} · {item.relation_label}</span>)}</div>
      ) : null}
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
  const freshnessLabel = evaluation.freshness === "DELAYED"
    ? `갱신 지연 · 마지막 확인 ${evaluation.as_of_date || evaluation.release_date || "-"}`
    : SERIES_FRESHNESS_LABEL[evaluation.freshness];
  const details = <>
    {changes.map(([key, value]) => (
      <span key={key}>{CHANGE_LABEL[key] || key} {formatSeriesChange(value, evaluation.unit)}</span>
    ))}
    <span>기준일 {evaluation.as_of_date || evaluation.release_date || "-"}</span>
    <span>최신성 {freshnessLabel}</span>
  </>;
  return (
    <div className="series-metrics" data-status={evaluation.freshness} tabIndex={0}>
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
  const statusLabel = price.freshness === "DELAYED"
    ? "갱신 지연"
    : PRICE_STATUS_LABEL[price.status];
  return (
    <section className="price-pathway" data-status={price.freshness || "UNAVAILABLE"}>
      <header>
        <h5>현재 움직임</h5>
        <b className={`price-status ${price.freshness === "DELAYED" ? "price-delayed" : `price-${price.status.toLowerCase()}`}`}>
          {statusLabel}
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
      {hasRateUnit ? <p className="movement-unit-note">현재 값은 마지막 저장 관측치이며, 금리 변화는 bp 기준입니다.</p> : null}
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
                supports_current_signal: row.supports_current_signal,
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
          const statusLabel = pathway.status === "DELAYED"
            ? PATHWAY_STATUS_LABEL.DELAYED
            : pathway.status === "UNAVAILABLE"
              ? PATHWAY_STATUS_LABEL.UNAVAILABLE
              : PATHWAY_STATUS_LABEL.OBSERVED;
          return (
            <article className={`pathway-item pathway-${String(pathway.status).toLowerCase()}`} key={pathway.pathway_id}>
              <header><strong>{pathway.label}</strong><span>{statusLabel}</span></header>
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
  const summary = item.summary || item.narrative || item.context;
  const interpretation = item.current_interpretation?.length ? item.current_interpretation : [item.narrative || item.summary || item.context];
  const nextChecks = item.next_check_conditions?.length
    ? item.next_check_conditions
    : ["다음 월의 가격과 관찰 경로가 같은 방향을 유지하는지 확인합니다."];
  return (
    <article className="implication-card is-connected" data-status={item.data_status} tabIndex={0}>
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
      <p className="implication-summary">{summary}</p>
      <EconomicStateBlock state={item.economic_state} />
      {item.assets?.length ? (
        <div className="commodity-asset-grid">
          {item.assets.map((asset) => (
            <article className="commodity-asset-card" data-status={asset.data_status} key={asset.asset_id}>
              <header><strong>{asset.label}</strong><span className={`coverage-status coverage-${asset.coverage.toLowerCase()}`}>{COVERAGE_LABEL[asset.coverage]}</span></header>
              <p>{asset.summary || asset.narrative}</p>
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

function RegimeRibbon({ points }: { points: CyclePoint[] }) {
  const ribbonStyle: RibbonStyle = {
    "--history-month-count": Math.max(points.length, 1),
  };
  return (
    <section className="ribbon-section" aria-labelledby="ribbon-title">
      <div className="section-heading"><div><span>Observed phase ribbon</span><h3 id="ribbon-title">최근 12개월 국면 흐름</h3></div><small>실제 관측 국면 · NBER 이력은 별도 음영</small></div>
      <div className="ribbon-legend">
        <span className="legend-recovery">회복</span>
        <span className="legend-expansion">확장</span>
        <span className="legend-slowdown">둔화</span>
        <span className="legend-contraction">위축</span>
        <span className="nber-recession">NBER 침체 이력</span>
      </div>
      <div className="regime-ribbon" role="list" aria-label="최근 월별 관측 경제 국면" style={ribbonStyle}>
        {points.length ? points.map((item, index) => (
          <div className={`ribbon-month phase-${item.phase}`} role="listitem" tabIndex={0} key={`${item.date}-${index}`} aria-label={`${formatKoreanMonth(item.date)} · ${PHASE_LABEL[item.phase]} · NBER ${item.nber_recession ? "침체" : "비침체"}`}>
            {item.nber_recession ? <i className="nber-recession" aria-label="NBER 침체" /> : null}
            {index === points.length - 1 ? <i className="current-marker" aria-label="현재" /> : null}
            <div className="ribbon-tooltip" role="tooltip">
              <strong>{formatKoreanMonth(item.date)} · {PHASE_LABEL[item.phase]}</strong>
              <span>NBER {item.nber_recession ? "침체" : "비침체"}</span>
              <span>판단 신뢰도 {CONFIDENCE_LABEL[item.confidence || ""] || "확인 불가"}</span>
              <span>수정 민감도 {REVISION_SENSITIVITY_LABEL[item.revision_sensitivity || ""] || "확인 불가"}</span>
            </div>
          </div>
        )) : (
          <div className="ribbon-month ribbon-empty-history phase-missing" role="listitem" aria-label="과거 경제사이클 이력 없음" />
        )}
      </div>
      <div className="ribbon-axis"><span>{formatMonth(points[0]?.date)}</span><span>{formatMonth(points[Math.floor(points.length / 2)]?.date)}</span><span>현재</span></div>
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
          <article className="guide-phase-contraction">
            <span>위축 신호</span>
            <strong>성장 레벨과 모멘텀이 함께 약함</strong>
            <p>상대 성장순환의 위축을 뜻하며 NBER 공식 침체와 같지 않습니다. 실물 약화의 범위와 지속성을 확인합니다.</p>
          </article>
        </div>

        <section className="cycle-guide-transitions" aria-labelledby="cycle-guide-transition-title">
          <h4 id="cycle-guide-transition-title">국면 전환은 이렇게 읽습니다</h4>
          <div className="cycle-guide-transition-grid">
            <article><strong>위축 → 회복</strong><p>바닥 통과의 초기 신호로 읽고 지속성을 확인합니다.</p></article>
            <article><strong>회복 → 확장</strong><p>기대 개선이 실제 생산·고용·이익으로 이어지는지 확인합니다.</p></article>
            <article><strong>확장 → 둔화</strong><p>건전한 정상화인지 여러 지표의 동반 약화인지 구분합니다.</p></article>
            <article><strong>둔화 → 위축</strong><p>약화가 일시적 충격을 넘어 넓고 오래 지속되는지 확인합니다.</p></article>
          </div>
        </section>

        <p className="cycle-guide-boundary">
          참고: 전형적 순환의 해석 예시이며 실제 예측 순서를 강제하지 않습니다. NBER의 공식 경기판정이나 개별 행동 지시도 아닙니다.
        </p>
      </div>
    </details>
  );
}

function EconomicCycleFreshnessBar({
  freshness,
  result,
}: {
  freshness?: EconomicCycleFreshness;
  result?: RefreshResult;
}) {
  const [collecting, setCollecting] = useState(false);
  if (!freshness && !result) return null;

  const action = freshness?.action;
  const cycleScope = freshness?.cycle_snapshot;
  const assetScope = freshness?.asset_pathways;
  const scopeCopy = cycleScope || assetScope
    ? [
        cycleScope?.status === "READY"
          ? "경제사이클 계산 최신"
          : cycleScope?.message || "경제사이클 계산 갱신 필요",
        assetScope?.status === "READY"
          ? "자산 경로 최신"
          : assetScope?.message || "자산 경로 갱신 필요",
      ].filter(Boolean).join(" · ")
    : null;
  const handleRefresh = () => {
    if (!action?.enabled || collecting) return;
    setCollecting(true);
    Streamlit.setComponentValue({
      event: {
        id: "refresh_economic_cycle_data",
        nonce: `${Date.now()}`,
      },
    });
  };

  return (
    <section
      className="cycle-freshness-bar"
      data-status={freshness?.overall_status || freshness?.status || result?.status || "READY"}
      aria-live="polite"
    >
      <div className="cycle-freshness-copy">
        <span>DATA FRESHNESS</span>
        <strong>
          {scopeCopy || (freshness?.status === "READY"
            ? `최신 계산 기준 ${freshness.persisted_as_of_date || freshness.target_as_of_date || "-"}`
            : freshness?.message || "경제사이클 최신 자료를 확인할 수 있습니다.")}
        </strong>
        <div className="cycle-freshness-meta">
          <span>마지막 성공 수집 <b>{freshness?.last_successful_collection_at || "기록 없음"}</b></span>
          <span>계산 기준일 <b>{freshness?.persisted_as_of_date || "없음"}</b></span>
          <span>사용 원천 최신일 <b>{assetScope?.latest_observation_date || freshness?.latest_source_observation_date || "확인 불가"}</b></span>
        </div>
        {result ? (
          <small className={`cycle-refresh-result result-${result.status}`}>
            {result.message}
          </small>
        ) : null}
      </div>
      {action?.enabled ? (
        <button
          className="cycle-freshness-action"
          type="button"
          disabled={collecting}
          onClick={handleRefresh}
        >
          {collecting
            ? "필요한 자료만 확인하는 중"
            : "최신 데이터 반영"}
        </button>
      ) : null}
    </section>
  );
}

function EconomicCycleContent({ payload }: { payload: CyclePayload }) {
  const observed = payload.observed_state;
  const realEvidence = payload.evidence.filter((evidence) => evidence.group === "real_economy");
  const forecastEvidence = payload.evidence.filter((evidence) => evidence.group === "forecast_context");
  const estimateTone =
    observed.data_status === "READY"
      ? "positive"
      : observed.data_status === "LIMITED"
        ? "caution"
        : "neutral";
  return (
    <main className="cycle-workbench" data-status={payload.status}>
      <EconomicCycleHero
        asOfDate={payload.as_of_date || "-"}
        estimateLabel={observed.confidence_label || "판단 제한"}
        estimateTone={estimateTone}
        hasIntramonth={Boolean(payload.intramonth_change)}
        summary={payload.headline?.summary || "저장된 경제사이클 결과를 확인합니다."}
        title={payload.headline?.phase_label || "판단 불가"}
      />

      <EconomicCycleFreshnessBar
        freshness={payload.data_freshness}
        result={payload.refresh_result}
      />

      <CurrentObservedState state={observed} recent={payload.recent_changes} />

      {payload.intramonth_change ? <IntramonthChangePanel intramonth={payload.intramonth_change} /> : null}

      <div className="cycle-layout">
        <CycleRouteMap payload={payload} />
        <TransitionPanel
          monitor={payload.transition_monitor}
          forecast={payload.transition_forecast}
          state={observed}
          recent={payload.recent_changes}
          intramonth={payload.intramonth_change}
        />
      </div>

      <section className="evidence-panel" aria-labelledby="evidence-title">
        <div className="section-heading"><div><span>Evidence</span><h3 id="evidence-title">현재 국면과 전환의 판단 근거</h3></div><small>현재 국면을 바꾸는 실물 근거와 보조 맥락을 구분</small></div>
        <div className="evidence-overview-grid">
          <EvidenceGroup title="현재 위치의 근거" subtitle="현재점에 반영되는 생산·소비와 고용·소득" rows={realEvidence} />
          <EvidenceGroup title="전환을 해석할 참고 맥락" subtitle="현재 국면을 바꾸지 않고 전환 조건을 해석하는 금융·선행·물가·정책 정보" rows={forecastEvidence} />
        </div>
      </section>

      <RegimeRibbon points={payload.cycle_map.points} />

      <section className="market-implications" aria-labelledby="implication-title">
        <div className="section-heading"><div><span>Measured market pathways</span><h3 id="implication-title">자산별 확인 포인트</h3></div><small>경제 상태·측정 경로·실제 가격을 분리해 확인</small></div>
        <div className="implication-grid">
          {payload.market_implications.map((item) => <MarketImplicationCard key={item.asset_group} item={item} />)}
        </div>
      </section>

      <MonthlySignalGuide />

      <details className="method-disclosure">
        <summary>방법론과 품질</summary>
        <div className="method-grid"><div><span>모델 버전</span><strong>{payload.model_version || "-"}</strong></div><div><span>기준일</span><strong>{payload.as_of_date || "-"}</strong></div><div><span>판단 신뢰도</span><strong>{observed.confidence_label || "판단 제한"}</strong></div></div>
        <p>{payload.transition_forecast
          ? "현재 국면은 confirmed RTDSM 실물지표로 확정합니다. 전환압력은 다음 3개 유효 발표 안의 전환 가능성이고, 다음 국면 분포는 전환 발생을 조건으로 모든 대안 국면을 비교합니다. 특정 전환 월이나 고정 순환 순서를 강제하지 않습니다."
          : "현재 국면은 월말 point-in-time 실물지표의 수준과 3개월 모멘텀으로 계산합니다. 전환 카드는 특정 월을 예측하지 않고 다음 정식 발표에서 확인할 조건을 보여줍니다."} 금·달러 가격은 저장된 연속선물 일봉이라 계약 교체 효과가 포함될 수 있습니다. 이 결과는 NBER의 공식 경기판정이 아니고 수익률 예측이나 매매 지시가 아닙니다.</p>
        <ul>{payload.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
      </details>
    </main>
  );
}

export function EconomicCycleWorkbenchView({
  payload,
  onCommand = () => undefined,
}: {
  payload: CyclePayload;
  onCommand?: (command: InflationPolicyCommand) => void;
}) {
  const [selectedView, setSelectedView] = useState<"cycle" | "inflation">("cycle");
  const inflationPayload = payload.inflation_policy;
  return (
    <div className="cycle-workbench-shell">
      {inflationPayload ? (
        <nav className="cycle-inner-navigation" role="tablist" aria-label="경제 분석 보기">
          <button
            type="button"
            role="tab"
            aria-selected={selectedView === "cycle"}
            onClick={() => setSelectedView("cycle")}
          >
            경기 국면
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={selectedView === "inflation"}
            onClick={() => setSelectedView("inflation")}
          >
            물가·정책 경로
          </button>
        </nav>
      ) : null}
      {selectedView === "inflation" && inflationPayload ? (
        <InflationPolicyWorkbench payload={inflationPayload} onCommand={onCommand} />
      ) : (
        <EconomicCycleContent payload={payload} />
      )}
    </div>
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
  if (!payload || payload.schema_version !== "economic_cycle_v3") return null;
  const handleCommand = (command: InflationPolicyCommand) => {
    Streamlit.setComponentValue({ event: command });
  };
  return (
    <section className="cycle-workbench-frame" ref={rootRef}>
      <EconomicCycleWorkbenchView payload={payload} onCommand={handleCommand} />
    </section>
  );
}

export default withStreamlitConnection(EconomicCycleWorkbench);
