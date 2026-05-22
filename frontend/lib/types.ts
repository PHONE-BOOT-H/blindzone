// frontend/lib/types.ts
export interface FeatureSummary {
  sgg_code: string;
  sgg_name: string;
  lon: number;
  lat: number;
  risk_index: number;
  accident_count: number;
  fatality_rate: number;
  ems_distance_km: number;
  ems_response_min: number;
}

export interface ShapItem {
  feature: string;
  shap_value: number;
  direction: string;
}

export interface FeatureDetail extends FeatureSummary {
  area_km2: number;
  fatality_count: number;
  injury_count: number;
  shap_top: ShapItem[];
}

export interface SimulationItem {
  sgg_code: string;
  sgg_name: string;
  lon: number;
  lat: number;
  risk_index: number;
  risk_index_new: number;
  risk_delta: number;
  ems_distance_km_new: number;
}

export interface SimulateResponse {
  avg_delta: number;
  max_drop: number;
  improved_count: number;
  items: SimulationItem[];
}

export interface ContrastItem {
  sgg_code: string;
  sgg_name: string;
  accident_count: number;
  accident_rank: number;
  risk_rank: number;
  rank_diff: number;
}

export interface ContrastResponse {
  blindzone_top10_not_in_accident_top10: number;
  accident_top10_not_in_blindzone_top10: number;
  items: ContrastItem[];
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  features_loaded: boolean;
  feature_count: number;
}
