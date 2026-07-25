// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import MacroContextSection from "../futures_macro_workbench/src/MacroContextSection";

afterEach(cleanup);

describe("MacroContextSection shared header adapter", () => {
  it("preserves actions, observation facts, pending notice, and evidence metadata", () => {
    const onAction = vi.fn();

    const { container } = render(
      <MacroContextSection
        command={{
          actions: [
            {
              detail: "저장 일봉을 갱신합니다.",
              id: "daily_refresh",
              kind: "primary",
              label: "일봉 갱신",
            },
            {
              detail: "DB에서 다시 읽습니다.",
              id: "reload",
              kind: "secondary",
              label: "다시 읽기",
            },
          ],
          detail: "일봉 17/17개 · 기준일 2026-07-23",
          title: "선물 매크로 패턴",
        }}
        hero={{
          as_of_date: "2026-07-23",
          coverage_label: "최근 1 · 5 · 20거래일",
          evidence: ["현재 체제: 혼재 체제", "전환 상태: 충돌"],
          kicker: "단기 방향 진단",
          observation_status: "OBSERVED",
          summary: "단일 방향 우위가 약합니다.",
          title: "혼재 체제",
          today_summary: "금리 부담이 강화됐습니다.",
          transition_label: "충돌",
        }}
        onAction={onAction}
        pendingActionId=""
        sessionEvidence={{
          latest_final_session: "2026-07-23",
          pending_session: "2026-07-24",
          status: "PENDING_SESSION_FINALIZATION",
        }}
      />,
    );

    expect(container.querySelector(".research-header--futures")).not.toBeNull();
    expect(screen.getByRole("heading", { level: 2, name: "혼재 체제" })).toBeTruthy();
    expect(screen.getByText("관측 완료")).toBeTruthy();
    expect(screen.getByText("2026-07-23")).toBeTruthy();
    expect(screen.getByText("최근 1 · 5 · 20거래일")).toBeTruthy();
    expect(screen.getByText("현재 체제: 혼재 체제")).toBeTruthy();
    expect(screen.getByText(/2026-07-24 데이터는 완료 전/)).toBeTruthy();
    expect(screen.getByText("관측 완료").closest(".research-header__fact")?.querySelector(".research-header__state-dot")).not.toBeNull();
    expect(screen.getByText("2026-07-23").closest(".research-header__fact")?.querySelector(".research-header__state-dot")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "일봉 갱신" }));
    expect(onAction).toHaveBeenCalledWith(expect.objectContaining({ id: "daily_refresh" }));
  });
});
