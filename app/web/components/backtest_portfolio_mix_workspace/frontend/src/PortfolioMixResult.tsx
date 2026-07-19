import React, { useMemo, useState } from "react"

type KpiRow = {
  id: string
  label: string
  value: number | null
  value_label: string
}

type ResultRow = {
  date: string
  date_label: string
  month_label: string
  balance: number
  balance_label: string
  index_value: number | null
  index_label: string
  cumulative_return: number | null
  cumulative_return_label: string
  return_value: number | null
  return_label: string
  available: boolean
}

type ContributionSegment = {
  strategy_label: string
  role_label: string
  target_weight: number | null
  target_weight_label: string
  amount: number | null
  amount_label: string
  share: number | null
  share_label: string
}

type ContributionRow = {
  date: string
  date_label: string
  segments: ContributionSegment[]
}

type DataTrustRow = {
  strategy_label: string
  requested_end_label: string
  actual_end_label: string
  result_rows_label: string
  price_freshness_label: string
  interpretation: string
}

export type MixResultEvidence = {
  identity: {
    title: string
    component_summary: string
    period_label: string
    date_policy_label: string
  }
  kpis: KpiRow[]
  equity_chart: {
    title: string
    description: string
    rows: ResultRow[]
    desktop_ticks: string[]
    compact_ticks: string[]
  }
  monthly_returns: {
    title: string
    description: string
    chart_rows: ResultRow[]
    table_rows: ResultRow[]
  }
  contribution: {
    summary_rows: ContributionSegment[]
    timeline_rows: ContributionRow[]
  }
  calculation_basis: Array<{ title: string; description: string }>
  data_trust_rows: DataTrustRow[]
}

const CHART_WIDTH = 720
const CHART_HEIGHT = 280
const PLOT_LEFT = 54
const PLOT_RIGHT = 24
const PLOT_TOP = 20
const PLOT_BOTTOM = 42
const HUNDRED = 100

function clamp(value: number, minimum: number, maximum: number) {
  return Math.min(maximum, Math.max(minimum, value))
}

function xForIndex(index: number, count: number) {
  const plotWidth = CHART_WIDTH - PLOT_LEFT - PLOT_RIGHT
  return count <= 1 ? PLOT_LEFT : PLOT_LEFT + (index / (count - 1)) * plotWidth
}

function nearestIndex(clientX: number, left: number, width: number, count: number) {
  if (count <= 1 || width <= 0) return 0
  const ratio = clamp((clientX - left) / width, 0, 1)
  return Math.round(ratio * (count - 1))
}

function tooltipLeft(x: number) {
  return `${clamp((x / CHART_WIDTH) * HUNDRED, 12, 88)}%`
}

function ChartEmpty({ children }: { children: React.ReactNode }) {
  return <div className="mix-chart-empty">{children}</div>
}

