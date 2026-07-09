import React, { useEffect } from "react"
import { Streamlit } from "streamlit-component-lib"

type Tone = "positive" | "warning" | "danger" | "neutral"

type FixItem = {
  label?: string
  status?: string
  statusLabel?: string
  displayLabel?: string
  issueTitle?: string
  currentProblem?: string
  completionCriteria?: string
  impactSummary?: string
  checkedEvidence?: string
  missingEvidence?: string
  actionLabel?: string
  whyItMatters?: string
  technicalLabel?: string
  fixLocation?: string
  fixAction?: string
  gateReason?: string
  tone?: Tone
}

type CoreGroup = {
  label?: string
  status?: string
  purpose?: string
  tone?: Tone
  modules?: string[]
}

type CriteriaCard = {
  label?: string
  displayLabel?: string
  issueTitle?: string
  status?: string
  statusLabel?: string
  technicalLabel?: string
  tone?: Tone
  explanation?: string
  evidence?: string
  currentProblem?: string
  completionCriteria?: string
  fixLocation?: string
  impactSummary?: string
  checkedEvidence?: string
  missingEvidence?: string
  actionLabel?: string
  whyItMatters?: string
  resolutionSurface?: string
}

type CriteriaGroup = {
  label?: string
  displayLabel?: string
  status?: string
  purpose?: string
  passedCriteria?: string[]
  remainingIssues?: string[]
  decisionSummary?: string
  tone?: Tone
  criteriaCards?: CriteriaCard[]
}

type ActionSpec = {
  id?: string
  label?: string
  detail?: string
  enabled?: boolean
  tone?: Tone
}

type NextStageAction = {
  targetStage?: string
  statusLabel?: string
  blockerCount?: number
  disabledReason?: string
  primaryAction?: ActionSpec
  secondaryAction?: ActionSpec
  boundaryNote?: string
}

type PracticalValidationFixQueueProps = {
  statusLabel: string
  tone: Tone
  verdict: string
  nextAction: string
  canSaveAndMove: boolean
  fixItems: FixItem[]
  coreGroups: CoreGroup[]
  criteriaGroups: CriteriaGroup[]
  nextStageAction: NextStageAction
}

const toneClass = (tone: Tone | string | undefined): Tone =>
  ["positive", "warning", "danger", "neutral"].includes(String(tone)) ? (tone as Tone) : "neutral"

const compact = (value: unknown, fallback = "-"): string => {
  const text = String(value ?? "").trim()
  return text || fallback
}

const joined = (items: string[] | undefined, fallback = "없음"): string => {
  const cleaned = (items ?? []).map((item) => compact(item, "")).filter(Boolean)
  return cleaned.length > 0 ? cleaned.join(" / ") : fallback
}

const reviewStatusLabel = (status: unknown): string => {
  const text = compact(status, "")
  const labels = ["데이터 주의", "2단계 실용성 주의", "최종 판단 참고", "Monitoring 추적"]
  const matched = labels.find((label) => text.startsWith(label))
  if (matched) return matched
  if (text.startsWith("REVIEW")) return "주의"
  return ""
}

const roleAwareGroupOutcome = (group: CriteriaGroup): { label: string; detail: string; tone: Tone } => {
  if (group.remainingIssues && group.remainingIssues.length > 0) {
    return { label: "실패", detail: joined(group.remainingIssues), tone: "danger" }
  }
  const reviewLabel = reviewStatusLabel(group.status)
  if (reviewLabel) {
    const tone = toneClass(group.tone)
    return {
      label: reviewLabel,
      detail: compact(group.decisionSummary),
      tone: tone === "neutral" ? "warning" : tone,
    }
  }
  if (group.passedCriteria && group.passedCriteria.length > 0) {
    return { label: "통과", detail: joined(group.passedCriteria), tone: "positive" }
  }
  return { label: "검토", detail: compact(group.decisionSummary), tone: toneClass(group.tone) }
}

const saveAndMovePayload = () => ({
  action: "save_and_move",
  source: "practical_validation_fix_queue",
  nonce: `${Date.now()}`,
})

const saveAuditOnlyPayload = () => ({
  action: "save_audit_only",
  source: "practical_validation_fix_queue",
  nonce: `${Date.now()}`,
})

const actionEnabled = (action: ActionSpec | undefined): boolean => action?.enabled !== false

