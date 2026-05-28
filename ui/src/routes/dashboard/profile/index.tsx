import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { getProfile, updateProfile } from "@/lib/api";
import { PageHeader } from "@/components/caros/PageHeader";
import { Profile } from "@/lib/types";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

export const Route = createFileRoute("/dashboard/profile/")({
  head: () => ({ meta: [{ title: "Profile · CAROS" }] }),
  component: ProfilePage,
});

function Section({ title, children }: any) {
  return (
    <section className="rounded-2xl border border-border bg-surface p-6">
      <h2 className="text-base font-semibold mb-5">{title}</h2>
      <div className="space-y-4">{children}</div>
    </section>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs uppercase tracking-wider text-muted-foreground mb-1.5">{label}</label>
      {children}
    </div>
  );
}

const inputCls = "w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:border-emerald/60";

function TagInput({ value, onChange, placeholder }: { value: string[]; onChange: (v: string[]) => void; placeholder?: string }) {
  const [draft, setDraft] = useState("");
  return (
    <div className="rounded-lg border border-border bg-background px-2 py-1.5 flex flex-wrap gap-1.5 min-h-10">
      {value.map((t) => (
        <span key={t} className="inline-flex items-center gap-1 rounded-md border border-emerald/40 bg-emerald/10 px-2 py-0.5 text-xs text-emerald">
          {t}
          <button onClick={() => onChange(value.filter((x) => x !== t))}><X className="h-3 w-3" /></button>
        </span>
      ))}
      <input
        value={draft} onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && draft.trim()) {
            onChange(Array.from(new Set([...value, draft.trim()])));
            setDraft("");
          }
        }}
        placeholder={placeholder}
        className="flex-1 min-w-32 bg-transparent px-1 py-1 text-sm focus:outline-none"
      />
    </div>
  );
}

function ProfilePage() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["profile"], queryFn: getProfile });
  const [p, setP] = useState<Profile | null>(null);
  useEffect(() => { if (data) setP(data); }, [data]);

  const save = useMutation({
    mutationFn: (patch: Partial<Profile>) => updateProfile(patch),
    onSuccess: () => { toast.success("Profile saved"); qc.invalidateQueries({ queryKey: ["profile"] }); },
  });

  if (!p) return <div className="h-64 rounded-xl bg-surface animate-pulse" />;
  const set = (k: keyof Profile, v: any) => setP({ ...p, [k]: v });

  return (
    <div className="animate-fade-up max-w-4xl space-y-6">
      <PageHeader
        title="Profile"
        subtitle="Your career targets and preferences shape every optimization."
        action={
          <button onClick={() => save.mutate(p)} disabled={save.isPending}
            className="rounded-lg bg-emerald px-4 py-2 text-sm font-semibold disabled:opacity-50" style={{ color: "var(--background)" }}>
            {save.isPending ? "Saving…" : "Save changes"}
          </button>
        }
      />

      <Section title="Personal info">
        <div className="grid sm:grid-cols-2 gap-4">
          <Field label="Full name"><input className={inputCls} value={p.fullName} onChange={(e) => set("fullName", e.target.value)} /></Field>
          <Field label="Email"><input className={inputCls} value={p.email} readOnly disabled /></Field>
          <Field label="Headline"><input className={inputCls} value={p.headline || ""} onChange={(e) => set("headline", e.target.value)} /></Field>
          <Field label="Location"><input className={inputCls} value={p.location || ""} onChange={(e) => set("location", e.target.value)} /></Field>
          <Field label="Phone"><input className={inputCls} value={p.phone || ""} onChange={(e) => set("phone", e.target.value)} /></Field>
          <Field label="LinkedIn"><input className={inputCls} value={p.linkedinUrl || ""} onChange={(e) => set("linkedinUrl", e.target.value)} /></Field>
          <Field label="GitHub"><input className={inputCls} value={p.githubUrl || ""} onChange={(e) => set("githubUrl", e.target.value)} /></Field>
          <Field label="Portfolio"><input className={inputCls} value={p.portfolioUrl || ""} onChange={(e) => set("portfolioUrl", e.target.value)} /></Field>
        </div>
      </Section>

      <Section title="Career targets">
        <Field label="Target roles"><TagInput value={p.targetRoles} onChange={(v) => set("targetRoles", v)} placeholder="Add a role and press Enter" /></Field>
        <Field label="Target industries"><TagInput value={p.targetIndustries} onChange={(v) => set("targetIndustries", v)} placeholder="Add an industry" /></Field>
        <div className="grid sm:grid-cols-3 gap-4">
          <Field label="Salary min (USD)"><input type="number" className={inputCls} value={p.salaryMin || ""} onChange={(e) => set("salaryMin", +e.target.value)} /></Field>
          <Field label="Salary max (USD)"><input type="number" className={inputCls} value={p.salaryMax || ""} onChange={(e) => set("salaryMax", +e.target.value)} /></Field>
          <Field label="Years experience"><input type="number" className={inputCls} value={p.yearsExperience} onChange={(e) => set("yearsExperience", +e.target.value)} /></Field>
        </div>
        <Field label="Preferred work type">
          <div className="inline-flex rounded-lg border border-border bg-background p-1">
            {(["remote", "hybrid", "onsite"] as const).map((w) => (
              <button key={w} onClick={() => set("workType", w)}
                className={cn("px-3 py-1.5 text-sm rounded-md capitalize transition-colors",
                  p.workType === w ? "bg-emerald text-background font-medium" : "text-muted-foreground hover:text-foreground")}>{w}</button>
            ))}
          </div>
        </Field>
      </Section>

      <Section title="Writing preferences">
        <div className="grid sm:grid-cols-2 gap-3">
          {([
            { k: "professional", desc: "Polished, neutral, broadly hireable." },
            { k: "confident", desc: "Assertive, outcome-led, recruiter-forward." },
            { k: "technical", desc: "Dense with stack, architecture, scale numbers." },
            { k: "concise", desc: "Brief bullets, maximum signal density." },
          ] as const).map((t) => {
            const sel = p.writingTone === t.k;
            return (
              <button key={t.k} onClick={() => set("writingTone", t.k)}
                className={cn("text-left rounded-xl border p-4 transition-all",
                  sel ? "border-emerald bg-emerald/10" : "border-border bg-background hover:bg-elevated")}>
                <div className="font-semibold text-sm capitalize">{t.k}</div>
                <div className="mt-1 text-xs text-muted-foreground">{t.desc}</div>
              </button>
            );
          })}
        </div>
      </Section>
    </div>
  );
}
