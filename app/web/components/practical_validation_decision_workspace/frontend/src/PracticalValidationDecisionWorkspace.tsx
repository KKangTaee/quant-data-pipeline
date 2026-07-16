import React, { useEffect, useState } from "react"
import { Streamlit } from "streamlit-component-lib"
import { DecisionWorkspace, Issue, WorkspaceIntent } from "./types"

const intentId = (prefix: string) =>
  `${prefix}-${globalThis.crypto?.randomUUID?.() ?? Date.now()}`

const emit = (intent: WorkspaceIntent) => Streamlit.setComponentValue(intent)

function StepTitle({
  step,
  title,
  detail,
}: {
  step: string
  title: string
  detail: string
}) {
  return (
    <header className="pv2-step-title">
      <span>{step}</span>
      <div>
        <h2>{title}</h2>
        <p>{detail}</p>
      </div>
    </header>
  )
}

function IssueCard({
  issue,
  workspace,
}: {
  issue: Issue
  workspace: DecisionWorkspace
}) {
  return (
    <article className="pv2-issue-card">
      <div>
        <strong>{issue.title}</strong>
        <span>{issue.action_label}</span>
      </div>
      {issue.observed && <p>{issue.observed}</p>}
      {issue.completion_criteria && <small>{issue.completion_criteria}</small>}
      {issue.actionable_now && issue.action_id && (
        <button
          type="button"
          onClick={() =>
            emit({
              action: "run_resolution_action",
              intent_id: intentId("resolution"),
              selection_source_id: workspace.candidate.selection_source_id,
              validation_result_id: workspace.validation_result_id,
              root_issue_id: issue.root_issue_id,
              action_id: issue.action_id!,
            })
          }
        >
          {issue.action_label || "지금 해결"}
        </button>
      )}
    </article>
  )
}

