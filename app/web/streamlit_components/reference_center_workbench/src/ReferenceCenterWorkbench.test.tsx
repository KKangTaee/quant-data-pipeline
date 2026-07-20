import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ComponentProps } from "streamlit-component-lib";
import type { ReferenceCenterPayload, ReferenceItem, ReferenceKind } from "./contracts";

const streamlitMocks = vi.hoisted(() => ({
  setComponentReady: vi.fn(),
  setComponentValue: vi.fn(),
  setFrameHeight: vi.fn(),
}));

vi.mock("streamlit-component-lib", () => ({
  Streamlit: streamlitMocks,
  withStreamlitConnection: <T,>(component: T) => component,
}));

import { ReferenceCenterWorkbench } from "./ReferenceCenterWorkbench";

function item(
  id: string,
  kind: ReferenceKind,
  title: string,
  overrides: Partial<ReferenceItem> = {},
): ReferenceItem {
  return {
    id,
    kind,
    category: overrides.category || "테스트",
    title,
    summary: overrides.summary || `${title} 요약`,
    aliases: overrides.aliases || [],
    keywords: overrides.keywords || [],
    related_surfaces: overrides.related_surfaces || ["Overview"],
    meaning: overrides.meaning || `${title}의 뜻입니다.`,
    impact: overrides.impact || `${title}의 영향입니다.`,
    next_action: overrides.next_action || `${title}의 다음 행동입니다.`,
    related_item_ids: overrides.related_item_ids || [],
    destination: overrides.destination === undefined ? "overview" : overrides.destination,
    search_text: overrides.search_text || `${title} ${overrides.summary || ""} ${(overrides.keywords || []).join(" ")}`.toLocaleLowerCase(),
  };
}

const journeys = [
  item("journey.market_understanding", "journey", "시장 이해", {
    related_item_ids: ["status.not_run"],
  }),
  item("journey.institutional_portfolios", "journey", "기관 보유"),
  item("journey.data_preparation", "journey", "데이터 준비"),
  item("journey.candidate_creation", "journey", "후보 생성"),
  item("journey.validation_decision", "journey", "검증과 판단"),
  item("journey.monitoring", "journey", "선정 후 추적"),
];

const notRun = item("status.not_run", "concept", "NOT_RUN", {
  category: "검증 상태",
  keywords: ["미실행", "validation"],
  related_surfaces: ["Practical Validation"],
  destination: "practical_validation",
  search_text: "not_run 미실행 validation practical validation",
});

const playbook = item("playbook.validation", "playbook", "검증 문제 해결", {
  keywords: ["not_run"],
  destination: "practical_validation",
  search_text: "검증 문제 해결 not_run practical validation",
});

function payload(overrides: Partial<ReferenceCenterPayload> = {}): ReferenceCenterPayload {
  return {
    schema_version: "reference_center_v1",
    component: "ReferenceCenterWorkbench",
    filters: [
      { id: "all", label: "전체" },
      { id: "journey", label: "사용 흐름" },
      { id: "concept", label: "상태·용어" },
      { id: "playbook", label: "문제 해결" },
    ],
    journeys: journeys.map((row) => row.id),
    items: [...journeys, notRun, playbook],
    initial_item_id: null,
    invalid_initial_item: false,
    empty_state: {
      title: "검색 결과가 없습니다",
      description: "다른 검색어를 입력하세요.",
      suggestions: ["NOT_RUN", "모니터링"],
    },
    ...overrides,
  };
}

function props(value?: ReferenceCenterPayload): ComponentProps {
  return { args: value ? { payload: value } : {} } as ComponentProps;
}

afterEach(cleanup);

