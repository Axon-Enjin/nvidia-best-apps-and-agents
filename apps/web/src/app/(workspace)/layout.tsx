import type { ReactNode } from "react";

import { LiveRegion, StatusProvider } from "@/components/ui/notice";
import { QueueLink, QueueMemoryProvider } from "@/features/session/queue-memory";
import { SessionProvider } from "@/features/session/session-provider";
import { SignOutButton } from "@/features/session/sign-out-button";
import { requireSession } from "@/lib/backend";

const CLINICAL_ROLES = new Set(["reviewer", "supervisor"]);

export default async function WorkspaceLayout({ children }: { children: ReactNode }) {
  const session = await requireSession();
  const { actor } = session;
  const clinical = actor.roles.some((role) => CLINICAL_ROLES.has(role));

  return (
    <StatusProvider>
      <SessionProvider actor={actor} csrfToken={session.csrf_token}>
        <QueueMemoryProvider>
          <a href="#main" className="skip-link">
            Skip to main content
          </a>
          <header className="bg-forest text-white">
            <div className="mx-auto flex min-h-14 max-w-[90rem] flex-wrap items-center gap-x-6 gap-y-2 px-4 py-2 md:px-6">
              <QueueLink className="text-[1.25rem] font-[650] tracking-tight text-white no-underline">Sentinel Claims</QueueLink>
              <div className="ml-auto flex items-center gap-4">
                <p className="text-sm">
                  <span className="font-semibold">{actor.username}</span>
                  <span className="text-white/80"> · {actor.roles.map((role) => role.charAt(0).toUpperCase() + role.slice(1)).join(", ")}</span>
                </p>
                <SignOutButton />
              </div>
            </div>
          </header>
          <p className="border-b border-rule-faint bg-surface">
            <span className="mx-auto block max-w-[90rem] px-4 py-1.5 text-sm text-ink-muted md:px-6">
              Evaluation workspace: sample patient records
            </span>
          </p>
          <div className="mx-auto max-w-[90rem] px-4 pb-16 pt-6 md:px-6">
            <LiveRegion />
            <main id="main" tabIndex={-1} className="outline-none">
              {clinical ? (
                children
              ) : (
                <section className="panel max-w-2xl p-6">
                  <h1 className="text-[1.75rem]">Claims</h1>
                  <p className="mt-3">Your account has no reviewer or supervisor role. Ask your operator to update it.</p>
                </section>
              )}
            </main>
          </div>
        </QueueMemoryProvider>
      </SessionProvider>
    </StatusProvider>
  );
}
