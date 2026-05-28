// Types mirror the FastAPI backend contract.

export type User = {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
};

export type Profile = {
  id: string;
  fullName: string;
  email: string;
  headline?: string;
  location?: string;
  phone?: string;
  linkedinUrl?: string;
  githubUrl?: string;
  portfolioUrl?: string;
  targetRoles: string[];
  targetIndustries: string[];
  salaryMin?: number;
  salaryMax?: number;
  workType: "remote" | "hybrid" | "onsite";
  yearsExperience: number;
  writingTone: "professional" | "confident" | "technical" | "concise";
};

export type ResumeStatus = "parsed" | "pending" | "failed" | "optimized";

export type ResumeExperience = {
  company: string;
  title: string;
  startDate: string;
  endDate: string;
  bullets: string[];
};

export type Resume = {
  id: string;
  label: string;
  fileName: string;
  version: number;
  status: ResumeStatus;
  strategy?: StrategyKey;
  parentResumeId?: string;
  atsScoreSnapshot?: number;
  skills: string[];
  experience: ResumeExperience[];
  projects: { name: string; description: string }[];
  education: { school: string; degree: string; year: string }[];
  certifications: string[];
  summary: string;
  createdAt: string;
};

export type Job = {
  id: string;
  title: string;
  company: string;
  companyUrl?: string;
  location: string;
  workType: "remote" | "hybrid" | "onsite";
  seniority: "intern" | "junior" | "mid" | "senior" | "staff" | "principal";
  domain: string;
  requiredSkills: string[];
  preferredSkills: string[];
  atsKeywords: string[];
  hiddenSignals: string[];
  tools: string[];
  softSkills: string[];
  salaryMin?: number;
  salaryMax?: number;
  rawText: string;
  createdAt: string;
};

export type ATSDimensionKey =
  | "keywordMatch"
  | "semanticMatch"
  | "technicalAlignment"
  | "seniorityAlignment"
  | "quantifiedImpact"
  | "atsSafety"
  | "readability"
  | "roleAlignment";

export const ATS_DIMENSIONS: { key: ATSDimensionKey; label: string }[] = [
  { key: "keywordMatch", label: "Keyword Match" },
  { key: "semanticMatch", label: "Semantic Match" },
  { key: "technicalAlignment", label: "Technical Alignment" },
  { key: "seniorityAlignment", label: "Seniority Alignment" },
  { key: "quantifiedImpact", label: "Quantified Impact" },
  { key: "atsSafety", label: "ATS Safety" },
  { key: "readability", label: "Readability" },
  { key: "roleAlignment", label: "Role Alignment" },
];

export type ATSScore = {
  id: string;
  resumeId: string;
  resumeName: string;
  jobId: string;
  jobTitle: string;
  jobCompany: string;
  overallScore: number; // 0-100
  dimensions: Record<ATSDimensionKey, number>; // 0-1
  missingKeywords: string[];
  weakSections: string[];
  recommendations: string[];
  recruiterCritique: string;
  atsSafe: boolean;
  safetyIssues: string[];
  createdAt: string;
};

export type StrategyKey =
  | "ats-aggressive"
  | "recruiter-friendly"
  | "startup-lean"
  | "enterprise-formal"
  | "technical-deep-dive"
  | "executive-style"
  | "one-page-compression"
  | "faang-style"
  | "european-cv";

export const STRATEGIES: { key: StrategyKey; name: string; icon: string; description: string }[] = [
  { key: "ats-aggressive", name: "ATS Aggressive", icon: "Target", description: "Maximum keyword density. Beat the filter." },
  { key: "recruiter-friendly", name: "Recruiter Friendly", icon: "Heart", description: "Skimmable, story-driven, recruiter-optimized." },
  { key: "startup-lean", name: "Startup Lean", icon: "Rocket", description: "Generalist-coded, impact-first, scrappy tone." },
  { key: "enterprise-formal", name: "Enterprise Formal", icon: "Building2", description: "Polished, structured, governance-friendly." },
  { key: "technical-deep-dive", name: "Technical Deep Dive", icon: "Cpu", description: "Stack details, architecture decisions, scale numbers." },
  { key: "executive-style", name: "Executive Style", icon: "Crown", description: "Leadership-forward, P&L outcomes, board-ready." },
  { key: "one-page-compression", name: "One-Page Compression", icon: "Minimize2", description: "Compress without losing signal. Perfect for early-career." },
  { key: "faang-style", name: "FAANG Style", icon: "Sparkles", description: "STAR bullets, quantified impact, scale-first." },
  { key: "european-cv", name: "European CV", icon: "Globe", description: "Europass-aligned format with full personal section." },
];

export type AsyncTask<T> = {
  id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress?: number;
  step?: string;
  result?: T;
  error?: string;
};
