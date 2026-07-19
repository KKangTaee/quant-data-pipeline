import React, { useEffect, useMemo, useState } from "react"
import { Streamlit } from "streamlit-component-lib"
import {
  BacktestAnalysisWorkspace,
  SettingsField,
  SingleSettingsWorkspace,
  WorkspaceIntent,
  WorkspaceSurface,
} from "./types"

function emitIntent(
  action: WorkspaceIntent["action"],
  payload: Record<string, unknown> = {},
) {
  Streamlit.setComponentValue({
    action,
    payload,
    nonce: `${Date.now()}-${Math.random()}`,
  })
}

function displayValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-"
  if (typeof value === "number") {
    return value.toLocaleString(undefined, { maximumFractionDigits: 3 })
  }
  return String(value)
}

function workspaceKindLabel(kind: string) {
  return kind === "portfolio_mix" ? "Portfolio Mix" : "Single Strategy"
}

type SettingsValues = Record<string, unknown>

function settingsIntentId(action: string) {
  return `${action}-${Date.now()}-${Math.random()}`
}

function emitSettingsIntent(
  action: "select_strategy_variant" | "run_single_strategy",
  workspace: SingleSettingsWorkspace,
  values: SettingsValues,
  variant: string | null = workspace.variant.value,
) {
  Streamlit.setComponentValue({
    action,
    intent_id: settingsIntentId(action),
    strategy_choice: workspace.strategy_choice,
    variant,
    values,
  })
}

function settingsInitialValues(workspace: SingleSettingsWorkspace) {
  return Object.fromEntries(
    workspace.sections.flatMap((section) =>
      section.fields.map((field) => [field.field_id, field.value]),
    ),
  )
}

function applyPresetProfile(
  workspace: SingleSettingsWorkspace,
  current: SettingsValues,
  fieldId: string,
  nextValue: unknown,
) {
  const next = { ...current, [fieldId]: nextValue }
  if (fieldId !== "preset_name" && fieldId !== "universe_mode") {
    return { values: next, sourceLabel: null }
  }
  if (fieldId === "universe_mode" && nextValue !== "preset") {
    return { values: next, sourceLabel: null }
  }
  const presetName = String(
    fieldId === "preset_name" ? nextValue : next.preset_name ?? "",
  )
  const profile = workspace.preset_profiles[presetName]
  if (!profile) return { values: next, sourceLabel: null }
  return {
    values: { ...next, ...profile.values },
    sourceLabel: profile.source_label,
  }
}

function optionLabel(field: SettingsField, value: unknown) {
  return (
    field.options?.find((option) => option.value === value)?.label ?? String(value)
  )
}

function optionFromString(field: SettingsField, value: string) {
  return field.options?.find((option) => String(option.value) === value)?.value ?? value
}

const MULTI_SELECT_COMPACT_LIMIT = 20
const MULTI_SELECT_RESULT_LIMIT = 100

function optionIdentity(value: unknown) {
  return String(value)
}

function normalizeMultiSelectValues(field: SettingsField, values: unknown[]) {
  const selected = new Set(values.map(optionIdentity))
  return (field.options ?? [])
    .filter((option) => selected.has(optionIdentity(option.value)))
    .map((option) => option.value)
}

