import React, { useMemo, useState } from "react"
import { Streamlit } from "streamlit-component-lib"
import { PortfolioMixResult, type MixResultEvidence } from "./PortfolioMixResult"

type Option = { value: unknown; label: string }
type Field = {
  field_id: string
  label: string
  control: "date" | "number" | "text" | "single_select" | "multi_select" | "segmented" | "toggle"
  value: unknown
  help?: string
  required?: boolean
  options?: Option[]
  min?: number
  max?: number
  step?: number
  visible_when?: Record<string, unknown>
}
type SettingsWorkspace = {
  profile: { display_name: string; description: string; selection_rule: string; holding_rule: string; risk_note: string }
  sections: Array<{ section_id: string; title: string; description: string; fields: Field[] }>
  preset_profiles: Record<string, { source_label: string; values: Record<string, unknown> }>
}
type ComponentCard = {
  component_id: string
  strategy_choice: string
  variant: string | null
  role: string
  role_label?: string
  weight_percent: number
  strategy_name: string
  purpose_label: string
  maturity: string
  settings_workspace?: SettingsWorkspace | null
  runtime_state: { status?: string; message?: string }
}
type CatalogItem = {
  strategy_choice: string
  label: string
  maturity: string
  maturity_label: string
  variants: Array<{ value: string | null; label: string }>
}
type Action = { id: string; label: string; enabled: boolean }
type CurrentResult = Record<string, unknown> & { evidence?: MixResultEvidence }

export type PortfolioMixWorkspace = {
  schema_version: string
  mode: "new" | "saved"
  draft: { shared: Record<string, unknown>; components: ComponentCard[] }
  catalog: {
    groups: Array<{ id: string; label: string; items: CatalogItem[] }>
    roles: Array<{ value: string; label: string }>
  }
  component_cards: ComponentCard[]
  allocation: { total_weight_percent: number; date_policy: string }
  validation: { valid: boolean; errors: Record<string, string>; issues: Array<{ root_issue_id: string; message: string }> }
  saved_mix: { rows: Array<{ id: string; name: string; saved_at: string; component_count: number; component_summary: string }>; empty: boolean }
  result: { status: "not_run" | "current" | "stale"; current: CurrentResult | null; reference: Record<string, unknown> | null }
  execution_action: Action | null
  actions: Action[]
  feedback?: { notice?: string; error?: { message?: string } | null }
}

const MULTI_SELECT_COMPACT_LIMIT = 12

function emit(id: string, payload: Record<string, unknown> = {}) {
  Streamlit.setComponentValue({
    event: { id, intent_id: `${id}-${Date.now()}-${Math.random()}`, payload },
  })
}

function StepHeading({ number, title, copy }: { number: number; title: string; copy: string }) {
  return (
    <header className="mix-step-heading">
      <span>{number}</span>
      <div><h2>{title}</h2><p>{copy}</p></div>
    </header>
  )
}

function optionValue(field: Field, raw: string) {
  return field.options?.find((option) => String(option.value) === raw)?.value ?? raw
}

