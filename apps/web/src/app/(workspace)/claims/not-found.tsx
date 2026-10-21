import { QueueLink } from "@/features/session/queue-memory";

export default function ClaimNotFound() {
  return (
    <section className="panel max-w-2xl p-6">
      <h1 className="text-[1.75rem]">Claim not found</h1>
      <p className="mt-2">This claim does not exist, or it is assigned to another reviewer.</p>
      <QueueLink className="link-button mt-2 inline-block">Back to claims</QueueLink>
    </section>
  );
}
