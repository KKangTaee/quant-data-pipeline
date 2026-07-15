import React, { useEffect, useMemo, useState } from "react";

type MetricOperand = {
  metric?: string;
  concept?: string;
  unit?: string;
  period_start?: string | null;
  period_end?: string | null;
  available_at?: string | null;
  value?: number | null;
};

type MetricProvenance = {
  source_kind?: "REPORTED" | "FILING_DERIVED" | string;
  rule?: string;
  operands?: MetricOperand[];
};

export type TurnaroundPoint = {
  slot_index?: number;
  slot_key?: string;
  status?: "AVAILABLE" | "MISSING" | string;
  period_end?: string | null;
  available_at?: string | null;
  revenue?: number | null;
  gross_profit?: number | null;
  operating_income?: number | null;
  ocf?: number | null;
  capex?: number | null;
  ttm_revenue?: number | null;
  ttm_gross_margin_pct?: number | null;
  ttm_operating_margin_pct?: number | null;
  revenue_yoy_pct?: number | null;
  ttm_ocf?: number | null;
  ttm_fcf?: number | null;
  metric_provenance?: Record<string, MetricProvenance>;
  derived_metrics?: string[];
  ttm_derived_metrics?: string[];
};

type Milestone = { status?: string; evidence?: Record<string, unknown> };
export type TurnaroundPayload = {
  schema_version?: string;
  status?: string;
  reason?: string;
  selection?: { symbol?: string; name?: string } | null;
  series?: {
    status?: string;
    timeline?: TurnaroundPoint[];
    current_balance?: Record<string, unknown>;
  };
  milestones?: {
    status?: string;
    headline?: string;
    milestones?: Record<string, Milestone>;
    evidence?: Record<string, unknown>;
  };
  risks?: {
    cash_runway?: Record<string, unknown>;
    debt_service?: Record<string, unknown>;
    dilution?: Record<string, unknown>;
    flags?: string[];
  };
  valuation?: {
    status?: string;
    method?: string | null;
    reason_code?: string | null;
    multiple?: number | null;
    yield_pct?: number | null;
    market_cap_basis_date?: string;
    price_basis_date?: string;
    statement_basis_date?: string;
    handoff?: string;
  };
  sections?: Record<string, { status?: string; reason_code?: string | null }>;
  sources?: string[];
  limitations?: string[];
};

type IndexedPoint = { point: TurnaroundPoint; index: number };
type WindowSize = 8 | 12 | 20;

const finite = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value);
const fmt = (value: unknown, digits = 1) => finite(value)
  ? value.toLocaleString("ko-KR", { maximumFractionDigits: digits })
  : "-";
const signed = (value: unknown, suffix = "%") => finite(value)
  ? `${value > 0 ? "+" : ""}${fmt(value)}${suffix}`
  : "-";
const compact = (value: unknown) => {
  if (!finite(value)) return "-";
  const absolute = Math.abs(value);
  if (absolute >= 1_000_000_000) return `${fmt(value / 1_000_000_000, 2)}B`;
  if (absolute >= 1_000_000) return `${fmt(value / 1_000_000, 2)}M`;
  if (absolute >= 1_000) return `${fmt(value / 1_000, 2)}K`;
  return fmt(value, 1);
};
const slotLabel = (point?: TurnaroundPoint) => point?.slot_key || point?.period_end || "-";

const metricLabels: Record<string, string> = {
  revenue: "매출",
  gross_profit: "매출총이익",
  operating_income: "영업이익",
  ocf: "영업현금흐름",
  capex: "자본지출",
};

const hasDerivedMetric = (point: TurnaroundPoint | undefined, metrics: string[]) => (
  (point?.derived_metrics || []).some((metric) => metrics.includes(metric))
);

const ttmHasDerivedMetric = (point: TurnaroundPoint | undefined, metrics: string[]) => (
  (point?.ttm_derived_metrics || []).some((metric) => metrics.includes(metric))
);

const primaryDerivation = (point: TurnaroundPoint | undefined, metrics: string[]) => {
  for (const metric of metrics) {
    const provenance = point?.metric_provenance?.[metric];
    if (provenance?.source_kind === "FILING_DERIVED") return { metric, provenance };
  }
  return null;
};

