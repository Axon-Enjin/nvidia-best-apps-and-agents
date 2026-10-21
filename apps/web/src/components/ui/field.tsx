import type { ReactNode } from "react";

/** ids for aria-describedby, matching the help and error ids Field renders. */
export function describedBy(id: string, parts: { help?: string | null; error?: string | null }): string | undefined {
  const ids = [parts.help ? `${id}-help` : null, parts.error ? `${id}-error` : null].filter(Boolean);
  return ids.length ? ids.join(" ") : undefined;
}

export function Field({
  id,
  label,
  help,
  error,
  required,
  children,
}: {
  id: string;
  label: string;
  help?: string | null;
  error?: string | null;
  required?: boolean;
  children: ReactNode;
}) {
  return (
    <div className="grid gap-1.5">
      <div className="flex flex-wrap items-baseline gap-x-1.5">
        <label htmlFor={id} className="label">
          {label}
        </label>
        {/* Visual indicator only; the control's `required` attribute announces it. */}
        {required ? (
          <span aria-hidden="true" className="text-sm text-ink-muted">
            (required)
          </span>
        ) : null}
      </div>
      {help ? (
        <p id={`${id}-help`} className="help">
          {help}
        </p>
      ) : null}
      {children}
      {error ? (
        <p id={`${id}-error`} className="field-error">
          {error}
        </p>
      ) : null}
    </div>
  );
}
