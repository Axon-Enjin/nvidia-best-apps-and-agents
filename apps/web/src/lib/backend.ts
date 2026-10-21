// Server-side reads from the review service, made with the reviewer's own
// session cookie. `next/headers` keeps this module out of client bundles.
import { cookies, headers } from "next/headers";
import { notFound, redirect } from "next/navigation";
import { cache } from "react";

import type { Actor, SessionState } from "./api-types";
import { backendUrl } from "./backend-url";

export class BackendError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : `Review service answered ${status}.`);
    this.status = status;
    this.detail = detail;
  }
}

export type SignedInSession = SessionState & { actor: Actor; csrf_token: string };

export const currentPath = cache(async (): Promise<string> => (await headers()).get("x-sentinel-path") ?? "/claims");

async function signInRedirect(): Promise<never> {
  redirect(`/login?next=${encodeURIComponent(await currentPath())}`);
}

async function get(path: string): Promise<Response> {
  const session = (await cookies()).get("sentinel_session");
  return fetch(backendUrl(path), {
    headers: { accept: "application/json", cookie: session ? `sentinel_session=${session.value}` : "" },
    cache: "no-store",
  });
}

export async function backendGet<T>(path: string): Promise<T> {
  const response = await get(path);
  if (response.status === 401) return signInRedirect();
  if (response.status === 404) notFound();
  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = body && typeof body === "object" && "detail" in body ? body.detail : null;
    throw new BackendError(response.status, detail);
  }
  return body as T;
}

export const getSession = cache(async (): Promise<SessionState> => {
  const response = await get("/api/session");
  if (!response.ok) throw new BackendError(response.status, null);
  return (await response.json()) as SessionState;
});

export const requireSession = cache(async (): Promise<SignedInSession> => {
  const session = await getSession();
  if (!session.authenticated || !session.actor || !session.csrf_token) return signInRedirect();
  return session as SignedInSession;
});
