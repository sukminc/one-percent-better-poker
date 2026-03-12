export type ProjectStatus = "live" | "building" | "idea";

export interface Project {
  slug: string;
  title: string;
  tagline: string;
  description: string;
  status: ProjectStatus;
  tags: string[];
  url?: string;
  featured?: boolean;
  seed: number;
  mvpProgress: number; // 0–100
  repoName?: string;   // GitHub repo name under sukminc/ (omit if no repo)
}

export const projects: Project[] = [
  {
    slug: "onepercentbetter",
    repoName: "one-percent-better",
    title: "onepercentbetter",
    tagline: "Performance Analytics & Edge Intelligence Platform",
    description:
      "End-to-end analytics platform built on FastAPI + Pandas/NumPy that quantifies behavioral deviations from optimal baselines, scores tendency patterns, and surfaces positional exploit signals. Architected for LLM agent integration: deviation signals feed an AI recommendation engine that generates actionable edge — the core agentic decision loop.",
    status: "building",
    tags: ["Next.js", "FastAPI", "SQLAlchemy", "Pandas", "NumPy", "Vercel"],
    url: "https://onepercentbetter.poker",
    featured: true,
    seed: 47,
    mvpProgress: 55,
  },
  {
    slug: "bluejays-moneyball",
    repoName: "bluejays-financial-mlops",
    title: "Blue Jays Moneyball ETL",
    tagline: "Production-Grade ELT & Self-Validating Pipeline",
    description:
      "Airflow + PostgreSQL pipeline integrating Spotrac payroll vs. MLB stats; DQ gates block all downstream transformation until checks pass — no silent failures. Regression DAG fires known-bad datasets against DQ gates, asserting failure — guardrails are CI/CD citizens that break the build if the safety net breaks.",
    status: "live",
    tags: ["Python", "Apache Airflow", "PostgreSQL", "Docker", "GitHub Actions"],
    url: "https://github.com/sukminc/bluejays-financial-mlops",
    seed: 18,
    mvpProgress: 100,
  },
  {
    slug: "actionkeeper",
    repoName: "action-keeper",
    title: "ActionKeeper",
    tagline: "Full-Stack Agreement & Negotiation Platform",
    description:
      "FastAPI + PostgreSQL with Clean Architecture (Service/Repository layers); tamper-evident SHA-256 receipt hashing and dual-confirmation negotiation engine with full persistent audit trail. Turn-based Accept/Counter/Decline workflow with visual term diffs, side-by-side counter-offer comparison, and real-time payout previews.",
    status: "building",
    tags: ["Python (FastAPI)", "TypeScript (Next.js)", "PostgreSQL", "Docker", "Stripe"],
    url: "https://github.com/sukminc/action-keeper",
    seed: 31,
    mvpProgress: 40,
  },
  {
    slug: "onepercent-focus",
    repoName: "OneBetterFocus",
    title: "1% Better Focus",
    tagline: "Minimalist Deep-Work Timer for iOS, Android & Web",
    description:
      "Flutter app built on the Pomodoro method — distraction-free 25/5 focus sessions with a dimming UI, confetti celebration on completion, and emoji self-reflection. Riverpod state engine fully decoupled from UI; local-first streak tracking with Supabase sync roadmapped. Freemium-ready with feature-flagged custom time sets for future IAP.",
    status: "building",
    tags: ["Flutter", "Dart", "Supabase", "iOS", "Android"],
    url: "https://github.com/sukminc/OneBetterFocus",
    seed: 63,
    mvpProgress: 70,
  },
  {
    slug: "twelvelabs-validator",
    repoName: "TwelveLabs",
    title: "TwelveLabs API Validator",
    tagline: "Multimodal Search Validation Framework",
    description:
      "JSON-driven validation suite for TwelveLabs multimodal video search API — decouples test logic from test data; covers linguistic edge cases (plurals, i18n: Korean/Japanese/Arabic), fuzzy matching, and injection attempts. Built to the same standard as a production observability tool.",
    status: "live",
    tags: ["Python", "TwelveLabs", "Pytest"],
    url: "https://github.com/sukminc/TwelveLabs",
    seed: 12,
    mvpProgress: 100,
  },
];
