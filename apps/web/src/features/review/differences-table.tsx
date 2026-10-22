import { documentLabel, fieldLabel } from "@/features/case/labels";
import type { Difference } from "@/lib/api-types";

import type { DifferenceMark } from "./evidence";

export function MarkBadge({ letter }: { letter: string }) {
  return (
    <span
      data-mark={letter}
      className="inline-grid size-6 shrink-0 place-items-center rounded-[3px] bg-teal font-mono text-xs font-bold text-white"
    >
      {letter}
    </span>
  );
}

/** Each differing value once, with the documents, pages and version that carry it. */
export function DifferencesTable({ marks, differences, version }: { marks: DifferenceMark[]; differences: Difference[]; version: number }) {
  const fields = [...new Set(marks.map((mark) => mark.field))];
  return (
    <div className="grid gap-2">
      <h3 className="eyebrow">What differs</h3>
      <div className="overflow-x-auto">
        <table aria-label="What differs" className="w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-ink">
              <th scope="col" className="w-10 py-1.5 pr-2 font-semibold">Mark</th>
              <th scope="col" className="py-1.5 pr-3 font-semibold">Field</th>
              <th scope="col" className="py-1.5 pr-3 font-semibold">Value</th>
              <th scope="col" className="py-1.5 font-semibold">Source in version {version}</th>
            </tr>
          </thead>
          <tbody>
            {fields.flatMap((field) => {
              const rows = marks.filter((mark) => mark.field === field);
              const expected = differences.find((difference) => difference.field === field)?.expected;
              return [
                ...rows.map((mark) => (
                  <tr key={`${field}-${mark.letter}`} className="border-b border-rule-faint align-top">
                    <td className="py-2 pr-2">
                      <MarkBadge letter={mark.letter} />
                    </td>
                    <td className="py-2 pr-3">{fieldLabel(field)}</td>
                    <td className="doc-ref whitespace-nowrap py-2 pr-3 text-[0.875rem] font-semibold">{mark.value}</td>
                    <td className="py-2">
                      <ul className="grid gap-0.5">
                        {mark.sources.map((source) => (
                          <li key={source.documentId}>
                            {documentLabel(source.type)} · {source.page ? `page ${source.page}` : "page not located"}
                          </li>
                        ))}
                      </ul>
                    </td>
                  </tr>
                )),
                ...(expected
                  ? [
                      <tr key={`${field}-expected`} className="border-b border-rule-faint align-top">
                        <td className="py-2 pr-2 text-ink-muted">–</td>
                        <td className="py-2 pr-3">{fieldLabel(field)}</td>
                        <td className="doc-ref whitespace-nowrap py-2 pr-3 text-[0.875rem] font-semibold">{expected}</td>
                        <td className="py-2 text-ink-muted">Claim record (expected)</td>
                      </tr>,
                    ]
                  : []),
              ];
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
