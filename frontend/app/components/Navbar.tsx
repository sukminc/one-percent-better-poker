"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "bg-[#0F0F11]/80 backdrop-blur-md border-b border-[#232329]" : "bg-transparent"
      }`}
    >
      <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <img
            src="/logo.svg"
            alt="onepercentbetter"
            className="h-8 w-8 transition-opacity group-hover:opacity-80"
          />
          <span className="text-sm font-semibold text-[#F7F8F8] tracking-tight leading-none hidden sm:block">
            onepercentbetter
          </span>
        </Link>

        <div className="flex items-center gap-6">
          <a href="#projects" className="text-sm text-[#8A8B97] hover:text-[#F7F8F8] transition-colors">
            Projects
          </a>
          <Link href="/about" className="text-sm text-[#8A8B97] hover:text-[#F7F8F8] transition-colors">
            About
          </Link>
        </div>
      </div>
    </nav>
  );
}
