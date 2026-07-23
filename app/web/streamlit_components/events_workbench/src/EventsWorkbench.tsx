import React, { useEffect, useMemo, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import "./style.css";

type EventBadge = {
  label: string;
  kind: string;
};

type EventItem = {
  date: string;
  display_date?: string;
  display_time?: string | null;
  time_basis?: string;
  days_until?: number | null;
  type: string;
  family: string;
  display_family?: string;
  display_family_label?: string;
  symbol?: string;
  symbols?: string[];
  issuer_key?: string;
  issuer_name?: string;
  title: string;
  relevance?: string;
  validation?: string;
  freshness?: string;
  source_authority?: string;
  source_type?: string;
  source_url?: string;
  collected_at?: string;
  needs_review?: boolean;
  badges?: EventBadge[];
};

type CalendarDay = {
  date: string;
  count: number;
  review_count: number;
  stale_count: number;
  by_family?: Record<string, number>;
  items?: EventItem[];
};

type CalendarCell = CalendarDay & {
  in_month: boolean;
  is_today: boolean;
  is_current_week: boolean;
  day_number: number;
};

type DensityBucket = {
  week_start: string;
  week_end?: string;
  label?: string;
  count: number;
  review_count: number;
  stale_count: number;
  by_family?: Record<string, number>;
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

type CommandResult = {
  key?: string;
  label?: string;
  status?: string;
  message?: string;
  jobs_run?: number | null;
};

type EventsView = {
  brief?: {
    title?: string;
    boundary_note?: string;
    next_event?: EventItem | null;
    next_fomc?: EventItem | null;
    counts?: Record<string, number>;
  };
  calendar?: {
    today?: string;
    current_week_start?: string;
    current_week_end?: string;
    weekday_labels?: string[];
    days?: CalendarDay[];
    density?: DensityBucket[];
  };
  trust_summary?: {
    official?: number;
    provider_estimate?: number;
    review_required?: number;
    warnings?: string[];
  };
  empty_state?: {
    status?: string;
    title?: string;
    description?: string;
  };
};

type EventsPayload = {
  schema_version?: string;
  status?: string;
  filter_options?: EventFilterOption[];
  views?: Record<string, EventsView>;
  coverage_summary?: {
    status?: string;
    label?: string;
    description?: string;
    expected_items?: number;
    covered_items?: number;
    failed_items?: number;
  };
  command?: {
    refresh_boundary?: string;
    actions?: EventAction[];
    earnings_universe?: {
      label?: string;
      description?: string;
    };
    last_results?: CommandResult[];
  };
  evidence?: {
    rows?: Record<string, unknown>[];
    row_count?: number;
  };
};

const DEFAULT_FILTERS: EventFilterOption[] = [
  { id: "all", label: "전체" },
  { id: "central_bank", label: "FOMC" },
  { id: "earnings", label: "실적" },
  { id: "market_holiday", label: "휴장·조기폐장" },
];

function valueText(value: unknown, fallback = "-"): string {
  return value === null || value === undefined || value === "" ? fallback : String(value);
}

function normalizedText(value: unknown): string {
  return valueText(value, "").trim().toLowerCase();
}

function cssToken(value: unknown): string {
  return normalizedText(value).replace(/[^a-z0-9_-]+/g, "_") || "unknown";
}

function familyLabel(value: unknown): string {
  const labels: Record<string, string> = {
    central_bank: "FOMC",
    earnings: "실적",
    market_holiday: "휴장·조기폐장",
    market_structure: "시장 일정",
    macro: "매크로",
    fixed_income: "국채·금리",
  };
  return labels[normalizedText(value)] || valueText(value, "기타");
}

function familyTone(value: unknown): string {
  const family = normalizedText(value);
  if (family === "central_bank") return "fomc";
  if (family === "market_holiday") return "holiday";
  if (family === "earnings") return "earnings";
  if (family === "macro" || family === "fixed_income") return "macro";
  return cssToken(family);
}

function eventFamilyKey(item: EventItem): string {
  return valueText(item.display_family || item.family, "unknown");
}

function parseDateParts(dateText: string): { year: number; month: number; day: number } | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateText || "");
  return match
    ? { year: Number(match[1]), month: Number(match[2]), day: Number(match[3]) }
    : null;
}