const derivationFormula = (provenance?: MetricProvenance) => {
  const operands = provenance?.operands || [];
  if (provenance?.rule === "fy_minus_q1_q2_q3" && operands.length >= 4) {
    return `FY ${compact(operands[0].value)} − Q1 ${compact(operands[1].value)} − Q2 ${compact(operands[2].value)} − Q3 ${compact(operands[3].value)}`;
  }
  if (provenance?.rule === "h1_minus_q1" && operands.length >= 2) {
    return `H1 ${compact(operands[0].value)} − Q1 ${compact(operands[1].value)}`;
  }
  if (provenance?.rule === "nine_months_minus_h1" && operands.length >= 2) {
    return `9M ${compact(operands[0].value)} − H1 ${compact(operands[1].value)}`;
  }
  if (provenance?.rule === "revenue_minus_cost" && operands.length >= 2) {
    return `매출 ${compact(operands[0].value)} − 원가 ${compact(operands[1].value)}`;
  }
  return null;
};

export function contiguousTurnaroundSegments(
  points: TurnaroundPoint[],
  key: keyof TurnaroundPoint,
): IndexedPoint[][] {
  const segments: IndexedPoint[][] = [];
  points.forEach((point, index) => {
    if (point.status !== "AVAILABLE" || !finite(point[key])) return;
    const current = segments[segments.length - 1];
    if (!current || current[current.length - 1].index !== index - 1) {
      segments.push([{ point, index }]);
    } else {
      current.push({ point, index });
    }
  });
  return segments;
}

function pointerIndex(
  event: React.MouseEvent<SVGSVGElement>,
  count: number,
  left: number,
  width: number,
  viewWidth: number,
) {
  const rect = event.currentTarget.getBoundingClientRect();
  const cursor = (event.clientX - rect.left) / rect.width * viewWidth;
  return Math.round(Math.max(0, Math.min(1, (cursor - left) / width)) * Math.max(0, count - 1));
}

function WindowSelector({ value, onChange }: { value: WindowSize; onChange: (value: WindowSize) => void }) {
  const options: { value: WindowSize; label: string }[] = [
    { value: 8, label: "8분기" },
    { value: 12, label: "12분기" },
    { value: 20, label: "20분기" },
  ];
  return <div className="turnaround-window-selector" aria-label="표시 분기 선택">
    {options.map((option) => <button key={option.value} type="button" aria-pressed={value === option.value} onClick={() => onChange(option.value)}>{option.label}</button>)}
  </div>;
}

type MilestoneDisplayState = "MET" | "ESTABLISHED" | "NOT_MET" | "UNKNOWN";
type MilestoneDisplayItem = {
  key: string;
  label: string;
  status: MilestoneDisplayState;
  detail: string;
};

const milestoneHeadlineLabels: Record<string, string> = {
  PER_READY: "PER 적용 가능",
  PER_CANDIDATE: "PER 후보",
  EARNINGS_TURN: "EPS 양전 신호",
  CASH_FLOW_TURN: "현금흐름 전환",
  OPERATING_IMPROVEMENT: "영업 개선",
  LOSS_BASELINE: "손실 기준",
  UNCONFIRMED: "근거 확인 중",
};

const analysisStatusLabels: Record<string, string> = {
  READY: "분석 가능",
  PARTIAL: "근거 일부",
  BLOCKED: "분석 전",
};

