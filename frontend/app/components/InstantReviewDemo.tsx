"use client";

import type { ChangeEvent, DragEvent } from "react";
import { useEffect, useRef, useState } from "react";

type ReviewResponse = {
  heroName: string | null;
  tournamentName: string;
  fileName: string;
  handsReviewed: number;
  fieldNote: string;
  habits: Array<{
    title: string;
    body: string;
  }>;
  adjustment: {
    title: string;
    body: string;
  };
};

const SAMPLE_TOURNAMENTS = [
  "Daily Heater 25",
  "Midnight Sprint 15",
  "Bounty Builder 32",
  "Late Night Stack 20",
];

const SAMPLE_FIELD_NOTES = [
  "This field leaned limp-heavy and calling-heavy. Weird pressure showed up often, but the patterns stayed readable.",
  "This tournament had more non-standard sizing than usual. The table kept drifting away from theory and into habit.",
  "This field looked chaotic at first, but the same pressure patterns kept repeating once stacks got shorter.",
];

const SAMPLE_HABITS = [
  {
    title: "Preflop passivity",
    body: "You flatted too often before the flop instead of taking the lead in clear pressure spots.",
  },
  {
    title: "Thin value hesitation",
    body: "You checked back value against wide callers when the table was already showing loose behavior.",
  },
  {
    title: "River caution",
    body: "Once pots got bigger, your default leaned toward folding rather than making one last decision.",
  },
  {
    title: "Turn slowdown",
    body: "You lost aggression on later streets and let opponents drive the pace too often.",
  },
  {
    title: "Safe-line bias",
    body: "Against non-standard players, you kept choosing the standard line instead of the more profitable one.",
  },
  {
    title: "Missed isolate spots",
    body: "You passed on a few clean chances to isolate weaker players and keep the hand simpler.",
  },
];

const SAMPLE_ADJUSTMENTS = [
  "Next session, take one extra thin value spot against a player who keeps calling too wide.",
  "Next session, choose one preflop flatting spot and turn it into an aggressive lead instead.",
  "Next session, save one river fold and review whether it was real pressure or just discomfort.",
  "Next session, attack one obvious weak limp instead of letting the hand drift multi-way.",
];

function pickRandom<T>(items: T[], count = 1): T[] {
  const pool = [...items];
  const picked: T[] = [];

  while (pool.length > 0 && picked.length < count) {
    const index = Math.floor(Math.random() * pool.length);
    picked.push(pool.splice(index, 1)[0]);
  }

  return picked;
}

function createSampleReview(): ReviewResponse {
  return {
    heroName: "Sample player",
    tournamentName: pickRandom(SAMPLE_TOURNAMENTS)[0],
    fileName: "sample-hand-history.txt",
    handsReviewed: 120 + Math.floor(Math.random() * 180),
    fieldNote: pickRandom(SAMPLE_FIELD_NOTES)[0],
    habits: pickRandom(SAMPLE_HABITS, 3),
    adjustment: {
      title: "1% Better poker strategy",
      body: pickRandom(SAMPLE_ADJUSTMENTS)[0],
    },
  };
}

function ReviewSheet({
  review,
  mode,
  onClose,
  onAnotherSample,
}: {
  review: ReviewResponse;
  mode: "sample" | "real";
  onClose: () => void;
  onAnotherSample: () => void;
}) {
  return (
    <div className="sheet-backdrop fixed inset-0 z-50 flex items-end justify-end">
      <button
        type="button"
        aria-label="Close report"
        className="absolute inset-0 cursor-default"
        onClick={onClose}
      />

      <aside className="report-sheet relative z-10 w-full rounded-t-[2rem] p-5 sm:max-w-[560px] sm:rounded-none sm:rounded-l-[2rem] sm:p-6">
        <div className="mx-auto h-1.5 w-14 rounded-full bg-[rgba(255,255,255,0.16)] sm:hidden" />

        <div className="mt-4 flex items-start justify-between gap-4 border-b border-[var(--color-line)] pb-4 sm:mt-0">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--color-muted)]">
              {mode === "real" ? "Your review" : "Sample report"}
            </p>
            <p className="mt-2 text-2xl font-semibold tracking-[-0.05em] text-white">
              {review.heroName ? `${review.heroName}, here is your pattern read.` : "Here is your pattern read."}
            </p>
            <p className="mt-2 text-sm leading-6 text-[var(--color-secondary)]">
              {review.tournamentName} · {review.handsReviewed} hands reviewed
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-full border border-[var(--color-line)] px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-white transition-colors hover:border-[var(--color-secondary-accent)] hover:bg-[rgba(28,120,255,0.12)]"
          >
            Close
          </button>
        </div>

        <div className="mt-5 space-y-4 overflow-y-auto sm:max-h-[calc(100vh-8rem)]">
          <div className="rounded-[1.5rem] border border-[rgba(28,120,255,0.24)] bg-[rgba(28,120,255,0.08)] p-5">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--color-secondary-accent)]">
              {review.adjustment.title}
            </p>
            <p className="mt-3 text-lg font-semibold text-white">{review.adjustment.body}</p>
          </div>

          <div className="mini-panel rounded-[1.5rem] p-5">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--color-muted)]">
              Table dynamic
            </p>
            <p className="mt-3 text-sm leading-6 text-[var(--color-secondary)]">{review.fieldNote}</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div className="mini-panel rounded-[1.4rem] p-4">
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--color-accent)]">
                Open
              </p>
              <p className="mt-3 text-lg font-semibold text-white">3 your patterns</p>
              <p className="mt-3 text-sm leading-6 text-[var(--color-secondary)]">
                One tournament. Three one-line pattern reasons.
              </p>
            </div>

            <div className="mini-panel rounded-[1.4rem] p-4">
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--color-accent)]">
                3-Bet
              </p>
              <p className="mt-3 text-lg font-semibold text-white">More quantified</p>
              <p className="mt-3 text-sm leading-6 text-[var(--color-secondary)]">
                Three patterns, deeper reasons, and limited quantified reads.
              </p>
            </div>

            <div className="mini-panel rounded-[1.4rem] p-4">
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--color-accent)]">
                All-In
              </p>
              <p className="mt-3 text-lg font-semibold text-white">Track over time</p>
              <p className="mt-3 text-sm leading-6 text-[var(--color-secondary)]">
                Higher limits and continuous pattern tracking across sessions.
              </p>
            </div>
          </div>

          {mode === "sample" && (
            <button
              type="button"
              onClick={onAnotherSample}
              className="w-full rounded-full border border-[var(--color-line)] px-5 py-3 text-sm font-semibold text-white transition-colors hover:border-[var(--color-secondary-accent)] hover:bg-[rgba(28,120,255,0.12)]"
            >
              Another sample
            </button>
          )}
        </div>
      </aside>
    </div>
  );
}

