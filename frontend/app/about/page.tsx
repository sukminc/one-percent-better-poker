import Link from "next/link";
import About from "../components/About";

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-[#0D0D11] text-[#F7F8F8]">
      <div className="max-w-4xl mx-auto px-6 pt-10 pb-4">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-[#4B4C58] hover:text-[#8A8B97] transition-colors"
        >
          ← Back
        </Link>
      </div>
      <About />
    </main>
  );
}
