import React, { useEffect } from "react"
import { Streamlit } from "streamlit-component-lib"

type Tone = "positive" | "warning" | "danger" | "neutral"

type DataActionItem = {
  groupId?: string
  group_id?: string
  moduleId?: string
  module_id?: string
  category?: string
  tickers?: string[]
  reason?: string
  nextAction?: string
  next_action?: string
  availability?: string
  source?: string
  targetAnchor?: string
  target_anchor?: string
}

type DataActionGroup = {
  groupId?: string
  group_id?: string
  label?: string
  description?: string
  tone?: Tone
  count?: number
  items?: DataActionItem[]
}

export type DataActionBoard = {
  title?: string
  detail?: string
  summary?: Record<string, number | string>
  groups?: DataActionGroup[]
}

type PracticalValidationDataActionBoardProps = {
  board: DataActionBoard
}

const groupLabels: Record<string, string> = {
  immediate_collect: "지금 수집 가능",
  source_map_discovery: "Source map 탐색",
  connector_needed: "Connector mapping 필요",
  no_action: "현재 수집으로 해결 불가",
}

const toneClass = (tone: Tone | string | undefined): Tone =>
  ["positive", "warning", "danger", "neutral"].includes(String(tone)) ? (tone as Tone) : "neutral"

const compact = (value: unknown, fallback = "-"): string => {
  const text = String(value ?? "").trim()
  return text || fallback
}

const numberValue = (value: unknown): number => {
  const parsed = Number(value ?? 0)
  return Number.isFinite(parsed) ? parsed : 0
}

function TickerChips({ tickers }: { tickers?: string[] }) {
  const cleaned = (tickers ?? []).map((ticker) => compact(ticker, "")).filter(Boolean).slice(0, 8)
  if (cleaned.length === 0) {
    return <span className="pv-data-action__chip pv-data-action__chip--empty">공통</span>
  }
  return (
    <div className="pv-data-action__chips" aria-label="ticker chips">
      {cleaned.map((ticker) => (
        <span className="pv-data-action__chip" key={ticker}>{ticker}</span>
      ))}
    </div>
  )
}

function DataActionCard({ item }: { item: DataActionItem }) {
  return (
    <article className="pv-data-action__card">
      <header>
        <div>
          <span className="pv-data-action__category">{compact(item.category)}</span>
          <h5>{compact(item.availability)}</h5>
        </div>
        <TickerChips tickers={item.tickers} />
      </header>
      <dl>
        <div>
          <dt>근거</dt>
          <dd>{compact(item.reason)}</dd>
        </div>
        <div>
          <dt>다음 행동</dt>
          <dd>{compact(item.nextAction ?? item.next_action)}</dd>
        </div>
      </dl>
    </article>
  )
}

export function PracticalValidationDataActionBoard({ board }: PracticalValidationDataActionBoardProps) {
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [board])

  const groups = Array.isArray(board.groups) ? board.groups : []
  const summary = board.summary ?? {}
  const itemCount = numberValue(summary.item_count)
  const actionableCount = numberValue(summary.actionable_count)

  return (
    <section className="pv-data-action">
      <header className="pv-data-action__head">
        <div>
          <div className="pv-data-action__kicker">Practical Validation Flow 4</div>
          <h4>{compact(board.title, "데이터 보강 대상")}</h4>
          <p>{compact(board.detail, "지금 보강할 수 있는 항목과 현재 수집으로 해결되지 않는 항목을 분리합니다.")}</p>
        </div>
        <div className="pv-data-action__summary" aria-label="data action summary">
          <span><b>{actionableCount}</b> 보강 경로</span>
          <span><b>{itemCount}</b> 전체 항목</span>
        </div>
      </header>

      <div className="pv-data-action__groups">
        {groups.map((group) => {
          const groupId = compact(group.groupId ?? group.group_id, "no_action")
          const items = Array.isArray(group.items) ? group.items : []
          return (
            <section className={`pv-data-action__group pv-data-action__group--${toneClass(group.tone)}`} key={groupId}>
              <header>
                <div>
                  <span>{groupLabels[groupId] ?? compact(group.label)}</span>
                  <h5>{compact(group.label ?? groupLabels[groupId])}</h5>
                </div>
                <b>{items.length}</b>
              </header>
              <p>{compact(group.description)}</p>
              <div className="pv-data-action__cards">
                {items.map((item, index) => (
                  <DataActionCard item={item} key={`${groupId}-${item.category ?? "item"}-${index}`} />
                ))}
                {items.length === 0 ? (
                  <div className="pv-data-action__empty">현재 표시할 항목이 없습니다.</div>
                ) : null}
              </div>
            </section>
          )
        })}
      </div>
    </section>
  )
}
