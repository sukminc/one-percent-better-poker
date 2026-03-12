"use client";

import { ArrowUpRight } from "lucide-react";

const experience = [
  {
    company: "onepercentbetter",
    role: "Founder & CEO",
    period: "Jul 2025 – Present",
    location: "Toronto, ON",
    bullets: [
      "Building AI-augmented data platforms with integrated LLM agent layers — implementing agentic orchestration using Claude API (Anthropic) and OpenAI API to automate data-driven decision loops.",
      "Hands-on application of dbt (data transformation), Kafka (streaming pipelines), and LLM integration patterns across active project architectures.",
      "Currently studying for Google Cloud Professional Data Engineer (GCP PDE).",
    ],
  },
  {
    company: "TheScore (Partnered with ESPN Bet)",
    role: "Senior Data Engineer",
    period: "Jul 2023 – Jul 2025",
    location: "Toronto, ON",
    bullets: [
      "Built and maintained Apache Airflow DAGs orchestrating nightly ingestion and transformation across BigQuery and AWS Redshift, processing millions of high-velocity betting transactions per day.",
      "Designed a Python-based observability framework monitoring 15+ ETL pipelines for volume anomalies and schema drift — automated alerting cut manual debugging effort by 60%.",
      "Developed SQL/Python transformation scripts for SOX-compliant financial and regulatory reporting, maintaining 100% audit trail coverage.",
      "Validated and optimized data workflows during large-scale legacy-to-cloud migration (GCP/AWS), ensuring zero data loss.",
    ],
  },
  {
    company: "Avesis",
    role: "Tech Lead (Contract via QA Consultants)",
    period: "Mar 2021 – Mar 2023",
    location: "Phoenix, AZ (Remote)",
    bullets: [
      "Led technical design of insurance ETL pipelines, defining data mapping specs and transformation rules for large-scale claims processing across enterprise Data Warehouses.",
      "Engineered automated Python data profiling routines that identified data corruption 40% earlier in the development lifecycle, preventing production incidents in underwriting workflows.",
    ],
  },
  {
    company: "Jewelers Mutual",
    role: "Data Engineer (Contract via QA Consultants)",
    period: "Feb 2020 – Mar 2021",
    location: "Neenah, WI (Remote)",
    bullets: [
      "Authored and optimized SQL and Python ETL scripts for Data Warehouse loading; implemented automated data profiling to surface quality issues at ingestion, before downstream impact.",
    ],
  },
  {
    company: "Wisetail (an Intertek Company)",
    role: "Data / QA Automation Engineer",
    period: "Aug 2019 – Feb 2020",
    location: "Toronto, ON",
    bullets: [
      "Integrated automated backend data validation workflows into Jenkins/GitHub Actions pipelines, providing real-time data quality visibility across policy management systems.",
    ],
  },
  {
    company: "Secret Location (eOne)",
    role: "SDET / QA Engineer",
    period: "Jul 2018 – Jul 2019",
    location: "Toronto, ON",
    bullets: [
      "Designed and executed automated data integrity test suites across distributed VR and mobile platforms, validating backend API consistency and catching critical regressions before production.",
      "Built SQL-based data consistency validation scripts and end-to-end integration tests for API-to-database layers across eOne content delivery pipelines.",
    ],
  },
  {
    company: "VRBO (Expedia Group)",
    role: "QA Engineer / Data Migration Analyst",
    period: "Jul 2016 – Mar 2018",
    location: "Toronto, ON",
    bullets: [
      "Led data integrity validation for a large-scale platform migration; built SQL reconciliation queries verifying source-to-target row counts and financial totals — zero data loss across millions of user records.",
      "Developed automated regression and smoke test suites validating booking and payment workflows across migration phases.",
    ],
  },
];

