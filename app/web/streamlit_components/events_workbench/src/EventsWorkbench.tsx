import React, { useEffect, useState } from "react";
import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import "./style.css";

type EventBadge = {
  label: string;
  kind: string;
};

type EventItem = {
  date: string;
  days_until?: number | null;
  type: string;
  family: string;
  symbol?: string;
  title: string;
  importance?: string;
  validation?: string;
  freshness?: string;
  source_authority?: string;
  universe_scope?: string;
  source_type?: string;
  source_url?: string;
  confidence?: unknown;
  collected_at?: string;
  event_time?: string;
  needs_review?: boolean;
  badges?: EventBadge[];
};

type EventRail = {
  key: string;
  label: string;
  count: number;
  review_count: number;
  items: EventItem[];
};

type RailTabs = {
  default_key?: string;
  empty_text?: string;
  tabs?: EventRail[];
};

type EventAction = {
  id: string;
  label: string;
  kind?: string;
  detail?: string;
};

type EventFilterOption = {
  id: string;
  label: string;
};

type EventFilterPayload = {
  label?: string;
  options?: EventFilterOption[];
};

type CommandResult = {
  key?: string;
  label?: string;
  status?: string;
  message?: string;
  rows_written?: number | null;
  events_found?: number | null;
  source?: string | null;
  method?: string | null;
  duration_sec?: number | null;
  jobs_run?: number | null;
  jobs_failed?: number | null;
  finished_at?: string | null;
  sub_results?: { label?: string; status?: string; message?: string }[];
};

type TrustSection = {
  key: string;
  label: string;
  count: number;
  items: EventItem[];
};

type TrustReview = {
  eyebrow?: string;
  title?: string;
  description?: string;
  official_count?: number;
  provider_estimate_count?: number;
  estimate_only_count?: number;
  cross_checked_count?: number;
  not_confirmed_count?: number;
  stale_estimate_count?: number;
  conflict_count?: number;
  warnings?: string[];
  sections?: TrustSection[];
  source_boundary?: string;
};

type CalendarDay = {
  date: string;
  count: number;
  review_count: number;
  stale_count: number;
  by_family?: Record<string, number>;
  top_titles?: string[];
  items?: EventItem[];
};

type DensityBucket = {
  week_start: string;
  count: number;
  review_count: number;
  stale_count: number;
  by_family?: Record<string, number>;
};

type EvidencePayload = {
  raw_fields?: string[];
  rows?: Record<string, unknown>[];
  row_count?: number;
};

type EventsPayload = {
  schema_version?: string;
  status?: string;
  brief?: {
    title?: string;
    boundary_note?: string;
    next_event?: EventItem | null;
    counts?: Record<string, number>;
    source_summary?: Record<string, number>;
    freshness_summary?: {
      latest_collected_at?: string | null;
      stale_estimate_count?: number;
      has_stale_estimates?: boolean;
      warning_count?: number;
    };
    family_counts?: Record<string, number>;
  };
  rails?: EventRail[];
  rail_tabs?: RailTabs;
  filters?: {
    family?: EventFilterPayload;
    source_state?: EventFilterPayload;
  };
  trust_review?: TrustReview;
  command?: {
    title?: string;
    refresh_boundary?: string;
    actions?: EventAction[];
    earnings_universe?: {
      label?: string;
      description?: string;
      top_movers_limit?: number;
      max_symbols?: number;
      lookahead_days?: number;
      cross_check?: string;
    };
    last_results?: CommandResult[];
  };
  calendar?: {
    today?: string;
    current_week_start?: string;
    current_week_end?: string;
    weekday_labels?: string[];
    days?: CalendarDay[];
    density?: DensityBucket[];
  };
  evidence?: EvidencePayload;
};

const FAMILY_OPTIONS = [
  { id: "all", label: "전체" },
  { id: "central_bank", label: "FOMC" },
  { id: "macro", label: "매크로" },
  { id: "earnings", label: "실적" },
  { id: "market_structure", label: "시장 구조" },
];