function dateFromText(dateText: string): Date | null {
  const parts = parseDateParts(dateText);
  return parts ? new Date(parts.year, parts.month - 1, parts.day) : null;
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

function dateFromMonthText(monthText: string): Date | null {
  if (!/^\d{4}-\d{2}$/.test(monthText || "")) return null;
  const [year, month] = monthText.split("-").map(Number);
  return new Date(year, month - 1, 1);
}

function monthTextFromDate(value: Date): string {
  return `${value.getFullYear()}-${`${value.getMonth() + 1}`.padStart(2, "0")}`;
}

function moveCalendarMonthValue(monthText: string, offset: number): string {
  const current = dateFromMonthText(monthText);
  return current
    ? monthTextFromDate(new Date(current.getFullYear(), current.getMonth() + offset, 1))
    : monthText;
}

function formatMonthTitle(monthText: string): string {
  const current = dateFromMonthText(monthText);
  return current ? `${current.getFullYear()}년 ${current.getMonth() + 1}월` : "월 선택";
}

function densityRangeLabel(bucket: DensityBucket): string {
  if (bucket.label) return bucket.label;
  const start = dateFromText(bucket.week_start);
  const end = bucket.week_end ? dateFromText(bucket.week_end) : start ? addDays(start, 6) : null;
  return start && end
    ? `${start.getMonth() + 1}/${start.getDate()}-${end.getMonth() + 1}/${end.getDate()}`
    : bucket.week_start;
}

function defaultMonthFromDays(days: CalendarDay[], today?: string): string {
  const todayMonth = (today || "").slice(0, 7);
  const months = Array.from(new Set(days.map((day) => day.date.slice(0, 7)).filter(Boolean))).sort();
  if (todayMonth && (months.includes(todayMonth) || !months.length)) return todayMonth;
  return months[0] || monthTextFromDate(new Date());
}

function buildCalendarMonthDays(
  monthText: string,
  dayMap: Map<string, CalendarDay>,
  calendar: EventsView["calendar"],
): CalendarCell[] {
  const monthDate = dateFromMonthText(monthText);
  if (!monthDate) return [];
  const mondayOffset = (monthDate.getDay() + 6) % 7;
  const gridStart = addDays(monthDate, -mondayOffset);
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
        items: [],
      }),
      in_month: cellDate.getMonth() === monthDate.getMonth(),
      is_today: dateText === calendar?.today,
      is_current_week: Boolean(
        calendar?.current_week_start
        && calendar?.current_week_end
        && dateText >= calendar.current_week_start
        && dateText <= calendar.current_week_end
      ),
      day_number: cellDate.getDate(),
    };
  });
}

function BriefCard({
  label,
  item,
  value,
}: {
  label: string;
  item?: EventItem | null;
  value?: string;
}) {
  return (
    <article className="events-workbench__brief-card">
      <span>{label}</span>
      {item ? (
        <>
          <strong>{item.title}</strong>
          <p>{valueText(item.display_date || item.date)} · {valueText(item.time_basis, "시간 기준 미확인")}</p>
        </>
      ) : (
        <>
          <strong>{value || "예정 없음"}</strong>
          <p>{value ? "선택 범위 기준" : "현재 기간에 확인된 일정이 없습니다."}</p>
        </>
      )}
    </article>
  );
}

