import React, { useEffect, useMemo, useState } from "react"
import {
  CandidateSelectorModel,
  DecisionBrief,
  DecisionBriefObservation,
  DecisionWorkspaceIntent,
  MonitoringCondition,
  Tone,
} from "./decisionBriefTypes"
import {
  CumulativeComparisonChart,
  PortfolioTraitMap as PortfolioTraitMapChart,
  UnderwaterChart,
} from "./DecisionBriefCharts"

type WorkspaceProps = {
  decisionBrief: DecisionBrief
  candidateSelector: CandidateSelectorModel
  onIntent: (intent: DecisionWorkspaceIntent) => void
}

function nextIntentId(prefix: string) {
  const generated = globalThis.crypto?.randomUUID?.()
  return generated ? `${prefix}-${generated}` : `${prefix}-${Date.now()}`
}

function SectionHeading({ eyebrow, title, detail }: { eyebrow: string; title: string; detail?: string }) {
  return (
    <header className="db-section-heading">
      <div className="db-section-heading-copy">
        <p className="db-kicker">{eyebrow}</p>
        <h2>{title}</h2>
      </div>
      {detail && <p className="db-section-detail">{detail}</p>}
    </header>
  )
}

function CandidateSelector({
  model,
  onIntent,
}: {
  model: CandidateSelectorModel
  onIntent: WorkspaceProps["onIntent"]
}) {
  const selectedIndex = model.options.findIndex((option) => option.selected)
  const selected = model.options[selectedIndex]
  return (
    <aside className="db-candidate-summary" aria-labelledby="db-candidate-title">
      <div className="db-candidate-summary-heading">
        <small>검토 후보 · {selectedIndex >= 0 ? selectedIndex + 1 : 0} / {model.options.length}</small>
        <strong id="db-candidate-title">{selected?.title || "검토할 후보를 선택하세요"}</strong>
        <span>{selected?.validation_id || selected?.source_type || "저장된 검증 없음"}</span>
      </div>
      <div className="db-candidate-options" role="list" aria-label="Final Review 후보 선택">
        {model.options.map((option) => (
          <button
            type="button"
            role="listitem"
            className={option.selected ? "is-selected" : ""}
            disabled={!option.eligible}
            key={option.source_id}
            onClick={() => {
              if (option.selected) return
              onIntent({
                action: "select_candidate",
                intent_id: nextIntentId("candidate"),
                source_id: option.source_id,
              })
            }}
          >
            <span>{option.title}</span>
            <small>{option.validation_id || option.source_type}</small>
          </button>
        ))}
      </div>
    </aside>
  )
}

function WorkspaceHeader({
  brief,
  model,
  onIntent,
}: {
  brief: DecisionBrief
  model: CandidateSelectorModel
  onIntent: WorkspaceProps["onIntent"]
}) {
  return (
    <header className="db-workspace-header" aria-labelledby="db-workspace-title">
      <div className="db-workspace-intro">
        <p className="db-kicker">Final Review Decision Workspace</p>
        <h1 id="db-workspace-title">이 포트폴리오를 실제 투자 검토 대상으로<br />계속 추적할 가치가 있는가?</h1>
        <p>새 검증을 실행하는 화면이 아니라, 저장된 근거로 추적 가치를 판단하고 이유를 기록하는 화면입니다.</p>
        <span className="db-header-state">{brief.verdict.label}</span>
      </div>
      <CandidateSelector model={model} onIntent={onIntent} />
    </header>
  )
}

function VerdictHero({ brief }: { brief: DecisionBrief }) {
  const period = brief.behavior_board.period
  return (
    <section className={`db-verdict db-tone-${brief.verdict.tone}`} aria-labelledby="db-verdict-title">
      <div className="db-verdict-main">
        <span className="db-route-label">{brief.verdict.label}</span>
        <h1 id="db-verdict-title">{brief.verdict.headline}</h1>
        <p className="db-thesis">{brief.verdict.thesis}</p>
        <div className="db-basis-chips" aria-label="판단 기준">
          <span>관측 {period.start || "미측정"} → {period.end || "미측정"}</span>
          <span>기준일 {brief.candidate.as_of || period.latest_valuation_date || "미측정"}</span>
          <span>{period.frequency || "빈도 미측정"}</span>
        </div>
      </div>
      <aside className="db-confidence" aria-label="근거 신뢰도">
        <span>근거 신뢰도</span>
        <strong>{brief.evidence_confidence.value}</strong>
        <small>{brief.evidence_confidence.label}</small>
        <p>{brief.evidence_confidence.ready_checks} / {brief.evidence_confidence.total_checks} ready checks</p>
      </aside>
    </section>
  )
}