function MilestoneRail({ model }: { model: TurnaroundPayload["milestones"] }) {
  const milestones = model?.milestones || {};
  const operating = milestones.OPERATING_IMPROVEMENT || {};
  const cash = milestones.CASH_FLOW_TURN || {};
  const earnings = milestones.EARNINGS_TURN || {};
  const perCandidate = milestones.PER_CANDIDATE || {};
  const perReady = milestones.PER_READY || {};
  const operatingEvidence = operating.evidence || {};
  const cashEvidence = cash.evidence || {};
  const currentOperatingMargin = operatingEvidence.current_operating_margin_pct;
  const currentTtmEps = earnings.evidence?.current_ttm_eps;
  const operatingEstablished = finite(currentOperatingMargin)
    && currentOperatingMargin > 0
    && !operatingEvidence.operating_margin_improvement;
  const epsEstablished = perCandidate.status === "MET"
    || perReady.status === "MET"
    || (finite(currentTtmEps) && currentTtmEps > 0);
  const unresolved = (status?: string): MilestoneDisplayState => (
    status === "UNKNOWN" || status === "UNCONFIRMED" ? "UNKNOWN" : "NOT_MET"
  );
  const operatingBaseMet = Boolean(
    operatingEvidence.revenue_direction || operatingEvidence.gross_margin_improvement,
  );
  const items: MilestoneDisplayItem[] = [
    { key: "REVENUE_GP", label: "매출 성장 / GP 개선", status: operatingBaseMet ? "MET" : unresolved(operating.status), detail: operatingBaseMet ? "확인" : "아직 미확인" },
    { key: "OPERATING_IMPROVEMENT", label: "영업 수익성 개선", status: operatingEvidence.operating_margin_improvement ? "MET" : operatingEstablished ? "ESTABLISHED" : unresolved(operating.status), detail: operatingEvidence.operating_margin_improvement ? "개선 확인" : operatingEstablished ? "흑자 · 개선폭 미달" : "아직 미확인" },
    { key: "CASH_FLOW_TURN", label: "OCF 양수 지속", status: cash.status === "MET" ? "MET" : unresolved(cash.status), detail: cash.status === "MET" ? "확인" : "아직 미확인" },
    { key: "FCF_TURN", label: "FCF 양수", status: cashEvidence.fcf_confirmed ? "MET" : unresolved(cash.status), detail: cashEvidence.fcf_confirmed ? "확인" : "아직 미확인" },
    { key: "EARNINGS_TURN", label: epsEstablished ? "TTM EPS 양수" : "EPS 양전 신호", status: earnings.status === "MET" ? "MET" : epsEstablished ? "ESTABLISHED" : unresolved(earnings.status), detail: earnings.status === "MET" ? "전환 확인" : epsEstablished ? "이미 양수" : "아직 미확인" },
    { key: "PER_READY", label: "PER 적용 가능", status: perReady.status === "MET" ? "MET" : unresolved(perReady.status), detail: perReady.status === "MET" ? "적용 가능" : "아직 미확인" },
  ];
  const headline = model?.headline || "LOSS_BASELINE";
  const headlineLabel = milestoneHeadlineLabels[headline] || headline.replaceAll("_", " ");
  const analysisStatus = model?.status || "BLOCKED";
  return <section className="turnaround-stage-panel">
    <div className="turnaround-section-head"><div><span>전환 단계</span><h3>{headlineLabel}</h3><p>영업·현금·이익 근거를 서로 독립적으로 확인합니다.</p></div><span className={`turnaround-status status-${analysisStatus}`}>{analysisStatusLabels[analysisStatus] || analysisStatus}</span></div>
    <div className="turnaround-milestone-rail">{items.map((item) => {
      const tone = item.status === "MET" ? "met" : item.status === "ESTABLISHED" ? "established" : item.status === "UNKNOWN" ? "unconfirmed" : "not-met";
      const icon = item.status === "MET" ? "✓" : item.status === "ESTABLISHED" ? "●" : item.status === "UNKNOWN" ? "?" : "–";
      return <div key={item.key} className={`milestone milestone-${tone}`}><span aria-hidden="true">{icon}</span><strong>{item.label}</strong><small>{item.status === "UNKNOWN" ? "근거 부족" : item.detail}</small></div>;
    })}</div>
    {model?.evidence?.burn_improving ? <p className="turnaround-support-note">현금 소진 속도는 개선 중이지만 현금흐름 전환과 동일하게 보지 않습니다.</p> : null}
  </section>;
}

