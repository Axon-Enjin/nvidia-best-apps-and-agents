import type { NextRequest } from "next/server";

import { backendUrl } from "@/lib/backend-url";
import { forwardRequestHeaders, forwardResponseHeaders } from "@/lib/proxy-headers";

// Same-origin boundary: the browser only ever talks to this origin. Requests are
// streamed to the review service unchanged apart from an allow-list of headers.
export const dynamic = "force-dynamic";

const UNREACHABLE = "Cannot reach the review service. Check that it is running, then try again.";

type Context = { params: Promise<{ path: string[] }> };

async function forward(request: NextRequest, { params }: Context): Promise<Response> {
  const { path } = await params;
  const target = backendUrl(`/api/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`);
  const proto = request.nextUrl.protocol === "https:" ? "https" : "http";
  const clientIp = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || null;
  const hasBody = request.method !== "GET" && request.method !== "HEAD";
  const init: RequestInit & { duplex?: "half" } = {
    method: request.method,
    headers: forwardRequestHeaders(request.headers, clientIp, proto),
    body: hasBody ? request.body : undefined,
    redirect: "manual",
    cache: "no-store",
  };
  if (hasBody) init.duplex = "half";
  let upstream: Response;
  try {
    upstream = await fetch(target, init);
  } catch {
    return Response.json({ detail: UNREACHABLE }, { status: 502, headers: { "cache-control": "no-store" } });
  }
  return new Response(upstream.body, { status: upstream.status, headers: forwardResponseHeaders(upstream.headers) });
}

export const GET = forward;
export const POST = forward;
export const PUT = forward;
export const DELETE = forward;
