export const QUEUE_VIEWS = ["all", "needs_review", "incomplete", "no_findings"] as const;
export type QueueView = (typeof QUEUE_VIEWS)[number];
export type QueueParams = { view: QueueView; q: string; page: number };
export const QUEUE_PAGE_SIZE = 20;

type SearchInput = URLSearchParams | Record<string, string | string[] | undefined>;

function first(search: SearchInput, key: string): string {
  if (search instanceof URLSearchParams) return search.get(key) ?? "";
  const value = search[key];
  return (Array.isArray(value) ? value[0] : value) ?? "";
}

export function parseQueueParams(search: SearchInput): QueueParams {
  const view = first(search, "view");
  const page = Number(first(search, "page"));
  return {
    view: (QUEUE_VIEWS as readonly string[]).includes(view) ? (view as QueueView) : "all",
    q: first(search, "q").trim().slice(0, 200),
    page: Number.isInteger(page) && page >= 1 ? page : 1,
  };
}

/** Query string without the leading `?`; defaults are omitted so URLs stay short. */
export function queueSearch(params: QueueParams): string {
  const search = new URLSearchParams();
  if (params.view !== "all") search.set("view", params.view);
  if (params.q) search.set("q", params.q);
  if (params.page > 1) search.set("page", String(params.page));
  return search.toString();
}