function OperatingChart({ points }: { points: TurnaroundPoint[] }) {
  const [selected, setSelected] = useState(Math.max(0, points.length - 1));
  useEffect(() => setSelected(Math.max(0, points.length - 1)), [points.length]);
  if (!points.length) return <div className="empty">영업 전환을 계산할 분기 근거가 없습니다.</div>;
  const left = 60, width = 800, viewWidth = 920;
  const operatingMetrics = ["revenue", "gross_profit", "operating_income"];
  const x = (index: number) => left + index / Math.max(1, points.length - 1) * width;
  const growthValues = points.map((point) => point.revenue_yoy_pct).filter(finite);
  const growthMin = Math.min(0, ...growthValues), growthMax = Math.max(0, ...growthValues);
  const growthRange = Math.max(1, growthMax - growthMin);
  const growthY = (value: number) => 24 + (growthMax - value) / growthRange * 120;
  const growthZero = growthY(0);
  const marginValues = points.flatMap((point) => [point.ttm_gross_margin_pct, point.ttm_operating_margin_pct]).filter(finite);
  const marginMin = Math.min(0, ...marginValues), marginMax = Math.max(0, ...marginValues);
  const marginRange = Math.max(1, marginMax - marginMin);
  const marginY = (value: number) => 205 + (marginMax - value) / marginRange * 120;
  const marginZero = marginY(0);
  const line = (segment: IndexedPoint[], key: "ttm_gross_margin_pct" | "ttm_operating_margin_pct") => segment.map(({ point, index }, itemIndex) => `${itemIndex ? "L" : "M"}${x(index).toFixed(1)},${marginY(point[key] as number).toFixed(1)}`).join(" ");
  const active = points[Math.min(selected, points.length - 1)];
  const activeDerivation = primaryDerivation(active, operatingMetrics);
  const activeFormula = derivationFormula(activeDerivation?.provenance);
  const activeSourceDerived = hasDerivedMetric(active, operatingMetrics);
  const activeTtmValueAvailable = finite(active?.ttm_gross_margin_pct)
    || finite(active?.ttm_operating_margin_pct);
  const activeTtmDerived = activeTtmValueAvailable
    && ttmHasDerivedMetric(active, operatingMetrics);
  return <div className="turnaround-chart-shell">
    <div className="turnaround-chart-legend">
      <span className="legend-revenue">매출 YoY</span>
      <span className="legend-gross">TTM GP margin</span>
      <span className="legend-operating">TTM 영업 margin</span>
      <span className="legend-derived">공시 기반 산출</span>
    </div>
    <svg viewBox="0 0 920 375" role="img" aria-label="그래프 1 · 영업 전환" onMouseMove={(event) => setSelected(pointerIndex(event, points.length, left, width, viewWidth))} onMouseLeave={() => setSelected(points.length - 1)}>
      <text className="turnaround-panel-label" x={left} y="17">QUARTERLY REVENUE YOY</text>
      <line className="zero-axis" x1={left} x2={left + width} y1={growthZero} y2={growthZero}/>
      {points.map((point, index) => !finite(point.revenue_yoy_pct) ? null : <rect key={`revenue-${index}`} className={point.revenue_yoy_pct >= 0 ? "turnaround-bar-positive" : "turnaround-bar-negative"} x={x(index) - Math.min(16, width / points.length * .3)} y={Math.min(growthY(point.revenue_yoy_pct), growthZero)} width={Math.min(32, width / points.length * .6)} height={Math.max(1, Math.abs(growthY(point.revenue_yoy_pct) - growthZero))}/>)}
      <text className="turnaround-panel-label" x={left} y="190">TTM MARGINS</text>
      <line className="zero-axis" x1={left} x2={left + width} y1={marginZero} y2={marginZero}/>
      {contiguousTurnaroundSegments(points, "ttm_gross_margin_pct").map((segment, index) => <path key={`gross-${index}`} className="turnaround-line-gross" d={line(segment, "ttm_gross_margin_pct")}/>)}
      {contiguousTurnaroundSegments(points, "ttm_operating_margin_pct").map((segment, index) => <path key={`operating-${index}`} className="turnaround-line-operating" d={line(segment, "ttm_operating_margin_pct")}/>)}
      <line className="hover-rule" x1={x(selected)} x2={x(selected)} y1="24" y2="325"/>
      {points.map((point, index) => hasDerivedMetric(point, operatingMetrics) ? <circle key={`derived-${index}`} className="turnaround-derived-marker" cx={x(index)} cy="334" r="4"><title>{`${slotLabel(point)} 공시 기반 산출`}</title></circle> : null)}
      {points.map((point, index) => index % Math.max(1, Math.ceil(points.length / 6)) === 0 || index === points.length - 1 ? <text key={`label-${index}`} className="axis-label" x={x(index)} y="355" textAnchor={index === 0 ? "start" : index === points.length - 1 ? "end" : "middle"}>{slotLabel(point)}</text> : null)}
    </svg>
    <div className="turnaround-inspector">
      <div className="turnaround-derived-heading">
        <strong>{slotLabel(active)}</strong>
        {activeSourceDerived ? <span className="turnaround-derived-badge">공시 기반 산출</span> : null}
      </div>
      <span>분기 매출 {compact(active?.revenue)}</span>
      <span>분기 영업 {compact(active?.operating_income)}</span>
      <span>매출 YoY {signed(active?.revenue_yoy_pct)}</span>
      <span>TTM GP {signed(active?.ttm_gross_margin_pct)}</span>
      <span>TTM 영업 {signed(active?.ttm_operating_margin_pct)}</span>
      {activeDerivation && activeFormula ? <small className="turnaround-derived-detail">{metricLabels[activeDerivation.metric] || activeDerivation.metric}: {activeFormula}</small> : null}
      {activeTtmDerived ? <small className="turnaround-derived-note">TTM 지표에 공시 기반 산출값 포함</small> : null}
      <small>filing 공개 {active?.available_at || "-"}</small>
    </div>
  </div>;
}
function CashChart({ points }: { points: TurnaroundPoint[] }) {
  const [selected, setSelected] = useState(Math.max(0, points.length - 1));
  useEffect(() => setSelected(Math.max(0, points.length - 1)), [points.length]);
  if (!points.length) return <div className="empty">현금 전환을 계산할 분기 근거가 없습니다.</div>;
  const left = 60, width = 800, top = 35, height = 250, viewWidth = 920;
  const cashMetrics = ["ocf", "capex"];
  const x = (index: number) => left + index / Math.max(1, points.length - 1) * width;
  const values = points.flatMap((point) => [point.ttm_ocf, point.ttm_fcf]).filter(finite);
  const min = Math.min(0, ...values), max = Math.max(0, ...values), range = Math.max(1, max - min);
  const y = (value: number) => top + (max - value) / range * height;
  const zero = y(0);
  const barWidth = Math.min(15, width / points.length * .24);
  const active = points[Math.min(selected, points.length - 1)];
  const activeDerivation = primaryDerivation(active, cashMetrics);
  const activeFormula = derivationFormula(activeDerivation?.provenance);
  const activeSourceDerived = hasDerivedMetric(active, cashMetrics);
  const activeTtmValueAvailable = finite(active?.ttm_ocf) || finite(active?.ttm_fcf);
  const activeTtmDerived = activeTtmValueAvailable
    && ttmHasDerivedMetric(active, cashMetrics);
  return <div className="turnaround-chart-shell">
    <div className="turnaround-chart-legend">
      <span className="legend-ocf">TTM OCF</span>
      <span className="legend-fcf">TTM FCF proxy</span>
      <span className="legend-derived">공시 기반 산출</span>
    </div>
    <svg viewBox="0 0 920 340" role="img" aria-label="그래프 2 · 현금 전환" onMouseMove={(event) => setSelected(pointerIndex(event, points.length, left, width, viewWidth))} onMouseLeave={() => setSelected(points.length - 1)}>
      <line className="zero-axis" x1={left} x2={left + width} y1={zero} y2={zero}/>
      {points.flatMap((point, index) => ([
        { key: "ocf", value: point.ttm_ocf, offset: -barWidth - 1 },
        { key: "fcf", value: point.ttm_fcf, offset: 1 },
      ]).map((item) => !finite(item.value) ? null : <rect key={`${item.key}-${index}`} className={`turnaround-cash-bar cash-${item.key} ${item.value < 0 ? "cash-negative" : ""}`} x={x(index) + item.offset} y={Math.min(y(item.value), zero)} width={barWidth} height={Math.max(1, Math.abs(y(item.value) - zero))}/>))}
      <line className="hover-rule" x1={x(selected)} x2={x(selected)} y1={top} y2={top + height}/>
      {points.map((point, index) => hasDerivedMetric(point, cashMetrics) ? <circle key={`cash-derived-${index}`} className="turnaround-derived-marker" cx={x(index)} cy="296" r="4"><title>{`${slotLabel(point)} 공시 기반 산출`}</title></circle> : null)}
      {points.map((point, index) => index % Math.max(1, Math.ceil(points.length / 6)) === 0 || index === points.length - 1 ? <text key={`cash-label-${index}`} className="axis-label" x={x(index)} y="318" textAnchor={index === 0 ? "start" : index === points.length - 1 ? "end" : "middle"}>{slotLabel(point)}</text> : null)}
    </svg>
    <div className="turnaround-inspector">
      <div className="turnaround-derived-heading">
        <strong>{slotLabel(active)}</strong>
        {activeSourceDerived ? <span className="turnaround-derived-badge">공시 기반 산출</span> : null}
      </div>
      <span>TTM OCF {compact(active?.ttm_ocf)}</span>
      <span>TTM FCF {compact(active?.ttm_fcf)}</span>
      <span>분기 OCF {compact(active?.ocf)}</span>
      {activeDerivation && activeFormula ? <small className="turnaround-derived-detail">{metricLabels[activeDerivation.metric] || activeDerivation.metric}: {activeFormula}</small> : null}
      {activeTtmDerived ? <small className="turnaround-derived-note">TTM 지표에 공시 기반 산출값 포함</small> : null}
      <small>filing 공개 {active?.available_at || "-"}</small>
    </div>
  </div>;
}
const riskLabel: Record<string, string> = {
  OK: "안정",
  WATCH: "확인 필요",
  HIGH: "높은 위험",
  NOT_APPLICABLE: "적용 전",
  NOT_MEANINGFUL: "해석 불가",
};

