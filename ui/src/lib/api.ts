// Mock in-memory API mirroring the FastAPI contract.
// Swap this file out to wire real backend.

import {
  Resume, Job, ATSScore, Profile, AsyncTask, StrategyKey, ATSDimensionKey, ATS_DIMENSIONS,
} from "./types";
import { seedResumes, seedJobs, seedScores, seedProfile } from "./seed";

const wait = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));
const uid = () => Math.random().toString(36).slice(2, 10);

const store = {
  profile: { ...seedProfile },
  resumes: [...seedResumes],
  jobs: [...seedJobs],
  scores: [...seedScores],
};

// ---------- Profile ----------
export async function getProfile(): Promise<Profile> {
  await wait(150);
  return { ...store.profile };
}
export async function updateProfile(patch: Partial<Profile>): Promise<Profile> {
  await wait(300);
  store.profile = { ...store.profile, ...patch };
  return { ...store.profile };
}

// ---------- Resumes ----------
export async function listResumes(): Promise<Resume[]> {
  await wait(200);
  return [...store.resumes].sort((a, b) => b.createdAt.localeCompare(a.createdAt));
}
export async function getResume(id: string): Promise<Resume> {
  await wait(150);
  const r = store.resumes.find((x) => x.id === id);
  if (!r) throw new Error("Resume not found");
  return r;
}
export async function uploadResume(file: File): Promise<Resume> {
  await wait(1200);
  const r: Resume = {
    id: `resume-${uid()}`,
    label: file.name.replace(/\.[^.]+$/, ""),
    fileName: file.name,
    version: 1,
    status: "parsed",
    skills: ["TypeScript", "React", "Node.js", "PostgreSQL"],
    summary: "Parsed from uploaded file (mock).",
    experience: [{ company: "Example Co", title: "Engineer", startDate: "2023-01", endDate: "Present", bullets: ["Did engineering things."] }],
    projects: [],
    education: [],
    certifications: [],
    createdAt: new Date().toISOString(),
  };
  store.resumes.unshift(r);
  return r;
}
export async function deleteResume(id: string): Promise<void> {
  await wait(200);
  store.resumes = store.resumes.filter((r) => r.id !== id);
}
export async function renameResume(id: string, label: string): Promise<Resume> {
  await wait(150);
  const r = store.resumes.find((x) => x.id === id);
  if (!r) throw new Error("Resume not found");
  r.label = label;
  return r;
}

// ---------- Jobs ----------
export async function listJobs(): Promise<Job[]> {
  await wait(200);
  return [...store.jobs].sort((a, b) => b.createdAt.localeCompare(a.createdAt));
}
export async function getJob(id: string): Promise<Job> {
  await wait(150);
  const j = store.jobs.find((x) => x.id === id);
  if (!j) throw new Error("Job not found");
  return j;
}
export async function analyzeJob(input: { rawText: string; company?: string; companyUrl?: string }): Promise<Job> {
  await wait(1800);
  const j: Job = {
    id: `job-${uid()}`,
    title: input.rawText.split("\n")[0]?.slice(0, 60) || "Untitled Role",
    company: input.company || "Unknown Co",
    companyUrl: input.companyUrl,
    location: "Remote",
    workType: "remote",
    seniority: "senior",
    domain: "Software Engineering",
    requiredSkills: ["TypeScript", "React", "Node.js", "PostgreSQL", "AWS"],
    preferredSkills: ["GraphQL", "Kubernetes"],
    atsKeywords: ["TypeScript", "React", "scalable", "distributed", "AWS", "CI/CD"],
    hiddenSignals: ["Mentions 'ownership' multiple times — senior IC track.", "Strong written communication implied."],
    tools: ["TypeScript", "React", "Node.js", "PostgreSQL"],
    softSkills: ["Ownership", "Communication"],
    rawText: input.rawText,
    createdAt: new Date().toISOString(),
  };
  store.jobs.unshift(j);
  return j;
}
export async function deleteJob(id: string): Promise<void> {
  await wait(200);
  store.jobs = store.jobs.filter((j) => j.id !== id);
}

// ---------- ATS ----------
export async function listScores(): Promise<ATSScore[]> {
  await wait(200);
  return [...store.scores].sort((a, b) => b.createdAt.localeCompare(a.createdAt));
}
export async function getScore(id: string): Promise<ATSScore> {
  await wait(150);
  const s = store.scores.find((x) => x.id === id);
  if (!s) throw new Error("Score not found");
  return s;
}

// ---------- Async tasks (poll pattern, mirrors backend 202 + GET task) ----------
const tasks = new Map<string, AsyncTask<any>>();