const REVIEW_OPTIONS = [
  { id: "all", label: "전체" },
  { id: "review", label: "확인 필요" },
  { id: "official", label: "공식 / 확인됨" },
  { id: "estimate", label: "추정 / 미확정" },
];

function valueText(value: unknown, fallback = "-"): string {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}

function normalizedText(value: unknown): string {
  return valueText(value, "").trim().toLowerCase();
}

function cssToken(value: unknown): string {
  return normalizedText(value).replace(/[^a-z0-9_-]+/g, "_") || "unknown";
}

function familyLabel(value: unknown): string {
  const family = normalizedText(value);
  if (family === "central_bank") {
    return "FOMC";
  }
  if (family === "market_structure") {
    return "시장 구조";
  }
  if (family === "fixed_income") {
    return "국채 / 금리";
  }
  if (family === "macro") {
    return "매크로";
  }
  if (family === "earnings") {
    return "실적";
  }
  return valueText(value, "미분류").replace(/_/g, " ");
}

function familyTone(value: unknown): string {
  const family = normalizedText(value);
  if (family === "central_bank") {
    return "fomc";
  }
  if (family === "market_structure") {
    return "structure";
  }
  if (family === "fixed_income") {
    return "macro";
  }
  return cssToken(family);
}

function matchesFamily(item: EventItem, familyFilter: string): boolean {
  if (familyFilter === "all") {
    return true;
  }
  const family = normalizedText(item.family);
  const type = normalizedText(item.type);
  if (familyFilter === "central_bank") {
    return family === "central_bank" || type.includes("fomc");
  }
  if (familyFilter === "macro") {
    return family === "macro" || family === "fixed_income" || type.startsWith("macro") || type.startsWith("treasury");
  }
  return family === familyFilter;
}

function matchesReviewState(item: EventItem, reviewFilter: string): boolean {
  if (reviewFilter === "all") {
    return true;
  }
  const authority = normalizedText(item.source_authority);
  const validation = normalizedText(item.validation);
  if (reviewFilter === "review") {
    return Boolean(item.needs_review);
  }
  if (reviewFilter === "official") {
    return ["official", "issuer_confirmed", "cross_checked"].includes(authority) || validation === "official";
  }
  if (reviewFilter === "estimate") {
    return (
      authority.includes("estimate") ||
      authority.includes("not_confirmed") ||
      ["estimate only", "not confirmed", "conflict"].includes(validation)
    );
  }
  return true;
}

function filterItems(items: EventItem[], familyFilter: string, reviewFilter: string): EventItem[] {
  return items.filter((item) => matchesFamily(item, familyFilter) && matchesReviewState(item, reviewFilter));
}

function aggregateFamilies(items: EventItem[]): Record<string, number> {
  return items.reduce<Record<string, number>>((acc, item) => {
    const family = item.family || "unknown";
    acc[family] = (acc[family] || 0) + 1;
    return acc;
  }, {});
}

function weekMatchesFilter(bucket: DensityBucket, familyFilter: string, reviewFilter: string): boolean {
  if (reviewFilter === "review" && !bucket.review_count) {
    return false;
  }
  if (reviewFilter === "estimate" && !bucket.review_count && !bucket.stale_count) {
    return false;
  }
  if (familyFilter === "all") {
    return true;
  }
  const families = bucket.by_family || {};
  if (familyFilter === "macro") {
    return Boolean(families.macro || families.fixed_income);
  }
  return Boolean(families[familyFilter]);
}

function parseDateParts(dateText: string): { year: number; month: number; day: number } | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateText || "");
  if (!match) {
    return null;
  }
  return {
    year: Number(match[1]),
    month: Number(match[2]),
    day: Number(match[3]),
  };
}

function dateFromText(dateText: string): Date | null {
  const parts = parseDateParts(dateText);
  if (!parts) {
    return null;
  }
  return new Date(parts.year, parts.month - 1, parts.day);
}

