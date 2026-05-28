import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Plus, Briefcase, Trash2, Loader2, X } from "lucide-react";
import { listJobs, analyzeJob, deleteJob } from "@/lib/api";
import { PageHeader, EmptyState } from "@/components/caros/PageHeader";
import { SkillTag } from "@/components/caros/SkillTag";
import { formatRelative } from "@/lib/utils-format";
import { toast } from "sonner";

export const Route = createFileRoute("/dashboard/jobs/")({
  head: () => ({ meta: [{ title: "Jobs · CAROS" }] }),
  component: JobsPage,
});

function AnalyzeModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [rawText, setRawText] = useState("");
  const [company, setCompany] = useState("");
  const [companyUrl, setCompanyUrl] = useState("");

  const mut = useMutation({
    mutationFn: () => analyzeJob({ rawText, company, companyUrl }),
    onSuccess: () => { toast.success("Job analyzed"); qc.invalidateQueries({ queryKey: ["jobs"] }); onClose(); },
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} className="w-full max-w-2xl rounded-2xl border border-border bg-surface p-6 md:p-8">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold">Analyze a job description</h2>
          <button onClick={onClose} className="rounded-md p-1 text-muted-foreground hover:bg-elevated"><X className="h-4 w-4" /></button>
        </div>
        <div className="space-y-4">
          <textarea
            value={rawText} onChange={(e) => setRawText(e.target.value)}
            placeholder="Paste the job description here…"
            className="w-full h-48 rounded-lg border border-border bg-background px-3 py-2.5 text-sm focus:outline-none focus:border-emerald/60 resize-none"
          />
          <div className="grid sm:grid-cols-2 gap-3">
            <input value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Company name (optional)"
              className="rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:border-emerald/60" />
            <input value={companyUrl} onChange={(e) => setCompanyUrl(e.target.value)} placeholder="Company URL (optional)"
              className="rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:border-emerald/60" />
          </div>
          <button
            onClick={() => mut.mutate()}
            disabled={!rawText.trim() || mut.isPending}
            className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-emerald px-4 py-2.5 text-sm font-semibold disabled:opacity-50 hover:bg-emerald-hover"
            style={{ color: "var(--background)" }}
          >
            {mut.isPending ? <><Loader2 className="h-4 w-4 animate-spin" /> Extracting intelligence…</> : "Analyze Job Description"}
          </button>
        </div>
      </div>
    </div>
  );
}

function JobsPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["jobs"], queryFn: listJobs });
  const [open, setOpen] = useState(false);
  const del = useMutation({
    mutationFn: deleteJob,
    onSuccess: () => { toast.success("Job deleted"); qc.invalidateQueries({ queryKey: ["jobs"] }); },
  });

  return (
    <div className="animate-fade-up">
      <PageHeader
        title="Jobs"
        subtitle="Analyzed job descriptions with extracted intelligence"
        action={
          <button onClick={() => setOpen(true)} className="inline-flex items-center gap-1.5 rounded-lg bg-emerald px-4 py-2 text-sm font-semibold hover:bg-emerald-hover" style={{ color: "var(--background)" }}>
            <Plus className="h-4 w-4" /> Analyze New Job
          </button>
        }
      />

      {isLoading ? (
        <div className="grid gap-3">{[...Array(2)].map((_, i) => <div key={i} className="h-40 rounded-xl bg-surface animate-pulse" />)}</div>
      ) : !data?.length ? (
        <EmptyState icon={Briefcase} title="No jobs analyzed yet" description="Paste a job description to extract required skills, ATS keywords, and hidden signals."
          action={<button onClick={() => setOpen(true)} className="rounded-lg bg-emerald px-4 py-2 text-sm font-semibold" style={{ color: "var(--background)" }}>Analyze your first job</button>}
        />
      ) : (
        <div className="grid gap-4">
          {data.map((j) => (
            <Link to={"/dashboard/jobs/$id" as any} params={{ id: j.id } as any} key={j.id}
              className="rounded-xl border border-border bg-surface p-5 transition-all hover:bg-elevated hover:border-emerald/30">
              <div className="flex items-start justify-between gap-4 mb-3">
                <div>
                  <div className="text-lg font-semibold">{j.title}</div>
                  <div className="text-sm text-emerald">{j.company}</div>
                </div>
                <button
                  onClick={(e) => { e.preventDefault(); del.mutate(j.id); }}
                  className="rounded-md p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
              <div className="flex items-center gap-2 mb-3">
                <span className="rounded-md border border-border bg-background px-2 py-0.5 text-xs text-muted-foreground capitalize">{j.seniority}</span>
                <span className="rounded-md border border-border bg-background px-2 py-0.5 text-xs text-muted-foreground">{j.domain}</span>
              </div>
              <div className="flex flex-wrap items-center gap-1.5">
                {j.requiredSkills.slice(0, 5).map((s) => <SkillTag key={s} variant="required">{s}</SkillTag>)}
                {j.requiredSkills.length > 5 && (
                  <span className="text-xs text-muted-foreground">+{j.requiredSkills.length - 5} more</span>
                )}
              </div>
              <div className="mt-4 pt-3 border-t border-border flex items-center gap-4 text-xs text-muted-foreground">
                <span><span className="font-mono text-foreground">{j.atsKeywords.length}</span> ATS keywords</span>
                <span><span className="font-mono text-foreground">{j.hiddenSignals.length}</span> hidden signals</span>
                <span className="ml-auto">{formatRelative(j.createdAt)}</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {open && <AnalyzeModal onClose={() => setOpen(false)} />}
    </div>
  );
}
