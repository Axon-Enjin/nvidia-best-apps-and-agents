"use client";

import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

type StatusContextValue = { message: string; announce: (message: string) => void };

const StatusContext = createContext<StatusContextValue>({ message: "", announce: () => {} });

/** One polite live region per page; saves and session changes are announced there, polling never is. */
export function StatusProvider({ children }: { children: ReactNode }) {
  const [message, setMessage] = useState("");
  const announce = useCallback((next: string) => setMessage(next), []);
  const value = useMemo(() => ({ message, announce }), [message, announce]);
  return <StatusContext.Provider value={value}>{children}</StatusContext.Provider>;
}

/** Where announcements appear: at the top of the page content, below the site header. */
export function LiveRegion() {
  const { message } = useContext(StatusContext);
  return (
    <p
      role="status"
      aria-live="polite"
      className={message ? "mb-4 border-l-4 border-teal bg-surface px-4 py-3 font-semibold text-ink" : "sr-only"}
    >
      {message}
    </p>
  );
}

export function useStatus(): { announce: (message: string) => void } {
  const { announce } = useContext(StatusContext);
  return { announce };
}
