"use client";

import { useMemo } from "react";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import MapLibreMap from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

import type { FeatureSummary, SimulationItem } from "@/lib/types";

interface Props {
  features: FeatureSummary[];
  selectedSgg?: string | null;
  simulationItems?: SimulationItem[];
  virtualEms?: [number, number][];
  onClickFeature?: (sgg_code: string) => void;
}

const KOREA_VIEW = {
  longitude: 127.8,
  latitude: 36.5,
  zoom: 6,
};

function getColor(value: number, qmin: number, qmax: number): [number, number, number, number] {
  const norm = Math.max(0, Math.min(1, (value - qmin) / (qmax - qmin + 1e-9)));
  const r = Math.floor(255 * norm);
  const g = Math.floor(200 * (1 - norm));
  return [r, g, 64, 200];
}

function getDeltaColor(delta: number): [number, number, number, number] {
  if (delta < -0.001) return [44, 160, 44, 200];
  return [200, 200, 200, 120];
}

export default function RiskMap({
  features,
  selectedSgg,
  simulationItems,
  virtualEms,
  onClickFeature,
}: Props) {
  const layers = useMemo(() => {
    if (simulationItems && simulationItems.length > 0) {
      const itemMap = new globalThis.Map(simulationItems.map((s) => [s.sgg_code, s]));
      return [
        new ScatterplotLayer({
          id: "sim-points",
          data: features,
          getPosition: (d: FeatureSummary) => [d.lon, d.lat],
          getRadius: (d: FeatureSummary) => {
            const sim = itemMap.get(d.sgg_code);
            const delta = sim ? sim.risk_delta : 0;
            return Math.max(3000, Math.min(15000, Math.abs(delta) * 500000));
          },
          getFillColor: (d: FeatureSummary) => {
            const sim = itemMap.get(d.sgg_code);
            return getDeltaColor(sim ? sim.risk_delta : 0);
          },
          pickable: true,
        }),
        new ScatterplotLayer({
          id: "virtual-ems",
          data: virtualEms ?? [],
          getPosition: (d: [number, number]) => d,
          getRadius: 5000,
          getFillColor: [255, 0, 0, 220],
          stroked: true,
          getLineColor: [120, 0, 0, 220],
          lineWidthMinPixels: 2,
        }),
      ];
    }
    const risks = features.map((f) => f.risk_index);
    const sorted = [...risks].sort((a, b) => a - b);
    const qmin = sorted[Math.floor(sorted.length * 0.05)] ?? 0;
    const qmax = sorted[Math.floor(sorted.length * 0.95)] ?? 1;
    return [
      new ScatterplotLayer({
        id: "risk-points",
        data: features,
        getPosition: (d: FeatureSummary) => [d.lon, d.lat],
        getRadius: (d: FeatureSummary) =>
          d.sgg_code === selectedSgg ? 15000 : 6000,
        getFillColor: (d: FeatureSummary) =>
          getColor(d.risk_index, qmin, qmax),
        stroked: true,
        getLineColor: (d: FeatureSummary) =>
          d.sgg_code === selectedSgg ? [0, 0, 0, 255] : [0, 0, 0, 60],
        lineWidthMinPixels: 1,
        pickable: true,
        onClick: (info: { object?: FeatureSummary }) => {
          if (info.object && onClickFeature) onClickFeature(info.object.sgg_code);
        },
      }),
    ];
  }, [features, selectedSgg, simulationItems, virtualEms, onClickFeature]);

  return (
    <div className="relative w-full h-[600px] rounded-lg overflow-hidden border">
      <DeckGL
        initialViewState={KOREA_VIEW}
        controller={true}
        layers={layers}
        getTooltip={({ object }: { object?: FeatureSummary }) =>
          object
            ? {
                html: `<div style="padding:8px;background:#fff;color:#111;border:1px solid #ccc;border-radius:4px">
              <b>${object.sgg_name}</b><br/>
              위험지수: ${object.risk_index.toFixed(3)}<br/>
              사고: ${object.accident_count}건<br/>
              응급도착 추정: ${object.ems_response_min.toFixed(1)}분
            </div>`,
                style: { background: "transparent", color: "#fff" },
              }
            : null
        }
      >
        <MapLibreMap
          mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
          attributionControl={{}}
        />
      </DeckGL>
      <div className="absolute bottom-2 left-2 bg-white/90 text-xs px-2 py-1 rounded">
        시군구 중심점 기준 · risk_index (탐색형)
      </div>
    </div>
  );
}
