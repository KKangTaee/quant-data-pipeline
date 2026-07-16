import React, { useEffect, useMemo, useState } from "react"
import {
  CandidateSelectorModel,
  DecisionBrief,
  DecisionBriefObservation,
  DecisionWorkspaceIntent,
  Level2HandoffItem,
  Level2MonitoringCondition,
  MonitoringCondition,
  Tone,
} from "./decisionBriefTypes"
import {
  CumulativeComparisonChart,
  UnderwaterChart,
} from "./DecisionBriefCharts"
import { DecisionBriefCharacter } from "./DecisionBriefCharacter"

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

function ObservationFreshness({
  brief,
  onIntent,
}: {
  brief: DecisionBrief
  onIntent: WorkspaceProps["onIntent"]
}) {
  const freshness = brief.observation_freshness
  const [pending, setPending] = useState(false)
  const limiter = freshness.limiting_symbols.length
    ? freshness.limiting_symbols.join(", ")
    : "없음"

  return (
    <section
      className={`db-freshness-strip db-tone-${freshness.tone}`}
      aria-label="관측 최신성"
    >
      <div className="db-freshness-state">
        <span>{freshness.label}</span>
        <strong>{freshness.summary}</strong>
        <p>{freshness.detail}</p>
      </div>
      <dl className="db-freshness-dates">
        <div><dt>현재 차트</dt><dd>{freshness.stored_curve_end || "미측정"}</dd></div>
        <div><dt>최신 완료 시장일</dt><dd>{freshness.latest_completed_market_date || "미측정"}</dd></div>
        <div><dt>DB 공통일</dt><dd>{freshness.db_common_price_date || "미측정"}</dd></div>
        <div><dt>제한 종목</dt><dd>{limiter}</dd></div>
      </dl>
      {freshness.last_result?.message && (
        <p className="db-freshness-result">{freshness.last_result.message}</p>
      )}
      {freshness.can_refresh && (
        <button
          type="button"
          className="db-freshness-action"
          disabled={pending}
          onClick={() => {
            if (pending) return
            setPending(true)
            onIntent({
              action: "refresh_observation",
              intent_id: nextIntentId("refresh"),
              source_id: freshness.selection_source_id,
              validation_id: freshness.validation_id,
            })
          }}
        >
          {pending ? "다시 계산하는 중..." : freshness.button_label || "최신 데이터로 다시 계산"}
        </button>
      )}
    </section>
  )
}