export default function About() {
  return (
    <section id="about" className="py-24 px-6 border-t border-[#111]">
      <div className="max-w-4xl mx-auto">

        {/* Open-to-work pill */}
        <div className="inline-flex items-center gap-2 border border-emerald-500/30 bg-emerald-500/5 rounded-full px-3 py-1 mb-10">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-emerald-400 font-mono tracking-widest uppercase">
            Open to Work — Data Engineering / AI Engineering Roles
          </span>
        </div>

        {/* Section label */}
        <span className="text-xs font-mono text-[#007AFF] tracking-widest uppercase">
          About
        </span>

        {/* Headline */}
        <h2 className="text-3xl md:text-4xl font-bold mt-3 tracking-tight text-white leading-snug mb-6">
          I built pipelines for ESPN Bet.{" "}
          <span className="text-[#333]">Now I build products with AI.</span>
        </h2>

        {/* Summary */}
        <div className="border-l-2 border-[#007AFF]/40 pl-5 mb-14">
          <p className="text-sm text-[#555] leading-relaxed">
            Senior Data Engineer with 10+ years making data systems production-worthy — by learning every way they fail, then engineering so they don&apos;t. At TheScore / ESPN Bet, designed Airflow-orchestrated ETL pipelines processing millions of daily transactions across BigQuery and Redshift; built a Python observability framework that cut debugging overhead by 60% and shipped SOX-compliant reconciliation systems under regulatory scrutiny.
          </p>
          <p className="text-sm text-[#555] leading-relaxed mt-3">
            Quality-first background means fail-fast DQ gates, schema drift detection, and self-validating pipelines baked in from day one — not bolted on after. When AI went from hype to production-ready, founded onepercentbetter: a live data platform with an LLM agent layer in active development. Full-stack across Python, SQL, Airflow, GCP, AWS, and Docker.
          </p>
        </div>

        {/* Experience timeline */}
        <div className="mb-14">
          <span className="text-xs font-mono text-[#007AFF] tracking-widest uppercase">
            Experience
          </span>

          <div className="mt-6 relative">
            <div className="absolute left-0 top-2 bottom-2 w-px bg-[#1a1a1a]" />

            <div className="flex flex-col gap-9 pl-6">
              {experience.map((e) => (
                <div key={e.company} className="relative">
                  <div className="absolute -left-[25px] top-1.5 w-2 h-2 rounded-full border border-[#007AFF]/50 bg-black" />

                  <div className="flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-1 mb-2">
                    <div>
                      <span className="text-sm font-semibold text-white font-mono">{e.company}</span>
                      <span className="text-xs text-[#007AFF] ml-2">{e.role}</span>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="text-[10px] font-mono text-[#333] block">{e.period}</span>
                      <span className="text-[10px] text-[#2a2a2a]">{e.location}</span>
                    </div>
                  </div>

                  <ul className="flex flex-col gap-1.5">
                    {e.bullets.map((b, i) => (
                      <li key={i} className="flex gap-2 text-xs text-[#555] leading-relaxed">
                        <span className="text-[#2a2a2a] shrink-0 mt-0.5">—</span>
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Education & Certs */}
        <div className="mb-14">
          <span className="text-xs font-mono text-[#007AFF] tracking-widest uppercase">
            Education & Certifications
          </span>

          <div className="mt-6 flex flex-col gap-3">
            <div className="flex items-start justify-between border border-[#1a1a1a] rounded-xl px-4 py-3 bg-black">
              <div>
                <p className="text-xs font-semibold text-white font-mono">University of Waterloo</p>
                <p className="text-[10px] text-[#555] mt-0.5">Studies in Chemical Engineering</p>
              </div>
              <span className="text-[10px] font-mono text-[#333]">2001 – 2005</span>
            </div>
            <div className="flex items-start justify-between border border-[#1a1a1a] rounded-xl px-4 py-3 bg-black">
              <div>
                <p className="text-xs font-semibold text-white font-mono">ISTQB Certified Tester</p>
                <p className="text-[10px] text-[#555] mt-0.5">Foundation Level (CTFL)</p>
              </div>
              <span className="text-[10px] font-mono text-emerald-500">Certified</span>
            </div>
            <div className="flex items-start justify-between border border-[#007AFF]/20 bg-[#007AFF]/5 rounded-xl px-4 py-3">
              <div>
                <p className="text-xs font-semibold text-white font-mono">Google Cloud Professional Data Engineer</p>
                <p className="text-[10px] text-[#555] mt-0.5">GCP PDE — Actively studying</p>
              </div>
              <span className="text-[10px] font-mono text-[#007AFF]">In Progress</span>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <a
            href="https://linkedin.com/in/sukminyoon"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-[#007AFF] text-white text-sm font-semibold px-5 py-2.5 rounded-md hover:bg-[#0066DD] transition-colors"
          >
            Connect on LinkedIn <ArrowUpRight size={14} />
          </a>
          <a
            href="https://github.com/sukminc"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 border border-[#2a2a2a] text-[#666] text-sm px-5 py-2.5 rounded-md hover:border-[#007AFF] hover:text-white transition-all"
          >
            View GitHub <ArrowUpRight size={14} />
          </a>
        </div>

      </div>
    </section>
  );
}
