import { cn } from "@/lib/utils";

type Variant = "required" | "preferred" | "missing" | "neutral";

export function SkillTag({
  children, variant = "neutral", className,
}: { children: React.ReactNode; variant?: Variant; className?: string }) {
  const styles: Record<Variant, string> = {
    required: "border-emerald/40 bg-emerald/10 text-emerald",
    preferred: "border-border-strong bg-elevated text-foreground/80",
    missing: "border-destructive/40 bg-destructive/10 text-destructive",
    neutral: "border-border bg-surface text-muted-foreground",
  };
  return (
    <span className={cn(
      "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
      styles[variant], className,
    )}>
      {children}
    </span>
  );
}
