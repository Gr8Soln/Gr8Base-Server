import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, CheckCircle2, AlertTriangle, MessageSquareQuote } from "lucide-react";
import { getScore } from "@/lib/api";
import { ScoreRing } from "@/components/caros/ScoreRing";
import { DimensionBar } from "@/components/caros/DimensionBar";
import { SkillTag } from "@/components/caros/SkillTag";
import { ATS_DIMENSIONS } from "@/lib/types";

export const Route = createFileRoute("/dashboard/ats/$id")({
  head: () => ({ meta: [{ title: "ATS Score · CAROS" }] }),
  component: ATSDetail,
});

function ATSDetail() {
  const { id } = Route.useParams();
  const { data: s, isLoading } = useQuery({ queryKey: ["score", id], queryFn: () => getScore(id) });

  if (isLoading || !s) return <div className="h-64 rounded-xl bg-surface animate-pulse" />;

  return (
    <div className="animate-fade-up">
      <Link to={"/dashboard/ats" as any} className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground mb-6">
        <ArrowLeft className="h-3.5 w-3.5" /> Back to scores
      </Link>

      <div className="grid md:grid-cols-[auto_1fr] gap-8 items-center mb-10">
        <ScoreRing score={s.overallScore} size={200} stroke={12} label="ATS Compatibility" />
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground">Resume → Job</div>
          <div className="mt-1 text-xl font-semibold">{s.resumeName}</div>
          <div className="text-sm text-muted-foreground">{s.jobTitle} at <span className="text-emerald">{s.jobCompany}</span></div>
          <div className="mt-4">
            {s.atsSafe ? (
              <span className="inline-flex items-center gap-1.5 rounded-md border border-emerald/40 bg-emerald/10 px-2.5 py-1 text-xs font-medium text-emerald">
                <CheckCircle2 className="h-3.5 w-3.5" /> ATS Safe
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 rounded-md border border-destructive/40 bg-destructive/10 px-2.5 py-1 text-xs font-medium text-destructive">
                <AlertTriangle className="h-3.5 w-3.5" /> ATS Issues Detected
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-surface p-7 mb-5">
        <div className="text-xs uppercase tracking-wider text-muted-foreground mb-5">Dimension Breakdown</div>
        <div className="grid md:grid-cols-2 gap-x-10 gap-y-4">
          {ATS_DIMENSIONS.map((d, i) => (
            <DimensionBar key={d.key} label={d.label} value={s.dimensions[d.key]} delay={i * 60} />
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-5 mb-5">
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="text-xs uppercase tracking-wider text-destructive mb-3">Missing Keywords</div>
          <div className="flex flex-wrap gap-1.5">
            {s.missingKeywords.length ? s.missingKeywords.map((k) => (
              <SkillTag key={k} variant="missing">{k}</SkillTag>
            )) : <span className="text-sm text-muted-foreground">None — great coverage.</span>}
          </div>
        </div>
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="text-xs uppercase tracking-wider text-warning mb-3">Weak Sections</div>
          <ul className="space-y-2 text-sm">
            {s.weakSections.map((w, i) => (
              <li key={i} className="flex gap-2"><AlertTriangle className="h-3.5 w-3.5 text-warning shrink-0 mt-1" /> {w}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="text-xs uppercase tracking-wider text-emerald mb-3">Recommendations</div>
          <ol className="space-y-2 text-sm">
            {s.recommendations.map((r, i) => (
              <li key={i} className="flex gap-2"><span className="font-mono text-xs text-emerald shrink-0 mt-0.5">{i + 1}.</span> {r}</li>
            ))}
          </ol>
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-elevated p-7 mb-8">
        <div className="flex items-center gap-2 mb-3">
          <MessageSquareQuote className="h-4 w-4 text-emerald" />
          <div className="text-xs uppercase tracking-wider text-muted-foreground">Recruiter Critique</div>
        </div>
        <p className="text-sm leading-relaxed text-foreground/90">{s.recruiterCritique}</p>
      </div>

      <Link to={"/dashboard/optimize" as any} className="inline-flex items-center gap-1.5 rounded-lg bg-emerald px-5 py-2.5 text-sm font-semibold hover:bg-emerald-hover" style={{ color: "var(--background)" }}>
        Optimize this resume for this job →
      </Link>
    </div>
  );
}
