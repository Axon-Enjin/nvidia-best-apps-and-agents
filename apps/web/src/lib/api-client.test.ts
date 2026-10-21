import assert from "node:assert/strict";
import { test } from "node:test";

import {
  ApiError,
  ConflictError,
  ServiceUnreachableError,
  SessionExpiredError,
  ValidationError,
  apiRequest,
  errorText,
} from "./api-client.ts";

type Call = { url: string; init: RequestInit };

function fakeFetch(status: number, body: unknown): { fetch: typeof fetch; calls: Call[] } {
  const calls: Call[] = [];
  const fetchImpl = (async (url: string | URL | Request, init?: RequestInit) => {
    calls.push({ url: String(url), init: init ?? {} });
    return new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
  }) as typeof fetch;
  return { fetch: fetchImpl, calls };
}

function header(call: Call | undefined, name: string): string | null {
  return new Headers(call?.init.headers).get(name);
}

test("sends the CSRF token on changes and not on reads", async () => {
  const { fetch, calls } = fakeFetch(200, { ok: true });
  await apiRequest("/api/claims", { csrfToken: "t" }, fetch);
  await apiRequest("/api/cases", { method: "POST", json: { a: 1 }, csrfToken: "t" }, fetch);
  assert.equal(header(calls[0], "x-csrf-token"), null);
  assert.equal(header(calls[1], "x-csrf-token"), "t");
  assert.equal(header(calls[1], "content-type"), "application/json");
  assert.equal(calls[1]?.init.body, JSON.stringify({ a: 1 }));
});

test("401 becomes SessionExpiredError and is never retried", async () => {
  const { fetch, calls } = fakeFetch(401, { detail: "Sign in to continue." });
  await assert.rejects(apiRequest("/api/claims", {}, fetch), SessionExpiredError);
  assert.equal(calls.length, 1);
});

test("409 keeps the server's explanation", async () => {
  const detail = "Case changed. Refresh before saving; your draft has not overwritten saved work.";
  const { fetch, calls } = fakeFetch(409, { detail });
  await assert.rejects(apiRequest("/api/x", { method: "POST", json: {} }, fetch), (error: unknown) => {
    assert.ok(error instanceof ConflictError);
    assert.equal(errorText(error), detail);
    return true;
  });
  assert.equal(calls.length, 1);
});

test("422 validation lists each message without the framework prefix", async () => {
  const { fetch } = fakeFetch(422, {
    detail: [
      { type: "value_error", loc: ["body"], msg: "Value error, Explain why this finding is being dismissed." },
      { type: "string_too_short", loc: ["body", "reason"], msg: "String should have at least 1 character" },
    ],
  });
  await assert.rejects(apiRequest("/api/x", { method: "POST", json: {} }, fetch), (error: unknown) => {
    assert.ok(error instanceof ValidationError);
    assert.deepEqual(error.messages, [
      "Explain why this finding is being dismissed.",
      "String should have at least 1 character",
    ]);
    return true;
  });
});

test("a structured conflict shows its message", async () => {
  const { fetch } = fakeFetch(409, { detail: { message: "Resolve current-version blockers before completing review.", blockers: [] } });
  await assert.rejects(apiRequest("/api/x", { method: "POST", json: {} }, fetch), (error: unknown) => {
    assert.equal(errorText(error), "Resolve current-version blockers before completing review.");
    return true;
  });
});

test("a network failure or proxy 502 becomes ServiceUnreachableError", async () => {
  let calls = 0;
  const failing = (async () => {
    calls += 1;
    throw new TypeError("fetch failed");
  }) as typeof fetch;
  await assert.rejects(apiRequest("/api/session", {}, failing), ServiceUnreachableError);
  assert.equal(calls, 1);
  const { fetch } = fakeFetch(502, { detail: "Cannot reach the review service. Check that it is running, then try again." });
  await assert.rejects(apiRequest("/api/session", {}, fetch), (error: unknown) => {
    assert.ok(error instanceof ServiceUnreachableError);
    assert.match(errorText(error), /Cannot reach the review service/);
    return true;
  });
});

test("other failures keep status and detail", async () => {
  const { fetch } = fakeFetch(413, { detail: "Limit: 25 MB per file and 100 MB per bundle version." });
  await assert.rejects(apiRequest("/api/x", { method: "POST", form: new FormData() }, fetch), (error: unknown) => {
    assert.ok(error instanceof ApiError);
    assert.equal(error.status, 413);
    assert.equal(errorText(error), "Limit: 25 MB per file and 100 MB per bundle version.");
    return true;
  });
});
