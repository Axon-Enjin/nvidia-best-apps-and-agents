"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState, type FormEvent } from "react";

import { describedBy, Field } from "@/components/ui/field";
import { apiRequest, errorText } from "@/lib/api-client";

export function SignInForm({ nextPath }: { nextPath: string }) {
  const router = useRouter();
  const errorRef = useRef<HTMLParagraphElement>(null);
  const [error, setError] = useState<{ text: string; attempt: number } | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    if (error) errorRef.current?.focus();
  }, [error]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setPending(true);
    try {
      await apiRequest("/api/session", {
        method: "POST",
        json: {
          username: String(data.get("username") ?? ""),
          password: String(data.get("password") ?? ""),
          otp: String(data.get("otp") ?? ""),
        },
      });
      router.replace(nextPath);
      router.refresh();
    } catch (failure) {
      setError((previous) => ({ text: errorText(failure), attempt: (previous?.attempt ?? 0) + 1 }));
      setPending(false);
    }
  }

  return (
    <form onSubmit={submit} className="grid gap-5" noValidate={false}>
      <Field id="username" label="Username" required>
        <input id="username" name="username" className="input" autoComplete="username" maxLength={80} required autoFocus />
      </Field>
      <Field id="password" label="Password" required>
        <input id="password" name="password" type="password" className="input" autoComplete="current-password" maxLength={128} required />
      </Field>
      <Field id="otp" label="Authenticator code" help="Required for supervisors and administrators.">
        <input
          id="otp"
          name="otp"
          className="input"
          inputMode="numeric"
          autoComplete="one-time-code"
          pattern="[0-9]{6}"
          maxLength={6}
          aria-describedby={describedBy("otp", { help: "y" })}
        />
      </Field>
      {error ? (
        <p id="login-error" ref={errorRef} role="alert" tabIndex={-1} className="border-l-4 border-blocking bg-blocking-tint px-4 py-3 font-semibold text-blocking">
          {error.text}
        </p>
      ) : null}
      <button id="sign-in" type="submit" className="btn btn-primary w-full" disabled={pending}>
        {pending ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}
