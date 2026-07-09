import React, { useEffect } from "react"
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
  label?: string
  detail?: string
  cap?: number
  reason?: string
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
  detail?: string
  action?: string
  rationale?: string
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
  saveHandoffSummary?: SaveHandoffSummary
  save_handoff_summary?: SaveHandoffSummary
  weaknessImprovement?: WeaknessImprovement
  weakness_improvement?: WeaknessImprovement
  summary?: Summary
  strengths?: ReportCard[]
  weaknesses?: ReportCard[]
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

function EvidenceList({ title, items, emptyLabel }: { title: string; items: ReportCard[]; emptyLabel: string }) {
  return (
    <section className="fr-invest-report__lane">
      <div className="fr-invest-report__lane-title">{title}</div>
      <div className="fr-invest-report__cards">
        {items.length > 0 ? (
          items.map((item, index) => (
            <article className={`fr-invest-report__card fr-invest-report__card--${toneClass(item.tone)}`} key={`${item.title ?? title}-${index}`}>
              <div>
                <h5>{compact(item.title)}</h5>
                <span>{compact(item.severity)}</span>
              </div>
              <p>{compact(item.detail)}</p>
              {item.action ? <small>{compact(item.action)}</small> : null}
            </article>
          ))
        ) : (
          <article className="fr-invest-report__card fr-invest-report__card--neutral">
            <div>
              <h5>{emptyLabel}</h5>
              <span>-</span>
            </div>
            <p>현재 report payload에 표시할 항목이 없습니다.</p>
          </article>
        )}
      </div>
    </section>
  )
}

function SmallSection({ section }: { section: ReportSection }) {
  return (
    <article className="fr-invest-report__mini">
      <h5>{compact(section.title)}</h5>
      <p>{compact(section.detail)}</p>
      <div>
        {section.score !== undefined ? <span>Score {formattedScore(section.score)}</span> : null}
        {field(section.reviewCadence, section.review_cadence) ? <span>{compact(field(section.reviewCadence, section.review_cadence))}</span> : null}
        {field(section.openReviewItems, section.open_review_items) !== undefined ? <span>Open {field(section.openReviewItems, section.open_review_items)}</span> : null}
        {field(section.policyBlockers, section.policy_blockers) !== undefined ? <span>Blocker {field(section.policyBlockers, section.policy_blockers)}</span> : null}
      </div>
    </article>
  )
}

