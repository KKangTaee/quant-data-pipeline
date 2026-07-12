import React, { useEffect } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import "./style.css";

type NumericMap = Record<string, number>;
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
    mean_multiple?: number; minus_1sigma?: number; plus_1sigma?: number; plus_2sigma?: number;
    period_sensitive?: boolean; basis_start?: string; basis_end?: string; current_basis_date?: string;
    series?: { month: string; trailing_pe: number }[];
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
    reason?: string; limitation?: string;
  };
  sources?: { name: string; role: string }[];
  limitations?: string[];
};

type Props = ComponentProps & { args: { payload?: ValuationPayload } };
const n = (value?: number, digits = 1) => value == null || !Number.isFinite(value) ? "-" : value.toLocaleString("ko-KR", { maximumFractionDigits: digits });
const bucketLabel: Record<string, string> = { LOW: "상대적 저평가", NEUTRAL: "중립 구간", HIGH: "상대적 고평가", EXTREME_HIGH: "매우 높은 구간" };
const sourceQualityLabel: Record<string, string> = { official_actual: "공식 actual", interpolated_ttm_proxy: "보간 TTM 대체 기준" };

function MultipleChart({ model }: { model: ValuationPayload["multiple_regime"] }) {
  const points = model.series || [];
  if (!points.length) return <div className="empty">유효한 Shiller 월별 PER 이력 60개월이 필요합니다.</div>;
  const bands = [model.minus_1sigma, model.mean_multiple, model.plus_1sigma, model.plus_2sigma].filter((v): v is number => v != null);
  const values = [...points.map((p) => p.trailing_pe), ...bands, model.current_pe || 0];
  const min = Math.min(...values) * .94, max = Math.max(...values) * 1.06, range = Math.max(1, max - min);
  const x = (i: number) => 52 + i / Math.max(1, points.length - 1) * 636;
  const y = (v: number) => 20 + (max - v) / range * 210;
  const line = points.map((p, i) => `${x(i).toFixed(1)},${y(p.trailing_pe).toFixed(1)}`).join(" ");
  return <svg viewBox="0 0 720 270" role="img" aria-label="최근 5년 후행 PER과 표준편차 구간">
    <rect className="zone zone-low" x="52" y={y(model.mean_multiple || min)} width="636" height={Math.max(0, y(model.minus_1sigma || min) - y(model.mean_multiple || min))} />
    <rect className="zone zone-high" x="52" y={y(model.plus_1sigma || max)} width="636" height={Math.max(0, y(model.mean_multiple || min) - y(model.plus_1sigma || max))} />
    {[model.minus_1sigma, model.mean_multiple, model.plus_1sigma, model.plus_2sigma].map((v, i) => v == null ? null : <g key={i}><line className={`band band-${i}`} x1="52" x2="688" y1={y(v)} y2={y(v)} /><text x="48" y={y(v)+4} textAnchor="end">{n(v,1)}x</text></g>)}
    <polyline className="history-line" fill="none" points={line} />
    <circle className="current-dot" cx="688" cy={y(model.current_pe || points[points.length-1].trailing_pe)} r="5" />
    <text className="axis-label" x="52" y="258">{points[0].month.slice(0,7)}</text><text className="axis-label" x="688" y="258" textAnchor="end">{points[points.length-1].month.slice(0,7)}</text>
  </svg>;
}

function ScenarioChart({ model }: { model: ValuationPayload["index_scenario"] }) {
  const scenarios = model.spx_scenarios || {}; const lower = scenarios.lower; const upper = scenarios.upper; const baseline = scenarios.baseline; const current = model.current_spx;
  if ([lower, upper, baseline, current].some((v) => v == null)) return <div className="empty">예상 EPS와 현재 SPX 근거가 갖춰지면 시나리오가 표시됩니다.</div>;
  const lo = Math.min(lower, current!) * .94, hi = Math.max(upper, current!) * 1.06, range = Math.max(1, hi-lo); const x = (v: number) => 58 + (v-lo)/range*604;
  return <svg viewBox="0 0 720 180" role="img" aria-label="예상 EPS 기반 SPX 시나리오 범위">
    <line className="scenario-axis" x1="58" x2="662" y1="92" y2="92" />
    <line className="scenario-range" x1={x(lower)} x2={x(upper)} y1="92" y2="92" />
    <circle className="scenario-end" cx={x(lower)} cy="92" r="6" /><circle className="scenario-end" cx={x(upper)} cy="92" r="6" />
    <circle className="scenario-baseline" cx={x(baseline)} cy="92" r="8" /><line className="current-marker" x1={x(current!)} x2={x(current!)} y1="44" y2="134" />
    <text x={x(lower)} y="128" textAnchor="middle">하단 {n(lower,0)}</text><text x={x(baseline)} y="68" textAnchor="middle">기준 {n(baseline,0)}</text><text x={x(upper)} y="128" textAnchor="middle">상단 {n(upper,0)}</text><text className="current-label" x={x(current!)} y="34" textAnchor="middle">현재 {n(current,0)}</text>
  </svg>;
}

