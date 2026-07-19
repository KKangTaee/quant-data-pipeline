import { describe, expect, it } from "vitest";
import { filterSortAndPaginateHoldings, queriesMatch } from "./workbenchState";

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
