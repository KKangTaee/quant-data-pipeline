// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import EconomicCycleHero from "../economic_cycle_workbench/src/EconomicCycleHero";

afterEach(cleanup);

describe("EconomicCycleHero shared header adapter", () => {
  it("renders the cycle decision with optional intramonth metadata and no empty actions", () => {
    const { container } = render(
      <EconomicCycleHero
        asOfDate="2026-06-30"
        estimateLabel="잠정 모델 추정"
        estimateTone="caution"
        hasIntramonth
        summary="현재는 회복 국면 가능성이 가장 높습니다."
        title="회복 우세"
      />,
    );

    expect(container.querySelector(".research-header--cycle")).not.toBeNull();
    expect(screen.getByRole("heading", { level: 2, name: "회복 우세" })).toBeTruthy();
    expect(screen.getByText("2026-06-30")).toBeTruthy();
    expect(screen.getByText("잠정 모델 추정")).toBeTruthy();
    expect(screen.getByText("현재 · +1개월 · +2개월")).toBeTruthy();
    expect(screen.getByText("월중 추정 별도 표시")).toBeTruthy();
    expect(screen.getByText("잠정 모델 추정").closest(".research-header__fact")?.querySelector(".research-header__state-dot")).not.toBeNull();
    expect(screen.getByText("2026-06-30").closest(".research-header__fact")?.querySelector(".research-header__state-dot")).toBeNull();
    expect(container.querySelector(".research-header__actions")).toBeNull();
  });

  it("omits the intramonth chip when no intramonth estimate exists", () => {
    render(
      <EconomicCycleHero
        asOfDate="2026-06-30"
        estimateLabel="검증된 모델 추정"
        estimateTone="positive"
        hasIntramonth={false}
        summary="현재는 회복 국면 가능성이 가장 높습니다."
        title="회복 우세"
      />,
    );

    expect(screen.queryByText("월중 추정 별도 표시")).toBeNull();
  });
});
