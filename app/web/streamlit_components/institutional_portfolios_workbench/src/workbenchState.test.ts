import { describe, expect, it } from "vitest";
import {
  STUDIO_DESTINATIONS,
  filterQuarterReviewRows,
  filterSortAndPaginateHoldings,
  managerDragExceededThreshold,
  managerDragScrollTop,
  queriesMatch,
  studioDestination,
} from "./workbenchState";

const rows = [
  {
    issuer_name: "Zulu Holdings",
    symbol: "ZZZ",
    cusip: "000000003",
    sector: "Technology",
    mapping_status: "mapped",
    weight_pct: 10,
    reported_value: 100,
  },
  {
    issuer_name: "Alpha Unmapped",
    symbol: null,
    cusip: "000000001",
    sector: "Unmapped",
    mapping_status: "unmapped",
    weight_pct: 30,
    reported_value: 300,
  },
  {
    issuer_name: "Beta Holdings",
    symbol: "BBB",
    cusip: "000000002",
    sector: "Financial Services",
    mapping_status: "mapped",
    weight_pct: 20,
    reported_value: 200,
  },
];

describe("filterSortAndPaginateHoldings", () => {
  it("filters before stable sorting and paginating", () => {
    const result = filterSortAndPaginateHoldings({
      rows,
      search: "holdings",
      mappingFilter: "mapped",
      sectorFilter: "all",
      sort: "issuer_asc",
      page: 2,
      pageSize: 1,
    });

    expect(result.filteredRows.map((row) => row.symbol)).toEqual(["BBB", "ZZZ"]);
    expect(result.visibleRows.map((row) => row.symbol)).toEqual(["ZZZ"]);
    expect(result.totalPages).toBe(2);
    expect(result.safePage).toBe(2);
    expect(result.start).toBe(2);
    expect(result.end).toBe(2);
  });

  it("clamps an out-of-range page after a filter reduces results", () => {
    const result = filterSortAndPaginateHoldings({
      rows,
      search: "000000001",
      mappingFilter: "unresolved",
      sectorFilter: "all",
      sort: "weight_desc",
      page: 9,
      pageSize: 50,
    });

    expect(result.visibleRows.map((row) => row.issuer_name)).toEqual(["Alpha Unmapped"]);
    expect(result.safePage).toBe(1);
    expect(result.start).toBe(1);
    expect(result.end).toBe(1);
  });
});

describe("queriesMatch", () => {
  it("matches trimmed lowercase ticker to the uppercase server response", () => {
    expect(queriesMatch(" nvda ", "NVDA")).toBe(true);
  });

  it("matches mixed-case issuer queries", () => {
    expect(queriesMatch("Nvidia Corp", "NVIDIA CORP")).toBe(true);
  });

  it("treats two cleared manager-search queries as the same response", () => {
    expect(queriesMatch(" ", "")).toBe(true);
  });
});

describe("institutional research studio navigation", () => {
  it("keeps one canonical destination list for desktop rail and mobile switcher", () => {
    expect(STUDIO_DESTINATIONS.map((item) => item.id)).toEqual([
      "overview",
      "quarter_review",
      "holdings",
      "security",
      "popularity",
    ]);
    expect(STUDIO_DESTINATIONS.map((item) => item.label)).toEqual([
      "포트폴리오 맥락",
      "분기 리뷰",
      "전체 보유",
      "종목 상세",
      "기관 보유 랭킹",
    ]);
  });

  it("resolves the visible destination context", () => {
    expect(studioDestination("overview").shortLabel).toBe("맥락");
    expect(studioDestination("popularity").description).toContain("다기관");
    expect(studioDestination("quarter_review").label).toBe("분기 리뷰");
  });
});

describe("quarter review filters", () => {
  const changes = [
    { change_type: "ADD", holding_symbol: "AAPL", issuer_name: "Apple Inc", cusip: "037833100" },
    { change_type: "DROP", holding_symbol: "IBM", issuer_name: "IBM Corp", cusip: "459200101" },
  ];

  it("combines change type with symbol, issuer, or CUSIP search", () => {
    expect(filterQuarterReviewRows(changes, { changeType: "ADD", query: "apple" })).toEqual([changes[0]]);
    expect(filterQuarterReviewRows(changes, { changeType: "all", query: "459200101" })).toEqual([changes[1]]);
  });
});

describe("manager rail drag scrolling", () => {
  it("moves scrollTop opposite to the pointer delta and never below zero", () => {
    expect(managerDragScrollTop(120, 300, 240)).toBe(180);
    expect(managerDragScrollTop(20, 100, 150)).toBe(0);
  });

  it("suppresses selection only after the pointer crosses the drag threshold", () => {
    expect(managerDragExceededThreshold(100, 104)).toBe(false);
    expect(managerDragExceededThreshold(100, 107)).toBe(true);
  });
});