function EventCard({ item }: { item: EventItem }) {
  const symbols = item.symbols?.length ? item.symbols.join(" · ") : item.symbol;
  return (
    <article className={`events-workbench__event-card events-workbench__event-card--${familyTone(eventFamilyKey(item))}`}>
      <div className="events-workbench__event-card-head">
        <span>{familyLabel(eventFamilyKey(item))}</span>
        <em>{valueText(item.relevance, "일반")}</em>
      </div>
      <strong>{item.title}</strong>
      {symbols ? <p className="events-workbench__symbols">{symbols}</p> : null}
      <p>{valueText(item.display_date || item.date)}{item.display_time ? ` ${item.display_time}` : ""}</p>
      <p className="events-workbench__time-basis">{valueText(item.time_basis, "시간 기준 미확인")}</p>
      <div className="events-workbench__badges">
        {(item.badges || []).slice(0, 4).map((badge) => (
          <span key={`${badge.kind}-${badge.label}`}>{badge.label}</span>
        ))}
      </div>
      {item.source_url?.startsWith("http") ? (
        <a href={item.source_url} rel="noreferrer" target="_blank">출처 확인</a>
      ) : null}
    </article>
  );
}

function CalendarHeader({
  activeMonth,
  eventCount,
  eventDays,
  onMove,
}: {
  activeMonth: string;
  eventCount: number;
  eventDays: number;
  onMove: (offset: number) => void;
}) {
  return (
    <div className="events-workbench__calendar-header">
      <div>
        <span className="events-workbench__eyebrow">월간 캘린더</span>
        <h3>{formatMonthTitle(activeMonth)}</h3>
        <p className="events-workbench__month-summary">이벤트 날짜 {eventDays}일 · 총 {eventCount}건</p>
      </div>
      <div className="events-workbench__month-nav" aria-label="월 이동">
        <button aria-label="이전 달" onClick={() => onMove(-1)} type="button">‹</button>
        <strong className="events-workbench__month-title">{formatMonthTitle(activeMonth)}</strong>
        <button aria-label="다음 달" onClick={() => onMove(1)} type="button">›</button>
      </div>
    </div>
  );
}

function DensityChart({ buckets }: { buckets: DensityBucket[] }) {
  const maxDensityCount = Math.max(1, ...buckets.map((bucket) => bucket.count || 0));
  return (
    <div className="events-workbench__density">
      <div className="events-workbench__density-head">
        <div>
          <span className="events-workbench__eyebrow">주간 밀집도</span>
          <h3>주간 일정 밀집도</h3>
        </div>
        <span>주간 합계</span>
      </div>
      {buckets.slice(0, 12).map((bucket) => (
        <div className="events-workbench__density-row" key={bucket.week_start}>
          <span>{densityRangeLabel(bucket)}</span>
          <div className="events-workbench__density-bar" title={`주간 합계 ${bucket.count}건`}>
            <div style={{ width: `${Math.max(8, (bucket.count / maxDensityCount) * 100)}%` }}>
              {Object.entries(bucket.by_family || {}).map(([family, count]) => (
                <i
                  className={`events-workbench__density-segment events-workbench__density-segment--${familyTone(family)}`}
                  key={`${bucket.week_start}-${family}`}
                  style={{ width: `${Math.max(8, (Number(count) / Math.max(1, bucket.count)) * 100)}%` }}
                />
              ))}
            </div>
          </div>
          <strong>총 {bucket.count}건</strong>
        </div>
      ))}
    </div>
  );
}

function rawValue(row: Record<string, unknown>, key: string): string {
  return valueText(row[key]);
}