function EquityChart({ model }: { model: MixResultEvidence["equity_chart"] }) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null)
  const rows = model.rows
  const values = rows.map((row) => row.index_value).filter((value): value is number => value !== null)
  const minimum = values.length ? Math.min(...values) : 0
  const maximum = values.length ? Math.max(...values) : 0
  const spread = maximum - minimum || 1
  const plotHeight = CHART_HEIGHT - PLOT_TOP - PLOT_BOTTOM
  const point = (row: ResultRow, index: number) => ({
    x: xForIndex(index, rows.length),
    y: PLOT_TOP + ((maximum - (row.index_value ?? minimum)) / spread) * plotHeight,
  })
  const points = rows.map((row, index) => point(row, index))
  const active = activeIndex === null ? null : rows[activeIndex]
  const activePoint = activeIndex === null ? null : points[activeIndex]
  const tickX = (date: string) => xForIndex(Math.max(0, rows.findIndex((row) => row.date === date)), rows.length)
  const move = (event: React.PointerEvent<SVGSVGElement>) => {
    const rect = event.currentTarget.getBoundingClientRect()
    setActiveIndex(nearestIndex(event.clientX, rect.left, rect.width, rows.length))
  }
  const clearActive = () => setActiveIndex(null)
  const shift = (offset: number) => setActiveIndex((current) => clamp((current ?? 0) + offset, 0, rows.length - 1))

  return (
    <article className="mix-chart-card">
      <header><div><h4>{model.title}</h4><p>{model.description}</p></div><span>기준 100</span></header>
      {rows.length === 0 ? <ChartEmpty>표시할 누적 성과가 없습니다.</ChartEmpty> : (
        <div className="mix-chart-stage">
          <svg
            className="mix-chart-svg"
            viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
            role="img"
            aria-label="Portfolio Mix 누적 성과 차트"
            tabIndex={0}
            onPointerMove={move}
            onPointerLeave={clearActive}
            onMouseLeave={clearActive}
            onPointerCancel={clearActive}
            onFocus={() => setActiveIndex(rows.length - 1)}
            onBlur={clearActive}
            onKeyDown={(event) => {
              if (event.key === "ArrowLeft") shift(-1)
              if (event.key === "ArrowRight") shift(1)
            }}
          >
            <line className="mix-chart-grid-line" x1={PLOT_LEFT} x2={CHART_WIDTH - PLOT_RIGHT} y1={PLOT_TOP} y2={PLOT_TOP} />
            <line className="mix-chart-grid-line" x1={PLOT_LEFT} x2={CHART_WIDTH - PLOT_RIGHT} y1={PLOT_TOP + plotHeight / 2} y2={PLOT_TOP + plotHeight / 2} />
            <line className="mix-chart-grid-line" x1={PLOT_LEFT} x2={CHART_WIDTH - PLOT_RIGHT} y1={PLOT_TOP + plotHeight} y2={PLOT_TOP + plotHeight} />
            <text className="mix-chart-axis-label" x={8} y={PLOT_TOP + 4}>{maximum.toFixed(1)}</text>
            <text className="mix-chart-axis-label" x={8} y={PLOT_TOP + plotHeight + 4}>{minimum.toFixed(1)}</text>
            <polyline className="mix-equity-line" points={points.map(({ x, y }) => `${x},${y}`).join(" ")} />
            {model.desktop_ticks.map((date) => <text key={`desktop-${date}`} className="mix-chart-tick is-desktop" x={tickX(date)} y={CHART_HEIGHT - 12}>{rows.find((row) => row.date === date)?.month_label}</text>)}
            {model.compact_ticks.map((date) => <text key={`compact-${date}`} className="mix-chart-tick is-compact" x={tickX(date)} y={CHART_HEIGHT - 12}>{rows.find((row) => row.date === date)?.month_label}</text>)}
            {activePoint && <><line className="mix-chart-crosshair" x1={activePoint.x} x2={activePoint.x} y1={PLOT_TOP} y2={PLOT_TOP + plotHeight} /><circle className="mix-chart-marker" cx={activePoint.x} cy={activePoint.y} r={5} /></>}
          </svg>
          {active && activePoint && <div className="mix-chart-tooltip" style={{ left: tooltipLeft(activePoint.x) }} role="status"><strong>{active.date_label}</strong><span>성과 지수 {active.index_label}</span><span>누적 수익률 {active.cumulative_return_label}</span><span>평가액 {active.balance_label}</span></div>}
        </div>
      )}
    </article>
  )
}