function MultiSelectFieldControl({ field, send }: {
  field: Field
  send: (value: unknown) => void
}) {
  const [query, setQuery] = useState("")
  const options = field.options ?? []
  const selected = Array.isArray(field.value) ? field.value : []
  const selectedKeys = new Set(selected.map((value) => String(value)))
  const normalizedQuery = query.trim().toLocaleLowerCase()
  const filteredOptions = options.filter((option) =>
    `${option.label} ${String(option.value)}`
      .toLocaleLowerCase()
      .includes(normalizedQuery),
  )
  const toggle = (nextValue: unknown) => {
    const key = String(nextValue)
    send(
      selectedKeys.has(key)
        ? selected.filter((value) => String(value) !== key)
        : [...selected, nextValue],
    )
  }
  const optionButton = (option: Option) => {
    const active = selectedKeys.has(String(option.value))
    return (
      <button
        type="button"
        role="checkbox"
        aria-checked={active}
        key={String(option.value)}
        onClick={() => toggle(option.value)}
      >
        <span aria-hidden="true">{active ? "✓" : ""}</span>
        {option.label}
      </button>
    )
  }

  if (options.length <= MULTI_SELECT_COMPACT_LIMIT) {
    return (
      <div className="mix-checkbox-grid" role="group" aria-label={field.label}>
        {options.map(optionButton)}
      </div>
    )
  }

  return (
    <div className="mix-multi-select">
      <div
        className="mix-multi-selected-shelf"
        aria-label={`${field.label} 현재 선택`}
      >
        <strong>선택 {selected.length}개</strong>
        <div>
          {selected.map((value) => {
            const label = options.find(
              (option) => String(option.value) === String(value),
            )?.label ?? String(value)
            return (
              <button
                type="button"
                className="mix-multi-chip"
                aria-label={`${label} 선택 해제`}
                key={String(value)}
                onClick={() => toggle(value)}
              >
                {label} <span aria-hidden="true">×</span>
              </button>
            )
          })}
          {selected.length === 0 && <span>선택된 자산 없음</span>}
        </div>
      </div>
      <input
        className="mix-multi-search"
        type="search"
        value={query}
        aria-label={`${field.label} 검색`}
        placeholder="종목 또는 자산 검색"
        onChange={(event) => setQuery(event.currentTarget.value)}
      />
      <div
        className="mix-multi-select-scroll"
        role="group"
        aria-label={`${field.label} 옵션`}
      >
        {filteredOptions.length > 0 ? (
          filteredOptions.map(optionButton)
        ) : (
          <p className="mix-multi-empty">일치하는 옵션이 없습니다.</p>
        )}
      </div>
    </div>
  )
}

function FieldControl({ field, componentId }: { field: Field; componentId: string }) {
  const send = (value: unknown) => emit(
    field.field_id === "preset_name" ? "apply_preset" : "set_component_field",
    field.field_id === "preset_name"
      ? { component_id: componentId, preset_name: value }
      : { component_id: componentId, field_id: field.field_id, value },
  )
  if (field.control === "toggle") {
    return <button type="button" className="mix-toggle" aria-pressed={field.value === true} onClick={() => send(field.value !== true)}>{field.value === true ? "사용" : "사용 안 함"}</button>
  }
  if (field.control === "segmented") {
    return <div className="mix-segmented">{(field.options ?? []).map((option) => <button type="button" key={String(option.value)} aria-pressed={option.value === field.value} onClick={() => send(option.value)}>{option.label}</button>)}</div>
  }
  if (field.control === "multi_select") {
    return <MultiSelectFieldControl field={field} send={send} />
  }
  if (field.control === "single_select") {
    return <select value={String(field.value ?? "")} onChange={(event) => send(optionValue(field, event.target.value))}>{(field.options ?? []).map((option) => <option key={String(option.value)} value={String(option.value)}>{option.label}</option>)}</select>
  }
  if (field.control === "text") {
    return <input type="text" value={String(field.value ?? "")} onChange={(event) => send(event.currentTarget.value)} />
  }
  return <input
    type={field.control === "date" ? "date" : "number"}
    value={String(field.value ?? "")}
    min={field.min}
    max={field.max}
    step={field.step}
    onChange={(event) => send(field.control === "number" ? event.currentTarget.valueAsNumber : event.currentTarget.value)}
  />
}

