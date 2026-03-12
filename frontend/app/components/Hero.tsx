"use client";

import { ArrowDown } from "lucide-react";

export default function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col justify-center pt-16 px-6 overflow-hidden">

      {/* Spectral node background */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: "url('/hero-bg.png')",
          backgroundSize: "cover",
          backgroundPosition: "center right",
          backgroundRepeat: "no-repeat",
          opacity: 0.72,
        }}
      />

      {/* Fade left so headline stays readable */}
      <div className="absolute inset-0 pointer-events-none"
        style={{
          background: "linear-gradient(to right, #0D0D11 28%, transparent 65%, #0D0D11 98%)",
        }}
      />
      {/* Fade bottom into projects section */}
      <div className="absolute bottom-0 left-0 right-0 h-40 pointer-events-none"
        style={{ background: "linear-gradient(to bottom, transparent, #0D0D11)" }}
      />

      <div className="relative max-w-5xl mx-auto w-full">

        {/* Status chip */}
        <div className="inline-flex items-center gap-2 bg-[#5E5CE6]/10 border border-[#5E5CE6]/20 rounded-full px-3 py-1 mb-10">
          <span className="w-1.5 h-1.5 rounded-full bg-[#5E5CE6] animate-pulse" />
          <span className="text-xs text-[#8A8B97]">Active build</span>
        </div>

        {/* Headline */}
        <h1 className="text-6xl md:text-8xl font-bold tracking-tight leading-[1.02] mb-6">
          Marginal gains.
          <br />
          <span className="text-[#5E5CE6]">Exponential results.</span>
        </h1>

        {/* Description */}
        <p className="text-lg text-[#8A8B97] max-w-xl leading-relaxed mb-5">
          Every system has inefficiencies. Every market has edges.
          We build data tools that find them — and compound the advantage
          1% at a time.
        </p>

        {/* Byline */}
        <p className="text-sm text-[#4B4C58] mb-14">
          Built by{" "}
          <a
            href="https://linkedin.com/in/sukminyoon"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#8A8B97] hover:text-[#5E5CE6] transition-colors underline underline-offset-2 decoration-[#4B4C58]"
          >
            Chris S. Yoon
          </a>
          {" "}— Senior Data Engineer & AI builder
        </p>

        {/* CTA buttons */}
        <div className="flex items-center gap-3 flex-wrap">
          <a
            href="#projects"
            className="inline-flex items-center gap-2 bg-[#5E5CE6] hover:bg-[#7B79F7] text-white text-sm font-medium px-5 py-2.5 rounded-xl transition-colors"
          >
            See what&apos;s shipping
            <ArrowDown size={14} className="animate-bounce" />
          </a>
          <a
            href="#fund"
            className="inline-flex items-center gap-2 border border-[#232329] hover:border-[#36363F] text-[#8A8B97] hover:text-[#F7F8F8] text-sm px-5 py-2.5 rounded-xl transition-all"
          >
            Back the build
          </a>
        </div>

      </div>
    </section>
  );
}
