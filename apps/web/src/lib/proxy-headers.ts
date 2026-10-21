// Header rules for the same-origin API proxy. Only headers the review service
// needs go upstream; only headers the browser needs come back, never cacheable.

const REQUEST_HEADERS = [
  "accept",
  "content-type",
  "cookie",
  "idempotency-key",
  "origin",
  "x-csrf-token",
  "user-agent",
] as const;

const RESPONSE_HEADERS = ["content-type", "content-disposition", "retry-after"] as const;

export function forwardRequestHeaders(
  incoming: Headers,
  clientIp: string | null,
  proto: "http" | "https",
): Headers {
  const headers = new Headers();
  for (const name of REQUEST_HEADERS) {
    const value = incoming.get(name);
    if (value !== null) headers.set(name, value);
  }
  headers.set("x-forwarded-proto", proto);
  if (clientIp) headers.set("x-forwarded-for", clientIp);
  const host = incoming.get("host");
  if (host) headers.set("x-forwarded-host", host);
  return headers;
}

export function forwardResponseHeaders(upstream: Headers): Headers {
  const headers = new Headers();
  for (const name of RESPONSE_HEADERS) {
    const value = upstream.get(name);
    if (value !== null) headers.set(name, value);
  }
  for (const cookie of upstream.getSetCookie()) headers.append("set-cookie", cookie);
  headers.set("cache-control", "no-store");
  headers.set("x-content-type-options", "nosniff");
  return headers;
}
