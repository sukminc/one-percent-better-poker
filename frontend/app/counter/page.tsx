import type { Metadata } from "next";
import HookTracker from "../components/HookTracker";

export const metadata: Metadata = {
  title: "1% Better Counter | onepercentbetter.poker",
  description:
    "Mobile-first poker counter that turns weird live reads into 1% better adjustments.",
};

export default function CounterPage() {
  return <HookTracker />;
}