function MonthlyReturnChart({ model }: { model: MixResultEvidence["monthly_returns"] }) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null)
  const rows = model.chart_rows
  const plotHeight = CHART_HEIGHT - PLOT_TOP - PLOT_BOTTOM
  const baseline = PLOT_TOP + plotHeight / 2
  const maximumAbsolute = Math.max(...rows.map((row) => Math.abs(row.return_value ?? 0)), 0.01)
  const barWidth = Math.max(2, Math.min(18, (CHART_WIDTH - PLOT_LEFT - PLOT_RIGHT) / Math.max(rows.length, 1) - 2))
  const active = activeIndex === null ? null : rows[activeIndex]
  const activeX = activeIndex === null ? null : xForIndex(activeIndex, rows.length)
  const move = (event: React.PointerEvent<SVGSVGElement>) => {
    const rect = event.currentTarget.getBoundingClientRect()
    setActiveIndex(nearestIndex(event.clientX, rect.left, rect.width, rows.length))
  }
  const clearActive = () => setActiveIndex(null)
  const shift = (offset: number) => setActiveIndex((current) => clamp((current ?? 0) + offset, 0, rows.length - 1))
  const tickRows = rows.length <= 3 ? rows : [rows[0], rows[Math.floor((rows.length - 1) / 2)], rows[rows.length - 1]]

  return (
    <article className="mix-chart-card">
      <header><div><h4>{model.title}</h4><p>{model.description}</p></div><span>월말 기준</span></header>
      {rows.length === 0 ? <ChartEmpty>계산 가능한 월별 수익률이 없습니다.</ChartEmpty> : (
        <div className="mix-chart-stage">
          <svg
            className="mix-chart-svg"
            viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
            role="img"
            aria-label="Portfolio Mix 월별 수익률 차트"
            tabIndex={0}
            onPointerMove={move}
            onPointerLeave={clearActive}
            onMouseLeave={clearActive}
            onPointerCancel={clearActive}
            onFocus={() => setActiveIndex(rows.length - 1)}
            onBlur={clearActive}
            onKeyDown={(event) => {
              if (event.key === "ArrowLeft") shift(-1)
              if (event.key === "ArrowRight") shift(1)
            }}
          >
            <line className="mix-chart-zero-line" x1={PLOT_LEFT} x2={CHART_WIDTH - PLOT_RIGHT} y1={baseline} y2={baseline} />
            {rows.map((row, index) => {
              const value = row.return_value ?? 0
              const barHeight = Math.abs(value) / maximumAbsolute * (plotHeight / 2 - 8)
              const x = xForIndex(index, rows.length) - barWidth / 2
              const y = value >= 0 ? baseline - barHeight : baseline
              return <rect key={row.date} className={value >= 0 ? "mix-return-bar is-positive" : "mix-return-bar is-negative"} x={x} y={y} width={barWidth} height={Math.max(1, barHeight)} rx={2} />
            })}
            {tickRows.map((row) => <text key={row.date} className="mix-chart-tick" x={xForIndex(rows.indexOf(row), rows.length)} y={CHART_HEIGHT - 12}>{row.month_label}</text>)}
            {activeX !== null && <line className="mix-chart-crosshair" x1={activeX} x2={activeX} y1={PLOT_TOP} y2={PLOT_TOP + plotHeight} />}
          </svg>
          {active && activeX !== null && <div className="mix-chart-tooltip" style={{ left: tooltipLeft(activeX) }} role="status"><strong>{active.month_label}</strong><span>월 수익률 {active.return_label}</span><span>월말 평가액 {active.balance_label}</span></div>}
        </div>
      )}
    </article>
  )
}

function ContributionEvidence({ evidence }: { evidence: MixResultEvidence["contribution"] }) {
  return (
    <section className="mix-evidence-section">
      <div><h4>구성 전략 기여도</h4><p>목표 비중을 적용한 마지막 평가액과 Mix 내 비중입니다.</p></div>
      {evidence.summary_rows.length === 0 ? <ChartEmpty>표시할 구성 전략 기여도가 없습니다.</ChartEmpty> : <>
        <div className="mix-table-scroll"><table><thead><tr><th>구성 전략</th><th>역할</th><th>목표 비중</th><th>기여 평가액</th><th>Mix 비중</th></tr></thead><tbody>{evidence.summary_rows.map((row) => <tr key={row.strategy_label}><th>{row.strategy_label}</th><td>{row.role_label}</td><td>{row.target_weight_label}</td><td>{row.amount_label}</td><td>{row.share_label}</td></tr>)}</tbody></table></div>
        <div className="mix-contribution-timeline">{evidence.timeline_rows.map((row) => <div className="mix-contribution-row" key={row.date}><time>{row.date_label}</time><div><div className="mix-segment-bar" aria-label={`${row.date_label} 구성 전략 기여 평가액`}>{row.segments.map((segment) => <span key={`amount-${segment.strategy_label}`} style={{ width: segment.share_label === "계산값 없음" ? "0%" : segment.share_label }} title={`${segment.strategy_label}: ${segment.amount_label}`}>{segment.amount_label}</span>)}</div><div className="mix-segment-bar is-share" aria-label={`${row.date_label} 구성 전략 비중`}>{row.segments.map((segment) => <span key={`share-${segment.strategy_label}`} style={{ width: segment.share_label === "계산값 없음" ? "0%" : segment.share_label }} title={`${segment.strategy_label}: ${segment.share_label}`}>{segment.share_label}</span>)}</div></div></div>)}</div>
      </>}
    </section>
  )
}

