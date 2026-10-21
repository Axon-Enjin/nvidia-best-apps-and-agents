"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

// Old static-UI links look like `/#case=<id>`. The fragment never reaches the
// server, so the browser forwards them to the claim's own route.
export default function Home() {
  const router = useRouter();
  useEffect(() => {
    const match = /^#case=([0-9a-f]{32})$/.exec(window.location.hash);
    router.replace(match ? `/claims/${match[1]}` : "/claims");
  }, [router]);
  return (
    <main id="main" className="px-4 py-12">
      <p>Opening your claims…</p>
    </main>
  );
}
