import React, { useEffect, useState } from "react"
import { Streamlit } from "streamlit-component-lib"

type Tone = "positive" | "warning" | "danger" | "neutral"

type ReportCard = {
  title?: string
  detail?: string
  action?: string
  severity?: string
  tone?: Tone
}

type Recommendation = {
  route?: string
  label?: string
  state?: string
  stateLabel?: string
  state_label?: string
  tone?: Tone
  monitoringCandidate?: boolean
  monitoring_candidate?: boolean
  monitoringHandoffState?: string
  monitoring_handoff_state?: string
}

type Score = {
  value?: number
  label?: string
  basis?: string
}

type Summary = {
  headline?: string
  verdict?: string
  nextAction?: string
  next_action?: string
  strongestEvidence?: string
  strongest_evidence?: string
  weakestConstraint?: string
  weakest_constraint?: string
}

type MonitoringConditions = {
  handoffReady?: boolean
  handoff_ready?: boolean
  trackingBenchmark?: string
  tracking_benchmark?: string
  reviewCadence?: string
  review_cadence?: string
  reviewTriggers?: string[]
  review_triggers?: string[]
  activeComponents?: number
  active_components?: number
  targetWeightTotal?: number
  target_weight_total?: number
}

type ReportSection = {
  title?: string
  detail?: string
  score?: number
  reviewCadence?: string
  review_cadence?: string
  openReviewItems?: number
  open_review_items?: number
  policyBlockers?: number
  policy_blockers?: number
}

type DecisionSummaryItem = {
  label?: string
  detail?: string
  tone?: Tone
  source?: string
}

type DecisionSummary = {
  headline?: string
  statusLabel?: string
  status_label?: string
  scoreLine?: string
  score_line?: string
  items?: DecisionSummaryItem[]
}

type ReportNarrative = {
  totalAssessment?: {
    label?: string
    headline?: string
    detail?: string
    tone?: Tone
  }
  total_assessment?: {
    label?: string
    headline?: string
    detail?: string
    tone?: Tone
  }
  decisionQuestions?: Array<{
    kind?: string
    label?: string
    question?: string
    required?: boolean
    effect?: string
    source?: string
  }>
  decision_questions?: Array<{
    kind?: string
    label?: string
    question?: string
    required?: boolean
    effect?: string
    source?: string
  }>
  boundaryNote?: string
  boundary_note?: string
}

type PatternGuideCard = {
  key?: string
  label?: string
  question?: string
  support?: string
  supportLabel?: string
  support_label?: string
  tone?: Tone
  conclusion?: string
  applicable?: boolean
  applicabilityReason?: string
  applicability_reason?: string
  currentDiagnosis?: string
  current_diagnosis?: string
  meaning?: string
  changeCondition?: string
  change_condition?: string
  nextAction?: string
  next_action?: string
  observed?: string[]
  evidenceTrace?: Array<{
    label?: string
    value?: string
    threshold?: string
    sourceLabel?: string
    source_label?: string
    technicalPath?: string
    technical_path?: string
    asOf?: string
    as_of?: string
  }>
  evidence_trace?: Array<{
    label?: string
    value?: string
    threshold?: string
    sourceLabel?: string
    source_label?: string
    technicalPath?: string
    technical_path?: string
    asOf?: string
    as_of?: string
  }>
  evidenceSources?: string[]
  evidence_sources?: string[]
  evidenceAsOf?: string
  evidence_as_of?: string
  missingSignals?: string[]
  missing_signals?: string[]
  monitoringTrigger?: string
  monitoring_trigger?: string
  experimentCandidate?: string
  experiment_candidate?: string
  directScenarioClaim?: boolean
  direct_scenario_claim?: boolean
  visibleFirstRead?: boolean
  visible_first_read?: boolean
}

type PatternGuide = {
  summary?: {
    headline?: string
    supportCounts?: Record<string, number>
    support_counts?: Record<string, number>
    boundaryNote?: string
    boundary_note?: string
    visibleCount?: number
    visible_count?: number
    additionalCount?: number
    additional_count?: number
  }
  cards?: PatternGuideCard[]
  visibleCards?: PatternGuideCard[]
  visible_cards?: PatternGuideCard[]
  additionalCards?: PatternGuideCard[]
  additional_cards?: PatternGuideCard[]
}

type InterpretationCard = {
  kind?: string
  title?: string
  detail?: string
  tone?: Tone
  badges?: string[]
}

type ReviewDispositionItem = {
  title?: string
  status?: string
  role?: string
  roleLabel?: string
  role_label?: string
  stageSurface?: string
  stage_surface?: string
  disposition?: string
  dispositionLabel?: string
  disposition_label?: string
  detail?: string
  action?: string
  observedValue?: string
  observed_value?: string
  threshold?: string
  evidenceSource?: string
  evidence_source?: string
  evidenceAsOf?: string
  evidence_as_of?: string
  traceStatus?: string
  trace_status?: string
  whyVisible?: string
  why_visible?: string
  userInstruction?: string
  user_instruction?: string
  ownership?: string
  finalReviewActionRequired?: boolean
  final_review_action_required?: boolean
  tone?: Tone
}

