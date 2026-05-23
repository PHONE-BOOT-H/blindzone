"use client";

import { useEffect, useState } from "react";
import RiskMap from "@/components/RiskMap";
import MetricCard from "@/components/MetricCard";
import { api } from "@/lib/api";
import type { FeatureSummary, SimulateResponse } from "@/lib/types";

export default function PolicyPage() {
  const [features, setFeatures] = useState<FeatureSummary[]>([]);
  const [virtualEms, setVirtualEms] = useState<[number, number][]>([]);
  const [lonInput, setLonInput] = useState("127.0");
  const [latInput, setLatInput] = useState("37.5");
  const [sim, setSim] = useState<SimulateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listFeatures().then(setFeatures).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    api.simulate(virtualEms).then(setSim).catch((e) => setError(String(e)));
  }, [virtualEms]);

  function addEms() {
    const lon = parseFloat(lonInput);
    const lat = parseFloat(latInput);
    if (Number.isFinite(lon) && Number.isFinite(lat)) {
      setVirtualEms([...virtualEms, [lon, lat]]);
    }
  }

  if (error) return <div className="text-red-600">에러: {error}</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">정책 시뮬레이터</h1>
        <p className="text-gray-600">
          가상 응급의료 거점을 추가하면 거리 기반 접근성이 어떻게 변하나? (정책 효과 예측 X — 민감도 분석)
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white border rounded-lg p-4 space-y-3">
            <h3 className="font-semibold">가상 응급의료 거점 추가</h3>
            <div>
              <label className="block text-sm">경도</label>
              <input
                className="w-full border rounded px-3 py-1"
                value={lonInput}
                onChange={(e) => setLonInput(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm">위도</label>
              <input
                className="w-full border rounded px-3 py-1"
                value={latInput}
                onChange={(e) => setLatInput(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={addEms}
                className="px-3 py-1 bg-blue-600 text-white rounded text-sm"
              >
                추가
              </button>
              <button
                onClick={() => setVirtualEms([])}
                className="px-3 py-1 border rounded text-sm"
              >
                초기화
              </button>
            </div>
            <div className="text-sm">
              현재 추가: <b>{virtualEms.length}</b>개
              <ul className="mt-1 text-xs text-gray-600">
                {virtualEms.map((p, i) => (
                  <li key={i}>
                    {i + 1}. ({p[0].toFixed(4)}, {p[1].toFixed(4)})
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {sim && (
            <div className="grid grid-cols-1 gap-3">
              <MetricCard
                label="평균 위험지수 변화"
                value={`${sim.avg_delta >= 0 ? "+" : ""}${sim.avg_delta.toFixed(4)}`}
              />
              <MetricCard
                label="가장 큰 위험 감소"
                value={sim.max_drop.toFixed(4)}
              />
              <MetricCard
                label="개선된 시군구 수"
                value={sim.improved_count}
                unit="개"
              />
            </div>
          )}
        </div>

        <div className="lg:col-span-2">
          <h2 className="text-xl font-semibold mb-3">시뮬레이션 결과 지도</h2>
          <RiskMap
            features={features}
            simulationItems={sim?.items ?? []}
            virtualEms={virtualEms}
          />
        </div>
      </div>

      {sim && sim.items.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-3">개선 효과 TOP 10 시군구</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-3 py-2 text-left">시군구</th>
                  <th className="px-3 py-2 text-right">기존 위험</th>
                  <th className="px-3 py-2 text-right">신규 위험</th>
                  <th className="px-3 py-2 text-right">변화</th>
                  <th className="px-3 py-2 text-right">거점까지 거리(km)</th>
                </tr>
              </thead>
              <tbody>
                {sim.items.slice(0, 10).map((row) => (
                  <tr key={row.sgg_code} className="border-t">
                    <td className="px-3 py-2">{row.sgg_name}</td>
                    <td className="px-3 py-2 text-right">
                      {row.risk_index.toFixed(3)}
                    </td>
                    <td className="px-3 py-2 text-right">
                      {row.risk_index_new.toFixed(3)}
                    </td>
                    <td className="px-3 py-2 text-right text-green-700">
                      {row.risk_delta.toFixed(4)}
                    </td>
                    <td className="px-3 py-2 text-right">
                      {row.ems_distance_km_new.toFixed(1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
