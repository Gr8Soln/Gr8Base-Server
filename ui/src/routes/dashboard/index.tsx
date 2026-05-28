import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { FileText, Briefcase, BarChart3, Wand2, Upload, FileSearch, ArrowRight, Sparkles } from "lucide-react";
import { listResumes, listJobs, listScores } from "@/lib/api";
import { ScoreBadge } from "@/components/caros/ScoreBadge";
import { StrategyBadge } from "@/components/caros/StrategyBadge";
import { formatRelative } from "@/lib/utils-format";

export const Route = createFileRoute("/dashboard/")({
  head: () => ({ meta: [{ title: "Dashboard · CAROS" }] }),
  component: Dashboard,
});

function StatCard({ icon: Icon, label, value }: any) {
  return (
    <div className="rounded-xl border border-border bg-surface p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase tracking-wider text-muted-foreground">{label}</span>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="mt-3 font-mono text-3xl font-semibold text-foreground tabular-nums">{value}</div>
    </div>
  );
}

function QuickAction({ icon: Icon, title, desc, to }: any) {
  return (
    <Link
      to={to}
      className="group flex items-start gap-4 rounded-xl border border-dashed border-border bg-surface/50 p-5 transition-all hover:border-emerald/40 hover:bg-elevated"
    >
      <div className="rounded-lg bg-emerald/10 p-2.5 border border-emerald/30">
        <Icon className="h-5 w-5 text-emerald" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <div className="font-semibold text-sm">{title}</div>
          <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-emerald group-hover:translate-x-0.5 transition-all" />
        </div>
        <div className="mt-0.5 text-xs text-muted-foreground">{desc}</div>
      </div>
    </Link>
  );
}

function Dashboard() {
  const resumes = useQuery({ queryKey: ["resumes"], queryFn: listResumes });
  const jobs = useQuery({ queryKey: ["jobs"], queryFn: listJobs });
  const scores = useQuery({ queryKey: ["scores"], queryFn: listScores });

  const avgScore = scores.data?.length
    ? (scores.data.reduce((a, s) => a + s.overallScore, 0) / scores.data.length).toFixed(1)
    : "—";

  return (
    <div className="space-y-10 animate-fade-up">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Welcome back.</h1>
        <p className="mt-1 text-sm text-muted-foreground">Your career command center.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={FileText} label="Resumes" value={resumes.data?.length ?? "—"} />
        <StatCard icon={Briefcase} label="Jobs analyzed" value={jobs.data?.length ?? "—"} />
        <StatCard icon={BarChart3} label="Scores run" value={scores.data?.length ?? "—"} />
        <StatCard icon={Sparkles} label="Avg ATS" value={<span className="text-emerald">{avgScore}</span>} />
      </div>

      <section>
        <div className="flex items-baseline justify-between mb-4">
          <h2 className="text-lg font-semibold">Recent activity</h2>
          <Link to={"/dashboard/ats" as any} className="text-xs text-emerald hover:underline">View all scores →</Link>
        </div>
        <div className="rounded-xl border border-border bg-surface divide-y divide-border">
          {scores.data?.slice(0, 3).map((s) => (
            <Link key={s.id} to={"/dashboard/ats/$id" as any} params={{ id: s.id } as any}
              className="flex items-center justify-between p-4 hover:bg-elevated transition-colors">
              <div className="min-w-0 flex-1">
                <div className="text-sm font-medium truncate">{s.resumeName} <span className="text-muted-foreground">→</span> {s.jobTitle}</div>
                <div className="mt-0.5 text-xs text-muted-foreground">{s.jobCompany} · {formatRelative(s.createdAt)}</div>
              </div>
              <ScoreBadge score={s.overallScore} />
            </Link>
          ))}
          {!scores.data?.length && (
            <div className="p-6 text-sm text-muted-foreground text-center">No scores yet. Run your first ATS score from the Optimize page.</div>
          )}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-4">Quick actions</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <QuickAction icon={Upload} title="Upload Resume" desc="Add a new version to your library" to="/dashboard/resumes" />
          <QuickAction icon={FileSearch} title="Analyze Job" desc="Extract intelligence from any JD" to="/dashboard/jobs" />
          <QuickAction icon={Wand2} title="Optimize" desc="Run the full optimization wizard" to="/dashboard/optimize" />
        </div>
      </section>

      <section>
        <div className="flex items-baseline justify-between mb-4">
          <h2 className="text-lg font-semibold">Resume versions</h2>
          <Link to={"/dashboard/resumes" as any} className="text-xs text-emerald hover:underline">View all →</Link>
        </div>
        <div className="grid gap-3">
          {resumes.data?.slice(0, 4).map((r) => (
            <div key={r.id} className="rounded-xl border border-border bg-surface p-4 flex items-center justify-between gap-4">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-medium text-sm">{r.label}</span>
                  <span className="font-mono text-xs text-muted-foreground">v{r.version}</span>
                  {r.strategy && <StrategyBadge strategy={r.strategy} />}
                </div>
                <div className="mt-1 text-xs text-muted-foreground">{r.skills.length} skills · {r.experience.length} roles · {formatRelative(r.createdAt)}</div>
              </div>
              {r.atsScoreSnapshot != null && <ScoreBadge score={r.atsScoreSnapshot} />}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