function RiskCards({ risks }: { risks: TurnaroundPayload["risks"] }) {
  const runway = risks?.cash_runway || {};
  const debt = risks?.debt_service || {};
  const dilution = risks?.dilution || {};
  const cards = [
    { key: "runway", title: "현금 runway", status: String(runway.status || "NOT_APPLICABLE"), value: finite(runway.quarters) ? `${fmt(runway.quarters)}분기` : "산정 전", detail: `TTM FCF ${compact(runway.ttm_fcf)}` },
    { key: "debt", title: "순부채 · 이자", status: String(debt.status || "NOT_MEANINGFUL"), value: finite(debt.interest_coverage) ? `${fmt(debt.interest_coverage, 2)}x` : "의미 없음", detail: `순부채 ${compact(debt.net_debt)}` },
    { key: "dilution", title: "희석주식 증가", status: String(dilution.status || "NOT_APPLICABLE"), value: signed(dilution.yoy_pct), detail: "split-neutral YoY" },
  ];
  return <section className="turnaround-risk-section"><div className="turnaround-section-head"><div><span>생존·자본 위험</span><h3>전환 전 버틸 수 있는가</h3><p>위험 신호는 milestone과 별도로 표시합니다.</p></div></div><div className="turnaround-risk-grid">{cards.map((card) => <article key={card.key} className={`turnaround-risk-card risk-${card.status.toLowerCase()}`}><span>{card.title}</span><strong>{card.value}</strong><small>{riskLabel[card.status] || card.status} · {card.detail}</small></article>)}</div>{risks?.flags?.length ? <ul className="turnaround-risk-flags">{risks.flags.map((flag) => <li key={flag}>{flag.replaceAll("_", " ")}</li>)}</ul> : null}</section>;
}

