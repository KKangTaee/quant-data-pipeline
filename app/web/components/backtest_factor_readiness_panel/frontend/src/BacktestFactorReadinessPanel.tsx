import React, { useEffect } from "react"
import { Streamlit } from "streamlit-component-lib"

type Tone = "positive" | "warning" | "danger" | "neutral"

type ReadinessItem = {
  label?: string
  value?: string
  detail?: string
  tone?: Tone
}

type ReadinessCheck = {
  id?: string
  title?: string
  status?: string
  tone?: Tone
  summary?: string
  detail?: string
  metrics?: ReadinessItem[]
  issues?: ReadinessItem[]
}

type ReadinessAction = {
  label?: string
  detail?: string
  tone?: Tone
}

type BacktestFactorReadinessPanelProps = {
  status: string
  tone: Tone
  headline: string
  summary: string
  strategyLabel: string
  runRecommended: boolean
  checks: ReadinessCheck[]
  actions: ReadinessAction[]
}

const tones: Tone[] = ["positive", "warning", "danger", "neutral"]

const toneClass = (tone: Tone | string | undefined): Tone =>
  tones.includes(String(tone) as Tone) ? (tone as Tone) : "neutral"

const compact = (value: unknown, fallback = "-"): string => {
  const text = String(value ?? "").trim()
  return text || fallback
}

export function BacktestFactorReadinessPanel(props: BacktestFactorReadinessPanelProps) {
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [props])

  const tone = toneClass(props.tone)
  const checks = Array.isArray(props.checks) ? props.checks : []
  const actions = Array.isArray(props.actions) ? props.actions : []

  return (
    <section className={`bt-factor-readiness bt-factor-readiness--${tone}`}>
      <header className="bt-factor-readiness__head">
        <div>
          <div className="bt-factor-readiness__kicker">Factor Readiness</div>
          <h4>{compact(props.headline)}</h4>
          <p>{compact(props.summary, "")}</p>
          {props.strategyLabel ? <small>{props.strategyLabel}</small> : null}
        </div>
        <div className="bt-factor-readiness__state">
          <span>{compact(props.status).replaceAll("_", " ")}</span>
          <b>{props.runRecommended ? "RUN READY" : "CHECK FIRST"}</b>
        </div>
      </header>

      <div className="bt-factor-readiness__checks">
        {checks.map((check, index) => {
          const checkTone = toneClass(check.tone)
          const metrics = Array.isArray(check.metrics) ? check.metrics : []
          const issues = Array.isArray(check.issues) ? check.issues : []
          return (
            <article className={`bt-factor-readiness__check bt-factor-readiness__check--${checkTone}`} key={`${check.id ?? "check"}-${index}`}>
              <div className="bt-factor-readiness__check-head">
                <span>{compact(check.title)}</span>
                <b>{compact(check.status).toUpperCase()}</b>
              </div>
              <p>{compact(check.summary, "")}</p>
              {check.detail ? <small>{check.detail}</small> : null}
              {metrics.length > 0 ? (
                <div className="bt-factor-readiness__metrics">
                  {metrics.map((item, itemIndex) => (
                    <div className="bt-factor-readiness__metric" key={`${item.label ?? "metric"}-${itemIndex}`}>
                      <span>{compact(item.label)}</span>
                      <b>{compact(item.value)}</b>
                      {item.detail ? <small>{item.detail}</small> : null}
                    </div>
                  ))}
                </div>
              ) : null}
              {issues.length > 0 ? (
                <div className="bt-factor-readiness__issues">
                  {issues.map((item, itemIndex) => (
                    <div className={`bt-factor-readiness__issue bt-factor-readiness__issue--${toneClass(item.tone)}`} key={`${item.label ?? "issue"}-${itemIndex}`}>
                      <span>{compact(item.label)}</span>
                      <b>{compact(item.value)}</b>
                      {item.detail ? <small>{item.detail}</small> : null}
                    </div>
                  ))}
                </div>
              ) : null}
            </article>
          )
        })}
      </div>

      <footer className="bt-factor-readiness__actions">
        {actions.map((action, index) => (
          <div className={`bt-factor-readiness__action bt-factor-readiness__action--${toneClass(action.tone)}`} key={`${action.label ?? "action"}-${index}`}>
            <span>{compact(action.label)}</span>
            <p>{compact(action.detail, "")}</p>
          </div>
        ))}
      </footer>
    </section>
  )
}

