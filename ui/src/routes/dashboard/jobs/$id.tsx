import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, MapPin, Briefcase, Building2, DollarSign, Info } from "lucide-react";
import { getJob } from "@/lib/api";
import { SkillTag } from "@/components/caros/SkillTag";
import { toast } from "sonner";
import { useState } from "react";

export const Route = createFileRoute("/dashboard/jobs/$id")({
  head: () => ({ meta: [{ title: "Job · CAROS" }] }),
  component: JobDetail,
});

function JobDetail() {
  const { id } = Route.useParams();
  const { data: j, isLoading } = useQuery({ queryKey: ["job", id], queryFn: () => getJob(id) });
  const [copied, setCopied] = useState<string | null>(null);

  if (isLoading || !j) return <div className="h-64 rounded-xl bg-surface animate-pulse" />;

  const copy = (s: string) => { navigator.clipboard.writeText(s); setCopied(s); toast.success("Copied"); setTimeout(() => setCopied(null), 1200); };

  return (
    <div className="animate-fade-up">
      <Link to={"/dashboard/jobs" as any} className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground mb-6">
        <ArrowLeft className="h-3.5 w-3.5" /> Back to jobs
      </Link>

      <div className="flex items-start justify-between gap-4 mb-6 flex-wrap">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">{j.title}</h1>
          <div className="mt-1 text-sm text-emerald">{j.company}</div>
        </div>
        <Link to={"/dashboard/optimize" as any} className="inline-flex items-center gap-1.5 rounded-lg bg-emerald px-4 py-2 text-sm font-semibold" style={{ color: "var(--background)" }}>
          Run ATS Score
        </Link>
      </div>

      <div className="flex flex-wrap items-center gap-4 mb-8 text-sm text-muted-foreground">
        <span className="inline-flex items-center gap-1.5"><Briefcase className="h-3.5 w-3.5" /> <span className="capitalize">{j.seniority}</span></span>
        <span className="inline-flex items-center gap-1.5"><Building2 className="h-3.5 w-3.5" /> {j.domain}</span>
        <span className="inline-flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5" /> {j.location} · {j.workType}</span>
        {j.salaryMin && j.salaryMax && (
          <span className="inline-flex items-center gap-1.5"><DollarSign className="h-3.5 w-3.5" /> ${(j.salaryMin / 1000).toFixed(0)}k – ${(j.salaryMax / 1000).toFixed(0)}k</span>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-5 mb-5">
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="text-xs uppercase tracking-wider text-emerald mb-3">Required Skills</div>
          <div className="flex flex-wrap gap-1.5">
            {j.requiredSkills.map((s) => <SkillTag key={s} variant="required">{s}</SkillTag>)}
          </div>
        </div>
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-3">Preferred Skills</div>
          <div className="flex flex-wrap gap-1.5">
            {j.preferredSkills.map((s) => <SkillTag key={s} variant="preferred">{s}</SkillTag>)}
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-5 mb-5">
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-3">ATS Keywords (click to copy)</div>
          <div className="flex flex-wrap gap-1.5">
            {j.atsKeywords.map((k) => (
              <button key={k} onClick={() => copy(k)}
                className={`rounded-md border px-2 py-0.5 font-mono text-xs transition-colors ${
                  copied === k ? "border-emerald bg-emerald/20 text-emerald" : "border-border-strong bg-elevated text-foreground/80 hover:border-emerald/40"
                }`}>
                {k}
              </button>
            ))}
          </div>
        </div>
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-3">Hidden Signals</div>
          <ul className="space-y-2.5 text-sm italic text-foreground/85">
            {j.hiddenSignals.map((s, i) => (
              <li key={i} className="flex gap-2"><Info className="h-4 w-4 text-info shrink-0 mt-0.5 not-italic" /> {s}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-3">Tools & Technologies</div>
          <div className="flex flex-wrap gap-1.5">
            {j.tools.map((t) => <SkillTag key={t} variant="neutral">{t}</SkillTag>)}
          </div>
        </div>
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-3">Soft Skills</div>
          <div className="flex flex-wrap gap-1.5">
            {j.softSkills.map((t) => <SkillTag key={t} variant="neutral">{t}</SkillTag>)}
          </div>
        </div>
      </div>
    </div>
  );
}
