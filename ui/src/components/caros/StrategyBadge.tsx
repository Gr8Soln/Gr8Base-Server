import { STRATEGIES, StrategyKey } from "@/lib/types";

export function StrategyBadge({ strategy }: { strategy: StrategyKey }) {
  const s = STRATEGIES.find((x) => x.key === strategy);
  return (
    <span className="inline-flex items-center rounded-full border border-emerald/40 bg-emerald/10 px-2.5 py-0.5 text-xs font-medium text-emerald">
      {s?.name || strategy}
    </span>
  );
}
