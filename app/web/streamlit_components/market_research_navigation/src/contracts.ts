export type MarketResearchView = { id: string; label: string };

export type MarketResearchFamily = {
  id: string;
  label: string;
  description: string;
  views: MarketResearchView[];
};

export type MarketResearchNavigationPayload = {
  schema_version: "market_research_navigation_v1";
  eyebrow: string;
  title: string;
  description: string;
  active_family: string;
  active_view: string;
  families: MarketResearchFamily[];
};