export function PracticalValidationDecisionWorkspace({
  workspace,
}: {
  workspace: DecisionWorkspace
}) {
  const [pendingAction, setPendingAction] = useState<string | null>(null)

  useEffect(() => {
    const resize = () => Streamlit.setFrameHeight()
    resize()
    const observer = new ResizeObserver(resize)
    observer.observe(document.body)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    setPendingAction(null)
  }, [workspace.replay.replay_id, workspace.validation_result_id])

  const resolveNow = workspace.resolution_lanes.resolve_now ?? []
  const engineeringRequired =
    workspace.resolution_lanes.engineering_required ?? []
  const handoff = workspace.resolution_lanes.final_review_handoff ?? []
  const measuredCautions = workspace.measured_cautions ?? []
  const visibleVerified = workspace.verified_findings.slice(0, 8)
  const validationResultId = workspace.validation_result_id
  const replayPending = pendingAction === "run_replay"

  return (
    <main className="pv2-workspace">
      <header className="pv2-header">
        <div>
          <p className="pv2-kicker">
            Practical Validation Decision Workspace
          </p>
          <h1>
            {workspace.header.question ||
              "이 후보는 Final Review에서 실제 투자 판단을 할 만큼 검증되었는가?"}
          </h1>
          <p>{workspace.header.detail}</p>
        </div>
        <aside>
          <strong>{workspace.candidate.title}</strong>
          <span>{workspace.candidate.as_of || "기준일 미측정"}</span>
        </aside>
      </header>

      <section className="pv2-step">
        <StepTitle
          step="1. 후보와 검증 기준"
          title="무엇을 어떤 기준으로 검증하는가"
          detail="후보와 판정 기준을 먼저 고정합니다."
        />
        <div className="pv2-selection-section pv2-candidate-section">
          <div className="pv2-subsection-title">
            <span>1A</span>
            <div>
              <h3>1A. 검증할 후보 선택</h3>
              <p>목록에서 실제로 재검증할 포트폴리오를 고릅니다.</p>
            </div>
          </div>
          <div className="pv2-choice-grid">
            {workspace.candidate_selector.options.map((option) => (
              <button
                type="button"
                className={option.selected ? "is-selected" : ""}
                aria-pressed={option.selected}
                disabled={!option.eligible}
                key={option.selection_source_id}
                onClick={() => {
                  if (option.selected) return
                  emit({
                    action: "select_source",
                    intent_id: intentId("source"),
                    selection_source_id: option.selection_source_id,
                    validation_result_id: workspace.validation_result_id,
                  })
                }}
              >
                <strong>{option.title}</strong>
                <span>{option.source_type_label}</span>
              </button>
            ))}
          </div>
          <div className="pv2-candidate-summary">
            <span>현재 검증 후보</span>
            <strong>{workspace.candidate.title}</strong>
            <small>
              {workspace.candidate.source_type_label} ·{" "}
              {workspace.candidate.as_of || "기준일 미측정"}
            </small>
          </div>
        </div>
        <div className="pv2-selection-section pv2-policy-section">
          <div className="pv2-subsection-title">
            <span>1B</span>
            <div>
              <h3>1B. 어떤 관점으로 검증할까요?</h3>
              <p>
                포트폴리오 설계가 아니라 손실 허용도와 운용 목적에 맞는 판정
                기준을 선택합니다.
              </p>
            </div>
          </div>
          <div className="pv2-profile-grid">
            {workspace.profile.options.map((option) => (
              <button
                type="button"
                className={option.selected ? "is-selected" : ""}
                aria-pressed={option.selected}
                key={option.profile_id}
                onClick={() => {
                  if (option.selected) return
                  emit({
                    action: "select_profile_preset",
                    intent_id: intentId("profile"),
                    selection_source_id:
                      workspace.candidate.selection_source_id,
                    validation_result_id: workspace.validation_result_id,
                    profile_id: option.profile_id,
                  })
                }}
              >
                <strong>{option.label}</strong>
                <span>{option.description}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      <section
        className={`pv2-step pv2-replay-step ${
          replayPending ? "is-pending" : ""
        }`}
        aria-busy={replayPending}
      >
        <StepTitle
          step="2. 최신 데이터 기준 재검증"
          title="현재 저장 데이터로 다시 재현하는가"
          detail="현재 세션 replay가 완료되어야 결과와 저장 경로가 열립니다."
        />
        <div className="pv2-replay">
          <div>
            <span>현재 상태</span>
            <strong>{workspace.replay.status}</strong>
            <small>{workspace.replay.replay_id || "아직 실행하지 않음"}</small>
          </div>
          <button
            type="button"
            disabled={!workspace.actions.run_replay.enabled || replayPending}
            onClick={() => {
              setPendingAction("run_replay")
              emit({
                action: "run_replay",
                intent_id: intentId("replay"),
                selection_source_id: workspace.candidate.selection_source_id,
                validation_result_id: workspace.validation_result_id,
              })
            }}
          >
            {replayPending
              ? "최신 데이터로 재검증 중"
              : workspace.actions.run_replay.label}
          </button>
        </div>
      </section>

      <section className={`pv2-verdict pv2-tone-${workspace.verdict.tone}`}>
        <span>{workspace.verdict.label}</span>
        <h2>{workspace.verdict.headline}</h2>
        <p>{workspace.verdict.detail}</p>
        <dl>
          <div>
            <dt>검증됨</dt>
            <dd>{workspace.summary.verified_count ?? 0}</dd>
          </div>
          <div>
            <dt>측정 주의</dt>
            <dd>{workspace.summary.measured_caution_count ?? 0}</dd>
          </div>
          <div>
            <dt>Level2 주의</dt>
            <dd>{workspace.summary.validated_caution_count ?? 0}</dd>
          </div>
          <div>
            <dt>지금 해결</dt>
            <dd>{workspace.summary.resolve_now_count ?? 0}</dd>
          </div>
          <div>
            <dt>개발 차단</dt>
            <dd>{workspace.summary.engineering_blocker_count ?? 0}</dd>
          </div>
          <div>
            <dt>인수할 한계</dt>
            <dd>{workspace.summary.accepted_limit_count ?? 0}</dd>
          </div>
          <div>
            <dt>최종 판단</dt>
            <dd>{workspace.summary.final_decision_count ?? 0}</dd>
          </div>
          <div>
            <dt>Monitoring</dt>
            <dd>{workspace.summary.monitoring_transfer_count ?? 0}</dd>
          </div>
        </dl>
      </section>

      <section className="pv2-step">
        <StepTitle
          step="3. 결과 해석과 해결 구분"
          title="검증된 내용과 남은 판단을 구분합니다"
          detail="해결할 수 있는 일과 Final Review로 넘길 항목을 섞지 않습니다."
        />
        {visibleVerified.length > 0 && (
          <div className="pv2-lane">
            <h3>검증된 내용</h3>
            <div className="pv2-card-grid">
              {visibleVerified.map((item) => (
                <article key={item.finding_id}>
                  <strong>{item.title}</strong>
                  <p>{item.detail}</p>
                </article>
              ))}
            </div>
            {workspace.verified_findings.length > visibleVerified.length && (
              <p>
                나머지{" "}
                {workspace.verified_findings.length - visibleVerified.length}개
                통과 근거는 상세 검증 근거에서 확인할 수 있습니다.
              </p>
            )}
          </div>
        )}
        {measuredCautions.length > 0 && (
          <div className="pv2-lane">
            <h3>주의해서 볼 결과</h3>
            <div className="pv2-card-grid">
              {measuredCautions.map((issue) => (
                <IssueCard
                  issue={issue}
                  workspace={workspace}
                  key={issue.root_issue_id}
                />
              ))}
            </div>
          </div>
        )}
        {resolveNow.length > 0 && (
          <div className="pv2-lane">
            <h3>지금 해야 할 일</h3>
            <div className="pv2-card-grid">
              {resolveNow.map((issue) => (
                <IssueCard
                  issue={issue}
                  workspace={workspace}
                  key={issue.root_issue_id}
                />
              ))}
            </div>
          </div>
        )}
        {engineeringRequired.length > 0 && (
          <div className="pv2-lane">
            <h3>개발 후 재검토</h3>
            <div className="pv2-card-grid">
              {engineeringRequired.map((issue) => (
                <IssueCard
                  issue={issue}
                  workspace={workspace}
                  key={issue.root_issue_id}
                />
              ))}
            </div>
          </div>
        )}
        {handoff.length > 0 && (
          <div className="pv2-lane">
            <h3>Final Review로 넘길 것</h3>
            <div className="pv2-card-grid">
              {handoff.map((issue) => (
                <IssueCard
                  issue={issue}
                  workspace={workspace}
                  key={issue.root_issue_id}
                />
              ))}
            </div>
          </div>
        )}
        <details className="pv2-disclosure">
          <summary>상세 검증 근거</summary>
          {workspace.category_disclosures.map((group) => (
            <article key={group.category_id}>
              <strong>{group.title}</strong>
              <span>{group.outcome}</span>
              <p>{group.question}</p>
              <ul>
                {group.technical_rows.map((row) => (
                  <li key={`${group.category_id}-${row.row_id}`}>
                    <b>{row.title}</b>
                    <span>{row.status}</span>
                    <p>{row.detail}</p>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </details>
      </section>

      <section className="pv2-step pv2-final-action">
        <StepTitle
          step="4. 저장하고 Final Review로 이동"
          title="현재 검증 결과를 기록하고 다음 판단으로 이동합니다"
          detail="이동은 최종 승인이나 주문 실행이 아닙니다."
        />
        <div>
          <button
            type="button"
            disabled={!workspace.actions.save_audit_only.enabled}
            onClick={() =>
              emit({
                action: "save_audit_only",
                intent_id: intentId("audit"),
                selection_source_id: workspace.candidate.selection_source_id,
                validation_result_id: validationResultId,
              })
            }
          >
            {workspace.actions.save_audit_only.label}
          </button>
          <button
            type="button"
            disabled={!workspace.actions.save_and_move.enabled}
            onClick={() =>
              emit({
                action: "save_and_move",
                intent_id: intentId("move"),
                selection_source_id: workspace.candidate.selection_source_id,
                validation_result_id: validationResultId,
              })
            }
          >
            {workspace.actions.save_and_move.label}
          </button>
        </div>
      </section>
    </main>
  )
}
