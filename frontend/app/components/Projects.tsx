"use client";

import { ArrowUpRight, Clock, ExternalLink, GitBranch } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import {
  SiNextdotjs, SiFastapi, SiPython, SiPandas, SiNumpy, SiVercel,
  SiPostgresql, SiDocker, SiApacheairflow, SiGithubactions, SiTypescript,
  SiFlutter, SiDart, SiSupabase, SiStripe, SiPytest, SiApple, SiAndroid,
  SiSqlalchemy,
} from "react-icons/si";
import { projects, type Project, type ProjectStatus } from "../data/projects";

const BMAC = "https://buymeacoffee.com/chris.yoon";
const GH_OWNER = "sukminc";

const REPO_MAP: Record<string, string> = Object.fromEntries(
  projects.filter((p) => p.repoName).map((p) => [p.slug, p.repoName!])
);

interface Commit {
  sha:     string;
  message: string;
  date:    string;
  url:     string;
}

interface CommitState {
  commits:    Commit[];
  totalCount: number | null;
  loading:    boolean;
}

const statusConfig: Record<ProjectStatus, { label: string; color: string; dot: string }> = {
  live:     { label: "Live",     color: "text-emerald-400", dot: "bg-emerald-400" },
  building: { label: "Building", color: "text-[#5E5CE6]",   dot: "bg-[#5E5CE6] animate-pulse" },
  idea:     { label: "Idea",     color: "text-[#4B4C58]",   dot: "bg-[#4B4C58]" },
};

const STATUS_BAR: Record<string, string> = {
  live:     "bg-emerald-400",
  building: "bg-[#5E5CE6]",
  idea:     "bg-[#4B4C58]",
};

type IconComponent = React.ComponentType<{ size?: number; color?: string; className?: string }>;

const TECH_ICONS: Record<string, { Icon: IconComponent; color: string }> = {
  "Next.js":              { Icon: SiNextdotjs,      color: "#ffffff" },
  "FastAPI":              { Icon: SiFastapi,         color: "#009688" },
  "Python":               { Icon: SiPython,          color: "#3776AB" },
  "Python (FastAPI)":     { Icon: SiFastapi,         color: "#009688" },
  "TypeScript":           { Icon: SiTypescript,      color: "#3178C6" },
  "TypeScript (Next.js)": { Icon: SiNextdotjs,       color: "#ffffff" },
  "SQLAlchemy":           { Icon: SiSqlalchemy,      color: "#D71F00" },
  "Pandas":               { Icon: SiPandas,          color: "#9575CD" },
  "NumPy":                { Icon: SiNumpy,           color: "#4DABF7" },
  "Vercel":               { Icon: SiVercel,          color: "#ffffff" },
  "PostgreSQL":           { Icon: SiPostgresql,      color: "#4169E1" },
  "Docker":               { Icon: SiDocker,          color: "#2496ED" },
  "Apache Airflow":       { Icon: SiApacheairflow,   color: "#017CEE" },
  "GitHub Actions":       { Icon: SiGithubactions,   color: "#2088FF" },
  "Flutter":              { Icon: SiFlutter,         color: "#54C5F8" },
  "Dart":                 { Icon: SiDart,            color: "#0175C2" },
  "Supabase":             { Icon: SiSupabase,        color: "#3ECF8E" },
  "Stripe":               { Icon: SiStripe,          color: "#635BFF" },
  "Pytest":               { Icon: SiPytest,          color: "#0A9EDC" },
  "iOS":                  { Icon: SiApple,           color: "#ffffff" },
  "Android":              { Icon: SiAndroid,         color: "#34A853" },
};

