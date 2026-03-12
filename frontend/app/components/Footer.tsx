import Link from "next/link";
import { Github, Linkedin } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-[#232329] py-8 px-6">
      <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <img
            src="/logo.png"
            alt="onepercentbetter.poker"
            className="h-5 w-auto"
            style={{ filter: "invert(1) hue-rotate(180deg)", opacity: 0.35 }}
          />
          <Link href="/about" className="text-xs text-[#4B4C58] hover:text-[#8A8B97] transition-colors">
            © {new Date().getFullYear()} Chris S. Yoon
          </Link>
        </div>
        <div className="flex items-center gap-5">
          <a
            href="https://linkedin.com/in/sukminyoon"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-[#4B4C58] hover:text-[#8A8B97] transition-colors"
          >
            <Linkedin size={12} />
            sukminyoon
          </a>
          <a
            href="https://github.com/sukminc"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-[#4B4C58] hover:text-[#8A8B97] transition-colors"
          >
            <Github size={12} />
            sukminc
          </a>
        </div>
      </div>
    </footer>
  );
}
