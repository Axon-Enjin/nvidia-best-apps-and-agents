"use client";

import { useState } from "react";

import { History } from "@/components/ui/icons";
import { documentLabel } from "@/features/case/labels";
import { useSession } from "@/features/session/session-provider";
import { errorText } from "@/lib/api-client";
import type { BundleDetail } from "@/lib/api-types";

import { originalHref } from "./documents-table";

/** Earlier versions stay inspectable; decisions apply only to the current version. */
export function EarlierVersions({ claimId, versions }: { claimId: string; versions: number[] }) {
  const { request } = useSession();
  const [opened, setOpened] = useState<Record<number, BundleDetail | string>>({});

  async function open(version: number) {
    try {
      const bundle = await request<BundleDetail>(`/api/claims/${claimId}/bundles/${version}`);
      setOpened((previous) => ({ ...previous, [version]: bundle }));
    } catch (error) {
      setOpened((previous) => ({ ...previous, [version]: errorText(error) }));
    }
  }

  if (!versions.length) return null;
  return (
    <details className="border-t border-rule pt-3">
      <summary className="inline-flex min-h-11 items-center gap-2 font-semibold">
        <History aria-hidden="true" className="size-4" />
        Earlier versions ({versions.length})
      </summary>
      <p className="mt-1 text-sm text-ink-muted">Historical evidence; decisions apply to the current version only.</p>
      <ul className="mt-3 grid gap-3">
        {versions.map((version) => {
          const bundle = opened[version];
          return (
            <li key={version} className="grid gap-2">
              {bundle === undefined ? (
                <button type="button" className="btn btn-secondary justify-self-start" onClick={() => void open(version)}>
                  Show version {version} documents
                </button>
              ) : typeof bundle === "string" ? (
                <p className="field-error">{bundle}</p>
              ) : (
                <>
                  <p className="doc-ref font-semibold">Version {version}</p>
                  <ul className="grid gap-1 pl-4">
                    {bundle.documents.map((document) => (
                      <li key={document.id}>
                        <a href={originalHref(document)} target="_blank" rel="noopener">
                          {documentLabel(document.type, document.filename)}
                        </a>
                        <span className="doc-ref ml-2 text-ink-muted">{document.filename}</span>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </li>
          );
        })}
      </ul>
    </details>
  );
}