function ObservationStrip({ observations }: { observations: DecisionBriefObservation[] }) {
  if (observations.length === 0) {
    return <div className="db-empty">구성·회전·비용·유동성 관측값이 미측정입니다.</div>
  }
  return (
    <div className="db-observation-strip">
      {observations.map((observation) => (
        <article key={observation.observation_id}>
          <span>{observation.title}</span>
          <strong>{observation.display_value}</strong>
          <p>{observation.interpretation}</p>
          <small>기준 {String(observation.threshold_or_comparator ?? "미측정")} · {observation.as_of || "기준일 없음"}</small>
        </article>
      ))}
    </div>
  )
}

function BehaviorBoard({ brief }: { brief: DecisionBrief }) {
  const board = brief.behavior_board
  return (
    <section className="db-section db-behavior" aria-labelledby="db-behavior-title">
      <SectionHeading
        eyebrow="Observed behavior"
        title="누적 성과, 손실 경로, 실행 현실성"
        detail="차트와 관측값은 저장된 curve와 structured evidence만 사용합니다."
      />
      <div className="db-chart-grid">
        <CumulativeComparisonChart candidate={board.cumulative_series} benchmark={board.benchmark_series} />
        <UnderwaterChart series={board.underwater_series} />
      </div>
      <ObservationStrip observations={board.execution_observations} />
    </section>
  )
}

function FindingColumn({
  title,
  tone,
  items,
}: {
  title: string
  tone: Tone
  items: DecisionBriefObservation[]
}) {
  return (
    <div className={`db-finding-column db-tone-${tone}`}>
      <h3>{title}</h3>
      {items.length === 0 ? (
        <p className="db-empty-inline">직접 비교 가능한 관측값이 없습니다.</p>
      ) : (
        <div className="db-finding-list">
          {items.map((item) => (
            <article key={item.observation_id}>
              <div><strong>{item.title}</strong><span>{item.display_value}</span></div>
              <p>{item.interpretation}</p>
              <small>{item.as_of || "기준일 없음"} · 근거 {item.evidence_refs.length}개</small>
            </article>
          ))}
        </div>
      )}
    </div>
  )
}

function StrengthWeaknessSection({ brief }: { brief: DecisionBrief }) {
  return (
    <section className="db-section db-findings" aria-labelledby="db-findings-title">
      <SectionHeading
        eyebrow="Measured findings"
        title="실제 강점과 약점"
        detail="Gate 통과나 준비 상태가 아니라 관측값과 comparator가 있는 항목만 표시합니다."
      />
      <div className="db-findings-grid">
        <FindingColumn title="관측된 강점" tone="positive" items={brief.strengths} />
        <FindingColumn title="관측된 약점" tone="warning" items={brief.weaknesses} />
      </div>
    </section>
  )
}

function PortfolioTraitMap({ brief }: { brief: DecisionBrief }) {
  return (
    <section className="db-section db-traits" aria-labelledby="db-traits-title">
      <SectionHeading
        eyebrow="Portfolio pressure map"
        title="포트폴리오 성격 지도"
        detail="품질 점수나 순위가 아니라 threshold 대비 pressure와 exposure를 읽습니다."
      />
      <PortfolioTraitMapChart axes={brief.trait_map.axes} />
    </section>
  )
}

function ConditionRow({ condition, index }: { condition: MonitoringCondition; index: number }) {
  return (
    <article className="db-condition-row">
      <span className="db-condition-index">{String(index + 1).padStart(2, "0")}</span>
      <div>
        <h3>{condition.title}</h3>
        <p>{condition.observation}</p>
      </div>
      <dl>
        <div><dt>변화 조건</dt><dd>{condition.threshold}</dd></div>
        <div><dt>확인 주기</dt><dd>{condition.cadence}</dd></div>
        <div><dt>재검토 행동</dt><dd>{condition.re_review_action}</dd></div>
      </dl>
    </article>
  )
}

function MonitoringConditions({ brief }: { brief: DecisionBrief }) {
  return (
    <section className="db-section db-monitoring" aria-labelledby="db-monitoring-title">
      <SectionHeading
        eyebrow="Monitoring change conditions"
        title="무엇이 바뀌면 다시 판단할 것인가"
        detail="저장 가능한 structured condition만 표시합니다."
      />
      {brief.monitoring_conditions.length === 0 ? (
        <div className="db-empty">구조화된 Monitoring 변화 조건이 미측정입니다.</div>
      ) : (
        <div className="db-condition-list">
          {brief.monitoring_conditions.map((condition, index) => (
            <ConditionRow key={condition.observation_id} condition={condition} index={index} />
          ))}
        </div>
      )}
    </section>
  )
}

