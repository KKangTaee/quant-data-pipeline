import type { ReferenceItem, ReferenceScope } from "./contracts";

const SCORE = {
  exactTitleOrAlias: 400,
  titleOrAliasPrefix: 300,
  keyword: 200,
  summaryOrBody: 100,
} as const;

function normalize(value: string): string {
  return String(value || "").toLocaleLowerCase().trim().replace(/\s+/g, " ");
}

function scoreItem(item: ReferenceItem, normalizedQuery: string, tokens: string[]): number {
  const title = normalize(item.title);
  const aliases = item.aliases.map(normalize);
  const keywords = item.keywords.map(normalize);
  let score = 0;

  if (title === normalizedQuery || aliases.includes(normalizedQuery)) {
    score += SCORE.exactTitleOrAlias * 1_000;
  } else if (title.startsWith(normalizedQuery) || aliases.some((alias) => alias.startsWith(normalizedQuery))) {
    score += SCORE.titleOrAliasPrefix * 1_000;
  }

  for (const token of tokens) {
    if (title === token || aliases.includes(token)) {
      score += SCORE.exactTitleOrAlias;
    } else if (title.startsWith(token) || aliases.some((alias) => alias.startsWith(token))) {
      score += SCORE.titleOrAliasPrefix;
    } else if (keywords.some((keyword) => keyword === token || keyword.includes(token))) {
      score += SCORE.keyword;
    } else {
      score += SCORE.summaryOrBody;
    }
  }
  return score;
}

export function searchReferenceItems(
  items: ReferenceItem[],
  query: string,
  scope: ReferenceScope,
): ReferenceItem[] {
  const scopedItems = items.filter((item) => scope === "all" || item.kind === scope);
  const normalizedQuery = normalize(query);
  if (!normalizedQuery) {
    return scopedItems;
  }

  const tokens = normalizedQuery.split(" ").filter(Boolean);
  return scopedItems
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => {
      const searchText = normalize(item.search_text);
      return tokens.every((token) => searchText.includes(token));
    })
    .map(({ item, index }) => ({
      item,
      index,
      score: scoreItem(item, normalizedQuery, tokens),
    }))
    .sort((left, right) => right.score - left.score || left.index - right.index)
    .map(({ item }) => item);
}
