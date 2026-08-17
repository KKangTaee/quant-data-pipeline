export type HoldingStateRow = {
  issuer_name: string;
  symbol?: string | null;
  cusip?: string | null;
  sector: string;
  mapping_status?: string | null;
  weight_pct: number;
  reported_value: number;
};

export type MappingFilter = "all" | "mapped" | "unresolved";
export type HoldingSort = "weight_desc" | "value_desc" | "issuer_asc";
export type StudioView = "overview" | "quarter_review" | "holdings" | "security" | "popularity";

export const STUDIO_DESTINATIONS: ReadonlyArray<{
  id: StudioView;
  label: string;
  shortLabel: string;
  description: string;
}> = [
  {
    id: "overview",
    label: "포트폴리오 맥락",
    shortLabel: "맥락",
    description: "집중도, 분기 변화와 섹터 노출",
  },
  {
    id: "quarter_review",
    label: "분기 리뷰",
    shortLabel: "분기 리뷰",
    description: "이전 분기 결과와 보유 변화",
  },
  {
    id: "holdings",
    label: "전체 보유",
    shortLabel: "전체 보유",
    description: "13F 보유 종목 검색과 필터",
  },
  {
    id: "security",
    label: "종목 상세",
    shortLabel: "종목 상세",
    description: "가격 흐름과 보유 기관 역조회",
  },
  {
    id: "popularity",
    label: "기관 보유 랭킹",
    shortLabel: "랭킹",
    description: "동일 분기 기준 다기관 보유 순위",
  },
];

export function studioDestination(view: StudioView) {
  return STUDIO_DESTINATIONS.find((item) => item.id === view) || STUDIO_DESTINATIONS[0];
}

export function normalizeQuery(value: string | null | undefined) {
  return String(value || "").trim().toLocaleUpperCase();
}

export function queriesMatch(left: string | null | undefined, right: string | null | undefined) {
  const normalizedLeft = normalizeQuery(left);
  const normalizedRight = normalizeQuery(right);
  return normalizedLeft === normalizedRight;
}

export function signedPercentagePointLabel(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) return "-";
  const numeric = Number(value);
  return `${numeric > 0 ? "+" : ""}${numeric.toFixed(2)}%p`;
}

export function filterSortAndPaginateHoldings<T extends HoldingStateRow>(options: {
  rows: T[];
  search: string;
  mappingFilter: MappingFilter;
  sectorFilter: string;
  sort: HoldingSort;
  page: number;
  pageSize: number;
}) {
  const query = options.search.trim().toLocaleLowerCase();
  const filteredRows = options.rows
    .map((row, index) => ({ row, index }))
    .filter(({ row }) => {
      const mapped = row.mapping_status === "mapped" && Boolean(row.symbol);
      const matchesQuery =
        !query ||
        [row.symbol, row.issuer_name, row.cusip].some((value) =>
          String(value || "").toLocaleLowerCase().includes(query)
        );
      const matchesMapping =
        options.mappingFilter === "all" ||
        (options.mappingFilter === "mapped" ? mapped : !mapped);
      const matchesSector = options.sectorFilter === "all" || row.sector === options.sectorFilter;
      return matchesQuery && matchesMapping && matchesSector;
    })
    .sort((left, right) => {
      let comparison = 0;
      if (options.sort === "issuer_asc") {
        comparison = left.row.issuer_name.localeCompare(right.row.issuer_name, "ko");
      } else if (options.sort === "value_desc") {
        comparison = Number(right.row.reported_value || 0) - Number(left.row.reported_value || 0);
      } else {
        comparison = Number(right.row.weight_pct || 0) - Number(left.row.weight_pct || 0);
      }
      return comparison || left.index - right.index;
    })
    .map(({ row }) => row);
  const pageSize = Math.max(1, Math.floor(options.pageSize));
  const totalPages = Math.max(1, Math.ceil(filteredRows.length / pageSize));
  const safePage = Math.max(1, Math.min(Math.floor(options.page), totalPages));
  const offset = (safePage - 1) * pageSize;
  const visibleRows = filteredRows.slice(offset, offset + pageSize);

  return {
    filteredRows,
    visibleRows,
    totalPages,
    safePage,
    start: filteredRows.length ? offset + 1 : 0,
    end: Math.min(offset + pageSize, filteredRows.length),
  };
}

export type QuarterReviewFilterRow = {
  change_type: string;
  holding_symbol?: string | null;
  issuer_name?: string | null;
  cusip?: string | null;
};

export function filterQuarterReviewRows<T extends QuarterReviewFilterRow>(
  rows: T[],
  options: { changeType: string; query: string }
) {
  const query = normalizeQuery(options.query);
  return rows.filter((row) => {
    const matchesType = options.changeType === "all" || row.change_type === options.changeType;
    const matchesQuery =
      !query ||
      [row.holding_symbol, row.issuer_name, row.cusip].some((value) => normalizeQuery(value).includes(query));
    return matchesType && matchesQuery;
  });
}