function ReviewDispositionList({ title, items, emptyLabel }: { title: string; items: ReviewDispositionItem[]; emptyLabel: string }) {
  return (
    <article className="fr-invest-report__review-group">
      <h5>{title}</h5>
      <div>
        {items.length > 0 ? (
          items.map((item, index) => (
            <section className={`fr-invest-report__review-item fr-invest-report__review-item--${toneClass(item.tone)}`} key={`${title}-${item.title ?? index}`}>
              <strong>{compact(item.title)}</strong>
              <span>{compact(item.roleLabel ?? item.role_label)} · {compact(item.dispositionLabel ?? item.disposition_label)}</span>
              <p>{compact(item.detail)}</p>
              <small>{compact(item.action)}</small>
            </section>
          ))
        ) : (
          <section className="fr-invest-report__review-item fr-invest-report__review-item--neutral">
            <strong>{emptyLabel}</strong>
            <span>-</span>
            <p>해당 분류의 Level2 REVIEW 항목이 없습니다.</p>
          </section>
        )}
      </div>
    </article>
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

function ScoreLimitList({ limits }: { limits: ScorecardLimit[] }) {
  return (
    <article className="fr-invest-report__score-limits">
      <h5>점수 제한</h5>
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
          <strong>적용된 score cap 없음</strong>
          <span>-</span>
          <p>현재 hard blocker나 과도한 open review로 인한 종합점수 상한은 없습니다.</p>
        </section>
      )}
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
          return (
            <section className={`fr-invest-report__review-impact fr-invest-report__review-impact--${toneClass(impact.tone)}`} key={`${impact.role ?? "review"}-${impact.title ?? index}`}>
              <div>
                <strong>{compact(impact.title)}</strong>
                <span>{formattedScore(scoreEffect)}</span>
              </div>
              <small>{compact(field(impact.roleLabel, impact.role_label))} · {compact(field(impact.targetDimension, impact.target_dimension))}</small>
              <p>{compact(impact.rationale ?? impact.detail)}</p>
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
  const source = report.source ?? {}
  const tone = toneClass(recommendation.tone)
  const monitoring = report.monitoringConditions ?? report.monitoring_conditions ?? {}
  const triggers = listItems(field(monitoring.reviewTriggers, monitoring.review_triggers))
  const performance = report.performanceInterpretation ?? report.performance_interpretation ?? {}
  const scenario = report.scenarioFit ?? report.scenario_fit ?? {}
  const risk = report.expectedRangeAndRisk ?? report.expected_range_and_risk ?? {}
  const benchmark = report.benchmarkRationale ?? report.benchmark_rationale ?? {}
  const level2Review = report.level2ReviewDisposition ?? report.level2_review_disposition ?? {}
  const saveHandoff = report.saveHandoffSummary ?? report.save_handoff_summary ?? {}
  const weaknessImprovement = report.weaknessImprovement ?? report.weakness_improvement ?? {}
  const level2Summary = level2Review.summary ?? {}
  const level2Groups = level2Review.groups ?? {}
  const handoffReady = field(monitoring.handoffReady, monitoring.handoff_ready) === true
  const monitoringCandidate = field(recommendation.monitoringCandidate, recommendation.monitoring_candidate) === true
  const openReviewCount = field(level2Summary.openReview, level2Summary.open_review) ?? 0
  const monitoringFollowupCount = field(level2Summary.monitoringFollowup, level2Summary.monitoring_followup) ?? 0
  const openReviewItems = field(level2Groups.openReview, level2Groups.open_review) ?? []
  const monitoringFollowupItems = field(level2Groups.monitoringFollowup, level2Groups.monitoring_followup) ?? []
  const scorecardOverall = field(scorecard.overallScore, scorecard.overall_score)
  const scorecardBand = field(scorecard.scoreBand, scorecard.score_band)
  const scorecardClassification = field(scorecard.classificationLabel, scorecard.classification_label)
  const scorecardDecision = field(scorecard.decisionLabel, scorecard.decision_label)
  const scorecardMonitoringCandidate = field(scorecard.monitoringCandidate, scorecard.monitoring_candidate) === true
  const scorecardPreCap = field(scorecard.preCapScore, scorecard.pre_cap_score)
  const scorecardDrivers = field(scorecard.scoreDrivers, scorecard.score_drivers) ?? {}
  const scorecardLimits = field(scorecard.scoreLimits, scorecard.score_limits) ?? []
  const scorecardReviewImpacts = field(scorecard.reviewImpacts, scorecard.review_impacts) ?? []
  const judgmentRecord = saveHandoff.judgmentRecord ?? saveHandoff.judgment_record ?? {}
  const monitoringHandoff = saveHandoff.monitoringHandoff ?? saveHandoff.monitoring_handoff ?? {}
  const saveRecordType = field(saveHandoff.recordType, saveHandoff.record_type)
  const improvementComparison = weaknessImprovement.comparison ?? {}
  const improvementProposals = weaknessImprovement.proposals ?? []
  const improvementCurrent = field(improvementComparison.currentScore, improvementComparison.current_score)
  const improvementLow = field(improvementComparison.expectedScoreLow, improvementComparison.expected_score_low)
  const improvementHigh = field(improvementComparison.expectedScoreHigh, improvementComparison.expected_score_high)
  const improvementStatus = field(improvementComparison.verificationStatus, improvementComparison.verification_status)

  return (
    <section className={`fr-invest-report fr-invest-report--${tone}`}>
      <header className="fr-invest-report__header">
        <div>
          <div className="fr-invest-report__kicker">Final Review 투자 검토서</div>
          <h3>{compact(summary.headline, "최종 검토 요약")}</h3>
          <p>{compact(summary.verdict)}</p>
        </div>
        <aside className="fr-invest-report__score" aria-label="최종 판단 점수">
          <span>{compact(recommendation.label)}</span>
          <strong>{formattedScore(score.value)}</strong>
          <small>{compact(score.label)}</small>
        </aside>
      </header>

      <div className="fr-invest-report__facts">
        <span>
          <b>{compact(source.title)}</b>
          후보
        </span>
        <span>
          <b>{compact(recommendation.stateLabel ?? recommendation.state_label)}</b>
          판단 상태
        </span>
        <span>
          <b>{monitoringCandidate ? "가능" : "불가"}</b>
          Monitoring 후보
        </span>
        <span>
          <b>{handoffReady ? "Ready" : "Blocked"}</b>
          Handoff
        </span>
      </div>

      <div className="fr-invest-report__summary">
        <article>
          <span>핵심 근거</span>
          <p>{compact(summary.strongestEvidence ?? summary.strongest_evidence)}</p>
        </article>
        <article>
          <span>가장 큰 약점</span>
          <p>{compact(summary.weakestConstraint ?? summary.weakest_constraint)}</p>
        </article>
        <article>
          <span>다음 행동</span>
          <p>{compact(summary.nextAction ?? summary.next_action)}</p>
        </article>
      </div>

      <div className="fr-invest-report__evidence">
        <EvidenceList title="강점" items={report.strengths ?? []} emptyLabel="강점 근거 없음" />
        <EvidenceList title="약점" items={report.weaknesses ?? []} emptyLabel="선택 차단 약점 없음" />
      </div>

      <div className="fr-invest-report__mini-grid">
        <SmallSection section={performance} />
        <SmallSection section={scenario} />
        <SmallSection section={risk} />
        <SmallSection section={benchmark} />
      </div>

      <section className="fr-invest-report__scorecard-panel">
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
          <ScoreLimitList limits={scorecardLimits} />
        </div>
        <ReviewImpactList impacts={scorecardReviewImpacts} />
        <ScorecardCategoryList categories={scorecard.categories ?? []} />
      </section>

      <section className="fr-invest-report__handoff-panel">
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

      <section className="fr-invest-report__improvement-panel">
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

      <section className="fr-invest-report__review-disposition">
        <div className="fr-invest-report__review-head">
          <div>
            <span>Level2 REVIEW 처리 결과</span>
            <h5>Final Review에서 다시 실행하지 않고 판단 근거로 소비합니다.</h5>
          </div>
          <div className="fr-invest-report__review-counts">
            <b>{level2Summary.blocker ?? 0}</b><small>Blocker</small>
            <b>{level2Summary.warning ?? 0}</b><small>Warning</small>
            <b>{openReviewCount}</b><small>Open</small>
            <b>{monitoringFollowupCount}</b><small>Monitoring</small>
          </div>
        </div>
        <div className="fr-invest-report__review-grid">
          <ReviewDispositionList title="Blocker" items={level2Groups.blocker ?? []} emptyLabel="저장 전 보강 없음" />
          <ReviewDispositionList title="Warning" items={level2Groups.warning ?? []} emptyLabel="최종 판단 warning 없음" />
          <ReviewDispositionList title="Open Review" items={openReviewItems} emptyLabel="Final Review open review 없음" />
          <ReviewDispositionList title="Monitoring Follow-up" items={monitoringFollowupItems} emptyLabel="Monitoring 추적 항목 없음" />
        </div>
      </section>

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
    </section>
  )
}
