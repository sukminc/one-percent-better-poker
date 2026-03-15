import Link from "next/link";
import { InstantReviewDemo } from "./components/InstantReviewDemo";

const tiers = [
  {
    label: "Open",
    amount: "$30",
    note: "3 your patterns · one-line reasons.",
    href: "https://buy.stripe.com/fZu8wQbT81DO8dIf6I1wY00",
  },
  {
    label: "3-Bet",
    amount: "$150",
    note: "3 patterns · more quantified reasons · limited depth.",
    href: "https://buy.stripe.com/5kQbJ20aqeqA51w4s41wY01",
  },
  {
    label: "All-In",
    amount: "$2,000",
    note: "Higher limits · continuous tracking over time.",
    href: "https://buy.stripe.com/28EfZi3mCfuE1Pk7Eg1wY03",
  },
];

const steps = [
  {
    value: "1",
    label: "Tournament",
    detail: "Upload one tournament first.",
  },
  {
    value: "3",
    label: "Habits",
    detail: "Catch the habits you repeat.",
  },
  {
    value: "1",
    label: "Adjustment",
    detail: "Leave with one next change.",
  },
];

const philosophy = [
  {
    title: "Your pattern",
    copy: "The only thing you can really control is the pattern you keep repeating.",
  },
  {
    title: "Their pattern",
    copy: "You do not know what they do behind the monitor. Their behavior still repeats.",
  },
  {
    title: "1% better",
    copy: "The goal is not perfect theory. The goal is one honest adjustment for the next session.",
  },
];

const counterPromises = [
  "Pick one habit only.",
  "Set a small honest target.",
  "Tap through the session.",
];

const counterExamples = [
  "You will CALL less than 3 times.",
  "You will RAISE more than 2 times.",
  "You will FOLD from Button more than 1 time.",
];

