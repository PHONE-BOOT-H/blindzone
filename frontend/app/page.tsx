"use client";

import { useEffect, useState } from "react";
import RiskMap from "@/components/RiskMap";
import MetricCard from "@/components/MetricCard";
import ShapExplanation from "@/components/ShapExplanation";
import Top10Table from "@/components/Top10Table";
import ContrastPanel from "@/components/ContrastPanel";
import { api } from "@/lib/api";
import type { FeatureSummary, FeatureDetail } from "@/lib/types";

export default function CitizenPage() {
  const [features, setFeatures] = useState<FeatureSummary[]>([]);
  const [top, setTop] = useState<FeatureSummary[]>([]);
  const [selectedCode, setSelectedCode] = useState<string | null>(null);
  const [detail, setDetail] = useState<FeatureDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.listFeatures(), api.top10()])
      .then(([f, t]) => {
        setFeatures(f);
        setTop(t);
      })
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    if (!selectedCode) {
      setDetail(null);
      return;
    }
    api.getFeature(selectedCode).then(setDetail).catch((e) => setError(String(e)));
  }, [selectedCode]);

  if (error) return <div className="text-red-600">에러: {error}</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">우리 동네 응급 사각지대 확인</h1>
        <p className="text-gray-600">
          사고 건수만으로는 드러나지 않는 응급 사각지대 — 사고·사망률·응급 접근성 결합 탐색
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">지역 검색</label>
            <select
              className="w-full border rounded px-3 py-2"
              value={selectedCode ?? ""}
              onChange={(e) => setSelectedCode(e.target.value || null)}
            >
              <option value="">시군구를 선택하세요</option>
              {features.map((f) => (
                <option key={f.sgg_code} value={f.sgg_code}>
                  {f.sgg_name}
                </option>
              ))}
            </select>
          </div>

          {detail && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <MetricCard
                  label="잠재 위험 지수"
                  value={detail.risk_index.toFixed(3)}
                />
                <MetricCard
                  label="사고 건수 (TAAS 다발지점)"
                  value={detail.accident_count}
                  unit="건"
                />
                <MetricCard
                  label="응급 도착시간 (추정)"
                  value={detail.ems_response_min.toFixed(1)}
                  unit="분"
                />
                <MetricCard
                  label="응급기관 거리"
                  value={detail.ems_distance_km.toFixed(1)}
                  unit="km"
                />
              </div>
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-semibold mb-2">왜 위험한가</h3>
                <ShapExplanation items={detail.shap_top} />
              </div>
            </>
          )}
        </div>

        <div className="lg:col-span-2">
          <h2 className="text-xl font-semibold mb-3">전국 위험지도</h2>
          <RiskMap
            features={features}
            selectedSgg={selectedCode}
            onClickFeature={setSelectedCode}
          />
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-3">전국 상위 잠재 위험지대 TOP 10</h2>
        <Top10Table items={top} />
      </div>

      <ContrastPanel />
    </div>
  );
}
