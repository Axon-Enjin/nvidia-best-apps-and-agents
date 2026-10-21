export type PollEnd = "done" | "gave_up" | "error";

/**
 * Bounded polling for real processing state. One request at a time; stopping
 * aborts the request in flight and drops any answer that arrives afterwards,
 * so an old claim's response can never replace a newer selection.
 */
export function createPoller<T>(options: {
  fetchOnce: (signal: AbortSignal) => Promise<T>;
  isDone: (value: T) => boolean;
  onValue: (value: T) => void;
  onEnd?: (reason: PollEnd, error?: unknown) => void;
  intervalMs?: number;
  maxPolls?: number;
}): { start: () => void; stop: () => void } {
  const interval = options.intervalMs ?? 1500;
  const limit = options.maxPolls ?? 80;
  let stopped = false;
  let polls = 0;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let controller: AbortController | undefined;

  async function tick() {
    if (stopped) return;
    polls += 1;
    controller = new AbortController();
    let value: T;
    try {
      value = await options.fetchOnce(controller.signal);
    } catch (error) {
      if (!stopped) options.onEnd?.("error", error);
      return;
    }
    if (stopped) return;
    options.onValue(value);
    if (options.isDone(value)) {
      options.onEnd?.("done");
      return;
    }
    if (polls >= limit) {
      options.onEnd?.("gave_up");
      return;
    }
    timer = setTimeout(() => void tick(), interval);
  }

  return {
    start() {
      stopped = false;
      polls = 0;
      timer = setTimeout(() => void tick(), interval);
    },
    stop() {
      stopped = true;
      clearTimeout(timer);
      controller?.abort();
    },
  };
}
