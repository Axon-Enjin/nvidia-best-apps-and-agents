"use client";

import Link from "next/link";
import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

type QueueMemory = {
  queueQuery: string;
  lastOpenedClaimId: string | null;
  rememberQuery: (query: string) => void;
  rememberOpened: (claimId: string) => void;
};

const QueueMemoryContext = createContext<QueueMemory | null>(null);

/** In-memory only: the queue filters and last opened claim survive in-app navigation, not reloads. */
export function QueueMemoryProvider({ children }: { children: ReactNode }) {
  const [queueQuery, rememberQuery] = useState("");
  const [lastOpenedClaimId, setLastOpened] = useState<string | null>(null);
  const value = useMemo(
    () => ({ queueQuery, lastOpenedClaimId, rememberQuery, rememberOpened: (id: string) => setLastOpened(id) }),
    [queueQuery, lastOpenedClaimId],
  );
  return <QueueMemoryContext.Provider value={value}>{children}</QueueMemoryContext.Provider>;
}

export function useQueueMemory(): QueueMemory {
  const value = useContext(QueueMemoryContext);
  if (!value) throw new Error("useQueueMemory must be used inside QueueMemoryProvider.");
  return value;
}

export function QueueLink({ className, children }: { className?: string; children: ReactNode }) {
  const { queueQuery } = useQueueMemory();
  return (
    <Link href={queueQuery ? `/claims?${queueQuery}` : "/claims"} className={className}>
      {children}
    </Link>
  );
}
