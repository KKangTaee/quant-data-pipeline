import React, { useEffect, useState } from "react"
import { Streamlit } from "streamlit-component-lib"
import {
  DecisionWorkspace,
  Issue,
  WorkspaceIntent,
  WorkspaceSurface,
} from "./types"

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
  pendingAction,
  onActionStart,
}: {
  issue: Issue
  workspace: DecisionWorkspace
  pendingAction?: string | null
  onActionStart?: (actionId: string) => void
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
          disabled={pendingAction !== null && pendingAction !== undefined}
          onClick={() => {
            onActionStart?.(issue.action_id!)
            emit({
              action: "run_resolution_action",
              intent_id: intentId("resolution"),
              selection_source_id: workspace.candidate.selection_source_id,
              validation_result_id: workspace.validation_result_id,
              root_issue_id: issue.root_issue_id,
              action_id: issue.action_id!,
            })
          }}
        >
          {pendingAction === issue.action_id
            ? "처리 중"
            : issue.action_label || "지금 해결"}
        </button>
      )}
    </article>
  )
}

export function PracticalValidationDecisionWorkspace({
  workspace,
  surface,
}: {
  workspace: DecisionWorkspace
  surface: WorkspaceSurface
}) {
  const evidenceCategories = workspace.category_disclosures
  const [pendingAction, setPendingAction] = useState<string | null>(null)
  const [candidateListOpen, setCandidateListOpen] = useState(false)
  const [activeEvidenceCategory, setActiveEvidenceCategory] = useState(
    evidenceCategories.find(
      (category) => category.summary.total_count > 0,
    )?.category_id ??
      evidenceCategories[0]?.category_id ??
      "",
  )

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

  useEffect(() => {
    if (
      !evidenceCategories.some(
        (category) => category.category_id === activeEvidenceCategory,
      )
    ) {
      setActiveEvidenceCategory(
        evidenceCategories.find(
          (category) => category.summary.total_count > 0,
        )?.category_id ??
          evidenceCategories[0]?.category_id ??
          "",
      )
    }
  }, [evidenceCategories, activeEvidenceCategory])

  const resolveNow = workspace.resolution_lanes.resolve_now ?? []
  const engineeringRequired =
    workspace.resolution_lanes.engineering_required ?? []
  const measuredCautions = workspace.measured_cautions ?? []
  const visibleVerified = workspace.verified_findings.slice(0, 8)
  const validationResultId = workspace.validation_result_id
  const replayPending = pendingAction === "run_replay"
  const activeEvidence = evidenceCategories.find(
    (category) => category.category_id === activeEvidenceCategory,
  )
  const selectedProfile = workspace.profile.options.find(
    (option) => option.selected,
  )
  const enrichmentStepFallbacks = [
    "자료 보강",
    "재검증",
    "새 결과 저장",
    "Final Review",
  ]
  const enrichmentStatusLabels: Record<string, string> = {
    completed: "완료",
    current: "지금 할 일",
    blocked: "확인 필요",
    next: "다음 단계",
    pending: "대기",
  }

  return (
    <main className="pv2-workspace" data-surface={surface}>
      {surface === "context" && (
        <>
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
      </header>

      <section className="pv2-step">
        <StepTitle
          step="1. 후보와 검증 기준"
          title="무엇을 어떤 기준으로 검증하는가"
          detail="후보와 판정 기준을 먼저 고정합니다."
        />
        <div className="pv2-selection-summary">
          <div>
            <span>검증 대상</span>
            <strong>{workspace.candidate.title}</strong>
            <small>
              {workspace.candidate.source_type_label} ·{" "}
              {workspace.candidate.as_of || "기준일 미측정"}
            </small>
          </div>
          <div>
            <span>판정 기준</span>
            <strong>{selectedProfile?.label || "판정 기준 미선택"}</strong>
          </div>
        </div>
        <div className="pv2-provenance-block pv2-candidate-provenance">
          <div>
            <strong>검증 대상 요약</strong>
            <p>Level 1에서 넘어온 후보의 핵심 조건만 확인합니다.</p>
          </div>
          <dl className="pv2-provenance-grid">
            <div>
              <dt>백테스트 기간</dt>
              <dd>{workspace.candidate.provenance.period_label}</dd>
            </div>
            <div>
              <dt>CAGR</dt>
              <dd>{workspace.candidate.provenance.cagr_label}</dd>
            </div>
            <div>
              <dt>MDD</dt>
              <dd>{workspace.candidate.provenance.mdd_label}</dd>
            </div>
            <div>
              <dt>구성</dt>
              <dd>{workspace.candidate.provenance.component_count}개 전략</dd>
            </div>
            <div>
              <dt>Data Trust</dt>
              <dd>{workspace.candidate.provenance.data_trust_label}</dd>
              <small>
                {workspace.candidate.provenance.warning_count > 0
                  ? `주의 ${workspace.candidate.provenance.warning_count}건`
                  : "경고 없음"}
              </small>
            </div>
          </dl>
        </div>
        <div className="pv2-selection-section pv2-candidate-section">
          <div className="pv2-selection-control-row">
            <div className="pv2-subsection-title">
              <span>1A</span>
              <div>
                <h3>1A. 검증할 후보</h3>
                <p>현재 후보를 바꾸려면 목록을 여세요.</p>
              </div>
            </div>
            <button
              type="button"
              className="pv2-candidate-toggle"
              aria-expanded={candidateListOpen}
              onClick={() => setCandidateListOpen((open) => !open)}
            >
              {candidateListOpen ? "후보 목록 닫기" : "후보 변경"}
            </button>
          </div>
          {candidateListOpen && (
            <div className="pv2-candidate-list">
              {workspace.candidate_selector.options.map((option) => (
                <button
                  type="button"
                  className={option.selected ? "is-selected" : ""}
                  aria-pressed={option.selected}
                  disabled={!option.eligible}
                  key={option.selection_source_id}
                  onClick={() => {
                    if (option.selected) {
                      setCandidateListOpen(false)
                      return
                    }
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
          )}
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
          <details
            className="pv2-profile-adjustment"
            defaultOpen={workspace.profile.profile_id === "custom"}
          >
            <summary>판정 기준 세부 조정</summary>
            <p>
              선택한 관점을 유지하면서 실제 목적과 손실 허용 범위에 맞게
              판정 기준을 조정합니다.
            </p>
            <div className="pv2-threshold-summary">
              <div>
                <span>Rolling</span>
                <strong>
                  {workspace.profile.threshold_summary.rolling_window_months}개월
                </strong>
              </div>
              <div>
                <span>MDD 검토선</span>
                <strong>
                  {workspace.profile.threshold_summary.mdd_review_line}%
                </strong>
              </div>
              <div>
                <span>편도 거래비용</span>
                <strong>
                  {workspace.profile.threshold_summary.one_way_cost_bps} bps
                </strong>
              </div>
            </div>
            <div className="pv2-profile-question-grid">
              {workspace.profile.questions.map((question) => (
                <label key={question.question_id}>
                  <span>{question.label}</span>
                  <select
                    value={question.value}
                    onChange={(event) =>
                      emit({
                        action: "update_profile_answer",
                        intent_id: intentId("profile-answer"),
                        selection_source_id:
                          workspace.candidate.selection_source_id,
                        validation_result_id: workspace.validation_result_id,
                        question_id: question.question_id,
                        answer: event.currentTarget.value,
                      })
                    }
                  >
                    {question.options.map((option) => (
                      <option value={option.value} key={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
              ))}
            </div>
          </details>
        </div>
      </section>

        </>
      )}

      {surface === "decision" && (
        <>
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
        {workspace.enrichment_lifecycle.visible && (
          <section
            className={`pv2-enrichment-lifecycle pv2-tone-${workspace.enrichment_lifecycle.collection_summary.tone}`}
            aria-label="자료 보강 후 Final Review 진행 상태"
          >
            <header>
              <div>
                <span>보강 이후 진행 상태</span>
                <h3>{workspace.enrichment_lifecycle.headline}</h3>
                <p>{workspace.enrichment_lifecycle.next_action}</p>
              </div>
              {workspace.enrichment_lifecycle.collection_summary.total_count > 0 && (
                <strong>
                  {workspace.enrichment_lifecycle.collection_summary.outcome_label}
                </strong>
              )}
            </header>
            <ol className="pv2-enrichment-steps">
              {workspace.enrichment_lifecycle.steps.map((step, index) => (
                <li className={`is-${step.status}`} key={step.key}>
                  <span>{index + 1}</span>
                  <div>
                    <strong>{step.label || enrichmentStepFallbacks[index]}</strong>
                    <small>{enrichmentStatusLabels[step.status] || step.status}</small>
                  </div>
                </li>
              ))}
            </ol>
            {workspace.enrichment_lifecycle.collection_summary.total_count > 0 && (
              <p className="pv2-enrichment-outcome">
                보강 작업 {workspace.enrichment_lifecycle.collection_summary.total_count}개 · 완료{" "}
                {workspace.enrichment_lifecycle.collection_summary.success_count} · 확인{" "}
                {workspace.enrichment_lifecycle.collection_summary.review_count} · 실패{" "}
                {workspace.enrichment_lifecycle.collection_summary.failure_count}
              </p>
            )}
          </section>
        )}
        <div className="pv2-recheck-mode-panel">
          <div>
            <strong>재검증 범위</strong>
            <p>이번 검증에서 사용할 기간을 먼저 확인하세요.</p>
          </div>
          <div className="pv2-recheck-mode-grid">
            {workspace.replay.mode_options.map((option) => (
              <button
                type="button"
                className={option.selected ? "is-selected" : ""}
                aria-pressed={option.selected}
                key={option.value}
                onClick={() => {
                  if (option.selected) return
                  emit({
                    action: "select_recheck_mode",
                    intent_id: intentId("recheck-mode"),
                    selection_source_id:
                      workspace.candidate.selection_source_id,
                    validation_result_id: workspace.validation_result_id,
                    recheck_mode: option.value,
                  })
                }}
              >
                <span>
                  {option.label}
                  {option.recommended && <small>권장</small>}
                </span>
                <small>{option.description}</small>
              </button>
            ))}
          </div>
        </div>
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
        {workspace.replay.provenance.visible && (
          <div className="pv2-provenance-block pv2-replay-provenance">
            <div>
              <strong>재검증 기록</strong>
              <p>선택한 범위가 실제로 어디까지 계산됐는지 확인합니다.</p>
            </div>
            <dl className="pv2-provenance-grid">
              <div>
                <dt>재검증 범위</dt>
                <dd>{workspace.replay.provenance.mode_label}</dd>
              </div>
              <div>
                <dt>요청 기간</dt>
                <dd>{workspace.replay.provenance.requested_period_label}</dd>
              </div>
              <div>
                <dt>실제 기간</dt>
                <dd>{workspace.replay.provenance.actual_period_label}</dd>
              </div>
              <div>
                <dt>최신 공통 가격일</dt>
                <dd>{workspace.replay.provenance.latest_common_price_date}</dd>
              </div>
              <div>
                <dt>기간 Coverage</dt>
                <dd>{workspace.replay.provenance.coverage_status}</dd>
                <small>종료일 차이 {workspace.replay.provenance.end_gap_days}일</small>
              </div>
            </dl>
            {workspace.replay.provenance.limiting_symbols.length > 0 && (
              <p className="pv2-provenance-warning">
                기간 제한 종목 · {workspace.replay.provenance.limiting_symbols.join(", ")}
              </p>
            )}
          </div>
        )}
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
                  <div className="pv2-evidence-title">
                    <strong>{item.display_title}</strong>
                    <span>{item.status_label}</span>
                  </div>
                  <small>{item.what_was_checked}</small>
                  <p>{item.result_summary}</p>
                  <p className="pv2-evidence-meaning">{item.meaning}</p>
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
                  pendingAction={pendingAction}
                  onActionStart={setPendingAction}
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
        {workspace.handoff_summary.items.length > 0 && (
          <div className="pv2-handoff-summary">
            <header>
              <div>
                <span>Final Review handoff</span>
                <h3>{workspace.handoff_summary.title}</h3>
                <p>{workspace.handoff_summary.detail}</p>
              </div>
              <dl>
                {workspace.handoff_summary.counts.accepted_limit > 0 && (
                  <div><dt>인수할 한계</dt><dd>{workspace.handoff_summary.counts.accepted_limit}</dd></div>
                )}
                {workspace.handoff_summary.counts.final_decision > 0 && (
                  <div><dt>최종 판단</dt><dd>{workspace.handoff_summary.counts.final_decision}</dd></div>
                )}
                {workspace.handoff_summary.counts.monitoring_transfer > 0 && (
                  <div><dt>Monitoring</dt><dd>{workspace.handoff_summary.counts.monitoring_transfer}</dd></div>
                )}
              </dl>
            </header>
            <div className="pv2-handoff-items">
              {workspace.handoff_summary.items.map((item) => (
                <article key={item.root_issue_id}>
                  <span>{item.handoff_label}</span>
                  <strong>{item.title}</strong>
                  <p>{item.summary}</p>
                  <small>{item.next_stage_action}</small>
                </article>
              ))}
            </div>
          </div>
        )}
        <details className="pv2-disclosure">
          <summary>상세 검증 근거</summary>
          <div
            className="pv2-evidence-category-tabs"
            role="tablist"
            aria-label="상세 검증 범주"
          >
            {evidenceCategories.map((group) => (
              <button
                type="button"
                role="tab"
                aria-selected={group.category_id === activeEvidenceCategory}
                className={
                  group.category_id === activeEvidenceCategory
                    ? "is-selected"
                    : ""
                }
                key={group.category_id}
                onClick={() => setActiveEvidenceCategory(group.category_id)}
              >
                <strong>{group.title}</strong>
                <span>{group.summary.total_count}개 · {group.outcome}</span>
              </button>
            ))}
          </div>
          {activeEvidence && (
            <article className="pv2-evidence-panel" role="tabpanel">
              <header>
                <div>
                  <strong>{activeEvidence.title}</strong>
                  <p>{activeEvidence.question}</p>
                </div>
                <span>{activeEvidence.outcome}</span>
              </header>
              <dl className="pv2-evidence-summary">
                <div>
                  <dt>확인 완료</dt>
                  <dd>{activeEvidence.summary.verified_count}</dd>
                </div>
                <div>
                  <dt>주의</dt>
                  <dd>{activeEvidence.summary.review_count}</dd>
                </div>
                <div>
                  <dt>보강 필요</dt>
                  <dd>{activeEvidence.summary.missing_count}</dd>
                </div>
                <div>
                  <dt>해당 없음</dt>
                  <dd>{activeEvidence.summary.not_applicable_count}</dd>
                </div>
              </dl>
              {activeEvidence.explanations.length > 0 ? (
                <ul>
                  {activeEvidence.explanations.map((row, index) => (
                    <li
                      key={`${activeEvidence.category_id}-${row.technical_trace.criterion}-${index}`}
                    >
                      <div className="pv2-evidence-title">
                        <b>{row.display_title}</b>
                        <span>{row.status_label}</span>
                      </div>
                      <dl className="pv2-explanation-grid">
                        <div>
                          <dt>무엇을 확인했나</dt>
                          <dd>{row.what_was_checked}</dd>
                        </div>
                        <div>
                          <dt>확인 결과</dt>
                          <dd>{row.result_summary}</dd>
                        </div>
                        <div>
                          <dt>이 결과의 의미</dt>
                          <dd>{row.meaning}</dd>
                        </div>
                        <div>
                          <dt>다음 조치</dt>
                          <dd>{row.next_action}</dd>
                        </div>
                      </dl>
                      <details className="pv2-technical-trace">
                        <summary>기술 원문</summary>
                        <p>Criteria: {row.technical_trace.criterion || "-"}</p>
                        <p>Status: {row.technical_trace.status || "-"}</p>
                        <p>Current: {row.technical_trace.current || "-"}</p>
                        <p>Evidence: {row.technical_trace.evidence || "-"}</p>
                      </details>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="pv2-empty-evidence">
                  이 범주에 저장된 상세 검증 근거가 없습니다.
                </p>
              )}
            </article>
          )}
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
        {workspace.record.visible && (
          <details className="pv2-record-disclosure">
            <summary>검증 기록</summary>
            <p>
              저장하거나 Final Review로 이동할 때 이어지는 현재 세션의 식별 정보입니다.
            </p>
            <dl className="pv2-provenance-grid">
              <div>
                <dt>판정 프로필</dt>
                <dd>{workspace.record.profile_label}</dd>
              </div>
              <div>
                <dt>재검증 방식</dt>
                <dd>{workspace.record.recheck_mode_label}</dd>
              </div>
              <div>
                <dt>실행 시각</dt>
                <dd>{workspace.record.attempted_at}</dd>
              </div>
              <div>
                <dt>Replay ID</dt>
                <dd>{workspace.record.replay_id}</dd>
              </div>
              <div>
                <dt>Validation ID</dt>
                <dd>{workspace.record.validation_id}</dd>
              </div>
            </dl>
          </details>
        )}
      </section>
        </>
      )}
    </main>
  )
}
