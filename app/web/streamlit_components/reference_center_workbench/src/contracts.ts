export type ReferenceKind = "journey" | "concept" | "playbook";
export type ReferenceScope = "all" | ReferenceKind;

export type ReferenceItem = {
  id: string;
  kind: ReferenceKind;
  category: string;
  title: string;
  summary: string;
  aliases: string[];
  keywords: string[];
  related_surfaces: string[];
  meaning: string;
  impact: string;
  next_action: string;
  related_item_ids: string[];
  destination: string | null;
  search_text: string;
};

export type ReferenceCenterPayload = {
  schema_version: "reference_center_v1";
  component: "ReferenceCenterWorkbench";
  filters: Array<{ id: ReferenceScope; label: string }>;
  journeys: string[];
  items: ReferenceItem[];
  initial_item_id: string | null;
  invalid_initial_item: boolean;
  empty_state: {
    title: string;
    description: string;
    suggestions: string[];
  };
};

export type ReferenceCenterEvent = {
  id: "navigate_to_surface";
  destination: string;
  item_id: string;
  nonce: string;
};
