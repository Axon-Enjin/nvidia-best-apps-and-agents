"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";

import { describedBy, Field } from "@/components/ui/field";
import { apiRequest, errorText } from "@/lib/api-client";

/** Signs the same reviewer back in over the page, so the draft underneath stays in place. */
export function ReauthDialog({
  open,
  username,
  onSignedIn,
  onClose,
}: {
  open: boolean;
  username: string;
  onSignedIn: (csrfToken: string) => void;
  onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const errorRef = useRef<HTMLParagraphElement>(null);
  const [error, setError] = useState<{ text: string; attempt: number } | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    const element = dialog.current;
    if (!element) return;
    if (open && !element.open) element.showModal();
    if (!open && element.open) element.close();
  }, [open]);

  useEffect(() => {
    if (error) errorRef.current?.focus();
  }, [error]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setPending(true);
    try {
      const result = await apiRequest<{ csrf_token: string }>("/api/session", {
        method: "POST",
        json: { username, password: String(data.get("password") ?? ""), otp: String(data.get("otp") ?? "") },
      });
      setError(null);
      onSignedIn(result.csrf_token);
    } catch (failure) {
      setError((previous) => ({ text: errorText(failure), attempt: (previous?.attempt ?? 0) + 1 }));
    } finally {
      setPending(false);
    }
  }

  return (
    <dialog
      ref={dialog}
      aria-labelledby="reauth-title"
      onCancel={onClose}
      className="m-auto w-[min(32rem,calc(100vw-2rem))] rounded-[var(--radius-panel)] border border-rule bg-surface p-6 text-ink shadow-[0_12px_40px_#172B2426] backdrop:bg-ink/40"
    >
      {open ? (
        <form onSubmit={submit} className="grid gap-4">
          <h2 id="reauth-title" className="text-xl">
            Sign in again to continue
          </h2>
          <p>Your session ended. Your unsaved work on this page is kept.</p>
          <Field id="reauth-username" label="Username">
            <input id="reauth-username" className="input" value={username} readOnly autoComplete="username" />
          </Field>
          <Field id="reauth-password" label="Password" required>
            <input id="reauth-password" name="password" type="password" className="input" required autoComplete="current-password" maxLength={128} />
          </Field>
          <Field id="reauth-otp" label="Authenticator code" help="Required for supervisors and administrators.">
            <input
              id="reauth-otp"
              name="otp"
              className="input"
              inputMode="numeric"
              autoComplete="one-time-code"
              pattern="[0-9]{6}"
              maxLength={6}
              aria-describedby={describedBy("reauth-otp", { help: "y" })}
            />
          </Field>
          {error ? (
            <p ref={errorRef} role="alert" tabIndex={-1} className="field-error">
              {error.text}
            </p>
          ) : null}
          <div className="flex flex-wrap gap-3">
            <button type="submit" className="btn btn-primary" disabled={pending}>
              Sign in
            </button>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      ) : null}
    </dialog>
  );
}