export function InstantReviewDemo() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [review, setReview] = useState<ReviewResponse | null>(null);
  const [sheetMode, setSheetMode] = useState<"sample" | "real" | null>(null);

  useEffect(() => {
    const previous = document.body.style.overflow;

    if (sheetMode) {
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.body.style.overflow = previous;
    };
  }, [sheetMode]);

  async function uploadFile(file: File) {
    setIsLoading(true);
    setError(null);
    setFileName(file.name);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/review", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error ?? "Upload failed.");
      }

      setReview(data);
      setSheetMode("real");
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload failed.");
    } finally {
      setIsLoading(false);
    }
  }

  function openSample() {
    setReview(createSampleReview());
    setSheetMode("sample");
    setError(null);
  }

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) {
      void uploadFile(file);
    }
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file) {
      void uploadFile(file);
    }
  }

  return (
    <>
      <div className="review-panel rounded-[2rem] p-5 sm:p-6">
        <div className="flex items-center justify-between border-b border-[var(--color-line)] pb-4">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--color-muted)]">
              Free review
            </p>
            <p className="mt-2 text-2xl font-semibold tracking-[-0.05em] text-white">
              Try one tournament now
            </p>
          </div>
          <div className="rounded-full bg-[rgba(255,154,61,0.14)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--color-accent)]">
            Mobile + web
          </div>
        </div>

        <div
          className={`upload-panel mt-5 rounded-[1.7rem] p-5 ${isDragging ? "upload-panel-active" : ""}`}
          onDragOver={(event) => {
            event.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={onDrop}
        >
          <p className="text-[12px] font-semibold uppercase tracking-[0.14em] text-[var(--color-accent)]">
            Drop .txt
          </p>
          <p className="mt-2 text-lg font-semibold text-white">
            Upload one tournament
          </p>

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="rounded-full bg-[var(--color-accent)] px-5 py-3 text-sm font-semibold text-[#0e1831] transition-transform hover:-translate-y-0.5"
            >
              Choose file
            </button>
            <button
              type="button"
              onClick={openSample}
              className="rounded-full border border-[var(--color-line)] px-5 py-3 text-sm font-semibold text-white transition-colors hover:border-[var(--color-secondary-accent)] hover:bg-[rgba(28,120,255,0.12)]"
            >
              Preview sample
            </button>
          </div>

          <input
            ref={inputRef}
            type="file"
            accept=".txt,text/plain"
            className="hidden"
            onChange={onFileChange}
          />

          {(fileName || isLoading) && (
            <div className="mt-4 rounded-[1.1rem] border border-[var(--color-line)] bg-[rgba(255,255,255,0.03)] px-4 py-4 text-sm text-[var(--color-secondary)]">
              {isLoading ? `Reviewing ${fileName ?? "your file"}...` : `Loaded ${fileName}`}
            </div>
          )}

          {error && (
            <div className="mt-4 rounded-[1.1rem] border border-[rgba(255,154,61,0.28)] bg-[rgba(255,154,61,0.08)] px-4 py-4 text-sm text-[#ffd7b2]">
              {error}
            </div>
          )}
        </div>
      </div>

      {sheetMode && review && (
        <ReviewSheet
          review={review}
          mode={sheetMode}
          onClose={() => setSheetMode(null)}
          onAnotherSample={() => {
            setReview(createSampleReview());
            setSheetMode("sample");
          }}
        />
      )}
    </>
  );
}