type Level2ReviewDisposition = {
  summary?: {
    total?: number
    blocker?: number
    warning?: number
    openReview?: number
    open_review?: number
    monitoringFollowup?: number
    monitoring_followup?: number
  }
  groups?: {
    blocker?: ReviewDispositionItem[]
    warning?: ReviewDispositionItem[]
    openReview?: ReviewDispositionItem[]
    open_review?: ReviewDispositionItem[]
    monitoringFollowup?: ReviewDispositionItem[]
    monitoring_followup?: ReviewDispositionItem[]
  }
  roleSections?: ReviewRoleSection[]
  role_sections?: ReviewRoleSection[]
  finalReviewSections?: ReviewRoleSection[]
  final_review_sections?: ReviewRoleSection[]
}

type ReviewRoleSection = {
  role?: string
  label?: string
  tone?: Tone
  count?: number
  actionOutcome?: string
  action_outcome?: string
  actionLabel?: string
  action_label?: string
  actionDetail?: string
  action_detail?: string
  items?: ReviewDispositionItem[]
}

type ScorecardCategory = {
  category?: string
  score?: number
  evidence?: string
  effect?: string
  tone?: Tone
}

type ScorecardDimension = {
  key?: string
  label?: string
  score?: number
  weight?: number
  evidence?: string
  interpretation?: string
  tone?: Tone
}

type ScorecardDriver = {
  label?: string
  detail?: string
  score?: number
  tone?: Tone
}

type ScorecardLimit = {
  code?: string
  label?: string
  detail?: string
  cap?: number
  reason?: string
  tone?: Tone
}

type RouteConstraint = {
  code?: string
  label?: string
  tone?: Tone
}

type ReviewImpact = {
  title?: string
  role?: string
  roleLabel?: string
  role_label?: string
  disposition?: string
  targetDimension?: string
  target_dimension?: string
  scoreEffect?: number
  score_effect?: number
  scorePolicy?: string
  score_policy?: string
  detail?: string
  action?: string
  rationale?: string
  observedValue?: string
  observed_value?: string
  threshold?: string
  evidenceSource?: string
  evidence_source?: string
  evidenceAsOf?: string
  evidence_as_of?: string
  traceStatus?: string
  trace_status?: string
  traceLabel?: string
  trace_label?: string
  traceItems?: Array<{
    label?: string
    status?: string
    observedValue?: string
    observed_value?: string
    judgmentBasis?: string
    judgment_basis?: string
    evidenceSource?: string
    evidence_source?: string
    evidenceAsOf?: string
    evidence_as_of?: string
  }>
  trace_items?: Array<{
    label?: string
    status?: string
    observedValue?: string
    observed_value?: string
    judgmentBasis?: string
    judgment_basis?: string
    evidenceSource?: string
    evidence_source?: string
    evidenceAsOf?: string
    evidence_as_of?: string
  }>
  tone?: Tone
}

type Scorecard = {
  overallScore?: number
  overall_score?: number
  preCapScore?: number
  pre_cap_score?: number
  scoreBand?: string
  score_band?: string
  classification?: string
  classificationLabel?: string
  classification_label?: string
  decisionLabel?: string
  decision_label?: string
  monitoringCandidate?: boolean
  monitoring_candidate?: boolean
  basis?: string
  categories?: ScorecardCategory[]
  dimensions?: ScorecardDimension[]
  headlineScores?: ScorecardDimension[]
  headline_scores?: ScorecardDimension[]
  scoreDrivers?: {
    positive?: ScorecardDriver[]
    negative?: ScorecardDriver[]
  }
  score_drivers?: {
    positive?: ScorecardDriver[]
    negative?: ScorecardDriver[]
  }
  scoreLimits?: ScorecardLimit[]
  score_limits?: ScorecardLimit[]
  routeConstraints?: RouteConstraint[]
  route_constraints?: RouteConstraint[]
  reviewImpacts?: ReviewImpact[]
  review_impacts?: ReviewImpact[]
}

type SaveHandoffSummary = {
  recordType?: string
  record_type?: string
  judgmentRecord?: {
    ready?: boolean
    label?: string
    detail?: string
  }
  judgment_record?: {
    ready?: boolean
    label?: string
    detail?: string
  }
  monitoringHandoff?: {
    candidate?: boolean
    state?: string
    label?: string
    detail?: string
  }
  monitoring_handoff?: {
    candidate?: boolean
    state?: string
    label?: string
    detail?: string
  }
}

type WeaknessImprovement = {
  proposals?: Array<{
    weakness?: string
    currentGap?: string
    current_gap?: string
    proposedChange?: string
    proposed_change?: string
    expectedEffect?: string
    expected_effect?: string
    verificationStep?: string
    verification_step?: string
    scope?: string
  }>
  comparison?: {
    currentScore?: number
    current_score?: number
    expectedScoreLow?: number
    expected_score_low?: number
    expectedScoreHigh?: number
    expected_score_high?: number
    verificationStatus?: string
    verification_status?: string
  }
}

