// BACKEND_URL is server-only configuration; it never reaches the browser bundle.
export function backendUrl(path: string): string {
  return new URL(path, process.env.BACKEND_URL ?? "http://127.0.0.1:8000").toString();
}
