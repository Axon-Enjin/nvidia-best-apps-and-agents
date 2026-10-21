import type { Metadata } from "next";
import Link from "next/link";

import { Upload } from "@/components/ui/icons";
import { parseQueueParams, QUEUE_PAGE_SIZE, queueSearch, type QueueParams, type QueueView } from "@/features/queue/queue-params";
import { QueueSearch } from "@/features/queue/queue-search";
import { QueueTable } from "@/features/queue/queue-table";
import type { QueuePage, QueueStats } from "@/lib/api-types";
import { backendGet } from "@/lib/backend";

export const metadata: Metadata = { title: "Claims" };

const FILTERS: { view: QueueView; label: string; count: keyof QueueStats }[] = [
  { view: "all", label: "All", count: "all" },
  { view: "needs_review", label: "Needs review", count: "needs_review" },
  { view: "incomplete", label: "Checks unavailable", count: "incomplete" },
  { view: "no_findings", label: "Completed", count: "no_findings" },
];

function href(params: QueueParams): string {
  const search = queueSearch(params);
  return search ? `/claims?${search}` : "/claims";
}

export default async function ClaimsPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const params = parseQueueParams(await searchParams);
  const query = new URLSearchParams({
    view: params.view,
    q: params.q,
    offset: String((params.page - 1) * QUEUE_PAGE_SIZE),
    limit: String(QUEUE_PAGE_SIZE),
  });
  const [page, stats] = await Promise.all([
    backendGet<QueuePage>(`/api/claims?${query}`),
    backendGet<QueueStats>("/api/stats"),
  ]);
  const first = page.total ? page.offset + 1 : 0;
  const last = page.offset + page.items.length;

  return (
    <>
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink pb-4">
        <div>
          <p className="eyebrow">Review queue</p>
          <h1 className="text-[1.75rem]">Claims</h1>
        </div>
        <Link href="/claims/new" className="btn btn-primary no-underline">
          <Upload aria-hidden="true" className="size-4" />
          Import a claim
        </Link>
      </div>

      <div className="mt-6 flex flex-wrap items-end justify-between gap-x-8 gap-y-4">
        <nav aria-label="Queue filter">
          <ul className="flex flex-wrap gap-x-1 gap-y-2">
            {FILTERS.map((filter) => {
              const active = filter.view === params.view;
              return (
                <li key={filter.view}>
                  <Link
                    href={href({ ...params, view: filter.view, page: 1 })}
                    aria-current={active ? "page" : undefined}
                    className={`inline-flex min-h-11 items-center gap-2 border-b-2 px-3 font-semibold no-underline transition-colors ${
                      active ? "border-forest text-ink" : "border-transparent text-ink-muted hover:border-rule hover:text-ink"
                    }`}
                  >
                    {filter.label}
                    {/* Totals ignore the search, so they are shown only when no search narrows the list. */}
                    {params.q ? null : (
                      <span className="rounded-full bg-surface px-2 text-sm font-normal text-ink-muted ring-1 ring-rule-faint">
                        {stats[filter.count]}
                      </span>
                    )}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
        <QueueSearch params={params} />
      </div>

      <QueueTable items={page.items} query={queueSearch(params)} />

      {page.total > QUEUE_PAGE_SIZE ? (
        <nav aria-label="Pages" className="mt-4 flex flex-wrap items-center gap-4 text-sm">
          <p className="text-ink-muted">
            Showing {first}–{last} of {page.total}
          </p>
          {params.page > 1 ? (
            <Link href={href({ ...params, page: params.page - 1 })} className="link-button">
              Previous page
            </Link>
          ) : null}
          {last < page.total ? (
            <Link href={href({ ...params, page: params.page + 1 })} className="link-button">
              Next page
            </Link>
          ) : null}
        </nav>
      ) : null}
    </>
  );
}
