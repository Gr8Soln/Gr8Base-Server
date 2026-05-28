import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { Upload, FileText, Trash2, Eye, Download, GitCompare, Wand2 } from "lucide-react";
import { listResumes, uploadResume, deleteResume } from "@/lib/api";
import { PageHeader, EmptyState } from "@/components/caros/PageHeader";
import { StrategyBadge } from "@/components/caros/StrategyBadge";
import { ScoreBadge } from "@/components/caros/ScoreBadge";
import { formatRelative } from "@/lib/utils-format";
import { toast } from "sonner";

export const Route = createFileRoute("/dashboard/resumes/")({
  head: () => ({ meta: [{ title: "Resumes · CAROS" }] }),
  component: ResumesPage,
});

function UploadZone({ onUpload }: { onUpload: (f: File) => void }) {
  const [drag, setDrag] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault(); setDrag(false);
        const f = e.dataTransfer.files?.[0]; if (f) onUpload(f);
      }}
      className={`rounded-2xl border-2 border-dashed p-10 text-center transition-all ${
        drag ? "border-emerald bg-emerald/5" : "border-border bg-surface/40 hover:border-emerald/40"
      }`}
    >
      <div className="mx-auto rounded-full bg-elevated p-3 w-fit mb-3">
        <Upload className="h-5 w-5 text-emerald" />
      </div>
      <div className="font-medium">Drag and drop your resume here</div>
      <div className="mt-1 text-xs text-muted-foreground">Supports PDF, DOCX, TXT — max 10MB</div>
      <button
        onClick={() => inputRef.current?.click()}
        className="mt-5 inline-flex items-center rounded-lg border border-border bg-elevated px-4 py-2 text-sm font-medium hover:bg-background transition-colors"
      >
        Browse files
      </button>
      <input
        ref={inputRef} type="file" accept=".pdf,.docx,.txt" className="hidden"
        onChange={(e) => { const f = e.target.files?.[0]; if (f) onUpload(f); }}
      />
    </div>
  );
}

function ResumesPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["resumes"], queryFn: listResumes });

  const upload = useMutation({
    mutationFn: uploadResume,
    onSuccess: () => { toast.success("Resume parsed"); qc.invalidateQueries({ queryKey: ["resumes"] }); },
  });
  const del = useMutation({
    mutationFn: deleteResume,
    onSuccess: () => { toast.success("Resume deleted"); qc.invalidateQueries({ queryKey: ["resumes"] }); },
  });

  return (
    <div className="animate-fade-up">
      <PageHeader
        title="Resumes"
        subtitle="Manage and optimize your resume versions"
      />

      <div className="mb-8">
        <UploadZone onUpload={(f) => upload.mutate(f)} />
        {upload.isPending && (
          <div className="mt-3 text-sm text-emerald">Parsing resume…</div>
        )}
      </div>

      {isLoading ? (
        <div className="grid gap-3">{[...Array(3)].map((_, i) => <div key={i} className="h-24 rounded-xl bg-surface animate-pulse" />)}</div>
      ) : !data?.length ? (
        <EmptyState icon={FileText} title="No resumes yet" description="Upload your first resume to get started." />
      ) : (
        <div className="grid gap-3">
          {data.map((r) => (
            <div key={r.id} className="rounded-xl border border-border bg-surface p-5 transition-all hover:bg-elevated">
              <div className="flex items-start justify-between gap-4 flex-wrap">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold">{r.label}</span>
                    <span className="font-mono text-xs text-muted-foreground">v{r.version}</span>
                    {r.strategy && <StrategyBadge strategy={r.strategy} />}
                    {r.parentResumeId && (
                      <span className="text-[10px] uppercase tracking-wider text-muted-foreground">optimized from v1</span>
                    )}
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground">
                    {r.fileName} · {r.skills.length} skills · {r.experience.length} roles · {formatRelative(r.createdAt)}
                  </div>
                </div>
                {r.atsScoreSnapshot != null && (
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-2xl font-semibold text-emerald tabular-nums">{r.atsScoreSnapshot.toFixed(1)}</span>
                    <ScoreBadge score={r.atsScoreSnapshot} />
                  </div>
                )}
              </div>
              <div className="mt-4 pt-4 border-t border-border flex items-center gap-1 flex-wrap text-xs">
                <Link to={"/dashboard/resumes/$id" as any} params={{ id: r.id } as any} className="inline-flex items-center gap-1 rounded-md px-2 py-1 hover:bg-background transition-colors">
                  <Eye className="h-3.5 w-3.5" /> View
                </Link>
                <Link to={"/dashboard/optimize" as any} className="inline-flex items-center gap-1 rounded-md px-2 py-1 hover:bg-background transition-colors">
                  <Wand2 className="h-3.5 w-3.5" /> Optimize
                </Link>
                <button onClick={() => toast.success("PDF queued (mock)")} className="inline-flex items-center gap-1 rounded-md px-2 py-1 hover:bg-background transition-colors">
                  <Download className="h-3.5 w-3.5" /> Download PDF
                </button>
                <button onClick={() => toast.info("Compare view coming soon")} className="inline-flex items-center gap-1 rounded-md px-2 py-1 hover:bg-background transition-colors">
                  <GitCompare className="h-3.5 w-3.5" /> Compare
                </button>
                <button onClick={() => del.mutate(r.id)} className="ml-auto inline-flex items-center gap-1 rounded-md px-2 py-1 text-destructive hover:bg-destructive/10 transition-colors">
                  <Trash2 className="h-3.5 w-3.5" /> Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
