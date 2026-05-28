import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { BarChart3 } from "lucide-react";
import { listScores } from "@/lib/api";
import { PageHeader, EmptyState } from "@/components/caros/PageHeader";
import { ScoreRing } from "@/components/caros/ScoreRing";
import { formatRelative } from "@/lib/utils-format";

export const Route = createFileRoute("/dashboard/ats/")({
  head: () => ({ meta: [{ title: "ATS Scores · CAROS" }] }),
  component: ATSListPage,
});

function ATSListPage() {
  const { data, isLoading } = useQuery({ queryKey: ["scores"], queryFn: listScores });
  return (
    <div className="animate-fade-up">
      <PageHeader title="ATS Scores" subtitle="Every score run, every dimension, every recommendation." />
      {isLoading ? (
        <div className="grid gap-4">{[...Array(2)].map((_, i) => <div key={i} className="h-40 rounded-xl bg-surface animate-pulse" />)}</div>
      ) : !data?.length ? (
        <EmptyState icon={BarChart3} title="No scores yet" description="Run your first ATS score from the Optimize page."
          action={<Link to={"/dashboard/optimize" as any} className="rounded-lg bg-emerald px-4 py-2 text-sm font-semibold" style={{ color: "var(--background)" }}>Open Optimize</Link>}
        />
      ) : (
        <div className="grid gap-4">
          {data.map((s) => (
            <Link to={"/dashboard/ats/$id" as any} params={{ id: s.id } as any} key={s.id}
              className="flex items-center gap-6 rounded-xl border border-border bg-surface p-5 transition-all hover:bg-elevated hover:border-emerald/30">
              <ScoreRing score={s.overallScore} size={100} stroke={7} label="ATS" />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium">{s.resumeName} <span className="text-muted-foreground">→</span> {s.jobTitle}</div>
                <div className="mt-0.5 text-xs text-muted-foreground">{s.jobCompany} · {formatRelative(s.createdAt)}</div>
                <div className="mt-3 text-xs text-emerald">View details →</div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
