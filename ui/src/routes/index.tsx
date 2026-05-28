import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Upload, FileSearch, Sparkles, ArrowRight, Target, Heart, Rocket,
  Building2, Cpu, Crown, Minimize2, Globe, Github, Twitter, FileText,
} from "lucide-react";
import { CarosMark } from "@/components/caros/CarosMark";
import { ScoreRing } from "@/components/caros/ScoreRing";
import { DimensionBar } from "@/components/caros/DimensionBar";
import { SkillTag } from "@/components/caros/SkillTag";
import { ATS_DIMENSIONS, STRATEGIES } from "@/lib/types";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "CAROS — Your career, engineered." },
      { name: "description", content: "AI-powered ATS optimization. Score your resume across 8 dimensions, rewrite for any job, increase interview rate." },
    ],
  }),
  component: Landing,
});

const STRATEGY_ICONS: Record<string, any> = {
  Target, Heart, Rocket, Building2, Cpu, Crown, Minimize2, Sparkles, Globe,
};

function TopNav() {
  return (
    <header className="fixed top-0 inset-x-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto max-w-7xl px-6 md:px-10 lg:px-16 h-16 flex items-center justify-between">
        <CarosMark size="md" />
        <nav className="hidden md:flex items-center gap-7 text-sm text-muted-foreground">
          <a href="#how" className="hover:text-foreground transition-colors">How it works</a>
          <a href="#scoring" className="hover:text-foreground transition-colors">Scoring</a>
          <a href="#strategies" className="hover:text-foreground transition-colors">Strategies</a>
        </nav>
        <Link
          to={"/auth/login" as any}
          className="inline-flex items-center gap-1.5 rounded-lg bg-emerald px-3.5 py-2 text-sm font-medium transition-colors hover:bg-emerald-hover"
          style={{ color: "var(--background)" }}
        >
          Sign in <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border">
      <div className="absolute inset-0 bg-grid bg-grid-fade pointer-events-none" />
      <div className="absolute top-1/3 -left-32 h-96 w-96 rounded-full bg-emerald/10 blur-3xl pointer-events-none" />
      <div className="relative mx-auto max-w-7xl px-6 md:px-10 lg:px-16 pt-32 md:pt-40 pb-24">
        <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-12 lg:gap-16 items-center">
          <div className="animate-fade-up">
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted-foreground mb-6">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald" />
              Career intelligence for engineers
            </div>
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-foreground leading-[1.02]">
              Your career,<br />
              <span className="text-emerald">engineered.</span>
            </h1>
            <p className="mt-6 text-lg text-muted-foreground max-w-xl leading-relaxed">
              CAROS analyzes your resume against any job description, scores ATS compatibility
              across 8 dimensions, and rewrites your resume to maximize interview conversion —
              in seconds.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link
                to={"/auth/login" as any}
                className="inline-flex items-center gap-1.5 rounded-lg bg-emerald px-5 py-2.5 text-sm font-semibold transition-all hover:bg-emerald-hover hover:shadow-lg hover:shadow-emerald/20"
                style={{ color: "var(--background)" }}
              >
                Get started free <ArrowRight className="h-4 w-4" />
              </Link>
              <a
                href="#how"
                className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-surface px-5 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-elevated"
              >
                See how it works
              </a>
            </div>
            <div className="mt-10 flex items-center gap-6 text-xs text-muted-foreground">
              <div><span className="text-foreground font-mono">8</span> scoring dimensions</div>
              <div><span className="text-foreground font-mono">9</span> strategies</div>
              <div><span className="text-foreground font-mono">3</span> templates</div>
            </div>
          </div>

          {/* Floating ATS card */}
          <div className="relative animate-fade-up" style={{ animationDelay: "120ms" }}>
            <div className="absolute -inset-6 bg-emerald/5 blur-3xl rounded-full pointer-events-none" />
            <div className="relative rounded-2xl border border-border bg-surface/80 backdrop-blur p-6 shadow-2xl shadow-black/40">
              <div className="flex items-start justify-between mb-5">
                <div>
                  <div className="text-xs uppercase tracking-wider text-muted-foreground">Resume → Job</div>
                  <div className="mt-1 text-sm font-medium">Senior Engineer · Stripe</div>
                </div>
                <span className="rounded-md border border-emerald/40 bg-emerald/10 px-2 py-0.5 font-mono text-xs text-emerald">v2</span>
              </div>
              <div className="flex items-center gap-6">
                <ScoreRing score={87.2} size={130} stroke={9} />
                <div className="flex-1 space-y-3 min-w-0">
                  {ATS_DIMENSIONS.slice(0, 4).map((d, i) => (
                    <DimensionBar key={d.key} label={d.label} value={[0.91, 0.88, 0.85, 0.88][i]} delay={i * 50} />
                  ))}
                </div>
              </div>
              <div className="mt-5 pt-5 border-t border-border flex flex-wrap gap-1.5">
                <SkillTag variant="required">Go</SkillTag>
                <SkillTag variant="required">Kafka</SkillTag>
                <SkillTag variant="required">PCI-DSS</SkillTag>
                <SkillTag variant="preferred">Rust</SkillTag>
                <SkillTag variant="missing">Webhooks</SkillTag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = [
    { icon: Upload, title: "Upload your resume", desc: "PDF, DOCX, or TXT. We parse skills, experience, projects." },
    { icon: FileSearch, title: "Paste a job description", desc: "We extract required skills, ATS keywords, and hidden signals." },
    { icon: Sparkles, title: "Get your optimized resume", desc: "Score, recommendations, and a rewritten resume in 60 seconds." },
  ];
  return (
    <section id="how" className="border-b border-border">
      <div className="mx-auto max-w-7xl px-6 md:px-10 lg:px-16 py-24">
        <div className="max-w-2xl mb-14">
          <div className="text-xs uppercase tracking-wider text-emerald mb-3">How it works</div>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">Three steps from upload to optimized.</h2>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {steps.map((s, i) => {
            const Icon = s.icon;
            return (
              <div key={i} className="relative rounded-2xl border border-border bg-surface p-6 transition-all duration-200 hover:bg-elevated hover:-translate-y-0.5">
                <div className="flex items-center justify-between mb-5">
                  <div className="rounded-lg bg-emerald/10 p-2.5 border border-emerald/30">
                    <Icon className="h-5 w-5 text-emerald" />
                  </div>
                  <span className="font-mono text-xs text-muted-foreground">0{i + 1}</span>
                </div>
                <h3 className="text-lg font-semibold mb-1.5">{s.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function ScoringSection() {
  const vals = [0.91, 0.88, 0.85, 0.88, 0.84, 0.95, 0.82, 0.86];
  return (
    <section id="scoring" className="border-b border-border bg-gradient-to-b from-background to-surface/30">
      <div className="mx-auto max-w-7xl px-6 md:px-10 lg:px-16 py-24">
        <div className="grid lg:grid-cols-2 gap-14 items-center">
          <div>
            <div className="text-xs uppercase tracking-wider text-emerald mb-3">ATS Scoring</div>
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-5">
              Know exactly why you're not getting interviews.
            </h2>
            <p className="text-muted-foreground text-lg leading-relaxed">
              CAROS evaluates your resume against any job across 8 independent dimensions —
              from keyword match to recruiter readability. No more guessing.
            </p>
            <div className="mt-8 flex items-center gap-6">
              <ScoreRing score={87.2} size={140} stroke={9} />
              <div className="text-sm space-y-2">
                <div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-emerald" /> 75+ — Strong</div>
                <div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-warning" /> 50-75 — Needs work</div>
                <div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-destructive" /> &lt;50 — Major gaps</div>
              </div>
            </div>
          </div>
          <div className="rounded-2xl border border-border bg-surface p-7 space-y-4">
            {ATS_DIMENSIONS.map((d, i) => (
              <DimensionBar key={d.key} label={d.label} value={vals[i]} delay={i * 60} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function BeforeAfter() {
  return (
    <section className="border-b border-border">
      <div className="mx-auto max-w-7xl px-6 md:px-10 lg:px-16 py-24">
        <div className="max-w-2xl mb-12">
          <div className="text-xs uppercase tracking-wider text-emerald mb-3">Optimization</div>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
            Rewritten to get past the filter — and impress the recruiter.
          </h2>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="rounded-2xl border border-border bg-surface p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="text-xs uppercase tracking-wider text-muted-foreground">Before</div>
              <span className="font-mono text-xs text-destructive">Score: 64.5</span>
            </div>
            <ul className="space-y-3 text-sm text-muted-foreground leading-relaxed">
              <li>· Worked on order matching engine.</li>
              <li>· Helped migrate monolith to microservices.</li>
              <li>· Reduced infrastructure costs through optimization.</li>
            </ul>
          </div>
          <div className="rounded-2xl border border-emerald/30 bg-emerald/[0.03] p-6 shadow-lg shadow-emerald/10">
            <div className="flex items-center justify-between mb-4">
              <div className="text-xs uppercase tracking-wider text-emerald">After · ATS Aggressive</div>
              <span className="font-mono text-xs text-emerald">Score: 87.2</span>
            </div>
            <ul className="space-y-3 text-sm text-foreground/90 leading-relaxed">
              <li>· Built Go-based <span className="text-emerald">order matching engine</span> processing <span className="font-mono">2M events/sec</span> at p99 800µs.</li>
              <li>· Led migration to <span className="text-emerald">14 microservices on Kubernetes</span>, cutting deploy time <span className="font-mono">87%</span>.</li>
              <li>· Reduced infra costs <span className="font-mono">38%</span> via query optimization + caching layer redesign.</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

function StrategiesSection() {
  return (
    <section id="strategies" className="border-b border-border bg-surface/30">
      <div className="mx-auto max-w-7xl px-6 md:px-10 lg:px-16 py-24">
        <div className="max-w-2xl mb-12">
          <div className="text-xs uppercase tracking-wider text-emerald mb-3">Strategies</div>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">Optimize for your exact target.</h2>
          <p className="mt-4 text-muted-foreground">
            Nine optimization strategies, each tuned for a specific hiring context.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {STRATEGIES.map((s) => {
            const Icon = STRATEGY_ICONS[s.icon] || Sparkles;
            return (
              <div key={s.key} className="rounded-xl border border-border bg-background p-5 transition-all duration-200 hover:border-emerald/40 hover:bg-elevated">
                <div className="flex items-center gap-3 mb-2">
                  <div className="rounded-md bg-emerald/10 p-1.5 border border-emerald/30">
                    <Icon className="h-4 w-4 text-emerald" />
                  </div>
                  <div className="font-semibold text-sm">{s.name}</div>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">{s.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function StatsBar() {
  const stats = [
    { v: "8", label: "Scoring dimensions" },
    { v: "9", label: "Optimization strategies" },
    { v: "3", label: "Resume templates" },
    { v: "OSS", label: "Open source" },
  ];
  return (
    <section className="border-b border-border">
      <div className="mx-auto max-w-7xl px-6 md:px-10 lg:px-16 py-12 grid grid-cols-2 md:grid-cols-4 gap-6">
        {stats.map((s) => (
          <div key={s.label} className="text-center md:text-left">
            <div className="font-mono text-3xl font-semibold text-emerald">{s.v}</div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground mt-1">{s.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function FinalCTA() {
  return (
    <section className="relative overflow-hidden border-b border-border">
      <div className="absolute inset-0 bg-grid bg-grid-fade opacity-50 pointer-events-none" />
      <div className="relative mx-auto max-w-7xl px-6 md:px-10 lg:px-16 py-24 text-center">
        <h2 className="text-4xl md:text-5xl font-bold tracking-tight max-w-2xl mx-auto">
          Start optimizing your resume — <span className="text-emerald">free.</span>
        </h2>
        <Link
          to={"/auth/login" as any}
          className="mt-8 inline-flex items-center gap-2 rounded-lg bg-emerald px-6 py-3 text-base font-semibold transition-all hover:bg-emerald-hover hover:shadow-xl hover:shadow-emerald/30"
          style={{ color: "var(--background)" }}
        >
          Get started <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="bg-background">
      <div className="mx-auto max-w-7xl px-6 md:px-10 lg:px-16 py-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <CarosMark size="md" />
          <p className="mt-2 text-sm text-muted-foreground">Open source. Built for engineers.</p>
        </div>
        <div className="flex items-center gap-5 text-sm text-muted-foreground">
          <a href="#" className="inline-flex items-center gap-1.5 hover:text-foreground transition-colors"><Github className="h-4 w-4" /> GitHub</a>
          <a href="#" className="inline-flex items-center gap-1.5 hover:text-foreground transition-colors"><FileText className="h-4 w-4" /> Docs</a>
          <a href="#" className="inline-flex items-center gap-1.5 hover:text-foreground transition-colors"><Twitter className="h-4 w-4" /> Twitter</a>
        </div>
      </div>
    </footer>
  );
}

function Landing() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <TopNav />
      <Hero />
      <HowItWorks />
      <ScoringSection />
      <BeforeAfter />
      <StrategiesSection />
      <StatsBar />
      <FinalCTA />
      <Footer />
    </div>
  );
}