type SelectionRationalePoint = {
  label?: string
  detail?: string
  tone?: Tone
}

type SelectionRationale = {
  headline?: string
  decisionRoute?: string
  decision_route?: string
  decisionLabel?: string
  decision_label?: string
  classificationLabel?: string
  classification_label?: string
  scoreSummary?: string
  score_summary?: string
  decisionReason?: string
  decision_reason?: string
  keyPoints?: SelectionRationalePoint[]
  key_points?: SelectionRationalePoint[]
  monitoringHandoffReason?: string
  monitoring_handoff_reason?: string
}

type RequiredDecisionNote = {
  kind?: string
  label?: string
  prompt?: string
  required?: boolean
  source?: string
}

export type InvestmentReport = {
  schemaVersion?: string
  schema_version?: string
  source?: {
    title?: string
    type?: string
    sourceId?: string
    source_id?: string
    validationId?: string
    validation_id?: string
  }
  recommendation?: Recommendation
  score?: Score
  scorecard?: Scorecard
  decisionSummary?: DecisionSummary
  decision_summary?: DecisionSummary
  reportNarrative?: ReportNarrative
  report_narrative?: ReportNarrative
  patternGuide?: PatternGuide
  pattern_guide?: PatternGuide
  selectionRationale?: SelectionRationale
  selection_rationale?: SelectionRationale
  requiredFinalDecisionNotes?: RequiredDecisionNote[]
  required_final_decision_notes?: RequiredDecisionNote[]
  saveHandoffSummary?: SaveHandoffSummary
  save_handoff_summary?: SaveHandoffSummary
  weaknessImprovement?: WeaknessImprovement
  weakness_improvement?: WeaknessImprovement
  summary?: Summary
  strengths?: ReportCard[]
  weaknesses?: ReportCard[]
  watchItems?: ReportCard[]
  watch_items?: ReportCard[]
  interpretationCards?: InterpretationCard[]
  interpretation_cards?: InterpretationCard[]
  performanceInterpretation?: ReportSection
  performance_interpretation?: ReportSection
  scenarioFit?: ReportSection
  scenario_fit?: ReportSection
  expectedRangeAndRisk?: ReportSection
  expected_range_and_risk?: ReportSection
  benchmarkRationale?: ReportSection
  benchmark_rationale?: ReportSection
  level2ReviewDisposition?: Level2ReviewDisposition
  level2_review_disposition?: Level2ReviewDisposition
  monitoringConditions?: MonitoringConditions
  monitoring_conditions?: MonitoringConditions
  boundaries?: Record<string, boolean>
}

type FinalReviewInvestmentReportProps = {
  report: InvestmentReport
}

const compact = (value: unknown, fallback = "-"): string => {
  const text = String(value ?? "").trim()
  return text || fallback
}

const toneClass = (tone: unknown): Tone => {
  const value = String(tone ?? "")
  return ["positive", "warning", "danger", "neutral"].includes(value) ? (value as Tone) : "neutral"
}

const formattedScore = (score: unknown): string => {
  const value = Number(score)
  if (!Number.isFinite(value)) return "-"
  return value.toFixed(1)
}

const field = <T,>(camel: T | undefined, snake: T | undefined): T | undefined => (camel !== undefined ? camel : snake)

const badgeText = (value: unknown): string => {
  const text = compact(value, "")
  const labels: Record<string, string> = {
    HIGH_SCORE: "강점",
    PASS: "통과",
    WATCH: "확인 필요",
    SCORE_CAP: "점수 제한",
    BLOCKER: "차단",
    WARNING: "주의",
  }
  return labels[text] ?? text.replaceAll("_", " ").toLowerCase()
}

type MetaItem = {
  label: string
  value: string
  tone?: Tone
}

function MetaStrip({ items }: { items: MetaItem[] }) {
  return (
    <dl className="fr-invest-report__meta-strip" aria-label="후보 메타 정보">
      {items.map((item) => (
        <div className={`fr-invest-report__meta-item fr-invest-report__meta-item--${toneClass(item.tone)}`} key={`${item.label}-${item.value}`}>
          <dt>{item.label}</dt>
          <dd>{item.value}</dd>
        </div>
      ))}
    </dl>
  )
}

function AssessmentPanel({ narrative }: { narrative: ReportNarrative }) {
  const assessment = narrative.totalAssessment ?? narrative.total_assessment ?? {}
  return (
    <section className={`fr-invest-report__assessment fr-invest-report__assessment--${toneClass(assessment.tone)}`} aria-label="총평">
      <span>{compact(assessment.label, "총평")}</span>
      <h5>{compact(assessment.headline)}</h5>
      <p>{compact(assessment.detail)}</p>
      <small>{compact(field(narrative.boundaryNote, narrative.boundary_note))}</small>
    </section>
  )
}

