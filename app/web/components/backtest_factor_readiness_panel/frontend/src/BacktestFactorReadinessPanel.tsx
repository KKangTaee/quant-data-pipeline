import React, { useEffect } from "react"
import { Streamlit } from "streamlit-component-lib"

type Tone = "positive" | "warning" | "danger" | "neutral"

type DiagnosticItem = {
  label?: string
  value?: string
}

type ReadinessAction = {
  id?: string
  label?: string
  detail?: string
  enabled?: boolean
  tone?: Tone
  symbols?: string[]
}

type ReadinessCheck = {
  id?: string
  title?: string
  status?: string
  status_label?: string
  statusLabel?: string
  tone?: Tone
  problem?: string
  symbols?: string[]
  symbol_sample?: string
  symbolSample?: string
  solution?: string
  action?: ReadinessAction
  diagnostics?: DiagnosticItem[]
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

const displaySymbols = (symbols: string[] | undefined, fallback?: string): string[] => {
  if (Array.isArray(symbols) && symbols.length > 0) {
    return symbols.map((symbol) => compact(symbol)).filter((symbol) => symbol !== "-")
  }
  const text = compact(fallback, "")
  if (!text) return []
  return text.split(",").map((symbol) => symbol.trim()).filter(Boolean)
}

const emitAction = (action: ReadinessAction | undefined, check: ReadinessCheck) => {
  if (!action?.id || action.enabled === false) return
  Streamlit.setComponentValue({
    source: "backtest_factor_readiness_panel",
    action: action.id,
    checkId: check.id ?? "",
    symbols: action.symbols ?? check.symbols ?? [],
    nonce: `${Date.now()}-${action.id}`,
  })
}

export function BacktestFactorReadinessPanel(props: BacktestFactorReadinessPanelProps) {
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [props])

  const tone = toneClass(props.tone)
  const checks = Array.isArray(props.checks) ? props.checks : []
  const actions = Array.isArray(props.actions) ? props.actions : []
  const stateLabel = props.runRecommended ? "실행 가능" : "확인 필요"

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
          <b>{stateLabel}</b>
        </div>
      </header>

      {checks.length === 0 ? (
        <div className="bt-factor-readiness__empty">
          <b>문제 없음</b>
          <p>현재 선택 기준에서는 추가 데이터 보강 없이 아래 Run Backtest 버튼으로 진행할 수 있습니다.</p>
          {actions.length > 0 ? <small>{compact(actions[0]?.detail, "")}</small> : null}
        </div>
      ) : (
        <div className="bt-factor-readiness__checks">
          {checks.map((check, index) => {
            const checkTone = toneClass(check.tone)
            const action = check.action
            const symbols = displaySymbols(check.symbols, check.symbol_sample ?? check.symbolSample)
            const visibleSymbols = symbols.slice(0, 14)
            const hiddenCount = Math.max(symbols.length - visibleSymbols.length, 0)
            const diagnostics = Array.isArray(check.diagnostics) ? check.diagnostics : []
            const statusLabel = compact(check.status_label ?? check.statusLabel, action?.enabled === false ? "수동 확인" : "해결 가능")
            return (
              <article className={`bt-factor-readiness__check bt-factor-readiness__check--${checkTone}`} key={`${check.id ?? "check"}-${index}`}>
                <div className="bt-factor-readiness__check-head">
                  <span>{compact(check.title)}</span>
                  <b>{statusLabel}</b>
                </div>

                <div className="bt-factor-readiness__block">
                  <span>문제</span>
                  <p>{compact(check.problem, "확인할 데이터 이슈가 있습니다.")}</p>
                </div>

                <div className="bt-factor-readiness__block">
                  <span>영향받는 티커</span>
                  {visibleSymbols.length > 0 ? (
                    <div className="bt-factor-readiness__symbols">
                      {visibleSymbols.map((symbol) => (
                        <code key={symbol}>{symbol}</code>
                      ))}
                      {hiddenCount > 0 ? <code>+{hiddenCount} more</code> : null}
                    </div>
                  ) : (
                    <p>-</p>
                  )}
                </div>

                <div className="bt-factor-readiness__block">
                  <span>해결 방법</span>
                  <p>{compact(check.solution, action?.detail ?? "")}</p>
                  {action?.id ? (
                    <button type="button" disabled={action.enabled === false} onClick={() => emitAction(action, check)}>
                      {compact(action.label, "해결 실행")}
                    </button>
                  ) : null}
                  {action?.detail ? <small>{action.detail}</small> : null}
                </div>

                {diagnostics.length > 0 ? (
                  <details className="bt-factor-readiness__details">
                    <summary>근거 보기</summary>
                    <dl>
                      {diagnostics.map((item, itemIndex) => (
                        <div key={`${item.label ?? "diagnostic"}-${itemIndex}`}>
                          <dt>{compact(item.label)}</dt>
                          <dd>{compact(item.value)}</dd>
                        </div>
                      ))}
                    </dl>
                  </details>
                ) : null}
              </article>
            )
          })}
        </div>
      )}
    </section>
  )
}
