import React, { useEffect } from "react"
import { Streamlit } from "streamlit-component-lib"

type Tone = "positive" | "warning" | "danger" | "neutral"

type MetricItem = {
  label?: string
  value?: string
  detail?: string
}

type BacktestPriceRefreshActionProps = {
  statusLabel: string
  tone: Tone
  summary: string
  detail: string
  metricItems: MetricItem[]
  actionText: string
  buttonLabel: string
  actionNote: string
  disabled: boolean
}

const toneClass = (tone: Tone | string | undefined): Tone =>
  ["positive", "warning", "danger", "neutral"].includes(String(tone)) ? (tone as Tone) : "neutral"

export function BacktestPriceRefreshAction(props: BacktestPriceRefreshActionProps) {
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [props])

  const submit = () => {
    if (props.disabled) return
    Streamlit.setComponentValue({
      action: "refresh",
      source: "backtest_price_refresh_action",
      nonce: `${Date.now()}`,
    })
  }

  const tone = toneClass(props.tone)
  const metricItems = props.metricItems.length > 0 ? props.metricItems : []

  return (
    <section className={`bt-react-price-refresh bt-react-price-refresh--${tone}`}>
      <header className="bt-react-price-refresh__head">
        <div>
          <div className="bt-react-price-refresh__kicker">가격 데이터 업데이트 가능</div>
          <h4>{props.summary}</h4>
          <p>{props.detail}</p>
        </div>
        <div className="bt-react-price-refresh__status">{props.statusLabel}</div>
      </header>

      <div className="bt-react-price-refresh__metrics">
        {metricItems.map((item, index) => (
          <div className="bt-react-price-refresh__metric" key={`${item.label ?? "metric"}-${index}`}>
            <span>{item.label ?? "-"}</span>
            <b>{item.value ?? "-"}</b>
            {item.detail ? <small>{item.detail}</small> : null}
          </div>
        ))}
      </div>

      <footer className="bt-react-price-refresh__action">
        <div>
          <div className="bt-react-price-refresh__action-label">
            {props.disabled ? "업데이트 보류" : "업데이트 가능"}
          </div>
          <div className="bt-react-price-refresh__action-text">{props.actionText}</div>
        </div>
        <button
          className="bt-react-price-refresh__button"
          disabled={props.disabled}
          onClick={submit}
          type="button"
        >
          {props.buttonLabel}
        </button>
        <p>{props.actionNote}</p>
      </footer>
    </section>
  )
}