function EventsWorkbench({ args }: ComponentProps) {
  const payload = ((args || {}).payload || {}) as EventsPayload;
  const [familyFilter, setFamilyFilter] = useState("all");
  const activeView = payload.views?.[familyFilter] || payload.views?.all || {};
  const brief = activeView.brief || {};
  const calendar = activeView.calendar || { days: [], density: [] };
  const calendarDays = calendar.days || [];
  const calendarDensity = calendar.density || [];
  const filterOptions = payload.filter_options || DEFAULT_FILTERS;
  const command = payload.command || { actions: [] };
  const commandActions = command.actions || [];
  const secondaryActions = commandActions.filter((action) => action.id !== "refresh_all");
  const lastResults = command.last_results || [];
  const evidenceRows = payload.evidence?.rows || [];
  const [pendingActionId, setPendingActionId] = useState("");
  const [calendarMonth, setCalendarMonth] = useState(defaultMonthFromDays(calendarDays, calendar.today));
  const [selectedDate, setSelectedDate] = useState("");
  const [expandedEvidence, setExpandedEvidence] = useState(false);
  const isPayloadReady = payload.schema_version === "events_workbench_v2";

  const dayMap = useMemo(
    () => new Map(calendarDays.map((day) => [day.date, day])),
    [calendarDays],
  );
  const activeCalendarMonth = /^\d{4}-\d{2}$/.test(calendarMonth)
    ? calendarMonth
    : defaultMonthFromDays(calendarDays, calendar.today);
  const calendarMonthDays = buildCalendarMonthDays(activeCalendarMonth, dayMap, calendar);
  const calendarMonthEventDays = calendarMonthDays.filter((day) => day.in_month && day.count > 0);
  const calendarMonthEventCount = calendarMonthEventDays.reduce((sum, day) => sum + day.count, 0);
  const selectedCalendarDay = calendarDays.find((day) => day.date === selectedDate) || null;

  useEffect(() => {
    Streamlit.setFrameHeight();
  }, [payload, familyFilter, calendarMonth, selectedDate, expandedEvidence, pendingActionId]);

  useEffect(() => {
    setPendingActionId("");
  }, [payload.schema_version, payload.status]);

  useEffect(() => {
    const nextMonth = defaultMonthFromDays(calendarDays, calendar.today);
    if (!calendarDays.some((day) => day.date.startsWith(activeCalendarMonth))) {
      setCalendarMonth(nextMonth);
    }
    if (selectedDate && !calendarDays.some((day) => day.date === selectedDate)) {
      setSelectedDate("");
    }
  }, [activeCalendarMonth, calendar.today, calendarDays, selectedDate]);

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
        <div>
          <span className="events-workbench__eyebrow">시장 일정</span>
          <h2>이번 주 시장 일정</h2>
          <p>한국시간 기준 · 공식 일정과 실적 추정을 구분합니다.</p>
        </div>
        <button
          className="events-workbench__refresh"
          disabled={pendingActionId === "refresh_all"}
          onClick={() => emitEvent("refresh_all")}
          type="button"
        >
          {pendingActionId === "refresh_all" ? "갱신 중" : "일정 갱신"}
        </button>
      </header>

      <section className="events-workbench__filterbar">
        <span>일정 타입</span>
        <div>
          {filterOptions.map((option) => (
            <button
              className={familyFilter === option.id ? "is-active" : ""}
              key={option.id}
              onClick={() => setFamilyFilter(option.id)}
              type="button"
            >
              {option.label}
            </button>
          ))}
        </div>
      </section>

      <div className="events-workbench__brief-grid">
        <BriefCard label="가장 중요한 다음 일정" item={brief.next_event} />
        <BriefCard label="이번 주 핵심 일정" value={`${valueText(brief.counts?.this_week, "0")}개`} />
        <BriefCard label="다음 FOMC" item={brief.next_fomc} />
      </div>

      <section className="events-workbench__calendar-layout">
        <div className="events-workbench__calendar-main">
          <CalendarHeader
            activeMonth={activeCalendarMonth}
            eventCount={calendarMonthEventCount}
            eventDays={calendarMonthEventDays.length}
            onMove={moveCalendarMonth}
          />
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
                  day.date === selectedDate ? "events-workbench__day--selected" : "",
                ].filter(Boolean).join(" ")}
                key={day.date}
              >
                <button
                  aria-label={`${day.date} 일정 ${day.count}건 보기`}
                  className="events-workbench__day-button"
                  disabled={!day.count}
                  onClick={() => day.count && setSelectedDate(day.date)}
                  type="button"
                >
                  <div className="events-workbench__day-head">
                    <strong>{day.day_number}</strong>
                    {day.count ? <span>{day.count}</span> : null}
                  </div>
                  <div className="events-workbench__day-families">
                    {Object.entries(day.by_family || {}).map(([family, count]) => (
                      <span className={`events-workbench__family-dot events-workbench__family-dot--${familyTone(family)}`} key={family}>
                        {familyLabel(family)} {count}
                      </span>
                    ))}
                  </div>
                </button>
              </div>
            ))}
          </div>
          <DensityChart buckets={calendarDensity} />
        </div>

        <aside className="events-workbench__selected-day">
          {selectedCalendarDay ? (
            <>
              <span className="events-workbench__eyebrow">선택 날짜</span>
              <h3>{selectedCalendarDay.date}</h3>
              <p>총 {selectedCalendarDay.count}건 · 확인 필요 {selectedCalendarDay.review_count}건</p>
              <div className="events-workbench__selected-day-list">
                {(selectedCalendarDay.items || []).map((item) => (
                  <EventCard
                    item={item}
                    key={`${selectedCalendarDay.date}-${item.issuer_key || item.symbol || item.title}`}
                  />
                ))}
              </div>
            </>
          ) : (
            <div className="events-workbench__empty">
              <strong>{activeView.empty_state?.title || "날짜를 선택하세요"}</strong>
              <p>{activeView.empty_state?.description || "날짜를 선택하면 해당 날짜의 중요 일정과 출처를 확인할 수 있습니다."}</p>
            </div>
          )}
        </aside>
      </section>

      <details className="events-workbench__support-details">
        <summary>자료 신뢰와 수집 범위</summary>
        <div className="events-workbench__support-grid">
          <div>
            <strong>{payload.coverage_summary?.label || "수집 범위"}</strong>
            <p>{payload.coverage_summary?.description}</p>
          </div>
          <div>
            <strong>공식 {valueText(activeView.trust_summary?.official, "0")}개</strong>
            <span>추정 {valueText(activeView.trust_summary?.provider_estimate, "0")}개</span>
            <span>확인 필요 {valueText(activeView.trust_summary?.review_required, "0")}개</span>
          </div>
        </div>
        <p className="events-workbench__support-boundary">{command.refresh_boundary}</p>
        <div className="events-workbench__universe-note">
          <strong>{command.earnings_universe?.label || "실적 예상 일정 기준"}</strong>
          <span>{command.earnings_universe?.description}</span>
        </div>
        <div className="events-workbench__secondary-actions">
          {secondaryActions.map((action) => (
            <button
              disabled={pendingActionId === action.id}
              key={action.id}
              onClick={() => emitEvent(action.id)}
              title={action.detail}
              type="button"
            >
              {pendingActionId === action.id ? "실행 중" : action.label}
            </button>
          ))}
        </div>
        {lastResults.length ? (
          <div className="events-workbench__last-results">
            <strong>마지막 갱신 결과</strong>
            {lastResults.slice(0, 4).map((result) => (
              <span className={`events-workbench__result--${cssToken(result.status)}`} key={result.key || result.label}>
                {valueText(result.label)} · {valueText(result.status)}{result.message ? ` · ${result.message}` : ""}
              </span>
            ))}
          </div>
        ) : null}
        <button className="events-workbench__evidence-toggle" onClick={() => setExpandedEvidence(!expandedEvidence)} type="button">
          {expandedEvidence ? "원본 근거 접기" : `원본 근거 ${valueText(payload.evidence?.row_count, "0")}건 보기`}
        </button>
        {expandedEvidence ? (
          <div className="events-workbench__evidence-table">
            <div className="events-workbench__evidence-head">
              <span>날짜</span><span>유형</span><span>제목</span><span>출처</span><span>수집 기준</span>
            </div>
            {evidenceRows.slice(0, 10).map((row, index) => (
              <div className="events-workbench__evidence-row" key={`${rawValue(row, "Date")}-${index}`}>
                <span>{rawValue(row, "Display Date KST") !== "-" ? rawValue(row, "Display Date KST") : rawValue(row, "Date")}</span>
                <span>{rawValue(row, "Type")}</span>
                <strong>{rawValue(row, "Title")}</strong>
                <span>{rawValue(row, "Source Authority")}</span>
                <span>{rawValue(row, "Collected At")}</span>
              </div>
            ))}
          </div>
        ) : null}
      </details>

      <button className="events-workbench__hidden-action" onClick={() => emitEvent("noop")} type="button">
        Component ready
      </button>
    </section>
  );
}

export default withStreamlitConnection(EventsWorkbench);
