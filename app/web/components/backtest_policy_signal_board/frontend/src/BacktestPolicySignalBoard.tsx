import React, { useEffect } from "react"
import { Streamlit, ComponentProps } from "streamlit-component-lib"

type Tone = "positive" | "warning" | "danger" | "neutral"

type Metric = {
  label?: string
  value?: string
  detail?: string
  tone?: Tone
}

type PolicySignalRow = {
  group?: string
  signal?: string
  status?: string
  effect?: string
  meaning?: string
  checked_evidence?: string
  display_detail?: string
  next_surface?: string
  source_key?: string
}

type SecondStageGroup = {
  label?: string
  count?: number
}

type BacktestPolicySignalBoardArgs = {
  tone?: Tone
  score?: string
  headline?: string
  subhead?: string
  metrics?: Metric[]
  firstStageRows?: PolicySignalRow[]
  secondStageGroups?: SecondStageGroup[]
  handoffNote?: string
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

export function BacktestPolicySignalBoard(props: ComponentProps) {
  const args = (props.args ?? {}) as BacktestPolicySignalBoardArgs

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [args])

  const boardTone = toneClass(args.tone)
  const metrics = args.metrics ?? []
  const firstRows = args.firstStageRows ?? []
  const secondGroups = args.secondStageGroups ?? []

  return (
    <section className={`bt-react-policy bt-react-policy--${boardTone}`}>
      <header className="bt-react-policy__head">
        <div>
          <div className="bt-react-policy__kicker">검증 기준 상세</div>
          <h4>{compact(args.headline)}</h4>
          <p>{compact(args.subhead, "")}</p>
        </div>
        <div className="bt-react-policy__score">{compact(args.score)}</div>
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
            <span>source 등록 전에 여기서 확정 가능한 항목만 봅니다.</span>
          </div>
          <div className="bt-react-policy__cards">
            {firstRows.length > 0 ? (
              firstRows.map((row, index) => {
                const tone = effectTone(row.effect)
                return (
                  <article className={`bt-react-policy__card bt-react-policy__card--${tone}`} key={`${row.signal ?? "row"}-${index}`}>
                    <div className="bt-react-policy__card-head">
                      <div>
                        <span>{compact(row.group)}</span>
                        <h5>{compact(row.signal)}</h5>
                      </div>
                      <b>{effectLabel(row.effect)}</b>
                    </div>
                    <div className="bt-react-policy__row">
                      <span>확인한 것</span>
                      <p>{compact(row.checked_evidence ?? row.meaning)}</p>
                    </div>
                    <div className="bt-react-policy__row">
                      <span>{row.effect === "block" ? "확인할 것" : "판정 근거"}</span>
                      <p>{compact(row.display_detail ?? row.meaning)}</p>
                    </div>
                    <footer>
                      <span>{compact(row.status)}</span>
                      <span>{compact(row.next_surface)}</span>
                    </footer>
                  </article>
                )
              })
            ) : (
              <div className="bt-react-policy__empty">
                <strong>1차에서 표시할 확정 항목이 없습니다.</strong>
                <span>기술 원천 상세는 아래 접힌 표에서 확인할 수 있습니다.</span>
              </div>
            )}
          </div>
        </div>

        <aside className="bt-react-policy__handoff">
          <div className="bt-react-policy__section-title">
            <strong>2차로 넘긴 확인 큐</strong>
            <span>상세 확인은 Practical Validation에서 합니다.</span>
          </div>
          <p>{compact(args.handoffNote)}</p>
          <div className="bt-react-policy__handoff-list">
            {secondGroups.length > 0 ? (
              secondGroups.map((group, index) => (
                <div className="bt-react-policy__handoff-item" key={`${group.label ?? "group"}-${index}`}>
                  <span>{compact(group.label)}</span>
                  <strong>{Number(group.count ?? 0)}개</strong>
                </div>
              ))
            ) : (
              <div className="bt-react-policy__handoff-empty">전달된 2차 확인 항목 없음</div>
            )}
          </div>
        </aside>
      </div>
    </section>
  )
}
