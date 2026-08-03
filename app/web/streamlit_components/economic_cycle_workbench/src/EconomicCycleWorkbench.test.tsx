import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import {
  EconomicCycleWorkbenchView,
  projectActualCoordinate,
  resolveMapDirectionPhase,
  selectCycleMapCheckpoints,
  type CyclePayload,
} from "./EconomicCycleWorkbench";

const ASSET_GROUPS = [
  ["rates", "채권·금리"],
  ["equities", "주식"],
  ["gold", "금"],
  ["dollar", "달러"],
  ["commodities", "원자재"],
] as const;

function asset(assetGroup: typeof ASSET_GROUPS[number][0], label: string) {
  return {
    asset_group: assetGroup,
    label,
    analysis_status: "READY" as const,
    coverage: "SUFFICIENT" as const,
    economic_state: { summary: "현재 경제 상태", observations: [] },
    current_movement: [],
    observed_pathways: [],
    current_interpretation: ["현재 해석을 유지합니다."],
    next_check_conditions: ["다음 발표에서 같은 경로를 확인합니다."],
    narrative: "자산 설명",
    summary: "자산 요약",
    context: "자산 맥락",
    is_directional_forecast: false as const,
  };
}

function fixture(): CyclePayload {
  const dates = [
    "2025-12-31",
    "2026-01-31",
    "2026-02-28",
    "2026-03-31",
    "2026-04-30",
    "2026-05-31",
    "2026-06-30",
  ];
  return {
    schema_version: "economic_cycle_v3",
    status: "READY",
    as_of_date: "2026-06-30",
    model_version: "cycle-observed-v1",
    headline: {
      phase: "contraction",
      phase_label: "위축",
      summary: "실물 수준과 모멘텀이 함께 약한 상태입니다.",
    },
    observed_state: {
      as_of_date: "2026-06-30",
      level: -0.60,
      momentum: -0.30,
      phase: "contraction",
      duration_months: 3,
      confidence: "MEDIUM",
      confidence_label: "보통",
      revision_sensitivity: "STABLE",
      revision_sensitivity_label: "안정",
      available_series: 8,
      data_status: "READY",
    },
    data_freshness: {
      status: "REFRESH_AVAILABLE",
      persisted_as_of_date: "2026-07-21",
      target_as_of_date: "2026-07-24",
      last_successful_collection_at: "2026-07-21 09:31:12",
      latest_source_observation_date: "2026-06-30",
      refresh_required: true,
      message: "현재 계산일 2026-07-21 · 최신 계산 가능일 2026-07-24",
      action: {
        id: "refresh_economic_cycle_data",
        label: "최신 발표 확인·재계산",
        enabled: true,
      },
    },
    recent_changes: [
      { horizon_months: 1, label: "최근 1개월", status: "MIXED", status_label: "혼조", composite_delta: 0.02, breadth: 0.50, available_pairs: 8 },
      { horizon_months: 3, label: "최근 3개월", status: "WEAKENING", status_label: "약화", composite_delta: -0.30, breadth: 0.25, available_pairs: 8 },
      { horizon_months: 6, label: "최근 6개월", status: "WEAKENING", status_label: "약화", composite_delta: -0.45, breadth: 0.25, available_pairs: 8 },
    ],
    transition_monitor: {
      observed_phase: "contraction",
      anchor_phase: "recovery",
      anchor_started_at: "2025-08-31",
      anchor_source: "CONFIRMED",
      anchor_source_label: "조건 확인",
      anchor_confirmed_at: "2025-08-31",
      target_phase: "expansion",
      status: "WATCH",
      status_label: "전환 조건 관찰",
      conditions_met: 1,
      conditions_total: 3,
      candidate_started_at: "2026-05-31",
      non_adjacent_observation: true,
      conditions: [
        { condition_id: "persistence", label: "지속성", status: "UNMET", threshold: "두 번 연속 확인" },
        { condition_id: "diffusion", label: "확산도", status: "UNAVAILABLE", threshold: "6개 이상 비교 필요" },
        { condition_id: "corroboration", label: "활동·고용 동반 확인", status: "MET", threshold: "두 축 동반 개선" },
      ],
      context: [],
    },
    cycle_map: {
      phase_order: ["recovery", "expansion", "slowdown", "contraction"],
      points: dates.map((date, index) => ({
        date,
        level: -1.20 + index * 0.10,
        momentum: -0.60 + index * 0.05,
        phase: "contraction" as const,
        phase_label: "위축",
        nber_recession: false,
        confidence: "MEDIUM",
        revision_sensitivity: "STABLE",
      })),
    },
    evidence: [],
    market_implications: ASSET_GROUPS.map(([group, label]) => asset(group, label)),
    limitations: ["확률 예측이 아닙니다."],
  };
}

