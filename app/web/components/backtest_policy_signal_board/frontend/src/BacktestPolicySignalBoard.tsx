import React, { useEffect, useMemo, useState } from "react"
import { Streamlit, ComponentProps } from "streamlit-component-lib"

type Tone = "positive" | "warning" | "danger" | "neutral"

type Metric = {
  label?: string
  value?: string
  detail?: string
  tone?: Tone
}

type CheckedItem = {
  label?: string
  detail?: string
}

type PolicySignalRow = {
  group?: string
  signal?: string
  status?: string
  effect?: string
  meaning?: string
  checked_evidence?: string
  plain_explanation?: string
  checked_items?: CheckedItem[]
  display_detail?: string
  next_surface?: string
  source_key?: string
}

type GroupedPolicyRows = {
  group: string
  helper: string
  rows: PolicySignalRow[]
}

type BacktestPolicySignalBoardArgs = {
  tone?: Tone
  headline?: string
  subhead?: string
  metrics?: Metric[]
  firstStageRows?: PolicySignalRow[]
}

const GROUP_ORDER = ["Data Trust", "Execution Source", "Validation Source", "Promotion", "Execution Review", "Validation Review"]

const GROUP_HELP: Record<string, string> = {
  "Data Trust": "성과를 읽어도 되는 데이터 범위인지 확인합니다.",
  "Execution Source": "실제로 운용할 때 거래 가능성과 ETF 운용 근거가 깨지지 않는지 봅니다.",
  "Validation Source": "후속 검증에서 benchmark와 방어 기준을 비교할 수 있는지 봅니다.",
  Promotion: "2차 검증 source로 넘길 수 있는 후보인지 확인합니다.",
  "Execution Review": "비용과 turnover처럼 실전 해석에서 이어서 볼 항목입니다.",
  "Validation Review": "최근 / 구간별 약화처럼 Practical Validation에서 확인할 항목입니다.",
}

const toneClass = (tone: Tone | string | undefined): Tone =>
  ["positive", "warning", "danger", "neutral"].includes(String(tone)) ? (tone as Tone) : "neutral"

const effectLabel = (effect: string | undefined): string => {
  if (effect === "block") return "확인 필요"
  if (effect === "pass") return "통과"
  if (effect === "review") return "2차 확인"
  return "참고"
}

const effectTone = (effect: string | undefined): Tone => {
  if (effect === "block") return "danger"
  if (effect === "pass") return "positive"
  if (effect === "review") return "warning"
  return "neutral"
}

const compact = (value: unknown, fallback = "-"): string => {
  const text = String(value ?? "").trim()
  return text || fallback
}

const rowKey = (row: PolicySignalRow, index: number): string =>
  `${compact(row.group, "group")}-${compact(row.signal, "signal")}-${compact(row.source_key, String(index))}`

const buildGroupedFirstRows = (rows: PolicySignalRow[]): GroupedPolicyRows[] => {
  const grouped = new Map<string, PolicySignalRow[]>()
  rows.forEach((row) => {
    const group = compact(row.group, "기타")
    grouped.set(group, [...(grouped.get(group) ?? []), row])
  })

  const orderedGroups = [
    ...GROUP_ORDER.filter((group) => grouped.has(group)),
    ...Array.from(grouped.keys()).filter((group) => !GROUP_ORDER.includes(group)).sort(),
  ]

  return orderedGroups.map((group) => ({
    group,
    helper: GROUP_HELP[group] ?? "1차 화면에서 바로 확인 가능한 기준입니다.",
    rows: grouped.get(group) ?? [],
  }))
}

