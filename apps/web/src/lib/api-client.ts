// Browser calls to the same-origin API. One request per call: nothing here
// retries or replays a change, so a failed save is always the reviewer's call.

export type RequestOptions = {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  json?: unknown;
  form?: FormData;
  csrfToken?: string;
  headers?: Record<string, string>;
  signal?: AbortSignal;
};

export class ApiError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, detail: unknown) {
    super(detailText(detail) ?? `The review service answered ${status}.`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export class SessionExpiredError extends ApiError {}
export class ForbiddenError extends ApiError {}
export class ConflictError extends ApiError {}

export class ValidationError extends ApiError {
  readonly messages: string[];

  constructor(status: number, detail: unknown) {
    super(status, detail);
    this.messages = validationMessages(detail);
  }
}

export class ServiceUnreachableError extends Error {
  constructor(message = UNREACHABLE) {
    super(message);
    this.name = "ServiceUnreachableError";
  }
}

const UNREACHABLE = "Cannot reach the review service. Check that it is running, then try again.";

function validationMessages(detail: unknown): string[] {
  if (!Array.isArray(detail)) return [];
  return detail
    .map((item) => (item && typeof item === "object" && "msg" in item ? String(item.msg) : ""))
    .filter(Boolean)
    .map((message) => message.replace(/^Value error, /, ""));
}

function detailText(detail: unknown): string | null {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return validationMessages(detail).join(" ") || null;
  if (detail && typeof detail === "object" && "message" in detail) return String(detail.message);
  return null;
}

export function errorText(error: unknown): string {
  if (error instanceof Error && error.message) return error.message;
  return "Something went wrong. Try again.";
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}, fetchImpl: typeof fetch = fetch): Promise<T> {
  const method = options.method ?? "GET";
  const headers = new Headers(options.headers);
  headers.set("accept", "application/json");
  let body: BodyInit | undefined;
  if (options.json !== undefined) {
    headers.set("content-type", "application/json");
    body = JSON.stringify(options.json);
  } else if (options.form) {
    body = options.form;
  }
  if (method !== "GET" && options.csrfToken) headers.set("x-csrf-token", options.csrfToken);

  let response: Response;
  try {
    response = await fetchImpl(path, { method, headers, body, credentials: "same-origin", cache: "no-store", signal: options.signal });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ServiceUnreachableError();
  }
  const type = response.headers.get("content-type") ?? "";
  const payload: unknown = type.includes("application/json") ? await response.json().catch(() => null) : await response.text();
  if (response.ok) return payload as T;
  const detail = payload && typeof payload === "object" && "detail" in payload ? payload.detail : payload;
  if (response.status === 502) throw new ServiceUnreachableError(detailText(detail) ?? UNREACHABLE);
  if (response.status === 401) throw new SessionExpiredError(401, detail);
  if (response.status === 403) throw new ForbiddenError(403, detail);
  if (response.status === 409) throw new ConflictError(409, detail);
  if (response.status === 422) throw new ValidationError(422, detail);
  throw new ApiError(response.status, detail);
}
