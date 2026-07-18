import React, { useState } from "react"
import { Streamlit } from "streamlit-component-lib"
import {
  BacktestAnalysisWorkspace,
  WorkspaceIntent,
  WorkspaceSurface,
} from "./types"

function emitIntent(
  action: WorkspaceIntent["action"],
  payload: Record<string, unknown> = {},
) {
  Streamlit.setComponentValue({
    action,
    payload,
    nonce: `${Date.now()}-${Math.random()}`,
  })
}

function displayValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-"
  if (typeof value === "number") {
    return value.toLocaleString(undefined, { maximumFractionDigits: 3 })
  }
  return String(value)
}

function workspaceKindLabel(kind: string) {
  return kind === "portfolio_mix" ? "Portfolio Mix" : "Single Strategy"
}

export function BacktestAnalysisDecisionWorkspace({
  workspace,
  surface,
}: {
  workspace: BacktestAnalysisWorkspace
  surface: WorkspaceSurface
}) {
  const saveAndMove = workspace.actions.save_and_move
  const saveMix = workspace.actions.save_mix
  const [mixName, setMixName] = useState("")
  const [mixDescription, setMixDescription] = useState("")
  const configurationRows = Object.entries(workspace.configuration_summary).slice(
    0,
    6,
  )

  return (
    <main className="bt1-workspace" data-surface={surface}>
      {surface === "context" && (
        <>
          <header className="bt1-header">
            <p className="bt1-kicker">Backtest Analysis Decision Workspace</p>
            <h1>{workspace.header.question}</h1>
            <p>
              후보 유형과 목적을 고정하고 필요한 설정만 입력한 뒤, 실행 결과를
              Level2 검증 준비 상태로 해석합니다.
            </p>
          </header>

          <section className="bt1-step">
            <div className="bt1-step-heading">
              <span>1</span>
              <div>
                <h2>어떤 후보를 만들까요?</h2>
                <p>단일 전략과 Portfolio Mix는 서로 다른 설정 흐름을 사용합니다.</p>
              </div>
            </div>
            <div className="bt1-entry-grid">
              {[
                {
                  id: "single_strategy",
                  title: "Single Strategy",
                  detail: "하나의 전략을 설정하고 결과를 검증 후보로 준비합니다.",
                },
                {
                  id: "portfolio_mix",
                  title: "Portfolio Mix",
                  detail: "여러 전략의 역할과 비중을 조합해 후보를 만듭니다.",
                },
              ].map((item) => (
                <button
                  type="button"
                  className={
                    workspace.workspace_kind === item.id ? "is-selected" : ""
                  }
                  aria-pressed={workspace.workspace_kind === item.id}
                  key={item.id}
                  onClick={() =>
                    emitIntent("select_workspace_kind", {
                      workspace_kind: item.id,
                    })
                  }
                >
                  <strong>{item.title}</strong>
                  <span>{item.detail}</span>
                </button>
              ))}
            </div>
          </section>

          <section className="bt1-step">
            <div className="bt1-step-heading">
              <span>2</span>
              <div>
                <h2>목적과 핵심 설정</h2>
                <p>현재 후보를 유지하면서 목적별 전략과 설정을 확인합니다.</p>
              </div>
            </div>
            {workspace.workspace_kind === "portfolio_mix" && (
              <aside className="bt1-current-work">
                <span>현재 작업</span>
                <strong>{workspace.current_work.title}</strong>
                <small>{workspaceKindLabel(workspace.current_work.workspace_kind)}</small>
              </aside>
            )}
            {workspace.workspace_kind === "single_strategy" && (
              <div className="bt1-purpose-grid">
                {workspace.strategy_catalog.map((group) => (
                  <article key={group.group_id}>
                    <h3>{group.label}</h3>
                    <div>
                      {group.items.map((item) => (
                        <button
                          type="button"
                          className={
                            workspace.current_work.title === item.strategy_choice
                              ? "is-selected"
                              : ""
                          }
                          key={item.strategy_choice}
                          onClick={() =>
                            emitIntent("select_strategy", {
                              strategy_choice: item.strategy_choice,
                            })
                          }
                        >
                          <strong>{item.strategy_choice}</strong>
                          {item.maturity === "development" && <span>개발 중</span>}
                        </button>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            )}
            {workspace.workspace_kind === "portfolio_mix" && (
              <div className="bt1-mix-entry">
                <div className="bt1-entry-grid">
                  <button
                    type="button"
                    className={
                      workspace.mix?.saved_entry_mode === "new"
                        ? "is-selected"
                        : ""
                    }
                    onClick={() => emitIntent("select_mix_mode", { mix_mode: "new" })}
                  >
                    <strong>새 Mix 만들기</strong>
                    <span>구성 전략을 실행한 뒤 역할과 비중을 새로 정합니다.</span>
                  </button>
                  <button
                    type="button"
                    className={
                      workspace.mix?.saved_entry_mode === "saved"
                        ? "is-selected"
                        : ""
                    }
                    onClick={() => emitIntent("select_mix_mode", { mix_mode: "saved" })}
                  >
                    <strong>저장된 Mix 불러오기</strong>
                    <span>재사용 가능한 저장 setup을 골라 이어서 검토합니다.</span>
                  </button>
                </div>
                {workspace.mix?.role_weight_rows.length ? (
                  <div className="bt1-mix-summary">
                    {workspace.mix.role_weight_rows.map((row) => (
                      <article key={`${row.strategy_name}-${row.role}`}>
                        <strong>{row.strategy_name}</strong>
                        <span>{row.role_label}</span>
                        <span>{displayValue(row.weight_percent)}%</span>
                      </article>
                    ))}
                    <p>총 비중 {displayValue(workspace.mix.total_weight_percent)}%</p>
                  </div>
                ) : null}
                {workspace.mix?.saved_entry_mode === "saved" &&
                  workspace.saved_mixes.length > 0 && (
                    <div className="bt1-saved-mix-list">
                      {workspace.saved_mixes.slice(0, 6).map((item, index) => (
                        <article key={String(item.portfolio_id ?? index)}>
                          <strong>{displayValue(item.name)}</strong>
                          <span>
                            {Array.isArray(item.strategy_names)
                              ? item.strategy_names.join(" · ")
                              : "-"}
                          </span>
                          <small>{displayValue(item.updated_at)}</small>
                        </article>
                      ))}
                    </div>
                  )}
              </div>
            )}
            {configurationRows.length > 0 && (
              <dl className="bt1-configuration-summary">
                {configurationRows.map(([key, value]) => (
                  <div key={key}>
                    <dt>{key}</dt>
                    <dd>{displayValue(value)}</dd>
                  </div>
                ))}
              </dl>
            )}
          </section>
        </>
      )}

      {surface === "decision" && (
        <>
          <section className="bt1-step bt1-decision">
            <div className="bt1-step-heading">
              <span>3</span>
              <div>
                <h2>실행 결과를 어떻게 판단할까요?</h2>
                <p>성과보다 후보 준비 상태와 남은 행동을 먼저 확인합니다.</p>
              </div>
            </div>
            <div className={`bt1-verdict bt1-verdict-${workspace.handoff_state}`}>
              <span>
                {workspace.result_freshness === "stale"
                  ? "이전 설정 결과"
                  : workspace.strategy_maturity === "development"
                    ? "개발 중"
                    : "Level1 판단"}
              </span>
              <h2>{workspace.decision.headline}</h2>
              <p>{workspace.decision.summary}</p>
            </div>
            {workspace.error && (
              <div className="bt1-error" role="alert">
                <strong>실행을 완료하지 못했습니다</strong>
                <span>{workspace.error.message}</span>
              </div>
            )}
            {workspace.decision.metrics.length > 0 && (
              <dl className="bt1-metric-grid">
                {workspace.decision.metrics.map((metric) => (
                  <div key={metric.metric_id}>
                    <dt>{metric.label}</dt>
                    <dd>{displayValue(metric.value)}</dd>
                  </div>
                ))}
              </dl>
            )}
            {workspace.decision.reasons.length > 0 && (
              <div className="bt1-reason-grid">
                {workspace.decision.reasons.map((reason) => (
                  <article key={reason.root_issue_id}>{reason.message}</article>
                ))}
              </div>
            )}
          </section>

          {(saveMix?.enabled === true || saveAndMove?.enabled === true) && (
            <section className="bt1-step bt1-final-action">
              <div className="bt1-step-heading">
                <span>4</span>
                <div>
                  <h2>저장 또는 Level2 이동</h2>
                  <p>Mix setup 저장과 검증 후보 등록은 서로 다른 작업입니다.</p>
                </div>
              </div>
              {saveMix?.enabled === true && (
                <div className="bt1-save-mix-form">
                  <label>
                    <span>Mix 이름</span>
                    <input
                      value={mixName}
                      onChange={(event) => setMixName(event.target.value)}
                      placeholder="다시 찾기 쉬운 이름"
                    />
                  </label>
                  <label>
                    <span>메모</span>
                    <textarea
                      value={mixDescription}
                      onChange={(event) => setMixDescription(event.target.value)}
                      placeholder="저장 목적과 다시 볼 조건"
                    />
                  </label>
                  <button
                    type="button"
                    className="bt1-secondary-action-button"
                    onClick={() =>
                      emitIntent("save_mix", {
                        name: mixName,
                        description: mixDescription,
                      })
                    }
                  >
                    {saveMix.label}
                  </button>
                </div>
              )}
              {saveAndMove?.enabled === true && (
                <button
                  type="button"
                  className="bt1-action-button"
                  onClick={() => emitIntent("save_and_move")}
                >
                  {saveAndMove.label}
                </button>
              )}
            </section>
          )}
        </>
      )}
    </main>
  )
}
