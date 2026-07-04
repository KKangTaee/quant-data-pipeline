import React from "react"
import { Streamlit } from "streamlit-component-lib"

type BacktestHandoffActionProps = {
  statusLabel: string
  tone: "positive" | "warning" | "danger" | "neutral"
  buttonLabel: string
  disabled: boolean
  reviewCount: number
  blockerCount: number
  boundaryText: string
}

const toneClass = (tone: BacktestHandoffActionProps["tone"]) =>
  ["positive", "warning", "danger", "neutral"].includes(tone) ? tone : "neutral"

export function BacktestHandoffAction(props: BacktestHandoffActionProps) {
  const submit = () => {
    if (props.disabled) return
    Streamlit.setComponentValue({
      action: "submit",
      source: "backtest_handoff_action",
    })
  }

  return (
    <section className={`bt-react-handoff bt-react-handoff--${toneClass(props.tone)}`}>
      <div className="bt-react-handoff__summary">
        <span>Source registration</span>
        <strong>{props.statusLabel}</strong>
        <em>
          Review {props.reviewCount} · Blocker {props.blockerCount}
        </em>
      </div>
      <button
        className="bt-react-handoff__button"
        disabled={props.disabled}
        onClick={submit}
        type="button"
      >
        {props.buttonLabel}
      </button>
      <p>{props.boundaryText}</p>
    </section>
  )
}
