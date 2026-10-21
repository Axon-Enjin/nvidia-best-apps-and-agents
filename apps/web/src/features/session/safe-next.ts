const FALLBACK = "/claims";

/** Return path after sign-in: only an in-app page path, never another origin or an API route. */
export function safeNextPath(value: string | null | undefined): string {
  if (!value || !value.startsWith("/") || value.startsWith("//") || value.includes("\\")) return FALLBACK;
  if (/[\s\u0000-\u001f\u007f]/.test(value)) return FALLBACK;
  if (/^\/api(?:[/?#]|$)/.test(value)) return FALLBACK;
  return value;
}
