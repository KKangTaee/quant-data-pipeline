import React from "react"
import { Streamlit } from "streamlit-component-lib"
import { WorkflowShell, WorkflowStage } from "./types"

function emitStageIntent(stage: WorkflowStage) {
  if (stage.is_active) return
  Streamlit.setComponentValue({
    type: "select_stage",
    stage_key: stage.stage_key,
    nonce: `${Date.now()}-${Math.random()}`,
  })
}

export function BacktestWorkflowShell({ shell }: { shell: WorkflowShell }) {
  const active = shell.active_stage_context
  return (
    <section className="bt-workflow-shell" aria-label="Backtest 후보 선정 흐름">
      <div className="bt-workflow-hero">
        <header className="bt-workflow-intro">
          <span className="bt-workflow-kicker">BACKTEST DECISION PIPELINE</span>
          <h1>{shell.headline}</h1>
          <p>{shell.description}</p>
        </header>

        <aside className="bt-workflow-current" aria-live="polite">
          <span>현재 단계 · {active.level_label}</span>
          <strong>{active.title}</strong>
          <p>{active.responsibility}</p>
        </aside>
      </div>

      <nav className="bt-workflow-rail" aria-label="Backtest 단계 이동">
        {shell.stages.map((stage, index) => (
          <button
            type="button"
            className={stage.is_active ? "is-active" : ""}
            aria-current={stage.is_active ? "step" : undefined}
            key={stage.stage_key}
            onClick={() => emitStageIntent(stage)}
          >
            <span className="bt-workflow-step">
              {String(index + 1).padStart(2, "0")}
              {stage.is_active && <em>CURRENT</em>}
            </span>
            <strong>{stage.title}</strong>
            <small>{stage.english_title}</small>
          </button>
        ))}
      </nav>
    </section>
  )
}