export function BacktestPolicySignalBoard(props: ComponentProps) {
  const args = (props.args ?? {}) as BacktestPolicySignalBoardArgs
  const [openHelpKey, setOpenHelpKey] = useState<string | null>(null)

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [args, openHelpKey])

  const boardTone = toneClass(args.tone)
  const metrics = args.metrics ?? []
  const firstRows = args.firstStageRows ?? []
  const groupedFirstRows = useMemo(() => buildGroupedFirstRows(firstRows), [firstRows])

  return (
    <section className={`bt-react-policy bt-react-policy--${boardTone}`}>
      <header className="bt-react-policy__head">
        <div>
          <div className="bt-react-policy__kicker">검증 기준 상세</div>
          <h4>{compact(args.headline)}</h4>
          <p>{compact(args.subhead, "")}</p>
        </div>
      </header>

      <div className="bt-react-policy__metrics">
        {metrics.map((metric, index) => (
          <div
            className={`bt-react-policy__metric bt-react-policy__metric--${toneClass(metric.tone)}`}
            key={`${metric.label ?? "metric"}-${index}`}
          >
            <span>{compact(metric.label)}</span>
            <strong>{compact(metric.value)}</strong>
            <em>{compact(metric.detail, "")}</em>
          </div>
        ))}
      </div>

      <div className="bt-react-policy__content">
        <div className="bt-react-policy__primary">
          <div className="bt-react-policy__section-title">
            <strong>1차에서 확인한 기준</strong>
            <span>source 등록 전에 Backtest에서 확정 가능한 항목만 카테고리별로 봅니다.</span>
          </div>
          <div className="bt-react-policy__groups">
            {groupedFirstRows.length > 0 ? (
              groupedFirstRows.map((group) => (
                <section className="bt-react-policy__group" key={group.group}>
                  <header className="bt-react-policy__group-head">
                    <div>
                      <strong>{group.group}</strong>
                      <span>{group.helper}</span>
                    </div>
                    <b>{group.rows.length}개</b>
                  </header>
                  <div className="bt-react-policy__cards">
                    {group.rows.map((row, index) => {
                      const tone = effectTone(row.effect)
                      const key = rowKey(row, index)
                      const helpId = `policy-help-${index}-${compact(row.source_key, "row").replace(/[^a-zA-Z0-9_-]/g, "-")}`
                      const isOpen = openHelpKey === key
                      const checkedItems = row.checked_items ?? []
                      return (
                        <article className={`bt-react-policy__card bt-react-policy__card--${tone}`} key={key}>
                          <div className="bt-react-policy__card-head">
                            <div>
                              <h5>{compact(row.signal)}</h5>
                              <p>{compact(row.plain_explanation ?? row.meaning)}</p>
                            </div>
                            <div className="bt-react-policy__card-actions">
                              <b>{effectLabel(row.effect)}</b>
                              <button
                                aria-controls={helpId}
                                aria-expanded={isOpen}
                                aria-label={`${compact(row.signal)} 설명 보기`}
                                className="bt-react-policy__help"
                                onClick={() => setOpenHelpKey(isOpen ? null : key)}
                                type="button"
                              >
                                ?
                              </button>
                            </div>
                          </div>
                          <div className="bt-react-policy__row">
                            <span>{row.effect === "block" ? "확인할 것" : "판정 근거"}</span>
                            <p>{compact(row.display_detail ?? row.checked_evidence ?? row.meaning)}</p>
                          </div>
                          {isOpen && (
                            <div className="bt-react-policy__help-panel" id={helpId}>
                              <strong>보는 것</strong>
                              {checkedItems.length > 0 ? (
                                <ul>
                                  {checkedItems.map((item, itemIndex) => (
                                    <li key={`${compact(item.label, "item")}-${itemIndex}`}>
                                      <span>{compact(item.label)}</span>
                                      <p>{compact(item.detail, "")}</p>
                                    </li>
                                  ))}
                                </ul>
                              ) : (
                                <p>{compact(row.checked_evidence ?? row.meaning)}</p>
                              )}
                            </div>
                          )}
                          <footer>
                            <span>{compact(row.status)}</span>
                            <span>{compact(row.next_surface)}</span>
                          </footer>
                        </article>
                      )
                    })}
                  </div>
                </section>
              ))
            ) : (
              <div className="bt-react-policy__empty">
                <strong>1차에서 표시할 확정 항목이 없습니다.</strong>
                <span>기술 원천 상세는 아래 접힌 표에서 확인할 수 있습니다.</span>
              </div>
            )}
          </div>
        </div>

      </div>
    </section>
  )
}
