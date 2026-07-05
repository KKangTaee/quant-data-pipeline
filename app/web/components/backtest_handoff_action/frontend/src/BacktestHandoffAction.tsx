import React, { useEffect } from "react"
import { Streamlit } from "streamlit-component-lib"

type Tone = "positive" | "warning" | "danger" | "neutral"

type HandoffCriterion = {
  label?: string
  value?: string
  tone?: Tone
}

type BacktestHandoffActionProps = {
  statusLabel: string
  tone: Tone
  summary: string
  score: string
  reasonTitle: string
  reasons: string[]
  criteria: HandoffCriterion[]
  actionText: string
  buttonLabel: string
  disabled: boolean
  reviewCount: number
  blockerCount: number
  boundaryText: string
}

const toneClass = (tone: Tone | string | undefined): Tone =>
  ["positive", "warning", "danger", "neutral"].includes(String(tone)) ? (tone as Tone) : "neutral"

export function BacktestHandoffAction(props: BacktestHandoffActionProps) {
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [props])

  const submit = () => {
    if (props.disabled) return
    Streamlit.setComponentValue({
      action: "submit",
      source: "backtest_handoff_action",
      nonce: `${Date.now()}`,
    })
  }

  const tone = toneClass(props.tone)
  const reasons = props.reasons.length > 0 ? props.reasons : ["막는 항목 없음"]
  const criteria = props.criteria.length > 0 ? props.criteria : [{ label: "상태", value: "-", tone: "neutral" }]

  return (
    <section className={`bt-react-handoff bt-react-handoff--${tone}`}>
      <header className="bt-react-handoff__head">
        <div>
          <div className="bt-react-handoff__kicker">2차 단계 진입 판단</div>
          <h4>2차 실전성 검증 Handoff</h4>
        </div>
        <div className="bt-react-handoff__status">{props.statusLabel}</div>
      </header>

      <div className="bt-react-handoff__body">
        <div className="bt-react-handoff__summary">
          <p>{props.summary}</p>
          <strong>진입 준비도 {props.score}</strong>
          <div className="bt-react-handoff__chips">
            {criteria.map((criterion, index) => (
              <div
                className={`bt-react-handoff__chip bt-react-handoff__chip--${toneClass(criterion.tone)}`}
                key={`${criterion.label ?? "criterion"}-${index}`}
              >
                <span>{criterion.label ?? "-"}</span>
                <b>{criterion.value ?? "-"}</b>
              </div>
            ))}
          </div>
        </div>

        <div className="bt-react-handoff__reasons">
          <div className="bt-react-handoff__reason-title">{props.reasonTitle}</div>
          <ul>
            {reasons.map((reason, index) => (
              <li key={`${reason}-${index}`}>{reason}</li>
            ))}
          </ul>
        </div>
      </div>

      <footer className="bt-react-handoff__action">
        <div>
          <div className="bt-react-handoff__action-label">
            {props.disabled ? "등록 보류" : "등록 가능"}
          </div>
          <div className="bt-react-handoff__action-text">{props.actionText}</div>
          <div className="bt-react-handoff__counts">
            2차 확인 {props.reviewCount} · 먼저 해결 {props.blockerCount}
          </div>
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
      </footer>
    </section>
  )
}
