import React, { useEffect } from "react"
import { Streamlit } from "streamlit-component-lib"

type Tone = "positive" | "warning" | "danger" | "neutral"

type FixItem = {
  label?: string
  status?: string
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

type PracticalValidationFixQueueProps = {
  statusLabel: string
  tone: Tone
  verdict: string
  nextAction: string
  canSaveAndMove: boolean
  fixItems: FixItem[]
  coreGroups: CoreGroup[]
  reviewCount: number
}

const toneClass = (tone: Tone | string | undefined): Tone =>
  ["positive", "warning", "danger", "neutral"].includes(String(tone)) ? (tone as Tone) : "neutral"

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
            fixLocation: "Final Review",
            fixAction: "저장 후 이동 전에 핵심 근거만 한 번 더 확인합니다.",
            tone: "positive" as Tone,
          },
        ]
  const coreGroups = props.coreGroups.length > 0 ? props.coreGroups : []

  return (
    <section className={`pv-react-fix pv-react-fix--${tone}`}>
      <header className="pv-react-fix__head">
        <div>
          <div className="pv-react-fix__kicker">2차 검증 결론 / Fix Queue</div>
          <h4>{props.verdict}</h4>
          {props.nextAction ? <p>{props.nextAction}</p> : null}
        </div>
        <div className="pv-react-fix__status">
          <span>{props.statusLabel}</span>
          <b>{props.canSaveAndMove ? "Final Review 이동 가능" : "Final Review 이동 보류"}</b>
        </div>
      </header>

      <div className="pv-react-fix__metrics">
        <div className="pv-react-fix__metric">
          <span>Fix Queue</span>
          <b>{props.fixItems.length}</b>
        </div>
        <div className="pv-react-fix__metric">
          <span>Review Items</span>
          <b>{props.reviewCount}</b>
        </div>
        <div className="pv-react-fix__metric">
          <span>Core Evidence</span>
          <b>{coreGroups.length}</b>
        </div>
      </div>

      <div className="pv-react-fix__body">
        <section className="pv-react-fix__lane">
          <div className="pv-react-fix__lane-title">먼저 해결할 항목</div>
          <div className="pv-react-fix__items">
            {fixItems.map((item, index) => (
              <article
                className={`pv-react-fix__item pv-react-fix__item--${toneClass(item.tone)}`}
                key={`${item.label ?? "fix"}-${index}`}
              >
                <div>
                  <span>{item.status ?? "-"}</span>
                  <h5>{item.label ?? "-"}</h5>
                </div>
                <p>{item.fixAction ?? "-"}</p>
                <small>{item.fixLocation ?? "-"}</small>
                {item.gateReason ? <em>{item.gateReason}</em> : null}
              </article>
            ))}
          </div>
        </section>

        <section className="pv-react-fix__lane">
          <div className="pv-react-fix__lane-title">핵심 근거 그룹</div>
          <div className="pv-react-fix__groups">
            {coreGroups.map((group, index) => (
              <article
                className={`pv-react-fix__group pv-react-fix__group--${toneClass(group.tone)}`}
                key={`${group.label ?? "core"}-${index}`}
              >
                <div>
                  <h5>{group.label ?? "-"}</h5>
                  <span>{group.status ?? "-"}</span>
                </div>
                <p>{group.purpose ?? "-"}</p>
                {group.modules && group.modules.length > 0 ? (
                  <small>{group.modules.slice(0, 4).join(" / ")}</small>
                ) : null}
              </article>
            ))}
            {coreGroups.length === 0 ? (
              <article className="pv-react-fix__group pv-react-fix__group--neutral">
                <div>
                  <h5>핵심 근거 그룹 없음</h5>
                  <span>-</span>
                </div>
                <p>workspace read model에 표시할 core evidence group이 없습니다.</p>
              </article>
            ) : null}
          </div>
        </section>
      </div>
    </section>
  )
}
