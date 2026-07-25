export type ObservationStatus = "OBSERVED" | "PARTIAL" | "UNAVAILABLE";

export const OBSERVATION_LABEL: Record<ObservationStatus, string> = {
  OBSERVED: "관측 완료",
  PARTIAL: "일부 관측",
  UNAVAILABLE: "관측 불가",
};