function ComponentEditor({ card, workspace }: { card: ComponentCard; workspace: PortfolioMixWorkspace }) {
  const values = useMemo(() => Object.fromEntries((card.settings_workspace?.sections ?? []).flatMap((section) => section.fields.map((field) => [field.field_id, field.value]))), [card.settings_workspace])
  const items = workspace.catalog.groups.flatMap((group) => group.items)
  const selectedItem = items.find((item) => item.strategy_choice === card.strategy_choice)
  return (
    <article className="mix-component-card">
      <div className="mix-component-head">
        <div><small>{card.purpose_label} · {card.maturity === "development" ? "개발 중" : "운영 전략"}</small><h3>{card.strategy_name}</h3></div>
        <button type="button" className="mix-quiet" disabled={workspace.component_cards.length <= 2} onClick={() => emit("remove_component", { component_id: card.component_id })}>제거</button>
      </div>
      <div className="mix-field-grid">
        <label>전략<select value={card.strategy_choice} onChange={(event) => emit("set_strategy", { component_id: card.component_id, value: event.target.value })}>{items.map((item) => <option key={item.strategy_choice} value={item.strategy_choice}>{item.label}</option>)}</select></label>
        {(selectedItem?.variants.length ?? 0) > 0 && <label>실행 기준<select value={card.variant ?? ""} onChange={(event) => emit("set_variant", { component_id: card.component_id, value: event.target.value })}>{selectedItem?.variants.map((variant) => <option key={String(variant.value)} value={String(variant.value)}>{variant.label}</option>)}</select></label>}
      </div>
      <details className="mix-details">
        <summary>세부 설정</summary>
        {(card.settings_workspace?.sections ?? []).map((section) => <section key={section.section_id} className="mix-settings-section"><h4>{section.title}</h4><p>{section.description}</p><div className="mix-field-grid">{section.fields.filter((field) => Object.entries(field.visible_when ?? {}).every(([key, expected]) => values[key] === expected)).map((field) => <label key={field.field_id}>{field.label}{field.required && <small>필수</small>}<FieldControl field={field} componentId={card.component_id} />{field.help && <span>{field.help}</span>}</label>)}</div></section>)}
      </details>
      {card.runtime_state?.status && card.runtime_state.status !== "idle" && <p className="mix-runtime" aria-live="polite">{card.runtime_state.message || card.runtime_state.status}</p>}
    </article>
  )
}