function startTask<T>(steps: string[], finalResult: () => T): string {
  const id = `task-${uid()}`;
  const task: AsyncTask<T> = { id, status: "running", progress: 0, step: steps[0] };
  tasks.set(id, task);
  let i = 0;
  const tick = () => {
    i++;
    if (i >= steps.length) {
      task.status = "completed";
      task.progress = 1;
      task.step = "Done";
      task.result = finalResult();
      return;
    }
    task.step = steps[i];
    task.progress = i / steps.length;
    setTimeout(tick, 900 + Math.random() * 400);
  };
  setTimeout(tick, 800);
  return id;
}

export async function getTask<T>(id: string): Promise<AsyncTask<T>> {
  await wait(100);
  const t = tasks.get(id);
  if (!t) throw new Error("Task not found");
  return t as AsyncTask<T>;
}

export function scoreResume(input: { resumeId: string; jobId: string }): string {
  return startTask(
    ["Parsing resume", "Extracting job signals", "Computing keyword match", "Running semantic analysis", "Evaluating ATS safety", "Generating recruiter critique", "Done"],
    () => {
      const resume = store.resumes.find((r) => r.id === input.resumeId)!;
      const job = store.jobs.find((j) => j.id === input.jobId)!;
      const baseDims = ATS_DIMENSIONS.map(() => 0.55 + Math.random() * 0.35);
      const dimsObj: Record<string, number> = {};
      ATS_DIMENSIONS.forEach((d, i) => { dimsObj[d.key] = baseDims[i]; });
      const overall = +(baseDims.reduce((a, b) => a + b, 0) / baseDims.length * 100).toFixed(1);
      const score: ATSScore = {
        id: `score-${uid()}`,
        resumeId: resume.id, resumeName: resume.label,
        jobId: job.id, jobTitle: job.title, jobCompany: job.company,
        overallScore: overall,
        dimensions: dimsObj as Record<ATSDimensionKey, number>,
        missingKeywords: job.requiredSkills.filter((s) => !resume.skills.includes(s)).slice(0, 5),
        weakSections: ["Summary lacks domain-specific keywords.", "Bullets could be more quantified."],
        recommendations: [
          `Add missing skills: ${job.requiredSkills.filter((s) => !resume.skills.includes(s)).slice(0, 3).join(", ")}`,
          "Lead each bullet with a quantified outcome.",
          "Mirror the job's exact phrasing for required skills.",
        ],
        recruiterCritique: `Solid candidate for ${job.title}. To strengthen the application, foreground domain expertise (${job.domain}) and ensure required skills appear on page 1.`,
        atsSafe: overall > 50,
        safetyIssues: overall < 50 ? ["Detected images in header — may not parse in older ATS."] : [],
        createdAt: new Date().toISOString(),
      };
      store.scores.unshift(score);
      resume.atsScoreSnapshot = overall;
      return score;
    },
  );
}

export function optimizeResume(input: { resumeId: string; jobId: string; strategy: StrategyKey; label?: string }): string {
  return startTask(
    ["Planning strategy", "Rewriting bullets", "Injecting keywords", "Evaluating ATS score", "Running recruiter critique", "Done"],
    () => {
      const base = store.resumes.find((r) => r.id === input.resumeId)!;
      const job = store.jobs.find((j) => j.id === input.jobId)!;
      const newScore = +(78 + Math.random() * 18).toFixed(1);
      const optimized: Resume = {
        ...base,
        id: `resume-${uid()}`,
        label: input.label || `${job.company} — ${input.strategy}`,
        fileName: `${base.fileName.replace(/\.[^.]+$/, "")}_${input.strategy}.pdf`,
        version: (base.version || 1) + 1,
        status: "optimized",
        strategy: input.strategy,
        parentResumeId: base.id,
        atsScoreSnapshot: newScore,
        skills: Array.from(new Set([...base.skills, ...job.requiredSkills])),
        summary: `${base.summary} Specialized for ${job.domain.toLowerCase()}.`,
        experience: base.experience.map((e) => ({
          ...e,
          bullets: e.bullets.map((b) => b.replace(/\.$/, "") + ` — aligned to ${job.requiredSkills[0] || "target role"}.`),
        })),
        createdAt: new Date().toISOString(),
      };
      store.resumes.unshift(optimized);
      return { resume: optimized, beforeScore: base.atsScoreSnapshot ?? 60, afterScore: newScore };
    },
  );
}

export function renderPdf(_input: { resumeId: string; template: string }): string {
  return startTask(["Rendering PDF", "Done"], () => ({ url: "data:," }));
}