function ResultEvidenceDetails({ evidence }: { evidence: MixResultEvidence }) {
  return (
    <details className="mix-result-details">
      <summary>상세 결과 근거</summary>
      <div className="mix-result-details-body">
        <ContributionEvidence evidence={evidence.contribution} />
        <section className="mix-evidence-section"><div><h4>월별 결과 표</h4><p>차트에서 제외된 계산 불가 월도 원본 날짜 순서로 남깁니다.</p></div>{evidence.monthly_returns.table_rows.length === 0 ? <ChartEmpty>표시할 월별 결과가 없습니다.</ChartEmpty> : <div className="mix-table-scroll"><table><thead><tr><th>기준 월</th><th>월 수익률</th><th>월말 평가액</th><th>누적 수익률</th></tr></thead><tbody>{evidence.monthly_returns.table_rows.map((row) => <tr key={row.date}><th>{row.month_label}</th><td>{row.return_label}</td><td>{row.balance_label}</td><td>{row.cumulative_return_label}</td></tr>)}</tbody></table></div>}</section>
        <section className="mix-evidence-section"><div><h4>계산 기준</h4><p>이 결과가 어떤 공통 날짜와 비중 원칙으로 만들어졌는지 설명합니다.</p></div><div className="mix-basis-grid">{evidence.calculation_basis.map((item) => <article key={item.title}><strong>{item.title}</strong><p>{item.description}</p></article>)}</div></section>
        <section className="mix-evidence-section"><div><h4>구성 전략 데이터 기준</h4><p>요청 종료일과 실제 계산 종료일, 가격 최신성 해석을 함께 확인합니다.</p></div>{evidence.data_trust_rows.length === 0 ? <ChartEmpty>표시할 데이터 기준이 없습니다.</ChartEmpty> : <div className="mix-table-scroll"><table><thead><tr><th>구성 전략</th><th>요청 종료일</th><th>실제 종료일</th><th>결과 행</th><th>가격 최신성</th><th>해석</th></tr></thead><tbody>{evidence.data_trust_rows.map((row) => <tr key={row.strategy_label}><th>{row.strategy_label}</th><td>{row.requested_end_label}</td><td>{row.actual_end_label}</td><td>{row.result_rows_label}</td><td>{row.price_freshness_label}</td><td>{row.interpretation}</td></tr>)}</tbody></table></div>}</section>
      </div>
    </details>
  )
}

export function PortfolioMixResult({ evidence }: { evidence: MixResultEvidence }) {
  return (
    <div className="mix-result-stack">
      <header className="mix-result-identity"><div><small>현재 실행 결과</small><h3>{evidence.identity.title}</h3></div><div><strong>{evidence.identity.component_summary}</strong><span>{evidence.identity.period_label} · {evidence.identity.date_policy_label}</span></div></header>
      <div className="mix-result-grid">{evidence.kpis.map((row) => <span key={row.id}><small>{row.label}</small><b>{row.value_label}</b></span>)}</div>
      <div className="mix-chart-grid"><EquityChart model={evidence.equity_chart} /><MonthlyReturnChart model={evidence.monthly_returns} /></div>
      <ResultEvidenceDetails evidence={evidence} />
    </div>
  )
}
