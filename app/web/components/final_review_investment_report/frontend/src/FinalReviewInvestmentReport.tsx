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
  observed?: string[]
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
}

type PatternGuide = {
  summary?: {
    headline?: string
    supportCounts?: Record<string, number>
    support_counts?: Record<string, number>
    boundaryNote?: string
    boundary_note?: string
  }
  cards?: PatternGuideCard[]
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

const listItems = (items: string[] | undefined): string[] => (items ?? []).map((item) => compact(item, "")).filter(Boolean)

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
  const cards = guide.cards ?? []
  return (
    <section className="fr-invest-report__patterns" aria-label="Monitoring 방향 가이드">
      <div className="fr-invest-report__section-head">
        <div>
          <span>조건부 패턴 프로토타입</span>
          <h5>Monitoring 방향 가이드</h5>
        </div>
        <strong>근거 충분 {counts.supported ?? 0} · 참고 {counts.indicative ?? 0} · 보류 {counts.insufficient ?? 0}</strong>
      </div>
      <p className="fr-invest-report__pattern-boundary">{compact(field(summary.boundaryNote, summary.boundary_note))}</p>
      <div className="fr-invest-report__pattern-list">
        {cards.map((card, index) => {
          const sources = field(card.evidenceSources, card.evidence_sources) ?? []
          const missing = field(card.missingSignals, card.missing_signals) ?? []
          return (
            <article className={`fr-invest-report__pattern fr-invest-report__pattern--${toneClass(card.tone)}`} key={card.key ?? index}>
              <div className="fr-invest-report__pattern-head">
                <span>{String(index + 1).padStart(2, "0")}</span>
                <h6>{compact(card.label)}</h6>
                <em>{compact(field(card.supportLabel, card.support_label))}</em>
              </div>
              <p>{compact(card.conclusion)}</p>
              <dl>
                <div><dt>근거</dt><dd>{card.observed?.length ? card.observed.join(" · ") : "직접 관측값 없음"}</dd></div>
                <div><dt>Source / 기준일</dt><dd>{sources.length ? sources.join(", ") : "-"} / {compact(field(card.evidenceAsOf, card.evidence_as_of))}</dd></div>
                <div><dt>보강 필요</dt><dd>{missing.length ? missing.join(", ") : "없음"}</dd></div>
              </dl>
              <small>{compact(field(card.monitoringTrigger, card.monitoring_trigger))}</small>
            </article>
          )
        })}
      </div>
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
          <span>해석</span>
          <h5>실제 판단에 쓰는 근거만 표시합니다.</h5>
        </div>
      </div>
      <div className="fr-invest-report__interpretation-rows">
        {cards.map((card, index) => (
          <article className={`fr-invest-report__interpretation-row fr-invest-report__interpretation-row--${toneClass(card.tone)}`} key={`${card.kind ?? card.title ?? "interpretation"}-${index}`}>
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
        <div className="fr-invest-report__detail-panel-head">
          <span>{activeTab.label}</span>
          <h5>{activeTab.title}</h5>
        </div>
        {activeTab.children}
      </div>
    </section>
  )
}

function ReviewActionBoard({ sections }: { sections: ReviewRoleSection[] }) {
  const total = sections.reduce((sum, section) => sum + Number(section.count ?? section.items?.length ?? 0), 0)
  return (
    <section className="fr-invest-report__review-actions" aria-label="Final Review 확인 필요">
      <div className="fr-invest-report__section-head">
        <div>
          <span>Level2 REVIEW handoff</span>
          <h5>Final Review 확인 필요</h5>
        </div>
        <strong>{total > 0 ? `${total}개 행동 확인` : "추가 확인 없음"}</strong>
      </div>
      <p className="fr-invest-report__review-boundary">
        저장된 Practical Validation evidence를 다시 실행하지 않고, 각 항목을 점수에 반영됨 / 저장 전 확인 / Monitoring 조건으로 넘김 / blocker로 구분합니다.
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
                      <span>{compact(item.detail)}</span>
                      <small>{compact(item.action)}</small>
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

function ScorecardCategoryList({ categories }: { categories: ScorecardCategory[] }) {
  return (
    <div className="fr-invest-report__scorecard-categories">
      {categories.map((category, index) => (
        <article className={`fr-invest-report__scorecard-category fr-invest-report__scorecard-category--${toneClass(category.tone)}`} key={`${category.category ?? "score"}-${index}`}>
          <div>
            <h5>{compact(category.category)}</h5>
            <strong>{formattedScore(category.score)}</strong>
          </div>
          <p>{compact(category.evidence)}</p>
          <small>{compact(category.effect)}</small>
        </article>
      ))}
    </div>
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
          <p>{compact(dimension.interpretation)}</p>
          <small>{compact(dimension.evidence)} · weight {Math.round((Number(dimension.weight) || 0) * 100)}%</small>
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
      <h5>Level2 REVIEW 점수 영향</h5>
      {impacts.length > 0 ? (
        impacts.map((impact, index) => {
          const scoreEffect = field(impact.scoreEffect, impact.score_effect)
          const scorePolicy = field(impact.scorePolicy, impact.score_policy)
          const observedValue = field(impact.observedValue, impact.observed_value)
          const evidenceSource = field(impact.evidenceSource, impact.evidence_source)
          const evidenceAsOf = field(impact.evidenceAsOf, impact.evidence_as_of)
          const traceStatus = field(impact.traceStatus, impact.trace_status)
          return (
            <section className={`fr-invest-report__review-impact fr-invest-report__review-impact--${toneClass(impact.tone)}`} key={`${impact.role ?? "review"}-${impact.title ?? index}`}>
              <div>
                <strong>{compact(impact.title)}</strong>
                <span>{Number(scoreEffect) === 0 ? "감점 없음" : formattedScore(scoreEffect)}</span>
              </div>
              <small>{compact(field(impact.roleLabel, impact.role_label))} · {compact(field(impact.targetDimension, impact.target_dimension))}</small>
              <p>{compact(impact.rationale ?? impact.detail)}</p>
              <dl className="fr-invest-report__review-trace">
                <div><dt>관측값</dt><dd>{compact(observedValue, "미제공")}</dd></div>
                <div><dt>판단 기준</dt><dd>{compact(impact.threshold, "미제공")}</dd></div>
                <div><dt>근거</dt><dd>{compact(evidenceSource, "미제공")}</dd></div>
                <div><dt>기준일</dt><dd>{compact(evidenceAsOf, "미제공")}</dd></div>
              </dl>
              <small>{compact(scorePolicy)} · {compact(traceStatus)}</small>
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
  const monitoring = report.monitoringConditions ?? report.monitoring_conditions ?? {}
  const triggers = listItems(field(monitoring.reviewTriggers, monitoring.review_triggers))
  const interpretationCards = field(report.interpretationCards, report.interpretation_cards) ?? []
  const watchItems = field(report.watchItems, report.watch_items) ?? report.weaknesses ?? []
  const level2Review = report.level2ReviewDisposition ?? report.level2_review_disposition ?? {}
  const saveHandoff = report.saveHandoffSummary ?? report.save_handoff_summary ?? {}
  const weaknessImprovement = report.weaknessImprovement ?? report.weakness_improvement ?? {}
  const level2Summary = level2Review.summary ?? {}
  const level2RoleSections = field(level2Review.roleSections, level2Review.role_sections) ?? []
  const reviewItemCount = Number(level2Summary.total ?? 0)
  const scorecardOverall = field(scorecard.overallScore, scorecard.overall_score)
  const scorecardBand = field(scorecard.scoreBand, scorecard.score_band)
  const scorecardClassification = field(scorecard.classificationLabel, scorecard.classification_label)
  const scorecardDecision = field(scorecard.decisionLabel, scorecard.decision_label)
  const scorecardMonitoringCandidate = field(scorecard.monitoringCandidate, scorecard.monitoring_candidate) === true
  const scorecardPreCap = field(scorecard.preCapScore, scorecard.pre_cap_score)
  const scorecardDrivers = field(scorecard.scoreDrivers, scorecard.score_drivers) ?? {}
  const scorecardLimits = field(scorecard.scoreLimits, scorecard.score_limits) ?? []
  const routeConstraints = field(scorecard.routeConstraints, scorecard.route_constraints) ?? []
  const scorecardReviewImpacts = field(scorecard.reviewImpacts, scorecard.review_impacts) ?? []
  const headlineScores = field(scorecard.headlineScores, scorecard.headline_scores) ?? []
  const judgmentRecord = saveHandoff.judgmentRecord ?? saveHandoff.judgment_record ?? {}
  const monitoringHandoff = saveHandoff.monitoringHandoff ?? saveHandoff.monitoring_handoff ?? {}
  const saveRecordType = field(saveHandoff.recordType, saveHandoff.record_type)
  const improvementComparison = weaknessImprovement.comparison ?? {}
  const improvementProposals = weaknessImprovement.proposals ?? []
  const improvementCurrent = field(improvementComparison.currentScore, improvementComparison.current_score)
  const improvementLow = field(improvementComparison.expectedScoreLow, improvementComparison.expected_score_low)
  const improvementHigh = field(improvementComparison.expectedScoreHigh, improvementComparison.expected_score_high)
  const improvementStatus = field(improvementComparison.verificationStatus, improvementComparison.verification_status)
  const metaItems: MetaItem[] = [
    { label: "후보", value: compact(source.title) },
    { label: "확인 필요", value: `${reviewItemCount}개`, tone: reviewItemCount > 0 ? "warning" : "positive" },
  ]
  const detailTabs: DetailTab[] = [
    {
      id: "score-evidence",
      label: "근거 상세",
      title: "최종 점수 체계",
      children: (
        <section className="fr-invest-report__scorecard-detail">
          <div className="fr-invest-report__scorecard-head">
            <div>
              <span>최종 점수 체계</span>
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
            <span>{scorecardMonitoringCandidate ? "Monitoring 후보" : "Monitoring handoff 보류"}</span>
            <span>{compact(scorecard.classification)}</span>
            <span>Pre-cap {formattedScore(scorecardPreCap)}</span>
          </div>
          <div className="fr-invest-report__scorecard-subtitle">세부 점수</div>
          <ScorecardDimensionList dimensions={scorecard.dimensions ?? []} />
          <div className="fr-invest-report__scorecard-subtitle">점수 영향</div>
          <div className="fr-invest-report__score-drivers">
            <ScoreDriverList title="가산 요인" drivers={scorecardDrivers.positive ?? []} />
            <ScoreDriverList title="감점 요인" drivers={scorecardDrivers.negative ?? []} />
            <ScoreLimitList limits={scorecardLimits} constraints={routeConstraints} />
          </div>
          <ReviewImpactList impacts={scorecardReviewImpacts} />
          <ScorecardCategoryList categories={scorecard.categories ?? []} />
        </section>
      ),
    },
    {
      id: "save-boundary",
      label: "저장 경계",
      title: "저장 / Monitoring handoff",
      children: (
        <section className="fr-invest-report__handoff-detail">
          <div>
            <span>저장 / Monitoring handoff</span>
            <h5>{compact(judgmentRecord.label)}</h5>
            <p>{compact(judgmentRecord.detail)}</p>
          </div>
          <div className="fr-invest-report__handoff-grid">
            <article>
              <span>Final Review 판단 저장</span>
              <strong>{judgmentRecord.ready ? "Ready" : "Check"}</strong>
              <p>{compact(saveRecordType)}</p>
            </article>
            <article>
              <span>Portfolio Monitoring</span>
              <strong>{monitoringHandoff.candidate ? "Handoff" : "Decision Only"}</strong>
              <p>{compact(monitoringHandoff.detail)}</p>
            </article>
            <article>
              <span>Order / Auto Rebalance</span>
              <strong>Disabled</strong>
              <p>Final Review는 판단 기록과 Monitoring 후보 handoff만 다룹니다.</p>
            </article>
          </div>
        </section>
      ),
    },
    {
      id: "improvement-candidates",
      label: "개선 후보",
      title: "약점 개선안",
      children: (
        <section className="fr-invest-report__improvement-detail">
          <div className="fr-invest-report__improvement-head">
            <div>
              <span>약점 개선안</span>
              <h5>현재 후보와 개선 기대 범위</h5>
            </div>
            <aside>
              <strong>{formattedScore(improvementCurrent)}</strong>
              <span>{formattedScore(improvementLow)} - {formattedScore(improvementHigh)}</span>
              <small>{compact(improvementStatus)}</small>
            </aside>
          </div>
          <div className="fr-invest-report__improvement-list">
            {improvementProposals.map((proposal, index) => (
              <article className="fr-invest-report__improvement-item" key={`${proposal.weakness ?? "proposal"}-${index}`}>
                <h5>{compact(proposal.weakness)}</h5>
                <p>{compact(field(proposal.currentGap, proposal.current_gap))}</p>
                <strong>{compact(field(proposal.proposedChange, proposal.proposed_change))}</strong>
                <small>{compact(field(proposal.verificationStep, proposal.verification_step))}</small>
              </article>
            ))}
          </div>
        </section>
      ),
    },
    {
      id: "monitoring-conditions",
      label: "Monitoring",
      title: "Monitoring 조건",
      children: (
        <footer className="fr-invest-report__monitoring">
          <div>
            <span>Monitoring 조건</span>
            <strong>{compact(field(monitoring.trackingBenchmark, monitoring.tracking_benchmark))}</strong>
            <small>{compact(field(monitoring.reviewCadence, monitoring.review_cadence))}</small>
          </div>
          <ul>
            {triggers.length > 0 ? triggers.map((trigger, index) => <li key={`${trigger}-${index}`}>{trigger}</li>) : <li>추적 trigger 없음</li>}
          </ul>
        </footer>
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

      <div className="fr-invest-report__evidence">
        <EvidenceRows title="강점" items={report.strengths ?? []} emptyLabel="강점 근거 없음" limit={3} />
        <EvidenceRows title="약점과 한계" items={watchItems} emptyLabel="현재 확인된 구조적 약점 없음" limit={3} />
      </div>

      <DecisionQuestionList narrative={reportNarrative} />

      <PatternGuidePanel guide={patternGuide} />

      <ReviewActionBoard sections={level2RoleSections} />

      <InterpretationRows cards={interpretationCards} />

      <DetailTabs tabs={detailTabs} />
    </section>
  )
}
