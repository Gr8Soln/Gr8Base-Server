import { scoreColorHex } from "@/lib/utils-format";

export function ScoreRing({
  score, size = 160, stroke = 10, label = "ATS Score",
}: { score: number; size?: number; stroke?: number; label?: string }) {
  const radius = (size - stroke) / 2;
  const circ = 2 * Math.PI * radius;
  const pct = Math.max(0, Math.min(100, score)) / 100;
  const offset = circ * (1 - pct);
  const color = scoreColorHex(score);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" strokeWidth={stroke}
          stroke="var(--border)"
        />
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" strokeWidth={stroke} strokeLinecap="round"
          stroke={color}
          strokeDasharray={circ}
          strokeDashoffset={offset}
          className="animate-ring"
          style={{
            ["--ring-circumference" as any]: `${circ}`,
            ["--ring-offset" as any]: `${offset}`,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="font-mono font-semibold tabular-nums" style={{ fontSize: size * 0.28, color }}>
          {score.toFixed(1)}
        </div>
        <div className="text-xs uppercase tracking-wider text-muted-foreground mt-1">{label}</div>
      </div>
    </div>
  );
}
