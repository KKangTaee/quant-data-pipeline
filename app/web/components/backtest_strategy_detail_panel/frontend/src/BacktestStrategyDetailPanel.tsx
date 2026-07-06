import React, { useEffect } from "react"
import { ComponentProps, Streamlit } from "streamlit-component-lib"

type DetailInput = {
  label?: string
  detail?: string
}

type DetailSection = {
  title?: string
  summary?: string
  items?: string[]
}

type StrategyDetailModel = {
  display_name?: string
  strategy_key?: string
  family?: string
  variant?: string
  summary?: string
  data_source?: string
  timing?: string
  universe_modes?: string[]
  universe_note?: string
  badges?: string[]
  is_prototype?: boolean
  primary_inputs?: DetailInput[]
  advanced_sections?: DetailSection[]
  preflight_sections?: DetailSection[]
  run_button_label?: string
}

type StrategyDetailArgs = {
  detailModel?: StrategyDetailModel
}

const compact = (value: unknown, fallback = "-"): string => {
  const text = String(value ?? "").trim()
  return text || fallback
}

const asArray = <T,>(value: T[] | undefined): T[] => (Array.isArray(value) ? value : [])

const keyText = (value: unknown, index: number): string =>
  `${compact(value, "item").replace(/[^a-zA-Z0-9_-]/g, "-")}-${index}`

const SectionList = ({ sections, emptyText }: { sections: DetailSection[]; emptyText: string }) => {
  if (sections.length === 0) {
    return <p className="bt-strategy-detail__empty">{emptyText}</p>
  }

  return (
    <div className="bt-strategy-detail__section-grid">
      {sections.map((section, index) => (
        <article className="bt-strategy-detail__section-card" key={keyText(section.title, index)}>
          <div>
            <strong>{compact(section.title)}</strong>
            <p>{compact(section.summary, "")}</p>
          </div>
          <div className="bt-strategy-detail__chips">
            {asArray(section.items).map((item, itemIndex) => (
              <span key={keyText(item, itemIndex)}>{compact(item)}</span>
            ))}
          </div>
        </article>
      ))}
    </div>
  )
}

export function BacktestStrategyDetailPanel(props: ComponentProps) {
  const args = (props.args ?? {}) as StrategyDetailArgs
  const detailModel = args.detailModel ?? {}
  const displayName = compact(detailModel.display_name, "Selected Strategy")
  const badges = asArray(detailModel.badges)
  const primaryInputs = asArray(detailModel.primary_inputs)
  const preflightSections = asArray(detailModel.preflight_sections)
  const advancedSections = asArray(detailModel.advanced_sections)
  const universeModes = asArray(detailModel.universe_modes)

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [detailModel])

  return (
    <section className="bt-strategy-detail">
      <header className="bt-strategy-detail__hero">
        <div className="bt-strategy-detail__copy">
          <span className="bt-strategy-detail__kicker">Strategy Detail</span>
          <h4>{displayName}</h4>
          <p>{compact(detailModel.summary, "")}</p>
          <div className="bt-strategy-detail__badges">
            {badges.map((badge, index) => (
              <span key={keyText(badge, index)}>{compact(badge)}</span>
            ))}
            {detailModel.is_prototype ? <span className="bt-strategy-detail__badge-warning">prototype</span> : null}
          </div>
        </div>
        <div className="bt-strategy-detail__run">
          <span>Run Action</span>
          <strong>{compact(detailModel.run_button_label)}</strong>
        </div>
      </header>

      <div className="bt-strategy-detail__facts">
        <div>
          <span>Data Source</span>
          <strong>{compact(detailModel.data_source)}</strong>
        </div>
        <div>
          <span>Timing</span>
          <strong>{compact(detailModel.timing)}</strong>
        </div>
        <div>
          <span>Universe</span>
          <strong>{universeModes.length ? universeModes.join(" / ") : "-"}</strong>
        </div>
      </div>

      <div className="bt-strategy-detail__note">
        <span>Universe Basis</span>
        <p>{compact(detailModel.universe_note, "")}</p>
      </div>

      <div className="bt-strategy-detail__body">
        <section>
          <div className="bt-strategy-detail__section-title">
            <strong>Primary Inputs</strong>
            <span>{primaryInputs.length} fields</span>
          </div>
          <div className="bt-strategy-detail__input-grid">
            {primaryInputs.map((item, index) => (
              <article className="bt-strategy-detail__input" key={keyText(item.label, index)}>
                <strong>{compact(item.label)}</strong>
                <p>{compact(item.detail, "")}</p>
              </article>
            ))}
          </div>
        </section>

        <section>
          <div className="bt-strategy-detail__section-title">
            <strong>Preflight</strong>
            <span>{preflightSections.length} checks</span>
          </div>
          <SectionList sections={preflightSections} emptyText="이 전략은 실행 전 별도 preflight panel이 없습니다." />
        </section>

        <section>
          <div className="bt-strategy-detail__section-title">
            <strong>Advanced Sections</strong>
            <span>{advancedSections.length} groups</span>
          </div>
          <SectionList sections={advancedSections} emptyText="이 전략은 기본 입력만으로 실행됩니다." />
        </section>
      </div>
    </section>
  )
}