const methodLabel: Record<string, string> = {
  P_E_HANDOFF: "PER 상대가치로 전환",
  P_FCF: "P/FCF",
  P_OCF: "P/OCF",
  EV_EBITDA: "EV/EBITDA",
  EV_GROSS_PROFIT: "EV/Gross Profit",
  EV_SALES: "EV/Sales",
};
const reasonLabel: Record<string, string> = {
  INPUT_STALE: "시장가치 입력 기준일이 가격 기준일과 7일 넘게 벌어졌습니다.",
  COMPONENT_MISSING: "현금·투자자산·부채 또는 정렬된 재무제표 근거가 부족합니다.",
  UNIT_UNVERIFIED: "USD·주당 단위를 검증하지 못했습니다.",
  SECTOR_METHOD_UNSUPPORTED: "이 업종에는 일반 기업용 배수를 적용하지 않습니다.",
  NEGATIVE_OR_ZERO_DENOMINATOR: "현재 양수인 가치평가 분모가 없습니다.",
  NEGATIVE_OR_ZERO_NUMERATOR: "현재 기업가치 분자가 0 이하입니다.",
};

function ValuationCard({ valuation }: { valuation: TurnaroundPayload["valuation"] }) {
  const ready = valuation?.status === "READY";
  const method = valuation?.method ? methodLabel[valuation.method] || valuation.method : "생존 지표 우선";
  return <section className={`turnaround-valuation-card valuation-${(valuation?.status || "BLOCKED").toLowerCase()}`}><div><span>현재 적용 가능한 가치평가 프레임</span><h3>{method}</h3><p>{ready ? "현재 단계에서 성립하는 가장 우선순위 높은 방법입니다." : reasonLabel[valuation?.reason_code || ""] || "숫자를 만들기보다 영업·현금 전환 근거를 먼저 확인합니다."}</p></div>{ready && valuation?.method !== "P_E_HANDOFF" ? <div className="turnaround-valuation-number"><strong>{fmt(valuation?.multiple, 2)}x</strong>{finite(valuation?.yield_pct) ? <span>yield {signed(valuation.yield_pct)}</span> : null}</div> : <span className="turnaround-status">{valuation?.status || "BLOCKED"}</span>}<footer>가격 {valuation?.price_basis_date || "-"} · 시장가치 {valuation?.market_cap_basis_date || "-"} · 재무제표 {valuation?.statement_basis_date || "-"}</footer></section>;
}