function App({ workspace }: { workspace: PortfolioMixWorkspace }) {
  const [saveName, setSaveName] = useState("")
  const allItems = workspace.catalog.groups.flatMap((group) => group.items)
  const selected = new Set(workspace.component_cards.map((card) => card.strategy_choice))
  const shared = workspace.draft.shared
  const chooseMode = (next: "new" | "saved") => emit("set_mode", { value: next })
  return (
    <main className="mix-workspace">
      <header className="mix-hero"><p className="mix-kicker">PORTFOLIO MIX DECISION WORKSPACE</p><h1>서로 다른 전략을 어떤 역할과 비중으로 함께 운용할까요?</h1><p>구성별 설정을 검증하고 같은 기간으로 실행한 뒤, Mix 전체를 하나의 Level1 후보로 판단합니다.</p></header>

      <section className="mix-step">
        <StepHeading number={1} title="구성 전략과 공통 기준" copy="전략별 preset과 공통 실행 기간을 먼저 고정합니다." />
        <div className="mix-mode" role="group" aria-label="Mix 시작 방식"><button type="button" aria-pressed={workspace.mode === "new"} onClick={() => chooseMode("new")}>새 Mix 만들기</button><button type="button" aria-pressed={workspace.mode === "saved"} onClick={() => chooseMode("saved")}>저장된 Mix 불러오기</button></div>
        {workspace.mode === "saved" ? <div className="mix-saved-shelf">{workspace.saved_mix.empty ? <p>저장된 Mix가 아직 없습니다. 새 Mix를 만든 뒤 저장할 수 있습니다.</p> : workspace.saved_mix.rows.map((row) => <article key={row.id}><h3>{row.name}</h3><p>{row.component_summary}</p><small>{row.saved_at}</small><div><button type="button" onClick={() => emit("restore_saved_mix", { saved_mix_id: row.id })}>불러와 편집</button><button type="button" onClick={() => emit("run_saved_mix", { saved_mix_id: row.id })}>현재 데이터로 실행</button></div></article>)}</div> : <>
          <div className="mix-shared-grid">
            <label>시작일<input type="date" value={String(shared.start ?? "")} onChange={(event) => emit("set_shared_field", { field_id: "start", value: event.target.value })} /></label>
            <label>종료일<input type="date" value={String(shared.end ?? "")} onChange={(event) => emit("set_shared_field", { field_id: "end", value: event.target.value })} /></label>
            <label>데이터 주기<select value={String(shared.timeframe ?? "1d")} onChange={(event) => emit("set_shared_field", { field_id: "timeframe", value: event.target.value })}><option value="1d">일별</option></select></label>
            <label>신호 기준<select value={String(shared.option ?? "month_end")} onChange={(event) => emit("set_shared_field", { field_id: "option", value: event.target.value })}><option value="month_end">월말</option><option value="close_based">종가 기준</option></select></label>
          </div>
          <div className="mix-component-grid">{workspace.component_cards.map((card) => <ComponentEditor key={card.component_id} card={card} workspace={workspace} />)}</div>
          {workspace.component_cards.length < 4 && <div className="mix-add-board"><h3>구성 전략 추가</h3>{workspace.catalog.groups.map((group) => <div key={group.id}><strong>{group.label}</strong><div>{group.items.map((item) => <button type="button" key={item.strategy_choice} disabled={selected.has(item.strategy_choice)} onClick={() => emit("add_component", { strategy_choice: item.strategy_choice, variant: item.variants[0]?.value ?? null })}>{item.label}</button>)}</div></div>)}</div>}
        </>}
      </section>

      <section className="mix-step">
        <StepHeading number={2} title="역할과 목표 비중" copy="각 전략의 책임을 정하고 목표 비중 합계 100%를 확인합니다." />
        <div className="mix-allocation-grid">{workspace.component_cards.map((card) => <article key={card.component_id}><strong>{card.strategy_name}</strong><label>역할<select value={card.role} onChange={(event) => emit("set_role", { component_id: card.component_id, value: event.target.value })}>{workspace.catalog.roles.map((role) => <option key={role.value} value={role.value}>{role.label}</option>)}</select></label><label>목표 비중 (%)<input type="number" min={0} max={100} step={1} value={card.weight_percent} onChange={(event) => emit("set_weight", { component_id: card.component_id, value: event.currentTarget.valueAsNumber })} /></label></article>)}</div>
        <div className={`mix-total ${workspace.validation.valid ? "is-valid" : ""}`}><span>목표 비중 합계</span><strong>{workspace.allocation.total_weight_percent}%</strong><small>날짜 정렬: {workspace.allocation.date_policy === "intersection" ? "공통 기간만 사용" : "전체 기간 사용"}</small></div>
        {workspace.validation.issues.length > 0 && <div className="mix-issues" aria-live="polite">{workspace.validation.issues.map((issue) => <p key={issue.root_issue_id}>{issue.message}</p>)}</div>}
      </section>

      <section className="mix-step">
        <StepHeading number={3} title="Mix 실행과 해석" copy="구성 전략을 같은 조건으로 계산한 뒤 Mix 전체 결과를 확인합니다." />
        {workspace.execution_action?.enabled && <button type="button" className="mix-primary" onClick={() => emit("run_mix")}>{workspace.execution_action.label}</button>}
        <div className="mix-result-shell">
          {workspace.result.status === "not_run" && <p className="mix-empty">설정을 완료한 뒤 실행하면 결과 해석이 이곳에 나타납니다.</p>}
          {workspace.result.status === "stale" && <div className="mix-reference"><strong>참고용 이전 결과</strong><p>현재 설정과 다르므로 다시 실행해야 저장하거나 Level2로 넘길 수 있습니다.</p></div>}
          {workspace.feedback?.error?.message && <p className="mix-error" role="alert">{workspace.feedback.error.message}</p>}
          {workspace.feedback?.notice && <p className="mix-notice" aria-live="polite">{workspace.feedback.notice}</p>}
          {workspace.result.status === "current" && workspace.result.current?.evidence && <div className="mix-current" aria-live="polite"><PortfolioMixResult evidence={workspace.result.current.evidence} /></div>}
          {workspace.result.status === "current" && !workspace.result.current?.evidence && <p className="mix-empty">현재 결과의 상세 근거를 표시할 수 없습니다. 같은 설정으로 다시 실행해 주세요.</p>}
        </div>
      </section>

      <section className="mix-step">
        <StepHeading number={4} title="저장하고 Level2로 이동" copy="재사용할 설정 저장과 검증 후보 등록을 서로 다른 작업으로 처리합니다." />
        {workspace.actions.length === 0 ? <p className="mix-empty">현재 설정과 일치하는 실행 결과가 준비되면 가능한 작업이 나타납니다.</p> : <div className="mix-action-board"><label>Mix 이름<input type="text" value={saveName} placeholder="예: 균형형 코어 Mix" onChange={(event) => setSaveName(event.currentTarget.value)} /></label><div className="mix-actions">{workspace.actions.map((action) => <button type="button" className="mix-primary" key={action.id} disabled={!action.enabled} onClick={() => emit(action.id, saveName.trim() ? { name: saveName.trim() } : {})}>{action.label}</button>)}</div></div>}
      </section>
    </main>
  )
}

export default App