function MultiSelectFieldControl({
  field,
  value,
  onChange,
  inputId,
}: {
  field: SettingsField
  value: unknown
  onChange: (value: unknown) => void
  inputId: string
}) {
  const options = field.options ?? []
  const selectedValues = Array.isArray(value) ? value : []
  const selectedKeys = new Set(selectedValues.map(optionIdentity))
  const [query, setQuery] = useState("")
  const normalizedQuery = query.trim().toLocaleLowerCase()
  const filteredOptions = options.filter((option) => {
    if (!normalizedQuery) return true
    return `${option.label} ${String(option.value)}`
      .toLocaleLowerCase()
      .includes(normalizedQuery)
  })
  const visibleOptions = filteredOptions.slice(0, MULTI_SELECT_RESULT_LIMIT)
  const remainingCount = Math.max(0, filteredOptions.length - visibleOptions.length)

  const toggleValue = (nextValue: unknown) => {
    const key = optionIdentity(nextValue)
    const next = selectedKeys.has(key)
      ? selectedValues.filter((item) => optionIdentity(item) !== key)
      : [...selectedValues, nextValue]
    onChange(normalizeMultiSelectValues(field, next))
  }
  const clearSelection = () => onChange([])

  if (options.length <= MULTI_SELECT_COMPACT_LIMIT) {
    return (
      <div
        className="bt1-settings-multi-select"
        id={inputId}
        role="group"
        aria-label={field.label}
      >
        <div className="bt1-multi-select-toolbar">
          <button
            type="button"
            onClick={() => onChange(options.map((option) => option.value))}
          >
            전체 선택
          </button>
          <button type="button" onClick={clearSelection}>
            선택 해제
          </button>
        </div>
        <div className="bt1-multi-select-compact">
          {options.map((option) => {
            const selected = selectedKeys.has(optionIdentity(option.value))
            return (
              <button
                type="button"
                className={selected ? "is-selected" : ""}
                aria-pressed={selected}
                key={optionIdentity(option.value)}
                onClick={() => toggleValue(option.value)}
              >
                <span aria-hidden="true">{selected ? "✓" : ""}</span>
                <span className="bt1-multi-select-option-label">
                  {option.label}
                </span>
              </button>
            )
          })}
        </div>
      </div>
    )
  }

  const addFilteredOptions = () =>
    onChange(
      normalizeMultiSelectValues(field, [
        ...selectedValues,
        ...filteredOptions.map((option) => option.value),
      ]),
    )

  return (
    <div className="bt1-settings-multi-select" id={inputId}>
      <div className="bt1-multi-select-search">
        <input
          type="search"
          value={query}
          aria-label={`${field.label} 검색`}
          placeholder="종목 또는 값을 검색"
          onChange={(event) => setQuery(event.target.value)}
        />
        <div className="bt1-selected-chip-shelf" aria-label="현재 선택">
          {selectedValues.map((item) => (
            <button
              type="button"
              className="bt1-selected-chip"
              aria-label={`${optionLabel(field, item)} 선택 해제`}
              key={optionIdentity(item)}
              onClick={() => toggleValue(item)}
            >
              {optionLabel(field, item)} <span aria-hidden="true">×</span>
            </button>
          ))}
        </div>
        <div className="bt1-multi-select-toolbar">
          <button type="button" onClick={addFilteredOptions}>
            검색 결과 전체 선택
          </button>
          <button type="button" onClick={clearSelection}>
            선택 해제
          </button>
        </div>
        <div
          className="bt1-multi-select-results"
          role="group"
          aria-label={`${field.label} 옵션`}
        >
          {visibleOptions.map((option) => {
            const selected = selectedKeys.has(optionIdentity(option.value))
            return (
              <button
                type="button"
                role="checkbox"
                aria-checked={selected}
                className={selected ? "is-selected" : ""}
                key={optionIdentity(option.value)}
                onClick={() => toggleValue(option.value)}
              >
                <span aria-hidden="true">{selected ? "✓" : ""}</span>
                <span className="bt1-multi-select-option-label">
                  {option.label}
                </span>
              </button>
            )
          })}
        </div>
        {remainingCount > 0 && (
          <small>검색 결과 {remainingCount}개가 더 있습니다.</small>
        )}
      </div>
    </div>
  )
}

function isSettingsFieldVisible(field: SettingsField, values: SettingsValues) {
  return Object.entries(field.visible_when ?? {}).every(
    ([dependency, expected]) => values[dependency] === expected,
  )
}