function BehaviorBoard({
  brief,
  onIntent,
}: {
  brief: DecisionBrief
  onIntent: WorkspaceProps["onIntent"]
}) {
  const board = brief.behavior_board
  return (
    <section className="db-section db-behavior" aria-labelledby="db-behavior-title">
      <SectionHeading
        eyebrow="Observed behavior"
        title="누적 성과, 손실 경로, 실행 현실성"
        detail="차트와 관측값은 저장된 curve와 structured evidence만 사용합니다."
      />
      <ObservationFreshness brief={brief} onIntent={onIntent} />
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

function PortfolioCharacterSection({ brief }: { brief: DecisionBrief }) {
  return (
    <section className="db-section db-character" aria-labelledby="db-character-title">
      <SectionHeading
        eyebrow="Portfolio character"
        title="포트폴리오 성격"
        detail="실제 관측값과 관리 기준 대비 상태를 분리해 읽습니다."
      />
      <DecisionBriefCharacter
        characterItems={brief.character_profile.items}
        pressureItems={brief.review_pressure.items}
      />
    </section>
  )
}

function HandoffItemCard({ item }: { item: Level2HandoffItem }) {
  return (
    <article className="db-handoff-card">
      <h4>{item.title}</h4>
      {item.observed && <p>{item.observed}</p>}
      {item.decision_guidance && <strong>{item.decision_guidance}</strong>}
      <small>Level2에서 확인한 근거 {item.evidence_refs.length}개</small>
    </article>
  )
}

function HandoffMonitoringCard({ item }: { item: Level2MonitoringCondition }) {
  return (
    <article className="db-handoff-card">
      <h4>{item.title}</h4>
      <p>{item.observation}</p>
      <dl>
        <div><dt>변화 조건</dt><dd>{item.threshold}</dd></div>
        <div><dt>확인 주기</dt><dd>{item.cadence}</dd></div>
        <div><dt>다시 할 판단</dt><dd>{item.re_review_action}</dd></div>
      </dl>
      <small>Level2 근거 {item.evidence_refs.length}개</small>
    </article>
  )
}

function Level2Handoff({ brief }: { brief: DecisionBrief }) {
  const handoff = brief.level2_handoff
  return (
    <section className="db-section db-handoff" aria-labelledby="db-handoff-title">
      <SectionHeading
        eyebrow="Level2 validated handoff"
        title="Level2에서 이어받은 판단"
        detail="Level2에서 해결할 일은 끝났습니다. 여기서는 확인된 근거를 최종 route 사유와 Monitoring 조건에 반영합니다."
      />
      {handoff.state === "blocked" ? (
        <div className="db-empty">Level2 차단 항목이 남아 있어 아직 Final Review 판단으로 승격되지 않았습니다.</div>
      ) : (
        <div className="db-handoff-grid">
          <div className="db-handoff-lane">
            <header><h3>최종 판단 입력</h3><span>{handoff.summary.final_decision_count}</span></header>
            <p>계좌·운용 목적처럼 이 화면에서 route 사유로 결정할 내용입니다.</p>
            {handoff.final_decisions.length ? handoff.final_decisions.map((item) => (
              <HandoffItemCard item={item} key={item.root_issue_id} />
            )) : <small className="db-handoff-empty">추가 판단 입력 없음</small>}
          </div>
          <div className="db-handoff-lane">
            <header><h3>인수한 검증 한계</h3><span>{handoff.summary.accepted_limit_count}</span></header>
            <p>Level2에서 근거를 확인했지만 결과 해석에 남겨야 하는 제한입니다.</p>
            {handoff.accepted_limits.length ? handoff.accepted_limits.map((item) => (
              <HandoffItemCard item={item} key={item.root_issue_id} />
            )) : <small className="db-handoff-empty">인수할 추가 한계 없음</small>}
          </div>
          <div className="db-handoff-lane">
            <header><h3>Monitoring 이관 조건</h3><span>{handoff.summary.monitoring_condition_count}</span></header>
            <p>관측값·조건·주기·재검토 행동이 모두 확인된 항목만 전달됩니다.</p>
            {handoff.monitoring_conditions.length ? handoff.monitoring_conditions.map((item) => (
              <HandoffMonitoringCard item={item} key={item.root_issue_id} />
            )) : <small className="db-handoff-empty">구조화된 이관 조건 없음</small>}
          </div>
        </div>
      )}
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

function EvidenceDisclosure({ brief }: { brief: DecisionBrief }) {
  const gaps = brief.disclosures.source_gaps ?? []
  const provenance = brief.disclosures.provenance ?? []
  return (
    <section className="db-disclosure">
      <details>
        <summary>Evidence confidence · source gaps · provenance</summary>
        <div className="db-disclosure-grid">
          <div>
            <h3>Evidence confidence</h3>
            <strong>{brief.evidence_confidence.value} / 100 · {brief.evidence_confidence.label}</strong>
            <p>{brief.evidence_confidence.basis}</p>
            <small>{brief.evidence_confidence.ready_checks} / {brief.evidence_confidence.total_checks} ready checks</small>
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
      <BehaviorBoard brief={decisionBrief} onIntent={onIntent} />
      <StrengthWeaknessSection brief={decisionBrief} />
      <PortfolioCharacterSection brief={decisionBrief} />
      <Level2Handoff brief={decisionBrief} />
      <MonitoringConditions brief={decisionBrief} />
      <DecisionAction brief={decisionBrief} onIntent={onIntent} />
      <EvidenceDisclosure brief={decisionBrief} />
    </main>
  )
}
