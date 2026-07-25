// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import EventsHero from "../events_workbench/src/EventsHero";

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
});