function DecisionAction({
  brief,
  onIntent,
}: {
  brief: DecisionBrief
  onIntent: WorkspaceProps["onIntent"]
}) {
  const action = brief.decision_action
  const [route, setRoute] = useState(action.suggested_route)
  const [reason, setReason] = useState("")
  useEffect(() => {
    setRoute(action.suggested_route)
    setReason("")
  }, [brief.candidate.source_id, action.suggested_route])
  const selected = action.options.find((option) => option.route === route) ?? action.options[0]
  const canSubmit = Boolean(selected?.recordable && reason.trim())

  return (
    <section className="db-section db-decision" aria-labelledby="db-decision-title">
      <SectionHeading
        eyebrow="Final route"
        title="최종 판단과 사유"
        detail="이 판단은 투자 승인이나 주문이 아니라 계속 추적할 대상인지에 대한 기록입니다."
      />
      <div className="db-route-options" role="radiogroup" aria-label="최종 route">
        {action.options.map((option) => (
          <button
            type="button"
            role="radio"
            aria-checked={route === option.route}
            className={`db-route-option db-tone-${option.tone} ${route === option.route ? "is-selected" : ""}`}
            key={option.route}
            onClick={() => setRoute(option.route)}
          >
            <span>{option.label}</span>
            <small>{option.recordable ? "판단 기록 가능" : option.disabled_reason}</small>
          </button>
        ))}
      </div>
      <label className="db-reason-field">
        <span>{action.reason_label}</span>
        <textarea
          value={reason}
          rows={4}
          placeholder={selected?.reason_placeholder || "판단 사유를 작성합니다."}
          onChange={(event) => setReason(event.target.value)}
        />
        <small>{action.reason_help}</small>
      </label>
      {!selected?.recordable && <p className="db-disabled-reason" role="alert">{selected?.disabled_reason}</p>}
      <button
        type="button"
        className="db-submit"
        disabled={!canSubmit}
        onClick={() => {
          if (!selected || !canSubmit) return
          onIntent({
            action: "record_final_decision",
            intent_id: nextIntentId("decision"),
            decision_route: selected.route,
            operator_reason: reason.trim(),
          })
        }}
      >
        {selected?.button_label || "최종 판단 기록"}
      </button>
    </section>
  )
}

function disclosureLabel(value: unknown): string {
  if (typeof value === "string") return value
  if (value && typeof value === "object") {
    const row = value as Record<string, unknown>
    return String(row.title || row.root_issue_id || "근거 항목")
  }
  return "근거 항목"
}

function EvidenceDisclosure({ brief }: { brief: DecisionBrief }) {
  const limits = brief.disclosures.accepted_limits ?? []
  const gaps = brief.disclosures.source_gaps ?? []
  const provenance = brief.disclosures.provenance ?? []
  return (
    <section className="db-disclosure">
      <details>
        <summary>Evidence confidence · accepted limits · provenance</summary>
        <div className="db-disclosure-grid">
          <div>
            <h3>Evidence confidence</h3>
            <strong>{brief.evidence_confidence.value} / 100 · {brief.evidence_confidence.label}</strong>
            <p>{brief.evidence_confidence.basis}</p>
            <small>{brief.evidence_confidence.ready_checks} / {brief.evidence_confidence.total_checks} ready checks</small>
          </div>
          <div>
            <h3>Accepted limits</h3>
            {limits.length ? <ul>{limits.map((item, index) => <li key={index}>{disclosureLabel(item)}</li>)}</ul> : <p>인수한 한계 없음</p>}
          </div>
          <div>
            <h3>Source gaps</h3>
            {gaps.length ? <ul>{gaps.map((gap) => <li key={gap}>{gap}</li>)}</ul> : <p>표시할 source gap 없음</p>}
          </div>
          <div>
            <h3>Provenance</h3>
            {provenance.length ? <ul>{provenance.map((item) => <li key={item}>{item}</li>)}</ul> : <p>추가 root trace 없음</p>}
          </div>
        </div>
      </details>
    </section>
  )
}

export function DecisionBriefWorkspace({ decisionBrief, candidateSelector, onIntent }: WorkspaceProps) {
  const hasBrief = decisionBrief?.schema_version === "decision_brief_v1"
  const selectedCandidate = useMemo(
    () => candidateSelector.options.find((option) => option.selected),
    [candidateSelector.options],
  )

  if (!hasBrief) {
    return <div className="db-workspace db-empty">Decision Brief payload를 읽을 수 없습니다.</div>
  }

  return (
    <main className="db-workspace" data-candidate={selectedCandidate?.source_id || decisionBrief.candidate.source_id}>
      <WorkspaceHeader brief={decisionBrief} model={candidateSelector} onIntent={onIntent} />
      <VerdictHero brief={decisionBrief} />
      <BehaviorBoard brief={decisionBrief} />
      <StrengthWeaknessSection brief={decisionBrief} />
      <PortfolioTraitMap brief={decisionBrief} />
      <MonitoringConditions brief={decisionBrief} />
      <DecisionAction brief={decisionBrief} onIntent={onIntent} />
      <EvidenceDisclosure brief={decisionBrief} />
    </main>
  )
}