export default function Home() {
  return (
    <main className="min-h-screen bg-[var(--color-background)] text-[var(--color-foreground)]">
      <section className="hero-shell px-6 pb-16 pt-8 sm:pb-20 sm:pt-10">
        <div className="mx-auto max-w-6xl">
          <div className="flex items-center justify-between border-b border-[var(--color-line)] pb-5">
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[var(--color-muted)]">
              1% Better Poker
            </p>
            <div className="flex items-center gap-2">
              <Link
                href="/counter"
                className="inline-flex items-center rounded-full border border-[rgba(28,120,255,0.28)] bg-[rgba(28,120,255,0.1)] px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-white transition-colors hover:border-[var(--color-secondary-accent)] hover:bg-[rgba(28,120,255,0.16)]"
              >
                Live counter
              </Link>
              <a
                href="#back"
                className="inline-flex items-center rounded-full border border-[var(--color-line)] px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-white transition-colors hover:border-[var(--color-accent)] hover:bg-[rgba(255,154,61,0.1)]"
              >
                Back it
              </a>
            </div>
          </div>

          <div className="mt-10 grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-end">
            <div className="max-w-2xl">
              <p className="inline-flex items-center rounded-full bg-[rgba(255,154,61,0.12)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--color-accent)]">
                Exploit Better
              </p>
              <h1 className="mt-5 text-5xl font-semibold tracking-[-0.07em] text-white sm:text-7xl sm:leading-[0.92]">
                Your pattern.
                <br />
                Their leaks.
                <br />
                One better session.
              </h1>
              <p className="mt-6 max-w-lg text-lg leading-8 text-[var(--color-secondary)]">
                Upload one tournament for a pattern read. Or walk into a live session with one habit and count it honestly.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <a
                  href="#mvp"
                  className="rounded-full bg-[var(--color-accent)] px-5 py-3 text-sm font-semibold text-[#0e1831] transition-transform hover:-translate-y-0.5"
                >
                  See the MVP
                </a>
                <Link
                  href="/counter"
                  className="rounded-full border border-[rgba(28,120,255,0.28)] bg-[rgba(28,120,255,0.08)] px-5 py-3 text-sm font-semibold text-white transition-colors hover:border-[var(--color-secondary-accent)] hover:bg-[rgba(28,120,255,0.14)]"
                >
                  Open counter
                </Link>
                <a
                  href="#back"
                  className="rounded-full border border-[var(--color-line)] bg-[rgba(28,120,255,0.08)] px-5 py-3 text-sm font-semibold text-white transition-colors hover:border-[var(--color-secondary-accent)] hover:bg-[rgba(28,120,255,0.14)]"
                >
                  Fund the build
                </a>
              </div>
            </div>

            <InstantReviewDemo />
          </div>
        </div>
      </section>

      <section id="counter" className="px-6 pb-16 sm:pb-20">
        <div className="mx-auto max-w-6xl">
          <div className="book-panel rounded-[2rem] p-6 sm:p-8">
            <div className="grid gap-8 lg:grid-cols-[0.82fr_1.18fr] lg:items-center">
              <div className="max-w-xl">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--color-secondary-accent)]">
                  Live counter
                </p>
                <h2 className="mt-4 text-3xl font-semibold tracking-[-0.06em] text-white sm:text-5xl">
                  One promise.
                  <br />
                  One session.
                </h2>
                <p className="mt-5 text-base leading-7 text-[var(--color-secondary)]">
                  The counter is the live version of the same philosophy. Pick one action, choose more or less, set a small target, and keep one promise to yourself.
                </p>

                <div className="mt-6 space-y-3">
                  {counterPromises.map((item) => (
                    <div key={item} className="mini-panel rounded-[1.25rem] px-4 py-3 text-sm text-white">
                      {item}
                    </div>
                  ))}
                </div>

                <div className="mt-6 flex flex-wrap gap-3">
                  <Link
                    href="/counter"
                    className="rounded-full bg-[var(--color-secondary-accent)] px-5 py-3 text-sm font-semibold text-white transition-transform hover:-translate-y-0.5"
                  >
                    Launch 1% Better Counter
                  </Link>
                  <a
                    href="#mvp"
                    className="rounded-full border border-[var(--color-line)] px-5 py-3 text-sm font-semibold text-white transition-colors hover:border-[var(--color-accent)] hover:bg-[rgba(255,154,61,0.08)]"
                  >
                    See the upload flow
                  </a>
                </div>
              </div>

              <div className="review-panel rounded-[2rem] p-5 sm:p-6">
                <div className="flex items-center justify-between border-b border-[var(--color-line)] pb-4">
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--color-muted)]">
                      1% Better Counter
                    </p>
                    <p className="mt-2 text-2xl font-semibold tracking-[-0.05em] text-white">
                      Track one habit now.
                    </p>
                  </div>
                  <span className="rounded-full border border-[rgba(255,154,61,0.24)] bg-[rgba(255,154,61,0.1)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--color-accent)]">
                    Live
                  </span>
                </div>

                <div className="mt-5 rounded-[1.5rem] border border-[var(--color-line)] bg-[rgba(255,255,255,0.02)] p-5">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--color-muted)]">
                    Session goal
                  </p>
                  <p className="mt-3 text-xl font-semibold text-white">
                    {counterExamples[0]}
                  </p>

                  <div className="mt-6 flex items-center gap-5">
                    <div
                      className="relative h-48 w-48 shrink-0 rounded-full"
                      style={{
                        background:
                          "conic-gradient(from 270deg, rgba(28,120,255,1) 0deg, rgba(28,120,255,1) 216deg, rgba(255,255,255,0.08) 216deg, rgba(255,255,255,0.08) 360deg)",
                      }}
                    >
                      <div className="absolute inset-[16px] rounded-full bg-[linear-gradient(180deg,rgba(13,24,48,0.98),rgba(9,16,30,0.99))]" />
                      <div className="absolute inset-[38px] flex items-center justify-center rounded-full border border-[rgba(255,255,255,0.06)] bg-[radial-gradient(circle_at_top,rgba(28,120,255,0.2),transparent_55%),rgba(255,255,255,0.03)]">
                        <span className="text-6xl font-semibold tracking-[-0.08em] text-white">
                          2
                        </span>
                      </div>
                    </div>

                    <div className="min-w-0 flex-1 space-y-3">
                      {counterExamples.map((example, index) => (
                        <div
                          key={example}
                          className={`rounded-[1.15rem] border px-4 py-3 text-sm leading-6 ${
                            index === 0
                              ? "border-[rgba(28,120,255,0.3)] bg-[rgba(28,120,255,0.1)] text-white"
                              : "border-[var(--color-line)] bg-[rgba(255,255,255,0.02)] text-[var(--color-secondary)]"
                          }`}
                        >
                          {example}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mt-6 rounded-full border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.04)] p-2">
                    <div className="score-bar h-3 w-[66%] rounded-full" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="mvp" className="px-6 pb-16 sm:pb-20">
        <div className="mx-auto max-w-6xl">
          <div className="book-panel rounded-[2rem] p-6 sm:p-8">
            <div className="grid gap-8 lg:grid-cols-[0.82fr_1.18fr] lg:items-start">
              <div className="max-w-xl">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--color-accent)]">
                  MVP promise
                </p>
                <h2 className="mt-4 text-3xl font-semibold tracking-[-0.06em] text-white sm:text-5xl">
                  Demo first.
                  <br />
                  Depth later.
                </h2>
                <p className="mt-5 text-base leading-7 text-[var(--color-secondary)]">
                  The free version shows one table dynamic and one next move. Paid tiers unlock more patterns, better reasons, and longer tracking.
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                {steps.map((step) => (
                  <div key={step.label} className="mini-panel rounded-[1.5rem] p-5">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--color-secondary-accent)]">
                      {step.label}
                    </p>
                    <p className="mt-4 text-5xl font-semibold tracking-[-0.06em] text-white">
                      {step.value}
                    </p>
                    <p className="mt-3 text-sm leading-6 text-[var(--color-secondary)]">
                      {step.detail}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="philosophy" className="px-6 pb-16 sm:pb-20">
        <div className="mx-auto max-w-6xl">
          <div className="book-panel rounded-[2rem] p-6 sm:p-8">
            <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
              <div className="max-w-xl">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--color-accent)]">
                  Why this matters
                </p>
                <h2 className="mt-4 text-3xl font-semibold tracking-[-0.06em] text-white sm:text-5xl">
                  Real poker is pattern.
                </h2>
                <p className="mt-5 text-base leading-7 text-[var(--color-secondary)]">
                  GTO studies perfect theory. Real online tournaments repeat human habits.
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                {philosophy.map((item) => (
                  <div key={item.title} className="mini-panel rounded-[1.5rem] p-5">
                    <p className="text-[12px] font-semibold uppercase tracking-[0.14em] text-[var(--color-accent)]">
                      {item.title}
                    </p>
                    <p className="mt-3 text-sm leading-6 text-[var(--color-secondary)]">
                      {item.copy}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="back" className="px-6 pb-24">
        <div className="mx-auto max-w-6xl">
          <div className="review-panel rounded-[2rem] p-6 sm:p-8">
            <div className="flex flex-col gap-6 lg:grid lg:grid-cols-[0.7fr_1.3fr] lg:items-end">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--color-muted)]">
                  Back the build
                </p>
                <h2 className="mt-4 text-3xl font-semibold tracking-[-0.06em] text-white sm:text-5xl">
                  Back the tool.
                </h2>
                <p className="mt-4 max-w-sm text-base leading-7 text-[var(--color-secondary)]">
                  Help ship the first honest poker habit coach.
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                {tiers.map((tier) => (
                  <a
                    key={tier.label}
                    href={tier.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="tier-panel rounded-[1.5rem] p-5 transition-transform hover:-translate-y-1"
                  >
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--color-accent)]">
                      {tier.label}
                    </p>
                    <p className="mt-4 text-4xl font-semibold tracking-[-0.05em] text-white">
                      {tier.amount}
                    </p>
                    <p className="mt-3 text-sm leading-6 text-[var(--color-secondary)]">
                      {tier.note}
                    </p>
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
