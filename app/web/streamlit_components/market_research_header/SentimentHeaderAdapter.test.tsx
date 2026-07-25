// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import SentimentHero from "../sentiment_workbench/src/SentimentHero";
import type { SentimentWorkbenchPayload } from "../sentiment_workbench/src/SentimentWorkbench";

afterEach(cleanup);

describe("SentimentHero shared header adapter", () => {
  it("keeps both source tones, actions, dates, and caution metadata", () => {
    const onAction = vi.fn();
    const payload = {
      axes: {
        investor_survey: {
          direction_label: "낙관 우위",
          latest_date: "2026-07-23",
          tone: "positive",
        },
        market_behavior: {
          direction_label: "공포",
          latest_date: "2026-07-24",
          tone: "warning",
        },
      },
      command: {
        actions: [
          {
            detail: "심리 자료를 갱신합니다.",
            id: "refresh",
            kind: "primary",
            label: "자료 갱신",
          },
          {
            detail: "DB에서 다시 읽습니다.",
            id: "reload",
            kind: "secondary",
            label: "다시 읽기",
          },
        ],
      },
      cross_read: {
        confidence_note: "두 소스의 시차를 함께 확인합니다.",
        meaning: "시장 행동과 개인투자자 설문을 합성하지 않고 함께 읽습니다.",
        status: "두 심리축 엇갈림",
      },
      freshness: {
        stale_count: 1,
      },
      summary: {
        headline: "시장 행동은 공포, 설문은 낙관 우위",
        phase_label: "합성하지 않고 두 축을 함께 관찰",
      },
    } as unknown as SentimentWorkbenchPayload;

    const { container } = render(
      <SentimentHero
        onAction={onAction}
        payload={payload}
        pendingActionLabel="자료 갱신"
      />,
    );

    expect(container.querySelector(".research-header--sentiment")).not.toBeNull();
    expect(screen.getByRole("heading", { level: 2, name: "시장 행동은 공포, 설문은 낙관 우위" })).toBeTruthy();
    expect(screen.getByText("공포").closest(".research-header__fact")?.querySelector(".research-header__state-dot")).not.toBeNull();
    expect(screen.getByText("낙관 우위").closest(".research-header__fact")?.querySelector(".research-header__state-dot")).not.toBeNull();
    expect(screen.getByText("CNN 2026-07-24")).toBeTruthy();
    expect(screen.getByText("AAII 2026-07-23")).toBeTruthy();
    expect(screen.getByText("합성점수 없음")).toBeTruthy();
    expect(screen.getByText("매수·매도 신호 아님")).toBeTruthy();
    expect(screen.getByText("stale 1 · 상세 근거 확인")).toBeTruthy();
    expect(screen.getByText("요청 전송 · 자료 갱신")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "자료 갱신" }));
    expect(onAction).toHaveBeenCalledWith(expect.objectContaining({ id: "refresh" }));
  });
});
