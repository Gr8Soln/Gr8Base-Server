import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { CheckCircle2, Circle, Loader2, ArrowRight, Sparkles } from "lucide-react";
import * as Icons from "lucide-react";
import { listResumes, listJobs, optimizeResume, getTask } from "@/lib/api";
import { PageHeader } from "@/components/caros/PageHeader";
import { ScoreRing } from "@/components/caros/ScoreRing";
import { STRATEGIES, StrategyKey } from "@/lib/types";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/dashboard/optimize/")({
  head: () => ({ meta: [{ title: "Optimize · CAROS" }] }),
  component: OptimizePage,
});

function OptimizePage() {
  const resumes = useQuery({ queryKey: ["resumes"], queryFn: listResumes });
  const jobs = useQuery({ queryKey: ["jobs"], queryFn: listJobs });

  const [step, setStep] = useState(1);
  const [resumeId, setResumeId] = useState<string>("");
  const [jobId, setJobId] = useState<string>("");
  const [strategy, setStrategy] = useState<StrategyKey>("ats-aggressive");
  const [label, setLabel] = useState("");
  const [taskId, setTaskId] = useState<string | null>(null);

  const task = useQuery({
    queryKey: ["task", taskId],
    queryFn: () => getTask<{ resume: any; beforeScore: number; afterScore: number }>(taskId!),
    enabled: !!taskId,
    refetchInterval: (q) => q.state.data?.status === "completed" ? false : 800,
  });

  const resume = resumes.data?.find((r) => r.id === resumeId);
  const job = jobs.data?.find((j) => j.id === jobId);
  const strat = STRATEGIES.find((s) => s.key === strategy)!;

  const start = () => {
    const id = optimizeResume({ resumeId, jobId, strategy, label });
    setTaskId(id);
    setStep(4);
  };

  // pre-select first items
  useEffect(() => { if (!resumeId && resumes.data?.length) setResumeId(resumes.data[0].id); }, [resumes.data, resumeId]);
  useEffect(() => { if (!jobId && jobs.data?.length) setJobId(jobs.data[0].id); }, [jobs.data, jobId]);

  return (
    <div className="animate-fade-up">
      <PageHeader title="Optimize" subtitle="Rewrite your resume for a specific job with one of nine strategies." />

      {/* Stepper */}
      <div className="flex items-center gap-2 mb-8 text-xs">
        {["Select", "Strategy", "Confirm", "Result"].map((label, i) => {
          const idx = i + 1;
          const active = step === idx;
          const done = step > idx;
          return (
            <div key={i} className="flex items-center gap-2">
              <div className={cn(
                "h-7 w-7 rounded-full inline-flex items-center justify-center font-mono text-xs border",
                done ? "border-emerald bg-emerald text-background" : active ? "border-emerald text-emerald" : "border-border text-muted-foreground",
              )}>{done ? <CheckCircle2 className="h-4 w-4" /> : idx}</div>
              <span className={cn("uppercase tracking-wider", active ? "text-emerald" : done ? "text-foreground" : "text-muted-foreground")}>{label}</span>
              {i < 3 && <div className="w-8 h-px bg-border ml-2" />}
            </div>
          );
        })}
      </div>

      {step === 1 && (
        <div className="grid md:grid-cols-2 gap-5">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">Resume</div>
            <select value={resumeId} onChange={(e) => setResumeId(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm focus:outline-none focus:border-emerald/60">
              {resumes.data?.map((r) => <option key={r.id} value={r.id}>{r.label} (v{r.version})</option>)}
            </select>
            {resume && (
              <div className="mt-3 rounded-xl border border-border bg-surface p-4 text-sm">
                <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Preview</div>
                <div>{resume.skills.length} skills · {resume.experience.length} roles</div>
              </div>
            )}
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">Job</div>
            <select value={jobId} onChange={(e) => setJobId(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm focus:outline-none focus:border-emerald/60">
              {jobs.data?.map((j) => <option key={j.id} value={j.id}>{j.title} @ {j.company}</option>)}
            </select>
            {job && (
              <div className="mt-3 rounded-xl border border-border bg-surface p-4 text-sm">
                <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Preview</div>
                <div className="capitalize">{job.seniority} · {job.domain}</div>
                <div className="mt-1 text-muted-foreground text-xs">{job.requiredSkills.slice(0, 4).join(" · ")}</div>
              </div>
            )}
          </div>
          <div className="md:col-span-2 flex justify-end">
            <button onClick={() => setStep(2)} disabled={!resumeId || !jobId}
              className="inline-flex items-center gap-1.5 rounded-lg bg-emerald px-5 py-2.5 text-sm font-semibold disabled:opacity-40" style={{ color: "var(--background)" }}>
              Continue <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {STRATEGIES.map((s) => {
              const Icon: any = (Icons as any)[s.icon] || Sparkles;
              const selected = s.key === strategy;
              return (
                <button key={s.key} onClick={() => setStrategy(s.key)}
                  className={cn(
                    "text-left rounded-xl border bg-surface p-4 transition-all",
                    selected ? "border-emerald bg-emerald/10 shadow-lg shadow-emerald/10" : "border-border hover:bg-elevated",
                  )}>
                  <div className="flex items-center gap-2 mb-1.5">
                    <div className={cn("rounded-md p-1.5 border", selected ? "bg-emerald/20 border-emerald/40" : "bg-elevated border-border")}>
                      <Icon className={cn("h-4 w-4", selected ? "text-emerald" : "text-muted-foreground")} />
                    </div>
                    <div className="font-semibold text-sm">{s.name}</div>
                  </div>
                  <div className="text-xs text-muted-foreground">{s.description}</div>
                </button>
              );
            })}
          </div>
          <div className="mt-5">
            <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">Label (optional)</div>
            <input value={label} onChange={(e) => setLabel(e.target.value)} placeholder={`e.g. ${job?.company || "Stripe"} application`}
              className="w-full max-w-md rounded-lg border border-border bg-surface px-3 py-2 text-sm focus:outline-none focus:border-emerald/60" />
          </div>
          <div className="mt-6 flex justify-between">
            <button onClick={() => setStep(1)} className="rounded-lg border border-border px-4 py-2 text-sm hover:bg-elevated">Back</button>
            <button onClick={() => setStep(3)} className="inline-flex items-center gap-1.5 rounded-lg bg-emerald px-5 py-2.5 text-sm font-semibold" style={{ color: "var(--background)" }}>
              Continue <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div>
          <div className="rounded-2xl border border-border bg-surface p-6 mb-6">
            <div className="grid md:grid-cols-3 gap-6 items-center">
              <div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground">Resume</div>
                <div className="mt-1 font-medium">{resume?.label}</div>
              </div>
              <div className="text-center text-emerald">→</div>
              <div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground">Job</div>
                <div className="mt-1 font-medium">{job?.title}</div>
                <div className="text-xs text-muted-foreground">{job?.company}</div>
              </div>
            </div>
            <div className="mt-5 pt-5 border-t border-border flex items-center justify-between">
              <div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground">Strategy</div>
                <div className="mt-1 font-medium text-emerald">{strat.name}</div>
              </div>
              <div className="text-xs text-muted-foreground">Estimated time: ~60 seconds</div>
            </div>
          </div>
          <div className="flex justify-between">
            <button onClick={() => setStep(2)} className="rounded-lg border border-border px-4 py-2 text-sm hover:bg-elevated">Back</button>
            <button onClick={start} className="inline-flex items-center gap-1.5 rounded-lg bg-emerald px-6 py-3 text-base font-semibold hover:bg-emerald-hover" style={{ color: "var(--background)" }}>
              <Sparkles className="h-4 w-4" /> Optimize Resume
            </button>
          </div>
        </div>
      )}

      {step === 4 && taskId && (
        <OptimizeRunner task={task.data} onReset={() => { setTaskId(null); setStep(1); }} />
      )}
    </div>
  );
}

function OptimizeRunner({ task, onReset }: { task: any; onReset: () => void }) {
  const steps = ["Planning strategy", "Rewriting bullets", "Injecting keywords", "Evaluating ATS score", "Running recruiter critique", "Done"];
  const currentIdx = task ? Math.round((task.progress || 0) * steps.length) : 0;
  const done = task?.status === "completed";

  if (done) {
    const before = task.result.beforeScore;
    const after = task.result.afterScore;
    const delta = after - before;
    return (
      <div className="animate-fade-up">
        <div className="rounded-2xl border border-emerald/30 bg-emerald/[0.03] p-8 text-center shadow-lg shadow-emerald/10">
          <div className="text-xs uppercase tracking-wider text-emerald mb-4">Optimization complete</div>
          <div className="flex items-center justify-center gap-8 mb-6">
            <div className="text-center">
              <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">Before</div>
              <ScoreRing score={before} size={120} stroke={8} label="" />
            </div>
            <ArrowRight className="h-6 w-6 text-emerald" />
            <div className="text-center">
              <div className="text-xs uppercase tracking-wider text-emerald mb-2">After</div>
              <ScoreRing score={after} size={120} stroke={8} label="" />
            </div>
          </div>
          <div className="font-mono text-3xl text-emerald font-semibold">+{delta.toFixed(1)} points</div>
          <div className="mt-2 text-sm text-muted-foreground">New version: <span className="text-foreground">{task.result.resume.label}</span></div>
          <div className="mt-6 flex items-center justify-center gap-2 flex-wrap">
            <Link to={"/dashboard/resumes/$id" as any} params={{ id: task.result.resume.id } as any}
              className="rounded-lg bg-emerald px-4 py-2 text-sm font-semibold" style={{ color: "var(--background)" }}>View resume</Link>
            <button onClick={onReset} className="rounded-lg border border-border px-4 py-2 text-sm hover:bg-elevated">Run another</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-border bg-surface p-8">
      <div className="text-xs uppercase tracking-wider text-emerald mb-5">Working…</div>
      <ul className="space-y-3">
        {steps.map((s, i) => {
          const active = i === currentIdx;
          const completed = i < currentIdx;
          return (
            <li key={i} className="flex items-center gap-3 text-sm">
              {completed ? <CheckCircle2 className="h-5 w-5 text-emerald" />
                : active ? <Loader2 className="h-5 w-5 text-emerald animate-spin" />
                : <Circle className="h-5 w-5 text-muted-foreground" />}
              <span className={cn(active ? "text-foreground" : completed ? "text-emerald" : "text-muted-foreground")}>{s}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