describe("ReferenceCenterWorkbench", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders search first, four filters, and all six journey cards", () => {
    render(<ReferenceCenterWorkbench {...props(payload())} />);

    expect(screen.getAllByRole("searchbox")[0]).toHaveAttribute("aria-label", "Reference 검색");
    for (const label of ["전체", "사용 흐름", "상태·용어", "문제 해결"]) {
      expect(screen.getByRole("button", { name: label })).toBeInTheDocument();
    }
    expect(screen.getAllByRole("button", { name: /^사용 흐름:/ })).toHaveLength(6);
  });

  it("searches and filters locally without emitting a Streamlit event", async () => {
    const user = userEvent.setup();
    render(<ReferenceCenterWorkbench {...props(payload())} />);

    await user.type(screen.getByRole("searchbox", { name: "Reference 검색" }), "NOT_RUN");
    expect(screen.getByRole("button", { name: "Reference 열기: NOT_RUN" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Reference 열기: 시장 이해" })).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "문제 해결" }));
    expect(screen.getByRole("button", { name: "Reference 열기: 검증 문제 해결" })).toBeInTheDocument();
    expect(streamlitMocks.setComponentValue).not.toHaveBeenCalled();
  });

  it("opens detail, navigates to a related item locally, and closes explicitly", async () => {
    const user = userEvent.setup();
    render(<ReferenceCenterWorkbench {...props(payload())} />);

    await user.click(screen.getByRole("button", { name: "사용 흐름: 시장 이해" }));
    expect(screen.getByRole("dialog", { name: "시장 이해 상세" })).toBeInTheDocument();
    expect(screen.getByText("뜻/목적")).toBeInTheDocument();
    expect(screen.getByText("어디서 보이나")).toBeInTheDocument();
    expect(screen.getByText("영향")).toBeInTheDocument();
    expect(screen.getByText("다음 행동")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "관련 항목 열기: NOT_RUN" }));
    expect(screen.getByRole("dialog", { name: "NOT_RUN 상세" })).toBeInTheDocument();
    expect(streamlitMocks.setComponentValue).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "상세 닫기" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("opens an initial deep-link item and emits only a typed destination event", async () => {
    const user = userEvent.setup();
    render(<ReferenceCenterWorkbench {...props(payload({ initial_item_id: "status.not_run" }))} />);

    expect(screen.getByRole("dialog", { name: "NOT_RUN 상세" })).toBeInTheDocument();
    expect(streamlitMocks.setFrameHeight).toHaveBeenCalledWith(760);
    await user.click(screen.getByRole("button", { name: "화면으로 이동" }));

    expect(streamlitMocks.setComponentValue).toHaveBeenCalledTimes(1);
    expect(streamlitMocks.setComponentValue).toHaveBeenCalledWith({
      event: expect.objectContaining({
        id: "navigate_to_surface",
        destination: "practical_validation",
        item_id: "status.not_run",
        nonce: expect.any(String),
      }),
    });
  });

  it("keeps search and selected detail state across a payload rerender", () => {
    const value = payload();
    const { rerender } = render(<ReferenceCenterWorkbench {...props(value)} />);
    const search = screen.getByRole("searchbox", { name: "Reference 검색" }) as HTMLInputElement;

    fireEvent.change(search, { target: { value: "NOT_RUN" } });
    fireEvent.click(screen.getByRole("button", { name: "Reference 열기: NOT_RUN" }));
    rerender(<ReferenceCenterWorkbench {...props({ ...value, empty_state: { ...value.empty_state } })} />);

    expect(screen.getByRole("searchbox", { name: "Reference 검색" })).toHaveValue("NOT_RUN");
    expect(screen.getByRole("dialog", { name: "NOT_RUN 상세" })).toBeInTheDocument();
  });

  it("shows zero-result, invalid-link, missing, and empty payload states", async () => {
    const user = userEvent.setup();
    const { rerender } = render(<ReferenceCenterWorkbench {...props(payload())} />);
    await user.type(screen.getByRole("searchbox", { name: "Reference 검색" }), "없는검색어");
    expect(screen.getByText("검색 결과가 없습니다")).toBeInTheDocument();

    rerender(<ReferenceCenterWorkbench {...props(payload({ invalid_initial_item: true }))} />);
    expect(screen.getByText("변경되었거나 삭제된 Reference 항목입니다.")).toBeInTheDocument();

    rerender(<ReferenceCenterWorkbench {...props()} />);
    expect(screen.getByText("Reference payload를 불러오지 못했습니다.")).toBeInTheDocument();

    rerender(<ReferenceCenterWorkbench {...props(payload({ items: [], journeys: [] }))} />);
    expect(screen.getByText("Reference 콘텐츠를 준비하지 못했습니다.")).toBeInTheDocument();
  });
});