function DecisionQuestionList({ narrative }: { narrative: ReportNarrative }) {
  const questions = field(narrative.decisionQuestions, narrative.decision_questions) ?? []
  return (
    <section className="fr-invest-report__questions" aria-label="저장 전 확인 질문">
      <div className="fr-invest-report__section-head">
        <div>
          <span>최종 판단 체크</span>
          <h5>저장 전 확인 질문</h5>
        </div>
        <strong>{questions.filter((item) => item.required).length}개 필수 확인</strong>
      </div>
      <div className="fr-invest-report__question-list">
        {questions.map((item, index) => (
          <article key={`${item.kind ?? "question"}-${index}`}>
            <div>
              <span>{compact(item.effect)}</span>
              <em>{item.required ? "필수" : "참고"}</em>
            </div>
            <h6>{compact(item.label)}</h6>
            <p>{compact(item.question)}</p>
            <small>{compact(item.source)}</small>
          </article>
        ))}
      </div>
    </section>
  )
}

function PatternGuidePanel({ guide }: { guide: PatternGuide }) {
  const summary = guide.summary ?? {}
  const counts = field(summary.supportCounts, summary.support_counts) ?? {}
  const cards = field(guide.visibleCards, guide.visible_cards) ?? guide.cards ?? []
  const additionalCards = field(guide.additionalCards, guide.additional_cards) ?? []
  return (
    <section className="fr-invest-report__patterns" aria-label="Monitoring 방향 가이드">
      <div className="fr-invest-report__section-head">
        <div>
          <span>저장 evidence 기반 조건부 가이드</span>
          <h5>Monitoring 방향 가이드</h5>
        </div>
        <strong>판단 가능 {counts.actionable ?? 0} · 조건부 추적 {counts.conditional ?? 0} · 추가 검증 {counts.needs_validation ?? 0} · 적용 제외 {counts.not_applicable ?? 0}</strong>
      </div>
      <p className="fr-invest-report__pattern-boundary">{compact(field(summary.boundaryNote, summary.boundary_note))}</p>
      <div className="fr-invest-report__pattern-list">
        {cards.map((card, index) => {
          const traces = field(card.evidenceTrace, card.evidence_trace) ?? []
          return (
            <article className={`fr-invest-report__pattern fr-invest-report__pattern--${toneClass(card.tone)}`} key={card.key ?? index}>
              <div className="fr-invest-report__pattern-head">
                <span>{String(index + 1).padStart(2, "0")}</span>
                <h6>{compact(card.label)}</h6>
                <em>{compact(field(card.supportLabel, card.support_label))}</em>
              </div>
              <dl className="fr-invest-report__pattern-guide">
                <div><dt>현재 진단</dt><dd>{compact(field(card.currentDiagnosis, card.current_diagnosis), compact(card.conclusion))}</dd></div>
                <div><dt>의미</dt><dd>{compact(card.meaning)}</dd></div>
                <div><dt>변화 조건</dt><dd>{compact(field(card.changeCondition, card.change_condition), compact(field(card.monitoringTrigger, card.monitoring_trigger)))}</dd></div>
                <div className="fr-invest-report__pattern-action"><dt>다음 행동</dt><dd>{compact(field(card.nextAction, card.next_action))}</dd></div>
              </dl>
              <details className="fr-invest-report__pattern-details">
                <summary>근거 및 기술 정보 보기</summary>
                {traces.length > 0 ? (
                  <div className="fr-invest-report__pattern-traces">
                    {traces.map((trace, traceIndex) => (
                      <article key={`${card.key ?? index}-trace-${traceIndex}`}>
                        <strong>{compact(trace.label)} · {compact(trace.value)}</strong>
                        <span>판단 기준 {compact(trace.threshold)}</span>
                        <span>{compact(field(trace.sourceLabel, trace.source_label))} · 기준일 {compact(field(trace.asOf, trace.as_of))}</span>
                        <code>{compact(field(trace.technicalPath, trace.technical_path))}</code>
                      </article>
                    ))}
                  </div>
                ) : <p>현재 표시할 직접 관측 trace가 없습니다.</p>}
              </details>
            </article>
          )
        })}
      </div>
      {additionalCards.length > 0 ? (
        <details className="fr-invest-report__pattern-more">
          <summary>나머지 {additionalCards.length}개 패턴 상태 보기</summary>
          <div>
            {additionalCards.map((card) => (
              <span key={card.key ?? card.label}>{compact(card.label)} · {compact(field(card.supportLabel, card.support_label))}</span>
            ))}
          </div>
        </details>
      ) : null}
    </section>
  )
}

