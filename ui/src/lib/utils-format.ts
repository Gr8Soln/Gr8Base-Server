export function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export function formatRelative(iso: string): string {
  const d = new Date(iso).getTime();
  const diff = Date.now() - d;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  return formatDate(iso);
}

export function scoreColor(score: number): { text: string; ring: string; bg: string } {
  if (score >= 75) return { text: "text-emerald", ring: "stroke-emerald", bg: "bg-emerald" };
  if (score >= 50) return { text: "text-warning", ring: "stroke-warning", bg: "bg-warning" };
  return { text: "text-destructive", ring: "stroke-destructive", bg: "bg-destructive" };
}

export function scoreColorHex(score: number): string {
  if (score >= 75) return "var(--emerald)";
  if (score >= 50) return "var(--warning)";
  return "var(--destructive)";
}
