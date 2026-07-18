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

export function normalizeQuery(value: string | null | undefined) {
  return String(value || "").trim().toLocaleUpperCase();
}

export function queriesMatch(left: string | null | undefined, right: string | null | undefined) {
  const normalizedLeft = normalizeQuery(left);
  const normalizedRight = normalizeQuery(right);
  return normalizedLeft === normalizedRight;
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
