import React, { useState } from "react"
import { Streamlit } from "streamlit-component-lib"
import { ResultWorkspace, ResultWorkspaceIntent } from "./types"
import { ResultWorkspaceChart } from "./ResultWorkspaceChart"

const nonce = () => globalThis.crypto?.randomUUID?.() ?? `${Date.now()}`

const emitIntent = (
  action: ResultWorkspaceIntent["action"],
  payload: ResultWorkspaceIntent["payload"],
) => Streamlit.setComponentValue({ action, payload, nonce: nonce() } satisfies ResultWorkspaceIntent)

function SectionHeading({ step, title, detail }: { step: string; title: string; detail: string }) {
  return (
    <div className="bt1r-section-heading">
      <span>{step}</span>
      <div><h2>{title}</h2><p>{detail}</p></div>
    </div>
  )
}

function ResultHeader({ workspace }: { workspace: ResultWorkspace }) {
  const role = workspace.lifecycle.error ? "alert" : "status"
  return (
    <header className="bt1r-header">
      <div>
        <p className="bt1r-kicker">Backtest Analysis Result Workspace</p>
        <h1>{workspace.identity.strategy_name}</h1>
        <p>{workspace.identity.variant_name || workspace.identity.period_label}</p>
      </div>
      <div className={`bt1r-lifecycle is-${workspace.lifecycle.state}`} role={role}>
        <span>결과 상태</span>
        <strong>{workspace.lifecycle.display_label}</strong>
        {workspace.lifecycle.reference_message && (
          <small className="bt1r-reference-message">
            {workspace.lifecycle.reference_message}
          </small>
        )}
        {workspace.lifecycle.error && <small>{workspace.lifecycle.error.message}</small>}
      </div>
    </header>
  )
}

function DataFreshnessActionCard({ workspace }: { workspace: ResultWorkspace }) {
  const freshness = workspace.data_freshness_action
  if (!freshness || !("state" in freshness) || freshness.state === "current") return null
  const primary = freshness.primary_action
  const action = primary ? workspace.actions[primary.id] : undefined
  const metrics = [
    ["요청 종료일", freshness.requested_end || "-"],
    ["목표 거래일", freshness.target_trading_end || "-"],
    ["현재 공통 기준일", freshness.current_common_latest || "-"],
    ["최신화 대상", `${freshness.affected_symbol_count}개`],
  ]
  return (
    <section
      className={`bt1r-freshness-card is-${freshness.state}`}
      role={freshness.state === "provider_gap" ? "alert" : "status"}
    >
      <div className="bt1r-freshness-copy">
        <span>요청 종료일과 가격 데이터 확인</span>
        <h2>{freshness.summary}</h2>
        <p>{freshness.guidance}</p>
        {freshness.feedback && <small>{freshness.feedback}</small>}
      </div>
      <dl className="bt1r-freshness-metrics">
        {metrics.map(([label, value]) => (
          <div key={label}><dt>{label}</dt><dd>{value}</dd></div>
        ))}
      </dl>
      {freshness.affected_symbol_sample.length > 0 && (
        <p className="bt1r-freshness-symbols">
          대상 예시 · {freshness.affected_symbol_sample.join(", ")}
        </p>
      )}
      {action && (
        <button type="button" disabled={!action.enabled} onClick={() => emitIntent(action.id, {
          run_result_id: workspace.identity.run_result_id,
          current_configuration_fingerprint: workspace.configuration_fingerprint,
        })}>{action.label}</button>
      )}
    </section>
  )
}

function PerformanceSummary({ workspace }: { workspace: ResultWorkspace }) {
  return (
    <section className="bt1r-section">
      <SectionHeading step="1" title="성과 요약" detail="성과와 위험을 같은 표시 단위로 먼저 확인합니다." />
      <dl className="bt1r-metric-grid">
        {workspace.performance_summary.map((item) => (
          <div key={item.metric_id}><dt>{item.label}</dt><dd>{item.value_label}</dd></div>
        ))}
      </dl>
    </section>
  )
}

function AllocationCard({ title, asOf, rows }: { title: string; asOf: string; rows: ResultWorkspace["holdings"]["current_allocation"] }) {
  return (
    <article className="bt1r-allocation-card">
      <header><h3>{title}</h3><span>{asOf || "기준일 없음"}</span></header>
      {rows.length ? (
        <ul>{rows.map((row) => <li key={row.ticker}><strong>{row.ticker}</strong><span>{row.weight_label}</span></li>)}</ul>
      ) : <p className="bt1r-empty-copy">표시 가능한 비중 근거가 없습니다.</p>}
    </article>
  )
}

function HoldingsComparison({ workspace }: { workspace: ResultWorkspace }) {
  const holdings = workspace.holdings
  const schedule = holdings.schedule
  return (
    <section className="bt1r-section">
      <SectionHeading step="3" title="현재 보유와 최신 신호 기준 목표 구성" detail="백테스트 모의 구성으로 실제 계좌나 주문이 아닙니다." />
      <div className="bt1r-schedule-strip">
        <div><span>현재 평가일</span><strong>{schedule.valuation_as_of || "-"}</strong></div>
        <div><span>최신 신호일</span><strong>{schedule.latest_signal_as_of}</strong></div>
        <div><span>마지막 리밸런싱</span><strong>{schedule.last_rebalance_as_of}</strong></div>
        <div><span>주기</span><strong>{schedule.cadence_label}</strong></div>
        <div><span>다음 예상</span><strong>{schedule.next_window_label}</strong></div>
      </div>
      <div className="bt1r-holdings-grid">
        <AllocationCard title="현재 보유" asOf={holdings.as_of} rows={holdings.current_allocation} />
        <AllocationCard title="목표 구성" asOf={holdings.target_as_of} rows={holdings.target_allocation} />
      </div>
      <p className="bt1r-holdings-explanation">{holdings.explanation}</p>
      {holdings.unavailable_reason && <p className="bt1r-inline-note">{holdings.unavailable_reason}</p>}
      {holdings.components && holdings.components.length > 0 && (
        <div className="bt1r-component-list">
          {holdings.components.map((component) => (
            <article key={component.component_id}><strong>{component.label}</strong><span>{component.status}</span></article>
          ))}
        </div>
      )}
    </section>
  )
}

