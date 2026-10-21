import { CircleAlert, CircleCheck, Clock, TriangleAlert } from "./icons";

export type Tone = "passed" | "attention" | "blocking" | "neutral";

const TONE_CLASS: Record<Tone, string> = {
  passed: "text-passed",
  attention: "text-attention",
  blocking: "text-blocking",
  neutral: "text-ink-muted",
};

const TONE_ICON = { passed: CircleCheck, attention: TriangleAlert, blocking: CircleAlert, neutral: Clock } as const;

/** Status always carries text; color and icon only reinforce it. */
export function StatusText({ tone, children, className = "" }: { tone: Tone; children: string; className?: string }) {
  const Icon = TONE_ICON[tone];
  return (
    <span className={`inline-flex items-center gap-1.5 font-semibold ${TONE_CLASS[tone]} ${className}`}>
      <Icon aria-hidden="true" className="size-4 shrink-0" strokeWidth={2.25} />
      <span>{children}</span>
    </span>
  );
}
