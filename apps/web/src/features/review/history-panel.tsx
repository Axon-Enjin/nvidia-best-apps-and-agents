import { History } from "@/components/ui/icons";
import { eventLabel } from "@/features/case/labels";
import type { ReviewEvent } from "@/lib/api-types";

const when = new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });

/** Every recorded event, newest first, with who, when, which revision and why. */
export function HistoryPanel({ events }: { events: ReviewEvent[] }) {
  const ordered = [...events].reverse();
  return (
    <details className="border-t border-rule pt-2">
      <summary className="inline-flex min-h-11 items-center gap-2 py-2 font-semibold">
        <History aria-hidden="true" className="size-4" />
        Review history ({events.length})
      </summary>
      {ordered.length ? (
        <ol aria-label="Review history" className="grid gap-3 py-2">
          {ordered.map((event) => (
            <li key={event.id} className="border-l-2 border-rule pl-3 text-sm">
              <p className="font-semibold">
                {eventLabel(event.action)} <span className="doc-ref font-normal text-ink-muted">{event.action}</span>
              </p>
              <p className="text-ink-muted">
                {event.actor} · {when.format(new Date(event.created_at * 1000))} · revision {event.revision}
              </p>
              {event.payload.reason ? <p className="mt-0.5">{event.payload.reason}</p> : null}
            </li>
          ))}
        </ol>
      ) : (
        <p aria-label="Review history" className="py-2 text-sm text-ink-muted">
          No review events yet.
        </p>
      )}
    </details>
  );
}
