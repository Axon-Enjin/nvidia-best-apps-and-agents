"use client";

import { StatusText, type Tone } from "@/components/ui/status-text";
import { checkLabel, checkSeverity, checkStatusText } from "@/features/case/labels";
import type { Check } from "@/lib/api-types";

export function issueStatus(check: Check, openTask: boolean): { tone: Tone; text: string } {
  if (check.status === "passed" && openTask) return { tone: "attention", text: "Correction to resolve" };
  return { tone: checkSeverity(check), text: checkStatusText(check) };
}

function IssueButton({ check, openTask, selected, onSelect }: { check: Check; openTask: boolean; selected: boolean; onSelect: (id: string) => void }) {
  const status = issueStatus(check, openTask);
  return (
    <button
      type="button"
      aria-current={selected ? "true" : undefined}
      onClick={() => onSelect(check.id)}
      className={`grid w-full gap-1 border-l-[3px] px-3 py-3 text-left transition-[background-color,border-color] duration-150 ${
        selected ? "border-teal bg-surface" : "border-transparent hover:bg-teal-tint"
      }`}
    >
      <span className="font-semibold leading-snug">{checkLabel(check.id)}</span>
      <span className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm">
        <span className="doc-ref text-ink-muted">{check.id}</span>
        <StatusText tone={status.tone}>{status.text}</StatusText>
      </span>
    </button>
  );
}

/** Unresolved issues (and open corrections) first; passed checks stay one click away, with their evidence. */
export function IssueList({
  checks,
  openTasks,
  selected,
  onSelect,
}: {
  checks: Check[];
  openTasks: ReadonlySet<string>;
  selected: string | null;
  onSelect: (id: string) => void;
}) {
  const actionable = checks.filter((check) => check.id !== "P10");
  const open = actionable.filter((check) => check.status !== "passed" || openTasks.has(check.id));
  const passed = actionable.filter((check) => !open.includes(check));
  return (
    <div className="grid gap-4">
      <div>
        <h2 className="border-t-2 border-ink pt-3 text-lg">Needs attention ({open.length})</h2>
        {open.length ? (
          <ul aria-label="Issues needing attention" className="mt-2 divide-y divide-rule-faint border-y border-rule-faint">
            {open.map((check) => (
              <li key={check.id}>
                <IssueButton check={check} openTask={openTasks.has(check.id)} selected={check.id === selected} onSelect={onSelect} />
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-2 text-ink-muted">Every check passed for this version.</p>
        )}
      </div>
      <details className="border-t border-rule pt-2" open={passed.some((check) => check.id === selected) || undefined}>
        <summary className="min-h-11 py-2 font-semibold">Passed checks ({passed.length})</summary>
        <ul aria-label="Passed checks" className="divide-y divide-rule-faint">
          {passed.map((check) => (
            <li key={check.id}>
              <IssueButton check={check} openTask={false} selected={check.id === selected} onSelect={onSelect} />
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}
