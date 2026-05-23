import type { FeatureSummary } from "@/lib/types";

export default function Top10Table({ items }: { items: FeatureSummary[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-3 py-2 text-left">시군구</th>
            <th className="px-3 py-2 text-right">위험지수</th>
            <th className="px-3 py-2 text-right">사고건수</th>
            <th className="px-3 py-2 text-right">사망사고비율</th>
            <th className="px-3 py-2 text-right">평균출동(분)</th>
            <th className="px-3 py-2 text-right">응급기관거리(km)</th>
          </tr>
        </thead>
        <tbody>
          {items.map((row) => (
            <tr key={row.sgg_code} className="border-t">
              <td className="px-3 py-2">{row.sgg_name}</td>
              <td className="px-3 py-2 text-right">
                {row.risk_index.toFixed(3)}
              </td>
              <td className="px-3 py-2 text-right">{row.accident_count}</td>
              <td className="px-3 py-2 text-right">
                {row.fatality_rate.toFixed(3)}
              </td>
              <td className="px-3 py-2 text-right">
                {row.ems_response_min.toFixed(1)}
              </td>
              <td className="px-3 py-2 text-right">
                {row.ems_distance_km.toFixed(1)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
