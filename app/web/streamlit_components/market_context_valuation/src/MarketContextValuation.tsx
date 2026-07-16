import React, { FormEvent, useEffect, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import TurnaroundAnalysis, { TurnaroundPayload } from "./TurnaroundAnalysis";
import "./style.css";

type NumericMap = Record<string, number>;
type HistoryPeriod = "1y" | "3y" | "5y";
type StockSearchResult = {
  symbol: string;
  name: string;
  exchange?: string;
  cik?: string;
};
type MultiplePoint = {
  month: string;
  trailing_pe: number;
  quality?: string;
  price_basis_date?: string;
  eps_basis_date?: string;
};
type ScenarioHistoryPoint = {
  month: string;
  slot_index?: number;
  status?: "AVAILABLE" | "MISSING";
  reason_code?: string | null;
  actual_spx?: number;
  actual_price?: number;
  lower_spx?: number;
  lower_price?: number;
  baseline_spx?: number;
  baseline_price?: number;
  upper_spx?: number;
  upper_price?: number;
  gap_to_baseline_pct?: number;
  eps_basis_date?: string;
  eps_carried_forward?: boolean;
  sep_release_date?: string;
  real_gdp_pct?: number;
  pce_inflation_pct?: number;
  current_macro_pct?: number;
};
type ScenarioHistory = {
  status?: string;
  reason_code?: string;
  window_months?: number;
  window_years?: number;
  observation_count?: number;
  missing_point_count?: number;
  missing_reason_counts?: Record<string, number>;
  required_history_months?: number;
  available_history_months?: number;
  limitation?: string;
  sep_releases?: string[];
  series?: ScenarioHistoryPoint[];
  timeline?: ScenarioHistoryPoint[];
};
type Scenario = {
  growth_pct?: number;
  projected_eps?: number;
  real_gdp_pct?: number;
  pce_inflation_pct?: number;
  macro_pct?: number;
  company_excess_pct?: number;
  multiple?: number;
  price?: number;
};
type DataFreshness = {
  status?: "READY" | "REFRESH_AVAILABLE" | "PARTIAL" | "BLOCKED" | string;
  expected_price_date?: string;
  price_basis_date?: string | null;
  profile_basis_date?: string | null;
  statement_period_end?: string | null;
  statement_available_at?: string | null;
  gaps?: { scope: string; reason_code: string; repairable: boolean }[];
  action?: {
    id: "refresh_us_stock_data";
    label: string;
    detail?: string;
    symbol: string;
    scopes?: string[];
    enabled: boolean;
  };
};
type CollectionResult = {
  status?: string;
  message?: string;
};
type ValuationPayload = {
  schema_version: string;
  status: "READY" | "NOT_SELECTED" | "COLLECTABLE" | "NOT_APPLICABLE" | "ERROR" | string;
  instrument?: {
    id: string;
    label: string;
    proxy_symbol?: string | null;
    price_label: string;
    multiple_label?: string;
    method_label?: string;
  };
  search?: { query?: string; results?: StockSearchResult[] };
  selection?: {
    symbol?: string;
    name?: string;
    exchange?: string;
    cik?: string;
    latest_price_date?: string;
    eps_basis_date?: string;
  } | null;
  readiness?: { status?: string; reason_code?: string; reason?: string };
  data_freshness?: DataFreshness;
  collection_result?: CollectionResult;
  turnaround_analysis?: TurnaroundPayload;
  recommended_analysis?: "per" | "turnaround" | null;
  basis?: {
    eps_basis?: string;
    spx?: { date?: string; price?: number };
    price?: { price_basis_date?: string; price?: number };
    official_window_months?: number;
    sensitivity_window_months?: number;
  };
  multiple_regime: {
    status?: string;
    bucket?: string;
    current_pe?: number;
    current_z?: number;
    mean_multiple?: number;
    minus_2sigma?: number;
    minus_1sigma?: number;
    plus_1sigma?: number;
    plus_2sigma?: number;
    period_sensitive?: boolean;
    current_is_provisional?: boolean;
    current_price_basis_date?: string;
    current_eps_basis_date?: string;
    latest_complete_pe?: number;
    latest_complete_basis_date?: string;
    sensitivity?: { bucket?: string; current_z?: number };
    series?: MultiplePoint[];
    limitation?: string;
  };
  earnings_scenario: {
    status?: string;
    release_date?: string;
    reason?: string;
    current_ttm_eps?: number;
    eps_source?: string;
    eps_source_quality?: string;
    eps_basis_date?: string;
    fallback_reason?: string;
    real_gdp_pct?: number;
    pce_inflation_pct?: number;
    current_macro_pct?: number;
    company_excess_growth?: { p25_pct?: number; p50_pct?: number; p75_pct?: number; observation_count?: number };
    conservative?: Scenario;
    baseline?: Scenario;
    optimistic?: Scenario;
    scenarios?: { conservative?: Scenario; baseline?: Scenario; optimistic?: Scenario };
    limitation?: string;
  };
  index_scenario: {
    status?: string;
    current_spx?: number;
    current_price?: number;
    spx_scenarios?: NumericMap;
    price_scenarios?: NumericMap;
    gap_pct?: NumericMap;
    current_vs_baseline_gap_pct?: number;
    valuation_position?: string;
    history?: ScenarioHistory;
    history_options?: Record<HistoryPeriod, ScenarioHistory>;
    reason?: string;
    limitation?: string;
  };
  sources?: { name: string; role: string }[];
  limitations?: string[];
};
type CombinedPayload = {
  schema_version: string;
  default_instrument: string;
  show_instrument_selector?: boolean;
  instruments: Record<string, ValuationPayload>;
};
type Props = ComponentProps & { args: { payload?: ValuationPayload | CombinedPayload } };
type AnalysisChoice = "per" | "turnaround";

const n = (value?: number, digits = 1) => value == null || !Number.isFinite(value) ? "-" : value.toLocaleString("ko-KR", { maximumFractionDigits: digits });
const signed = (value?: number, digits = 1) => value == null || !Number.isFinite(value) ? "-" : `${value > 0 ? "+" : ""}${n(value, digits)}%`;
const monthLabel = (value?: string) => value ? value.slice(0, 7).replace("-", ".") : "-";
const bucketLabel: Record<string, string> = { LOW: "상대적 저평가", NEUTRAL: "중립 구간", HIGH: "상대적 고평가", EXTREME_HIGH: "매우 높은 구간" };
const sourceQualityLabel: Record<string, string> = { official_actual: "공식 actual", interpolated_ttm_proxy: "보간 TTM 대체 기준", reconstructed_actual: "SEC actual 재구성" };

function emitEvent(id: string, fields: Record<string, unknown> = {}) {
  Streamlit.setComponentValue({ event: { id, ...fields, nonce: Date.now() } });
}

function pointerIndex(event: React.MouseEvent<SVGSVGElement>, count: number, left: number, width: number, viewWidth: number) {
  const rect = event.currentTarget.getBoundingClientRect();
  const cursor = (event.clientX - rect.left) / rect.width * viewWidth;
  return Math.round(Math.max(0, Math.min(1, (cursor - left) / width)) * Math.max(0, count - 1));
}

function StockSearch({ payload }: { payload: ValuationPayload }) {
  const [query, setQuery] = useState(payload.search?.query || "");
  useEffect(() => setQuery(payload.search?.query || ""), [payload.search?.query]);
  const results = payload.search?.results || [];
  const submit = (event: FormEvent) => {
    event.preventDefault();
    emitEvent("search_us_stock", { query: query.trim() });
  };
  return <section className="stock-search" aria-label="미국 개별주식 검색">
    <form onSubmit={submit}>
      <label htmlFor="us-stock-query">기업명·티커 검색</label>
      <div><input id="us-stock-query" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="예: Apple, AAPL" minLength={2}/><button type="submit">검색</button></div>
      <small>현재 DB에 등록된 SEC CIK 연결 미국 보통주만 검색합니다.</small>
    </form>
    {payload.selection?.symbol ? <div className="stock-selection"><div><span>선택 종목</span><strong>{payload.selection.name || payload.selection.symbol}</strong><small>{payload.selection.symbol} · {payload.selection.exchange || "거래소 확인 중"}</small></div><button type="button" onClick={() => emitEvent("search_us_stock", { query: "" })}>다른 종목 검색</button></div> : null}
    {results.length ? <div className="stock-search-results" role="list">{results.map((result) => <button key={result.symbol} type="button" role="listitem" onClick={() => emitEvent("select_us_stock", { symbol: result.symbol })}><span><strong>{result.symbol}</strong><small>{result.exchange || "-"}</small></span><span>{result.name}</span></button>)}</div> : payload.search?.query && payload.search.query.length >= 2 ? <p className="search-empty">검색 가능한 미국 보통주를 찾지 못했습니다.</p> : null}
  </section>;
}

function StockState({ payload }: { payload: ValuationPayload }) {
  const readiness = payload.readiness || {};
  const statusCopy: Record<string, { title: string; detail: string }> = {
    NOT_SELECTED: { title: "평가할 미국 개별주식을 선택하세요", detail: "기업명 또는 티커를 검색한 뒤 한 종목을 선택하면 DB 자료만으로 먼저 평가 가능 여부를 확인합니다." },
    COLLECTABLE: { title: "가치평가 원자료가 더 필요합니다", detail: readiness.reason || "저장된 가격 또는 SEC 분기 실적에 수집 가능한 누락 구간이 있습니다." },
    NOT_APPLICABLE: { title: "현재 PER 방식으로 평가할 수 없습니다", detail: readiness.reason || "적자, 짧은 상장 이력 또는 주당 단위 문제로 상대 PER 평가가 적용되지 않습니다." },
    ERROR: { title: "가치평가 자료를 확인하지 못했습니다", detail: readiness.reason || "DB identity 또는 저장 자료 구조를 확인해 주세요." },
  };
  const copy = statusCopy[payload.status] || statusCopy.ERROR;
  return <section className={`stock-state stock-state-${payload.status.toLowerCase()}`} aria-live="polite">
    <span>{payload.status.replace("_", " ")}</span><h3>{copy.title}</h3><p>{copy.detail}</p>
    {readiness.reason_code ? <code>{readiness.reason_code}</code> : null}
  </section>;
}

function MultipleChart({ model, isStock }: { model: ValuationPayload["multiple_regime"]; isStock: boolean }) {
  const points = model.series || [];
  const [selected, setSelected] = useState(Math.max(0, points.length - 1));
  useEffect(() => setSelected(Math.max(0, points.length - 1)), [points.length]);
  if (!points.length) return <div className="empty">positive 월별 PER 이력 60개월이 필요합니다.</div>;
  const anchors = [model.minus_2sigma, model.minus_1sigma, model.mean_multiple, model.plus_1sigma, model.plus_2sigma].filter((value): value is number => value != null);
  const values = [...points.map((point) => point.trailing_pe), ...anchors];
  const min = Math.min(...values) * .96, max = Math.max(...values) * 1.04, range = Math.max(1, max - min);
  const left = 54, width = 744, top = 24, height = 240, viewWidth = 920;
  const x = (index: number) => left + index / Math.max(1, points.length - 1) * width;
  const y = (value: number) => top + (max - value) / range * height;
  const path = points.map((point, index) => `${index ? "L" : "M"}${x(index).toFixed(1)},${y(point.trailing_pe).toFixed(1)}`).join(" ");
  const area = `${path} L${x(points.length - 1)},${top + height} L${left},${top + height} Z`;
  const active = points[Math.min(selected, points.length - 1)];
  const completeEndIndex = points.reduce((latest, point, index) => point.quality === "provisional" ? latest : index, -1);
  const completePath = points.slice(0, completeEndIndex + 1).map((point, index) => `${index ? "L" : "M"}${x(index).toFixed(1)},${y(point.trailing_pe).toFixed(1)}`).join(" ");
  const provisionalStartIndex = Math.max(0, completeEndIndex);
  const provisionalPath = points.slice(provisionalStartIndex).map((point, index) => `${index ? "L" : "M"}${x(provisionalStartIndex + index).toFixed(1)},${y(point.trailing_pe).toFixed(1)}`).join(" ");
  const bands = [
    { key: "minus2", label: "-2σ", value: model.minus_2sigma, tone: "deep-low" },
    { key: "minus1", label: "-1σ", value: model.minus_1sigma, tone: "low" },
    { key: "mean", label: "중심", value: model.mean_multiple, tone: "mean" },
    { key: "plus1", label: "+1σ", value: model.plus_1sigma, tone: "high" },
    { key: "plus2", label: "+2σ", value: model.plus_2sigma, tone: "deep-high" },
  ];
  return <div className="multiple-chart-wrap"><div className="multiple-legend"><span className="legend-complete">{isStock ? "filing-aware 완결 PER" : "완결 PER"}</span>{!isStock && completeEndIndex < points.length - 1 ? <span className="legend-provisional">잠정 PER · 최신 EPS 유지</span> : null}</div><div className="chart-shell multiple-chart-shell"><svg viewBox={`0 0 ${viewWidth} 310`} role="img" aria-label="최근 60개월 후행 PER과 로그 표준편차 구간" onMouseMove={(event) => setSelected(pointerIndex(event, points.length, left, width, viewWidth))} onMouseLeave={() => setSelected(points.length - 1)}><defs><linearGradient id="multipleArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#355f82" stopOpacity=".18"/><stop offset="100%" stopColor="#355f82" stopOpacity="0"/></linearGradient></defs>{[0, 1, 2, 3, 4].map((index) => <line key={index} className="chart-grid" x1={left} x2={left + width} y1={top + index * height / 4} y2={top + index * height / 4}/>)}{bands.map((band) => band.value == null ? null : <g key={band.key}><line className={`multiple-band band-${band.tone}`} x1={left} x2={left + width} y1={y(band.value)} y2={y(band.value)}/><text className={`band-label label-${band.tone}`} x={left + width + 14} y={y(band.value) + 4}>{band.label} <tspan>{n(band.value, 1)}x</tspan></text></g>)}<path className="multiple-area" d={area}/><path className="multiple-line" d={isStock ? path : completePath}/>{!isStock && completeEndIndex < points.length - 1 ? <path className="provisional-line" d={provisionalPath}/> : null}<line className="hover-rule" x1={x(selected)} x2={x(selected)} y1={top} y2={top + height}/><circle className="hover-dot" cx={x(selected)} cy={y(active.trailing_pe)} r="5"/><circle className={`current-ring ${model.current_is_provisional ? "provisional-current" : ""}`} cx={x(points.length - 1)} cy={y(points[points.length - 1].trailing_pe)} r="8"/>{[0, 12, 24, 36, 48, points.length - 1].filter((value, index, all) => value < points.length && all.indexOf(value) === index).map((index) => <text key={index} className="axis-label" x={x(index)} y="294" textAnchor={index === 0 ? "start" : index === points.length - 1 ? "end" : "middle"}>{monthLabel(points[index].month)}</text>)}</svg><div className="chart-inspector" style={{ left: `${x(selected) / viewWidth * 100}%`, top: `${Math.max(72, y(active.trailing_pe)) / 310 * 100}%` }}><span>{monthLabel(active.month)}</span><strong>{n(active.trailing_pe, 2)}x</strong><small>{active.quality === "provisional" ? `잠정 PER · EPS ${monthLabel(active.eps_basis_date)}` : `EPS ${active.eps_basis_date || "-"}`}</small></div></div></div>;
}

function ScenarioChart({ model, label }: { model: ValuationPayload["index_scenario"]; label: string }) {
  const scenarios = model.price_scenarios || model.spx_scenarios || {};
  const lower = scenarios.lower, upper = scenarios.upper, baseline = scenarios.baseline, current = model.current_price ?? model.current_spx;
  if ([lower, upper, baseline, current].some((value) => value == null)) return <div className="empty">예상 EPS와 현재 가격 근거가 갖춰지면 시나리오가 표시됩니다.</div>;
  const lo = Math.min(lower, current!) * .95, hi = Math.max(upper, current!) * 1.05, range = Math.max(1, hi - lo);
  const x = (value: number) => 72 + (value - lo) / range * 776;
  return <div className="scenario-ruler"><svg viewBox="0 0 920 190" role="img" aria-label={`${label} 상대가치 시나리오 범위`}><line className="scenario-axis" x1="72" x2="848" y1="98" y2="98"/><line className="scenario-range" x1={x(lower)} x2={x(upper)} y1="98" y2="98"/><circle className="scenario-end" cx={x(lower)} cy="98" r="7"/><circle className="scenario-end" cx={x(upper)} cy="98" r="7"/><circle className="scenario-baseline" cx={x(baseline)} cy="98" r="10"/><line className="current-marker" x1={x(current!)} x2={x(current!)} y1="42" y2="150"/><text x={x(lower)} y="138" textAnchor="middle">보수 {n(lower, 0)}</text><text className="baseline-label" x={x(baseline)} y="66" textAnchor="middle">기준 {n(baseline, 0)}</text><text x={x(upper)} y="138" textAnchor="middle">낙관 {n(upper, 0)}</text><text className="current-label" x={x(current!)} y="30" textAnchor="middle">현재 {n(current, 0)}</text></svg></div>;
}

const historyValue = (point: ScenarioHistoryPoint, key: "actual" | "lower" | "baseline" | "upper") => {
  if (key === "actual") return point.actual_price ?? point.actual_spx ?? 0;
  if (key === "lower") return point.lower_price ?? point.lower_spx ?? 0;
  if (key === "baseline") return point.baseline_price ?? point.baseline_spx ?? 0;
  return point.upper_price ?? point.upper_spx ?? 0;
};

const historyPointAvailable = (point: ScenarioHistoryPoint) => point.status !== "MISSING"
  && (["actual", "lower", "baseline", "upper"] as const).every((key) => Number.isFinite(historyValue(point, key)) && historyValue(point, key) > 0);

function contiguousHistorySegments(timeline: ScenarioHistoryPoint[]) {
  const segments: ScenarioHistoryPoint[][] = [];
  timeline.forEach((point, index) => {
    if (!historyPointAvailable(point)) return;
    const slot = point.slot_index ?? index;
    const current = segments[segments.length - 1];
    const previous = current?.[current.length - 1];
    if (!previous || slot !== (previous.slot_index ?? slot - 1) + 1) {
      segments.push([point]);
    } else {
      current.push(point);
    }
  });
  return segments;
}

const historyGapReasonLabel: Record<string, string> = {
  NON_POSITIVE_EPS: "당시 TTM EPS가 0 이하라 PER가 성립하지 않습니다.",
  INSUFFICIENT_ROLLING_PER_WARMUP: "당시 60개월 positive PER 이력이 충분하지 않습니다.",
  INSUFFICIENT_PIT_EVIDENCE: "당시 공개된 filing·SEP 근거가 충분하지 않습니다.",
  PRICE_MISSING: "해당 월의 저장 가격이 없습니다.",
};

const historyGapMessage = (history?: ScenarioHistory) => {
  if (history?.reason_code === "INSUFFICIENT_PIT_EVIDENCE") {
    const complete = history.observation_count ?? 0;
    const target = history.window_months ?? 0;
    const stored = history.available_history_months;
    return stored != null
      ? `positive PER 원자료 ${stored}개월은 있지만 filing·SEP가 모두 갖춰진 과거 평가점은 ${complete}/${target}개월입니다.`
      : `filing·SEP가 모두 갖춰진 과거 평가점은 ${complete}/${target}개월입니다.`;
  }
  if (history?.required_history_months && history.available_history_months != null) {
    return `${history.required_history_months}개월이 필요하지만 현재 ${history.available_history_months}개월이 준비됐습니다.`;
  }
  return "과거 시점 자료가 충분해지면 흐름을 표시합니다.";
};

function ScenarioHistoryChart({ options, fallback, symbol, isStock }: { options?: Record<HistoryPeriod, ScenarioHistory>; fallback?: ScenarioHistory; symbol: string; isStock: boolean }) {
  const periods: { key: HistoryPeriod; label: string; years: number }[] = [{ key: "1y", label: "1년", years: 1 }, { key: "3y", label: "3년", years: 3 }, { key: "5y", label: "5년", years: 5 }];
  const [period, setPeriod] = useState<HistoryPeriod>("1y");
  const history = options?.[period] || fallback;
  const points = history?.series || [];
  const timeline = history && history.timeline?.length
    ? history.timeline
    : points.map((point, index) => ({ ...point, slot_index: point.slot_index ?? index, status: "AVAILABLE" as const }));
  const availablePoints = timeline.filter(historyPointAvailable);
  const lastAvailableSlot = availablePoints[availablePoints.length - 1]?.slot_index ?? Math.max(0, timeline.length - 1);
  const [selected, setSelected] = useState(lastAvailableSlot);
  useEffect(() => setSelected(lastAvailableSlot), [lastAvailableSlot, period]);
  const years = history?.window_years || periods.find((item) => item.key === period)?.years || 1;
  const partial = Boolean(isStock && history && history.status === "PARTIAL");
  if (!history || (history.status !== "READY" && !partial) || availablePoints.length < 2) return <div className="history-block"><div className="history-period-selector">{periods.map((item) => <button key={item.key} type="button" aria-pressed={period === item.key} onClick={() => setPeriod(item.key)}>{item.label}</button>)}</div><div className="empty compact-empty history-empty"><strong>상대가치 계산 이력이 부족합니다</strong><span>{historyGapMessage(history)}</span></div></div>;
  const values = availablePoints.flatMap((point) => [historyValue(point, "actual"), historyValue(point, "lower"), historyValue(point, "upper")]);
  const min = Math.min(...values) * .97, max = Math.max(...values) * 1.03, range = Math.max(1, max - min);
  const left = 58, width = 792, top = 30, height = 250, viewWidth = 920;
  const x = (slot: number) => left + slot / Math.max(1, timeline.length - 1) * width;
  const y = (value: number) => top + (max - value) / range * height;
  const segments = contiguousHistorySegments(timeline);
  const line = (segment: ScenarioHistoryPoint[], key: "actual" | "baseline") => segment.map((point, index) => `${index ? "L" : "M"}${x(point.slot_index ?? index).toFixed(1)},${y(historyValue(point, key)).toFixed(1)}`).join(" ");
  const band = (segment: ScenarioHistoryPoint[]) => `${segment.map((point, index) => `${index ? "L" : "M"}${x(point.slot_index ?? index).toFixed(1)},${y(historyValue(point, "upper")).toFixed(1)}`).join(" ")} ${segment.slice().reverse().map((point) => `L${x(point.slot_index ?? 0).toFixed(1)},${y(historyValue(point, "lower")).toFixed(1)}`).join(" ")} Z`;
  const active = timeline[Math.min(selected, timeline.length - 1)] as ScenarioHistoryPoint;
  const activeAvailable = historyPointAvailable(active);
  const missingTarget = history.window_months ?? timeline.length;
  const missingCount = history.missing_point_count ?? Math.max(0, missingTarget - availablePoints.length);
  const missingSummary = Object.entries(history.missing_reason_counts || {}).map(([reason, count]) => `${historyGapReasonLabel[reason] || reason} ${count}개월`).join(" · ");
  return <div className="history-block"><div className="subsection-head"><div><span>{years} YEAR · POINT-IN-TIME</span><h4>최근 {years}년 상대가치 흐름</h4><p>실제 {symbol} 가격과 당시 공개된 filing·SEP만 사용한 재구성</p></div><div className="history-period-selector">{periods.map((item) => <button key={item.key} type="button" aria-pressed={period === item.key} onClick={() => setPeriod(item.key)}>{item.label}</button>)}</div></div>{partial ? <div className="history-partial-notice" role="status"><strong>부분 이력 · 계산 가능 {availablePoints.length}/{missingTarget}개월</strong><span>누락 {missingCount}개월{missingSummary ? ` · ${missingSummary}` : ""}</span><small>결측 월은 연결·보간하지 않습니다.</small></div> : null}<div className="chart-legend"><span className="legend-actual">실제 {symbol}</span><span className="legend-baseline">기준 시나리오</span><span className="legend-band">보수–낙관</span></div><div className="chart-shell history-chart-shell"><svg viewBox="0 0 920 330" role="img" aria-label={`최근 ${years}년 ${symbol} 상대가치 흐름`} onMouseMove={(event) => setSelected(pointerIndex(event, timeline.length, left, width, viewWidth))} onMouseLeave={() => setSelected(lastAvailableSlot)}>{[0, 1, 2, 3, 4].map((index) => <line key={index} className="chart-grid" x1={left} x2={left + width} y1={top + index * height / 4} y2={top + index * height / 4}/>)}{segments.map((segment) => <path key={`band-${segment[0].month}`} className="history-band" d={band(segment)}/>)}{segments.map((segment) => <path key={`baseline-${segment[0].month}`} className="history-baseline" d={line(segment, "baseline")}/>)}{segments.map((segment) => <path key={`actual-${segment[0].month}`} className="history-actual" d={line(segment, "actual")}/>)}<line className="hover-rule" x1={x(selected)} x2={x(selected)} y1={top} y2={top + height}/>{activeAvailable ? <><circle className="history-hover-dot" cx={x(selected)} cy={y(historyValue(active, "actual"))} r="5"/><circle className="history-baseline-dot" cx={x(selected)} cy={y(historyValue(active, "baseline"))} r="5"/></> : null}{timeline.map((point, index) => index % Math.max(1, Math.ceil((timeline.length - 1) / 6)) === 0 || index === timeline.length - 1 ? <text key={point.month} className="axis-label" x={x(index)} y="316" textAnchor={index === 0 ? "start" : index === timeline.length - 1 ? "end" : "middle"}>{years === 1 ? `${point.month.slice(5, 7)}월` : monthLabel(point.month)}</text> : null)}</svg>{activeAvailable ? <div className="history-inspector"><div><span>{monthLabel(active.month)}</span><strong>{n(historyValue(active, "actual"), 0)}</strong><small>실제 가격</small></div><div><span>상대가치 구간</span><strong>{n(historyValue(active, "lower"), 0)}–{n(historyValue(active, "upper"), 0)}</strong><small>기준 {n(historyValue(active, "baseline"), 0)}</small></div><div><span>기준 대비</span><strong className={(active.gap_to_baseline_pct || 0) > 0 ? "gap-high" : "gap-low"}>{signed(active.gap_to_baseline_pct)}</strong><small>실제 ÷ 기준</small></div><div><span>FOMC 거시 기준</span><strong>{signed(active.current_macro_pct ?? ((active.real_gdp_pct || 0) + (active.pce_inflation_pct || 0)))}</strong><small>SEP {active.sep_release_date || "-"}</small></div><div><span>EPS 기준</span><strong>{isStock ? active.eps_basis_date || "filing-aware" : active.eps_basis_date || "-"}</strong><small>future filing 소급 없음</small></div></div> : <div className="history-gap-inspector"><span>{monthLabel(active.month)}</span><strong>상대가치 계산 공백</strong><small>{historyGapReasonLabel[active.reason_code || ""] || "당시 계산 근거가 충분하지 않습니다."}</small></div>}</div><p className="limitation">각 월말 당시 공개된 근거만 사용한 상대가치 재구성입니다.</p></div>;
}

function ReadyValuation({ payload, isStock }: { payload: ValuationPayload; isStock: boolean }) {
  const multiple = payload.multiple_regime || {};
  const earnings = payload.earnings_scenario || {};
  const index = payload.index_scenario || {};
  const instrument = payload.instrument!;
  const symbol = instrument.proxy_symbol || payload.selection?.symbol || "선택 종목";
  const baseline = isStock ? earnings.scenarios?.baseline : earnings.baseline;
  const excess = earnings.company_excess_growth;
  const gap = index.current_vs_baseline_gap_pct;
  const gapLabel = index.valuation_position === "ABOVE_BASELINE" ? "기준 시나리오보다 현재 가격이 높음" : index.valuation_position === "BELOW_BASELINE" ? "기준 시나리오보다 현재 가격이 낮음" : "기준 시나리오와 유사";
  return <><section className="valuation-section"><div className="section-head"><div><span>그래프 1</span><h3>{isStock ? "최근 60개월 멀티플 구간" : "최근 5년 멀티플 구간"}</h3><p>{isStock ? "positive 월별 PER의 로그 분포와 최근 36개월 민감도를 함께 봅니다." : "완결 월별 PER 분포와 최신 EPS를 유지한 잠정 PER"}</p></div><div className={`regime regime-${multiple.bucket || "blocked"}`}>{bucketLabel[multiple.bucket || ""] || "자료 확인 필요"}</div></div><div className="metrics"><div><span>{!isStock && multiple.current_is_provisional ? "현재 잠정 PER" : "현재 PER"}</span><strong>{n(multiple.current_pe, 2)}x</strong><small>가격 {multiple.current_price_basis_date || "-"}</small></div><div><span>{isStock ? "60개월 중심" : "5년 중심"}</span><strong>{n(multiple.mean_multiple, 2)}x</strong></div><div><span>현재 Z</span><strong>{n(multiple.current_z, 2)}</strong></div><div><span>{isStock ? "36개월 민감도" : "3년 민감도"}</span><strong>{bucketLabel[multiple.sensitivity?.bucket || ""] || "-"}</strong></div></div><MultipleChart model={multiple} isStock={isStock}/><p className="basis-note">EPS 기준 {multiple.current_eps_basis_date || earnings.eps_basis_date || "-"} · {isStock ? "월말까지 공개된 최신 4개 분기 희석 EPS TTM" : "As-Reported actual TTM"}</p>{multiple.period_sensitive ? <p className="notice">{isStock ? "36개월과 60개월" : "3년과 5년"} 판정이 달라 기간 민감도가 큽니다.</p> : null}<p className="limitation">{multiple.limitation}</p></section><section className="valuation-section"><div className="section-head"><div><span>그래프 2</span><h3>{isStock ? `${symbol} 거시·기업 실적 결합 상대가치 시나리오` : `FOMC 예상 실적 기반 지수 시나리오 · 적정 ${symbol} 구간`}</h3><p>{isStock ? "FOMC real GDP + PCE에 최근 3년 기업 초과 EPS 성장 P25/P50/P75를 결합합니다." : "현재 TTM EPS에 SEP 실질 GDP와 PCE 물가상승률을 합산 적용"}</p></div><div className="release"><span>SEP 발표</span><strong>{earnings.release_date || "-"}</strong></div></div><div className="source-row"><div><span>EPS 출처</span><strong>{earnings.eps_source || "EPS 출처 미확정"}</strong><small>EPS 기준 {earnings.eps_basis_date || "-"}</small></div><span className={`source-badge quality-${earnings.eps_source_quality || "unknown"}`}>{sourceQualityLabel[earnings.eps_source_quality || ""] || "출처 확인 필요"}</span></div>{isStock ? <div className="metrics metrics-five"><div><span>현재 TTM EPS</span><strong>{n(earnings.current_ttm_eps, 2)}</strong></div><div><span>FOMC 거시 기준</span><strong>{signed(earnings.current_macro_pct)}</strong><small>GDP {n(earnings.real_gdp_pct, 1)}% + PCE {n(earnings.pce_inflation_pct, 1)}%</small></div><div><span>기업 초과성장</span><strong>{signed(excess?.p50_pct)}</strong><small>P25 {signed(excess?.p25_pct)} · P75 {signed(excess?.p75_pct)}</small></div><div><span>예상 EPS 성장률</span><strong>{signed(baseline?.growth_pct)}</strong></div><div><span>예상 EPS</span><strong>{n(baseline?.projected_eps, 2)}</strong></div></div> : <div className="metrics metrics-five"><div><span>현재 TTM EPS</span><strong>{n(earnings.current_ttm_eps, 2)}</strong></div><div><span>적용 GDP</span><strong>{n(baseline?.real_gdp_pct, 1)}%</strong></div><div><span>적용 PCE</span><strong>{n(baseline?.pce_inflation_pct, 1)}%</strong></div><div><span>예상 EPS 성장률</span><strong>{n(baseline?.growth_pct, 1)}%</strong></div><div><span>예상 EPS</span><strong>{n(baseline?.projected_eps, 2)}</strong></div></div>}<p className="method-note">{isStock ? "기업 자체 이력과 FOMC 거시 proxy를 결합한 상대가치 시나리오입니다." : "거시 지표 기반 자체 예상이며 애널리스트 컨센서스가 아닙니다."}</p>{index.status === "READY" ? <ScenarioChart model={index} label={symbol}/> : <div className="empty">{index.reason || earnings.reason || "시나리오 근거를 확인해 주세요."}</div>}{gap != null ? <div className={`valuation-gap position-${index.valuation_position || "unknown"}`}><span>{gapLabel}</span><strong>{signed(gap)}</strong><small>현재 가격과 기준 예상 EPS × 자체 60개월 중심 PER 비교</small></div> : null}{index.gap_pct ? <div className="gap-row"><span>보수 {signed(index.gap_pct.lower)}</span><strong>기준 {signed(index.gap_pct.baseline)}</strong><span>낙관 {signed(index.gap_pct.upper)}</span></div> : null}<p className="scenario-disclaimer">공식 적정가·목표주가·매매 신호가 아닙니다.</p><ScenarioHistoryChart options={index.history_options} fallback={index.history} symbol={symbol} isStock={isStock}/><p className="limitation">{index.limitation || earnings.limitation}</p></section></>;
}

function FreshnessBar({ freshness, collecting, result, onRefresh }: { freshness?: DataFreshness; collecting: boolean; result?: CollectionResult; onRefresh: () => void }) {
  const action = freshness?.action;
  const statusLabel: Record<string, string> = {
    READY: "최신 자료 확인됨",
    REFRESH_AVAILABLE: "최신화 가능",
    PARTIAL: "일부 자료 확인 필요",
    BLOCKED: "최신화 조건 확인 필요",
  };
  const gapLabels: Record<string, string> = {
    asset_profile: "시장가치",
    prices: "가격",
    sec_identity: "SEC 기업 연결",
    sec_statements: "재무제표",
  };
  const gapSummary = (freshness?.gaps || []).map((gap) => gapLabels[gap.scope] || gap.scope).join(" · ");
  return <section className={`freshness-bar freshness-${(freshness?.status || "blocked").toLowerCase()}`} aria-label="선택 기업 데이터 최신화">
    <div className="freshness-basis"><span>자료 기준</span><strong>가격 {freshness?.price_basis_date || "-"} · 시장가치 {freshness?.profile_basis_date || "-"} · 재무 {freshness?.statement_period_end || "-"}</strong><small>공개 {freshness?.statement_available_at || "-"} · 최신 완료 거래일 {freshness?.expected_price_date || "-"}</small></div>
    <div className="freshness-action"><span>{statusLabel[freshness?.status || ""] || "자료 상태 확인 중"}</span><p>{result?.message || action?.detail || (gapSummary ? `${gapSummary} 자료를 다시 확인할 수 있습니다.` : "현재 저장 자료로 분석합니다.")}</p>{action?.enabled ? <button type="button" disabled={collecting} onClick={onRefresh}>{collecting ? "갱신 중" : action.label || "최신 데이터로 다시 계산"}</button> : null}</div>
  </section>;
}

function MarketContextValuation({ args }: Props) {
  const root = args.payload;
  const combined = root && "instruments" in root ? root as CombinedPayload : null;
  const [selectedInstrument, setSelectedInstrument] = useState(combined?.default_instrument || "sp500");
  const [collecting, setCollecting] = useState(false);
  const [analysisBySymbol, setAnalysisBySymbol] = useState<Record<string, AnalysisChoice>>({});
  const payload = combined?.instruments[selectedInstrument] || root as ValuationPayload | undefined;
  const showCombinedSelector = Boolean(combined && combined.show_instrument_selector !== false && Object.keys(combined.instruments).length > 1);
  useEffect(() => { Streamlit.setFrameHeight(); window.setTimeout(() => Streamlit.setFrameHeight(), 180); }, [payload, selectedInstrument, collecting, analysisBySymbol]);
  useEffect(() => setCollecting(false), [payload?.collection_result?.status, payload?.data_freshness?.status]);
  if (!payload) return null;
  const isStock = payload.instrument?.id === "us_stock" || selectedInstrument === "us_stock";
  const symbol = payload.selection?.symbol || payload.instrument?.proxy_symbol || "-";
  const recommended: AnalysisChoice = payload.recommended_analysis === "per" ? "per" : "turnaround";
  const selectedAnalysis: AnalysisChoice = isStock && payload.selection?.symbol
    ? analysisBySymbol[payload.selection.symbol] || recommended
    : "per";
  const showTurnaround = Boolean(isStock && payload.selection?.symbol && selectedAnalysis === "turnaround");
  const basisDate = isStock
    ? showTurnaround
      ? payload.data_freshness?.statement_period_end
      : payload.data_freshness?.price_basis_date || payload.selection?.latest_price_date || payload.basis?.price?.price_basis_date
    : payload.basis?.spx?.date;
  const basisLabel = isStock ? showTurnaround ? "재무 기준일" : "가격 기준일" : "기준일";
  const chooseAnalysis = (choice: AnalysisChoice) => {
    if (!payload.selection?.symbol) return;
    setAnalysisBySymbol((current) => ({ ...current, [payload.selection!.symbol!]: choice }));
  };
  const refresh = () => {
    const action = payload.data_freshness?.action;
    if (!action?.enabled || action.id !== "refresh_us_stock_data") return;
    setCollecting(true);
    emitEvent(action.id, { symbol: action.symbol });
  };
  return <main className="valuation-workbench" data-status={showTurnaround ? payload.turnaround_analysis?.status : payload.status}>
    {showCombinedSelector ? <nav className="instrument-selector" aria-label="가치평가 대상 선택"><button type="button" aria-pressed={selectedInstrument === "sp500"} onClick={() => setSelectedInstrument("sp500")}><span>S&amp;P 500</span><small>시장 지수</small></button><button type="button" aria-pressed={selectedInstrument === "us_stock"} onClick={() => setSelectedInstrument("us_stock")}><span>미국 개별주식</span><small>기업명·티커 검색</small></button></nav> : null}
    {isStock ? <StockSearch payload={payload}/> : null}
    <header className="valuation-header"><div><span className="eyebrow">{isStock ? showTurnaround ? "U.S. STOCK TURNAROUND ANALYSIS" : "U.S. STOCK RELATIVE VALUATION" : "S&P 500 VALUATION"}</span><h2>{isStock && payload.selection ? `${payload.selection.name || symbol} ${showTurnaround ? "전환 분석" : "상대가치 평가"}` : "멀티플과 예상 실적을 한 화면에서 비교"}</h2><p>{isStock ? showTurnaround ? "분기 filing 근거로 영업·현금 전환과 생존 위험을 먼저 읽습니다." : "한 기업의 filing-aware EPS와 자체 멀티플 이력으로 현재 위치를 읽습니다." : "과거 대비 현재 가격 수준과 FOMC 거시 가정을 분리해 읽습니다."}</p></div><div className="basis"><span>{basisLabel}</span><strong>{basisDate || "-"}</strong><small>{showTurnaround ? `공개 ${payload.data_freshness?.statement_available_at || "-"} · 가격 ${payload.data_freshness?.price_basis_date || "-"}` : payload.instrument?.method_label || "As-Reported actual TTM"}</small></div></header>
    {isStock && payload.selection?.symbol ? <FreshnessBar freshness={payload.data_freshness} collecting={collecting} result={payload.collection_result} onRefresh={refresh}/> : null}
    {isStock && payload.selection?.symbol ? <nav className="analysis-selector" aria-label="개별주식 분석 선택"><button type="button" aria-pressed={selectedAnalysis === "per"} onClick={() => chooseAnalysis("per")}><span>PER 상대가치</span><small>{payload.multiple_regime?.status === "READY" ? "적용 가능" : "적용 전"}</small></button><button type="button" aria-pressed={selectedAnalysis === "turnaround"} onClick={() => chooseAnalysis("turnaround")}><span>전환 분석</span><small>{payload.turnaround_analysis?.status || "확인 중"}</small></button></nav> : null}
    {showTurnaround
      ? <TurnaroundAnalysis payload={payload.turnaround_analysis}/>
      : isStock && payload.status !== "READY"
        ? <StockState payload={payload}/>
        : <ReadyValuation payload={payload} isStock={isStock}/>}
    {!showTurnaround ? <details className="evidence"><summary>산식·자료 출처·한계 보기</summary><div className="evidence-grid">{(payload.sources || []).map((source) => <div key={source.name}><strong>{source.name}</strong><span>{source.role}</span></div>)}</div><ul>{(payload.limitations || []).map((item) => <li key={item}>{item}</li>)}</ul></details> : null}
  </main>;
}

export default withStreamlitConnection(MarketContextValuation);
