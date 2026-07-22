import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ComponentProps } from "streamlit-component-lib";

const streamlitMocks = vi.hoisted(() => ({
  setComponentValue: vi.fn(),
  setFrameHeight: vi.fn(),
}));

vi.mock("streamlit-component-lib", () => ({
  Streamlit: streamlitMocks,
  withStreamlitConnection: <T,>(component: T) => component,
}));

import { MarketResearchNavigation } from "./MarketResearchNavigation";
import type { MarketResearchNavigationPayload } from "./contracts";

const payload: MarketResearchNavigationPayload = {
  schema_version: "market_research_navigation_v1",
  eyebrow: "RESEARCH WORKSPACE",
  title: "Market Research",
  description: "Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다.",
  active_family: "market-environment",
  active_view: "economic-cycle",
  families: [
    { id: "market-environment", label: "시장 환경", description: "경제·매크로·심리·일정", views: [
      { id: "economic-cycle", label: "경제 사이클" },
      { id: "futures-macro", label: "선물 매크로" },
      { id: "sentiment", label: "심리" },
      { id: "events", label: "일정" },
    ] },
    { id: "index-valuation", label: "지수 가치평가", description: "대표지수 멀티플과 실적", views: [
      { id: "sp500", label: "S&P 500" },
    ] },
    { id: "stock-research", label: "종목 리서치", description: "변동 종목과 개별 기업", views: [
      { id: "market-movers", label: "변동 종목" },
      { id: "us-stock", label: "개별 종목" },
    ] },
  ],
};

function props(value?: MarketResearchNavigationPayload): ComponentProps {
  return { args: value ? { payload: value } : {}, width: 1280 } as ComponentProps;
}

afterEach(cleanup);

describe("MarketResearchNavigation", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders one accessible heading and selected family/view states", () => {
    render(<MarketResearchNavigation {...props(payload)} />);
    expect(screen.getByRole("heading", { name: "Market Research", level: 1 })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /시장 환경/ })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "경제 사이클" })).toHaveAttribute("aria-current", "page");
  });

  it("emits the target family default view once", async () => {
    const user = userEvent.setup();
    render(<MarketResearchNavigation {...props(payload)} />);
    await user.click(screen.getByRole("button", { name: /지수 가치평가/ }));
    expect(streamlitMocks.setComponentValue).toHaveBeenCalledTimes(1);
    expect(streamlitMocks.setComponentValue).toHaveBeenCalledWith({
      event: { id: "select_view", view: "sp500", nonce: expect.any(Number) },
    });
  });

  it("emits a local view and ignores the already active family and view", async () => {
    const user = userEvent.setup();
    render(<MarketResearchNavigation {...props(payload)} />);
    await user.click(screen.getByRole("button", { name: /시장 환경/ }));
    await user.click(screen.getByRole("button", { name: "선물 매크로" }));
    await user.click(screen.getByRole("button", { name: "경제 사이클" }));
    expect(streamlitMocks.setComponentValue).toHaveBeenCalledTimes(1);
    expect(streamlitMocks.setComponentValue).toHaveBeenCalledWith({
      event: { id: "select_view", view: "futures-macro", nonce: expect.any(Number) },
    });
  });

  it("shows a bounded empty state without a payload", () => {
    render(<MarketResearchNavigation {...props()} />);
    expect(screen.getByText("Market Research 탐색을 불러오지 못했습니다.")).toBeInTheDocument();
    expect(streamlitMocks.setComponentValue).not.toHaveBeenCalled();
  });
});
