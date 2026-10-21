import assert from "node:assert/strict";
import { test } from "node:test";

import { forwardRequestHeaders, forwardResponseHeaders } from "./proxy-headers.ts";

test("drops host, authorization, connection and unknown headers", () => {
  const incoming = new Headers({
    host: "127.0.0.1:3000",
    authorization: "Bearer secret",
    connection: "keep-alive",
    "x-unknown": "1",
    cookie: "sentinel_session=abc",
    "content-type": "application/json",
    "x-csrf-token": "token",
    "idempotency-key": "key-1",
    origin: "http://127.0.0.1:3000",
    accept: "application/json",
    "user-agent": "browser",
  });
  const forwarded = forwardRequestHeaders(incoming, "127.0.0.1", "http");
  for (const name of ["host", "authorization", "connection", "x-unknown"]) {
    assert.equal(forwarded.get(name), null, name);
  }
  assert.equal(forwarded.get("cookie"), "sentinel_session=abc");
  assert.equal(forwarded.get("x-csrf-token"), "token");
  assert.equal(forwarded.get("idempotency-key"), "key-1");
  assert.equal(forwarded.get("origin"), "http://127.0.0.1:3000");
  assert.equal(forwarded.get("content-type"), "application/json");
});

test("adds forwarded proto, for and host", () => {
  const forwarded = forwardRequestHeaders(new Headers({ host: "127.0.0.1:3000" }), "10.0.0.5", "https");
  assert.equal(forwarded.get("x-forwarded-proto"), "https");
  assert.equal(forwarded.get("x-forwarded-for"), "10.0.0.5");
  assert.equal(forwarded.get("x-forwarded-host"), "127.0.0.1:3000");
});

test("keeps two set-cookie headers separately", () => {
  const upstream = new Headers();
  upstream.append("set-cookie", "a=1; HttpOnly");
  upstream.append("set-cookie", "b=2; HttpOnly");
  upstream.set("content-type", "application/json");
  const response = forwardResponseHeaders(upstream);
  assert.deepEqual(response.getSetCookie(), ["a=1; HttpOnly", "b=2; HttpOnly"]);
  assert.equal(response.get("content-type"), "application/json");
});

test("forces no-store even when upstream allows caching", () => {
  const response = forwardResponseHeaders(new Headers({ "cache-control": "public, max-age=3600" }));
  assert.equal(response.get("cache-control"), "no-store");
  assert.equal(response.get("x-content-type-options"), "nosniff");
});

test("keeps download headers and drops transfer headers", () => {
  const response = forwardResponseHeaders(new Headers({
    "content-disposition": 'attachment; filename="record.csv"',
    "retry-after": "300",
    "content-length": "12",
    "content-encoding": "gzip",
    "x-frame-options": "DENY",
  }));
  assert.equal(response.get("content-disposition"), 'attachment; filename="record.csv"');
  assert.equal(response.get("retry-after"), "300");
  assert.equal(response.get("content-length"), null);
  assert.equal(response.get("content-encoding"), null);
});
