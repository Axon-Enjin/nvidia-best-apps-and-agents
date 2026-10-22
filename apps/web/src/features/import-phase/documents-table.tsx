import { StatusText } from "@/components/ui/status-text";
import { documentLabel, documentStatusText, documentStatusTone, fieldLabel } from "@/features/case/labels";
import type { BundleDetail, ReviewState, SourceDocument } from "@/lib/api-types";

const PREVIEWABLE = new Set(["image/png", "image/jpeg", "application/pdf"]);

export function originalHref(document: Pick<SourceDocument, "id" | "content_type">): string {
  return `/api/documents/${document.id}/${PREVIEWABLE.has(document.content_type) ? "preview" : "content"}`;
}

function problemText(status: string, problems: string[]): string | null {
  if (!problems.length) return null;
  if (status === "ambiguous") return `Conflicting values for ${problems.map(fieldLabel).join(", ")}.`;
  return problems.join(" ");
}

/** Every document in the current version with its effective state (scan confirmations included). */
export function DocumentsTable({ bundle, review }: { bundle: BundleDetail; review: ReviewState | null }) {
  return (
    <section aria-labelledby="documents-heading" className="grid gap-3">
      <h2 id="documents-heading" className="border-t border-ink pt-3 text-lg">
        Documents in version {bundle.version}
      </h2>
      <div className="overflow-x-auto">
        <table aria-labelledby="documents-heading" className="w-full border-collapse text-left">
          <thead>
            <tr className="border-b border-ink">
              <th scope="col" className="eyebrow py-2 pr-4">Document</th>
              <th scope="col" className="eyebrow hidden py-2 pr-4 sm:table-cell">Pages</th>
              <th scope="col" className="eyebrow hidden py-2 pr-4 sm:table-cell">Status</th>
              <th scope="col" className="eyebrow py-2">Original</th>
            </tr>
          </thead>
          <tbody>
            {bundle.documents.map((document) => {
              const status = review?.confirmations.find((item) => item.document_id === document.id)?.status ?? document.status;
              const problems = problemText(status, document.problems);
              return (
                <tr key={document.id} className="border-b border-rule-faint align-top">
                  <td className="py-3 pr-4">
                    <p className="font-semibold">{documentLabel(document.type, document.filename)}</p>
                    <p className="doc-ref break-all text-ink-muted">{document.filename}</p>
                    <div className="mt-1 sm:hidden">
                      <StatusText tone={documentStatusTone(status)}>{documentStatusText(status)}</StatusText>
                      {problems ? <p className="mt-1 text-sm text-ink-muted">{problems}</p> : null}
                    </div>
                  </td>
                  <td className="hidden py-3 pr-4 tabular-nums sm:table-cell">{document.page_count}</td>
                  <td className="hidden py-3 pr-4 sm:table-cell">
                    <StatusText tone={documentStatusTone(status)}>{documentStatusText(status)}</StatusText>
                    {problems ? <p className="mt-1 max-w-md text-sm text-ink-muted">{problems}</p> : null}
                  </td>
                  <td className="py-3">
                    <a href={originalHref(document)} target="_blank" rel="noopener" className="link-button py-0">
                      Open<span className="sr-only"> original {documentLabel(document.type, document.filename)}</span>
                    </a>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
