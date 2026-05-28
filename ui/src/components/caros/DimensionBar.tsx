import { useEffect, useState } from "react";

export function DimensionBar({
  label, value, delay = 0,
}: { label: string; value: number; delay?: number }) {
  const pct = Math.round(value * 100);
  const [w, setW] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setW(pct), 50 + delay);
    return () => clearTimeout(t);
  }, [pct, delay]);
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <span className="text-foreground/90">{label}</span>
        <span className="font-mono text-emerald tabular-nums">{pct}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-border overflow-hidden">
        <div
          className="h-full rounded-full bg-emerald transition-all duration-700 ease-out"
          style={{ width: `${w}%` }}
        />
      </div>
    </div>
  );
}