function dateTextFromDate(value: Date): string {
  const year = value.getFullYear();
  const month = `${value.getMonth() + 1}`.padStart(2, "0");
  const day = `${value.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function addDays(value: Date, days: number): Date {
  const next = new Date(value);
  next.setDate(next.getDate() + days);
  return next;
}

function isMonthText(monthText: string): boolean {
  return /^\d{4}-\d{2}$/.test(monthText || "");
}

function dateFromMonthText(monthText: string): Date | null {
  if (!isMonthText(monthText)) {
    return null;
  }
  const [yearText, monthNumberText] = monthText.split("-");
  return new Date(Number(yearText), Number(monthNumberText) - 1, 1);
}

function monthTextFromDate(value: Date): string {
  const year = value.getFullYear();
  const month = `${value.getMonth() + 1}`.padStart(2, "0");
  return `${year}-${month}`;
}

function moveCalendarMonthValue(monthText: string, offset: number): string {
  const current = dateFromMonthText(monthText);
  if (!current) {
    return monthText;
  }
  return monthTextFromDate(new Date(current.getFullYear(), current.getMonth() + offset, 1));
}

function formatMonthTitle(monthText: string): string {
  const current = dateFromMonthText(monthText);
  if (!current) {
    return "월 선택";
  }
  return `${current.getFullYear()}년 ${current.getMonth() + 1}월`;
}

function monthOptionsFromDays(days: CalendarDay[], today?: string): string[] {
  const options = Array.from(new Set(days.map((day) => day.date.slice(0, 7)).filter(Boolean))).sort();
  const todayMonth = (today || "").slice(0, 7);
  if (todayMonth && !options.includes(todayMonth)) {
    options.unshift(todayMonth);
  }
  return options;
}

function defaultMonthFromDays(days: CalendarDay[], today?: string): string {
  const options = monthOptionsFromDays(days, today);
  if (!options.length) {
    return (today || dateTextFromDate(new Date())).slice(0, 7);
  }
  const todayMonth = (today || "").slice(0, 7);
  if (todayMonth && options.includes(todayMonth)) {
    return todayMonth;
  }
  return options[0];
}

function monthSelectOptions(monthOptions: string[], activeMonth: string): string[] {
  return Array.from(new Set([activeMonth, ...monthOptions].filter(Boolean))).sort();
}

function buildCalendarMonthDays(
  monthText: string,
  dayMap: Map<string, CalendarDay>,
  calendar: EventsPayload["calendar"],
): Array<CalendarDay & { in_month: boolean; is_today: boolean; is_current_week: boolean; day_number: number }> {
  const [yearText, monthNumberText] = (monthText || "").split("-");
  const year = Number(yearText);
  const monthNumber = Number(monthNumberText);
  if (!year || !monthNumber) {
    return [];
  }
  const firstDay = new Date(year, monthNumber - 1, 1);
  const mondayOffset = (firstDay.getDay() + 6) % 7;
  const gridStart = addDays(firstDay, -mondayOffset);
  const todayText = calendar?.today || "";
  const weekStart = calendar?.current_week_start || "";
  const weekEnd = calendar?.current_week_end || "";
  return Array.from({ length: 42 }, (_value, index) => {
    const cellDate = addDays(gridStart, index);
    const dateText = dateTextFromDate(cellDate);
    const source = dayMap.get(dateText);
    return {
      ...(source || {
        date: dateText,
        count: 0,
        review_count: 0,
        stale_count: 0,
        by_family: {},
        top_titles: [],
        items: [],
      }),
      in_month: cellDate.getMonth() === monthNumber - 1,
      is_today: dateText === todayText,
      is_current_week: Boolean(weekStart && weekEnd && dateText >= weekStart && dateText <= weekEnd),
      day_number: cellDate.getDate(),
    };
  });
}

function CountTile({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="events-workbench__count-tile">
      <span>{label}</span>
      <strong>{valueText(value, "0")}</strong>
    </div>
  );
}

function EventCard({ item }: { item: EventItem }) {
  const title = item.symbol ? `${item.symbol} · ${item.title}` : item.title;
  return (
    <article className={`events-workbench__event-card events-workbench__event-card--${familyTone(item.family)}`}>
      <div className="events-workbench__event-date">
        {item.date}
        {item.event_time && item.event_time !== "-" ? <span>{item.event_time}</span> : null}
      </div>
      <div className="events-workbench__event-title">{title}</div>
      <div className="events-workbench__event-meta">
        {valueText(item.type)} · {valueText(item.freshness)} · {valueText(item.validation)}
      </div>
      <div className="events-workbench__badges">
        {(item.badges || []).slice(0, 5).map((badge) => (
          <span className={`events-workbench__badge events-workbench__badge--${badge.kind}`} key={`${badge.kind}-${badge.label}`}>
            {badge.label}
          </span>
        ))}
      </div>
    </article>
  );
}

function TrustItem({ item }: { item: EventItem }) {
  const title = item.symbol ? `${item.symbol} · ${item.title}` : item.title;
  const badgeText = (item.badges || [])
    .filter((badge) => ["source_authority", "freshness", "validation"].includes(badge.kind))
    .map((badge) => badge.label)
    .join(" · ");
  return (
    <div className="events-workbench__trust-item">
      <strong>{title}</strong>
      <span>
        {item.date}
        {badgeText ? ` · ${badgeText}` : ""}
      </span>
    </div>
  );
}

function dayTooltipText(day: CalendarDay): string {
  const titles = (day.top_titles || []).slice(0, 3).join(" / ");
  return `${day.date} · 이벤트 ${day.count}개 · 확인 필요 ${day.review_count}개 · 오래된 추정 ${day.stale_count}개${titles ? ` · ${titles}` : ""}`;
}

function rawValue(row: Record<string, unknown>, key: string): string {
  return valueText(row[key]);
}

function EventsWorkbench({ args }: ComponentProps) {
  const payload = ((args || {}).payload || {}) as EventsPayload;
  const rails = payload.rails || [];
  const railTabs = {
    default_key: payload.rail_tabs?.default_key || rails[0]?.key || "",
    empty_text: payload.rail_tabs?.empty_text || "선택한 조건에 맞는 일정이 없습니다.",
    tabs: payload.rail_tabs?.tabs || rails,
  };
  const command = payload.command || { actions: [] };
  const commandActions = command.actions || [];
  const lastResults = command.last_results || [];
  const calendar = payload.calendar || { days: [], density: [] };
  const calendarDays = calendar.days || [];
  const calendarDensity = calendar.density || [];
  const evidence = payload.evidence || { rows: [] };
  const evidenceRows = evidence.rows || [];
  const brief = payload.brief || {};
  const counts = brief.counts || {};
  const sourceSummary = brief.source_summary || {};
  const freshness = brief.freshness_summary || {};
  const trust = payload.trust_review || {};
  const trustSections = trust.sections || [];
  const [pendingActionId, setPendingActionId] = useState("");
  const [familyFilter, setFamilyFilter] = useState("all");
  const [reviewFilter, setReviewFilter] = useState("all");
  const [activeRailKey, setActiveRailKey] = useState(railTabs.default_key || railTabs.tabs?.[0]?.key || "");
  const [calendarMonth, setCalendarMonth] = useState(defaultMonthFromDays(calendarDays, calendar.today));
  const [expandedEvidence, setExpandedEvidence] = useState(false);
  const isPayloadReady = payload.schema_version === "events_workbench_v1";

  const familyOptions = payload.filters?.family?.options || FAMILY_OPTIONS;
  const reviewOptions = payload.filters?.source_state?.options || REVIEW_OPTIONS;
  const filteredRailTabs = (railTabs.tabs || []).map((rail) => {
    const items = filterItems(rail.items || [], familyFilter, reviewFilter);
    return {
      ...rail,
      count: items.length,
      review_count: items.filter((item) => item.needs_review).length,
      items,
    };
  });
  const activeRail = filteredRailTabs.find((rail) => rail.key === activeRailKey) || filteredRailTabs[0];
  const filteredCalendarDays = calendarDays
    .map((day) => {
      const items = filterItems(day.items || [], familyFilter, reviewFilter);
      return {
        ...day,
        count: items.length,
        review_count: items.filter((item) => item.needs_review).length,
        stale_count: items.filter((item) => normalizedText(item.freshness).includes("stale")).length,
        by_family: aggregateFamilies(items),
        top_titles: items.slice(0, 3).map((item) => item.title),
        items,
      };
    })
    .filter((day) => day.count > 0);
  const filteredDayMap = new Map(filteredCalendarDays.map((day) => [day.date, day]));
  const monthOptions = monthOptionsFromDays(filteredCalendarDays, calendar.today);
  const activeCalendarMonth = isMonthText(calendarMonth) ? calendarMonth : defaultMonthFromDays(filteredCalendarDays, calendar.today);
  const calendarMonthDays = buildCalendarMonthDays(activeCalendarMonth, filteredDayMap, calendar);
  const calendarMonthEventDays = calendarMonthDays.filter((day) => day.in_month && day.count > 0);
  const calendarMonthEventCount = calendarMonthEventDays.reduce((total, day) => total + day.count, 0);
  const visibleMonthOptions = monthSelectOptions(monthOptions, activeCalendarMonth);
  const filteredDensity = calendarDensity.filter((bucket) => weekMatchesFilter(bucket, familyFilter, reviewFilter));
  const maxDensityCount = Math.max(1, ...filteredDensity.map((bucket) => bucket.count || 0));

  useEffect(() => {
    Streamlit.setFrameHeight();
  }, [payload]);

  useEffect(() => {
    Streamlit.setFrameHeight();
  }, [familyFilter, reviewFilter, activeRailKey, calendarMonth, expandedEvidence, pendingActionId]);

  useEffect(() => {
    setPendingActionId("");
  }, [payload.schema_version, brief.freshness_summary?.latest_collected_at]);

  useEffect(() => {
    const defaultKey = railTabs.default_key || railTabs.tabs?.[0]?.key || "";
    if (defaultKey && !filteredRailTabs.some((rail) => rail.key === activeRailKey)) {
      setActiveRailKey(defaultKey);
    }
  }, [activeRailKey, filteredRailTabs, railTabs.default_key, railTabs.tabs]);

  useEffect(() => {
    const nextDefaultMonth = defaultMonthFromDays(filteredCalendarDays, calendar.today);
    if (!isMonthText(calendarMonth)) {
      setCalendarMonth(nextDefaultMonth);
    }
  }, [calendar.today, calendarMonth, filteredCalendarDays]);

  const emitEvent = (id: string) => {
    setPendingActionId(id);
    Streamlit.setComponentValue({ event: { id, nonce: `${Date.now()}-${Math.random()}` } });
  };

  const moveCalendarMonth = (offset: number) => {
    setCalendarMonth(moveCalendarMonthValue(activeCalendarMonth, offset));
  };

  if (!isPayloadReady) {
    return (
      <section className="events-workbench">
        <div className="events-workbench__fallback-note">Events workbench payload unavailable.</div>
      </section>
    );
  }

  return (
    <section className="events-workbench">
      <header className="events-workbench__hero">
        <div className="events-workbench__hero-copy">
          <span className="events-workbench__eyebrow">시장 일정</span>
          <h2>{brief.title || "다가오는 시장 이벤트 브리프"}</h2>
          <p>{brief.boundary_note}</p>
        </div>
        <div className="events-workbench__next-card">
          <span className="events-workbench__eyebrow">다음 이벤트</span>
          <strong>{brief.next_event ? brief.next_event.date : "예정 없음"}</strong>
          <p>{brief.next_event ? brief.next_event.title : "현재 기간에 확인할 다음 일정이 없습니다."}</p>
        </div>
      </header>

      <div className="events-workbench__counts">
        <CountTile label="오늘" value={counts.today} />
        <CountTile label="이번 주" value={counts.this_week} />
        <CountTile label="30일 내" value={counts.next_30d} />
        <CountTile label="공식 일정" value={sourceSummary.official} />
        <CountTile label="추정 일정" value={sourceSummary.provider_estimate} />
        <CountTile label="오래된 추정" value={freshness.stale_estimate_count} />
      </div>

      <section className="events-workbench__command">
        <div className="events-workbench__command-copy">
          <span className="events-workbench__eyebrow">갱신</span>
          <h3>{command.title || "화면 / 수집 갱신"}</h3>
          <p>{command.refresh_boundary}</p>
          {command.earnings_universe ? (
            <div className="events-workbench__universe-note">
              <strong>{command.earnings_universe.label || "실적 예상 일정 기준"}</strong>
              <span>{command.earnings_universe.description}</span>
              <em>
                {command.earnings_universe.lookahead_days}일 lookahead · {command.earnings_universe.cross_check}
              </em>
            </div>
          ) : null}
        </div>
        <div className="events-workbench__actions">
          {commandActions.map((action) => (
            <button
              className={`events-workbench__action events-workbench__action--${action.kind || "secondary"}`}
              disabled={pendingActionId === action.id}
              key={action.id}
              onClick={() => emitEvent(action.id)}
              title={action.detail || action.label}
              type="button"
            >
              {pendingActionId === action.id ? "실행 중" : action.label}
            </button>
          ))}
        </div>
        {lastResults.length ? (
          <div className="events-workbench__command-results">
            <strong>마지막 갱신 결과</strong>
            <div>
              {lastResults.slice(0, 4).map((result) => (
                <span className={`events-workbench__result-pill events-workbench__result-pill--${cssToken(result.status)}`} key={result.key || result.label}>
                  {valueText(result.label)} · {valueText(result.status)}
                  {result.jobs_run !== null && result.jobs_run !== undefined ? ` · ${result.jobs_run} jobs` : ""}
                  {result.message ? ` · ${result.message}` : ""}
                </span>
              ))}
            </div>
          </div>
        ) : null}
      </section>

      <section className="events-workbench__filterbar">
        <div className="events-workbench__filtergroup">
          <span>{payload.filters?.family?.label || "일정 타입"}</span>
          <div>
            {familyOptions.map((option) => (
              <button
                className={familyFilter === option.id ? "events-workbench__filter is-active" : "events-workbench__filter"}
                key={option.id}
                onClick={() => setFamilyFilter(option.id)}
                type="button"
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
        <div className="events-workbench__filtergroup">
          <span>{payload.filters?.source_state?.label || "자료 상태"}</span>
          <div>
            {reviewOptions.map((option) => (
              <button
                className={reviewFilter === option.id ? "events-workbench__filter is-active" : "events-workbench__filter"}
                key={option.id}
                onClick={() => setReviewFilter(option.id)}
                type="button"
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="events-workbench__rail">
        <div className="events-workbench__rail-header">
          <div>
            <span className="events-workbench__eyebrow">주의할 이벤트</span>
            <h3>{activeRail?.label || "오늘 / 이번 주"}</h3>
          </div>
          <span>{activeRail?.count || 0} rows · {activeRail?.review_count || 0} 확인 필요</span>
        </div>
        <div className="events-workbench__rail-tabs">
          {railTabs.tabs.map((rail) => {
            const filteredRail = filteredRailTabs.find((candidate) => candidate.key === rail.key) || rail;
            return (
              <button
                className={activeRailKey === rail.key ? "events-workbench__rail-tab is-active" : "events-workbench__rail-tab"}
                key={rail.key}
                onClick={() => setActiveRailKey(rail.key)}
                type="button"
              >
                <strong>{rail.label}</strong>
                <span>{filteredRail.count} · {filteredRail.review_count} 확인</span>
              </button>
            );
          })}
        </div>
        <div className="events-workbench__rail-items">
          {(activeRail?.items || []).slice(0, 8).map((item) => (
            <EventCard item={item} key={`${activeRail?.key}-${item.date}-${item.type}-${item.symbol || item.title}`} />
          ))}
          {!(activeRail?.items || []).length && <div className="events-workbench__empty">{railTabs.empty_text || "선택한 조건에 맞는 일정이 없습니다."}</div>}
        </div>
      </section>

      <section className="events-workbench__trust">
        <div>
          <span className="events-workbench__eyebrow">{trust.eyebrow || "자료 상태"}</span>
          <h3>{trust.title || "일정 확정성 / 추정 일정 점검"}</h3>
          {trust.description ? <p>{trust.description}</p> : null}
          {trust.source_boundary ? <p>{trust.source_boundary}</p> : null}
        </div>
        <div>
          <div className="events-workbench__trust-grid">
            <CountTile label="공식 일정" value={trust.official_count} />
            <CountTile label="제공사 추정" value={trust.provider_estimate_count} />
            <CountTile label="미확정" value={trust.not_confirmed_count} />
            <CountTile label="오래된 추정" value={trust.stale_estimate_count} />
          </div>
          <div className="events-workbench__trust-sections">
            {trustSections.map((section) => {
              const items = filterItems(section.items || [], familyFilter, reviewFilter);
              return (
                <section className="events-workbench__trust-section" key={section.key}>
                  <div className="events-workbench__trust-section-head">
                    <strong>{section.label}</strong>
                    <span>{items.length}</span>
                  </div>
                  {items.slice(0, 3).map((item) => (
                    <TrustItem item={item} key={`${section.key}-${item.date}-${item.type}-${item.symbol || item.title}`} />
                  ))}
                  {!items.length && <div className="events-workbench__empty events-workbench__empty--compact">해당 일정 없음</div>}
                </section>
              );
            })}
          </div>
          {(trust.warnings || []).length ? (
            <div className="events-workbench__warnings">
              {(trust.warnings || []).slice(0, 3).map((warning) => (
                <span key={warning}>{warning}</span>
              ))}
            </div>
          ) : null}
        </div>
      </section>

      <section className="events-workbench__calendar">
        <div className="events-workbench__section-head">
          <div>
            <span className="events-workbench__eyebrow">캘린더</span>
            <h3>캘린더로 보는 일정 근거</h3>
          </div>
          <div className="events-workbench__month-control">
            <div className="events-workbench__month-nav" aria-label="월 이동">
              <button aria-label="이전 달" onClick={() => moveCalendarMonth(-1)} type="button">
                ‹
              </button>
              <strong className="events-workbench__month-title">{formatMonthTitle(activeCalendarMonth)}</strong>
              <button aria-label="다음 달" onClick={() => moveCalendarMonth(1)} type="button">
                ›
              </button>
            </div>
            <span className="events-workbench__month-summary">
              이벤트 날짜 {calendarMonthEventDays.length}일 · 이벤트 {calendarMonthEventCount}건
            </span>
            <select className="events-workbench__month-select" value={activeCalendarMonth} onChange={(event) => setCalendarMonth(event.target.value)}>
              {visibleMonthOptions.map((month) => (
                <option key={month} value={month}>
                  {month}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="events-workbench__month-grid">
          {(calendar.weekday_labels || ["월", "화", "수", "목", "금", "토", "일"]).map((label) => (
            <div className="events-workbench__weekday" key={label}>{label}</div>
          ))}
          {calendarMonthDays.map((day) => (
            <div
              className={[
                "events-workbench__day",
                day.in_month ? "" : "events-workbench__day--outside-month",
                day.is_today ? "events-workbench__day--today" : "",
                day.is_current_week ? "events-workbench__day--current-week" : "",
                day.count ? "events-workbench__day--has-events" : "",
              ].filter(Boolean).join(" ")}
              key={day.date}
              title={dayTooltipText(day)}
            >
              <div className="events-workbench__day-head">
                <strong>{day.day_number}</strong>
                {day.count ? <span>{day.count}</span> : null}
              </div>
              {day.count ? (
                <div className="events-workbench__day-families">
                  {Object.entries(day.by_family || {}).map(([family, count]) => (
                  <span className={`events-workbench__family-dot events-workbench__family-dot--${familyTone(family)}`} key={family}>
                    {familyLabel(family)} {count}
                  </span>
                  ))}
                </div>
              ) : null}
              {day.count ? (
                <div className="events-workbench__day-meta">
                  확인 {day.review_count} · 오래된 추정 {day.stale_count}
                </div>
              ) : null}
              {day.count ? (
                <div className="events-workbench__day-tooltip" role="tooltip">
                  <strong>{day.date}</strong>
                  <span>이벤트 {day.count}개 · 확인 필요 {day.review_count}개 · 오래된 추정 {day.stale_count}개</span>
                  {(day.top_titles || []).slice(0, 3).map((title) => (
                    <em key={`${day.date}-${title}`}>{title}</em>
                  ))}
                </div>
              ) : null}
            </div>
          ))}
        </div>

        <div className="events-workbench__density">
          {filteredDensity.slice(0, 12).map((bucket) => (
            <div className="events-workbench__density-row" key={bucket.week_start}>
              <span>{bucket.week_start}</span>
              <div className="events-workbench__density-bar" title={`이벤트 ${bucket.count}개 · 확인 필요 ${bucket.review_count}개`}>
                <div className="events-workbench__density-fill" style={{ width: `${Math.max(8, (bucket.count / maxDensityCount) * 100)}%` }}>
                  {Object.entries(bucket.by_family || {}).map(([family, count]) => (
                    <i
                      className={`events-workbench__density-segment events-workbench__density-segment--${familyTone(family)}`}
                      key={`${bucket.week_start}-${family}`}
                      style={{ width: `${Math.max(8, (Number(count) / Math.max(1, bucket.count)) * 100)}%` }}
                    />
                  ))}
                </div>
              </div>
              <strong>{bucket.count}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="events-workbench__evidence">
        <div className="events-workbench__section-head">
          <div>
            <span className="events-workbench__eyebrow">상세 근거</span>
            <h3>원본 / 상세 근거</h3>
          </div>
          <button type="button" onClick={() => setExpandedEvidence(!expandedEvidence)}>
            {expandedEvidence ? "접기" : `${valueText(evidence.row_count, "0")} rows`}
          </button>
        </div>
        {expandedEvidence ? (
          <div className="events-workbench__evidence-table">
            <div className="events-workbench__evidence-head">
              <span>날짜</span>
              <span>유형</span>
              <span>제목</span>
              <span>출처</span>
              <span>수집 기준</span>
            </div>
            {evidenceRows.slice(0, 10).map((row, index) => (
              <div className="events-workbench__evidence-row" key={`${rawValue(row, "Date")}-${rawValue(row, "Type")}-${index}`}>
                <span>{rawValue(row, "Date")}</span>
                <span>{rawValue(row, "Type")}</span>
                <strong>{rawValue(row, "Symbol") !== "-" ? `${rawValue(row, "Symbol")} · ${rawValue(row, "Title")}` : rawValue(row, "Title")}</strong>
                <span>
                  {rawValue(row, "Source URL").startsWith("http") ? (
                    <a href={rawValue(row, "Source URL")} rel="noreferrer" target="_blank">
                      {rawValue(row, "Source Authority")}
                    </a>
                  ) : (
                    rawValue(row, "Source Authority")
                  )}
                </span>
                <span>{rawValue(row, "Collected At")}</span>
              </div>
            ))}
          </div>
        ) : null}
      </section>

      <button className="events-workbench__hidden-action" type="button" onClick={() => emitEvent("noop")}>
        Component ready
      </button>
    </section>
  );
}

export default withStreamlitConnection(EventsWorkbench);