function EvidenceRows({ title, items, emptyLabel, limit }: { title: string; items: ReportCard[]; emptyLabel: string; limit: number }) {
  const visibleItems = items.slice(0, limit)
  const hiddenCount = Math.max(0, items.length - visibleItems.length)
  return (
    <section className="fr-invest-report__evidence-lane">
      <div className="fr-invest-report__lane-title">{title}</div>
      <div className="fr-invest-report__evidence-rows">
        {visibleItems.length > 0 ? (
          visibleItems.map((item, index) => (
            <article className={`fr-invest-report__evidence-row fr-invest-report__evidence-row--${toneClass(item.tone)}`} key={`${item.title ?? title}-${index}`}>
              <div>
                <h5>{compact(item.title)}</h5>
                <span>{badgeText(item.severity)}</span>
              </div>
              <p>{compact(item.detail)}</p>
              {item.action ? <small>{compact(item.action)}</small> : null}
            </article>
          ))
        ) : (
          <article className="fr-invest-report__evidence-row fr-invest-report__evidence-row--neutral">
            <div>
              <h5>{emptyLabel}</h5>
              <span>-</span>
            </div>
            <p>현재 report payload에 표시할 항목이 없습니다.</p>
          </article>
        )}
      </div>
      {hiddenCount > 0 ? <p className="fr-invest-report__more-note">추가 {hiddenCount}개 항목은 아래 근거 상세에서 확인합니다.</p> : null}
    </section>
  )
}

