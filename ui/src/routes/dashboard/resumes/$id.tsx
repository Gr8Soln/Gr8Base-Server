import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Download } from "lucide-react";
import { getResume } from "@/lib/api";
import { SkillTag } from "@/components/caros/SkillTag";
import { StrategyBadge } from "@/components/caros/StrategyBadge";
import { formatDate } from "@/lib/utils-format";
import { toast } from "sonner";

export const Route = createFileRoute("/dashboard/resumes/$id")({
  head: () => ({ meta: [{ title: "Resume · CAROS" }] }),
  component: ResumeDetail,
});

function ResumeDetail() {
  const { id } = Route.useParams();
  const { data: r, isLoading } = useQuery({ queryKey: ["resume", id], queryFn: () => getResume(id) });

  if (isLoading || !r) return <div className="h-64 rounded-xl bg-surface animate-pulse" />;

  return (
    <div className="animate-fade-up max-w-4xl">
      <Link to={"/dashboard/resumes" as any} className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground mb-6">
        <ArrowLeft className="h-3.5 w-3.5" /> Back to resumes
      </Link>

      <div className="flex items-start justify-between gap-4 mb-6 flex-wrap">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-2xl font-bold tracking-tight">{r.label}</h1>
            <span className="font-mono text-xs text-muted-foreground">v{r.version}</span>
            {r.strategy && <StrategyBadge strategy={r.strategy} />}
          </div>
          <p className="mt-1.5 text-sm text-muted-foreground">{r.fileName} · {formatDate(r.createdAt)}</p>
        </div>
        <button onClick={() => toast.success("PDF queued (mock)")} className="inline-flex items-center gap-1.5 rounded-lg bg-emerald px-4 py-2 text-sm font-medium" style={{ color: "var(--background)" }}>
          <Download className="h-4 w-4" /> Download PDF
        </button>
      </div>

      <div className="rounded-2xl border border-border bg-surface p-6 mb-5">
        <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">Summary</div>
        <p className="text-sm leading-relaxed text-foreground/90">{r.summary}</p>
      </div>

      <div className="rounded-2xl border border-border bg-surface p-6 mb-5">
        <div className="text-xs uppercase tracking-wider text-muted-foreground mb-3">Skills</div>
        <div className="flex flex-wrap gap-1.5">
          {r.skills.map((s) => <SkillTag key={s} variant="required">{s}</SkillTag>)}
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-surface p-6 mb-5">
        <div className="text-xs uppercase tracking-wider text-muted-foreground mb-4">Experience</div>
        <div className="space-y-6">
          {r.experience.map((e, i) => (
            <div key={i}>
              <div className="flex items-baseline justify-between flex-wrap gap-1">
                <div className="font-semibold">{e.title}</div>
                <div className="font-mono text-xs text-muted-foreground">{e.startDate} → {e.endDate}</div>
              </div>
              <div className="text-sm text-emerald">{e.company}</div>
              <ul className="mt-3 space-y-1.5 text-sm text-foreground/90">
                {e.bullets.map((b, j) => <li key={j} className="flex gap-2"><span className="text-emerald shrink-0">·</span>{b}</li>)}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {r.projects.length > 0 && (
        <div className="rounded-2xl border border-border bg-surface p-6 mb-5">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-3">Projects</div>
          {r.projects.map((p, i) => (
            <div key={i} className="text-sm"><span className="font-semibold">{p.name}</span> — <span className="text-muted-foreground">{p.description}</span></div>
          ))}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-5">
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-3">Education</div>
          {r.education.map((e, i) => (
            <div key={i} className="text-sm"><div className="font-semibold">{e.degree}</div><div className="text-muted-foreground">{e.school} · {e.year}</div></div>
          ))}
        </div>
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-3">Certifications</div>
          <ul className="space-y-1 text-sm">
            {r.certifications.map((c, i) => <li key={i}>· {c}</li>)}
            {!r.certifications.length && <li className="text-muted-foreground">None</li>}
          </ul>
        </div>
      </div>
    </div>
  );
}