export default function TurnaroundAnalysis({ payload }: { payload?: TurnaroundPayload }) {
  const [windowSize, setWindowSize] = useState<WindowSize>(12);
  const timeline = payload?.series?.timeline || [];
  const points = useMemo(() => timeline.slice(-windowSize), [timeline, windowSize]);
  if (!payload || payload.status === "NOT_SELECTED") return <div className="empty">전환 분석할 종목을 먼저 선택하세요.</div>;
  if (payload.status === "ERROR" || payload.status === "NOT_APPLICABLE") return <section className="stock-state"><span>{payload.status}</span><h3>전환 분석을 표시할 수 없습니다</h3><p>{payload.reason || "저장된 identity와 재무제표 구조를 확인해 주세요."}</p></section>;
  return <div className="turnaround-analysis" data-status={payload.status}>
    <MilestoneRail model={payload.milestones}/>
    <section className="turnaround-chart-section"><div className="turnaround-section-head"><div><span>영업 · 현금 전환</span><h3>분기 흐름을 같은 시간축에서 확인</h3><p>결측 분기는 연결·보간하지 않고 0 기준선을 항상 유지합니다.</p></div><WindowSelector value={windowSize} onChange={setWindowSize}/></div><div className="turnaround-chart-grid"><article><h4>그래프 1 · 영업 전환</h4><OperatingChart points={points}/></article><article><h4>그래프 2 · 현금 전환</h4><CashChart points={points}/></article></div></section>
    <RiskCards risks={payload.risks}/>
    <ValuationCard valuation={payload.valuation}/>
    <details className="evidence turnaround-evidence"><summary>전환 분석 자료 출처·한계 보기</summary><ul>{(payload.sources || []).map((source) => <li key={source}>{source}</li>)}{(payload.limitations || []).map((item) => <li key={item}>{item}</li>)}</ul></details>
  </div>;
}
