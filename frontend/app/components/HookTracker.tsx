"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";

type ActionId = "bet" | "call" | "raise";
type ModeId = "more" | "less";
type PositionId = "utg" | "hj" | "co" | "btn" | "sb" | "bb";
type Stage = "setup" | "counter" | "complete";

type CounterState = {
  stage: Stage;
  action: ActionId | null;
  mode: ModeId | null;
  position: PositionId | null;
  target: number | null;
  count: number;
  goalLocked: boolean;
};

const STORAGE_KEY = "opb-1-better-counter-v7";

const ACTIONS: Array<{ id: ActionId; label: string }> = [
  { id: "bet", label: "Fold" },
  { id: "call", label: "Call" },
  { id: "raise", label: "Raise" },
];

const POSITIONS: Array<{ id: PositionId; label: string }> = [
  { id: "utg", label: "Under the Gun" },
  { id: "hj", label: "Hijack" },
  { id: "co", label: "Cutoff" },
  { id: "btn", label: "Button" },
  { id: "sb", label: "Small Blind" },
  { id: "bb", label: "Big Blind" },
];

const MODES: Array<{ id: ModeId; label: string }> = [
  { id: "more", label: "More" },
  { id: "less", label: "Less" },
];

function getTargetTicks(mode: ModeId | null) {
  return mode === "more" ? [1, 2, 3, 4, 5] : [0, 1, 2, 3, 4, 5];
}

const DEFAULT_STATE: CounterState = {
  stage: "setup",
  action: null,
  mode: null,
  position: null,
  target: null,
  count: 0,
  goalLocked: false,
};

function clampState(value: CounterState): CounterState {
  const mode = MODES.some((item) => item.id === value.mode) ? value.mode : null;
  const rawTarget =
    typeof value.target === "number" && value.target >= 0 && value.target <= 5
      ? value.target
      : null;
  const target =
    mode === "more"
      ? rawTarget === null
        ? null
        : Math.max(1, rawTarget)
      : rawTarget;

  return {
    stage: value.stage === "complete" ? "complete" : value.stage === "counter" ? "counter" : "setup",
    action: ACTIONS.some((item) => item.id === value.action) ? value.action : null,
    mode,
    position: POSITIONS.some((item) => item.id === value.position) ? value.position : null,
    target,
    count: Math.max(0, value.count || 0),
    goalLocked: Boolean(value.goalLocked),
  };
}

function selectedClass(isSelected: boolean) {
  return isSelected
    ? "border-[#1C78FF] bg-[linear-gradient(180deg,rgba(28,120,255,0.24),rgba(16,69,160,0.18))] text-white shadow-[0_18px_34px_rgba(28,120,255,0.18)]"
    : "border-white/10 bg-white/4 text-[#D0C8BA] hover:border-white/20 hover:text-white";
}

function buildSentence(
  action: ActionId | null,
  mode: ModeId | null,
  target: number | null,
  position: PositionId | null
) {
  if (!action || !mode || target === null) {
    return "";
  }

  const actionLabel = ACTIONS.find((item) => item.id === action)?.label.toUpperCase() ?? "RAISE";
  const positionLabel = position ? POSITIONS.find((item) => item.id === position)?.label ?? "" : "";
  const actionPhrase = positionLabel ? `${actionLabel} from ${positionLabel}` : actionLabel;
  if (mode === "less" && target === 0) {
    return `You will keep ${actionPhrase} at 0.`;
  }

  const compareWord = mode === "more" ? "more than" : "less than";
  const unit = target === 1 ? "time" : "times";

  return `You will ${actionPhrase} ${compareWord} ${target} ${unit}.`;
}

function getModesForAction(action: ActionId | null) {
  if (action === "bet") {
    return MODES.filter((mode) => mode.id === "more");
  }

  return MODES;
}

