// frontend/lib/api.ts
import type {
  FeatureSummary, FeatureDetail, SimulateResponse, HealthResponse,
  ContrastResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!resp.ok) throw new Error(`API ${path} failed: ${resp.status}`);
  return resp.json();
}

export const api = {
  health: () => fetchJson<HealthResponse>("/api/health"),
  listFeatures: () => fetchJson<FeatureSummary[]>("/api/features"),
  getFeature: (sggCode: string) => fetchJson<FeatureDetail>(`/api/features/${sggCode}`),
  top10: () => fetchJson<FeatureSummary[]>("/api/top10"),
  simulate: (virtualEms: [number, number][]) =>
    fetchJson<SimulateResponse>("/api/simulate", {
      method: "POST",
      body: JSON.stringify({ virtual_ems: virtualEms }),
    }),
  contrast: () => fetchJson<ContrastResponse>("/api/contrast"),
};
