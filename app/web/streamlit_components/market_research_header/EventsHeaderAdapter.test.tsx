// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import EventsHero, * as EventsHeroModule from "../events_workbench/src/EventsHero";

afterEach(cleanup);

describe("EventsHero shared header adapter", () => {
  it("renders the next event as a neutral fact and existing counts as metadata", () => {
    const { container } = render(
      <EventsHero
        boundaryNote="공식 일정과 추정 일정을 구분해서 확인합니다."
        counts={{
          next30d: 31,
          staleEstimate: 2,
          thisWeek: 8,
          today: 2,
        }}
        nextEvent={{
          date: "2026-07-29",
          title: "FOMC",
        }}
        title="이번 주 주요 일정을 먼저 확인"
      />,
    );

    expect(container.querySelector(".research-header--events")).not.toBeNull();
    expect(screen.getByRole("heading", { level: 2, name: "이번 주 주요 일정을 먼저 확인" })).toBeTruthy();
    expect(screen.getByText("2026-07-29 · FOMC")).toBeTruthy();
    expect(screen.getByText("오늘 2건")).toBeTruthy();
    expect(screen.getByText("이번 주 8건")).toBeTruthy();
    expect(screen.getByText("30일 내 31건")).toBeTruthy();
    expect(screen.getByText("오래된 추정 2건")).toBeTruthy();
    expect(screen.getByText("2026-07-29 · FOMC").closest(".research-header__fact")?.querySelector(".research-header__state-dot")).toBeNull();
    expect(container.querySelector(".research-header__actions")).toBeNull();
  });

  it("uses the existing empty-state wording when no next event exists", () => {
    render(
      <EventsHero
        boundaryNote="공식 일정과 추정 일정을 구분해서 확인합니다."
        counts={{}}
        nextEvent={null}
        title=""
      />,
    );

    expect(screen.getByRole("heading", { level: 2, name: "다가오는 시장 이벤트 브리프" })).toBeTruthy();
    expect(screen.getByText("예정 없음")).toBeTruthy();
  });

  it("keeps the official refresh action in the shared header", () => {
    const onRefresh = vi.fn();

    render(
      <EventsHero
        boundaryNote="공식 일정과 추정 일정을 구분해서 확인합니다."
        counts={{}}
        nextEvent={null}
        primaryAction={{
          disabled: false,
          label: "공식 일정 갱신",
          onClick: onRefresh,
        }}
        title="이번 주 시장 일정"
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "공식 일정 갱신" }));

    expect(onRefresh).toHaveBeenCalledTimes(1);
  });

  it("maps the current events view counts without relying on removed top-level fields", () => {
    expect(typeof EventsHeroModule.buildEventsHeroCounts).toBe("function");

    const counts = EventsHeroModule.buildEventsHeroCounts(
      {
        next_30d: 31,
        this_week: 8,
        today: 2,
      },
      [
        { stale_count: 2 },
        { stale_count: 1 },
      ],
    );

    expect(counts).toEqual({
      next30d: 31,
      staleEstimate: 3,
      thisWeek: 8,
      today: 2,
    });
  });
});
