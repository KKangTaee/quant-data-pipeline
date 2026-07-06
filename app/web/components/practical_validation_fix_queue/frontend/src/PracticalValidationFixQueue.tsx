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
  reviewCriteria?: string[]
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
  reviewCount: number
}

const toneClass = (tone: Tone | string | undefined): Tone =>
  ["positive", "warning", "danger", "neutral"].includes(String(tone)) ? (tone as Tone) : "neutral"

const compact = (value: unknown, fallback = "-"): string => {
  const text = String(value ?? "").trim()
  return text || fallback
}

export function PracticalValidationFixQueue(props: PracticalValidationFixQueueProps) {
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [props])

  const tone = toneClass(props.tone)
  const fixItems =
    props.fixItems.length > 0
      ? props.fixItems
      : [
          {
            label: "필수 보강 항목 없음",
            status: "Ready",
            statusLabel: "통과",
            displayLabel: "필수 보강 항목 없음",
            issueTitle: "Final Review 이동을 막는 이슈 없음",
            fixLocation: "Flow 5",
            currentProblem: "현재 기준에서 Final Review 이동을 즉시 막는 이슈가 없습니다.",
            completionCriteria: "Flow 5에서 저장 / 이동 전에 핵심 기준만 한 번 더 확인합니다.",
            impactSummary: "필수 blocker가 없으면 Final Review에서 최종 판단과 모니터링 후보 가능 여부를 확인할 수 있습니다.",
            tone: "positive" as Tone,
          },
        ]
  const coreGroups = props.coreGroups.length > 0 ? props.coreGroups : []
  const criteriaGroups = props.criteriaGroups.length > 0 ? props.criteriaGroups : []
  const visibleFixItems = fixItems.slice(0, 3)
  const hiddenFixCount = Math.max(fixItems.length - visibleFixItems.length, 0)
  const visibleCriteriaGroups = criteriaGroups.slice(0, 3)
  const hiddenCriteriaGroupCount = Math.max(criteriaGroups.length - visibleCriteriaGroups.length, 0)
  const flowAction = props.canSaveAndMove
    ? "Flow 5에서 저장 / 이동"
    : "먼저 해결 후 Flow 5에서 저장 / 이동"
  const nextStepItems = props.canSaveAndMove
    ? [
        "Flow 5에서 검증 결과를 저장하고 Final Review로 이동합니다.",
        "Final Review에서 최종 판단과 모니터링 후보 저장 가능 여부를 확인합니다.",
      ]
    : [
        "아래 이슈의 완료 기준을 먼저 맞춘 뒤 Flow 5에서 저장 / 이동을 다시 시도합니다.",
        "Flow 4의 카테고리별 검증 결과에서 통과한 기준과 남은 문제를 함께 확인합니다.",
      ]

  return (
    <section className={`pv-react-fix pv-react-fix--${tone}`}>
      <header className="pv-react-fix__head">
        <div>
          <div className="pv-react-fix__kicker">Final Review 이동 판단</div>
          <h4>{props.verdict}</h4>
          {props.nextAction ? <p>{props.nextAction}</p> : null}
        </div>
        <div className="pv-react-fix__status">
          <span>{props.statusLabel}</span>
          <b>{props.canSaveAndMove ? "Final Review 이동 가능" : "Final Review 이동 보류"}</b>
          <small>{props.fixItems.length > 0 ? `먼저 해결 ${props.fixItems.length}` : "즉시 막는 항목 없음"}</small>
        </div>
      </header>

      <div className="pv-react-fix__decision">
        <div className="pv-react-fix__summary" aria-label="카테고리별 검증 결과 요약">
          <span>
            <b>{props.statusLabel}</b> 검증 결과
          </span>
          <span>
            <b>{props.fixItems.length}</b> 막는 이슈
          </span>
          <span>
            <b>{props.reviewCount}</b> Final Review 확인
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
            {props.canSaveAndMove ? "이동 준비" : "이동 보류"}
          </div>
          <div className="pv-react-fix__action-text">{flowAction}</div>
        </div>
        <p>최종 선택, 투자 추천, live 승인, 주문 지시는 만들지 않습니다.</p>
      </footer>

      <div className="pv-react-fix__body">
        <section className="pv-react-fix__lane">
          <div className="pv-react-fix__lane-title">Final Review 이동을 막는 이슈</div>
          <div className="pv-react-fix__items">
            {visibleFixItems.map((item, index) => (
              <article
                className={`pv-react-fix__item pv-react-fix__item--${toneClass(item.tone)}`}
                key={`${item.label ?? "fix"}-${index}`}
              >
                <div>
                  <span>{item.statusLabel ?? item.status ?? "-"}</span>
                  <h5>{item.issueTitle ?? item.displayLabel ?? item.label ?? "-"}</h5>
                </div>
                <dl className="pv-react-fix__readable">
                  <dt>현재 문제</dt>
                  <dd>{item.currentProblem ?? item.gateReason ?? item.missingEvidence ?? "-"}</dd>
                  <dt>완료 기준</dt>
                  <dd>{item.completionCriteria ?? item.actionLabel ?? item.fixAction ?? "-"}</dd>
                  <dt>보강 위치</dt>
                  <dd>{item.fixLocation ?? "-"}</dd>
                </dl>
                {item.impactSummary || item.whyItMatters ? (
                  <p className="pv-react-fix__why">{item.impactSummary ?? item.whyItMatters}</p>
                ) : null}
                <small>기술 기준: {item.technicalLabel ?? `${item.label ?? "-"} · ${item.status ?? "-"}`}</small>
              </article>
            ))}
            {hiddenFixCount > 0 ? (
              <div className="pv-react-fix__more">나머지 {hiddenFixCount}개는 Flow 4 카테고리별 검증 결과에서 이어서 확인합니다.</div>
            ) : null}
          </div>
        </section>

        <section className="pv-react-fix__lane pv-react-fix__criteria-preview">
          <div className="pv-react-fix__lane-title">카테고리별 검증 결과</div>
          <div className="pv-react-fix__groups">
            {visibleCriteriaGroups.map((group, index) => (
              <article
                className={`pv-react-fix__group pv-react-fix__group--${toneClass(group.tone)}`}
                key={`${group.label ?? "criteria"}-${index}`}
              >
                <div>
                  <h5>{compact(group.displayLabel ?? group.label)}</h5>
                  <span>{compact(group.status)}</span>
                </div>
                <p>{compact(group.purpose)}</p>
                <dl className="pv-react-fix__criteria-summary">
                  <dt>상태</dt>
                  <dd>{compact(group.status)}</dd>
                  <dt>통과한 기준</dt>
                  <dd>{group.passedCriteria && group.passedCriteria.length > 0 ? group.passedCriteria.join(" / ") : "없음"}</dd>
                  <dt>남은 문제</dt>
                  <dd>{group.remainingIssues && group.remainingIssues.length > 0 ? group.remainingIssues.join(" / ") : "없음"}</dd>
                  <dt>판정</dt>
                  <dd>{compact(group.decisionSummary)}</dd>
                </dl>
              </article>
            ))}
            {hiddenCriteriaGroupCount > 0 ? (
              <div className="pv-react-fix__more">추가 기준 그룹 {hiddenCriteriaGroupCount}개는 Flow 4에서 확인합니다.</div>
            ) : null}
            {criteriaGroups.length === 0 ? (
              <article className="pv-react-fix__group pv-react-fix__group--neutral">
                <div>
                  <h5>기준 상세 그룹 없음</h5>
                  <span>-</span>
                </div>
                <p>workspace read model에 표시할 카테고리별 검증 결과가 없습니다.</p>
              </article>
            ) : null}
          </div>
        </section>
      </div>
    </section>
  )
}