function MarketContextValuation({ args }: Props) {
  const payload = args.payload;
  useEffect(() => { Streamlit.setFrameHeight(); window.setTimeout(() => Streamlit.setFrameHeight(), 120); }, [payload]);
  if (!payload) return null;
  const multiple = payload.multiple_regime || {}; const earnings = payload.earnings_scenario || {}; const index = payload.index_scenario || {};
  const baseline = earnings.baseline;
  const gap = index.current_vs_baseline_gap_pct;
  const gapLabel = index.valuation_position === "ABOVE_BASELINE" ? "기준 시나리오 대비 고평가" : index.valuation_position === "BELOW_BASELINE" ? "기준 시나리오 대비 저평가" : "기준 시나리오와 유사";
  return <main className="valuation-workbench" data-status={payload.status}>
    <header className="valuation-header"><div><span className="eyebrow">S&amp;P 500 VALUATION</span><h2>멀티플과 예상 실적을 한 화면에서 비교</h2><p>과거 대비 현재 가격 수준과 FOMC 거시 가정을 분리해 읽습니다.</p></div><div className="basis"><span>기준일</span><strong>{payload.basis?.spx?.date || "-"}</strong><small>{payload.basis?.eps_basis || "As-Reported actual TTM"}</small></div></header>
    <section className="valuation-section"><div className="section-head"><div><span>그래프 1</span><h3>최근 5년 멀티플 구간</h3><p>월별 SPX ÷ 당시 TTM EPS의 log(PER) 분포</p></div><div className={`regime regime-${multiple.bucket || "blocked"}`}>{bucketLabel[multiple.bucket || ""] || "자료 확인 필요"}</div></div>
      <div className="metrics"><div><span>현재 PER</span><strong>{n(multiple.current_pe,2)}x</strong></div><div><span>5년 중심</span><strong>{n(multiple.mean_multiple,2)}x</strong></div><div><span>현재 Z</span><strong>{n(multiple.current_z,2)}</strong></div><div><span>3년 민감도</span><strong>{bucketLabel[multiple.sensitivity?.bucket || ""] || "-"}</strong></div></div>
      <MultipleChart model={multiple} /><p className="basis-note">Shiller 최신 PER 기준 {multiple.current_basis_date || multiple.basis_end || "-"}</p>{multiple.period_sensitive ? <p className="notice">3년과 5년 판정이 달라 기간 민감도가 큽니다.</p> : null}<p className="limitation">{multiple.limitation}</p>
    </section>
    <section className="valuation-section"><div className="section-head"><div><span>그래프 2</span><h3>FOMC 예상 실적 기반 지수 시나리오 · 적정 SPX 구간</h3><p>현재 TTM EPS에 SEP 실질 GDP와 PCE 물가상승률을 합산 적용</p></div><div className="release"><span>SEP 발표</span><strong>{earnings.release_date || "-"}</strong></div></div>
      <div className="source-row"><div><span>EPS 출처</span><strong>{earnings.eps_source || "Robert Shiller TTM EPS"}</strong><small>EPS 기준 {earnings.eps_basis_date || "-"}</small></div><span className={`source-badge quality-${earnings.eps_source_quality || "unknown"}`}>{sourceQualityLabel[earnings.eps_source_quality || ""] || "출처 확인 필요"}</span></div>
      {earnings.fallback_reason ? <p className="fallback-note">{earnings.fallback_reason}</p> : null}
      <div className="metrics metrics-five"><div><span>현재 TTM EPS</span><strong>{n(earnings.current_ttm_eps,2)}</strong></div><div><span>적용 GDP</span><strong>{n(baseline?.real_gdp_pct,1)}%</strong></div><div><span>적용 PCE</span><strong>{n(baseline?.pce_inflation_pct,1)}%</strong></div><div><span>예상 EPS 성장률</span><strong>{n(baseline?.growth_pct,1)}%</strong></div><div><span>예상 EPS</span><strong>{n(baseline?.projected_eps,2)}</strong></div></div>
      <p className="method-note">거시 지표 기반 자체 예상이며 애널리스트 컨센서스가 아닙니다.</p>
      {index.status === "READY" ? <ScenarioChart model={index} /> : <div className="empty">{index.reason || earnings.reason || "시나리오 근거를 확인해 주세요."}</div>}
      {gap != null ? <div className={`valuation-gap position-${index.valuation_position || "unknown"}`}><span>{gapLabel}</span><strong>{gap > 0 ? "+" : ""}{n(gap,1)}%</strong><small>현재 SPX와 기준 예상 EPS × 5년 중심 PER 비교</small></div> : null}
      {index.gap_pct ? <div className="gap-row"><span>현재 대비 하단 {n(index.gap_pct.lower,1)}%</span><strong>기준 {n(index.gap_pct.baseline,1)}%</strong><span>상단 {n(index.gap_pct.upper,1)}%</span></div> : null}
      {index.basis_date_mismatch ? <p className="basis-note">계산 기준일이 다릅니다 · EPS {index.basis_dates?.eps || "-"} · SEP {index.basis_dates?.sep || "-"} · SPX {index.basis_dates?.spx || "-"}</p> : null}<p className="limitation">{index.limitation || earnings.limitation}</p>
    </section>
    <details className="evidence"><summary>산식·자료 출처·한계 보기</summary><div className="evidence-grid">{(payload.sources || []).map((source: { name: string; role: string }) => <div key={source.name}><strong>{source.name}</strong><span>{source.role}</span></div>)}</div><ul>{(payload.limitations || []).map((item: string) => <li key={item}>{item}</li>)}</ul></details>
  </main>;
}

export default withStreamlitConnection(MarketContextValuation);
