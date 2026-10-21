"use client";

import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

type StatusContextValue = { announce: (message: string) => void };

const StatusContext = createContext<StatusContextValue>({ announce: () => {} });

/** One polite live region per page; saves and session changes are announced here, polling never is. */
export function StatusProvider({ children }: { children: ReactNode }) {
  const [message, setMessage] = useState("");
  const announce = useCallback((next: string) => setMessage(next), []);
  const value = useMemo(() => ({ announce }), [announce]);
  return (
    <StatusContext.Provider value={value}>
      <p
        role="status"
        aria-live="polite"
        className={
          message
            ? "mb-4 border-l-4 border-teal bg-surface px-4 py-3 font-semibold text-ink"
            : "sr-only"
        }
      >
        {message}
      </p>
      {children}
    </StatusContext.Provider>
  );
}

export function useStatus(): StatusContextValue {
  return useContext(StatusContext);
}