function InterpretationRows({ cards }: { cards: InterpretationCard[] }) {
  if (cards.length === 0) return null
  return (
    <section className="fr-invest-report__interpretation" aria-label="해석">
      <div className="fr-invest-report__section-head">
        <div>
          <span>총평 해석</span>
          <h5>이 후보를 읽는 네 가지 기준</h5>
        </div>
      </div>
      <div className="fr-invest-report__interpretation-rows">
        {cards.map((card, index) => (
          <article className={`fr-invest-report__interpretation-row fr-invest-report__interpretation-row--${toneClass(card.tone)}`} key={`${card.kind ?? card.title ?? "interpretation"}-${index}`}>
            <span className="fr-invest-report__interpretation-index">{String(index + 1).padStart(2, "0")}</span>
            <div>
              <h5>{compact(card.title)}</h5>
              <p>{compact(card.detail)}</p>
            </div>
            {card.badges && card.badges.length > 0 ? (
              <div className="fr-invest-report__inline-badges">
                {card.badges.map((badge, badgeIndex) => (
                  <span key={`${badge}-${badgeIndex}`}>{compact(badge)}</span>
                ))}
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  )
}

type DetailTab = {
  id: string
  label: string
  title: string
  question: string
  children: React.ReactNode
}

function DetailTabs({ tabs }: { tabs: DetailTab[] }) {
  const [activeId, setActiveId] = useState(tabs[0]?.id ?? "")
  const activeTab = tabs.find((tab) => tab.id === activeId) ?? tabs[0]

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [activeId])

  if (!activeTab) return null

  return (
    <section className="fr-invest-report__detail-tabs" aria-label="근거 상세 탭">
      <div className="fr-invest-report__detail-tablist" role="tablist" aria-label="투자 검토서 상세 근거">
        {tabs.map((tab) => {
          const isActive = tab.id === activeTab.id
          return (
            <button
              aria-controls={`fr-invest-report-panel-${tab.id}`}
              aria-selected={isActive}
              className={`fr-invest-report__detail-tab${isActive ? " fr-invest-report__detail-tab--active" : ""}`}
              id={`fr-invest-report-tab-${tab.id}`}
              key={tab.id}
              onClick={() => setActiveId(tab.id)}
              role="tab"
              type="button"
            >
              <span>{tab.label}</span>
              <strong>{tab.title}</strong>
              <small>{tab.question}</small>
            </button>
          )
        })}
      </div>
      <div
        aria-labelledby={`fr-invest-report-tab-${activeTab.id}`}
        className="fr-invest-report__detail-panel"
        id={`fr-invest-report-panel-${activeTab.id}`}
        role="tabpanel"
      >
        {activeTab.children}
      </div>
    </section>
  )
}

function ReviewActionBoard({ sections }: { sections: ReviewRoleSection[] }) {
  const total = sections.reduce((sum, section) => sum + Number(section.count ?? section.items?.length ?? 0), 0)
  const directActionCount = sections
    .flatMap((section) => section.items ?? [])
    .filter((item) => field(item.finalReviewActionRequired, item.final_review_action_required)).length
  return (
    <section className="fr-invest-report__review-actions" aria-label="Final Review 판단 항목">
      <div className="fr-invest-report__section-head">
        <div>
          <span>2단계 검증에서 넘어온 판단 재료</span>
          <h5>Final Review에서 결정할 것</h5>
        </div>
        <strong>{total > 0 ? `직접 결정 ${directActionCount}개 · 인수 제한 ${total - directActionCount}개` : "추가 판단 없음"}</strong>
      </div>
      <p className="fr-invest-report__review-boundary">
        검증을 다시 실행하는 화면이 아닙니다. 지금 결정할 조건, Monitoring 조건, 이미 2단계에서 점수에 반영한 제한을 구분합니다.
      </p>
      <div className="fr-invest-report__review-action-list">
        {sections.map((section) => {
          const items = section.items ?? []
          const actionLabel = field(section.actionLabel, section.action_label)
          const actionDetail = field(section.actionDetail, section.action_detail)
          return (
            <article className={`fr-invest-report__review-action fr-invest-report__review-action--${toneClass(section.tone)}`} key={section.role ?? section.label}>
              <div>
                <span>{compact(section.label)}</span>
                <strong>{section.count ?? items.length}</strong>
              </div>
              <em>{compact(actionLabel)}</em>
              <p>{compact(actionDetail)}</p>
              {items.length > 0 ? (
                <ul>
                  {items.map((item, index) => (
                    <li key={`${section.role ?? "review"}-${item.title ?? index}`}>
                      <strong>{compact(item.title)}</strong>
                      <span><b>왜 보이나</b>{compact(field(item.whyVisible, item.why_visible), compact(item.detail))}</span>
                      <small><b>사용자 판단</b>{compact(field(item.userInstruction, item.user_instruction), compact(item.action))}</small>
                    </li>
                  ))}
                </ul>
              ) : (
                <small>현재 해당 항목이 없습니다.</small>
              )}
            </article>
          )
        })}
      </div>
    </section>
  )
}

function ScorecardDimensionList({ dimensions }: { dimensions: ScorecardDimension[] }) {
  return (
    <div className="fr-invest-report__scorecard-dimensions" aria-label="세부 점수">
      {dimensions.map((dimension, index) => (
        <article className={`fr-invest-report__scorecard-dimension fr-invest-report__scorecard-dimension--${toneClass(dimension.tone)}`} key={`${dimension.key ?? "dimension"}-${index}`}>
          <div>
            <h5>{compact(dimension.label)}</h5>
            <strong>{formattedScore(dimension.score)}</strong>
          </div>
          <div className="fr-invest-report__scorebar" aria-hidden="true">
            <span style={{ width: `${Math.max(0, Math.min(100, Number(dimension.score) || 0))}%` }} />
          </div>
          <div className="fr-invest-report__scorecard-dimension-copy">
            <p>{compact(dimension.interpretation)}</p>
            <small>비중 {Math.round((Number(dimension.weight) || 0) * 100)}% · {compact(dimension.evidence)}</small>
          </div>
        </article>
      ))}
    </div>
  )
}

function ScoreDriverList({ title, drivers }: { title: string; drivers: ScorecardDriver[] }) {
  return (
    <article className="fr-invest-report__score-driver-group">
      <h5>{title}</h5>
      {drivers.map((driver, index) => (
        <section className={`fr-invest-report__score-driver fr-invest-report__score-driver--${toneClass(driver.tone)}`} key={`${title}-${driver.label ?? index}`}>
          <strong>{compact(driver.label)}</strong>
          <span>{formattedScore(driver.score)}</span>
          <p>{compact(driver.detail)}</p>
        </section>
      ))}
    </article>
  )
}

function ScoreLimitList({ limits, constraints }: { limits: ScorecardLimit[]; constraints: RouteConstraint[] }) {
  return (
    <article className="fr-invest-report__score-limits">
      <h5>점수 / route 정책</h5>
      {limits.length > 0 ? (
        limits.map((limit, index) => (
          <section className={`fr-invest-report__score-limit fr-invest-report__score-limit--${toneClass(limit.tone)}`} key={`${limit.label ?? "limit"}-${index}`}>
            <strong>{compact(limit.label)}</strong>
            <span>cap {formattedScore(limit.cap)}</span>
            <p>{compact(limit.detail ?? limit.reason)}</p>
          </section>
        ))
      ) : (
        <section className="fr-invest-report__score-limit fr-invest-report__score-limit--positive">
          <strong>REVIEW 개수 자동 감점 없음</strong>
          <span>Attractiveness</span>
          <p>근거 부족은 근거 신뢰도로, blocker는 선택 route 제약으로 분리합니다.</p>
        </section>
      )}
      {constraints.map((constraint) => (
        <section className={`fr-invest-report__score-limit fr-invest-report__score-limit--${toneClass(constraint.tone)}`} key={constraint.code ?? constraint.label}>
          <strong>{compact(constraint.label)}</strong>
          <span>Route</span>
          <p>투자 매력도 점수는 유지하고 선택 / 저장 가능 여부에만 적용합니다.</p>
        </section>
      ))}
    </article>
  )
}

function ReviewImpactList({ impacts }: { impacts: ReviewImpact[] }) {
  return (
    <article className="fr-invest-report__review-impacts">
      <h5>REVIEW 근거와 반영 정책</h5>
      {impacts.length > 0 ? (
        impacts.map((impact, index) => {
          const scoreEffect = field(impact.scoreEffect, impact.score_effect)
          const scorePolicy = field(impact.scorePolicy, impact.score_policy)
          const evidenceSource = field(impact.evidenceSource, impact.evidence_source)
          const evidenceAsOf = field(impact.evidenceAsOf, impact.evidence_as_of)
          const traceStatus = field(impact.traceStatus, impact.trace_status)
          const traceLabel = field(impact.traceLabel, impact.trace_label)
          const traceItems = field(impact.traceItems, impact.trace_items) ?? []
          return (
            <section className={`fr-invest-report__review-impact fr-invest-report__review-impact--${toneClass(impact.tone)}`} key={`${impact.role ?? "review"}-${impact.title ?? index}`}>
              <div>
                <strong>{compact(impact.title)}</strong>
                <span>{compact(traceLabel, Number(scoreEffect) === 0 ? "정성 판단" : "근거 확인")}</span>
              </div>
              <small>{compact(field(impact.roleLabel, impact.role_label))} · {Number(scoreEffect) === 0 ? "감점 없음" : `${formattedScore(scoreEffect)} 반영`}</small>
              <p>{compact(impact.rationale ?? impact.detail)}</p>
              {traceItems.length > 0 ? (
                <div className="fr-invest-report__review-trace-list">
                  {traceItems.map((trace, traceIndex) => {
                    const traceObserved = field(trace.observedValue, trace.observed_value)
                    const traceBasis = field(trace.judgmentBasis, trace.judgment_basis)
                    const traceSource = field(trace.evidenceSource, trace.evidence_source)
                    const traceAsOf = field(trace.evidenceAsOf, trace.evidence_as_of)
                    return (
                      <section key={`${trace.label ?? "trace"}-${traceIndex}`}>
                        <div><strong>{compact(trace.label, "세부 근거")}</strong><em>{compact(trace.status)}</em></div>
                        <p><b>관측</b>{compact(traceObserved, "수치 관측 없음")}</p>
                        <p><b>판단 근거</b>{compact(traceBasis, "정성 판단")}</p>
                        <details>
                          <summary>출처와 기준일</summary>
                          <small>{compact(traceSource, compact(evidenceSource, "저장 evidence"))} · {compact(traceAsOf, compact(evidenceAsOf, "기준일 미기록"))}</small>
                        </details>
                      </section>
                    )
                  })}
                </div>
              ) : (
                <div className={`fr-invest-report__review-trace-state fr-invest-report__review-trace-state--${traceStatus}`}>
                  {traceStatus === "qualitative"
                    ? "수치로 자동 판정하지 않는 항목입니다. 아래 사용자 판단을 선택 또는 보류 사유에 기록합니다."
                    : "요약 REVIEW와 세부 audit 근거의 연결이 아직 없습니다. 이 항목만으로 수치를 추정하지 않습니다."}
                </div>
              )}
              <small>{compact(scorePolicy)} · {compact(field(impact.targetDimension, impact.target_dimension))}</small>
              {impact.action ? <em>{compact(impact.action)}</em> : null}
            </section>
          )
        })
      ) : (
        <section className="fr-invest-report__review-impact fr-invest-report__review-impact--positive">
          <div>
            <strong>점수 영향 항목 없음</strong>
            <span>-</span>
          </div>
          <small>Level2 REVIEW</small>
          <p>Final Review 점수에 반영할 Level2 REVIEW 부담이 없습니다.</p>
        </section>
      )}
    </article>
  )
}

export function FinalReviewInvestmentReport({ report }: FinalReviewInvestmentReportProps) {
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [report])

  const recommendation = report.recommendation ?? {}
  const score = report.score ?? {}
  const scorecard = report.scorecard ?? {}
  const summary = report.summary ?? {}
  const decisionSummary = report.decisionSummary ?? report.decision_summary ?? {}
  const reportNarrative = report.reportNarrative ?? report.report_narrative ?? {}
  const patternGuide = report.patternGuide ?? report.pattern_guide ?? {}
  const source = report.source ?? {}
  const tone = toneClass(recommendation.tone)
  const interpretationCards = field(report.interpretationCards, report.interpretation_cards) ?? []
  const watchItems = field(report.watchItems, report.watch_items) ?? report.weaknesses ?? []
  const level2Review = report.level2ReviewDisposition ?? report.level2_review_disposition ?? {}
  const level2RoleSections = field(level2Review.roleSections, level2Review.role_sections) ?? []
  const finalReviewSections = field(level2Review.finalReviewSections, level2Review.final_review_sections)
    ?? level2RoleSections.filter((section) => Number(section.count ?? section.items?.length ?? 0) > 0)
  const directDecisionCount = finalReviewSections
    .flatMap((section) => section.items ?? [])
    .filter((item) => field(item.finalReviewActionRequired, item.final_review_action_required)).length
  const scorecardOverall = field(scorecard.overallScore, scorecard.overall_score)
  const scorecardBand = field(scorecard.scoreBand, scorecard.score_band)
  const scorecardClassification = field(scorecard.classificationLabel, scorecard.classification_label)
  const scorecardDecision = field(scorecard.decisionLabel, scorecard.decision_label)
  const scorecardDrivers = field(scorecard.scoreDrivers, scorecard.score_drivers) ?? {}
  const scorecardLimits = field(scorecard.scoreLimits, scorecard.score_limits) ?? []
  const routeConstraints = field(scorecard.routeConstraints, scorecard.route_constraints) ?? []
  const scorecardReviewImpacts = field(scorecard.reviewImpacts, scorecard.review_impacts) ?? []
  const headlineScores = field(scorecard.headlineScores, scorecard.headline_scores) ?? []
  const patternCards = patternGuide.cards ?? []
  const metaItems: MetaItem[] = [
    { label: "후보", value: compact(source.title) },
    { label: "직접 결정", value: `${directDecisionCount}개`, tone: directDecisionCount > 0 ? "warning" : "positive" },
  ]
  const detailTabs: DetailTab[] = [
    {
      id: "score-evidence",
      label: "점수",
      title: "점수 근거",
      question: "왜 이 점수인가?",
      children: (
        <section className="fr-invest-report__scorecard-detail">
          <div className="fr-invest-report__scorecard-head">
            <div>
              <span>투자 매력도 산정 근거</span>
              <h5>{compact(scorecardClassification, compact(recommendation.label))}</h5>
              <p>{compact(scorecard.basis)}</p>
            </div>
            <aside>
              <strong>{formattedScore(scorecardOverall)}</strong>
              <span>/ 100</span>
              <small>{compact(scorecardBand)}</small>
            </aside>
          </div>
          <div className="fr-invest-report__scorecard-meta">
            <span>{compact(scorecardDecision)}</span>
            <span>REVIEW 개수 자동 감점 없음</span>
          </div>
          <div className="fr-invest-report__scorecard-subtitle">세부 점수</div>
          <ScorecardDimensionList dimensions={scorecard.dimensions ?? []} />
          <div className="fr-invest-report__scorecard-subtitle">점수 영향</div>
          <div className="fr-invest-report__score-drivers">
            <ScoreDriverList title="점수를 지지한 근거" drivers={scorecardDrivers.positive ?? []} />
            <ScoreDriverList title="해석상 확인할 축" drivers={scorecardDrivers.negative ?? []} />
            <ScoreLimitList limits={scorecardLimits} constraints={routeConstraints} />
          </div>
        </section>
      ),
    },
    {
      id: "review-evidence",
      label: "REVIEW",
      title: "남은 판단 근거",
      question: "무엇을 수용하거나 확인해야 하나?",
      children: (
        <section className="fr-invest-report__review-evidence-detail">
          <p>2단계 요약을 저장된 세부 audit와 연결해 관측, 판단 근거, 점수 반영 방식과 사용자의 결정을 함께 보여줍니다.</p>
          <ReviewImpactList impacts={scorecardReviewImpacts} />
        </section>
      ),
    },
    {
      id: "pattern-experiments",
      label: "다음 실험",
      title: "다음 실험 아이디어",
      question: "다음 백테스트에서 무엇을 바꿔볼까?",
      children: (
        <section className="fr-invest-report__experiment-detail">
          <p>아래 항목은 점수 개선 예측이 아니라 별도 counterfactual backtest가 필요한 실험 후보입니다.</p>
          <div className="fr-invest-report__experiment-list">
            {patternCards.map((card, index) => (
              <article key={`${card.key ?? "experiment"}-${index}`}>
                <div><span>{compact(field(card.supportLabel, card.support_label))}</span><em>{String(index + 1).padStart(2, "0")}</em></div>
                <h5>{compact(card.label)}</h5>
                <p>{compact(field(card.experimentCandidate, card.experiment_candidate))}</p>
                <small>{compact(card.question)}</small>
              </article>
            ))}
          </div>
        </section>
      ),
    },
  ]

  return (
    <section className={`fr-invest-report fr-invest-report--${tone}`}>
      <header className="fr-invest-report__header">
        <div>
          <div className="fr-invest-report__title-row">
            <div className="fr-invest-report__kicker">Final Review 투자 검토서</div>
            <span className={`fr-invest-report__status fr-invest-report__status--${tone}`}>
              {compact(recommendation.stateLabel ?? recommendation.state_label)}
            </span>
          </div>
          <h3>{compact(decisionSummary.headline, compact(summary.headline, "최종 검토 요약"))}</h3>
          <p>{compact(summary.verdict)}</p>
        </div>
        <aside className="fr-invest-report__score" aria-label="최종 판단 점수">
          <span>투자 매력도</span>
          <strong>{formattedScore(score.value)}</strong>
          <small>{compact(score.label)}</small>
        </aside>
      </header>

      <MetaStrip items={metaItems} />

      <section className="fr-invest-report__headline-scores" aria-label="핵심 점수 구분">
        {headlineScores.map((item) => (
          <article className={`fr-invest-report__headline-score fr-invest-report__headline-score--${toneClass(item.tone)}`} key={item.key ?? item.label}>
            <span>{compact(item.label)}</span>
            <strong>{formattedScore(item.score)}</strong>
            <p>{compact(item.interpretation)}</p>
          </article>
        ))}
      </section>

      <AssessmentPanel narrative={reportNarrative} />

      <InterpretationRows cards={interpretationCards} />

      <div className="fr-invest-report__evidence">
        <EvidenceRows title="강점" items={report.strengths ?? []} emptyLabel="강점 근거 없음" limit={3} />
        <EvidenceRows title="약점과 한계" items={watchItems} emptyLabel="현재 확인된 구조적 약점 없음" limit={3} />
      </div>

      <DecisionQuestionList narrative={reportNarrative} />

      <PatternGuidePanel guide={patternGuide} />

      <ReviewActionBoard sections={finalReviewSections} />

      <DetailTabs tabs={detailTabs} />
    </section>
  )
}
