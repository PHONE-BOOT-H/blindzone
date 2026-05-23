import type { ShapItem } from "@/lib/types";

export default function ShapExplanation({ items }: { items: ShapItem[] }) {
  if (items.length === 0) {
    return <div className="text-sm text-gray-500">설명 로드 실패</div>;
  }
  return (
    <ul className="space-y-2">
      {items.map((item) => {
        const arrow = item.shap_value > 0 ? "↑" : "↓";
        const color = item.shap_value > 0 ? "text-red-600" : "text-green-600";
        return (
          <li key={item.feature} className="flex items-center gap-2">
            <span className={`font-medium ${color}`}>{arrow}</span>
            <span className="font-medium">{item.feature}</span>
            <span className="text-sm text-gray-500">
              (영향도 {item.shap_value >= 0 ? "+" : ""}
              {item.shap_value.toFixed(3)})
            </span>
          </li>
        );
      })}
    </ul>
  );
}
