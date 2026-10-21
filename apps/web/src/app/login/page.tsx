import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { SignInForm } from "@/features/session/sign-in-form";
import { safeNextPath } from "@/features/session/safe-next";
import type { SessionState } from "@/lib/api-types";
import { getSession } from "@/lib/backend";

export const metadata: Metadata = { title: "Sign in" };

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string | string[] }> }) {
  const { next } = await searchParams;
  const nextPath = safeNextPath(typeof next === "string" ? next : null);
  let session: SessionState | null = null;
  try {
    session = await getSession();
  } catch {
    session = null; // The form explains an unreachable review service when it is used.
  }
  if (session?.authenticated) redirect(nextPath);

  return (
    <main id="main" className="mx-auto flex min-h-dvh w-full max-w-[28rem] flex-col justify-center gap-8 px-4 py-12">
      <header>
        <p className="border-b border-ink pb-3 text-[1.375rem] font-[650] tracking-tight text-forest">Sentinel Claims</p>
        <h1 className="mt-8 text-[1.75rem]">Sign in to your workspace</h1>
        <p className="mt-2 text-ink-muted">Review evidence and coordinate corrections with your claims team.</p>
      </header>
      <div className="panel border-t-4 border-t-forest p-6">
        <SignInForm nextPath={nextPath} />
      </div>
      <footer className="grid gap-2 text-sm text-ink-muted">
        <p>Ask your local operator to create or reset your named account.</p>
        <p>Evaluation workspace: sample patient records</p>
      </footer>
    </main>
  );
}
