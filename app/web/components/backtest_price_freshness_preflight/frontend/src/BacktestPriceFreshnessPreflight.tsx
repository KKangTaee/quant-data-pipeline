import React, { useEffect } from "react"
import { Streamlit } from "streamlit-component-lib"

type Tone = "positive" | "warning" | "danger" | "neutral"

type MetricItem = {
  label?: string
  value?: string
  detail?: string
}

type IssueRow = {
  label?: string
  value?: string
  detail?: string
  tone?: Tone
}

type BacktestPriceFreshnessPreflightProps = {
  statusLabel: string
  tone: Tone
  headline: string
  summary: string
  detail: string
  metricItems: MetricItem[]
  issueRows: IssueRow[]
  nextAction: string
  footnote: string
}

const toneClass = (tone: Tone | string | undefined): Tone =>
  ["positive", "warning", "danger", "neutral"].includes(String(tone)) ? (tone as Tone) : "neutral"

const compact = (value: unknown, fallback = "-"): string => {
  const text = String(value ?? "").trim()
  return text || fallback
}

export function BacktestPriceFreshnessPreflight(props: BacktestPriceFreshnessPreflightProps) {
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [props])

  const tone = toneClass(props.tone)
  const metricItems = props.metricItems.length > 0 ? props.metricItems : []
  const issueRows = props.issueRows.length > 0 ? props.issueRows : []

  return (
    <section className={`bt-react-freshness bt-react-freshness--${tone}`}>
      <header className="bt-react-freshness__head">
        <div>
          <div className="bt-react-freshness__kicker">Price Freshness Preflight</div>
          <h4>{compact(props.headline)}</h4>
          <p>{compact(props.summary, "")}</p>
        </div>
        <div className="bt-react-freshness__status">{compact(props.statusLabel)}</div>
      </header>

      <p className="bt-react-freshness__detail">{compact(props.detail, "")}</p>

      <div className="bt-react-freshness__metrics">
        {metricItems.map((item, index) => (
          <div className="bt-react-freshness__metric" key={`${item.label ?? "metric"}-${index}`}>
            <span>{compact(item.label)}</span>
            <b>{compact(item.value)}</b>
            {item.detail ? <small>{item.detail}</small> : null}
          </div>
        ))}
      </div>

      <div className="bt-react-freshness__issues">
        {issueRows.length > 0 ? (
          issueRows.map((item, index) => (
            <article
              className={`bt-react-freshness__issue bt-react-freshness__issue--${toneClass(item.tone)}`}
              key={`${item.label ?? "issue"}-${index}`}
            >
              <span>{compact(item.label)}</span>
              <strong>{compact(item.value)}</strong>
              <p>{compact(item.detail, "")}</p>
            </article>
          ))
        ) : (
          <article className="bt-react-freshness__issue bt-react-freshness__issue--positive">
            <span>Issue Summary</span>
            <strong>추가 조치 없음</strong>
            <p>현재 선택한 실행 종료 기준에서 missing 또는 stale 가격 문제가 감지되지 않았습니다.</p>
          </article>
        )}
      </div>

      <footer className="bt-react-freshness__footer">
        <strong>{compact(props.nextAction)}</strong>
        <span>{compact(props.footnote, "")}</span>
      </footer>
    </section>
  )
}
