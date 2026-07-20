import { describe, expect, it } from "vitest";
import type { ReferenceItem } from "./contracts";
import { searchReferenceItems } from "./search";

function item(
  id: string,
  fields: Partial<ReferenceItem> & Pick<ReferenceItem, "kind" | "title">,
): ReferenceItem {
  const aliases = fields.aliases || [];
  const keywords = fields.keywords || [];
  const summary = fields.summary || "";
  const meaning = fields.meaning || "";
  return {
    id,
    kind: fields.kind,
    category: fields.category || "테스트",
    title: fields.title,
    summary,
    aliases,
    keywords,
    related_surfaces: fields.related_surfaces || ["Overview"],
    meaning,
    impact: fields.impact || "영향",
    next_action: fields.next_action || "다음 행동",
    related_item_ids: fields.related_item_ids || [],
    destination: fields.destination || "overview",
    search_text: [fields.title, ...aliases, ...keywords, summary, meaning].join(" ").toLocaleLowerCase(),
  };
}

const rankedItems = [
  item("summary", {
    kind: "playbook",
    title: "검증 근거 확인",
    summary: "not 상태의 원인을 설명합니다",
  }),
  item("keyword", {
    kind: "concept",
    title: "실행 상태",
    keywords: ["not"],
  }),
  item("alias-prefix", {
    kind: "journey",
    title: "검증 흐름",
    aliases: ["not run guide"],
  }),
  item("exact", {
    kind: "concept",
    title: "NOT",
  }),
];

describe("searchReferenceItems", () => {
  it("preserves catalog order for an empty query", () => {
    expect(searchReferenceItems(rankedItems, "", "all").map((row) => row.id)).toEqual(
      rankedItems.map((row) => row.id),
    );
  });

  it("ranks exact title, alias prefix, keyword, then summary matches", () => {
    expect(searchReferenceItems(rankedItems, "not", "all").map((row) => row.id)).toEqual([
      "exact",
      "alias-prefix",
      "keyword",
      "summary",
    ]);
  });

  it("requires every normalized token to match", () => {
    const items = [
      item("both", { kind: "playbook", title: "시나리오", keywords: ["stale", "update"] }),
      item("one", { kind: "playbook", title: "시나리오", keywords: ["stale"] }),
    ];
    expect(searchReferenceItems(items, " STALE   update ", "all").map((row) => row.id)).toEqual(["both"]);
  });

  it("filters journey, concept, and playbook scopes", () => {
    expect(searchReferenceItems(rankedItems, "", "journey").map((row) => row.kind)).toEqual(["journey"]);
    expect(searchReferenceItems(rankedItems, "", "concept").map((row) => row.kind)).toEqual([
      "concept",
      "concept",
    ]);
    expect(searchReferenceItems(rankedItems, "", "playbook").map((row) => row.kind)).toEqual(["playbook"]);
  });

  it("normalizes case and returns an empty list when nothing matches", () => {
    expect(searchReferenceItems(rankedItems, "NoT", "all")).toHaveLength(4);
    expect(searchReferenceItems(rankedItems, "없는검색어", "all")).toEqual([]);
  });
});
