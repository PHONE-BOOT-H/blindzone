"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { ContrastResponse } from "@/lib/types";

export default function ContrastPanel() {
  const [data, setData] = useState<ContrastResponse | null>(null);

  useEffect(() => {
    api.contrast().then(setData).catch(() => setData(null));
  }, []);

  if (!data) return null;

  return (
    <div className="bg-white border rounded-lg p-4 space-y-3">
      <h3 className="font-semibold">사고 빈도 지도와 BlindZone의 차이</h3>
      <p className="text-sm text-gray-700">
        BlindZone TOP10 중 <b>{data.blindzone_top10_not_in_accident_top10}곳</b>은
        사고건수 TOP10에 포함되지 않습니다. 즉 사고 빈도만 보면 덜 위험해 보이지만,
        응급 접근성을 결합하면 잠재 위험이 큰 지역입니다.
      </p>
      <div className="overflow-x-auto">
        <table className="w-full text-xs border">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-2 py-1 text-left">시군구</th>
              <th className="px-2 py-1 text-right">사고 순위</th>
              <th className="px-2 py-1 text-right">BlindZone 순위</th>
              <th className="px-2 py-1 text-right">순위 차이</th>
            </tr>
          </thead>
          <tbody>
            {data.items.slice(0, 12).map((it) => (
              <tr key={it.sgg_code} className="border-t">
                <td className="px-2 py-1">{it.sgg_name}</td>
                <td className="px-2 py-1 text-right">{it.accident_rank}</td>
                <td className="px-2 py-1 text-right">{it.risk_rank}</td>
                <td className="px-2 py-1 text-right">
                  {it.rank_diff > 0 ? `+${it.rank_diff}` : it.rank_diff}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-gray-500">
        해석: 순위 차이가 큰 양수는 사고는 적은데 BlindZone에서 높은 위험으로 발굴된 곳 (응급 접근성 등 결합 효과).
      </p>
    </div>
  );
}