describe("EconomicCycleWorkbenchView", () => {
  it("renders the decision flow and preserves the five asset checkpoint blocks", () => {
    const html = renderToStaticMarkup(<EconomicCycleWorkbenchView payload={fixture()} />);

    expect(html.indexOf("현재 관측 국면")).toBeLessThan(html.indexOf("핵심 시점으로 본 실제 경로"));
    expect(html.indexOf("핵심 시점으로 본 실제 경로")).toBeLessThan(html.indexOf("현재 관측과 전환 기준"));
    expect(html.indexOf("현재 관측과 전환 기준")).toBeLessThan(html.indexOf("자산별 확인 포인트"));
    expect(html).not.toContain("현재와 앞으로 1·2개월");
    expect(html).not.toContain("전망 확률");

    const positions = ASSET_GROUPS.map(([, label]) => html.indexOf(
      `<span>${label}</span><strong>측정된 시장 경로와 현재 움직임</strong>`,
    ));
    expect(positions.every((position) => position >= 0)).toBe(true);
    expect(positions).toEqual([...positions].sort((left, right) => left - right));
    expect(html).toContain("현재 움직임");
    expect(html).toContain("함께 관찰된 경로");
    expect(html).toContain("현재 해석");
    expect(html).toContain("향후 1·2개월 확인 조건");
  });

  it("uses the same fixed minus-two to two domain for level and momentum", () => {
    expect(projectActualCoordinate({ level: 2, momentum: 2 })).toEqual({ x: 308, y: 48 });
    expect(projectActualCoordinate({ level: -2, momentum: -2 })).toEqual({ x: 52, y: 272 });
  });

  it("selects and labels six-month, three-month, one-month and current checkpoints", () => {
    const payload = fixture();
    const checkpoints = selectCycleMapCheckpoints(payload.cycle_map.points);
    const watchHtml = renderToStaticMarkup(<EconomicCycleWorkbenchView payload={fixture()} />);
    const maintain = fixture();
    maintain.transition_monitor = {
      ...maintain.transition_monitor!,
      status: "MAINTAIN",
      status_label: "현재 국면 유지",
    };
    const maintainHtml = renderToStaticMarkup(<EconomicCycleWorkbenchView payload={maintain} />);

    expect(checkpoints.map((point) => point.date)).toEqual([
      "2025-12-31",
      "2026-03-31",
      "2026-05-31",
      "2026-06-30",
    ]);
    expect(watchHtml).toContain("6개월 전");
    expect(watchHtml).toContain("3개월 전");
    expect(watchHtml).toContain("1개월 전");
    expect(watchHtml).toContain("현재</text>");
    expect(watchHtml).toContain('class="transition-pressure-arrow"');
    expect(watchHtml).toContain("예측 경로가 아님");
    expect(maintainHtml).not.toContain('class="transition-pressure-arrow"');
  });

  it("resolves a non-adjacent map arrow from the current observed phase", () => {
    const payload = fixture();

    expect(resolveMapDirectionPhase(payload.transition_monitor, "contraction")).toBe("recovery");
  });

  it("puts the current observation before the anchor and explains the structural target", () => {
    const html = renderToStaticMarkup(<EconomicCycleWorkbenchView payload={fixture()} />);

    expect(html.indexOf("현재 관측 위축")).toBeLessThan(html.indexOf("전환 기준 앵커"));
    expect(html).toContain("모델 기준과 불일치");
    expect(html).toContain("회복 → 확장 확인 조건");
    expect(html).toContain("확장 가능성이 높다는 예측이 아닙니다");
    expect(html).toContain("조건 확인 · 2025년 08월");
  });

  it("distinguishes unavailable transition evidence from an unmet condition", () => {
    const html = renderToStaticMarkup(<EconomicCycleWorkbenchView payload={fixture()} />);

    expect(html).toContain("condition-unavailable");
    expect(html).toContain("자료 부족");
  });

  it("separates freshness dates and shows expected refresh duration", () => {
    const html = renderToStaticMarkup(<EconomicCycleWorkbenchView payload={fixture()} />);

    expect(html).toContain("마지막 성공 수집");
    expect(html).toContain("2026-07-21 09:31:12");
    expect(html).toContain("계산 기준일");
    expect(html).toContain("사용 원천 최신일");
    expect(html).toContain("보통 1분 내외");
  });

  it("shows all phase colors and accessible month details in the regime ribbon", () => {
    const payload = fixture();
    payload.cycle_map.points = payload.cycle_map.points.map((point, index) => ({
      ...point,
      phase: (["recovery", "expansion", "slowdown", "contraction"] as const)[index % 4],
      nber_recession: index === 0,
    }));
    const html = renderToStaticMarkup(<EconomicCycleWorkbenchView payload={payload} />);

    expect(html).toContain('class="legend-recovery"');
    expect(html).toContain('class="legend-expansion"');
    expect(html).toContain('class="legend-slowdown"');
    expect(html).toContain('class="legend-contraction"');
    expect(html).toContain('role="tooltip"');
    expect(html).toContain("판단 신뢰도 보통");
    expect(html).toContain("수정 민감도 안정");
    expect(html).toContain("NBER 침체");
  });
});