function SettingsFieldControl({
  field,
  value,
  onChange,
  error,
  applicationNotice,
}: {
  field: SettingsField
  value: unknown
  onChange: (value: unknown) => void
  error?: string
  applicationNotice?: string | null
}) {
  const inputId = `bt1-setting-${field.field_id}`
  let control: React.ReactNode
  switch (field.control) {
    case "date":
      control = (
        <input
          id={inputId}
          type="date"
          value={String(value ?? "")}
          onChange={(event) => onChange(event.target.value)}
        />
      )
      break
    case "number":
      control = (
        <input
          id={inputId}
          type="number"
          value={typeof value === "number" ? value : ""}
          min={field.min}
          max={field.max}
          step={field.step ?? "any"}
          onChange={(event) =>
            onChange(event.target.value === "" ? null : event.target.valueAsNumber)
          }
        />
      )
      break
    case "text":
      control = (
        <input
          id={inputId}
          type="text"
          value={String(value ?? "")}
          onChange={(event) => onChange(event.target.value)}
        />
      )
      break
    case "single_select":
      control = (
        <select
          id={inputId}
          value={String(value ?? "")}
          onChange={(event) => onChange(optionFromString(field, event.target.value))}
        >
          {(field.options ?? []).map((option) => (
            <option key={String(option.value)} value={String(option.value)}>
              {option.label}
            </option>
          ))}
        </select>
      )
      break
    case "multi_select":
      control = (
        <MultiSelectFieldControl
          field={field}
          value={value}
          onChange={onChange}
          inputId={inputId}
        />
      )
      break
    case "segmented":
      control = (
        <div className="bt1-settings-segmented" id={inputId}>
          {(field.options ?? []).map((option) => (
            <button
              type="button"
              className={option.value === value ? "is-selected" : ""}
              aria-pressed={option.value === value}
              key={String(option.value)}
              onClick={() => onChange(option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
      )
      break
    case "toggle":
      control = (
        <button
          id={inputId}
          type="button"
          className={`bt1-settings-toggle ${value === true ? "is-on" : ""}`}
          aria-pressed={value === true}
          onClick={() => onChange(value !== true)}
        >
          <span aria-hidden="true" />
          {value === true ? "사용" : "사용 안 함"}
        </button>
      )
      break
  }

  return (
    <div
      className={`bt1-settings-field ${field.wide ? "is-wide" : ""} ${
        error ? "has-error" : ""
      }`}
    >
      <label
        htmlFor={
          field.control === "segmented" || field.control === "multi_select"
            ? undefined
            : inputId
        }
      >
        {field.label}
        {field.required && <span className="bt1-required">필수</span>}
      </label>
      {control}
      {field.help && <small>{field.help}</small>}
      {field.control === "multi_select" && Array.isArray(value) && (
        <small className="bt1-settings-selection-summary">
          {value.length}개 선택 · {value.slice(0, 5).map((item) => optionLabel(field, item)).join(", ")}
        </small>
      )}
      {applicationNotice && (
        <p className="bt1-settings-application-notice" role="status">
          {applicationNotice}
        </p>
      )}
      {error && <p className="bt1-settings-field-error">{error}</p>}
    </div>
  )
}

function SingleSettingsEditor({ workspace }: { workspace: SingleSettingsWorkspace }) {
  const initialValues = useMemo(
    () => settingsInitialValues(workspace),
    [workspace.draft_key],
  )
  const [values, setValues] = useState<SettingsValues>(initialValues)
  const [pending, setPending] = useState(false)
  const [presetApplication, setPresetApplication] = useState<string | null>(null)

  useEffect(() => {
    setValues(initialValues)
    setPending(false)
    setPresetApplication(null)
  }, [workspace.draft_key, initialValues])

  useEffect(() => {
    setPending(false)
  }, [workspace.validation_errors])

  const setFieldValue = (fieldId: string, nextValue: unknown) => {
    const applied = applyPresetProfile(workspace, values, fieldId, nextValue)
    setValues(applied.values)
    setPresetApplication(applied.sourceLabel)
  }

  return (
    <main className="bt1-workspace bt1-settings-workspace" data-surface="settings">
      <header className="bt1-settings-profile">
        <p className="bt1-kicker">현재 설정 대상</p>
        <h1>{workspace.profile.display_name}</h1>
        <div className="bt1-settings-badges">
          <span>{workspace.profile.purpose_label}</span>
          <span>{workspace.profile.maturity_label}</span>
        </div>
        <p>{workspace.profile.description}</p>
        {workspace.variant.options.length > 0 && (
          <div className="bt1-settings-variant" aria-label="실행 기준">
            {workspace.variant.options.map((option) => (
              <button
                type="button"
                className={option.value === workspace.variant.value ? "is-selected" : ""}
                aria-pressed={option.value === workspace.variant.value}
                key={String(option.value)}
                onClick={() =>
                  emitSettingsIntent(
                    "select_strategy_variant",
                    workspace,
                    values,
                    String(option.value),
                  )
                }
              >
                {option.label}
              </button>
            ))}
          </div>
        )}
      </header>

      <div className="bt1-settings-sections">
        {workspace.sections.map((section) => {
          const visibleFields = section.fields.filter((field) =>
            isSettingsFieldVisible(field, values),
          )
          const primaryFields = visibleFields.filter((field) => !field.advanced)
          const advancedFields = visibleFields.filter((field) => field.advanced)
          return (
            <section className="bt1-settings-section" key={section.section_id}>
              <div className="bt1-settings-section-heading">
                <h2>{section.title}</h2>
                <p>{section.description}</p>
              </div>
              <div className="bt1-settings-grid">
                {primaryFields.map((field) => (
                  <SettingsFieldControl
                    field={field}
                    value={values[field.field_id]}
                    error={workspace.validation_errors[field.field_id]}
                    applicationNotice={
                      field.field_id === "preset_name" ? presetApplication : null
                    }
                    key={field.field_id}
                    onChange={(nextValue) => setFieldValue(field.field_id, nextValue)}
                  />
                ))}
              </div>
              {advancedFields.length > 0 && (
                <details className="bt1-settings-disclosure">
                  <summary>고급 설정과 기술 근거</summary>
                  <div className="bt1-settings-grid">
                    {advancedFields.map((field) => (
                      <SettingsFieldControl
                        field={field}
                        value={values[field.field_id]}
                        error={workspace.validation_errors[field.field_id]}
                        applicationNotice={
                          field.field_id === "preset_name"
                            ? presetApplication
                            : null
                        }
                        key={field.field_id}
                        onChange={(nextValue) => setFieldValue(field.field_id, nextValue)}
                      />
                    ))}
                  </div>
                </details>
              )}
            </section>
          )
        })}
      </div>

      <aside className="bt1-settings-rule-summary">
        <div>
          <strong>어떻게 선택하나요?</strong>
          <span>{workspace.profile.selection_rule}</span>
        </div>
        <div>
          <strong>어떻게 보유하나요?</strong>
          <span>{workspace.profile.holding_rule}</span>
        </div>
        <div>
          <strong>무엇을 주의하나요?</strong>
          <span>{workspace.profile.risk_note}</span>
        </div>
      </aside>

      <button
        type="button"
        className="bt1-action-button bt1-settings-submit"
        disabled={pending || workspace.action.enabled !== true}
        onClick={() => {
          setPending(true)
          emitSettingsIntent("run_single_strategy", workspace, values)
        }}
      >
        {pending ? "실행 요청 중…" : workspace.action.label}
      </button>
    </main>
  )
}

function AnalysisDecisionSurfaces({
  workspace,
  surface,
}: {
  workspace: BacktestAnalysisWorkspace
  surface: WorkspaceSurface
}) {
  const saveAndMove = workspace.actions.save_and_move
  const saveMix = workspace.actions.save_mix
  const [mixName, setMixName] = useState("")
  const [mixDescription, setMixDescription] = useState("")
  const configurationRows = Object.entries(workspace.configuration_summary).slice(
    0,
    6,
  )

  return (
    <main className="bt1-workspace" data-surface={surface}>
      {surface === "context" && (
        <>
          <header className="bt1-header">
            <p className="bt1-kicker">Backtest Analysis Decision Workspace</p>
            <h1>{workspace.header.question}</h1>
            <p>
              후보 유형과 목적을 고정하고 필요한 설정만 입력한 뒤, 실행 결과를
              Level2 검증 준비 상태로 해석합니다.
            </p>
          </header>

          <section className="bt1-step">
            <div className="bt1-step-heading">
              <span>1</span>
              <div>
                <h2>어떤 후보를 만들까요?</h2>
                <p>단일 전략과 Portfolio Mix는 서로 다른 설정 흐름을 사용합니다.</p>
              </div>
            </div>
            <div className="bt1-entry-grid">
              {[
                {
                  id: "single_strategy",
                  title: "Single Strategy",
                  detail: "하나의 전략을 설정하고 결과를 검증 후보로 준비합니다.",
                },
                {
                  id: "portfolio_mix",
                  title: "Portfolio Mix",
                  detail: "여러 전략의 역할과 비중을 조합해 후보를 만듭니다.",
                },
              ].map((item) => (
                <button
                  type="button"
                  className={
                    workspace.workspace_kind === item.id ? "is-selected" : ""
                  }
                  aria-pressed={workspace.workspace_kind === item.id}
                  key={item.id}
                  onClick={() =>
                    emitIntent("select_workspace_kind", {
                      workspace_kind: item.id,
                    })
                  }
                >
                  <strong>{item.title}</strong>
                  <span>{item.detail}</span>
                </button>
              ))}
            </div>
          </section>

          <section className="bt1-step">
            <div className="bt1-step-heading">
              <span>2</span>
              <div>
                <h2>목적과 핵심 설정</h2>
                <p>현재 후보를 유지하면서 목적별 전략과 설정을 확인합니다.</p>
              </div>
            </div>
            {workspace.workspace_kind === "portfolio_mix" && (
              <aside className="bt1-current-work">
                <span>현재 작업</span>
                <strong>{workspace.current_work.title}</strong>
                <small>{workspaceKindLabel(workspace.current_work.workspace_kind)}</small>
              </aside>
            )}
            {workspace.workspace_kind === "single_strategy" && (
              <div className="bt1-purpose-grid">
                {workspace.strategy_catalog.map((group) => (
                  <article key={group.group_id}>
                    <h3>{group.label}</h3>
                    <div>
                      {group.items.map((item) => (
                        <button
                          type="button"
                          className={
                            workspace.current_work.title === item.strategy_choice
                              ? "is-selected"
                              : ""
                          }
                          key={item.strategy_choice}
                          onClick={() =>
                            emitIntent("select_strategy", {
                              strategy_choice: item.strategy_choice,
                            })
                          }
                        >
                          <strong>{item.strategy_choice}</strong>
                          {item.maturity === "development" && <span>개발 중</span>}
                        </button>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            )}
            {workspace.workspace_kind === "portfolio_mix" && (
              <div className="bt1-mix-entry">
                <div className="bt1-entry-grid">
                  <button
                    type="button"
                    className={
                      workspace.mix?.saved_entry_mode === "new"
                        ? "is-selected"
                        : ""
                    }
                    onClick={() => emitIntent("select_mix_mode", { mix_mode: "new" })}
                  >
                    <strong>새 Mix 만들기</strong>
                    <span>구성 전략을 실행한 뒤 역할과 비중을 새로 정합니다.</span>
                  </button>
                  <button
                    type="button"
                    className={
                      workspace.mix?.saved_entry_mode === "saved"
                        ? "is-selected"
                        : ""
                    }
                    onClick={() => emitIntent("select_mix_mode", { mix_mode: "saved" })}
                  >
                    <strong>저장된 Mix 불러오기</strong>
                    <span>재사용 가능한 저장 setup을 골라 이어서 검토합니다.</span>
                  </button>
                </div>
                {workspace.mix?.role_weight_rows.length ? (
                  <div className="bt1-mix-summary">
                    {workspace.mix.role_weight_rows.map((row) => (
                      <article key={`${row.strategy_name}-${row.role}`}>
                        <strong>{row.strategy_name}</strong>
                        <span>{row.role_label}</span>
                        <span>{displayValue(row.weight_percent)}%</span>
                      </article>
                    ))}
                    <p>총 비중 {displayValue(workspace.mix.total_weight_percent)}%</p>
                  </div>
                ) : null}
                {workspace.mix?.saved_entry_mode === "saved" &&
                  workspace.saved_mixes.length > 0 && (
                    <div className="bt1-saved-mix-list">
                      {workspace.saved_mixes.slice(0, 6).map((item, index) => (
                        <article key={String(item.portfolio_id ?? index)}>
                          <strong>{displayValue(item.name)}</strong>
                          <span>
                            {Array.isArray(item.strategy_names)
                              ? item.strategy_names.join(" · ")
                              : "-"}
                          </span>
                          <small>{displayValue(item.updated_at)}</small>
                        </article>
                      ))}
                    </div>
                  )}
              </div>
            )}
            {configurationRows.length > 0 && (
              <dl className="bt1-configuration-summary">
                {configurationRows.map(([key, value]) => (
                  <div key={key}>
                    <dt>{key}</dt>
                    <dd>{displayValue(value)}</dd>
                  </div>
                ))}
              </dl>
            )}
          </section>
        </>
      )}

      {surface === "decision" && (
        <>
          <section className="bt1-step bt1-decision">
            <div className="bt1-step-heading">
              <span>3</span>
              <div>
                <h2>실행 결과를 어떻게 판단할까요?</h2>
                <p>성과보다 후보 준비 상태와 남은 행동을 먼저 확인합니다.</p>
              </div>
            </div>
            <div className={`bt1-verdict bt1-verdict-${workspace.handoff_state}`}>
              <span>
                {workspace.result_freshness === "stale"
                  ? "이전 설정 결과"
                  : workspace.strategy_maturity === "development"
                    ? "개발 중"
                    : "Level1 판단"}
              </span>
              <h2>{workspace.decision.headline}</h2>
              <p>{workspace.decision.summary}</p>
            </div>
            {workspace.error && (
              <div className="bt1-error" role="alert">
                <strong>실행을 완료하지 못했습니다</strong>
                <span>{workspace.error.message}</span>
              </div>
            )}
            {workspace.decision.metrics.length > 0 && (
              <dl className="bt1-metric-grid">
                {workspace.decision.metrics.map((metric) => (
                  <div key={metric.metric_id}>
                    <dt>{metric.label}</dt>
                    <dd>{displayValue(metric.value)}</dd>
                  </div>
                ))}
              </dl>
            )}
            {workspace.decision.reasons.length > 0 && (
              <div className="bt1-reason-grid">
                {workspace.decision.reasons.map((reason) => (
                  <article key={reason.root_issue_id}>{reason.message}</article>
                ))}
              </div>
            )}
          </section>

          {(saveMix?.enabled === true || saveAndMove?.enabled === true) && (
            <section className="bt1-step bt1-final-action">
              <div className="bt1-step-heading">
                <span>4</span>
                <div>
                  <h2>저장 또는 Level2 이동</h2>
                  <p>Mix setup 저장과 검증 후보 등록은 서로 다른 작업입니다.</p>
                </div>
              </div>
              {saveMix?.enabled === true && (
                <div className="bt1-save-mix-form">
                  <label>
                    <span>Mix 이름</span>
                    <input
                      value={mixName}
                      onChange={(event) => setMixName(event.target.value)}
                      placeholder="다시 찾기 쉬운 이름"
                    />
                  </label>
                  <label>
                    <span>메모</span>
                    <textarea
                      value={mixDescription}
                      onChange={(event) => setMixDescription(event.target.value)}
                      placeholder="저장 목적과 다시 볼 조건"
                    />
                  </label>
                  <button
                    type="button"
                    className="bt1-secondary-action-button"
                    onClick={() =>
                      emitIntent("save_mix", {
                        name: mixName,
                        description: mixDescription,
                      })
                    }
                  >
                    {saveMix.label}
                  </button>
                </div>
              )}
              {saveAndMove?.enabled === true && (
                <button
                  type="button"
                  className="bt1-action-button"
                  onClick={() => emitIntent("save_and_move")}
                >
                  {saveAndMove.label}
                </button>
              )}
            </section>
          )}
        </>
      )}
    </main>
  )
}

export function BacktestAnalysisDecisionWorkspace({
  workspace,
  surface,
}: {
  workspace: BacktestAnalysisWorkspace | SingleSettingsWorkspace
  surface: WorkspaceSurface
}) {
  if (surface === "settings") {
    return <SingleSettingsEditor workspace={workspace as SingleSettingsWorkspace} />
  }
  return (
    <AnalysisDecisionSurfaces
      workspace={workspace as BacktestAnalysisWorkspace}
      surface={surface}
    />
  )
}