function HandoffAndQuestions({ workspace }: { workspace: ResultWorkspace }) {
  const readiness = workspace.technical_handoff_readiness
  const action = workspace.actions.save_and_move
  return (
    <section className="bt1r-section">
      <SectionHeading step="4" title="Level2 인계 상태와 검증 질문" detail="Level1 기술 준비 상태와 Level2가 확인할 질문을 분리합니다." />
      <div className={`bt1r-handoff is-${readiness.state}`}>
        <div><span>Level1 기술 상태</span><strong>{readiness.label}</strong></div>
        {readiness.reasons.length > 0 && <ul>{readiness.reasons.map((reason) => <li key={reason.root_issue_id}>{reason.message}</li>)}</ul>}
        {action && (
          <button type="button" disabled={!action.enabled} onClick={() => emitIntent("save_and_move", {
            run_result_id: workspace.identity.run_result_id,
            current_configuration_fingerprint: workspace.configuration_fingerprint,
          })}>{action.label}</button>
        )}
      </div>
      {workspace.level2_validation_questions.length > 0 && (
        <div className="bt1r-question-grid">
          {workspace.level2_validation_questions.map((question) => (
            <article key={question.root_issue_id}>
              <span>{question.lane_label}</span><h3>{question.title}</h3><p>{question.summary}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

function EvidenceGroups({ workspace }: { workspace: ResultWorkspace }) {
  return (
    <section className="bt1r-section">
      <SectionHeading step="5" title="목적별 검증 근거" detail="상세 진단을 목적별 네 그룹으로 정리했습니다." />
      <div className="bt1r-evidence-grid">
        {workspace.evidence_groups.map((group) => (
          <article key={group.group_id}><h3>{group.label}</h3><p>{group.summary}</p><dl>{group.items.map((item) => <div key={item.label}><dt>{item.label}</dt><dd>{item.value}</dd></div>)}</dl></article>
        ))}
      </div>
    </section>
  )
}

function UserTables({ workspace }: { workspace: ResultWorkspace }) {
  const [activeTable, setActiveTable] = useState<"performance" | "holdings">("performance")
  const rows = activeTable === "performance" ? workspace.performance_rows : workspace.holding_change_rows
  const columns = rows.length ? Object.keys(rows[0]) : []
  return (
    <section className="bt1r-section">
      <SectionHeading step="6" title="사용자용 결과 표" detail="성과 흐름과 보유 변화를 필요한 열만 남겨 확인합니다." />
      <div className="bt1r-table-tabs" role="tablist">
        <button type="button" role="tab" aria-selected={activeTable === "performance"} onClick={() => setActiveTable("performance")}>성과 시계열</button>
        <button type="button" role="tab" aria-selected={activeTable === "holdings"} onClick={() => setActiveTable("holdings")}>보유 변화</button>
      </div>
      <div className="bt1r-table-shell" tabIndex={0}>
        {rows.length ? <table><thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={index}>{columns.map((column) => <td key={column}>{String((row as Record<string, unknown>)[column] ?? "-")}</td>)}</tr>)}</tbody></table> : <p className="bt1r-empty-copy">표시 가능한 결과 행이 없습니다.</p>}
      </div>
    </section>
  )
}

function TechnicalAppendix({ workspace }: { workspace: ResultWorkspace }) {
  return (
    <details className="bt1r-appendix">
      <summary>계산 및 데이터 기준</summary>
      <div className="bt1r-basis-grid">
        {workspace.technical_appendix.sections.map((section) => (
          <article key={section.section_id}>
            <h3>{section.label}</h3>
            <div>
              {section.rows.map((row) => (
                <div className={`is-${row.status}`} key={row.label}>
                  <strong>{row.label}</strong>
                  <span>{row.value_label}</span>
                  <small>{row.explanation}</small>
                </div>
              ))}
            </div>
          </article>
        ))}
      </div>
      <details className="bt1r-raw-disclosure">
        <summary>원본 필드 보기</summary>
        <p>원본 결과 {workspace.technical_appendix.raw.row_count}행</p>
        <code>{workspace.technical_appendix.raw.columns.join(", ")}</code>
        <pre>{JSON.stringify(workspace.technical_appendix.raw.meta, null, 2)}</pre>
      </details>
    </details>
  )
}

export function BacktestAnalysisResultWorkspace({ workspace }: { workspace: ResultWorkspace }) {
  if (!workspace.visible) return null
  return (
    <main className="bt1r-workspace">
      <ResultHeader workspace={workspace} />
      <DataFreshnessActionCard workspace={workspace} />
      <PerformanceSummary workspace={workspace} />
      <ResultWorkspaceChart chart={workspace.chart} />
      <HoldingsComparison workspace={workspace} />
      <HandoffAndQuestions workspace={workspace} />
      <EvidenceGroups workspace={workspace} />
      <UserTables workspace={workspace} />
      <TechnicalAppendix workspace={workspace} />
    </main>
  )
}
