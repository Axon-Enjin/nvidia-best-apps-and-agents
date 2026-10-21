"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, type FormEvent } from "react";

import { queueSearch, type QueueParams } from "./queue-params";

/** Search replaces the URL (no history entry per keystroke); filters and paging stay links. */
export function QueueSearch({ params }: { params: QueueParams }) {
  const router = useRouter();
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => () => clearTimeout(timer.current), []);

  function go(q: string) {
    const search = queueSearch({ ...params, q: q.trim().slice(0, 200), page: 1 });
    router.replace(search ? `/claims?${search}` : "/claims", { scroll: false });
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearTimeout(timer.current);
    go(String(new FormData(event.currentTarget).get("q") ?? ""));
  }

  return (
    <form role="search" action="/claims" method="get" onSubmit={submit} className="grid w-full gap-1.5 sm:w-80">
      <label htmlFor="queue-search" className="eyebrow">
        Search claims
      </label>
      <input
        id="queue-search"
        name="q"
        type="search"
        className="input"
        defaultValue={params.q}
        maxLength={200}
        placeholder="Claim reference or patient ID"
        autoComplete="off"
        onChange={(event) => {
          const value = event.currentTarget.value;
          clearTimeout(timer.current);
          timer.current = setTimeout(() => go(value), 300);
        }}
      />
      {params.view !== "all" ? <input type="hidden" name="view" value={params.view} /> : null}
    </form>
  );
}