function TechBadge({ tag }: { tag: string }) {
  const entry = TECH_ICONS[tag];
  if (entry) {
    const { Icon, color } = entry;
    return (
      <div title={tag} className="w-6 h-6 rounded-md bg-[#1C1C1F] border border-[#232329] flex items-center justify-center">
        <Icon size={13} color={color} />
      </div>
    );
  }
  // Named tech without an icon — dot + label, same height as icon badges
  return (
    <div title={tag} className="h-6 flex items-center gap-1.5 bg-[#1C1C1F] border border-[#232329] rounded-md px-2">
      <span className="w-1 h-1 rounded-full bg-[#4B4C58] flex-shrink-0" />
      <span className="text-[10px] text-[#4B4C58] leading-none">{tag}</span>
    </div>
  );
}

function timeAgo(iso: string): string {
  const s = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60)   return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60)   return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24)   return `${h}h ago`;
  const d = Math.floor(h / 24);
  if (d < 30)   return `${d}d ago`;
  return `${Math.floor(d / 30)}mo ago`;
}

function ProjectCard({ project, commitState }: { project: Project; commitState: CommitState }) {
  const cfg = statusConfig[project.status];
  const repoName = REPO_MAP[project.slug];

  return (
    <div className={project.featured ? "md:col-span-2" : ""}>
      <div
        className={`flex flex-col rounded-2xl p-6 bg-[#161618] border transition-colors h-full ${
          project.featured
            ? "border-[#5E5CE6]/25 hover:border-[#5E5CE6]/40"
            : "border-[#232329] hover:border-[#36363F]"
        }`}
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${cfg.dot}`} />
              <h3 className="text-sm font-semibold text-[#F7F8F8] truncate">{project.title}</h3>
            </div>
            {repoName && (
              <div className="flex items-center gap-1.5 text-[10px] text-[#4B4C58] pl-3.5">
                <GitBranch size={9} />
                <span className="font-mono">{GH_OWNER}/{repoName}</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2.5 flex-shrink-0">
            {commitState.totalCount !== null && (
              <div className="text-right">
                <span className="text-base font-bold text-[#F7F8F8] leading-none">{commitState.totalCount}</span>
                <p className="text-[9px] text-[#4B4C58]">commits</p>
              </div>
            )}
            <a
              href={BMAC}
              target="_blank"
              rel="noopener noreferrer"
              className="w-7 h-7 rounded-lg border border-[#232329] flex items-center justify-center text-[#4B4C58] hover:border-[#5E5CE6]/40 hover:text-[#5E5CE6] transition-all"
            >
              <ArrowUpRight size={13} />
            </a>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mb-4">
          <div className="flex justify-between text-[10px] text-[#4B4C58] mb-1.5">
            <span className="truncate pr-2">{project.tagline}</span>
            <span className="flex-shrink-0">
              {project.mvpProgress === 100 ? "Live ✓" : `${project.mvpProgress}%`}
            </span>
          </div>
          <div className="h-1 bg-[#232329] rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${STATUS_BAR[project.status] ?? "bg-[#4B4C58]"}`}
              style={{ width: `${project.mvpProgress}%` }}
            />
          </div>
        </div>

        {/* Commit feed */}
        <div className="flex flex-col gap-0.5 mb-4 flex-1">
          {commitState.loading && (
            <div className="space-y-2 py-1">
              {[0, 1, 2].map((i) => (
                <div key={i} className="flex gap-2.5 animate-pulse">
                  <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-[#232329] flex-shrink-0" />
                  <div className="flex-1 space-y-1.5">
                    <div className="h-2.5 bg-[#1C1C1F] rounded w-3/4" />
                    <div className="h-2 bg-[#1C1C1F] rounded w-1/3" />
                  </div>
                </div>
              ))}
            </div>
          )}
          {!commitState.loading &&
            commitState.commits.map((c, i) => (
              <a
                key={c.sha}
                href={c.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-start gap-2.5 py-1.5 hover:bg-white/[0.02] rounded-lg px-1.5 -mx-1.5 transition-colors"
              >
                <div className={`mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0 ${i === 0 ? "bg-[#5E5CE6]" : "bg-[#36363F]"}`} />
                <div className="flex-1 min-w-0">
                  <p className={`text-xs truncate leading-snug ${i === 0 ? "text-[#F7F8F8]" : "text-[#8A8B97]"} group-hover:text-[#F7F8F8] transition-colors`}>
                    {c.message.split("\n")[0]}
                  </p>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <code className="text-[9px] text-[#4B4C58] font-mono">{c.sha.slice(0, 7)}</code>
                    <span className="text-[9px] text-[#36363F]">·</span>
                    <span className="flex items-center gap-1 text-[9px] text-[#4B4C58]">
                      <Clock size={8} />
                      {timeAgo(c.date)}
                    </span>
                  </div>
                </div>
                <ExternalLink size={10} className="mt-1 flex-shrink-0 text-[#4B4C58] opacity-0 group-hover:opacity-100 transition-opacity" />
              </a>
            ))}
        </div>

        {/* Tech icons */}
        <div className="flex flex-wrap gap-1.5 mb-5">
          {project.tags.map((tag) => (
            <TechBadge key={tag} tag={tag} />
          ))}
        </div>

        {/* Single fund CTA → scrolls to #fund */}
        <a
          href="#fund"
          className="flex items-center justify-between w-full rounded-xl border border-[#232329] hover:border-[#5E5CE6]/40 bg-[#1C1C1F] hover:bg-[#5E5CE6]/5 px-4 py-3 transition-all group"
        >
          <span className="text-sm text-[#8A8B97] group-hover:text-[#F7F8F8] transition-colors">
            Back this build
          </span>
          <ArrowUpRight size={14} className="text-[#4B4C58] group-hover:text-[#5E5CE6] transition-colors" />
        </a>
      </div>
    </div>
  );
}

export default function Projects() {
  const [commitMap, setCommitMap] = useState<Record<string, CommitState>>(() =>
    Object.fromEntries(
      projects.map((p) => [p.slug, { commits: [], totalCount: null, loading: !!REPO_MAP[p.slug] }])
    )
  );

  // Stable sort order — set once when commits first arrive, never re-shuffled
  const sortedSlugsRef = useRef<string[] | null>(null);
  const loadedCount = useRef(0);
  const totalRepos = projects.filter((p) => REPO_MAP[p.slug]).length;

  useEffect(() => {
    projects.forEach(async (project) => {
      const repoName = REPO_MAP[project.slug];
      if (!repoName) return;
      try {
        const res = await fetch(`/api/commits?repo=${repoName}`);
        if (!res.ok) throw new Error(`${res.status}`);
        const data = await res.json();
        setCommitMap((prev) => ({
          ...prev,
          [project.slug]: { commits: data.commits, totalCount: data.totalCount, loading: false },
        }));
      } catch {
        setCommitMap((prev) => ({
          ...prev,
          [project.slug]: { commits: [], totalCount: null, loading: false },
        }));
      } finally {
        loadedCount.current += 1;
        // Lock sort order once all repos have responded
        if (loadedCount.current >= totalRepos && !sortedSlugsRef.current) {
          setCommitMap((snap) => {
            sortedSlugsRef.current = [...projects]
              .sort((a, b) => {
                const aDate = snap[a.slug]?.commits[0]?.date ?? "";
                const bDate = snap[b.slug]?.commits[0]?.date ?? "";
                return bDate.localeCompare(aDate);
              })
              .map((p) => p.slug);
            return snap;
          });
        }
      }
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const displayOrder = sortedSlugsRef.current
    ? sortedSlugsRef.current.map((slug) => projects.find((p) => p.slug === slug)!).filter(Boolean)
    : projects;

  return (
    <section id="projects" className="py-24 px-6 border-t border-[#232329]">
      <div className="max-w-5xl mx-auto">
        <div className="mb-10">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <p className="text-xs text-[#8A8B97]">Projects · Live from GitHub</p>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-[#F7F8F8] tracking-tight">
            Sorted by{" "}
            <span className="text-[#4B4C58]">latest activity.</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {displayOrder.map((p) => (
            <ProjectCard
              key={p.slug}
              project={p}
              commitState={commitMap[p.slug] ?? { commits: [], totalCount: null, loading: false }}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
