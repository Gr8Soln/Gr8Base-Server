import {
  Resume, Job, ATSScore, Profile, ATS_DIMENSIONS, ATSDimensionKey,
} from "./types";

export const seedProfile: Profile = {
  id: "user-1",
  fullName: "Alex Morgan",
  email: "alex@caros.dev",
  headline: "Senior Software Engineer · Distributed Systems",
  location: "Berlin, Germany",
  phone: "+49 30 1234 5678",
  linkedinUrl: "https://linkedin.com/in/alexmorgan",
  githubUrl: "https://github.com/alexmorgan",
  portfolioUrl: "https://alexmorgan.dev",
  targetRoles: ["Senior Backend Engineer", "Staff Engineer", "Platform Engineer"],
  targetIndustries: ["FinTech", "Developer Tools", "Infrastructure"],
  salaryMin: 120000,
  salaryMax: 180000,
  workType: "remote",
  yearsExperience: 7,
  writingTone: "technical",
};

const dims = (vals: number[]): Record<ATSDimensionKey, number> => {
  const out: Record<string, number> = {};
  ATS_DIMENSIONS.forEach((d, i) => { out[d.key] = vals[i] ?? 0.5; });
  return out as Record<ATSDimensionKey, number>;
};

export const seedResumes: Resume[] = [
  {
    id: "resume-1",
    label: "Master Resume",
    fileName: "alex_morgan_resume.pdf",
    version: 1,
    status: "parsed",
    skills: ["Go", "Python", "Rust", "Kubernetes", "PostgreSQL", "gRPC", "Kafka", "AWS", "Terraform", "Distributed Systems"],
    summary: "Senior engineer with 7 years building high-throughput backend systems. Shipped trading infra processing 2M events/sec.",
    experience: [
      {
        company: "Northbound Capital", title: "Senior Backend Engineer", startDate: "2022-03", endDate: "Present",
        bullets: [
          "Built order matching engine processing 2M+ events/sec with p99 latency under 800µs.",
          "Led migration from monolith to 14 microservices, cutting deploy time from 45min to 6min.",
          "Designed event-sourced ledger handling $1.2B in daily transaction volume.",
        ],
      },
      {
        company: "Pageflow", title: "Backend Engineer", startDate: "2019-06", endDate: "2022-02",
        bullets: [
          "Owned the billing platform serving 80k customers across 12 currencies.",
          "Reduced infra costs by 38% through query optimization and caching layer redesign.",
        ],
      },
    ],
    projects: [
      { name: "ratemyk8s", description: "OSS tool that audits Kubernetes clusters for cost waste. 2.3k stars." },
    ],
    education: [{ school: "TU Berlin", degree: "M.Sc. Computer Science", year: "2018" }],
    certifications: ["AWS Solutions Architect — Associate", "CKA"],
    createdAt: "2025-04-12T10:00:00Z",
    atsScoreSnapshot: 64.5,
  },
  {
    id: "resume-2",
    label: "Stripe Application — v2",
    fileName: "alex_morgan_stripe_v2.pdf",
    version: 2,
    status: "optimized",
    strategy: "ats-aggressive",
    parentResumeId: "resume-1",
    atsScoreSnapshot: 87.2,
    skills: ["Go", "Python", "Rust", "Kubernetes", "PostgreSQL", "gRPC", "Kafka", "AWS", "Terraform", "Stripe API", "Payments", "PCI-DSS"],
    summary: "Senior backend engineer specializing in payments infrastructure. 7 years scaling financial systems handling billions in volume.",
    experience: [
      {
        company: "Northbound Capital", title: "Senior Backend Engineer", startDate: "2022-03", endDate: "Present",
        bullets: [
          "Architected event-sourced payments ledger handling $1.2B daily volume with strong consistency guarantees.",
          "Built Go-based order matching engine: 2M events/sec throughput, p99 latency 800µs, 99.99% uptime SLA.",
          "Led migration to 14 microservices on Kubernetes (AWS EKS), reducing deploy cycle 87% (45min → 6min).",
          "Owned PCI-DSS compliance posture across payment-handling services; passed SOC2 Type II audit.",
        ],
      },
    ],
    projects: [{ name: "ratemyk8s", description: "OSS Kubernetes cost-audit tool, 2.3k stars on GitHub." }],
    education: [{ school: "TU Berlin", degree: "M.Sc. Computer Science", year: "2018" }],
    certifications: ["AWS Solutions Architect — Associate", "Certified Kubernetes Administrator (CKA)"],
    createdAt: "2025-05-20T14:30:00Z",
  },
  {
    id: "resume-3",
    label: "Concise One-Pager",
    fileName: "alex_morgan_short.pdf",
    version: 1,
    status: "parsed",
    skills: ["Go", "Python", "Kubernetes", "PostgreSQL", "AWS"],
    summary: "Senior backend engineer. Distributed systems, payments, scale.",
    experience: [
      {
        company: "Northbound Capital", title: "Senior Backend Engineer", startDate: "2022-03", endDate: "Present",
        bullets: ["Built matching engine: 2M events/sec, p99 800µs.", "Migrated monolith → 14 microservices."],
      },
    ],
    projects: [],
    education: [{ school: "TU Berlin", degree: "M.Sc. CS", year: "2018" }],
    certifications: [],
    createdAt: "2025-05-01T09:00:00Z",
  },
];