export default function HookTracker() {
  const [state, setState] = useState<CounterState>(DEFAULT_STATE);
  const [hasHydrated, setHasHydrated] = useState(false);
  const [isCelebrating, setIsCelebrating] = useState(false);
  const [celebrationKey, setCelebrationKey] = useState(0);
  const [showPositionOptions, setShowPositionOptions] = useState(false);
  const previousGoalHitRef = useRef(false);

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setState(clampState(JSON.parse(saved) as CounterState));
      }
    } catch {
      window.localStorage.removeItem(STORAGE_KEY);
    } finally {
      setHasHydrated(true);
    }
  }, []);

  useEffect(() => {
    if (!hasHydrated) {
      return;
    }

    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [hasHydrated, state]);

  const sentence = useMemo(
    () => buildSentence(state.action, state.mode, state.target, state.position),
    [state.action, state.mode, state.position, state.target]
  );

  const displayCount = useMemo(() => {
    if (state.target === null) {
      return state.count;
    }

    if (state.mode === "less") {
      return Math.max(state.target - state.count, 0);
    }

    return state.count;
  }, [state.count, state.mode, state.target]);

  const progressPercent = useMemo(() => {
    if (state.target === null) {
      return 0;
    }

    if (state.mode === "less") {
      if (state.target === 0) {
        return state.count === 0 ? 0 : 100;
      }

      return Math.max(0, Math.min((state.count / state.target) * 100, 100));
    }

    if (state.target === 0) {
      return state.count === 0 ? 0 : 100;
    }

    return Math.max(0, Math.min((state.count / state.target) * 100, 100));
  }, [state.count, state.mode, state.target]);

  const goalHit =
    state.target !== null &&
    (state.mode === "less" ? state.count <= state.target : state.count >= state.target);
  const overGoal =
    state.mode === "more" && state.target !== null && state.count > state.target;
  const missedLessGoal =
    state.mode === "less" && state.target !== null && state.count > state.target;
  const cleanZeroSession =
    state.mode === "less" && state.target === 0 && state.count === 0;
  const missedGoal = state.target !== null && !goalHit;
  const liveGoalReached =
    state.target !== null &&
    (state.mode === "more"
      ? state.count >= state.target
      : state.mode === "less"
        ? state.target > 0 && state.count >= state.target
        : false);
  const extraCount =
    state.target !== null
      ? state.mode === "more"
        ? Math.max(state.count - state.target, 0)
        : Math.max(state.target - state.count, 0)
      : 0;
  const progressShellClass = overGoal
    ? "border-[#FF9A3D]/40 bg-[radial-gradient(circle_at_top,_rgba(255,154,61,0.24),_transparent_55%),rgba(255,255,255,0.04)]"
    : missedLessGoal
      ? "border-[#FF8460]/30 bg-[radial-gradient(circle_at_top,_rgba(255,132,96,0.12),_transparent_55%),rgba(255,255,255,0.03)]"
      : liveGoalReached
        ? "border-[#1C78FF]/24 bg-[radial-gradient(circle_at_top,_rgba(28,120,255,0.14),_transparent_55%),rgba(255,255,255,0.03)]"
        : "border-white/10 bg-white/[0.03]";
  const readyToStart =
    state.action !== null && state.mode !== null && state.target !== null;
  const shouldCelebrate =
    (state.mode === "more" && liveGoalReached && !overGoal) ||
    (state.mode === "less" && state.target !== null && state.target > 0 && state.count === state.target);

  useEffect(() => {
    if (!state.goalLocked) {
      previousGoalHitRef.current = false;
      setIsCelebrating(false);
      return;
    }

    if (shouldCelebrate && !previousGoalHitRef.current) {
      previousGoalHitRef.current = true;
      setCelebrationKey((value) => value + 1);
      setIsCelebrating(true);

      const timeout = window.setTimeout(() => {
        setIsCelebrating(false);
      }, 2600);

      return () => window.clearTimeout(timeout);
    }

    previousGoalHitRef.current = shouldCelebrate;
  }, [shouldCelebrate, state.goalLocked]);

  function setAction(action: ActionId) {
    setState((current) => ({
      ...current,
      action,
      mode: action === "bet" && current.mode === "less" ? null : current.mode,
      stage: "setup",
      goalLocked: false,
      count: 0,
    }));
  }

  function setMode(mode: ModeId) {
    if (state.action === "bet" && mode === "less") {
      return;
    }

    setState((current) => ({
      ...current,
      mode,
      target:
        mode === "more"
          ? current.target === null || current.target === 0
            ? 3
            : current.target
          : current.target ?? 3,
      stage: "setup",
      goalLocked: false,
      count: 0,
    }));
  }

  function setTarget(target: number) {
    setState((current) => ({
      ...current,
      target,
      stage: "setup",
      goalLocked: false,
      count: 0,
    }));
  }

  function setPosition(position: PositionId | null) {
    setState((current) => ({
      ...current,
      position: current.position === position ? null : position,
      stage: "setup",
      goalLocked: false,
      count: 0,
    }));
  }

  function startCounting() {
    setState((current) => ({
      ...current,
      stage: "counter",
      goalLocked: true,
      count: 0,
    }));
  }

  function increase() {
    setState((current) => ({
      ...current,
      count: current.count + 1,
    }));
  }

  function finish() {
    setState((current) => ({
      ...current,
      stage: "complete",
    }));
  }

  function startAgain() {
    setState(DEFAULT_STATE);
  }

  const celebrationBits = Array.from({ length: 18 }, (_, index) => ({
    id: `${celebrationKey}-${index}`,
    left: `${8 + ((index * 11) % 84)}%`,
    delay: `${(index % 6) * 0.06}s`,
    duration: `${1.6 + (index % 4) * 0.18}s`,
    color:
      index % 3 === 0 ? "#1C78FF" : index % 3 === 1 ? "#FF9A3D" : "#F7FBFF",
    rotate: `${-28 + (index % 7) * 9}deg`,
  }));
  const nextSessionMessage = overGoal
    ? "Lock the same habit again next session and make it automatic."
    : goalHit
      ? "Repeat this line next session. Repetition turns intent into identity."
      : "Not this session. The rep still counts. Show up again and run it back next session.";
  const progressTone = overGoal
    ? { start: "#FF9A3D", end: "#FFB56E" }
    : missedLessGoal
      ? { start: "#FF6B6B", end: "#FF9A7A" }
      : liveGoalReached
        ? { start: "#1C78FF", end: "#63A6FF" }
        : { start: "#1C78FF", end: "#63A6FF" };
  const progressSweep = Math.max(0, Math.min(progressPercent, 100));
  const ringBackground = `conic-gradient(from 270deg, ${progressTone.start} 0deg, ${progressTone.end} ${(progressSweep / 100) * 360}deg, rgba(255,255,255,0.08) ${(progressSweep / 100) * 360}deg, rgba(255,255,255,0.08) 360deg)`;
  const progressValueLabel = overGoal
    ? `+${extraCount} over`
    : state.mode === "less"
      ? `${displayCount} left`
      : `${state.count} / ${state.target}`;
  const progressSupport = overGoal
    ? "You did more than you asked of yourself."
    : cleanZeroSession
      ? "You kept it at zero all session."
      : liveGoalReached
        ? state.mode === "less"
          ? "You hit the line exactly."
          : "The line is cleared."
        : missedLessGoal
          ? "Pull it back and finish cleaner next session."
          : state.mode === "less"
            ? "Count down cleanly."
            : "Keep tapping. Small reps compound.";

  return (
    <main className="min-h-[100dvh] bg-[radial-gradient(circle_at_top_left,_rgba(28,120,255,0.18),_transparent_26%),radial-gradient(circle_at_top_right,_rgba(255,154,61,0.16),_transparent_22%),linear-gradient(180deg,_#122344_0%,_#09111F_72%)] px-4 text-[#F7FBFF] sm:px-6" style={{ paddingTop: "max(1rem, env(safe-area-inset-top))", paddingBottom: "max(1.25rem, env(safe-area-inset-bottom))" }}>
      <div
        className="mx-auto flex w-full max-w-md flex-col gap-5"
        style={{
          minHeight:
            "calc(100dvh - max(1rem, env(safe-area-inset-top)) - max(1.25rem, env(safe-area-inset-bottom)))",
        }}
      >
        <header className="rounded-[30px] border border-white/10 bg-[linear-gradient(180deg,rgba(13,24,48,0.96),rgba(9,17,31,0.98))] p-5 shadow-[0_24px_80px_rgba(4,10,24,0.34)] backdrop-blur">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-[10px] uppercase tracking-[0.32em] text-[#88A0C4]">
                by onepercentbetter.poker
              </p>
              <h1 className="mt-2 text-[2rem] font-semibold tracking-tight text-white">
                1% Better Counter
              </h1>
            </div>
            <Link
              href="/"
              className="rounded-full border border-white/12 px-3 py-1.5 text-xs text-[#D0D8E6] transition hover:border-[#1C78FF]/50 hover:text-white"
            >
              Home
            </Link>
          </div>
        </header>

        {state.stage !== "complete" ? (
          <section className="relative overflow-hidden rounded-[30px] border border-white/10 bg-[linear-gradient(180deg,rgba(13,24,48,0.98),rgba(9,16,30,0.99))] p-5 shadow-[0_20px_60px_rgba(4,10,24,0.34)]">
            {isCelebrating ? (
              <div
                key={celebrationKey}
                className="pointer-events-none absolute inset-0 overflow-hidden"
                aria-hidden="true"
              >
                <div className="celebration-flash absolute inset-x-[18%] top-8 h-28 rounded-full bg-[radial-gradient(circle,_rgba(255,154,61,0.28),_rgba(255,154,61,0.05)_55%,_transparent_70%)] blur-2xl" />
                <div className="celebration-ring absolute left-1/2 top-20 h-24 w-24 -translate-x-1/2 rounded-full border border-[#FF9A3D]/60" />
                <div className="celebration-ring celebration-ring-delay absolute left-1/2 top-16 h-36 w-36 -translate-x-1/2 rounded-full border border-[#1C78FF]/45" />
                {celebrationBits.map((bit) => (
                  <span
                    key={bit.id}
                    className="celebration-bit absolute top-14 h-4 w-2 rounded-full"
                    style={{
                      left: bit.left,
                      animationDelay: bit.delay,
                      animationDuration: bit.duration,
                      background: bit.color,
                      transform: `rotate(${bit.rotate})`,
                    }}
                  />
                ))}
              </div>
            ) : null}
            {!state.goalLocked ? (
              <>
                <div className="rounded-[24px] border border-white/10 bg-black/20 p-4">
                  <p className="text-[10px] uppercase tracking-[0.24em] text-[#8E877C]">
                    Session
                  </p>
                  <p className="mt-3 text-xl font-semibold leading-8 text-white">
                    What do you want to make 1% better this session?
                  </p>
                </div>

                <div className="mt-5 rounded-[26px] border border-white/10 bg-black/16 p-4">
                  <p className="mb-3 text-[10px] uppercase tracking-[0.24em] text-[#8E877C]">
                    Action
                  </p>
                  <div className="grid grid-cols-3 gap-2">
                    {ACTIONS.map((action) => (
                      <button
                        key={action.id}
                        type="button"
                        onClick={() => setAction(action.id)}
                        className={`rounded-[18px] border px-4 py-4 text-sm transition ${selectedClass(
                          state.action === action.id
                        )}`}
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                </div>

                {state.action ? (
                  <div className="mt-5 rounded-[26px] border border-[#1C78FF]/18 bg-[radial-gradient(circle_at_top,_rgba(28,120,255,0.14),_transparent_58%),linear-gradient(180deg,_rgba(255,255,255,0.03),_rgba(255,255,255,0.02))] p-4 transition-all duration-300">
                    <p className="text-[10px] uppercase tracking-[0.24em] text-[#88A0C4]">
                      Goal
                    </p>
                    <div className="mt-4 space-y-4">
                      <div className="grid grid-cols-2 gap-2">
                        {getModesForAction(state.action).map((mode) => (
                          <button
                            key={mode.id}
                            type="button"
                            onClick={() => setMode(mode.id)}
                            className={`rounded-[18px] border px-4 py-4 text-sm transition ${selectedClass(
                              state.mode === mode.id
                            )}`}
                          >
                            {mode.label}
                          </button>
                        ))}
                      </div>

                      {state.mode ? (
                        <div className="relative overflow-hidden rounded-[24px] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.06),rgba(255,255,255,0.02))] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_18px_36px_rgba(0,0,0,0.22)] backdrop-blur-xl">
                          <div className="pointer-events-none absolute inset-x-6 top-0 h-14 rounded-full bg-[radial-gradient(circle,_rgba(255,255,255,0.12),_transparent_72%)] blur-xl" />
                          <div className="relative flex items-end justify-between gap-4">
                            <div>
                              <p className="text-[10px] uppercase tracking-[0.24em] text-[#8E877C]">
                                Target
                              </p>
                              <p className="mt-2 text-[4.25rem] font-semibold leading-[0.92] tracking-[-0.05em] text-white">
                                {state.target ?? 3}
                              </p>
                            </div>
                            <p className="pb-2 text-sm font-medium text-[#D7D4CD]">
                              {state.mode === "more" ? "Push higher" : "Stay lower"}
                            </p>
                          </div>
                          <input
                            aria-label="Goal target"
                            type="range"
                            min={state.mode === "more" ? "1" : "0"}
                            max="5"
                            step="1"
                            value={state.target ?? 3}
                            onChange={(event) => {
                              setTarget(Number(event.target.value));
                            }}
                            className="goal-slider mt-5 w-full"
                          />
                          <div
                            className={`mt-3 grid gap-1 px-0.5 text-xs font-medium text-[#8E877C] ${
                              state.mode === "more" ? "grid-cols-5" : "grid-cols-6"
                            }`}
                          >
                            {getTargetTicks(state.mode).map((tick) => (
                              <span key={tick} className="text-center">
                                {tick}
                              </span>
                            ))}
                          </div>
                        </div>
                      ) : null}

                      <div className="rounded-[22px] border border-white/8 bg-black/14 p-3">
                        <button
                          type="button"
                          onClick={() => setShowPositionOptions((current) => !current)}
                          className="flex w-full items-center justify-between text-left"
                        >
                          <p className="text-[10px] uppercase tracking-[0.24em] text-[#8E877C]">
                            Position
                          </p>
                          <span className="text-xs font-medium text-[#88A0C4]">
                            {showPositionOptions ? "Hide" : "Add"}
                          </span>
                        </button>

                        {showPositionOptions ? (
                          <div className="mt-3 grid grid-cols-2 gap-2">
                            {POSITIONS.map((position) => (
                              <button
                                key={position.id}
                                type="button"
                                onClick={() => setPosition(position.id)}
                                className={`rounded-[18px] border px-3 py-4 text-base leading-5 transition ${selectedClass(
                                  state.position === position.id
                                )}`}
                              >
                                {position.label}
                              </button>
                            ))}
                          </div>
                        ) : null}

                        <div className="mt-3 border-t border-white/8 pt-3">
                          <div className="flex items-center justify-between gap-3">
                            <p className="text-[10px] uppercase tracking-[0.24em] text-[#8E877C]">
                              Time Structure
                            </p>
                            <span className="rounded-full border border-[#FF9A3D]/30 bg-[rgba(255,154,61,0.1)] px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.18em] text-[#FFD7AF]">
                              In progress
                            </span>
                          </div>
                        </div>
                      </div>

                      {readyToStart ? (
                        <div className="rounded-[22px] border border-[#1C78FF]/18 bg-black/18 p-4">
                          <p className="text-sm leading-6 text-[#F7FBFF]">{sentence}</p>
                          <button
                            type="button"
                            onClick={startCounting}
                            className="mt-4 w-full rounded-[18px] bg-[#1C78FF] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#3A8CFF]"
                          >
                            Start counting
                          </button>
                        </div>
                      ) : null}
                    </div>
                  </div>
                ) : null}
              </>
            ) : (
              <>
                <div className="rounded-[24px] border border-[#1C78FF]/16 bg-[radial-gradient(circle_at_top,_rgba(28,120,255,0.14),_transparent_55%),linear-gradient(180deg,_rgba(255,255,255,0.03),_rgba(255,255,255,0.02))] p-4 transition-all duration-500">
                  <p className="text-[10px] uppercase tracking-[0.24em] text-[#88A0C4]">
                    Session
                  </p>
                  <p className="mt-3 text-lg font-semibold leading-7 text-white">
                    {sentence}
                  </p>
                </div>

                <div className={`mt-5 rounded-[32px] border p-5 transition-all duration-500 ${progressShellClass}`}>
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-[10px] uppercase tracking-[0.24em] text-[#8E877C]">
                        Goal
                      </p>
                      <p className="mt-2 text-3xl font-semibold text-white">{state.target}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] uppercase tracking-[0.24em] text-[#8E877C]">
                        Progress
                      </p>
                      <p className="mt-2 text-3xl font-semibold text-white">{progressValueLabel}</p>
                    </div>
                  </div>

                  <div className="mt-6 flex justify-center">
                    <button
                      type="button"
                      onClick={increase}
                      className="relative flex aspect-square w-full max-w-[20rem] items-center justify-center rounded-full p-[18px] shadow-[0_40px_90px_rgba(0,0,0,0.42)] transition active:scale-[0.985]"
                      style={{ background: ringBackground }}
                      aria-label="Tap to count"
                    >
                      <span className="pointer-events-none absolute inset-[18px] rounded-full bg-black/40 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]" />
                      {overGoal ? (
                        <span className="pointer-events-none absolute inset-[10px] rounded-full bg-[radial-gradient(circle,_rgba(255,154,61,0.16),_transparent_62%)] blur-xl" />
                      ) : null}
                      <div className="relative flex h-full w-full items-center justify-center rounded-full border border-white/8 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.08),_rgba(255,255,255,0.02)_42%,_rgba(11,11,16,0.92)_70%)] text-center">
                        <p className="text-[7.5rem] font-semibold leading-none tracking-[-0.08em] text-white">
                          {displayCount}
                        </p>
                      </div>
                    </button>
                  </div>

                  <div className="mt-5 flex items-center justify-between gap-3 text-xs text-[#E2DBCE]">
                    {overGoal ? (
                      <span className="rounded-full border border-[#FF9A3D]/30 bg-[rgba(255,154,61,0.1)] px-2.5 py-1 font-medium uppercase tracking-[0.18em] text-[#FFD7AF]">
                        Momentum
                      </span>
                    ) : (
                      <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 font-medium uppercase tracking-[0.18em] text-[#D0D8E6]">
                        Session
                      </span>
                    )}
                    <span>{progressValueLabel}</span>
                  </div>
                  <div className="mt-3 text-sm text-[#A9A193]">{progressSupport}</div>
                </div>

                <div className="mt-6">
                  <button
                    type="button"
                    onClick={finish}
                    className="w-full rounded-[22px] border border-white/10 bg-white/4 px-4 py-3 text-sm text-white transition hover:border-white/20"
                  >
                    Finish
                  </button>
                </div>
              </>
            )}
          </section>
        ) : null}

        {state.stage === "complete" ? (
          <section className="relative overflow-hidden rounded-[30px] border border-white/10 bg-[linear-gradient(180deg,rgba(13,24,48,0.98),rgba(9,16,30,0.99))] p-5 shadow-[0_20px_60px_rgba(4,10,24,0.34)]">
            {shouldCelebrate ? (
              <div
                key={`complete-${celebrationKey}`}
                className="pointer-events-none absolute inset-0 overflow-hidden"
                aria-hidden="true"
              >
                <div className="celebration-flash absolute inset-x-[12%] top-8 h-36 rounded-full bg-[radial-gradient(circle,_rgba(255,154,61,0.24),_rgba(255,154,61,0.05)_55%,_transparent_70%)] blur-2xl" />
                <div className="celebration-ring absolute left-1/2 top-16 h-32 w-32 -translate-x-1/2 rounded-full border border-[#FF9A3D]/60" />
                <div className="celebration-ring celebration-ring-delay absolute left-1/2 top-12 h-44 w-44 -translate-x-1/2 rounded-full border border-[#1C78FF]/45" />
                {celebrationBits.map((bit) => (
                  <span
                    key={`complete-${bit.id}`}
                    className="celebration-bit absolute top-12 h-4 w-2 rounded-full"
                    style={{
                      left: bit.left,
                      animationDelay: bit.delay,
                      animationDuration: bit.duration,
                      background: bit.color,
                      transform: `rotate(${bit.rotate})`,
                    }}
                  />
                ))}
              </div>
            ) : null}
            <h2 className="text-2xl font-semibold text-white">
              {overGoal
                ? "Goal crushed."
                : cleanZeroSession
                  ? "Perfect clean sheet."
                  : goalHit
                    ? "Goal hit."
                    : "Good rep."}
            </h2>
            <p className="mt-3 text-sm leading-6 text-[#D6CFC2]">{sentence}</p>

            <div className={`mt-5 rounded-[26px] border p-4 ${progressShellClass}`}>
              <p className="text-3xl font-semibold text-white">
                {overGoal
                  ? `${state.count} / ${state.target}`
                  : state.mode === "less"
                    ? `${displayCount} left`
                    : `${state.count} / ${state.target}`}
              </p>
              <p className="mt-3 text-base font-medium leading-7 text-[#FFF7EA]">
                {overGoal
                  ? "You went past the line. That is a real 1% session."
                  : cleanZeroSession
                    ? "Zero all the way through. Strong discipline."
                  : goalHit
                    ? "You kept the promise and hit the line."
                    : "You showed up, tracked it, and gave yourself a real rep."}
              </p>
              <p className="mt-2 text-sm leading-6 text-[#D9D1C4]">
                {overGoal
                  ? `You finished ${extraCount} above your goal. Let that momentum stick.`
                  : cleanZeroSession
                    ? "Holding the number at zero still counts as a win. That control matters."
                  : goalHit
                    ? "That is how small intent turns into a better habit."
                    : "Missing the line is not the point. Logging the attempt is how the habit starts to change."}
              </p>
            </div>

            <div className={`mt-4 rounded-[26px] border p-4 ${missedGoal ? "border-[#1C78FF]/18 bg-[radial-gradient(circle_at_top,_rgba(28,120,255,0.12),_transparent_58%),rgba(255,255,255,0.02)]" : "border-white/10 bg-black/18"}`}>
              <p className="text-sm leading-6 text-[#F3EEE6]">
                {missedGoal
                  ? nextSessionMessage
                  : "Upload GGPoker hands to see what you repeat without noticing."}
              </p>
            </div>

            <div className="mt-5 flex flex-col gap-3">
              <button
                type="button"
                onClick={startAgain}
                className="w-full rounded-[22px] bg-[#1C78FF] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#3A8CFF]"
              >
                {missedGoal ? "Try next session" : "Run next session"}
              </button>
              <Link
                href="/"
                className="w-full rounded-[22px] border border-white/10 bg-white/4 px-4 py-3 text-center text-sm text-white transition hover:border-white/20"
              >
                Learn More
              </Link>
            </div>
          </section>
        ) : null}
      </div>
      <style jsx>{`
        .goal-slider {
          -webkit-appearance: none;
          appearance: none;
          height: 32px;
          background: transparent;
        }

        .goal-slider:focus {
          outline: none;
        }

        .goal-slider::-webkit-slider-runnable-track {
          height: 8px;
          border-radius: 999px;
          background: linear-gradient(180deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.06));
          box-shadow:
            inset 0 1px 1px rgba(255, 255, 255, 0.1),
            inset 0 -1px 1px rgba(0, 0, 0, 0.34);
        }

        .goal-slider::-moz-range-track {
          height: 8px;
          border: 0;
          border-radius: 999px;
          background: linear-gradient(180deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.06));
          box-shadow:
            inset 0 1px 1px rgba(255, 255, 255, 0.1),
            inset 0 -1px 1px rgba(0, 0, 0, 0.34);
        }

        .goal-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          margin-top: -8px;
          height: 24px;
          width: 24px;
          border-radius: 999px;
          border: 0;
          background:
            radial-gradient(circle at 35% 35%, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.72) 58%, rgba(214, 228, 255, 0.82) 100%);
          box-shadow:
            0 10px 24px rgba(0, 0, 0, 0.32),
            0 0 0 1px rgba(255, 255, 255, 0.36),
            inset 0 1px 1px rgba(255, 255, 255, 0.7);
        }

        .goal-slider::-moz-range-thumb {
          height: 24px;
          width: 24px;
          border-radius: 999px;
          border: 0;
          background:
            radial-gradient(circle at 35% 35%, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.72) 58%, rgba(214, 228, 255, 0.82) 100%);
          box-shadow:
            0 10px 24px rgba(0, 0, 0, 0.32),
            0 0 0 1px rgba(255, 255, 255, 0.36),
            inset 0 1px 1px rgba(255, 255, 255, 0.7);
        }

        .celebration-bit {
          opacity: 0;
          animation-name: confettiBurst;
          animation-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
          animation-fill-mode: forwards;
        }

        .celebration-ring {
          opacity: 0;
          animation: ringBurst 1.4s ease-out forwards;
        }

        .celebration-ring-delay {
          animation-delay: 0.12s;
        }

        .celebration-flash {
          opacity: 0;
          animation: flashBurst 1.3s ease-out forwards;
        }

        @keyframes confettiBurst {
          0% {
            opacity: 0;
            transform: translate3d(0, 0, 0) scale(0.7);
          }
          10% {
            opacity: 1;
          }
          100% {
            opacity: 0;
            transform: translate3d(0, 230px, 0) rotate(220deg) scale(1);
          }
        }

        @keyframes ringBurst {
          0% {
            opacity: 0.7;
            transform: translateX(-50%) scale(0.2);
          }
          100% {
            opacity: 0;
            transform: translateX(-50%) scale(1.6);
          }
        }

        @keyframes flashBurst {
          0% {
            opacity: 0;
            transform: scale(0.75);
          }
          15% {
            opacity: 1;
          }
          100% {
            opacity: 0;
            transform: scale(1.2);
          }
        }
      `}</style>
    </main>
  );
}
