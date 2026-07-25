// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import ResearchHeader from "./ResearchHeader";

afterEach(cleanup);

describe("ResearchHeader", () => {
  it("omits optional regions instead of rendering empty slots", () => {
    const { container } = render(
      <ResearchHeader
        eyebrow="U.S. ECONOMIC CYCLE"
        kicker="현재 경기 위치"
        summary="현재는 회복 국면 가능성이 가장 높습니다."
        title="회복 우세"
        titleId="cycle-title"
        variant="cycle"
      />,
    );

    expect(screen.getByRole("heading", { level: 2, name: "회복 우세" })).toBeTruthy();
    expect(container.querySelector(".research-header__facts")).toBeNull();
    expect(container.querySelector(".research-header__actions")).toBeNull();
    expect(container.querySelector(".research-header__notice")).toBeNull();
    expect(container.querySelector(".research-header__meta")).toBeNull();
  });

  it("shows an indicator only for facts explicitly marked as state", () => {
    render(
      <ResearchHeader
        eyebrow="FUTURES MACRO"
        facts={[
          {
            id: "observation",
            label: "관측 상태",
            value: "관측 완료",
            tone: "info",
            showIndicator: true,
          },
          {
            id: "as-of",
            label: "기준일",
            value: "2026-07-23",
          },
        ]}
        kicker="단기 방향 진단"
        summary="단일 방향 우위가 약합니다."
        title="혼재 체제"
        titleId="futures-title"
        variant="futures"
      />,
    );

    const stateFact = screen.getByText("관측 상태").closest(".research-header__fact");
    const dateFact = screen.getByText("기준일").closest(".research-header__fact");

    expect(stateFact).not.toBeNull();
    expect(dateFact).not.toBeNull();
    expect(within(stateFact as HTMLElement).getByText("관측 완료")).toBeTruthy();
    expect(stateFact?.querySelectorAll(".research-header__state-dot")).toHaveLength(1);
    expect(dateFact?.querySelector(".research-header__state-dot")).toBeNull();
  });

  it("dispatches enabled actions and keeps disabled actions inert", () => {
    const onRefresh = vi.fn();
    const onReload = vi.fn();

    render(
      <ResearchHeader
        actions={[
          {
            id: "refresh",
            kind: "primary",
            label: "일봉 갱신",
            onClick: onRefresh,
          },
          {
            disabled: true,
            id: "reload",
            kind: "secondary",
            label: "요청 중",
            onClick: onReload,
          },
        ]}
        eyebrow="FUTURES MACRO"
        kicker="단기 방향 진단"
        summary="단일 방향 우위가 약합니다."
        title="혼재 체제"
        titleId="futures-actions-title"
        variant="futures"
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "일봉 갱신" }));
    fireEvent.click(screen.getByRole("button", { name: "요청 중" }));

    expect(onRefresh).toHaveBeenCalledTimes(1);
    expect(onReload).not.toHaveBeenCalled();
  });
});