export function PracticalValidationFixQueue(props: PracticalValidationFixQueueProps) {
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [props])

  const tone = toneClass(props.tone)
  const coreGroups = props.coreGroups.length > 0 ? props.coreGroups : []
  const criteriaGroups = props.criteriaGroups.length > 0 ? props.criteriaGroups : []
  const visibleCriteriaGroups = criteriaGroups.slice(0, 7)
  const hiddenCriteriaGroupCount = Math.max(criteriaGroups.length - visibleCriteriaGroups.length, 0)
  const failedCategoryCount = criteriaGroups.filter((group) => (group.remainingIssues ?? []).length > 0).length
  const fallbackNextStageAction: NextStageAction = {
    targetStage: "Final Review",
    statusLabel: props.canSaveAndMove ? "이동 가능" : "보강 필요",
    blockerCount: props.fixItems.length,
    disabledReason: props.canSaveAndMove ? "" : "자세한 원인과 보강 기준은 Flow 4에서 확인합니다.",
    primaryAction: {
      id: "save_and_move",
      label: "저장하고 Final Review로 이동",
      detail: props.canSaveAndMove
        ? "검증 결과를 저장하고 Final Review에서 최종 판단을 이어갑니다."
        : "Flow 4에서 보강 항목을 확인한 뒤 다시 시도합니다.",
      enabled: props.canSaveAndMove,
      tone: props.canSaveAndMove ? "positive" : "danger",
    },
    secondaryAction: {
      id: "save_audit_only",
      label: "검증 결과 저장(기록용)",
      detail: "audit trail만 남깁니다.",
      enabled: true,
      tone: "neutral",
    },
    boundaryNote: "Final Review 이동은 최종 승인, 투자 추천, live approval, broker order, auto rebalance가 아닙니다.",
  }
  const nextStageAction: NextStageAction = {
    ...fallbackNextStageAction,
    ...props.nextStageAction,
    primaryAction: {
      ...fallbackNextStageAction.primaryAction,
      ...(props.nextStageAction?.primaryAction ?? {}),
    },
    secondaryAction: {
      ...fallbackNextStageAction.secondaryAction,
      ...(props.nextStageAction?.secondaryAction ?? {}),
    },
  }
  const primaryAction = nextStageAction.primaryAction
  const secondaryAction = nextStageAction.secondaryAction
  const primaryEnabled = actionEnabled(primaryAction)
  const secondaryEnabled = actionEnabled(secondaryAction)
  const nextStepItems = primaryEnabled
    ? [compact(primaryAction?.detail, "검증 결과를 저장하고 Final Review에서 최종 판단을 이어갑니다.")]
    : [compact(nextStageAction.disabledReason ?? primaryAction?.detail, "자세한 원인과 보강 기준은 Flow 4에서 확인합니다.")]

  const submitSaveAndMove = () => {
    if (!primaryEnabled) return
    Streamlit.setComponentValue(saveAndMovePayload())
  }

  const submitSaveAuditOnly = () => {
    if (!secondaryEnabled) return
    Streamlit.setComponentValue(saveAuditOnlyPayload())
  }

  return (
    <section className={`pv-react-fix pv-react-fix--${tone}`}>
      <header className="pv-react-fix__head">
        <div>
          <div className="pv-react-fix__kicker">Practical Validation 검증 결론</div>
          <h4>{props.verdict}</h4>
          {props.nextAction ? <p>{props.nextAction}</p> : null}
        </div>
        <div className="pv-react-fix__status">
          <span>{props.statusLabel}</span>
          <b>{props.canSaveAndMove ? "검증 보강 완료" : "검증 보강 필요"}</b>
          <small>{props.fixItems.length > 0 ? `보강 항목 ${props.fixItems.length}` : "현재 보강 기준 없음"}</small>
        </div>
      </header>

      <div className="pv-react-fix__decision">
        <div className="pv-react-fix__summary" aria-label="검증 결론 요약">
          <span>
            <b>{props.statusLabel}</b> 검증 상태
          </span>
          <span>
            <b>{failedCategoryCount}</b> 실패 카테고리
          </span>
          <span>
            <b>{criteriaGroups.length || coreGroups.length}</b> 검증 카테고리
          </span>
        </div>

        <aside className="pv-react-fix__next">
          <div className="pv-react-fix__lane-title">다음 단계</div>
          <ul>
            {nextStepItems.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        </aside>
      </div>

      <footer className="pv-react-fix__action">
        <div>
          <div className="pv-react-fix__action-label">
            {primaryEnabled ? "다음 위치" : "상세 확인 위치"}
          </div>
          <div className="pv-react-fix__action-text">
            {primaryEnabled ? compact(nextStageAction.targetStage) : compact(nextStageAction.disabledReason)}
          </div>
        </div>
        <div className="pv-react-fix__buttons">
          <button
            className="pv-react-fix__button pv-react-fix__button--primary"
            disabled={!primaryEnabled}
            onClick={submitSaveAndMove}
            type="button"
          >
            {compact(primaryAction?.label, "저장하고 Final Review로 이동")}
          </button>
          <button
            className="pv-react-fix__button pv-react-fix__button--secondary"
            disabled={!secondaryEnabled}
            onClick={submitSaveAuditOnly}
            type="button"
          >
            {compact(secondaryAction?.label, "검증 결과 저장(기록용)")}
          </button>
        </div>
        <p>{compact(secondaryAction?.detail, "audit trail만 남깁니다.")}</p>
        <p>{compact(nextStageAction.boundaryNote)}</p>
      </footer>

      <div className="pv-react-fix__body pv-react-fix__body--single">
        <section className="pv-react-fix__lane pv-react-fix__criteria-preview">
          <div className="pv-react-fix__lane-title">카테고리별 검증 요약</div>
          <div className="pv-react-fix__groups pv-react-fix__groups--compact">
            {visibleCriteriaGroups.map((group, index) => {
              const outcome = roleAwareGroupOutcome(group)
              return (
                <article className={`pv-react-fix__group pv-react-fix__group--${outcome.tone}`} key={`${group.label ?? "criteria"}-${index}`}>
                  <div>
                    <h5>{compact(group.displayLabel ?? group.label)}</h5>
                    <span>{compact(group.status)}</span>
                  </div>
                  <p>
                    <b>{outcome.label}</b>: {outcome.detail}
                  </p>
                  {(group.remainingIssues ?? []).length > 0 && (group.passedCriteria ?? []).length > 0 ? (
                    <small>통과: {joined(group.passedCriteria)}</small>
                  ) : null}
                </article>
              )
            })}
            {hiddenCriteriaGroupCount > 0 ? (
              <div className="pv-react-fix__more">나머지 {hiddenCriteriaGroupCount}개 카테고리는 Flow 4에서 확인합니다.</div>
            ) : null}
            {criteriaGroups.length === 0 ? (
              <article className="pv-react-fix__group pv-react-fix__group--neutral">
                <div>
                  <h5>검증 카테고리 없음</h5>
                  <span>-</span>
                </div>
                <p>workspace read model에 표시할 카테고리별 검증 요약이 없습니다.</p>
              </article>
            ) : null}
          </div>
        </section>
      </div>
    </section>
  )
}
