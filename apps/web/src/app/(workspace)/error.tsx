"use client";

export default function WorkspaceError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <section role="alert" className="panel max-w-2xl border-l-4 border-l-blocking p-6">
      <h1 className="text-[1.375rem]">This page could not load</h1>
      <p className="mt-2">
        {error.message && !error.digest ? error.message : "The review service did not answer as expected. Your saved work is unchanged."}
      </p>
      <button type="button" className="btn btn-primary mt-4" onClick={reset}>
        Try again
      </button>
    </section>
  );
}
