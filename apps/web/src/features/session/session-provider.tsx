"use client";

import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

import { useStatus } from "@/components/ui/notice";
import { apiRequest, SessionExpiredError, type RequestOptions } from "@/lib/api-client";
import type { Actor } from "@/lib/api-types";

import { ReauthDialog } from "./reauth-dialog";

type SessionContextValue = {
  actor: Actor;
  csrfToken: string;
  /** Same-origin API call with the CSRF token. A 401 opens the sign-in dialog and rejects; nothing is retried. */
  request: <T>(path: string, options?: RequestOptions) => Promise<T>;
  /** Increments after each successful re-sign-in, so forms can show that their draft is still theirs to save. */
  reauthenticated: number;
};

const SessionContext = createContext<SessionContextValue | null>(null);

export function SessionProvider({ actor, csrfToken, children }: { actor: Actor; csrfToken: string; children: ReactNode }) {
  const { announce } = useStatus();
  const [renewedToken, setRenewedToken] = useState<string | null>(null);
  const [reauthOpen, setReauthOpen] = useState(false);
  const [reauthenticated, setReauthenticated] = useState(0);
  const token = renewedToken ?? csrfToken;

  const request = useCallback(
    async <T,>(path: string, options: RequestOptions = {}): Promise<T> => {
      try {
        return await apiRequest<T>(path, { ...options, csrfToken: token });
      } catch (error) {
        if (error instanceof SessionExpiredError) setReauthOpen(true);
        throw error;
      }
    },
    [token],
  );

  const signedIn = useCallback(
    (nextToken: string) => {
      setRenewedToken(nextToken);
      setReauthOpen(false);
      setReauthenticated((count) => count + 1);
      announce("Signed in again. Review your draft, then save.");
    },
    [announce],
  );

  const value = useMemo(() => ({ actor, csrfToken: token, request, reauthenticated }), [actor, token, request, reauthenticated]);
  return (
    <SessionContext.Provider value={value}>
      {children}
      <ReauthDialog open={reauthOpen} username={actor.username} onSignedIn={signedIn} onClose={() => setReauthOpen(false)} />
    </SessionContext.Provider>
  );
}

export function useSession(): SessionContextValue {
  const value = useContext(SessionContext);
  if (!value) throw new Error("useSession must be used inside SessionProvider.");
  return value;
}
