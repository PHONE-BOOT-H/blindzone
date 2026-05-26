// frontend/lib/api.ts
import type {
  FeatureSummary, FeatureDetail, SimulateResponse, HealthResponse,
  ContrastResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const STATIC = "/data"; // public/data — 백엔드 다운 시 fallback (export_static.py 생성)

async function tryFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(url, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!resp.ok) throw new Error(`fetch ${url} failed: ${resp.status}`);
  return resp.json();
}

// 라이브 API 우선, 실패하면 정적 스냅샷으로 graceful fallback.
async function withFallback<T>(apiPath: string, staticUrl: string): Promise<T> {
  try {
    return await tryFetch<T>(`${API_BASE}${apiPath}`);
  } catch {
    return await tryFetch<T>(staticUrl); // 같은 도메인 정적 파일 — 항상 살아있음
  }
}

export const api = {
  health: () => tryFetch<HealthResponse>(`${API_BASE}/api/health`),

  listFeatures: () =>
    withFallback<FeatureSummary[]>("/api/features", `${STATIC}/features.json`),

  top10: () =>
    withFallback<FeatureSummary[]>("/api/top10", `${STATIC}/top10.json`),

  contrast: () =>
    withFallback<ContrastResponse>("/api/contrast", `${STATIC}/contrast.json`),

  getFeature: async (sggCode: string): Promise<FeatureDetail> => {
    try {
      return await tryFetch<FeatureDetail>(`${API_BASE}/api/features/${sggCode}`);
    } catch {
      const all = await tryFetch<Record<string, FeatureDetail>>(`${STATIC}/details.json`);
      const d = all[sggCode];
      if (!d) throw new Error(`detail ${sggCode} not in static fallback`);
      return d;
    }
  },

  simulate: async (virtualEms: [number, number][]): Promise<SimulateResponse> => {
    try {
      return await tryFetch<SimulateResponse>(`${API_BASE}/api/simulate`, {
        method: "POST",
        body: JSON.stringify({ virtual_ems: virtualEms }),
      });
    } catch {
      // 백엔드 다운 시: 사전계산된 예시(인제/옹진 거점) 중 가까운 것 반환
      const ex = await tryFetch<Record<string, SimulateResponse>>(`${STATIC}/simulate_examples.json`);
      const [lon = 0, lat = 0] = virtualEms[0] ?? [];
      const nearOngjin = Math.abs(lon - 125.7) < 1.0 && Math.abs(lat - 37.66) < 1.0;
      return ex[nearOngjin ? "ongjin" : "inje"];
    }
  },
};
