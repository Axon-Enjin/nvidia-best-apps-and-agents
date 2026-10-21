import assert from "node:assert/strict";
import { test } from "node:test";

import { createPoller } from "./poller.ts";

const flush = () => new Promise((resolve) => setImmediate(resolve));

test("polls until the value is done, then stops", async (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const values = ["queued", "running", "succeeded"];
  const seen: string[] = [];
  const ends: string[] = [];
  let fetches = 0;
  const poller = createPoller({
    fetchOnce: async () => values[fetches++] ?? "succeeded",
    isDone: (value) => value === "succeeded",
    onValue: (value) => seen.push(value),
    onEnd: (reason) => ends.push(reason),
    intervalMs: 1500,
  });
  poller.start();
  for (let i = 0; i < 5; i += 1) {
    t.mock.timers.tick(1500);
    await flush();
  }
  assert.deepEqual(seen, ["queued", "running", "succeeded"]);
  assert.deepEqual(ends, ["done"]);
  assert.equal(fetches, 3);
});

test("gives up after the poll limit", async (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  let fetches = 0;
  const ends: string[] = [];
  const poller = createPoller({
    fetchOnce: async () => {
      fetches += 1;
      return "queued";
    },
    isDone: () => false,
    onValue: () => {},
    onEnd: (reason) => ends.push(reason),
    intervalMs: 1000,
    maxPolls: 3,
  });
  poller.start();
  for (let i = 0; i < 6; i += 1) {
    t.mock.timers.tick(1000);
    await flush();
  }
  assert.equal(fetches, 3);
  assert.deepEqual(ends, ["gave_up"]);
});

test("a value arriving after stop never reaches onValue, and the request is aborted", async (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  let release: (value: string) => void = () => {};
  let signal: AbortSignal | undefined;
  const seen: string[] = [];
  const poller = createPoller({
    fetchOnce: (abort) => {
      signal = abort;
      return new Promise<string>((resolve) => {
        release = resolve;
      });
    },
    isDone: () => true,
    onValue: (value) => seen.push(value),
  });
  poller.start();
  t.mock.timers.tick(1500);
  await flush();
  poller.stop();
  release("succeeded");
  await flush();
  assert.deepEqual(seen, []);
  assert.equal(signal?.aborted, true);
});