export const seedJobs: Job[] = [
  {
    id: "job-1",
    title: "Senior Software Engineer, Payments",
    company: "Stripe",
    companyUrl: "https://stripe.com",
    location: "Remote (EU)",
    workType: "remote",
    seniority: "senior",
    domain: "Payments / FinTech",
    requiredSkills: ["Go", "Distributed Systems", "PostgreSQL", "Kafka", "gRPC", "Kubernetes"],
    preferredSkills: ["Rust", "Payments Infrastructure", "PCI-DSS", "Event Sourcing"],
    atsKeywords: ["distributed systems", "high availability", "low latency", "Go", "microservices", "Kubernetes", "PostgreSQL", "Kafka", "payments", "PCI", "SLA", "p99", "throughput"],
    hiddenSignals: [
      "Mentions 'ownership' 4× — they want self-directed senior engineers.",
      "Calls out 'mentoring' — staff-track promotion path implied.",
      "Required: experience operating systems at >1B daily transactions.",
    ],
    tools: ["Go", "Kubernetes", "PostgreSQL", "Kafka", "Datadog", "Terraform", "AWS"],
    softSkills: ["Ownership", "Cross-team collaboration", "Written communication"],
    salaryMin: 165000,
    salaryMax: 220000,
    rawText: "About the role...",
    createdAt: "2025-05-18T08:00:00Z",
  },
  {
    id: "job-2",
    title: "Staff Platform Engineer",
    company: "Vercel",
    companyUrl: "https://vercel.com",
    location: "Remote",
    workType: "remote",
    seniority: "staff",
    domain: "Developer Tools / Infrastructure",
    requiredSkills: ["Go", "TypeScript", "Kubernetes", "Edge Compute", "Distributed Systems"],
    preferredSkills: ["Rust", "WebAssembly", "CDN architecture"],
    atsKeywords: ["edge", "serverless", "platform", "Go", "TypeScript", "Kubernetes", "scale", "global", "latency", "developer experience"],
    hiddenSignals: [
      "'You define the technical strategy' — staff IC role, not management.",
      "Public technical writing strongly preferred.",
    ],
    tools: ["Go", "TypeScript", "Kubernetes", "Cloudflare Workers", "AWS"],
    softSkills: ["Technical leadership", "Written communication", "Long-horizon planning"],
    salaryMin: 200000,
    salaryMax: 280000,
    rawText: "Vercel is hiring...",
    createdAt: "2025-05-22T11:15:00Z",
  },
];

export const seedScores: ATSScore[] = [
  {
    id: "score-1",
    resumeId: "resume-1",
    resumeName: "Master Resume",
    jobId: "job-1",
    jobTitle: "Senior Software Engineer, Payments",
    jobCompany: "Stripe",
    overallScore: 64.5,
    dimensions: dims([0.62, 0.71, 0.68, 0.85, 0.55, 0.92, 0.78, 0.6]),
    missingKeywords: ["PCI-DSS", "Payments Infrastructure", "Event Sourcing", "Stripe API"],
    weakSections: ["Summary lacks payments domain language.", "Bullets under-quantify customer impact."],
    recommendations: [
      "Add 'PCI-DSS' and 'payments infrastructure' to skills and summary.",
      "Rewrite Northbound bullets to lead with $-impact and transaction volume.",
      "Surface event-sourcing experience explicitly — it's mentioned in JD twice.",
    ],
    recruiterCritique: "Strong technical foundation but reads as generic backend. For Stripe, payments-specific signal needs to be on page 1 — domain expertise here beats breadth. Lead with transaction volume and compliance posture.",
    atsSafe: true,
    safetyIssues: [],
    createdAt: "2025-05-19T13:20:00Z",
  },
  {
    id: "score-2",
    resumeId: "resume-2",
    resumeName: "Stripe Application — v2",
    jobId: "job-1",
    jobTitle: "Senior Software Engineer, Payments",
    jobCompany: "Stripe",
    overallScore: 87.2,
    dimensions: dims([0.91, 0.88, 0.85, 0.88, 0.84, 0.95, 0.82, 0.86]),
    missingKeywords: ["Webhooks at scale"],
    weakSections: ["Could add 1-2 more quantified outcomes."],
    recommendations: [
      "Consider adding webhook-handling experience if applicable.",
      "Add a one-line project description tying OSS work to payments.",
    ],
    recruiterCritique: "Excellent alignment. Payments domain is now front-and-center, quantified outcomes throughout. Would shortlist this candidate.",
    atsSafe: true,
    safetyIssues: [],
    createdAt: "2025-05-20T14:45:00Z",
  },
];
