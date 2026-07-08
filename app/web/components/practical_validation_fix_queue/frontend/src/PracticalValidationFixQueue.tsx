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

type PracticalValidationFixQueueProps = {
  statusLabel: string
  tone: Tone
  verdict: string
  nextAction: string
  canSaveAndMove: boolean
  fixItems: FixItem[]
  coreGroups: CoreGroup[]
  criteriaGroups: CriteriaGroup[]
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

const groupOutcome = (group: CriteriaGroup): { label: string; detail: string; tone: Tone } => {
  if (group.remainingIssues && group.remainingIssues.length > 0) {
    return { label: "실패", detail: joined(group.remainingIssues), tone: "danger" }
  }
  if (group.passedCriteria && group.passedCriteria.length > 0) {
    return { label: "통과", detail: joined(group.passedCriteria), tone: "positive" }
  }
  if (compact(group.status, "").includes("보강 항목 없음")) {
    return { label: "통과", detail: compact(group.decisionSummary, "보강 항목 없음"), tone: "positive" }
  }
  return { label: "확인 필요", detail: compact(group.decisionSummary), tone: toneClass(group.tone) }
}

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
  const flowAction = props.canSaveAndMove
    ? "Flow 5에서 검증 결과 저장"
    : "Flow 4에서 상세 원인 확인"
  const nextStepItems = props.canSaveAndMove
    ? ["Flow 5에서 검증 결과를 저장합니다."]
    : ["자세한 원인과 보강 기준은 Flow 4에서 확인합니다."]

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
          <small>{props.fixItems.length > 0 ? `보강 항목 ${props.fixItems.length}` : "보강 항목 없음"}</small>
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
            {props.canSaveAndMove ? "다음 위치" : "상세 확인 위치"}
          </div>
          <div className="pv-react-fix__action-text">{flowAction}</div>
        </div>
      </footer>

      <div className="pv-react-fix__body pv-react-fix__body--single">
        <section className="pv-react-fix__lane pv-react-fix__criteria-preview">
          <div className="pv-react-fix__lane-title">카테고리별 검증 요약</div>
          <div className="pv-react-fix__groups pv-react-fix__groups--compact">
            {visibleCriteriaGroups.map((group, index) => (
              <article className={`pv-react-fix__group pv-react-fix__group--${groupOutcome(group).tone}`} key={`${group.label ?? "criteria"}-${index}`}>
                <div>
                  <h5>{compact(group.displayLabel ?? group.label)}</h5>
                  <span>{compact(group.status)}</span>
                </div>
                <p>
                  <b>{groupOutcome(group).label}</b>: {groupOutcome(group).detail}
                </p>
                {(group.remainingIssues ?? []).length > 0 && (group.passedCriteria ?? []).length > 0 ? (
                  <small>통과: {joined(group.passedCriteria)}</small>
                ) : null}
              </article>
            ))}
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
