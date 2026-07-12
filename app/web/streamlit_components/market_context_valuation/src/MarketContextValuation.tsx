import React, { useEffect, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import "./style.css";

type NumericMap = Record<string, number>;
type MultiplePoint = { month: string; trailing_pe: number };
type ScenarioHistoryPoint = {
  month: string;
  actual_spx: number;
  eps_basis_date: string;
  eps_carried_forward: boolean;
  current_ttm_eps: number;
  sep_release_date: string;
  target_year: number;
  real_gdp_pct: number;
  pce_inflation_pct: number;
  growth_pct: number;
  projected_eps: number;
  lower_spx: number;
  baseline_spx: number;
  upper_spx: number;
  gap_to_baseline_pct: number;
};

type ValuationPayload = {
  schema_version: string;
  status: string;
  basis: {
    eps_basis?: string;
    spx?: { date?: string; price?: number };
    official_window_months?: number;
    sensitivity_window_months?: number;
  };
  multiple_regime: {
    status?: string; bucket?: string; current_pe?: number; current_z?: number;
    mean_multiple?: number; minus_2sigma?: number; minus_1sigma?: number;
    plus_1sigma?: number; plus_2sigma?: number;
    period_sensitive?: boolean; basis_start?: string; basis_end?: string; current_basis_date?: string;
    series?: MultiplePoint[];
    sensitivity?: { bucket?: string; mean_multiple?: number; current_z?: number };
    limitation?: string;
  };
  earnings_scenario: {
    status?: string; target_year?: number; release_date?: string; reason?: string;
    current_ttm_eps?: number; eps_source?: string; eps_source_quality?: string;
    eps_basis_date?: string; fallback_reason?: string;
    conservative?: { growth_pct: number; projected_eps: number; real_gdp_pct: number; pce_inflation_pct: number };
    baseline?: { growth_pct: number; projected_eps: number; real_gdp_pct: number; pce_inflation_pct: number };
    optimistic?: { growth_pct: number; projected_eps: number; real_gdp_pct: number; pce_inflation_pct: number };
    limitation?: string;
  };
  index_scenario: {
    status?: string; as_of?: string; current_spx?: number; spx_scenarios?: NumericMap;
    gap_pct?: NumericMap; spy_status?: string; spy_equivalent?: NumericMap | null;
    current_vs_baseline_gap_pct?: number; valuation_position?: string;
    basis_dates?: { eps?: string; sep?: string; spx?: string }; basis_date_mismatch?: boolean;
    history?: {
      status?: string; window_months?: number; rolling_multiple_months?: number;
      label?: string; methodology?: string; limitation?: string;
      sep_releases?: string[]; series?: ScenarioHistoryPoint[];
    };
    reason?: string; limitation?: string;
  };
  sources?: { name: string; role: string }[];
  limitations?: string[];
};

type Props = ComponentProps & { args: { payload?: ValuationPayload } };
const n = (value?: number, digits = 1) => value == null || !Number.isFinite(value) ? "-" : value.toLocaleString("ko-KR", { maximumFractionDigits: digits });
const signed = (value?: number, digits = 1) => value == null || !Number.isFinite(value) ? "-" : `${value > 0 ? "+" : ""}${n(value, digits)}%`;
const monthLabel = (value: string) => value.slice(0, 7).replace("-", ".");
const bucketLabel: Record<string, string> = { LOW: "상대적 저평가", NEUTRAL: "중립 구간", HIGH: "상대적 고평가", EXTREME_HIGH: "매우 높은 구간" };
const sourceQualityLabel: Record<string, string> = { official_actual: "공식 actual", interpolated_ttm_proxy: "보간 TTM 대체 기준" };

function pointerIndex(event: React.MouseEvent<SVGSVGElement>, count: number, left: number, width: number, viewWidth: number) {
  const rect = event.currentTarget.getBoundingClientRect();
  const cursor = (event.clientX - rect.left) / rect.width * viewWidth;
  const ratio = Math.max(0, Math.min(1, (cursor - left) / width));
  return Math.round(ratio * Math.max(0, count - 1));
}

function MultipleChart({ model }: { model: ValuationPayload["multiple_regime"] }) {
  const points = model.series || [];
  const [selected, setSelected] = useState(Math.max(0, points.length - 1));
  useEffect(() => setSelected(Math.max(0, points.length - 1)), [points.length]);
  if (!points.length) return <div className="empty">유효한 Shiller 월별 PER 이력 60개월이 필요합니다.</div>;

  const anchors = [model.minus_2sigma, model.minus_1sigma, model.mean_multiple, model.plus_1sigma, model.plus_2sigma].filter((value): value is number => value != null);
  const values = [...points.map((point) => point.trailing_pe), ...anchors];
  const min = Math.min(...values) * .96;
  const max = Math.max(...values) * 1.04;
  const range = Math.max(1, max - min);
  const left = 54, width = 744, top = 24, height = 240, viewWidth = 920;
  const x = (index: number) => left + index / Math.max(1, points.length - 1) * width;
  const y = (value: number) => top + (max - value) / range * height;
  const path = points.map((point, index) => `${index ? "L" : "M"}${x(index).toFixed(1)},${y(point.trailing_pe).toFixed(1)}`).join(" ");
  const area = `${path} L${x(points.length - 1)},${top + height} L${left},${top + height} Z`;
  const active = points[Math.min(selected, points.length - 1)];
  const bands = [
    { key: "minus2", label: "-2σ", value: model.minus_2sigma, tone: "deep-low" },
    { key: "minus1", label: "-1σ", value: model.minus_1sigma, tone: "low" },
    { key: "mean", label: "중심", value: model.mean_multiple, tone: "mean" },
    { key: "plus1", label: "+1σ", value: model.plus_1sigma, tone: "high" },
    { key: "plus2", label: "+2σ", value: model.plus_2sigma, tone: "deep-high" },
  ];
  const zone = (upper?: number, lower?: number, className = "") => upper == null || lower == null ? null : <rect className={`multiple-zone ${className}`} x={left} y={y(upper)} width={width} height={Math.max(0, y(lower) - y(upper))} />;

  return <div className="chart-shell multiple-chart-shell">
    <svg viewBox={`0 0 ${viewWidth} 310`} role="img" aria-label="최근 5년 후행 PER과 대칭 표준편차 구간" onMouseMove={(event) => setSelected(pointerIndex(event, points.length, left, width, viewWidth))} onMouseLeave={() => setSelected(points.length - 1)}>
      <defs>
        <linearGradient id="multipleArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#355f82" stopOpacity=".18"/><stop offset="100%" stopColor="#355f82" stopOpacity="0"/></linearGradient>
      </defs>
      {zone(model.minus_1sigma, model.minus_2sigma, "zone-deep-low")}
      {zone(model.mean_multiple, model.minus_1sigma, "zone-low")}
      {zone(model.plus_1sigma, model.mean_multiple, "zone-high")}
      {zone(model.plus_2sigma, model.plus_1sigma, "zone-deep-high")}
      {[0, 1, 2, 3, 4].map((index) => <line key={index} className="chart-grid" x1={left} x2={left + width} y1={top + index * height / 4} y2={top + index * height / 4} />)}
      {bands.map((band) => band.value == null ? null : <g key={band.key}><line className={`multiple-band band-${band.tone}`} x1={left} x2={left + width} y1={y(band.value)} y2={y(band.value)} /><text className={`band-label label-${band.tone}`} x={left + width + 14} y={y(band.value) + 4}>{band.label} <tspan>{n(band.value, 1)}x</tspan></text></g>)}
      <path className="multiple-area" d={area} />
      <path className="multiple-line" d={path} />
      <line className="hover-rule" x1={x(selected)} x2={x(selected)} y1={top} y2={top + height} />
      <circle className="hover-dot" cx={x(selected)} cy={y(active.trailing_pe)} r="5" />
      <circle className="current-ring" cx={x(points.length - 1)} cy={y(points[points.length - 1].trailing_pe)} r="8" />
      {[0, 12, 24, 36, 48, points.length - 1].filter((value, index, all) => value < points.length && all.indexOf(value) === index).map((index) => <text key={index} className="axis-label" x={x(index)} y="294" textAnchor={index === 0 ? "start" : index === points.length - 1 ? "end" : "middle"}>{monthLabel(points[index].month)}</text>)}
    </svg>
    <div className="chart-inspector"><span>{monthLabel(active.month)}</span><strong>{n(active.trailing_pe, 2)}x</strong><small>월별 후행 PER</small></div>
  </div>;
}

function ScenarioChart({ model }: { model: ValuationPayload["index_scenario"] }) {
  const scenarios = model.spx_scenarios || {};
  const lower = scenarios.lower, upper = scenarios.upper, baseline = scenarios.baseline, current = model.current_spx;
  if ([lower, upper, baseline, current].some((value) => value == null)) return <div className="empty">예상 EPS와 현재 SPX 근거가 갖춰지면 시나리오가 표시됩니다.</div>;
  const lo = Math.min(lower, current!) * .95, hi = Math.max(upper, current!) * 1.05, range = Math.max(1, hi - lo);
  const x = (value: number) => 72 + (value - lo) / range * 776;
  return <div className="scenario-ruler"><svg viewBox="0 0 920 190" role="img" aria-label="예상 EPS 기반 SPX 시나리오 범위">
    <line className="scenario-axis" x1="72" x2="848" y1="98" y2="98" />
    <line className="scenario-range" x1={x(lower)} x2={x(upper)} y1="98" y2="98" />
    <circle className="scenario-end" cx={x(lower)} cy="98" r="7"/><circle className="scenario-end" cx={x(upper)} cy="98" r="7"/>
    <circle className="scenario-baseline" cx={x(baseline)} cy="98" r="10"/><line className="current-marker" x1={x(current!)} x2={x(current!)} y1="42" y2="150"/>
    <text x={x(lower)} y="138" textAnchor="middle">하단 {n(lower, 0)}</text><text className="baseline-label" x={x(baseline)} y="66" textAnchor="middle">기준 {n(baseline, 0)}</text><text x={x(upper)} y="138" textAnchor="middle">상단 {n(upper, 0)}</text><text className="current-label" x={x(current!)} y="30" textAnchor="middle">현재 {n(current, 0)}</text>
  </svg></div>;
}

function ScenarioHistoryChart({ history }: { history?: ValuationPayload["index_scenario"]["history"] }) {
  const points = history?.series || [];
  const [selected, setSelected] = useState(Math.max(0, points.length - 1));
  useEffect(() => setSelected(Math.max(0, points.length - 1)), [points.length]);
  if (history?.status !== "READY" || points.length < 2) return <div className="empty compact-empty">과거 SEP vintage가 준비되면 최근 1년 흐름이 표시됩니다.</div>;
  const values = points.flatMap((point) => [point.actual_spx, point.lower_spx, point.upper_spx]);
  const min = Math.min(...values) * .97, max = Math.max(...values) * 1.03, range = Math.max(1, max - min);
  const left = 58, width = 792, top = 30, height = 250, viewWidth = 920;
  const x = (index: number) => left + index / Math.max(1, points.length - 1) * width;
  const y = (value: number) => top + (max - value) / range * height;
  const linePath = (key: "actual_spx" | "baseline_spx") => points.map((point, index) => `${index ? "L" : "M"}${x(index).toFixed(1)},${y(point[key]).toFixed(1)}`).join(" ");
  const bandPath = `${points.map((point, index) => `${index ? "L" : "M"}${x(index).toFixed(1)},${y(point.upper_spx).toFixed(1)}`).join(" ")} ${points.slice().reverse().map((point, reverseIndex) => `L${x(points.length - 1 - reverseIndex).toFixed(1)},${y(point.lower_spx).toFixed(1)}`).join(" ")} Z`;
  const active = points[Math.min(selected, points.length - 1)];
  const startTime = new Date(points[0].month).getTime(), endTime = new Date(points[points.length - 1].month).getTime();
  const releaseX = (release: string) => left + Math.max(0, Math.min(1, (new Date(release).getTime() - startTime) / Math.max(1, endTime - startTime))) * width;
  return <div className="history-block">
    <div className="subsection-head"><div><span>1 YEAR · RECONSTRUCTED</span><h4>최근 1년 적정 SPX 흐름</h4><p>실제 SPX와 당시 최신 SEP를 적용한 5년 rolling 적정 구간</p></div><div className="reconstruction-badge">과거 시점 재구성</div></div>
    <div className="chart-legend"><span className="legend-actual">실제 SPX</span><span className="legend-baseline">기준 적정가</span><span className="legend-band">하단–상단</span><span className="legend-sep">SEP 발표</span></div>
    <div className="chart-shell history-chart-shell"><svg viewBox="0 0 920 330" role="img" aria-label="최근 1년 실제 SPX와 재구성 적정 SPX 흐름" onMouseMove={(event) => setSelected(pointerIndex(event, points.length, left, width, viewWidth))} onMouseLeave={() => setSelected(points.length - 1)}>
      {[0, 1, 2, 3, 4].map((index) => <line key={index} className="chart-grid" x1={left} x2={left + width} y1={top + index * height / 4} y2={top + index * height / 4}/>)}
      <path className="history-band" d={bandPath}/>
      {(history?.sep_releases || []).map((release) => <g key={release}><line className="sep-marker" x1={releaseX(release)} x2={releaseX(release)} y1={top} y2={top + height}/><text className="sep-label" x={releaseX(release) + 4} y={top + 12}>SEP {release.slice(5, 7)}/{release.slice(8, 10)}</text></g>)}
      <path className="history-baseline" d={linePath("baseline_spx")}/><path className="history-actual" d={linePath("actual_spx")}/>
      <line className="hover-rule" x1={x(selected)} x2={x(selected)} y1={top} y2={top + height}/>
      <circle className="history-hover-dot" cx={x(selected)} cy={y(active.actual_spx)} r="5"/><circle className="history-baseline-dot" cx={x(selected)} cy={y(active.baseline_spx)} r="5"/>
      {points.map((point, index) => index % 2 === 0 || index === points.length - 1 ? <text key={point.month} className="axis-label" x={x(index)} y="316" textAnchor={index === 0 ? "start" : index === points.length - 1 ? "end" : "middle"}>{point.month.slice(5, 7)}월</text> : null)}
    </svg>
      <div className="history-inspector"><div><span>{monthLabel(active.month)}</span><strong>{n(active.actual_spx, 0)}</strong><small>실제 SPX</small></div><div><span>적정 구간</span><strong>{n(active.lower_spx, 0)}–{n(active.upper_spx, 0)}</strong><small>기준 {n(active.baseline_spx, 0)}</small></div><div><span>기준 대비</span><strong className={active.gap_to_baseline_pct > 0 ? "gap-high" : "gap-low"}>{signed(active.gap_to_baseline_pct)}</strong><small>실제 ÷ 기준</small></div><div><span>적용 SEP</span><strong>{active.sep_release_date}</strong><small>GDP {n(active.real_gdp_pct, 1)}% + PCE {n(active.pce_inflation_pct, 1)}%</small></div><div><span>EPS 기준</span><strong>{active.eps_basis_date}</strong><small>{active.eps_carried_forward ? "최신 확인 EPS 유지" : "해당 월 EPS"}</small></div></div>
    </div>
    <p className="limitation">{history?.limitation}</p>
  </div>;
}

function MarketContextValuation({ args }: Props) {
  const payload = args.payload;
  useEffect(() => { Streamlit.setFrameHeight(); window.setTimeout(() => Streamlit.setFrameHeight(), 160); }, [payload]);
  if (!payload) return null;
  const multiple = payload.multiple_regime || {}, earnings = payload.earnings_scenario || {}, index = payload.index_scenario || {};
  const baseline = earnings.baseline;
  const gap = index.current_vs_baseline_gap_pct;
  const gapLabel = index.valuation_position === "ABOVE_BASELINE" ? "기준 시나리오 대비 고평가" : index.valuation_position === "BELOW_BASELINE" ? "기준 시나리오 대비 저평가" : "기준 시나리오와 유사";
  return <main className="valuation-workbench" data-status={payload.status}>
    <header className="valuation-header"><div><span className="eyebrow">S&amp;P 500 VALUATION</span><h2>멀티플과 예상 실적을 한 화면에서 비교</h2><p>과거 대비 현재 가격 수준과 FOMC 거시 가정을 분리해 읽습니다.</p></div><div className="basis"><span>기준일</span><strong>{payload.basis?.spx?.date || "-"}</strong><small>{payload.basis?.eps_basis || "As-Reported actual TTM"}</small></div></header>
    <section className="valuation-section"><div className="section-head"><div><span>그래프 1</span><h3>최근 5년 멀티플 구간</h3><p>월별 SPX ÷ 당시 TTM EPS의 log(PER) 분포</p></div><div className={`regime regime-${multiple.bucket || "blocked"}`}>{bucketLabel[multiple.bucket || ""] || "자료 확인 필요"}</div></div>
      <div className="metrics"><div><span>현재 PER</span><strong>{n(multiple.current_pe, 2)}x</strong></div><div><span>5년 중심</span><strong>{n(multiple.mean_multiple, 2)}x</strong></div><div><span>현재 Z</span><strong>{n(multiple.current_z, 2)}</strong></div><div><span>3년 민감도</span><strong>{bucketLabel[multiple.sensitivity?.bucket || ""] || "-"}</strong></div></div>
      <MultipleChart model={multiple}/><p className="basis-note">Shiller 최신 PER 기준 {multiple.current_basis_date || multiple.basis_end || "-"}</p>{multiple.period_sensitive ? <p className="notice">3년과 5년 판정이 달라 기간 민감도가 큽니다.</p> : null}<p className="limitation">{multiple.limitation}</p>
    </section>
    <section className="valuation-section"><div className="section-head"><div><span>그래프 2</span><h3>FOMC 예상 실적 기반 지수 시나리오 · 적정 SPX 구간</h3><p>현재 TTM EPS에 SEP 실질 GDP와 PCE 물가상승률을 합산 적용</p></div><div className="release"><span>SEP 발표</span><strong>{earnings.release_date || "-"}</strong></div></div>
      <div className="source-row"><div><span>EPS 출처</span><strong>{earnings.eps_source || "Robert Shiller TTM EPS"}</strong><small>EPS 기준 {earnings.eps_basis_date || "-"}</small></div><span className={`source-badge quality-${earnings.eps_source_quality || "unknown"}`}>{sourceQualityLabel[earnings.eps_source_quality || ""] || "출처 확인 필요"}</span></div>
      {earnings.fallback_reason ? <p className="fallback-note">{earnings.fallback_reason}</p> : null}
      <div className="metrics metrics-five"><div><span>현재 TTM EPS</span><strong>{n(earnings.current_ttm_eps, 2)}</strong></div><div><span>적용 GDP</span><strong>{n(baseline?.real_gdp_pct, 1)}%</strong></div><div><span>적용 PCE</span><strong>{n(baseline?.pce_inflation_pct, 1)}%</strong></div><div><span>예상 EPS 성장률</span><strong>{n(baseline?.growth_pct, 1)}%</strong></div><div><span>예상 EPS</span><strong>{n(baseline?.projected_eps, 2)}</strong></div></div>
      <p className="method-note">거시 지표 기반 자체 예상이며 애널리스트 컨센서스가 아닙니다.</p>
      {index.status === "READY" ? <ScenarioChart model={index}/> : <div className="empty">{index.reason || earnings.reason || "시나리오 근거를 확인해 주세요."}</div>}
      {gap != null ? <div className={`valuation-gap position-${index.valuation_position || "unknown"}`}><span>{gapLabel}</span><strong>{signed(gap)}</strong><small>현재 SPX와 기준 예상 EPS × 5년 중심 PER 비교</small></div> : null}
      {index.gap_pct ? <div className="gap-row"><span>현재 대비 하단 {signed(index.gap_pct.lower)}</span><strong>기준 {signed(index.gap_pct.baseline)}</strong><span>상단 {signed(index.gap_pct.upper)}</span></div> : null}
      <ScenarioHistoryChart history={index.history}/>
      {index.basis_date_mismatch ? <p className="basis-note">계산 기준일이 다릅니다 · EPS {index.basis_dates?.eps || "-"} · SEP {index.basis_dates?.sep || "-"} · SPX {index.basis_dates?.spx || "-"}</p> : null}<p className="limitation">{index.limitation || earnings.limitation}</p>
    </section>
    <details className="evidence"><summary>산식·자료 출처·한계 보기</summary><div className="evidence-grid">{(payload.sources || []).map((source: { name: string; role: string }) => <div key={source.name}><strong>{source.name}</strong><span>{source.role}</span></div>)}</div><ul>{(payload.limitations || []).map((item: string) => <li key={item}>{item}</li>)}</ul></details>
  </main>;
}

export default withStreamlitConnection(MarketContextValuation);
