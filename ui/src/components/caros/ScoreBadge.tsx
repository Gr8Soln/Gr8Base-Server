import { cn } from "@/lib/utils";

export function ScoreBadge({ score, className }: { score: number; className?: string }) {
  const tone = score >= 75
    ? "border-emerald/40 bg-emerald/10 text-emerald"
    : score >= 50
    ? "border-warning/40 bg-warning/10 text-warning"
    : "border-destructive/40 bg-destructive/10 text-destructive";
  return (
    <span className={cn(
      "inline-flex items-center rounded-md border px-2 py-0.5 font-mono text-xs font-semibold tabular-nums",
      tone, className,
    )}>
      {score.toFixed(1)}
    </span>
  );
}
