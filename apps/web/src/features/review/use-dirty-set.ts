"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export type TrackDirty = (key: string) => (dirty: boolean) => void;

/** Aggregates several forms' unsaved state into one flag. */
export function useDirtySet(onChange?: (dirty: boolean) => void): { dirty: boolean; track: TrackDirty } {
  const [keys, setKeys] = useState<ReadonlySet<string>>(() => new Set());
  const track = useCallback<TrackDirty>(
    (key) => (dirty) =>
      setKeys((previous) => {
        if (previous.has(key) === dirty) return previous;
        const next = new Set(previous);
        if (dirty) next.add(key);
        else next.delete(key);
        return next;
      }),
    [],
  );
  const dirty = keys.size > 0;
  const report = useRef(onChange);
  useEffect(() => {
    report.current = onChange;
  });
  useEffect(() => {
    report.current?.(dirty);
  }, [dirty]);
  return { dirty, track };
}
