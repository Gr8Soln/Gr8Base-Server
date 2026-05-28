import { Link } from "@tanstack/react-router";
import { cn } from "@/lib/utils";

export function CarosMark({ className, size = "md" }: { className?: string; size?: "sm" | "md" | "lg" }) {
  const sizes = { sm: "text-base", md: "text-xl", lg: "text-3xl" };
  return (
    <Link to="/" className={cn("inline-flex items-baseline font-bold tracking-tight", sizes[size], className)}>
      <span className="text-foreground">CAR</span>
      <span className="text-emerald">OS</span>
    </Link>
  );
}
