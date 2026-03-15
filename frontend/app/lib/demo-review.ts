type Street = "preflop" | "flop" | "turn" | "river";
type Action = "fold" | "check" | "call" | "raise" | "bet";

type ActionCounts = Record<Street, Record<Action, number>>;

export type DemoReview = {
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

const STREETS: Street[] = ["preflop", "flop", "turn", "river"];
const ACTIONS: Action[] = ["fold", "check", "call", "raise", "bet"];

const STREET_MARKER_RE =
  /\*\*\* (HOLE CARDS|FLOP|TURN|RIVER|SHOWDOWN|SHOW DOWN|SUMMARY) \*\*\*/;
const ACTION_LINE_RE =
  /^(\S+): (folds|checks|calls|raises|bets)(?: ([\d,$.]+))?(?: to ([\d,$.]+))?/;
const HERO_RE = /Dealt to (\S+) \[/;

function emptyCounts(): ActionCounts {
  return {
    preflop: { fold: 0, check: 0, call: 0, raise: 0, bet: 0 },
    flop: { fold: 0, check: 0, call: 0, raise: 0, bet: 0 },
    turn: { fold: 0, check: 0, call: 0, raise: 0, bet: 0 },
    river: { fold: 0, check: 0, call: 0, raise: 0, bet: 0 },
  };
}

function splitHands(raw: string): string[] {
  return raw
    .split(/(?=Poker Hand #)/)
    .map((block) => block.trim())
    .filter((block) => block.startsWith("Poker Hand #"));
}

function inferHeroName(raw: string): string | null {
  const match = raw.match(HERO_RE);
  return match?.[1] ?? null;
}

function parseTournamentName(fileName: string): string {
  const stem = fileName.replace(/\.txt$/i, "");
  const parts = stem.split(" - ");
  return parts[1] ?? parts[0] ?? "Uploaded tournament";
}

function toAction(raw: string): Action {
  if (raw === "folds") return "fold";
  if (raw === "checks") return "check";
  if (raw === "calls") return "call";
  if (raw === "raises") return "raise";
  return "bet";
}

function parseCounts(raw: string, heroName: string | null) {
  const hands = splitHands(raw);
  const counts = emptyCounts();
  const streetSeen = { flop: 0, turn: 0, river: 0 };
  let villainAllIns = 0;
  let villainRaises = 0;
  let villainCalls = 0;

  for (const hand of hands) {
    const lines = hand.split(/\r?\n/);
    let street: Street = "preflop";

    if (hand.includes("*** FLOP ***")) streetSeen.flop += 1;
    if (hand.includes("*** TURN ***")) streetSeen.turn += 1;
    if (hand.includes("*** RIVER ***")) streetSeen.river += 1;

    for (const line of lines) {
      const marker = line.match(STREET_MARKER_RE);
      if (marker) {
        if (marker[1] === "FLOP") street = "flop";
        if (marker[1] === "TURN") street = "turn";
        if (marker[1] === "RIVER") street = "river";
        continue;
      }

      const actionMatch = line.match(ACTION_LINE_RE);
      if (!actionMatch) {
        continue;
      }

      const [, actor, rawAction] = actionMatch;
      const action = toAction(rawAction);

      if (heroName && actor === heroName) {
        counts[street][action] += 1;
      } else {
        if (/all-?in/i.test(line)) villainAllIns += 1;
        if (action === "raise") villainRaises += 1;
        if (action === "call") villainCalls += 1;
      }
    }
  }

  return { hands, counts, streetSeen, villainAllIns, villainRaises, villainCalls };
}

type Candidate = {
  score: number;
  title: string;
  body: string;
  adjustment: string;
};

function buildCandidates(
  handsReviewed: number,
  counts: ActionCounts,
  streetSeen: { flop: number; turn: number; river: number },
): Candidate[] {
  const preflopLead = counts.preflop.raise;
  const preflopCall = counts.preflop.call;
  const preflopFold = counts.preflop.fold;
  const flopPassive = counts.flop.check + counts.flop.call;
  const flopAggro = counts.flop.bet + counts.flop.raise;
  const turnPassive = counts.turn.check + counts.turn.call;
  const turnAggro = counts.turn.bet + counts.turn.raise;
  const riverFold = counts.river.fold;
  const riverContinue = counts.river.call + counts.river.raise + counts.river.bet;

  const candidates: Candidate[] = [];

  if (preflopCall >= Math.max(3, preflopLead + 2)) {
    candidates.push({
      score: preflopCall - preflopLead,
      title: "Preflop passivity",
      body: `You called ${preflopCall} times preflop and only took the lead ${preflopLead} times. Your default line leaned passive before the flop.`,
      adjustment: "Pick one spot next session where you raise instead of flatting before the flop.",
    });
  }

  if (preflopFold >= Math.max(4, Math.round(handsReviewed * 0.38))) {
    candidates.push({
      score: preflopFold,
      title: "Too many early give-ups",
      body: `You folded preflop ${preflopFold} times in this tournament. The sample suggests you gave up a lot of entry points before hands developed.`,
      adjustment: "Review one preflop fold before your next session and ask whether it was fear or discipline.",
    });
  }

  if (flopPassive >= Math.max(3, flopAggro + 2) && streetSeen.flop > 0) {
    candidates.push({
      score: flopPassive - flopAggro,
      title: "Passive flop follow-through",
      body: `After seeing flops, you checked or called ${flopPassive} times and bet or raised ${flopAggro} times. You often let the hand stay on their terms.`,
      adjustment: "Take one extra stab on a flop next session when the spot is clearly drifting passive.",
    });
  }

  if (turnPassive >= Math.max(2, turnAggro + 2) && streetSeen.turn > 0) {
    candidates.push({
      score: turnPassive - turnAggro,
      title: "Turn pressure dropped",
      body: `By the turn, your aggression slowed down. You checked or called ${turnPassive} times but only pushed the action ${turnAggro} times.`,
      adjustment: "Before your next session, flag one turn spot where you can keep pressure instead of auto-checking.",
    });
  }

  if (riverFold >= Math.max(2, riverContinue + 1) && streetSeen.river > 0) {
    candidates.push({
      score: riverFold,
      title: "River caution",
      body: `You folded ${riverFold} river spots in this sample. Once pots got large, your default reaction leaned toward exit over decision.`,
      adjustment: "Save one river fold next session and review whether the pressure was real or just uncomfortable.",
    });
  }

  if (candidates.length === 0) {
    candidates.push({
      score: 1,
      title: "Baseline pattern forming",
      body: "This tournament gave enough signal to start a pattern profile, but the strongest leak is not obvious yet.",
      adjustment: "Upload one more clean tournament next session so the pattern read gets sharper.",
    });
  }

  if (candidates.length < 3) {
    const fallbacks: Candidate[] = [
      {
        score: 0,
        title: "Rhythm over results",
        body: "The first review is more about repeated behavior than finish position. Your value comes from pattern repetition, not one outcome.",
        adjustment: "Keep the same upload habit next session so the review gets more honest.",
      },
      {
        score: 0,
        title: "Reviewable sample",
        body: "This tournament already has enough actions to start a real habit log. That is the right place to begin.",
        adjustment: "Bring one more tournament with a similar format to compare the same habits.",
      },
    ];

    for (const fallback of fallbacks) {
      if (candidates.length >= 3) break;
      candidates.push(fallback);
    }
  }

  return candidates.sort((a, b) => b.score - a.score).slice(0, 3);
}

function buildFieldNote(
  villainAllIns: number,
  villainRaises: number,
  villainCalls: number,
  handsReviewed: number,
) {
  if (villainAllIns >= 3) {
    return `This field showed jam-heavy pressure. We caught ${villainAllIns} all-in actions from opponents across ${handsReviewed} hands.`;
  }

  if (villainCalls > villainRaises && villainCalls >= 4) {
    return `This field leaned calling-heavy. Opponents called ${villainCalls} times versus ${villainRaises} raises in tracked actions.`;
  }

  return `This first sample is enough to start your habit log. More tournaments will make the pattern read sharper.`;
}

export function createDemoReview(input: {
  rawText: string;
  fileName: string;
}): DemoReview {
  const heroName = inferHeroName(input.rawText);
  const tournamentName = parseTournamentName(input.fileName);
  const { hands, counts, streetSeen, villainAllIns, villainRaises, villainCalls } =
    parseCounts(input.rawText, heroName);
  const handsReviewed = hands.length;

  if (handsReviewed === 0) {
    throw new Error("No valid GGPoker hands found in this file.");
  }

  const candidates = buildCandidates(handsReviewed, counts, streetSeen);
  const fieldNote = buildFieldNote(villainAllIns, villainRaises, villainCalls, handsReviewed);

  return {
    heroName,
    tournamentName,
    fileName: input.fileName,
    handsReviewed,
    fieldNote,
    habits: candidates.map(({ title, body }) => ({ title, body })),
    adjustment: {
      title: "1% Better poker strategy",
      body: candidates[0]?.adjustment ?? "Upload another tournament and keep building the pattern log.",
    },
  };
}
